"use client";

import { Star } from "lucide-react";

const testimonials = [
    {
        quote: "We were about to hire two more SDRs. Sipes Automation built a system that does the work of three people for a fraction of the cost. It's honestly unfair advantage.",
        author: "Sarah Jenkins",
        role: "CEO, Elevate Digital",
        result: "Saved $120k/yr",
    },
    {
        quote: "I was spending 15 hours a week just cleaning up lead lists. Now it happens automatically while I sleep. My calendar is full of qualified calls.",
        author: "Marcus Thorne",
        role: "Founder, GrowthBound",
        result: "3x Lead Quality",
    },
    {
        quote: "The onboarding bot is a game changer. Contracts signed, payments collected, and project folders created in seconds. Professionalism at scale.",
        author: "Elena Rodriguez",
        role: "COO, Creative Pulse",
        result: "90% Admin Reduced",
    },
];

export function Testimonials() {
    return (
        <section className="py-24 bg-zinc-50 border-y border-zinc-100">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-16">
                    <h2 className="text-4xl font-bold tracking-tight mb-4 text-zinc-900">
                        Trusted by Growing Agencies
                    </h2>
                    <p className="text-lg text-zinc-500 max-w-2xl mx-auto">
                        Join the founders who switched from "hiring more bodies" to "building better systems".
                    </p>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
                    {testimonials.map((t, i) => (
                        <div
                            key={i}
                            className="bg-white p-8 rounded-2xl border border-zinc-100 shadow-sm hover:shadow-md transition-shadow duration-300 flex flex-col"
                        >
                            <div className="flex items-center gap-1 text-yellow-500 mb-6">
                                {[...Array(5)].map((_, i) => (
                                    <Star key={i} className="w-5 h-5 fill-current" />
                                ))}
                            </div>

                            <p className="text-zinc-700 text-lg leading-relaxed mb-8 flex-grow">
                                "{t.quote}"
                            </p>

                            <div className="flex items-center justify-between mt-auto">
                                <div>
                                    <div className="font-bold text-zinc-900">{t.author}</div>
                                    <div className="text-sm text-zinc-500">{t.role}</div>
                                </div>
                                <div className="bg-blue-50 text-blue-700 px-3 py-1 rounded-full text-xs font-semibold border border-blue-100">
                                    {t.result}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </section>
    );
}
