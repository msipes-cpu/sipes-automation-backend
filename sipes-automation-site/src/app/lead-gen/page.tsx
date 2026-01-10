
"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { ArrowRight, Download, Loader2, CheckCircle, AlertCircle, CreditCard, Play } from "lucide-react";

// Assuming backend URL. ideally from env.
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function LeadGenPage() {
    const [url, setUrl] = useState("");
    const [email, setEmail] = useState("");
    const [limit, setLimit] = useState<number>(100);
    const [status, setStatus] = useState<"idle" | "submitting" | "processing" | "success" | "error">("idle");
    const [runId, setRunId] = useState<string | null>(null);
    const [resultLink, setResultLink] = useState<string | null>(null);
    const [errorMsg, setErrorMsg] = useState<string>("");
    const [logs, setLogs] = useState<string[]>([]);
    const [price, setPrice] = useState<number>(0);

    // Calculate price whenever limit changes
    useEffect(() => {
        if (!limit || limit <= 0) {
            setPrice(0);
            return;
        }
        // $0.50 per 1000 leads
        // Logic: (limit / 1000) * 0.50
        // But what if limit < 1000? $0.50 minimum? Or proportional?
        // Prompt said: "50 cents a thousand leads... If it's over 10,000 leads, it's $10... whatever you think a reasonable amount would be"
        // Let's simplified: $0.50 per 1000 items. 
        let calc = (limit / 1000) * 0.50;
        if (calc < 0.50) calc = 0.50; // Minimum charge
        setPrice(parseFloat(calc.toFixed(2)));
    }, [limit]);

    const handleStart = async (skipPayment: boolean) => {
        if (!url || !email || !limit) {
            setErrorMsg("Please fill in all fields.");
            setStatus("error");
            return;
        }

        if (!skipPayment) {
            // Placeholder for Stripe
            // In a real app we would create a Stripe Intent here
            alert("Payment Integration Pending (Stripe Keys Missing). Proceeding as test...");
        }

        setStatus("submitting");
        setErrorMsg("");
        setResultLink(null);
        setLogs([]);

        try {
            const res = await fetch(`${API_BASE_URL}/api/leads/process-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ url, email, limit }),
            });

            if (!res.ok) {
                throw new Error("Failed to start process");
            }

            const data = await res.json();
            setRunId(data.run_id);
            setStatus("processing");
        } catch (err) {
            console.error(err);
            setStatus("error");
            setErrorMsg("Failed to connect to backend.");
        }
    };

    // Polling logic
    useEffect(() => {
        if (status !== "processing" || !runId) return;

        const interval = setInterval(async () => {
            try {
                const res = await fetch(`${API_BASE_URL}/api/runs/${runId}`);
                if (res.ok) {
                    const data = await res.json();
                    const runStatus = data.run?.status;

                    // Check logs for output
                    if (data.logs) {
                        data.logs.forEach((log: any) => {
                            try {
                                const logData = typeof log.data === 'string' ? JSON.parse(log.data) : log.data;
                                const stdout = logData.stdout || "";

                                // Updated Regex to be more robust
                                // Matches "Sheet URL: https://..." up to whitespace
                                const match = stdout.match(/Sheet URL:\s*(https?:\/\/[^\s]+)/);
                                if (match) {
                                    setResultLink(match[1]);
                                }
                            } catch (e) {
                                // ignore parse errors
                            }
                        });
                    }

                    if (runStatus === "COMPLETED") {
                        // Keep processing until we find the link if possible, or just complete
                        // If we found the link, great.
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

                            {/* Action Buttons */}
                            <div className="pt-4 flex flex-col md:flex-row gap-4">
                                {/* Confirm & Pay Button */}
                                <button
                                    onClick={() => handleStart(false)}
                                    disabled={status === "submitting" || status === "processing"}
                                    className={`flex-1 flex items-center justify-center gap-2 py-4 rounded-xl font-semibold text-white transition-all transform active:scale-[0.98]
                                        ${status === "submitting" || status === "processing"
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

                                {/* Nah Button */}
                                <button
                                    onClick={() => handleStart(true)}
                                    disabled={status === "submitting" || status === "processing"}
                                    className={`md:w-32 flex items-center justify-center gap-2 py-4 rounded-xl font-semibold transition-all transform active:scale-[0.98] border border-zinc-200
                                        ${status === "submitting" || status === "processing"
                                            ? "bg-zinc-100 text-zinc-400 cursor-not-allowed"
                                            : "bg-white text-zinc-600 hover:bg-zinc-50 hover:text-zinc-900"}
                                    `}
                                >
                                    <Play className="w-4 h-4 fill-current" />
                                    Nah
                                </button>
                            </div>

                        </div>
                    </div>

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
                                        {status === "processing" && `Processing ${limit} leads... We are scraping Apollo, enriching emails, and verifying data.`}
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
            </div>
        </main>
    );
}
