"use client";

import { motion } from "framer-motion";
import { Play } from "lucide-react";

export function VideoSection() {
    return (
        <section className="py-24 bg-zinc-50 overflow-hidden">
            <div className="max-w-6xl mx-auto px-6 text-center">
                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    whileInView={{ opacity: 1, y: 0 }}
                    viewport={{ once: true }}
                    className="mb-12"
                >
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6">
                        See How We Build In <br />
                        <span className="text-blue-600">48 Hours</span>
                    </h2>
                    <p className="text-zinc-500 text-lg max-w-2xl mx-auto">
                        No magic. Just engineering. Watch how we analyze, build, and deploy your custom system.
                    </p>
                </motion.div>

                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    whileInView={{ opacity: 1, scale: 1 }}
                    transition={{ duration: 0.5 }}
                    viewport={{ once: true }}
                    className="relative max-w-4xl mx-auto"
                >
                    {/* Mac Window Frame Decoration */}
                    <div className="bg-white rounded-2xl shadow-2xl border border-zinc-200 overflow-hidden">
                        <div className="bg-zinc-100 border-b border-zinc-200 px-4 py-3 flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-400" />
                            <div className="w-3 h-3 rounded-full bg-yellow-400" />
                            <div className="w-3 h-3 rounded-full bg-green-400" />
                            <div className="ml-4 text-xs font-mono text-zinc-400">sipes-automation-demo.mp4</div>
                        </div>

                        {/* Video Placeholder */}
                        <div className="aspect-video bg-zinc-900 relative flex items-center justify-center group cursor-pointer">
                            <div className="absolute inset-0 bg-blue-500/10 group-hover:bg-blue-500/5 transition-colors" />

                            {/* Play Button */}
                            <div className="w-20 h-20 bg-white/10 backdrop-blur-sm rounded-full flex items-center justify-center group-hover:scale-110 transition-transform border border-white/20 shadow-2xl">
                                <Play className="w-8 h-8 text-white fill-white ml-1" />
                            </div>

                            <p className="absolute bottom-8 left-0 right-0 text-zinc-400 text-sm font-medium">Click to watch the walkthrough</p>
                        </div>
                    </div>

                    {/* Background Glow */}
                    <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[120%] h-[120%] bg-blue-400/20 blur-[100px] -z-10 pointer-events-none rounded-full" />
                </motion.div>
            </div>
        </section>
    );
}
