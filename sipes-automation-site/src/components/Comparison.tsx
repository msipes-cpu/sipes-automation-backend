"use client";

import { CheckCircle2, XCircle, TrendingUp, TrendingDown } from "lucide-react";

export function Comparison() {
    return (
        <section className="py-24 bg-white">
            <div className="max-w-6xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6">
                        How We Compare to <span className="text-blue-600">Your Alternatives</span>
                    </h2>
                    <p className="text-zinc-500 text-lg">
                        You've probably considered hiring, DIY automation, or outsourcing. Here's why agencies choose us instead.
                    </p>
                </div>

                <div className="overflow-x-auto">
                    <div className="min-w-[800px] bg-white border border-zinc-200 rounded-3xl shadow-xl overflow-hidden">
                        <div className="grid grid-cols-6 bg-zinc-50 p-6 border-b border-zinc-200 text-xs font-bold uppercase tracking-wider text-zinc-500">
                            <div className="col-span-1"></div>
                            <div className="text-center text-blue-600">Sipes Automation</div>
                            <div className="text-center">Ops Manager</div>
                            <div className="text-center">Virtual Assistant</div>
                            <div className="text-center">DIY Zapier</div>
                            <div className="text-center">Upwork Expert</div>
                        </div>

                        {[
                            { metric: "Cost", ours: "$2.5k - $5k once", ops: "$60k-$80k/yr", va: "$24k-$36k/yr", diy: "$100/mo + Time", upwork: "$50-$100/hr" },
                            { metric: "Timeline", ours: "48h - 10 Days", ops: "3-6 Months", va: "2-4 Weeks", diy: "Weeks/Months", upwork: "Variable" },
                            { metric: "Reliability", ours: "100% Guaranteed", ops: "Varies", va: "Makes Mistakes", diy: "Breaks Often", upwork: "Varies" },
                            { metric: "Availability", ours: "24/7/365", ops: "40 hrs/wk", va: "40 hrs/wk", diy: "24/7 (if working)", upwork: "Limited" },
                            { metric: "Guarantee", ours: "Double-Penalty", ops: "None", va: "None", diy: "None", upwork: "Rarely" },
                            { metric: "Turnover", ours: "Never Quits", ops: "Might Quit", va: "Might Quit", diy: "N/A", upwork: "Ghosts" },
                        ].map((row, i) => (
                            <div key={i} className="grid grid-cols-6 p-5 border-b border-zinc-100 items-center hover:bg-blue-50/10 transition-colors text-sm">
                                <div className="font-bold text-zinc-900">{row.metric}</div>
                                <div className="text-center font-bold text-blue-600 bg-blue-50/50 py-2 rounded-lg border border-blue-100/50 shadow-sm">
                                    {row.ours}
                                </div>
                                <div className="text-center text-zinc-500">{row.ops}</div>
                                <div className="text-center text-zinc-500">{row.va}</div>
                                <div className="text-center text-zinc-500">{row.diy}</div>
                                <div className="text-center text-zinc-500">{row.upwork}</div>
                            </div>
                        ))}

                        <div className="p-6 bg-zinc-50 text-center">
                            <p className="text-zinc-600 italic font-medium">
                                "You're not just buying automation. You're buying a Robot Ops Manager that costs $5k instead of $80k."
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
