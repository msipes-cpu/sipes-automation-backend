"use client";

import { motion } from "framer-motion";
import { TrendingUp, Users, Clock, ArrowUpRight } from "lucide-react";
import Link from "next/link";

export function Results() {
    return (
        <section id="results" className="py-24 bg-white">
            <div className="max-w-7xl mx-auto px-6">
                <div className="text-center mb-16 max-w-3xl mx-auto">
                    <span className="text-blue-600 font-bold tracking-wider text-sm uppercase mb-3 block">Recent Results</span>
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6 leading-tight">
                        We Don't Sell "Services". <br />
                        <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">We Sell Capacity.</span>
                    </h2>
                </div>

                <div className="grid lg:grid-cols-3 gap-8">
                    {/* Case Study 1 */}
                    <Link href="/work/roofing-agency-onboarding" className="block">
                        <div className="bg-zinc-50 rounded-3xl p-8 border border-zinc-100 hover:shadow-xl transition-all hover:-translate-y-1 h-full">
                            <div className="flex items-center gap-2 mb-6 text-zinc-400 text-xs font-bold uppercase tracking-wider">
                                <span className="bg-blue-100 text-blue-700 px-2 py-1 rounded">Roofing Agency</span>
                                <span>•</span>
                                <span>Onboarding</span>
                            </div>
                            <h3 className="text-xl font-bold text-zinc-900 mb-4">"We were spending 3 hours per client just on onboarding."</h3>
                            <div className="space-y-4 text-zinc-600 text-sm mb-8">
                                <p><strong>Problem:</strong> Founder couldn't take on more clients without hiring.</p>
                                <p><strong>Solution:</strong> Full onboarding automation (Contracts → Folders → CRM).</p>
                                <div className="bg-white p-4 rounded-xl border border-zinc-200 shadow-sm">
                                    <p className="text-green-600 font-bold flex items-center gap-2"><ArrowUpRight size={16} /> Saves 15h/week</p>
                                    <p className="text-zinc-500 mt-1">Took on 5 more clients in 60 days.</p>
                                </div>
                            </div>
                        </div>
                    </Link>

                    {/* Case Study 2 */}
                    <Link href="/work/lead-gen-speed-to-lead" className="block">
                        <div className="bg-zinc-50 rounded-3xl p-8 border border-zinc-100 hover:shadow-xl transition-all hover:-translate-y-1 h-full">
                            <div className="flex items-center gap-2 mb-6 text-zinc-400 text-xs font-bold uppercase tracking-wider">
                                <span className="bg-green-100 text-green-700 px-2 py-1 rounded">Lead Gen Agency</span>
                                <span>•</span>
                                <span>Speed-to-Lead</span>
                            </div>
                            <h3 className="text-xl font-bold text-zinc-900 mb-4">"Our lead response time went from 4 hours to 5 seconds."</h3>
                            <div className="space-y-4 text-zinc-600 text-sm mb-8">
                                <p><strong>Problem:</strong> Losing 40% of deals because leads went cold.</p>
                                <p><strong>Solution:</strong> Speed-to-Lead Install (Instant SMS/Email/CRM Sync).</p>
                                <div className="bg-white p-4 rounded-xl border border-zinc-200 shadow-sm">
                                    <p className="text-green-600 font-bold flex items-center gap-2"><ArrowUpRight size={16} /> +$30k/mo Revenue</p>
                                    <p className="text-zinc-500 mt-1">Close rate increased from 15% to 25%.</p>
                                </div>
                            </div>
                        </div>
                    </Link>

                    {/* Case Study 3 */}
                    <Link href="/work/seo-agency-reporting" className="block">
                        <div className="bg-zinc-50 rounded-3xl p-8 border border-zinc-100 hover:shadow-xl transition-all hover:-translate-y-1 h-full">
                            <div className="flex items-center gap-2 mb-6 text-zinc-400 text-xs font-bold uppercase tracking-wider">
                                <span className="bg-purple-100 text-purple-700 px-2 py-1 rounded">SEO Agency</span>
                                <span>•</span>
                                <span>Reporting</span>
                            </div>
                            <h3 className="text-xl font-bold text-zinc-900 mb-4">"Reporting manual work reduced from 10 hours/month to 0."</h3>
                            <div className="space-y-4 text-zinc-600 text-sm mb-8">
                                <p><strong>Problem:</strong> Manual data pulling from GSC, Ahrefs, GA4.</p>
                                <p><strong>Solution:</strong> Automated Reporting Hub.</p>
                                <div className="bg-white p-4 rounded-xl border border-zinc-200 shadow-sm">
                                    <p className="text-green-600 font-bold flex items-center gap-2"><ArrowUpRight size={16} /> +120hrs/yr Saved</p>
                                    <p className="text-zinc-500 mt-1">Founder gained 2 full weeks of time back.</p>
                                </div>
                            </div>
                        </div>
                    </Link>
                </div>
            </div>
        </section>
    );
}
