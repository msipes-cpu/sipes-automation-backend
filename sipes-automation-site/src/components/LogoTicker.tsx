"use client";

import { motion } from "framer-motion";

// Using text placeholders for logos for simplicity, 
// in production replace with SVG/Images
const brands = [
    "HubSpot", "Salesforce", "Zapier", "OpenAI",
    "Make", "Slack", "Stripe", "Notion", "Airtable",
    "ClickUp", "Pipedrive", "GoHighLevel"
];

export function LogoTicker() {
    return (
        <section className="py-10 bg-zinc-50 border-y border-zinc-200/50 overflow-hidden">
            <div className="max-w-7xl mx-auto px-6 mb-6 text-center">
                <p className="text-xs font-bold text-zinc-400 uppercase tracking-widest">
                    Powering automations for your favorite tools
                </p>
            </div>
            <div className="flex overflow-hidden">
                <motion.div
                    animate={{ x: "-50%" }}
                    transition={{
                        duration: 20,
                        ease: "linear",
                        repeat: Infinity,
                    }}
                    className="flex gap-16 pr-16 whitespace-nowrap"
                >
                    {[...brands, ...brands].map((brand, i) => (
                        <div key={i} className="flex items-center gap-2 group cursor-default">
                            <span className="text-2xl font-bold text-zinc-300 group-hover:text-zinc-600 transition-colors">
                                {brand}
                            </span>
                        </div>
                    ))}
                </motion.div>
            </div>
        </section>
    );
}
