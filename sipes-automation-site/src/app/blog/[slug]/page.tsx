import { getPostBySlug, getAllPosts } from "@/lib/blog";
import { notFound } from "next/navigation";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Calendar, Tag, ArrowLeft } from "lucide-react";
import Link from "next/link";
import { Metadata } from "next";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";

interface Props {
    params: Promise<{
        slug: string;
    }>;
}

export async function generateMetadata({ params }: Props): Promise<Metadata> {
    const { slug } = await params;
    const post = getPostBySlug(slug);

    if (!post) {
        return {
            title: "Post Not Found",
        };
    }

    return {
        title: `${post.title} | Sipes Automation`,
        description: post.description,
    };
}

export async function generateStaticParams() {
    const posts = getAllPosts();
    return posts.map((post) => ({
        slug: post.slug,
    }));
}

export default async function BlogPost({ params }: Props) {
    const { slug } = await params;
    const post = getPostBySlug(slug);

    if (!post) {
        notFound();
    }

    return (
        <main className="min-h-screen bg-white selection:bg-blue-100 selection:text-blue-900">
            <Navbar />

            {/* Header Section */}
            <header className="pt-32 pb-12 px-6 max-w-4xl mx-auto">
                <Link
                    href="/blog"
                    className="inline-flex items-center text-zinc-500 hover:text-blue-600 transition-colors mb-8 text-sm font-medium group"
                >
                    <ArrowLeft className="w-4 h-4 mr-2 group-hover:-translate-x-1 transition-transform" />
                    Back to Blog
                </Link>

                <div className="space-y-6">
                    <div className="flex flex-wrap items-center gap-4 text-sm text-zinc-500">
                        <div className="flex items-center gap-2">
                            <Calendar className="w-4 h-4" />
                            {new Date(post.date).toLocaleDateString("en-US", { year: 'numeric', month: 'long', day: 'numeric' })}
                        </div>
                        {post.tags && (
                            <div className="flex flex-wrap gap-2">
                                {post.tags.map(tag => (
                                    <span key={tag} className="flex items-center gap-1 bg-zinc-100 px-2.5 py-0.5 rounded-full text-xs font-medium text-zinc-600">
                                        <Tag className="w-3 h-3" /> {tag}
                                    </span>
                                ))}
                            </div>
                        )}
                    </div>

                    <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold tracking-tight text-zinc-900 leading-[1.1]">
                        {post.title}
                    </h1>
                </div>
            </header>

            {/* Featured Image */}
            {post.coverImage && (
                <div className="max-w-5xl mx-auto px-6 mb-16">
                    <div className="aspect-[21/9] rounded-2xl overflow-hidden shadow-2xl shadow-blue-900/5 ring-1 ring-zinc-100">
                        <img
                            src={post.coverImage}
                            alt={post.title}
                            className="w-full h-full object-cover"
                        />
                    </div>
                </div>
            )}

            {/* Content Body */}
            <article className="px-6 max-w-3xl mx-auto pb-32">
                <div className="prose prose-lg prose-zinc max-w-none 
                    prose-headings:font-bold prose-headings:tracking-tight prose-headings:text-zinc-900 
                    prose-p:text-zinc-600 prose-p:leading-relaxed 
                    prose-a:text-blue-600 prose-a:font-medium hover:prose-a:text-blue-500 prose-a:no-underline 
                    prose-strong:text-zinc-900 prose-strong:font-semibold
                    prose-code:text-blue-600 prose-code:bg-blue-50 prose-code:px-1 prose-code:py-0.5 prose-code:rounded prose-code:font-medium prose-code:before:content-none prose-code:after:content-none
                    prose-ul:text-zinc-600 prose-li:marker:text-blue-300
                    prose-img:rounded-xl prose-img:shadow-lg prose-img:border prose-img:border-zinc-100">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>{post.content}</ReactMarkdown>
                </div>
            </article>

            <Footer />
        </main>
    );
}
