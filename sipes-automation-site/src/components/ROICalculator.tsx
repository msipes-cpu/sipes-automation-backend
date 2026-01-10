"use client";

import { useState } from "react";
import { DollarSign, AlertCircle } from "lucide-react";

export function ROICalculator() {
    const [clientValue, setClientValue] = useState(2500); // Monthly retainer
    const [missedClients, setMissedClients] = useState(3); // Clients lost/rejected due to capacity

    const monthlyLoss = clientValue * missedClients;
    const yearlyLoss = monthlyLoss * 12;

    return (
        <section id="roicalc" className="py-24 bg-zinc-50/50">
            <div className="max-w-4xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6">
                        Calculate Your <span className="text-red-500">Revenue Leakage</span>
                    </h2>
                    <p className="text-zinc-500 text-lg">
                        See exactly how much revenue you are burning by being "too busy" to handle more clients.
                    </p>
                </div>

                <div className="grid md:grid-cols-2 gap-8 items-center bg-white border border-zinc-100 rounded-3xl p-8 shadow-2xl shadow-zinc-200/50">
                    {/* Inputs */}
                    <div className="space-y-10">
                        <div className="space-y-4">
                            <label className="flex items-center justify-between text-zinc-700 font-bold">
                                <span>Avg. Monthly Retainer</span>
                                <span className="text-blue-600 text-xl">${clientValue}</span>
                            </label>
                            <input
                                type="range"
                                min="1000"
                                max="10000"
                                step="500"
                                value={clientValue}
                                onChange={(e) => setClientValue(parseInt(e.target.value))}
                                className="w-full h-2 bg-zinc-100 rounded-lg appearance-none cursor-pointer accent-blue-600"
                            />
                            <p className="text-xs text-zinc-400 font-medium">How much is one client worth per month?</p>
                        </div>

                        <div className="space-y-4">
                            <label className="flex items-center justify-between text-zinc-700 font-bold">
                                <span>Clients You Can't Handle</span>
                                <span className="text-red-500 text-xl">{missedClients}</span>
                            </label>
                            <input
                                type="range"
                                min="1"
                                max="10"
                                step="1"
                                value={missedClients}
                                onChange={(e) => setMissedClients(parseInt(e.target.value))}
                                className="w-full h-2 bg-zinc-100 rounded-lg appearance-none cursor-pointer accent-red-500"
                            />
                            <p className="text-xs text-zinc-400 font-medium">Clients ghosted/rejected due to "no bandwidth"?</p>
                        </div>
                    </div>

                    {/* ResultsCard */}
                    <div className="bg-zinc-900 rounded-2xl p-8 text-white relative overflow-hidden group">
                        <div className="absolute top-0 right-0 w-32 h-32 bg-red-500/20 rounded-full blur-3xl -mr-16 -mt-16 pointer-events-none group-hover:bg-red-500/30 transition-all"></div>

                        <div className="space-y-8 relative z-10">
                            <div className="space-y-2">
                                <div className="flex items-center gap-2 text-red-400">
                                    <AlertCircle size={16} />
                                    <span className="text-xs font-bold uppercase tracking-wider">Annual Revenue Lost</span>
                                </div>
                                <div className="flex items-baseline gap-2">
                                    <span className="text-5xl font-bold text-white">${yearlyLoss.toLocaleString()}</span>
                                </div>
                                <p className="text-zinc-500 text-sm">per year left on the table.</p>
                            </div>

                            <div className="w-full h-px bg-white/10" />

                            <div className="space-y-1">
                                <span className="text-zinc-400 text-xs font-bold uppercase tracking-wider">Potential Upside</span>
                                <div className="flex items-baseline gap-2">
                                    <DollarSign className="w-6 h-6 text-green-400" />
                                    <span className="text-3xl font-bold text-green-400">${monthlyLoss.toLocaleString()}</span>
                                    <span className="text-zinc-500">/ month</span>
                                </div>
                                <p className="text-xs text-zinc-500 mt-2">
                                    We unlock this capacity in <span className="text-white font-bold">48 hours</span>.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
    );
}
