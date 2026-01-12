import Link from "next/link";
import { cn } from "@/lib/utils";

export function Navbar() {
    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/70 backdrop-blur-xl border-b border-zinc-200/50 supports-[backdrop-filter]:bg-white/60">
            <div className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
                <Link href="/" className="flex items-center gap-2 group">
                    <div className="w-8 h-8 bg-black rounded-lg grid grid-cols-2 gap-1 p-1.5 group-hover:scale-95 transition-transform duration-200">
                        <div className="bg-white rounded-full w-full h-full" />
                        <div className="bg-blue-500 rounded-full w-full h-full" />
                        <div className="bg-gray-500 rounded-full w-full h-full" />
                        <div className="bg-white rounded-full w-full h-full" />
                    </div>
                    <span className="text-xl font-bold text-zinc-900 tracking-tight">
                        Sipes Automation
                    </span>
                </Link>

                <div className="hidden md:flex items-center gap-8 text-sm font-medium text-zinc-500">
                    <Link href="#solution" className="hover:text-black transition-colors">The Solution</Link>
                    <Link href="#results" className="hover:text-black transition-colors">Results</Link>
                    <Link href="https://sipesautomation.com/blog" className="hover:text-black transition-colors">Blog</Link>
                    <Link href="#faq" className="hover:text-black transition-colors">FAQ</Link>
                    {/* <Link href="/tools" className="hover:text-black transition-colors">Tools</Link> */}
                </div>

                <Link
                    href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                    className="bg-black text-white px-5 py-2.5 rounded-lg text-sm font-semibold hover:bg-zinc-800 transition-all hover:shadow-lg"
                >
                    Book a Call
                </Link>
            </div>
        </nav >
    );
}
