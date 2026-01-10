"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ArrowRight, CheckCircle2, TrendingUp, Users, DollarSign } from "lucide-react";

const FloatingCard = ({ children, className, delay = 0 }: { children: React.ReactNode; className?: string; delay?: number }) => (
    <motion.div
        initial={{ opacity: 0, y: 20, scale: 0.95 }}
        animate={{ opacity: 1, y: 0, scale: 1 }}
        transition={{ duration: 0.8, delay, type: "spring" }}
        className={`absolute bg-white rounded-2xl shadow-xl border border-zinc-100 p-4 ${className}`}
    >
        {children}
    </motion.div>
);

export function Hero() {
    return (
        <section className="relative min-h-screen pt-32 pb-20 overflow-hidden bg-dot-pattern flex flex-col items-center justify-center">

            {/* --- Floating Elements --- */}

            {/* Top Left: Revenue Growth */}
            <FloatingCard className="hidden lg:block top-32 left-[8%] -rotate-3 w-56" delay={0.2}>
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center text-green-600">
                        <TrendingUp size={20} />
                    </div>
                    <div>
                        <p className="text-xs font-bold text-zinc-500 uppercase">Monthly Capacity</p>
                        <p className="text-lg font-bold text-zinc-900">+$50,000</p>
                    </div>
                </div>
                <div className="h-1.5 w-full bg-zinc-100 rounded-full overflow-hidden">
                    <motion.div
                        initial={{ width: "0%" }}
                        animate={{ width: "100%" }}
                        transition={{ delay: 0.5, duration: 1 }}
                        className="h-full bg-green-500"
                    />
                </div>
            </FloatingCard>

            {/* Bottom Right: New Clients */}
            <FloatingCard className="hidden lg:block bottom-32 right-[10%] rotate-3 p-4" delay={0.4}>
                <div className="flex items-center gap-4">
                    <div className="py-2 px-4 bg-blue-50 rounded-xl text-center">
                        <span className="block text-2xl font-bold text-blue-600">+5</span>
                        <span className="text-[10px] font-bold text-zinc-400 uppercase">New Clients</span>
                    </div>
                    <div className="text-left">
                        <p className="text-sm font-medium text-zinc-600">Without hiring</p>
                        <p className="text-sm font-medium text-zinc-600">extra staff.</p>
                    </div>
                </div>
            </FloatingCard>

            {/* --- Main Content --- */}
            <div className="relative z-10 max-w-4xl mx-auto px-6 text-center">

                {/* Authority Badge */}
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5 }}
                    className="inline-flex items-center gap-2 bg-blue-50 border border-blue-100 text-blue-700 px-4 py-1.5 rounded-full mb-8 font-medium text-sm"
                >
                    <Users size={14} />
                    <span>Trusted by 150+ Agencies • 48-Hour Deployment</span>
                </motion.div>

                <motion.h1
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.1 }}
                    className="text-5xl md:text-7xl font-bold text-zinc-900 mb-8 tracking-tight leading-[1.1]"
                >
                    Add <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">$50,000</span> in Monthly Capacity. <br />
                    Without Hiring.
                </motion.h1>

                <motion.p
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.2 }}
                    className="text-xl text-zinc-500 max-w-2xl mx-auto mb-10 leading-relaxed"
                >
                    We install the automation systems that let marketing agencies take on 5 more clients without adding headcount. Deployed in 48 hours to 10 days. Guaranteed.
                </motion.p>

                {/* The Guarantee Box */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5, delay: 0.3 }}
                    className="bg-zinc-900 text-white p-6 rounded-2xl max-w-2xl mx-auto mb-10 border border-zinc-800 shadow-2xl relative overflow-hidden group"
                >
                    <div className="absolute top-0 right-0 w-64 h-64 bg-blue-600/20 rounded-full blur-3xl -mr-32 -mt-32 pointer-events-none group-hover:bg-blue-600/30 transition-all" />

                    <div className="flex items-start gap-4 text-left relative z-10">
                        <div className="w-12 h-12 rounded-full bg-blue-600 flex-shrink-0 flex items-center justify-center shadow-lg border-2 border-zinc-900">
                            <CheckCircle2 size={24} className="text-white" />
                        </div>
                        <div>
                            <h3 className="text-lg font-bold text-white mb-1">Double-Penalty Guarantee</h3>
                            <p className="text-zinc-400 text-sm leading-relaxed">
                                If we don't hit our timeline (48hrs - 10 days) or our systems don't work, we refund you 100% <strong>PLUS pay you up to $1,000</strong> for wasting your time.
                            </p>
                        </div>
                    </div>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.5, delay: 0.4 }}
                    className="flex flex-col sm:flex-row items-center justify-center gap-4"
                >
                    <Link
                        href="#work"
                        onClick={(e) => {
                            e.preventDefault();
                            document.querySelector("#solution")?.scrollIntoView({ behavior: "smooth" });
                        }}
                        className="group inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-600/30 transition-all hover:-translate-y-1"
                    >
                        See How It Works
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                    <Link
                        href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                        className="inline-flex items-center gap-2 bg-white text-zinc-900 border-2 border-zinc-200 px-8 py-4 rounded-xl text-lg font-bold hover:border-zinc-300 hover:bg-zinc-50 transition-all"
                    >
                        Book a Call
                    </Link>
                </motion.div>
            </div>
        </section>
    );
}
