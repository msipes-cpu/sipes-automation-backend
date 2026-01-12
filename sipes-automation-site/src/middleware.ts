import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
    const hostname = request.headers.get('host') || '';
    const pathname = request.nextUrl.pathname;

    // STRICT SEO POLICY:
    // Blog content MUST live on sipesautomation.com.
    // If a user accesses /blog from a subdomain (e.g. malak.sipesautomation.com),
    // they must be redirected to the main domain to prevent duplicate content and brand confusion.

    // Check if we are on a path that requires the main domain
    if (pathname.startsWith('/blog')) {
        // Define the main domain
        const mainDomain = 'sipesautomation.com';

        // Check if the current hostname is NOT the main domain
        // We also exclude 'localhost' to allow local development
        if (hostname !== mainDomain && !hostname.includes('localhost')) {
            const url = new URL(request.nextUrl);
            url.hostname = mainDomain;
            url.protocol = 'https';
            url.port = ''; // Clear port for production redirect
            return NextResponse.redirect(url);
        }
    }

    return NextResponse.next();
}

export const config = {
    matcher: [
        /*
         * Match all request paths except for the ones starting with:
         * - api (API routes)
         * - _next/static (static files)
         * - _next/image (image optimization files)
         * - favicon.ico (favicon file)
         */
        '/((?!api|_next/static|_next/image|favicon.ico).*)',
    ],
};
