"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Plus, Minus } from "lucide-react";

const faqs = [
    {
        q: "Which system should I choose?",
        a: "Ask yourself: 'What's my biggest bottleneck?' If you're losing leads because you can't respond fast enough, start with Speed-to-Lead ($2,500). If you're drowning in manual client work and onboarding, get the 5-Client Capacity System ($4,997). If you have both, get the Capacity System (it includes Speed-to-Lead)."
    },
    {
        q: "Can we start small and upgrade later?",
        a: "Absolutely. That's why we have the Speed-to-Lead Install for $2,500. It's the fastest way to trust us. Once you satisfy the ROI, you can upgrade to the full Capacity System."
    },
    {
        q: "Do you offer monthly retainers?",
        a: "Yes, but only for clients who've gone through one of these initial systems first. The retainer ($2k-$3k/mo) includes new automation builds, optimization, and priority support. We discuss this after your initial system is live."
    },
    {
        q: "How is this different from hiring on Upwork?",
        a: "Upwork experts are 'task doers'—they fix a broken Zap. We are 'system builders'. We've done this 150+ times and know exactly what works. Plus, we offer a Double-Penalty Guarantee. Can an Upwork freelancer do that?"
    },
    {
        q: "What if it doesn't work?",
        a: "Then you get paid. Our Double-Penalty Guarantee means if we don't deliver on time or it doesn't work, you get 100% refunded PLUS we pay you for wasting your time."
    }
];

export function FAQ() {
    const [openIndex, setOpenIndex] = useState<number | null>(null);

    return (
        <section id="faq" className="py-24 bg-white">
            <div className="max-w-3xl mx-auto px-6">
                <h2 className="text-3xl md:text-5xl font-bold text-center text-zinc-900 mb-16">
                    Common Questions
                </h2>

                <div className="space-y-4">
                    {faqs.map((faq, i) => (
                        <div
                            key={i}
                            className="border border-zinc-200 rounded-2xl bg-zinc-50/50 overflow-hidden hover:bg-white transition-colors"
                        >
                            <button
                                onClick={() => setOpenIndex(openIndex === i ? null : i)}
                                className="w-full flex items-center justify-between p-6 text-left hover:text-blue-600 transition-colors"
                            >
                                <span className="font-bold text-lg text-zinc-800">{faq.q}</span>
                                {openIndex === i ? (
                                    <Minus className="text-zinc-500" />
                                ) : (
                                    <Plus className="text-zinc-500" />
                                )}
                            </button>
                            <AnimatePresence>
                                {openIndex === i && (
                                    <motion.div
                                        initial={{ height: 0, opacity: 0 }}
                                        animate={{ height: "auto", opacity: 1 }}
                                        exit={{ height: 0, opacity: 0 }}
                                        className="overflow-hidden"
                                    >
                                        <div className="p-6 pt-0 text-zinc-500 leading-relaxed font-medium">
                                            {faq.a}
                                        </div>
                                    </motion.div>
                                )}
                            </AnimatePresence>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
