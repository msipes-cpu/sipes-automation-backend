import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { ArrowRight, Database, Search } from "lucide-react";

export default function ToolsPage() {
    return (
        <main className="min-h-screen bg-zinc-50 text-zinc-900 font-sans">
            <Navbar />

            <div className="pt-32 pb-20 px-6">
                <div className="max-w-5xl mx-auto">
                    <div className="text-center mb-16">
                        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-6 text-zinc-900">
                            Free Automation Tools
                        </h1>
                        <p className="text-lg text-zinc-600 max-w-2xl mx-auto">
                            Powerful tools to help you scale your agency, verify leads, and automate your workflow. Free to use.
                        </p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {/* Apollo Lead Gen Card */}
                        <div className="bg-white rounded-2xl border border-zinc-200 p-8 hover:shadow-xl transition-all group">
                            <div className="w-12 h-12 bg-blue-100 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
                                <Database className="w-6 h-6 text-blue-600" />
                            </div>
                            <h3 className="text-xl font-bold mb-3">Apollo Lead Generator</h3>
                            <p className="text-zinc-600 mb-6 text-sm leading-relaxed">
                                Scrape, enrich, and verify leads directly from Apollo. Get verified emails and export to Google Sheets instantly.
                            </p>
                            <Link
                                href="/tools/lead-gen"
                                className="inline-flex items-center gap-2 text-blue-600 font-semibold text-sm hover:gap-3 transition-all"
                            >
                                Use Tool <ArrowRight className="w-4 h-4" />
                            </Link>
                        </div>

                        {/* Placeholder for future tools */}
                        <div className="bg-zinc-50 rounded-2xl border border-zinc-200 border-dashed p-8 flex flex-col items-center justify-center text-center opacity-75">
                            <div className="w-12 h-12 bg-zinc-100 rounded-xl flex items-center justify-center mb-6">
                                <Search className="w-6 h-6 text-zinc-400" />
                            </div>
                            <h3 className="text-lg font-semibold mb-2 text-zinc-500">More Coming Soon</h3>
                            <p className="text-zinc-400 text-xs text-center">
                                We are building more tools for finding decision makers and automating outreach.
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <Footer />
        </main>
    );
}
