import { integrations } from "@/lib/seo-content";
import { Hero } from "@/components/Hero";
import { Comparison } from "@/components/Comparison";
import { Process } from "@/components/Process";
import { StickyCTA } from "@/components/StickyCTA";
import { SlideInLeadMagnet } from "@/components/SlideInLeadMagnet";
import { CommonAutomations } from "@/components/CommonAutomations";
import { Navbar } from "@/components/Navbar";
import { FAQ } from "@/components/FAQ";
import Link from "next/link";
import { ArrowRight, Zap } from "lucide-react";

export async function generateStaticParams() {
    return Object.keys(integrations).map((slug) => ({
        slug,
    }));
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
    const data = integrations[params.slug];
    if (!data) return {};

    return {
        title: `${data.toolName} Automation Experts | Sipes Automation`,
        description: data.metaDesc,
    };
}

export default function IntegrationPage({ params }: { params: { slug: string } }) {
    const data = integrations[params.slug];

    if (!data) {
        return <div>Tool not found</div>;
    }

    return (
        <main className="min-h-screen bg-white selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            {/* Custom Hero */}
            <section className="relative min-h-[90vh] pt-32 pb-20 overflow-hidden bg-dot-pattern flex flex-col items-center justify-center text-center px-6">

                <div className="inline-flex items-center gap-2 bg-zinc-100 text-zinc-600 px-4 py-1.5 rounded-full mb-8 font-medium text-sm border border-zinc-200">
                    <Zap size={14} className="fill-zinc-600" />
                    <span>Specialized {data.toolName} Implementation</span>
                </div>

                <h1 className="text-5xl md:text-7xl font-bold text-zinc-900 mb-8 max-w-5xl mx-auto tracking-tight leading-[1.1]">
                    {data.heroTitle}
                </h1>
                <p className="text-xl text-zinc-500 max-w-2xl mx-auto mb-10 leading-relaxed">
                    {data.heroSub}
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                        className="group inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-600/30 transition-all hover:-translate-y-1"
                    >
                        Fix My {data.toolName}
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>
            </section>

            <div className="py-12 bg-zinc-900 border-y border-zinc-800 text-center">
                <p className="text-zinc-300 font-bold text-lg">
                    Stop struggling with {data.painPoint}. We deploy our <span className="bg-blue-600/20 text-blue-400 px-2 py-0.5 rounded border border-blue-600/30">{data.exampleAutomation}</span> blueprint in 48 hours.
                </p>
            </div>

            <CommonAutomations />
            <Comparison />
            <Process />
            <FAQ />

            <StickyCTA />
            <SlideInLeadMagnet />

            <footer className="py-12 border-t border-zinc-100 text-center text-zinc-500 text-sm bg-zinc-50">
                <div className="max-w-7xl mx-auto px-6">
                    &copy; {new Date().getFullYear()} Sipes Automation. {data.toolName} Certified Experts.
                </div>
            </footer>
        </main>
    );
}
