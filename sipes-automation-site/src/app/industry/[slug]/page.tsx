import { industries } from "@/lib/seo-content";
import { Hero } from "@/components/Hero";
import { Comparison } from "@/components/Comparison";
import { Process } from "@/components/Process";
import { StickyCTA } from "@/components/StickyCTA";
import { SlideInLeadMagnet } from "@/components/SlideInLeadMagnet";
import { CommonAutomations } from "@/components/CommonAutomations";
import { Navbar } from "@/components/Navbar";
import { FAQ } from "@/components/FAQ";
import Link from "next/link";
import { ArrowRight, CheckCircle2 } from "lucide-react";

export async function generateStaticParams() {
    return Object.keys(industries).map((slug) => ({
        slug,
    }));
}

export async function generateMetadata({ params }: { params: { slug: string } }) {
    const data = industries[params.slug];
    if (!data) return {};

    return {
        title: `${data.title} | Sipes Automation`,
        description: data.metaDesc,
    };
}

export default function IndustryPage({ params }: { params: { slug: string } }) {
    const data = industries[params.slug];

    if (!data) {
        return <div>Industry not found</div>;
    }

    return (
        <main className="min-h-screen bg-white selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            {/* Custom Hero */}
            <section className="relative min-h-[90vh] pt-32 pb-20 overflow-hidden bg-dot-pattern flex flex-col items-center justify-center text-center px-6">
                <h1 className="text-5xl md:text-7xl font-bold text-zinc-900 mb-8 max-w-5xl mx-auto tracking-tight leading-[1.1]">
                    {data.heroTitle} <br />
                    <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">Without Hiring.</span>
                </h1>
                <p className="text-xl text-zinc-500 max-w-2xl mx-auto mb-10 leading-relaxed">
                    {data.heroSub}
                </p>
                <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                    <Link
                        href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                        className="group inline-flex items-center gap-2 bg-blue-600 text-white px-8 py-4 rounded-xl text-lg font-bold hover:bg-blue-700 shadow-lg shadow-blue-600/30 transition-all hover:-translate-y-1"
                    >
                        Automate My Firm
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </Link>
                </div>
            </section>

            <div className="py-12 bg-blue-50 border-y border-blue-100 text-center">
                <p className="text-blue-900 font-bold text-lg">
                    Stop wasting time {data.painPoint}. Let us build your <span className="bg-blue-200 px-2 py-0.5 rounded text-blue-800">{data.exampleAutomation}</span> today.
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
                    &copy; {new Date().getFullYear()} Sipes Automation. Specialized in {data.title}.
                </div>
            </footer>
        </main>
    );
}
