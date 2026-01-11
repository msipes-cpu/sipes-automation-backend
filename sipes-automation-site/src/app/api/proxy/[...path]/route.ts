import { NextRequest, NextResponse } from "next/server";

// Validates and returns the backend URL from environment
const getBackendUrl = () => {
    const url = process.env.NEXT_PUBLIC_API_URL;
    if (!url) return null;
    return url.endsWith('/') ? url.slice(0, -1) : url;
};

async function handler(req: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
    const resolvedParams = await params;
    const backendBase = getBackendUrl();

    if (!backendBase) {
        return NextResponse.json(
            { error: "Backend URL not configured on server" },
            { status: 500 }
        );
    }

    // Reconstruct the path (e.g., /api/proxy/leads/test-run -> /leads/test-run)
    // Note: The params.path array contains ["leads", "test-run"]
    // We want to forward to {BACKEND_URL}/api/{path} usually, but the backend paths
    // in main.py start with /api/.
    // Let's assume the frontend sends requests to /api/proxy/api/leads/test-run
    // or just /api/proxy/leads/test-run?
    // Let's look at how the frontend calls it.
    // If frontend calls: /api/proxy/api/leads/test-run
    // params.path = ["api", "leads", "test-run"]
    // Target: {BACKEND_URL}/api/leads/test-run

    const path = resolvedParams.path.join("/");
    const searchParams = req.nextUrl.search; // includes ?admin_key=...
    const targetUrl = `${backendBase}/api/${path}${searchParams}`;
    // Wait, if path already includes 'api', we shouldn't add it again if the backend url doesn't have it.
    // BUT, commonly backend URL is just the host.
    // Let's verify backend/main.py endpoints. They are /api/...
    // So if the user requests /api/proxy/leads/test-run (path=["leads", "test-run"])
    // We want {BACKEND_URL}/api/leads/test-run.

    // However, if the user requests /api/proxy/api/leads/test-run (path=["api", "leads", "test-run"])
    // We want {BACKEND_URL}/api/leads/test-run.
    // Let's be safe: If path starts with 'api/', use it as is. If not, prepend 'api/'.

    let finalPath = path;
    if (!path.startsWith("api/")) {
        finalPath = `api/${path}`;
    }

    const finalTarget = `${backendBase}/${finalPath}${searchParams}`;

    console.log(`[Proxy] Forwarding ${req.method} to: ${finalTarget}`);

    try {
        const headers = new Headers(req.headers);
        // Clean headers that might cause issues
        headers.delete("host");
        headers.delete("connection");

        // Pass body if not GET/HEAD
        let body = undefined;
        if (req.method !== 'GET' && req.method !== 'HEAD') {
            body = await req.blob();
        }

        const backendRes = await fetch(finalTarget, {
            method: req.method,
            headers: headers,
            body: body,
            // crucial for self-signed certs or internal network issues if needed (usually not on proper cloud)
            cache: 'no-store'
        });

        // Forward response back to client
        const data = await backendRes.blob();
        const resHeaders = new Headers(backendRes.headers);

        // Ensure CORS allows the frontend to read this (which it does by default for same-origin)
        return new NextResponse(data, {
            status: backendRes.status,
            statusText: backendRes.statusText,
            headers: resHeaders
        });

    } catch (error: any) {
        console.error("[Proxy Error]", error);
        return NextResponse.json(
            { error: "Proxy connection failed", details: error.message },
            { status: 502 }
        );
    }
}

export { handler as GET, handler as POST, handler as PUT, handler as DELETE };
