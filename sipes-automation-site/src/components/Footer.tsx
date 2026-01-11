import Link from "next/link";

export function Footer() {
    return (
        <footer className="py-12 border-t border-zinc-100 text-center text-zinc-500 text-sm bg-zinc-50">
            <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-4">
                <p>© {new Date().getFullYear()} Sipes Automation. All rights reserved.</p>

                <div className="flex items-center gap-6">
                    <Link href="/tools" className="hover:text-zinc-900 transition-colors">
                        Tools
                    </Link>
                </div>

                <p className="flex items-center gap-2">
                    <span>Built in 48 hours.</span>
                    <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                </p>
            </div>
        </footer>
    );
}
