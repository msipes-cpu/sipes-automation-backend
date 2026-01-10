"use client";

import { motion } from "framer-motion";
import { Phone, FileText, Settings } from "lucide-react";

export function Process() {
    return (
        <section className="py-24 bg-zinc-50 relative border-y border-zinc-100">
            <div className="max-w-5xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-3xl md:text-4xl font-bold text-zinc-900 mb-4">
                        How To Get Started
                    </h2>
                    <p className="text-zinc-500">Simple, transparent, and fast.</p>
                </div>

                <div className="relative">
                    {/* Connector Line */}
                    <div className="hidden md:block absolute top-12 left-0 w-full h-0.5 bg-zinc-200 -z-0"></div>

                    <div className="grid md:grid-cols-3 gap-12">
                        {[
                            {
                                icon: Phone,
                                title: "1. Consultation Call",
                                desc: "Schedule a call with an AI system engineer (typically billed at $500/hr) to assess your systems and goals.",
                                badge: "Value: $500"
                            },
                            {
                                icon: FileText,
                                title: "2. Plan & Scheduling",
                                desc: "We deliver a comprehensive roadmap detailing scope, timeline, and budget—before you pay a dime.",
                                badge: "Free Roadmap"
                            },
                            {
                                icon: Settings,
                                title: "3. Build & Implement",
                                desc: "We kickoff, go dark for 48 hours, and emerge with your fully built, tested, and live automation system.",
                                badge: "48-Hour Sprint"
                            }
                        ].map((step, i) => (
                            <motion.div
                                key={i}
                                initial={{ opacity: 0, y: 20 }}
                                whileInView={{ opacity: 1, y: 0 }}
                                transition={{ delay: i * 0.2 }}
                                viewport={{ once: true }}
                                className="relative z-10 bg-white p-8 rounded-2xl border border-zinc-200 shadow-sm text-center group hover:border-blue-400 transition-colors"
                            >
                                <div className="w-16 h-16 mx-auto bg-white border-4 border-zinc-100 rounded-full flex items-center justify-center mb-6 text-zinc-900 group-hover:border-blue-100 group-hover:bg-blue-50 transition-colors">
                                    <step.icon size={28} className="text-zinc-700 group-hover:text-blue-600" />
                                </div>

                                {step.badge && (
                                    <span className="inline-block bg-zinc-100 text-zinc-600 text-[10px] font-bold px-2 py-1 rounded-full uppercase tracking-wide mb-3">
                                        {step.badge}
                                    </span>
                                )}

                                <h3 className="text-xl font-bold text-zinc-900 mb-3">{step.title}</h3>
                                <p className="text-zinc-500 text-sm leading-relaxed">
                                    {step.desc}
                                </p>
                            </motion.div>
                        ))}
                    </div>
                </div>
            </div>
        </section>
    );
}
