"use client";

import { motion, useScroll, useTransform, AnimatePresence } from "framer-motion";
import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

export function StickyCTA() {
    const { scrollY } = useScroll();
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        return scrollY.onChange((latest) => {
            setIsVisible(latest > 600); // Show after Hero
        });
    }, [scrollY]);

    return (
        <AnimatePresence>
            {isVisible && (
                <motion.div
                    initial={{ y: 100, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    exit={{ y: 100, opacity: 0 }}
                    className="fixed bottom-0 left-0 right-0 z-50 p-4 bg-white/10 backdrop-blur-none pointer-events-none flex justify-center"
                >
                    <div className="bg-zinc-900 text-white p-2 pl-4 pr-2 rounded-full shadow-2xl flex items-center gap-4 pointer-events-auto border border-white/10 max-w-sm w-full sm:w-auto mx-auto transform hover:scale-105 transition-transform">
                        <div className="flex flex-col">
                            <span className="text-sm font-bold">Get 40 Hours Back</span>
                            <span className="text-[10px] text-zinc-400">Only 2 spots left for Jan</span>
                        </div>
                        <Link
                            href="https://cal.com/michael-sipes-qrtuxw/discovery-call"
                            className="bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-bold flex items-center gap-2"
                        >
                            Book Now <ArrowRight size={14} />
                        </Link>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
}
