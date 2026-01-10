"use client";

import { motion, AnimatePresence } from "framer-motion";
import { X, Download, CheckCircle2, Loader2 } from "lucide-react";
import { useState } from "react";

interface LeadMagnetModalProps {
    isOpen: boolean;
    onClose: () => void;
    title?: string;
    subtitle?: string;
}

export function LeadMagnetModal({
    isOpen,
    onClose,
    title = "Unlock the $50k Capacity Vault",
    subtitle = "Get instant access to the 50 automation SOPs we install for high-growth agencies."
}: LeadMagnetModalProps) {
    const [email, setEmail] = useState("");
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");

        try {
            const res = await fetch("/api/lead-magnet", {
                method: "POST",
                body: JSON.stringify({ email }),
                headers: { "Content-Type": "application/json" }
            });

            if (res.ok) {
                setStatus("success");
                // Optional: Redirect to the vault page after 2 seconds
                setTimeout(() => {
                    window.location.href = "/resources/50-ways";
                }, 1500);
            } else {
                setStatus("error");
            }
        } catch (e) {
            setStatus("error");
        }
    };

    return (
        <AnimatePresence>
            {isOpen && (
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-zinc-900/90 backdrop-blur-sm p-4"
                >
                    <motion.div
                        initial={{ scale: 0.95, opacity: 0, y: 10 }}
                        animate={{ scale: 1, opacity: 1, y: 0 }}
                        exit={{ scale: 0.95, opacity: 0, y: 10 }}
                        className="bg-white rounded-3xl max-w-lg w-full p-8 relative shadow-2xl overflow-hidden"
                    >
                        {/* Close Button */}
                        <button
                            onClick={onClose}
                            className="absolute top-4 right-4 text-zinc-400 hover:text-zinc-600 transition-colors bg-zinc-100/50 p-2 rounded-full hover:bg-zinc-100"
                        >
                            <X size={20} />
                        </button>

                        {/* Success State */}
                        {status === "success" ? (
                            <div className="text-center py-12">
                                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6 text-green-600 animate-in zoom-in duration-300">
                                    <CheckCircle2 size={40} />
                                </div>
                                <h3 className="text-2xl font-bold text-zinc-900 mb-2">Access Granted!</h3>
                                <p className="text-zinc-500 mb-6">Redirecting you to the vault...</p>
                                <div className="h-1 w-24 bg-zinc-100 mx-auto rounded-full overflow-hidden">
                                    <div className="h-full bg-green-500 animate-progress origin-left w-full" />
                                </div>
                            </div>
                        ) : (
                            // Form State
                            <div className="text-center">
                                <div className="w-16 h-16 bg-blue-50 rounded-full flex items-center justify-center mx-auto mb-6 text-blue-600 ring-4 ring-blue-50/50">
                                    <Download size={32} />
                                </div>

                                <h3 className="text-2xl md:text-3xl font-bold text-zinc-900 mb-3 tracking-tight">
                                    {title}
                                </h3>
                                <p className="text-zinc-500 mb-8 max-w-xs mx-auto text-sm leading-relaxed">
                                    {subtitle}
                                </p>

                                <form onSubmit={handleSubmit} className="space-y-4">
                                    <div className="space-y-1 text-left">
                                        <label htmlFor="email" className="text-xs font-bold text-zinc-500 uppercase tracking-wider ml-1">Work Email</label>
                                        <input
                                            id="email"
                                            type="email"
                                            required
                                            value={email}
                                            onChange={(e) => setEmail(e.target.value)}
                                            placeholder="name@company.com"
                                            className="w-full px-4 py-3 rounded-xl border-2 border-zinc-100 focus:outline-none focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 transition-all font-medium text-lg placeholder:text-zinc-300 text-zinc-900"
                                        />
                                    </div>

                                    <button
                                        type="submit"
                                        disabled={status === "loading"}
                                        className="w-full bg-zinc-900 hover:bg-black text-white font-bold py-4 rounded-xl transition-all shadow-xl hover:shadow-2xl hover:-translate-y-0.5 disabled:opacity-70 disabled:hover:translate-y-0 text-lg flex items-center justify-center gap-2"
                                    >
                                        {status === "loading" ? (
                                            <>
                                                <Loader2 className="animate-spin" />
                                                Unlocking...
                                            </>
                                        ) : (
                                            <>
                                                Get The List
                                                <span className="text-zinc-500 font-normal ml-1">→ Free</span>
                                            </>
                                        )}
                                    </button>
                                </form>

                                <div className="mt-6 flex items-center justify-center gap-6 text-[10px] text-zinc-400 uppercase tracking-wider font-semibold">
                                    <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500" /> Instant Access</span>
                                    <span className="flex items-center gap-1"><CheckCircle2 size={12} className="text-green-500" /> No Spam</span>
                                </div>
                            </div>
                        )}
                    </motion.div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
