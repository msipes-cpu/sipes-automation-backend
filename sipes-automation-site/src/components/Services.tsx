"use client";

import { motion } from "framer-motion";
import { Zap, Layout, CheckCircle2, ArrowRight } from "lucide-react";
import Link from "next/link";

export function Services() {
    return (
        <section id="solution" className="py-24 bg-zinc-50 relative overflow-hidden">
            <div className="max-w-7xl mx-auto px-6 relative z-10">
                <div className="text-center mb-16 max-w-3xl mx-auto">
                    <span className="text-blue-600 font-bold tracking-wider text-sm uppercase mb-3 block">Choose Your Starting Point</span>
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6 leading-tight">
                        Solve Your Biggest Bottleneck
                    </h2>
                    <p className="text-zinc-500 text-lg">
                        Most marketing agencies hit a revenue ceiling because the founder becomes the bottleneck. We remove that bottleneck with proven automation systems.
                    </p>
                </div>

                <div className="grid lg:grid-cols-2 gap-8 max-w-5xl mx-auto">

                    {/* Offer 1: Speed to Lead */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        viewport={{ once: true }}
                        className="bg-white rounded-3xl p-8 border border-zinc-200 shadow-xl hover:shadow-2xl transition-all duration-300 relative overflow-hidden group flex flex-col"
                    >
                        <div className="absolute top-0 right-0 p-4">
                            <span className="bg-green-100 text-green-700 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                                48-Hour Install
                            </span>
                        </div>

                        <div className="w-14 h-14 bg-blue-100 rounded-2xl flex items-center justify-center mb-6 text-blue-600 group-hover:scale-110 transition-transform">
                            <Zap size={32} />
                        </div>

                        <h3 className="text-2xl font-bold text-zinc-900 mb-2">Speed-to-Lead Install</h3>
                        <p className="text-zinc-500 mb-6 font-medium">Never lose a lead to slow response times again.</p>

                        <div className="space-y-4 mb-8 flex-1">
                            <p className="text-sm text-zinc-600 leading-relaxed">
                                Research shows leads contacted in 5 seconds convert 400% better. We make it automatic.
                            </p>
                            <ul className="space-y-3">
                                {[
                                    "Facebook/Google Leads → Instant CRM Sync",
                                    "Auto-SMS + Email (Under 5 Seconds)",
                                    "Round-Robin Sales Team Assignment",
                                    "Backup Alerts (No Lead Left Behind)"
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-sm text-zinc-700 font-medium">
                                        <CheckCircle2 size={16} className="text-blue-500 mt-0.5 shrink-0" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="bg-zinc-50 rounded-xl p-4 mb-8 border border-zinc-100">
                            <p className="text-xs text-zinc-400 uppercase font-bold tracking-wider mb-1">Guarantee</p>
                            <p className="text-sm text-zinc-600 font-medium">
                                Flowing in 48 hours or we refund 100% + pay you <span className="text-zinc-900 underline decoration-blue-500/50">$500 for wasting time</span>.
                            </p>
                        </div>

                        <div className="flex items-center justify-between mt-auto pt-6 border-t border-zinc-100">
                            <div>
                                <p className="text-sm text-zinc-400 font-medium">One-Time Investment</p>
                                <p className="text-3xl font-bold text-zinc-900">$2,500</p>
                            </div>
                            <Link href="https://cal.com/michael-sipes-qrtuxw/discovery-call" className="bg-zinc-900 hover:bg-blue-600 text-white px-6 py-3 rounded-xl font-bold transition-colors flex items-center gap-2">
                                Get Started
                                <ArrowRight size={18} />
                            </Link>
                        </div>
                    </motion.div>

                    {/* Offer 2: Capacity System */}
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        whileInView={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 }}
                        viewport={{ once: true }}
                        className="bg-zinc-900 rounded-3xl p-8 border border-zinc-800 shadow-2xl relative overflow-hidden group flex flex-col"
                    >
                        {/* Shine Effect */}
                        <div className="absolute top-0 right-0 -mr-20 -mt-20 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl pointer-events-none group-hover:bg-blue-600/30 transition-all" />

                        <div className="absolute top-0 right-0 p-4 z-10">
                            <span className="bg-blue-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide shadow-lg shadow-blue-900/50">
                                Most Popular
                            </span>
                        </div>

                        <div className="w-14 h-14 bg-zinc-800 rounded-2xl flex items-center justify-center mb-6 text-white border border-zinc-700 group-hover:border-blue-500/50 transition-colors z-10 relative">
                            <Layout size={32} />
                        </div>

                        <h3 className="text-2xl font-bold text-white mb-2 relative z-10">5-Client Capacity System</h3>
                        <p className="text-zinc-400 mb-6 font-medium relative z-10">Handle 5 more clients without hiring an Ops Manager.</p>

                        <div className="space-y-4 mb-8 flex-1 relative z-10">
                            <p className="text-sm text-zinc-400 leading-relaxed">
                                The complete operating system for scaling agencies. We install 3 core systems:
                            </p>
                            <ul className="space-y-3">
                                {[
                                    "Automated Client Onboarding (Contract → Kickoff)",
                                    "INCLUDES Speed-to-Lead System",
                                    "Client Communication Hub (Auto-Reporting)",
                                    "Weekly Status & Task Automation"
                                ].map((item, i) => (
                                    <li key={i} className="flex items-start gap-3 text-sm text-zinc-300 font-medium">
                                        <CheckCircle2 size={16} className="text-blue-500 mt-0.5 shrink-0" />
                                        {item}
                                    </li>
                                ))}
                            </ul>
                        </div>

                        <div className="bg-zinc-800/50 rounded-xl p-4 mb-8 border border-zinc-700/50 relative z-10">
                            <p className="text-xs text-zinc-500 uppercase font-bold tracking-wider mb-1">Double-Penalty Guarantee</p>
                            <p className="text-sm text-zinc-300 font-medium">
                                Live in 10 days or we refund 100% + pay you <span className="text-white underline decoration-blue-500">$1,000</span>.
                            </p>
                        </div>

                        <div className="flex items-center justify-between mt-auto pt-6 border-t border-zinc-800 relative z-10">
                            <div>
                                <p className="text-sm text-zinc-500 font-medium">One-Time Investment</p>
                                <p className="text-3xl font-bold text-white">$4,997</p>
                            </div>
                            <Link href="https://cal.com/michael-sipes-qrtuxw/discovery-call" className="bg-blue-600 hover:bg-blue-500 text-white px-6 py-3 rounded-xl font-bold transition-colors flex items-center gap-2 shadow-lg shadow-blue-900/20">
                                Scale Now
                                <ArrowRight size={18} />
                            </Link>
                        </div>
                    </motion.div>

                </div>
            </div>
        </section>
    );
}
