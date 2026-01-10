"use client";

import { AlertTriangle } from "lucide-react";

interface DisclaimerProps {
    onAckChange: (acknowledged: boolean) => void;
}

export function Disclaimer({ onAckChange }: DisclaimerProps) {
    return (
        <div className="bg-amber-50 border border-amber-200 rounded-xl p-4 mt-8 md:mt-0">
            <div className="flex gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                <div className="space-y-3">
                    <h4 className="font-semibold text-amber-900 text-sm">
                        Legal Disclaimer & Usage Agreement
                    </h4>
                    <p className="text-sm text-amber-800 leading-relaxed">
                        This tool enriches publicly available data for outreach purposes only.
                        You agree to obtain proper consent, comply with all applicable laws
                        (CAN-SPAM, GDPR, CCPA), and manually verify emails before sending.
                        We are not responsible for deliverability, bounces, or legal issues arising
                        from the use of this data.
                    </p>

                    <label className="flex items-center gap-3 cursor-pointer group">
                        <div className="relative flex items-center">
                            <input
                                type="checkbox"
                                className="peer h-5 w-5 cursor-pointer appearance-none rounded-md border border-amber-400 bg-white checked:bg-amber-600 checked:border-transparent transition-all"
                                onChange={(e) => onAckChange(e.target.checked)}
                            />
                            <svg
                                className="pointer-events-none absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-3.5 h-3.5 opacity-0 peer-checked:opacity-100 transition-opacity text-white"
                                viewBox="0 0 14 14"
                                fill="none"
                            >
                                <path
                                    d="M11.6666 3.5L5.24992 9.91667L2.33325 7"
                                    stroke="currentColor"
                                    strokeWidth="2"
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                />
                            </svg>
                        </div>
                        <span className="text-sm font-medium text-amber-900 group-hover:text-amber-800 transition-colors select-none">
                            I understand and agree to these terms.
                        </span>
                    </label>
                </div>
            </div>
        </div>
    );
}
