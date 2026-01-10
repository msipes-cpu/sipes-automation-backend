"use client";

import { useState, useMemo } from "react";
import projectsData from "@/data/projects.json";
import { Navbar } from "@/components/Navbar";
import { ArrowRight, CheckCircle2 } from "lucide-react";

export default function AuditPage() {
    const [selectedIndustry, setSelectedIndustry] = useState<string>("");

    // Extract unique industries
    const industries = useMemo(() => {
        const unique = new Set(projectsData.map((p) => p.industry).filter(Boolean));
        return Array.from(unique);
    }, []);

    // Filter projects
    const relevantProjects = useMemo(() => {
        if (!selectedIndustry) return [];
        return projectsData.filter(p => p.industry === selectedIndustry);
    }, [selectedIndustry]);

    return (
        <main className="bg-white min-h-screen text-zinc-900 selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            <div className="max-w-5xl mx-auto px-6 py-24">

                {/* Hero */}
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <h1 className="text-4xl md:text-6xl font-bold text-zinc-900 mb-6 tracking-tight">
                        Free Automation Audit
                    </h1>
                    <p className="text-xl text-zinc-600 mb-8">
                        See exactly how much time and money you can save. Select your industry to see valid proof of work first.
                    </p>

                    {/* Selector */}
                    <div className="max-w-md mx-auto relative">
                        <select
                            className="w-full px-6 py-4 text-lg border-2 border-zinc-200 rounded-2xl appearance-none bg-white focus:outline-none focus:border-blue-600 focus:ring-4 focus:ring-blue-50 transition-all font-medium text-zinc-700 cursor-pointer"
                            value={selectedIndustry}
                            onChange={(e) => setSelectedIndustry(e.target.value)}
                        >
                            <option value="" disabled>Select your industry...</option>
                            {industries.map(ind => (
                                <option key={ind} value={ind as string}>{ind}</option>
                            ))}
                        </select>
                        <div className="absolute right-6 top-1/2 -translate-y-1/2 pointer-events-none text-zinc-400">
                            ▼
                        </div>
                    </div>
                </div>

                {/* Dynamic Proof Section */}
                {selectedIndustry && (
                    <div className="animate-in fade-in slide-in-from-bottom-8 duration-500">
                        <div className="flex items-center justify-center gap-2 mb-8 text-green-600 font-bold uppercase tracking-wide text-sm">
                            <CheckCircle2 size={16} />
                            We have experience in {selectedIndustry}
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-12 justify-center">
                            {relevantProjects.map((project) => (
                                <a
                                    key={project.id}
                                    href={`/work/${project.slug}`}
                                    className="group bg-zinc-50 border border-zinc-100 p-8 rounded-3xl hover:bg-white hover:shadow-xl transition-all duration-300 block"
                                >
                                    <h3 className="text-lg font-bold text-zinc-900 mb-2 group-hover:text-blue-600 transition-colors">
                                        {project.title}
                                    </h3>
                                    <p className="text-zinc-500 text-sm mb-4">
                                        {project.description}
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {project.technologies.slice(0, 3).map(tech => (
                                            <span key={tech} className="text-[10px] font-bold uppercase tracking-wide text-zinc-400 bg-white px-2 py-1 rounded border border-zinc-100">
                                                {tech}
                                            </span>
                                        ))}
                                    </div>
                                </a>
                            ))}
                        </div>

                        <div className="text-center">
                            <a
                                href="https://calendly.com"
                                className="inline-flex items-center gap-2 bg-blue-600 text-white text-lg font-bold px-8 py-4 rounded-full hover:bg-blue-700 transition-all shadow-lg shadow-blue-900/20 hover:scale-105"
                            >
                                Book Your Audit Now <ArrowRight size={20} />
                            </a>
                            <p className="mt-4 text-xs text-zinc-400">
                                No obligation. 100% free strategy session.
                            </p>
                        </div>
                    </div>
                )}

            </div>
        </main>
    );
}
