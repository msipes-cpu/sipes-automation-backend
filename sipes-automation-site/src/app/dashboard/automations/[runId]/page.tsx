"use client";

import { useEffect, useState } from "react";
import ReactFlow, { Handle, Position, MarkerType, useNodesState, useEdgesState } from "reactflow";
import "reactflow/dist/style.css";
import { ArrowLeft, Clock, CheckCircle, XCircle } from "lucide-react";
import Link from "next/link";
import { useParams } from "next/navigation";

// --- Types ---
type LogEvent = {
    id: number;
    run_id: string;
    timestamp: string;
    event_type: "step_start" | "step_end" | "error";
    data: any;
};

type RunData = {
    run: {
        run_id: string;
        script_name: string;
        status: string;
        start_time: string;
        end_time: string | null;
    };
    logs: LogEvent[];
};

type StepInfo = {
    id: string;
    name: string;
    status: "running" | "success" | "failed";
    startTime: string;
    endTime?: string;
    output?: string;
    error?: string;
};

// --- Custom Minimal Node ---
const MinimalNode = ({ data }: { data: StepInfo }) => {
    return (
        <div className={`
      relative group flex items-center gap-4 p-4 rounded-sm border
      ${data.status === 'success' ? 'bg-card/40 border-primary/20 hover:border-primary/50' :
                data.status === 'failed' ? 'bg-card/40 border-destructive/20' :
                    'bg-card/40 border-blue-500/20'}
      backdrop-blur-sm w-96 transition-all hover:bg-card/60 tech-border
    `}>
            {/* Icon/Status Indicator */}
            <div className={`
        flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center border border-white/5
        ${data.status === 'success' ? 'bg-primary/10 text-primary' :
                    data.status === 'failed' ? 'bg-destructive/10 text-destructive' :
                        'bg-blue-500/10 text-blue-400 animate-pulse'}
      `}>
                {data.status === 'success' && <CheckCircle className="w-5 h-5" />}
                {data.status === 'failed' && <XCircle className="w-5 h-5" />}
                {data.status === 'running' && <div className="w-2 h-2 rounded-full bg-blue-400 animate-ping" />}
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                <h3 className="font-display font-bold text-foreground truncate text-base tracking-wide">{data.name}</h3>
                <div className="flex items-center gap-2 mt-0.5">
                    <p className="text-xs text-muted-foreground font-mono">
                        {data.startTime && new Date(data.startTime).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </p>
                    {data.status === 'running' && <span className="text-xs text-blue-400 font-mono">PROCESSING...</span>}
                </div>
            </div>

            {/* Connection Handles */}
            <Handle type="target" position={Position.Top} className="!opacity-0" />
            <Handle type="source" position={Position.Bottom} className="!opacity-0" />
        </div>
    );
};

const nodeTypes = { custom: MinimalNode };

export default function RunDetailPage() {
    const params = useParams();
    const runId = params.runId as string;

    const [data, setData] = useState<RunData | null>(null);
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [loading, setLoading] = useState(true);

    const isRunning = data?.run.status === 'running';

    useEffect(() => {
        const fetchData = () => {
            fetch(`http://localhost:8000/api/runs/${runId}`)
                .then((res) => res.json())
                .then((json: RunData) => {
                    const parsedLogs = json.logs.map(l => ({
                        ...l,
                        data: typeof l.data === 'string' ? JSON.parse(l.data) : l.data
                    }));
                    setData({ ...json, logs: parsedLogs });
                    setLoading(false);
                })
                .catch((err) => console.error(err));
        };

        fetchData();
        const interval = isRunning ? setInterval(fetchData, 2000) : null;
        return () => { if (interval) clearInterval(interval); };
    }, [runId, isRunning]);

    useEffect(() => {
        if (!data) return;

        const steps: Record<string, StepInfo> = {};
        const stepOrder: string[] = [];

        data.logs.forEach(log => {
            const stepId = log.data.step_id;
            if (!stepId) return;

            if (log.event_type === 'step_start') {
                if (!steps[stepId]) {
                    steps[stepId] = {
                        id: stepId,
                        name: log.data.step_name,
                        status: 'running',
                        startTime: log.timestamp
                    };
                    stepOrder.push(stepId);
                }
            } else if (log.event_type === 'step_end') {
                if (steps[stepId]) {
                    steps[stepId].status = log.data.status === 'success' ? 'success' : 'failed';
                    steps[stepId].endTime = log.timestamp;
                    steps[stepId].output = log.data.output;
                }
            }
        });

        const newNodes = stepOrder.map((stepId, index) => ({
            id: stepId,
            type: 'custom',
            position: { x: 0, y: index * 120 },
            data: steps[stepId],
            draggable: false,
        }));

        const newEdges = stepOrder.slice(0, -1).map((stepId, index) => ({
            id: `e-${stepId}-${stepOrder[index + 1]}`,
            source: stepId,
            target: stepOrder[index + 1],
            animated: false,
            type: 'straight',
            style: { stroke: '#1E293B', strokeWidth: 2 },
        }));

        setNodes(newNodes);
        setEdges(newEdges);

    }, [data, setNodes, setEdges]);

    if (loading) return <div className="h-screen flex items-center justify-center text-muted-foreground font-mono">INITIALIZING...</div>;
    if (!data) return <div className="h-screen flex items-center justify-center text-muted-foreground font-mono">RUN NOT FOUND</div>;

    return (
        <div className="h-screen flex flex-col bg-background text-foreground font-sans selection:bg-primary/30">
            {/* Header */}
            <div className="px-8 py-6 border-b border-border bg-background/80 backdrop-blur-xl z-20 sticky top-0 tech-border">
                <div className="flex items-center gap-6">
                    <Link href="/dashboard/automations" className="p-2 -ml-2 hover:bg-white/5 rounded-full transition-colors text-muted-foreground hover:text-foreground">
                        <ArrowLeft className="w-5 h-5" />
                    </Link>
                    <div>
                        <h1 className="text-2xl font-bold font-display tracking-tight text-foreground mb-1 uppercase">
                            {data.run.script_name}
                        </h1>
                        <div className="flex items-center gap-3 text-sm text-muted-foreground">
                            <span className={`flex items-center gap-1.5 font-mono ${data.run.status === 'completed' ? 'text-primary' :
                                    data.run.status === 'failed' ? 'text-destructive' : 'text-blue-400'
                                }`}>
                                {data.run.status === 'completed' && <CheckCircle className="w-4 h-4" />}
                                {data.run.status === 'running' && <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />}
                                <span className="uppercase tracking-wider">{data.run.status}</span>
                            </span>
                            <span className="w-1 h-1 rounded-full bg-border" />
                            <span className="font-mono text-muted-foreground">ID: {data.run.run_id.split('-')[0]}</span>
                        </div>
                    </div>
                </div>

                <div className="flex gap-3">
                    <button className="px-4 py-2 bg-card border border-border text-foreground text-sm font-mono uppercase tracking-wide hover:bg-primary/10 hover:border-primary/50 transition-all rounded-sm">
                        View Logs
                    </button>
                </div>
            </div>

            {/* Canvas */}
            <div className="flex-1 w-full flex justify-center bg-background overflow-hidden relative">
                <div className="absolute inset-0 bg-[linear-gradient(rgba(30,41,59,0.1)_1px,transparent_1px),linear-gradient(90deg,rgba(30,41,59,0.1)_1px,transparent_1px)] bg-[size:40px_40px] pointer-events-none opacity-20"></div>
                <div className="w-full max-w-3xl h-full py-12 relative z-10">
                    <ReactFlow
                        nodes={nodes}
                        edges={edges}
                        nodeTypes={nodeTypes}
                        onNodesChange={onNodesChange}
                        onEdgesChange={onEdgesChange}
                        fitView
                        minZoom={0.5}
                        maxZoom={1}
                        panOnScroll={false}
                        zoomOnScroll={false}
                        panOnDrag={false}
                        zoomOnDoubleClick={false}
                        proOptions={{ hideAttribution: true }}
                        className="!bg-transparent"
                    >
                    </ReactFlow>
                </div>
            </div>
        </div>
    );
}
