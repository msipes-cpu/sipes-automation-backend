"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, CheckSquare, Download, ArrowRight } from "lucide-react";
import { LeadMagnetModal } from "./LeadMagnetModal";

export function SlideInLeadMagnet() {
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        // Show after 8 seconds offering the resource
        const timer = setTimeout(() => {
            setIsVisible(true);
        }, 8000);

        return () => clearTimeout(timer);
    }, []);

    const [showModal, setShowModal] = useState(false);

    if (!isVisible && !showModal) return null;

    return (
        <>
            <LeadMagnetModal
                isOpen={showModal}
                onClose={() => setShowModal(false)}
            />

            <AnimatePresence>
                {isVisible && (
                    <motion.div
                        initial={{ x: 400, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 400, opacity: 0 }}
                        transition={{ type: "spring", stiffness: 300, damping: 30 }}
                        className="fixed bottom-6 right-6 z-[90] max-w-sm w-full"
                    >
                        <div className="bg-white rounded-2xl shadow-blue-900/10 shadow-2xl border border-zinc-200 overflow-hidden flex">

                            {/* "Book Cover" Visual Spine */}
                            <div className="w-12 bg-blue-600 flex flex-col items-center justify-center p-2 relative overflow-hidden">
                                <div className="absolute inset-0 bg-gradient-to-tr from-blue-800 to-blue-500" />
                                <span className="relative z-10 -rotate-90 whitespace-nowrap text-white text-[10px] font-bold uppercase tracking-widest opacity-80">
                                    Secret Checklist
                                </span>
                            </div>

                            <div className="p-5 flex-1 relative">
                                <button
                                    onClick={() => setIsVisible(false)}
                                    className="absolute top-2 right-2 text-zinc-300 hover:text-zinc-600 transition-colors p-1"
                                >
                                    <X size={16} />
                                </button>

                                <div className="mb-3">
                                    <span className="inline-block bg-blue-50 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full uppercase tracking-wide mb-2">
                                        Use What We Use
                                    </span>
                                    <h4 className="font-bold text-zinc-900 leading-tight text-lg mb-1">
                                        50 Ways to Add $50k
                                    </h4>
                                    <p className="text-xs text-zinc-500 leading-relaxed font-medium">
                                        The exact SOPs we install to scale agencies without hiring.
                                    </p>
                                </div>

                                <div className="space-y-2 mb-4">
                                    {[
                                        "✅ Onboarding Flows",
                                        "✅ Reporting Bots",
                                        "✅ Churn Predictors"
                                    ].map((item, i) => (
                                        <div key={i} className="flex items-center gap-2 text-xs text-zinc-600">
                                            {item}
                                        </div>
                                    ))}
                                </div>

                                <button
                                    onClick={() => {
                                        setIsVisible(false); // Hide the small card
                                        setShowModal(true);  // Show the full page modal
                                    }}
                                    className="w-full bg-zinc-900 hover:bg-black text-white text-xs font-bold py-3 rounded-xl flex items-center justify-center gap-2 transition-all hover:shadow-lg group"
                                >
                                    <Download size={14} className="group-hover:-translate-y-0.5 transition-transform" />
                                    Access Vault
                                </button>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
