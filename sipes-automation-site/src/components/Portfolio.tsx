"use client";

import { useState, useMemo } from "react";
import { Star, CheckCircle2, ArrowUpRight, Filter, Layers } from "lucide-react";
import projectsData from "@/data/projects.json";
import testimonialsData from "@/data/testimonials.json";

type Project = typeof projectsData[0] & {
    testimonial?: typeof testimonialsData[0];
};

export function Portfolio() {
    const [activeFilter, setActiveFilter] = useState("All");

    // Merge projects with their testimonials
    const allProjects: Project[] = useMemo(() => {
        return projectsData.map((project) => ({
            ...project,
            testimonial: testimonialsData.find((t) => t.project_id === project.id),
        }));
    }, []);

    // Extract unique industries for filter tabs
    const industries = useMemo(() => {
        const unique = new Set(allProjects.map((p) => p.industry).filter(Boolean));
        return ["All", ...Array.from(unique)];
    }, [allProjects]);

    // Extract all unique tools for the marquee/list
    const allTools = useMemo(() => {
        const tools = new Set<string>();
        allProjects.forEach(p => p.technologies.forEach(t => tools.add(t)));
        return Array.from(tools).sort();
    }, [allProjects]);

    const filteredProjects = activeFilter === "All"
        ? allProjects
        : allProjects.filter((p) => p.industry === activeFilter);

    return (
        <section className="py-24 bg-zinc-50 relative overflow-hidden" id="work">
            {/* Background Pattern */}
            <div className="absolute inset-0 opacity-[0.03] pointer-events-none"
                style={{ backgroundImage: 'radial-gradient(#000 1px, transparent 1px)', backgroundSize: '32px 32px' }}>
            </div>

            <div className="max-w-7xl mx-auto px-6 relative">
                <div className="text-center max-w-3xl mx-auto mb-16">
                    <div className="inline-flex items-center gap-2 bg-blue-100 text-blue-700 px-3 py-1 rounded-full text-xs font-bold uppercase tracking-wider mb-4">
                        <Layers className="w-3 h-3" />
                        Case Studies
                    </div>
                    <h2 className="text-3xl md:text-5xl font-bold text-zinc-900 mb-6 tracking-tight">
                        Built for Scale & Efficiency
                    </h2>
                    <p className="text-lg text-zinc-500">
                        From AI agents to complex CRM migrations, explore the systems I&apos;ve engineered for high-growth businesses.
                    </p>
                </div>

                {/* Filter Tabs */}
                <div className="flex flex-wrap justify-center gap-2 mb-12">
                    {industries.map((industry) => (
                        <button
                            key={industry}
                            onClick={() => setActiveFilter(industry!)}
                            className={`px-4 py-2 rounded-full text-sm font-medium transition-all duration-200 border ${activeFilter === industry
                                ? "bg-zinc-900 text-white border-zinc-900 shadow-lg shadow-zinc-900/20"
                                : "bg-white text-zinc-600 border-zinc-200 hover:border-zinc-300 hover:bg-zinc-50"
                                }`}
                        >
                            {industry}
                        </button>
                    ))}
                </div>

                {/* Projects Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-20">
                    {filteredProjects.map((project) => (
                        <a
                            key={project.id}
                            href={`/work/${project.slug}`}
                            className="group flex flex-col bg-white border border-zinc-200 rounded-3xl overflow-hidden hover:shadow-xl hover:shadow-zinc-200/50 transition-all duration-300 hover:-translate-y-1 block"
                        >
                            <div className="p-8 flex-1 flex flex-col">
                                {/* Header */}
                                <div className="flex items-start justify-between mb-4">
                                    <span className="inline-block px-2.5 py-1 bg-zinc-100 text-zinc-600 rounded-lg text-xs font-semibold uppercase tracking-wide">
                                        {project.industry}
                                    </span>
                                    {project.testimonial && (
                                        <div className="flex items-center gap-1 text-amber-500">
                                            <Star size={14} className="fill-amber-500" />
                                            <span className="text-xs font-bold">5.0</span>
                                        </div>
                                    )}
                                </div>

                                <h3 className="text-xl font-bold text-zinc-900 mb-3 group-hover:text-blue-600 transition-colors">
                                    {project.title}
                                </h3>
                                <p className="text-zinc-500 text-sm leading-relaxed mb-6 flex-1">
                                    {project.description}
                                </p>

                                {/* Tech Stack */}
                                <div className="flex flex-wrap gap-2 mt-auto">
                                    {project.technologies.slice(0, 3).map((tech) => (
                                        <span
                                            key={tech}
                                            className="px-2 py-1 bg-zinc-50 border border-zinc-100 rounded-md text-[10px] uppercase font-bold text-zinc-500 tracking-wide"
                                        >
                                            {tech}
                                        </span>
                                    ))}
                                    {project.technologies.length > 3 && (
                                        <span className="px-2 py-1 bg-zinc-50 border border-zinc-100 rounded-md text-[10px] uppercase font-bold text-zinc-400 tracking-wide">
                                            +{project.technologies.length - 3}
                                        </span>
                                    )}
                                </div>
                            </div>

                            {/* Testimonial Footer (if exists) */}
                            {project.testimonial && (
                                <div className="bg-blue-50/50 border-t border-blue-100/50 p-6">
                                    <div className="flex items-center gap-3 mb-3">
                                        <div className="bg-white p-1.5 rounded-full shadow-sm">
                                            <CheckCircle2 size={14} className="text-blue-600" />
                                        </div>
                                        <span className="text-xs font-bold text-blue-900 uppercase tracking-wide">Client Feedback</span>
                                    </div>
                                    <p className="text-sm text-zinc-700 italic">
                                        &quot;{project.testimonial.content.length > 100 ? project.testimonial.content.slice(0, 100) + "..." : project.testimonial.content}&quot;
                                    </p>
                                </div>
                            )}
                        </a>
                    ))}
                </div>

                {/* Moving Tools Brand Ticker Style */}
                <div className="border-t border-zinc-200 pt-16">
                    <p className="text-center text-zinc-400 text-xs font-bold uppercase tracking-widest mb-8">
                        Powering Automations With
                    </p>
                    <div className="flex flex-wrap justify-center gap-x-8 gap-y-4 opacity-60 grayscale hover:grayscale-0 transition-all duration-500">
                        {allTools.map(tool => (
                            <span key={tool} className="text-lg font-bold text-zinc-400 hover:text-zinc-900 transition-colors cursor-default">
                                {tool}
                            </span>
                        ))}
                    </div>
                </div>

            </div>
        </section>
    );
}
