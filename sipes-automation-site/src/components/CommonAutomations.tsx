"use client";

import { motion } from "framer-motion";
import { UserPlus, Zap, BarChart3, FileText, CalendarCheck } from "lucide-react";

const automations = [
    {
        icon: UserPlus,
        title: "The Onboarding 'Instant-Start'",
        problem: "Manually creating Folders, Slack channels, and sending welcome emails take 2+ hours per client.",
        solution: "Contract Signed → Auto-create Drive/Slack → Send Welcome Kit → Assign Team Tasks.",
        timeSaved: "15h / month",
        color: "bg-blue-50 text-blue-600"
    },
    {
        icon: Zap,
        title: "Speed-to-Lead Responder",
        problem: "Leads go cold if you don't reply in 5 mins. Doing this manually 24/7 is impossible.",
        solution: "Form Submit → Instant SMS/Email → Update CRM → Notify Sales Rep (Round Robin).",
        timeSaved: "20h / month",
        color: "bg-amber-50 text-amber-600"
    },
    {
        icon: BarChart3,
        title: "The 'Zero-Touch' Report",
        problem: "Copy-pasting Facebook Ads data into spreadsheets every Friday afternoon.",
        solution: "Auto-pull Data (FB/Google/TikTok) → Format in Looker Studio → Email PDF to Client.",
        timeSaved: "10h / month",
        color: "bg-purple-50 text-purple-600"
    },
    {
        icon: FileText,
        title: "Invoice & Chaser Bot",
        problem: "Chasing clients for late payments and manually generating invoices.",
        solution: "Project Done → Generate QuickBooks Invoice → Send → Auto-follow up on Due Date.",
        timeSaved: "5h / month",
        color: "bg-green-50 text-green-600"
    },
    {
        icon: CalendarCheck,
        title: "The Meeting Prep Assistant",
        problem: "Scrambling to find client info 5 mins before a call.",
        solution: "Call Booked → Create Zoom → Pull CRM Info → Generate Agenda Doc → Slack You.",
        timeSaved: "8h / month",
        color: "bg-rose-50 text-rose-600"
    }
];

export function CommonAutomations() {
    return (
        <section className="py-24 bg-white border-y border-zinc-100">
            <div className="max-w-6xl mx-auto px-6">
                <div className="text-center mb-16">
                    <span className="text-blue-600 font-bold tracking-wider text-sm uppercase mb-3 block">Real World Examples</span>
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6">
                        Where Are You Wasting Time?
                    </h2>
                    <p className="text-zinc-500 text-lg max-w-2xl mx-auto">
                        These are the "Big 5" automations we build for almost every agency.
                        How many of these are you still doing manually?
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {automations.map((auto, i) => (
                        <motion.div
                            key={i}
                            initial={{ opacity: 0, y: 20 }}
                            whileInView={{ opacity: 1, y: 0 }}
                            transition={{ delay: i * 0.1 }}
                            viewport={{ once: true }}
                            className="group bg-white rounded-3xl p-8 border border-zinc-200 hover:border-blue-300 hover:shadow-xl hover:-translate-y-1 transition-all duration-300 relative overflow-hidden"
                        >
                            <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-6 ${auto.color} group-hover:scale-110 transition-transform`}>
                                <auto.icon size={24} />
                            </div>

                            <h3 className="text-xl font-bold text-zinc-900 mb-4">{auto.title}</h3>

                            <div className="space-y-4 mb-8">
                                <div>
                                    <p className="text-xs font-bold text-zinc-400 uppercase tracking-wide mb-1">The Pain</p>
                                    <p className="text-sm text-zinc-600 leading-relaxed">{auto.problem}</p>
                                </div>
                                <div>
                                    <p className="text-xs font-bold text-blue-500 uppercase tracking-wide mb-1">The Fix</p>
                                    <p className="text-sm text-zinc-900 font-medium leading-relaxed">{auto.solution}</p>
                                </div>
                            </div>

                            <div className="absolute bottom-6 right-8">
                                <div className="inline-flex items-center gap-1.5 bg-zinc-100 text-zinc-600 px-3 py-1.5 rounded-full text-xs font-bold group-hover:bg-blue-600 group-hover:text-white transition-colors">
                                    <span>⏱ Saves ~{auto.timeSaved}</span>
                                </div>
                            </div>
                        </motion.div>
                    ))}

                    {/* CTA Card for the 6th slot */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }}
                        whileInView={{ opacity: 1, scale: 1 }}
                        viewport={{ once: true }}
                        className="bg-blue-600 rounded-3xl p-8 flex flex-col items-center justify-center text-center text-white"
                    >
                        <h3 className="text-2xl font-bold mb-4">Have a weird workflow?</h3>
                        <p className="text-blue-100 mb-8 leading-relaxed">
                            If you repeat it more than 3 times a week, we can automate it.
                        </p>
                        <a href="https://cal.com/michael-sipes-qrtuxw/discovery-call" className="bg-white text-blue-600 px-8 py-3 rounded-xl font-bold hover:bg-blue-50 transition-colors w-full">
                            Challenge Us
                        </a>
                    </motion.div>
                </div>
            </div>
        </section>
    );
}
