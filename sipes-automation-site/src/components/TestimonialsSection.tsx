"use client";

import { Star, CheckCircle2 } from "lucide-react";
import testimonialsData from "@/data/testimonials.json";

export function TestimonialsSection() {
    // Filter only featured testimonials if you want, or just take the first 4 for now
    const testimonials = testimonialsData.slice(0, 4);

    return (
        <section className="py-24 bg-white relative overflow-hidden">
            {/* Background decoration */}
            <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-zinc-200 to-transparent" />

            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center max-w-2xl mx-auto mb-16">
                    <div className="inline-flex items-center gap-2 bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4">
                        <Star className="w-3 h-3 fill-blue-700" />
                        Client Success Stories
                    </div>
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6 tracking-tight">
                        Trusted by Growing Agencies
                    </h2>
                    <p className="text-lg text-zinc-500">
                        We don&apos;t just build automations. We build specific outcomes.
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {testimonials.map((t) => (
                        <div
                            key={t.id}
                            className="group bg-zinc-50 border border-zinc-100 p-8 rounded-3xl hover:shadow-xl hover:shadow-blue-900/5 transition-all duration-300 hover:-translate-y-1"
                        >
                            <div className="flex items-start justify-between mb-6">
                                <div>
                                    <div className="flex gap-1 mb-2">
                                        {[...Array(5)].map((_, i) => (
                                            <Star key={i} size={14} className="fill-amber-400 text-amber-400" />
                                        ))}
                                    </div>
                                    <h4 className="font-bold text-zinc-900 text-lg">{t.project_title}</h4>
                                    <p className="text-xs font-mono text-zinc-400 uppercase tracking-wide mt-1">
                                        Via {t.source}
                                    </p>
                                </div>
                                {t.is_verified && (
                                    <div className="bg-white border border-zinc-200 rounded-full px-3 py-1 flex items-center gap-1.5 shadow-sm">
                                        <CheckCircle2 size={12} className="text-green-500" />
                                        <span className="text-[10px] font-bold text-zinc-600 uppercase tracking-wide">Verified</span>
                                    </div>
                                )}
                            </div>

                            <blockquote className="text-zinc-600 leading-relaxed mb-6 font-medium">
                                "{t.content}"
                            </blockquote>

                            <div className="flex items-center gap-3 pt-6 border-t border-zinc-100">
                                <div className="w-10 h-10 bg-gradient-to-br from-blue-100 to-blue-50 rounded-full flex items-center justify-center text-blue-600 font-bold text-sm">
                                    {t.client_name.charAt(0)}
                                </div>
                                <div>
                                    <div className="font-bold text-zinc-900 text-sm">{t.client_name}</div>
                                    <div className="text-xs text-zinc-500">{t.client_company}</div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>

                <div className="mt-12 text-center">
                    <a
                        href="https://www.upwork.com/freelancers/~018115668a734"
                        target="_blank"
                        className="inline-flex items-center gap-2 text-sm font-semibold text-zinc-500 hover:text-zinc-900 transition-colors border-b border-transparent hover:border-zinc-900 pb-0.5"
                    >
                        See all verified reviews on Upwork →
                    </a>
                </div>

            </div>
        </section>
    );
}
