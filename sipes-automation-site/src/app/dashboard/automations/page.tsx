"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowRight, Activity, CheckCircle, XCircle } from "lucide-react";

type Run = {
    run_id: string;
    script_name: string;
    status: string;
    start_time: string;
    end_time: string | null;
};

export default function AutomationsPage() {
    const [runs, setRuns] = useState<Run[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetch("http://localhost:8000/api/runs")
            .then((res) => res.json())
            .then((data) => {
                setRuns(data.runs);
                setLoading(false);
            })
            .catch((err) => {
                console.error("Failed to fetch runs:", err);
                setLoading(false);
            });
    }, []);

    return (
        <div className="p-8 max-w-7xl mx-auto min-h-screen">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold font-display tracking-tight text-foreground uppercase">Mission Control</h1>
                    <p className="text-muted-foreground mt-2 font-mono text-sm">Monitor your automation fleet.</p>
                </div>
                <button
                    onClick={() => window.location.reload()}
                    className="px-4 py-2 bg-card border border-border hover:bg-primary/10 hover:border-primary/50 text-foreground rounded-sm text-sm font-mono uppercase tracking-wide transition-all shadow-lg"
                >
                    Refresh Data
                </button>
            </div>

            <div className="glass-panel rounded-sm overflow-hidden tech-border">
                {loading ? (
                    <div className="p-12 text-center text-muted-foreground font-mono animate-pulse">
                        &gt; INITIALIZING DATA STREAM...
                    </div>
                ) : runs.length === 0 ? (
                    <div className="p-12 text-center text-muted-foreground font-mono">
                        &gt; NO ACTIVE SIGNALS FOUND.
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full text-left">
                            <thead>
                                <tr className="border-b border-border bg-card/40">
                                    <th className="p-4 font-mono text-xs text-muted-foreground uppercase tracking-wider">Script Algorithm</th>
                                    <th className="p-4 font-mono text-xs text-muted-foreground uppercase tracking-wider">Status Signal</th>
                                    <th className="p-4 font-mono text-xs text-muted-foreground uppercase tracking-wider">Run ID</th>
                                    <th className="p-4 font-mono text-xs text-muted-foreground uppercase tracking-wider">Timestamp</th>
                                    <th className="p-4 font-mono text-xs text-muted-foreground uppercase tracking-wider text-right">Access</th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-border/30">
                                {runs.map((run) => (
                                    <tr key={run.run_id} className="hover:bg-primary/5 transition-colors group">
                                        <td className="p-4 font-medium text-foreground bg-transparent font-display tracking-wide">{run.script_name}</td>
                                        <td className="p-4">
                                            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded-full text-[10px] font-bold border uppercase tracking-widest ${run.status === 'completed' ? 'bg-primary/10 text-primary border-primary/20' :
                                                run.status === 'failed' ? 'bg-destructive/10 text-destructive border-destructive/20' :
                                                    'bg-blue-500/10 text-blue-400 border-blue-500/20'
                                                }`}>
                                                {run.status === 'completed' && <CheckCircle className="w-3 h-3" />}
                                                {run.status === 'failed' && <XCircle className="w-3 h-3" />}
                                                {run.status === 'running' && <Activity className="w-3 h-3 animate-pulse" />}
                                                {run.status}
                                            </div>
                                        </td>
                                        <td className="p-4 text-sm text-muted-foreground font-mono">{run.run_id.split('-')[0]}</td>
                                        <td className="p-4 text-sm text-muted-foreground font-mono">
                                            {new Date(run.start_time).toLocaleString()}
                                        </td>
                                        <td className="p-4 text-right">
                                            <Link
                                                href={`/dashboard/automations/${run.run_id}`}
                                                className="inline-flex items-center gap-1 text-sm font-mono text-primary opacity-60 group-hover:opacity-100 hover:text-primary transition-all uppercase tracking-wide"
                                            >
                                                [ View Trace ] <ArrowRight className="w-4 h-4" />
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
