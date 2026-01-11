"use client";

import { motion } from "framer-motion";
import { Search, Zap, FileSpreadsheet, ArrowRight, MousePointer2 } from "lucide-react";

export function ProcessVisual() {
    return (
        <div className="w-full relative py-16 px-4 md:px-12 overflow-hidden bg-slate-50 dark:bg-slate-900 rounded-3xl border border-slate-200 dark:border-slate-800">
            {/* Dot Grid Background */}
            <div className="absolute inset-0 opacity-[0.4]" style={{
                backgroundImage: 'radial-gradient(#94a3b8 1px, transparent 1px)',
                backgroundSize: '24px 24px'
            }}></div>

            {/* Header */}
            <div className="relative z-10 text-center mb-16">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs font-bold uppercase tracking-wider mb-4 border border-blue-200 dark:border-blue-800">
                    <Zap className="w-3 h-3" />
                    <span>Automated Workflow</span>
                </div>
                <h2 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white">
                    How We Automate This
                </h2>
                <p className="mt-4 text-slate-500 dark:text-slate-400 max-w-xl mx-auto">
                    We replace manual data entry with an intelligent, 3-step autonomous workflow.
                </p>
            </div>

            {/* Workflow Canvas */}
            <div className="relative z-10 max-w-6xl mx-auto">
                <div className="flex flex-col md:flex-row items-stretch md:items-center justify-between gap-8 md:gap-4 relative">

                    {/* SVG Connector Line (Desktop) */}
                    <div className="hidden md:block absolute top-1/2 left-0 w-full h-24 -translate-y-1/2 pointer-events-none z-0">
                        <svg className="w-full h-full" preserveAspectRatio="none">
                            <path
                                d="M 150,48 C 300,48 300,48 450,48"
                                fill="none"
                                stroke="#cbd5e1"
                                strokeWidth="2"
                                strokeDasharray="6 6"
                                className="dark:stroke-slate-700"
                            />
                            <path
                                d="M 650,48 C 800,48 800,48 950,48"
                                fill="none"
                                stroke="#cbd5e1"
                                strokeWidth="2"
                                strokeDasharray="6 6"
                                className="dark:stroke-slate-700"
                            />
                        </svg>

                        {/* Animated Packets */}
                        <motion.div
                            className="absolute top-[44px] left-[18%] w-2 h-2 bg-blue-500 rounded-full shadow-[0_0_8px_rgba(59,130,246,0.8)]"
                            animate={{ x: [0, 200], opacity: [0, 1, 0] }}
                            transition={{ duration: 2, repeat: Infinity, ease: "linear" }}
                        />
                        <motion.div
                            className="absolute top-[44px] left-[65%] w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.8)]"
                            animate={{ x: [0, 200], opacity: [0, 1, 0] }}
                            transition={{ duration: 2, delay: 1, repeat: Infinity, ease: "linear" }}
                        />
                    </div>

                    {/* Nodes */}
                    <WorkflowNode
                        step="01"
                        title="Extraction"
                        icon={<Search className="w-5 h-5 text-purple-600 dark:text-purple-400" />}
                        desc="Fetches raw data from Apollo URL"
                        color="purple"
                    />

                    <div className="hidden md:flex items-center justify-center -mx-4 z-10">
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-1.5 rounded-full shadow-sm text-slate-400">
                            <ArrowRight className="w-4 h-4" />
                        </div>
                    </div>

                    <WorkflowNode
                        step="02"
                        title="Enrichment"
                        icon={<Zap className="w-5 h-5 text-blue-600 dark:text-blue-400" />}
                        desc="Verifies email deliverables safely"
                        color="blue"
                        active={true}
                    />

                    <div className="hidden md:flex items-center justify-center -mx-4 z-10">
                        <div className="bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700 p-1.5 rounded-full shadow-sm text-slate-400">
                            <ArrowRight className="w-4 h-4" />
                        </div>
                    </div>

                    <WorkflowNode
                        step="03"
                        title="Delivery"
                        icon={<FileSpreadsheet className="w-5 h-5 text-green-600 dark:text-green-400" />}
                        desc="Compiles to Google Sheets"
                        color="green"
                    />

                </div>
            </div>

            {/* CTA Overlay */}
            <div className="relative z-10 mt-16 text-center">
                <a
                    href="https://calendly.com/sipes-automation/30min"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center gap-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 px-8 py-4 rounded-xl font-bold shadow-xl hover:scale-105 transition-transform"
                >
                    <MousePointer2 className="w-5 h-5" />
                    Build A Workflow Like This For Me
                </a>
            </div>
        </div>
    );
}

function WorkflowNode({ step, title, icon, desc, color, active = false }: any) {
    const borderColor = active
        ? "border-blue-500 ring-4 ring-blue-500/10"
        : "border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:hover:border-slate-600";

    return (
        <motion.div
            initial={{ y: 20, opacity: 0 }}
            whileInView={{ y: 0, opacity: 1 }}
            viewport={{ once: true }}
            className={`flex-1 bg-white dark:bg-slate-800 rounded-2xl border ${borderColor} p-1 shadow-lg transition-all relative group z-10 max-w-sm mx-auto w-full`}
        >
            {/* Header Bar */}
            <div className="flex items-center justify-between p-3 border-b border-slate-100 dark:border-slate-700/50">
                <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center bg-${color}-50 dark:bg-${color}-900/20`}>
                        {icon}
                    </div>
                    <span className="font-bold text-slate-700 dark:text-slate-200 text-sm">{title}</span>
                </div>
                <span className="text-[10px] font-mono text-slate-400 bg-slate-50 dark:bg-slate-900 px-2 py-1 rounded">
                    NODE_{step}
                </span>
            </div>

            {/* Body */}
            <div className="p-4">
                <div className="space-y-2">
                    {/* Simulated Params */}
                    <div className="flex items-center justify-between text-xs">
                        <span className="text-slate-400">Input</span>
                        <span className="font-mono text-slate-600 dark:text-slate-300">JSON</span>
                    </div>
                    <div className="h-px bg-slate-100 dark:bg-slate-700/50 my-2"></div>
                    <p className="text-sm text-slate-500 dark:text-slate-400 leading-relaxed">
                        {desc}
                    </p>
                </div>
            </div>

            {/* Connector Dots */}
            <div className={`hidden md:block absolute top-[50%] -left-[5px] w-2.5 h-2.5 rounded-full border-2 border-slate-300 bg-white z-20 ${step === '01' ? 'opacity-0' : ''}`}></div>
            <div className={`hidden md:block absolute top-[50%] -right-[5px] w-2.5 h-2.5 rounded-full border-2 border-slate-300 bg-white z-20 ${step === '03' ? 'opacity-0' : ''}`}></div>

        </motion.div>
    );
}
