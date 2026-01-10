import { Navbar } from "@/components/Navbar";
import { fiftyWays } from "@/lib/lead-magnet-data";
import { CheckCircle2, Lock } from "lucide-react";

export const metadata = {
    title: "The Vault: 50 Ways to Add $50k | Sipes Automation",
    description: "Exclusive checklist for agency owners.",
    robots: "noindex, nofollow" // Keep it secret
};

export default function FiftyWaysPage() {
    return (
        <main className="min-h-screen bg-zinc-50 selection:bg-blue-100 selection:text-blue-900 pb-20">
            <Navbar />

            <div className="bg-zinc-900 pt-32 pb-16 px-6 text-center">
                <div className="inline-flex items-center gap-2 bg-blue-900/30 text-blue-400 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-6 border border-blue-800">
                    <Lock size={12} />
                    Secret Vault Access
                </div>
                <h1 className="text-4xl md:text-6xl font-bold text-white mb-6">
                    50 Ways to Add <span className="text-blue-500">$50k Capacity</span>
                </h1>
                <p className="text-zinc-400 max-w-2xl mx-auto text-lg">
                    The exact SOPs we install. Don't share this page.
                </p>
            </div>

            <div className="max-w-4xl mx-auto px-6 -mt-10 relative z-10">

                {fiftyWays.map((section, idx) => (
                    <div key={idx} className="bg-white rounded-2xl shadow-xl border border-zinc-100 mb-8 overflow-hidden">
                        <div className="bg-zinc-50 border-b border-zinc-100 px-8 py-4 flex items-center justify-between">
                            <h2 className="text-xl font-bold text-zinc-900">
                                {section.category}
                            </h2>
                            <span className="text-xs font-mono text-zinc-400">
                                {idx * 10 + 1}-{idx * 10 + 10}
                            </span>
                        </div>
                        <div className="divide-y divide-zinc-50">
                            {section.items.map((item, i) => (
                                <div key={i} className="px-8 py-5 flex items-start gap-4 hover:bg-blue-50/50 transition-colors group">
                                    <CheckCircle2 className="w-5 h-5 text-blue-500 shrink-0 mt-0.5" />
                                    <span className="text-zinc-600 font-medium group-hover:text-zinc-900">
                                        {item}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </div>
                ))}

                <div className="bg-blue-600 rounded-3xl p-8 text-center text-white shadow-2xl shadow-blue-600/20">
                    <h3 className="text-2xl font-bold mb-4">Want us to build 3 of these for you?</h3>
                    <p className="text-blue-100 mb-8 max-w-xl mx-auto">
                        We can deploy the "Onboarding Flow", "Reporting Bot", and "Invoice Chaser" in 48 hours.
                    </p>
                    <a
                        href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                        className="inline-block bg-white text-blue-600 font-bold px-8 py-4 rounded-xl hover:bg-zinc-100 transition-colors"
                    >
                        Book Implementation Call
                    </a>
                </div>

            </div>
        </main>
    );
}
