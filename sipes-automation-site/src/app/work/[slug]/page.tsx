import { getProjects, Project } from "@/lib/projects";
import { Navbar } from "@/components/Navbar";
import { ArrowLeft, CheckCircle2, Star, Calendar, ExternalLink } from "lucide-react";
import Link from "next/link";
import { notFound } from "next/navigation";
import testimonialsData from "@/data/testimonials.json";

// Force static generation for SEO
export async function generateStaticParams() {
    const projects = await getProjects();
    return projects.map((project) => ({
        slug: project.slug,
    }));
}

export default async function CaseStudyPage({ params }: { params: Promise<{ slug: string }> }) {
    const { slug } = await params;
    const projects = await getProjects();
    const project = projects.find((p) => p.slug === slug);

    if (!project) {
        notFound();
    }

    const testimonial = testimonialsData.find((t) => t.project_id === project.id);

    return (
        <main className="bg-white min-h-screen text-zinc-900 selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            <article className="max-w-4xl mx-auto px-6 py-24">
                <Link
                    href="/#work"
                    className="inline-flex items-center gap-2 text-sm text-zinc-500 hover:text-blue-600 transition-colors mb-12"
                >
                    <ArrowLeft size={16} />
                    Back to Portfolio
                </Link>

                {/* Header */}
                <div className="mb-12">
                    <div className="flex items-center gap-3 mb-6">
                        <span className="inline-block px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-bold uppercase tracking-wide border border-blue-100">
                            {project.industry} Case Study
                        </span>
                        {project.featured && (
                            <span className="inline-flex items-center gap-1 px-3 py-1 bg-amber-50 text-amber-700 rounded-full text-xs font-bold uppercase tracking-wide border border-amber-100">
                                <Star size={12} className="fill-amber-500 text-amber-500" />
                                Verified Success
                            </span>
                        )}
                    </div>

                    <h1 className="text-4xl md:text-5xl font-bold text-zinc-900 mb-6 leading-tight">
                        {project.title}
                    </h1>
                </div>

                {/* Main Content Grid */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-12">

                    {/* Left Column: Details */}
                    <div className="md:col-span-2 space-y-12">

                        {/* Overview */}
                        <section>
                            <h2 className="text-xl font-bold text-zinc-900 mb-4 flex items-center gap-2">
                                <div className="w-1 h-6 bg-blue-600 rounded-full" />
                                The Challenge & Solution
                            </h2>
                            <p className="text-lg text-zinc-600 leading-relaxed">
                                {project.description}
                            </p>
                        </section>

                        {/* Testimonial Block */}
                        {testimonial && (
                            <section className="bg-zinc-50 border border-zinc-100 p-8 rounded-3xl relative overflow-hidden">
                                <div className="absolute top-0 right-0 p-8 opacity-5">
                                    <Star size={120} />
                                </div>
                                <div className="relative z-10">
                                    <div className="flex items-center gap-2 mb-4">
                                        {[...Array(5)].map((_, i) => (
                                            <Star key={i} size={16} className="fill-amber-500 text-amber-500" />
                                        ))}
                                    </div>
                                    <blockquote className="text-xl font-medium text-zinc-900 leading-relaxed mb-6">
                                        "{testimonial.content}"
                                    </blockquote>

                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                                            {testimonial.client_name.charAt(0)}
                                        </div>
                                        <div>
                                            <div className="font-bold text-zinc-900 text-sm">
                                                {testimonial.client_name}
                                            </div>
                                            <div className="text-xs text-zinc-500">
                                                {testimonial.client_company} • {testimonial.created_at.split('T')[0]}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </section>
                        )}
                    </div>

                    {/* Right Column: Sidebar */}
                    <div className="space-y-8">
                        {/* Tech Stack */}
                        <div className="bg-white border border-zinc-200 p-6 rounded-2xl shadow-sm">
                            <h3 className="text-sm font-bold text-zinc-900 uppercase tracking-wider mb-4">
                                Technologies Used
                            </h3>
                            <div className="flex flex-wrap gap-2">
                                {project.technologies.map((tech) => (
                                    <span
                                        key={tech}
                                        className="px-3 py-1.5 bg-zinc-50 border border-zinc-100 rounded-lg text-sm font-medium text-zinc-600"
                                    >
                                        {tech}
                                    </span>
                                ))}
                            </div>
                        </div>

                        {/* Quick Stats or CTA */}
                        <div className="bg-blue-600 text-white p-6 rounded-2xl shadow-lg shadow-blue-900/20">
                            <h3 className="font-bold text-lg mb-2">Need similar results?</h3>
                            <p className="text-blue-100 text-sm mb-6">
                                I can implement a similar {project.industry} automation for your business in days, not months.
                            </p>
                            <Link
                                href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                                className="block w-full text-center bg-white text-blue-700 py-3 rounded-xl font-bold hover:bg-blue-50 transition-colors"
                            >
                                Book a Strategy Call
                            </Link>
                        </div>
                    </div>
                </div>

            </article>

            {/* Footer */}
            <footer className="py-12 border-t border-zinc-100 text-center text-zinc-500 text-sm bg-zinc-50 mt-12">
                <div className="max-w-7xl mx-auto px-6">
                    <p>© {new Date().getFullYear()} Sipes Automation. {project.industry} Automation Specialist.</p>
                </div>
            </footer>
        </main>
    );
}
