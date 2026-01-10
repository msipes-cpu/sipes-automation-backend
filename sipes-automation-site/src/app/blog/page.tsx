import Link from "next/link";
import { getAllPosts } from "@/lib/blog";
import { ArrowRight, Calendar, Tag } from "lucide-react";

export const metadata = {
    title: "Blog | Sipes Automation",
    description: "Insights on agency automation, operational efficiency, and scaling without hiring.",
};

export default function BlogIndex() {
    const posts = getAllPosts();

    return (
        <div className="bg-black text-white min-h-screen">
            {/* Header */}
            <div className="pt-32 pb-16 px-6 max-w-7xl mx-auto text-center">
                <h1 className="text-5xl md:text-7xl font-bold tracking-tighter mb-6 bg-gradient-to-r from-blue-400 to-purple-600 text-transparent bg-clip-text">
                    Automation Insights
                </h1>
                <p className="text-xl text-gray-400 max-w-2xl mx-auto">
                    Learn how top agencies are scaling ops, cutting costs, and adding capacity with automation.
                </p>
            </div>

            {/* Posts Grid */}
            <div className="max-w-7xl mx-auto px-6 pb-32">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {posts.map((post) => (
                        <Link
                            key={post.slug}
                            href={`/blog/${post.slug}`}
                            className="group relative bg-zinc-900 border border-zinc-800 rounded-2xl overflow-hidden hover:border-blue-500/50 transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10"
                        >
                            <div className="p-8 h-full flex flex-col">
                                <div className="flex items-center gap-4 text-sm text-gray-500 mb-6">
                                    <div className="flex items-center gap-2">
                                        <Calendar className="w-4 h-4" />
                                        {new Date(post.date).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' })}
                                    </div>
                                    {post.tags && post.tags.length > 0 && (
                                        <div className="flex items-center gap-2">
                                            <Tag className="w-4 h-4" />
                                            {post.tags[0]}
                                        </div>
                                    )}
                                </div>

                                <h3 className="text-2xl font-bold mb-4 group-hover:text-blue-400 transition-colors">
                                    {post.title}
                                </h3>

                                <p className="text-gray-400 mb-8 line-clamp-3 flex-grow">
                                    {post.description}
                                </p>

                                <div className="flex items-center text-blue-400 font-medium group-hover:translate-x-2 transition-transform">
                                    Read Article <ArrowRight className="w-4 h-4 ml-2" />
                                </div>
                            </div>
                        </Link>
                    ))}
                </div>

                {posts.length === 0 && (
                    <div className="text-center text-gray-500 py-20">
                        <p>No posts found yet. Check back soon!</p>
                    </div>
                )}
            </div>
        </div>
    );
}
