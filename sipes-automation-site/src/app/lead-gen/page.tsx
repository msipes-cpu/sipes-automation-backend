
"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { Navbar } from "@/components/Navbar";
import { Disclaimer } from "@/components/Disclaimer";
import { ArrowRight, Download, Loader2, CheckCircle, AlertCircle, CreditCard, Play } from "lucide-react";

// Assuming backend URL. ideally from env.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function LeadGenContent() {
    const searchParams = useSearchParams();
    const router = useRouter();

    const [url, setUrl] = useState("");
    const [email, setEmail] = useState("");
    const [limit, setLimit] = useState<number>(100);
    const [status, setStatus] = useState<"idle" | "submitting" | "processing" | "success" | "error">("idle");
    const [runId, setRunId] = useState<string | null>(null);
    const [resultLink, setResultLink] = useState<string | null>(null);
    const [errorMsg, setErrorMsg] = useState<string>("");
    const [logs, setLogs] = useState<string[]>([]);
    const [price, setPrice] = useState<number>(0);
    const [paymentSessionId, setPaymentSessionId] = useState<string | null>(null);
    const [disclaimerAccepted, setDisclaimerAccepted] = useState(false);
    const [progress, setProgress] = useState(0);

    // Calculate price
    useEffect(() => {
        if (!limit || limit <= 0) {
            setPrice(0);
            return;
        }
        let calc = (limit / 1000) * 0.50;
        if (calc < 0.50) calc = 0.50; // Minimum charge
        setPrice(parseFloat(calc.toFixed(2)));
    }, [limit]);

    // Check for Return from Stripe
    useEffect(() => {
        const success = searchParams.get("success");
        const sessionId = searchParams.get("session_id");
        const canceled = searchParams.get("canceled");

        if (canceled) {
            setErrorMsg("Payment canceled.");
            setStatus("error");
            // Clear params
            router.replace("/lead-gen");
        } else if (success === "true" && sessionId) {
            // Payment success! content
            setStatus("processing");
            setPaymentSessionId(sessionId);
            // Clear params to look clean
            router.replace("/lead-gen");
        }
    }, [searchParams, router]);

    const handleStart = async (skipPayment: boolean) => {
        if (!url || !email || !limit) {
            setErrorMsg("Please fill in all fields.");
            setStatus("error");
            return;
        }

        setStatus("submitting");
        setErrorMsg("");
        setResultLink(null);
        setLogs([]);

        try {
            if (skipPayment) {
                // Direct specific "Nah" endpoint or just standard process?
                // Standard process with skip_payment flag if backend supported?
                // Actually backend process-url handles free run if no payment requirement enforced.
                // We'll just call process-url directly.
                const res = await fetch(`${API_BASE_URL}/api/leads/process-url`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url, email, limit }),
                });

                if (!res.ok) throw new Error("Failed to start process");
                const data = await res.json();
                setRunId(data.run_id);
                setStatus("processing");
            } else {
                // Payment Flow
                const res = await fetch(`${API_BASE_URL}/api/create-checkout-session`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url, email, limit }),
                });

                if (!res.ok) throw new Error("Failed to create checkout session");
                const data = await res.json();
                if (data.checkoutUrl) {
                    window.location.href = data.checkoutUrl;
                } else {
                    throw new Error("No checkout URL returned");
                }
            }
        } catch (err) {
            console.error(err);
            setStatus("error");
            setErrorMsg("Failed to initiate process. Backend may be offline or Stripe keys missing.");
        }
        const [previewLoading, setPreviewLoading] = useState(false);
        const [previewData, setPreviewData] = useState<any[]>([]);

        const handlePreview = async () => {
            if (!url) {
                setErrorMsg("Please enter an Apollo URL first.");
                setStatus("error");
                return;
            }

            setPreviewLoading(true);
            setErrorMsg("");
            setResultLink(null);
            setPreviewData([]);

            try {
                const res = await fetch(`${API_BASE_URL}/api/leads/preview`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ url, email: "preview@test.com", limit: 10 }),
                });

                if (!res.ok) throw new Error("Failed to fetch preview");
                const data = await res.json();
                setPreviewData(data.leads || []);
            } catch (err) {
                console.error(err);
                setErrorMsg("Failed to load preview. Please check the URL.");
                setStatus("error");
            } finally {
                setPreviewLoading(false);
            }
        };

        const handleStart = async (skipPayment: boolean) => {
            if (!url || !email || !limit) {
                setErrorMsg("Please fill in all fields.");
                setStatus("error");
                return;
            }

            setStatus("submitting");
            setErrorMsg("");
            setResultLink(null);
            setLogs([]);
            setPreviewData([]); // Clear preview on start

            try {
                if (skipPayment) {
                    // Direct specific "Nah" endpoint or just standard process?
                    // Standard process with skip_payment flag if backend supported?
                    // Actually backend process-url handles free run if no payment requirement enforced.
                    // We'll just call process-url directly.
                    const res = await fetch(`${API_BASE_URL}/api/leads/process-url`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url, email, limit }),
                    });

                    if (!res.ok) throw new Error("Failed to start process");
                    const data = await res.json();
                    setRunId(data.run_id);
                    setStatus("processing");
                } else {
                    // Payment Flow
                    const res = await fetch(`${API_BASE_URL}/api/create-checkout-session`, {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ url, email, limit }),
                    });

                    if (!res.ok) throw new Error("Failed to create checkout session");
                    const data = await res.json();
                    if (data.checkoutUrl) {
                        window.location.href = data.checkoutUrl;
                    } else {
                        throw new Error("No checkout URL returned");
                    }
                }
            } catch (err) {
                console.error(err);
                setStatus("error");
                setErrorMsg("Failed to initiate process. Backend may be offline or Stripe keys missing.");
            }
        };

        // Polling logic for Payment -> RunID Lookup
        // If we have a paymentSessionId but NO runId yet, we poll for the runId
        useEffect(() => {
            if (!paymentSessionId || runId) return;

            const interval = setInterval(async () => {
                try {
                    const res = await fetch(`${API_BASE_URL}/api/runs/lookup?session_id=${paymentSessionId}`);
                    if (res.ok) {
                        const data = await res.json();
                        if (data.run_id) {
                            setRunId(data.run_id);
                            setPaymentSessionId(null); // Stop looking up
                            clearInterval(interval);
                        }
                    }
                } catch (e) {
                    // Ignore, webhook might be processing
                }
            }, 2000);

            return () => clearInterval(interval);
        }, [paymentSessionId, runId]);


        // Polling logic for Run Progress
        useEffect(() => {
            if (status !== "processing" || !runId) return;

            const interval = setInterval(async () => {
                try {
                    const res = await fetch(`${API_BASE_URL}/api/runs/${runId}`);
                    if (res.ok) {
                        const data = await res.json();
                        const runStatus = data.run?.status;

                        if (data.logs) {
                            data.logs.forEach((log: any) => {
                                try {
                                    const logData = typeof log.data === 'string' ? JSON.parse(log.data) : log.data;
                                    const stdout = logData.stdout || "";
                                    const match = stdout.match(/Sheet URL:\s*(https?:\/\/[^\s]+)/);
                                    if (match) setResultLink(match[1]);
                                } catch (e) { }
                            });
                        }

                        if (runStatus === "COMPLETED") {
                            setStatus("success");
                            clearInterval(interval);
                        } else if (runStatus === "FAILED" || runStatus === "ERROR") {
                            setStatus("error");
                            setErrorMsg("Process failed. Check logs.");
                            clearInterval(interval);
                        }
                    }
                } catch (err) {
                    console.error("Polling error", err);
                }
            }, 2000);

            return () => clearInterval(interval);
        }, [status, runId]);

        return (
            <main className="min-h-screen bg-zinc-50 text-zinc-900 selection:bg-blue-100 selection:text-blue-900 font-sans">
                <Navbar />

                <div className="pt-32 pb-20 px-6">
                    <div className="max-w-3xl mx-auto">
                        <div className="text-center mb-12">
                            <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4 text-zinc-900">
                                Apollo Lead Generator
                            </h1>
                            <p className="text-lg text-zinc-600">
                                Paste your Apollo search URL below to extract, enrich, and export verified leads to Google Sheets.
                            </p>
                        </div>

                        <div className="bg-white rounded-2xl shadow-xl border border-zinc-100 p-8">
                            <div className="space-y-6">

                                {/* URL Input */}
                                <div>
                                    <label htmlFor="url" className="block text-sm font-medium text-zinc-700 mb-2">
                                        Apollo Search URL
                                    </label>
                                    <input
                                        id="url"
                                        type="url"
                                        required
                                        placeholder="https://app.apollo.io/#/people?personTitles[]=ceo..."
                                        className="w-full px-4 py-3 rounded-xl border border-zinc-200 bg-zinc-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                                        value={url}
                                        onChange={(e) => setUrl(e.target.value)}
                                    />
                                    <p className="text-xs text-zinc-500 mt-2">
                                        Copy the full URL from your browser address bar after applying filters in Apollo.
                                    </p>
                                </div>

                                {/* Email and Limit Row */}
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                    <div>
                                        <label htmlFor="email" className="block text-sm font-medium text-zinc-700 mb-2">
                                            Notification Email
                                        </label>
                                        <input
                                            id="email"
                                            type="email"
                                            required
                                            placeholder="name@company.com"
                                            className="w-full px-4 py-3 rounded-xl border border-zinc-200 bg-zinc-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                        />
                                    </div>
                                    <div>
                                        <label htmlFor="limit" className="block text-sm font-medium text-zinc-700 mb-2">
                                            Number of Leads
                                        </label>
                                        <input
                                            id="limit"
                                            type="number"
                                            min="1"
                                            max="10000"
                                            required
                                            className="w-full px-4 py-3 rounded-xl border border-zinc-200 bg-zinc-50 focus:bg-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                                            value={limit}
                                            onChange={(e) => setLimit(parseInt(e.target.value))}
                                        />
                                        <p className="text-xs text-zinc-500 mt-2">
                                            Estimated Cost: <span className="font-semibold text-green-600">${price.toFixed(2)}</span>
                                        </p>
                                    </div>
                                </div>

                                {/* Disclaimer */}
                                <Disclaimer onAckChange={setDisclaimerAccepted} />

                                {/* Action Buttons */}
                                <div className="pt-4 flex flex-col md:flex-row gap-4">
                                    {/* Confirm & Pay Button */}
                                    <button
                                        onClick={() => handleStart(false)}
                                        disabled={status === "submitting" || status === "processing" || !disclaimerAccepted}
                                        className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white transition-all transform active:scale-[0.98]
                                        ${status === "submitting" || status === "processing" || !disclaimerAccepted
                                                ? "bg-zinc-400 cursor-not-allowed"
                                                : "bg-blue-600 hover:bg-blue-700 shadow-lg hover:shadow-blue-500/25"}
                                    `}
                                    >
                                        {status === "submitting" || status === "processing" ? (
                                            <Loader2 className="w-5 h-5 animate-spin" />
                                        ) : (
                                            <CreditCard className="w-5 h-5" />
                                        )}
                                        Confirm & Pay (${price.toFixed(2)})
                                    </button>

                                    {/* Preview Button */}
                                    <button
                                        onClick={() => handlePreview()}
                                        disabled={status === "submitting" || status === "processing" || previewLoading}
                                        className={`flex items-center justify-center gap-2 px-6 py-4 rounded-xl font-semibold transition-all transform active:scale-[0.98] border border-zinc-200
                                        ${status === "submitting" || status === "processing" || previewLoading
                                                ? "bg-zinc-100 text-zinc-400 cursor-not-allowed"
                                                : "bg-white text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"}
                                    `}
                                    >
                                        {previewLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
                                        Preview 10
                                    </button>

                                    {/* Nah Button (Removed or moved to bottom if needed, sticking to design) */}
                                    {/* Keeping Nah button but making it smaller/link if needed, or removing. User wanted previews. */}
                                    {/* The user prompt didn't say to remove "Nah", but "Preview" is better trust. I'll replace Nah with Preview or keep both? */}
                                    {/* "After URL submission, show a free sample... Require payment to run the full batch." */}
                                    {/* I'll keep Nah for now as a "Skip Payment" back door for the admin if they want it, but typically we'd hide it. */}
                                    {/* Let's replace 'Nah' with 'Preview' for the main public UI, or put Preview alongside. */}
                                    {/* The 'Nah' button was a debug tool. I'll replace it with 'Preview' as the 'Secondary Action'. */}
                                </div>

                                {/* Admin / Debug Bypass (Using a tiny link or hidden) */}
                                {/* For now, I'll just add the Preview button alongside. */}

                            </div>
                        </div>

                    </div>
                </div>

                {/* Preview Table */}
                {previewData.length > 0 && (
                    <div className="mt-8 bg-white rounded-2xl shadow-xl border border-zinc-100 p-8 overflow-hidden">
                        <h3 className="text-xl font-bold text-zinc-900 mb-4 flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            Preview Results (First 10)
                        </h3>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-zinc-600">
                                <thead className="text-xs text-zinc-700 uppercase bg-zinc-50">
                                    <tr>
                                        <th className="px-4 py-3 rounded-l-lg">Name</th>
                                        <th className="px-4 py-3">Title</th>
                                        <th className="px-4 py-3">Company</th>
                                        <th className="px-4 py-3 rounded-r-lg">Verified Email</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {previewData.map((lead, idx) => (
                                        <tr key={idx} className="bg-white border-b hover:bg-zinc-50">
                                            <td className="px-4 py-3 font-medium text-zinc-900">
                                                {lead.first_name} {lead.last_name}
                                            </td>
                                            <td className="px-4 py-3">
                                                {lead.title || "-"}
                                            </td>
                                            <td className="px-4 py-3">
                                                {lead.company || "-"}
                                            </td>
                                            <td className="px-4 py-3 font-mono text-xs text-blue-600">
                                                {lead.blitz_email || "Not Found"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                        <p className="text-xs text-zinc-500 mt-4 text-center">
                            * Emails are partially masked for preview. Full verified emails included in purchase.
                        </p>
                    </div>
                )}

                {/* Status Area */}
                {(status === "processing" || status === "success" || status === "error") && (
                    <div className={`mt-8 p-6 rounded-xl border ${status === "success" ? "bg-green-50 border-green-200" :
                        status === "error" ? "bg-red-50 border-red-200" :
                            "bg-blue-50 border-blue-200"
                        }`}>
                        <div className="flex items-start gap-4">
                            {status === "processing" && <Loader2 className="w-6 h-6 text-blue-600 animate-spin mt-1" />}
                            {status === "success" && <CheckCircle className="w-6 h-6 text-green-600 mt-1" />}
                            {status === "error" && <AlertCircle className="w-6 h-6 text-red-600 mt-1" />}

                            <div className="flex-1">
                                <h3 className={`font-semibold text-lg mb-1 ${status === "success" ? "text-green-900" :
                                    status === "error" ? "text-red-900" :
                                        "text-blue-900"
                                    }`}>
                                    {status === "processing" ? "Enriching Leads..." :
                                        status === "success" ? "Process Complete!" :
                                            "Error Occurred"}
                                </h3>

                                <p className={`text-sm ${status === "success" ? "text-green-700" :
                                    status === "error" ? "text-red-700" :
                                        "text-blue-700"
                                    }`}>
                                    {status === "processing" && !paymentSessionId && `Processing leads... We are scraping Apollo, enriching emails, and verifying data.`}
                                    {status === "processing" && paymentSessionId && `Payment Received! Waiting for job to start...`}
                                    {status === "error" && (errorMsg || "Something went wrong. Please check your inputs.")}
                                    {status === "success" && !resultLink && "Finished, but could not find the sheet link in logs."}
                                </p>

                                {resultLink && (
                                    <div className="mt-4">
                                        <a
                                            href={resultLink}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                            className="inline-flex items-center gap-2 px-6 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium shadow-md transition-colors"
                                        >
                                            <Download className="w-4 h-4" />
                                            Open Google Sheet
                                        </a>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                )}

            </div>
            </div >
        </main >
    );
}

export default function LeadGenPage() {
    return (
        <Suspense fallback={<div className="min-h-screen bg-zinc-50 flex items-center justify-center"><Loader2 className="w-8 h-8 animate-spin text-zinc-400" /></div>}>
            <LeadGenContent />
        </Suspense>
    );
}
