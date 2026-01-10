"use client";

import { useState, useEffect } from "react";
import { LeadMagnetModal } from "./LeadMagnetModal";

export function ExitIntent() {
    const [isVisible, setIsVisible] = useState(false);
    const [hasShown, setHasShown] = useState(false);

    useEffect(() => {
        const handleMouseLeave = (e: MouseEvent) => {
            if (e.clientY <= 0 && !hasShown) {
                setIsVisible(true);
                setHasShown(true);
            }
        };

        document.addEventListener("mouseleave", handleMouseLeave);
        return () => document.removeEventListener("mouseleave", handleMouseLeave);
    }, [hasShown]);

    return (
        <LeadMagnetModal
            isOpen={isVisible}
            onClose={() => setIsVisible(false)}
            title="Wait! Don't Leave Empty Handed."
            subtitle="Not ready to book? Steal our internal list of 50 Money-Printing Automations used by high-growth agencies."
        />
    );
}
