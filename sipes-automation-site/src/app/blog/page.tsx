import Link from "next/link";
import { getAllPosts } from "@/lib/blog";
import { ArrowRight, Calendar, Tag } from "lucide-react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

export const metadata = {
    title: "Blog | Sipes Automation",
    description: "Insights on agency automation, operational efficiency, and scaling without hiring.",
};

export default function BlogIndex() {
    const posts = getAllPosts();

    return (
        <main className="min-h-screen bg-white selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            {/* Header */}
            <section className="pt-32 pb-20 px-6 max-w-7xl mx-auto text-center relative overflow-hidden">
                <div className="absolute top-0 left-0 w-full h-full bg-dot-pattern opacity-[0.4] -z-10" />

                <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-zinc-900 mb-6">
                    Automation Insights
                </h1>
                <p className="text-xl text-zinc-500 max-w-2xl mx-auto leading-relaxed">
                    Learn how top agencies are scaling ops, cutting costs, and adding capacity with automation.
                </p>
            </section>

            {/* Posts Grid */}
            <section className="max-w-7xl mx-auto px-6 pb-32">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {posts.map((post) => (
                        <Link
                            key={post.slug}
                            href={`/blog/${post.slug}`}
                            className="group relative bg-white border border-zinc-200 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 hover:shadow-xl hover:shadow-blue-500/5 hover:-translate-y-1"
                        >
                            {post.coverImage && (
                                <div className="aspect-video w-full overflow-hidden border-b border-zinc-100">
                                    <img
                                        src={post.coverImage}
                                        alt={post.title}
                                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                                    />
                                </div>
                            )}

                            <div className="p-8 flex flex-col h-full relative">
                                <div className="flex items-center gap-4 text-sm text-zinc-500 mb-4">
                                    <div className="flex items-center gap-2">
                                        <Calendar className="w-4 h-4" />
                                        {new Date(post.date).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' })}
                                    </div>
                                    {post.tags && post.tags.length > 0 && (
                                        <div className="flex items-center gap-2 px-2 py-0.5 bg-zinc-100 rounded-full text-xs font-medium text-zinc-600">
                                            <Tag className="w-3 h-3" />
                                            {post.tags[0]}
                                        </div>
                                    )}
                                </div>

                                <h3 className="text-2xl font-bold text-zinc-900 mb-3 group-hover:text-blue-600 transition-colors leading-tight">
                                    {post.title}
                                </h3>

                                <p className="text-zinc-500 mb-8 line-clamp-3 text-base leading-relaxed">
                                    {post.description}
                                </p>

                                <div className="mt-auto flex items-center text-blue-600 font-semibold group-hover:translate-x-1 transition-transform">
                                    Read Article <ArrowRight className="w-4 h-4 ml-2" />
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>

                {posts.length === 0 && (
                    <div className="text-center text-zinc-400 py-20 bg-zinc-50 rounded-3xl border border-zinc-100">
                        <p>No posts found yet. Check back soon!</p>
                    </div>
                )}
            </section>

            <Footer />
        </main>
    );
}
