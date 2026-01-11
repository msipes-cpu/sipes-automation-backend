
"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar"; // Assuming Navbar component exists
import { Loader2, RefreshCw, CheckCircle, XCircle, Clock, Database, Search } from "lucide-react";

// Assuming backend URL logic same as main page
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface Run {
    run_id: string;
    start_time: string;
    status: string;
    script_name: string;
    meta: {
        email?: string;
        limit?: string;
        url?: string;
    };
}

export default function AdminDashboard() {
    const [runs, setRuns] = useState<Run[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [lastRefresh, setLastRefresh] = useState(new Date());

    const fetchRuns = async () => {
        setLoading(true);
        try {
            // Optional: Add ?admin_key=SECRET if you enabled it backend side
            const res = await fetch(`${API_BASE_URL}/api/admin/runs?limit=100`);
            if (!res.ok) throw new Error("Failed to fetch runs");
            const data = await res.json();
            setRuns(data.runs || []);
            setLastRefresh(new Date());
            setError("");
        } catch (err: any) {
            console.error(err);
            // Show the URL we tried to help debug env var issues
            setError(`Failed to load data from ${API_BASE_URL}. details: ${err.message}`);
        } finally {
            setLoading(false);
        }
    };

    const handleTestRun = async () => {
        if (!process.env.NEXT_PUBLIC_ADMIN_KEY) {
            alert("Admin Key not configured in frontend .env");
            return;
        }
        try {
            const res = await fetch(`${API_BASE_URL}/api/leads/test-run?admin_key=${process.env.NEXT_PUBLIC_ADMIN_KEY}`, {
                method: "POST"
            });
            const data = await res.json();
            if (data.run_id) {
                window.location.href = `/tools/lead-gen?run_id=${data.run_id}`;
            } else {
                alert("Failed to start test run: " + JSON.stringify(data));
            }
        } catch (e: any) {
            alert("Error starting test run: " + e.message);
        }
    };

    // Initial Fetch & Poll
    useEffect(() => {
        fetchRuns();
        const interval = setInterval(fetchRuns, 15000); // 15s refresh
        return () => clearInterval(interval);
    }, []);

    // Stats
    const totalRuns = runs.length;
    const completedRuns = runs.filter(r => r.status === "COMPLETED" || r.status === "SUCCESS").length;
    const failedRuns = runs.filter(r => r.status === "FAILED" || r.status === "ERROR").length;
    const totalLeads = runs.reduce((acc, curr) => acc + (parseInt(curr.meta?.limit || "0") || 0), 0);

    return (
        <main className="min-h-screen bg-gray-50 text-gray-900 font-sans">
            <div className="bg-white border-b border-gray-200">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        <div className="flex items-center gap-2">
                            <span className="text-xl font-bold text-gray-900">⚡ Sipes Auto Admin</span>
                            <span className="px-2 py-1 bg-red-100 text-red-700 text-xs rounded-full font-medium">Internal</span>
                            <span className="text-xs text-gray-400 font-mono ml-2 hidden md:block" title="Current API Target">
                                [{API_BASE_URL}]
                            </span>
                        </div>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                            <span>Last updated: {lastRefresh.toLocaleTimeString()}</span>

                            <button
                                onClick={handleTestRun}
                                className="bg-indigo-600 text-white px-3 py-1.5 rounded text-sm hover:bg-indigo-700 transition"
                            >
                                Run System Test (Free)
                            </button>

                            <button
                                onClick={fetchRuns}
                                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                                title="Refresh Now"
                            >
                                <RefreshCw className={`w-4 h-4 ${loading ? "animate-spin" : ""}`} />
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">

                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
                    <StatCard
                        title="Total Runs"
                        value={totalRuns}
                        icon={<Database className="w-5 h-5 text-blue-600" />}
                    />
                    <StatCard
                        title="Leads Requested"
                        value={totalLeads.toLocaleString()}
                        icon={<Search className="w-5 h-5 text-purple-600" />}
                    />
                    <StatCard
                        title="Completed"
                        value={completedRuns}
                        icon={<CheckCircle className="w-5 h-5 text-green-600" />}
                    />
                    <StatCard
                        title="Failed"
                        value={failedRuns}
                        icon={<XCircle className="w-5 h-5 text-red-600" />}
                    />
                </div>

                {/* Table */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm text-left text-gray-600">
                            <thead className="text-xs text-gray-700 uppercase bg-gray-50 border-b border-gray-200">
                                <tr>
                                    <th className="px-6 py-3">Date</th>
                                    <th className="px-6 py-3">Email</th>
                                    <th className="px-6 py-3">Limit</th>
                                    <th className="px-6 py-3">Status</th>
                                    <th className="px-6 py-3">Apollo URL</th>
                                    <th className="px-6 py-3">Run ID</th>
                                </tr>
                            </thead>
                            <tbody>
                                {runs.map((run) => (
                                    <tr key={run.run_id} className="bg-white border-b hover:bg-gray-50">
                                        <td className="px-6 py-4 font-mono text-xs whitespace-nowrap">
                                            {new Date(run.start_time).toLocaleString()}
                                        </td>
                                        <td className="px-6 py-4 font-medium text-gray-900">
                                            {run.meta.email || "-"}
                                        </td>
                                        <td className="px-6 py-4">
                                            {run.meta.limit || "-"}
                                        </td>
                                        <td className="px-6 py-4">
                                            <RunStatusBadge status={run.status} />
                                        </td>
                                        <td className="px-6 py-4 max-w-xs truncate" title={run.meta.url}>
                                            <a href={run.meta.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline cursor-pointer">
                                                {run.meta.url || "-"}
                                            </a>
                                        </td>
                                        <td className="px-6 py-4 font-mono text-xs text-gray-400">
                                            {run.run_id.substring(0, 8)}...
                                        </td>
                                    </tr>
                                ))}
                                {runs.length === 0 && !loading && (
                                    <tr>
                                        <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                                            No runs found.
                                        </td>
                                    </tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </main>
    );
}

function StatCard({ title, value, icon }: { title: string, value: string | number, icon: any }) {
    return (
        <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-200 flex items-center justify-between">
            <div>
                <p className="text-sm font-medium text-gray-500">{title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
                {icon}
            </div>
        </div>
    );
}

function RunStatusBadge({ status }: { status: string }) {
    let colorClass = "bg-gray-100 text-gray-800";
    if (status === "COMPLETED" || status === "SUCCESS") colorClass = "bg-green-100 text-green-800";
    else if (status === "FAILED" || status === "ERROR") colorClass = "bg-red-100 text-red-800";
    else if (status === "QUEUED" || status === "PENDING") colorClass = "bg-yellow-100 text-yellow-800";
    else if (status === "PROCESSING" || status === "running") colorClass = "bg-blue-100 text-blue-800";

    return (
        <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
            {status}
        </span>
    );
}
