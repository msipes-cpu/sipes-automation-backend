import { useState } from "react";
import { Link, useRoute } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  ArrowLeft, 
  Play, 
  Save, 
  Settings, 
  Plus, 
  MoreHorizontal,
  Zap,
  Mail,
  FileText,
  Database,
  MessageSquare,
  CheckCircle2,
  Clock
} from "lucide-react";

// Mock data for a specific workflow
const workflowData = {
  id: "WF-001",
  name: "Client Onboarding Automation",
  status: "active",
  nodes: [
    { id: 1, type: "trigger", label: "Contract Signed", icon: FileText, x: 100, y: 300, status: "success" },
    { id: 2, type: "action", label: "Create Slack Channel", icon: MessageSquare, x: 400, y: 200, status: "success" },
    { id: 3, type: "action", label: "Generate Drive Folder", icon: Database, x: 400, y: 400, status: "success" },
    { id: 4, type: "action", label: "Send Welcome Email", icon: Mail, x: 700, y: 300, status: "running" },
    { id: 5, type: "action", label: "Assign Tasks", icon: Zap, x: 1000, y: 300, status: "pending" },
  ],
  connections: [
    { from: 1, to: 2 },
    { from: 1, to: 3 },
    { from: 2, to: 4 },
    { from: 3, to: 4 },
    { from: 4, to: 5 },
  ]
};

export default function WorkflowEditor() {
  const [, params] = useRoute("/workflow/:id");
  const [nodes, setNodes] = useState(workflowData.nodes);

  return (
    <DashboardLayout>
      <div className="h-[calc(100vh-8rem)] flex flex-col">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-4">
            <Link href="/workflows">
              <Button variant="ghost" size="icon">
                <ArrowLeft className="h-5 w-5" />
              </Button>
            </Link>
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-display font-bold text-foreground tracking-tight">
                  {workflowData.name}
                </h1>
                <Badge variant="outline" className="border-primary/30 text-primary bg-primary/10">
                  ACTIVE
                </Badge>
              </div>
              <p className="text-sm text-muted-foreground font-mono mt-1">ID: {params?.id || "WF-001"} • Last run: 2 mins ago</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Button variant="outline" className="border-border">
              <Settings className="h-4 w-4 mr-2" /> Settings
            </Button>
            <Button variant="secondary">
              <Save className="h-4 w-4 mr-2" /> Save
            </Button>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_15px_rgba(16,185,129,0.4)]">
              <Play className="h-4 w-4 mr-2" /> Test Run
            </Button>
          </div>
        </div>

        {/* Canvas Area */}
        <div className="flex-1 bg-[#0B1120] rounded-lg border border-border relative overflow-hidden shadow-inner">
          {/* Grid Background */}
          <div 
            className="absolute inset-0 opacity-20 pointer-events-none"
            style={{ 
              backgroundImage: `linear-gradient(#1E293B 1px, transparent 1px), linear-gradient(90deg, #1E293B 1px, transparent 1px)`,
              backgroundSize: '40px 40px'
            }} 
          />

          {/* Nodes & Connections Layer */}
          <div className="absolute inset-0">
            <svg className="absolute inset-0 w-full h-full pointer-events-none">
              {workflowData.connections.map((conn, i) => {
                const start = nodes.find(n => n.id === conn.from);
                const end = nodes.find(n => n.id === conn.to);
                if (!start || !end) return null;

                // Calculate bezier curve
                const startX = start.x + 200; // Width of node
                const startY = start.y + 40;  // Half height
                const endX = end.x;
                const endY = end.y + 40;
                const controlPoint1X = startX + (endX - startX) / 2;
                const controlPoint2X = startX + (endX - startX) / 2;

                return (
                  <path
                    key={i}
                    d={`M ${startX} ${startY} C ${controlPoint1X} ${startY}, ${controlPoint2X} ${endY}, ${endX} ${endY}`}
                    fill="none"
                    stroke="#1E293B"
                    strokeWidth="2"
                    className="animate-[dash_20s_linear_infinite]"
                  />
                );
              })}
              {/* Active Flow Highlight */}
              {workflowData.connections.slice(0, 3).map((conn, i) => {
                 const start = nodes.find(n => n.id === conn.from);
                 const end = nodes.find(n => n.id === conn.to);
                 if (!start || !end) return null;
 
                 const startX = start.x + 200;
                 const startY = start.y + 40;
                 const endX = end.x;
                 const endY = end.y + 40;
                 const controlPoint1X = startX + (endX - startX) / 2;
                 const controlPoint2X = startX + (endX - startX) / 2;

                 return (
                   <path
                     key={`active-${i}`}
                     d={`M ${startX} ${startY} C ${controlPoint1X} ${startY}, ${controlPoint2X} ${endY}, ${endX} ${endY}`}
                     fill="none"
                     stroke="#10B981"
                     strokeWidth="2"
                     strokeDasharray="10,10"
                     className="animate-[dash_1s_linear_infinite]"
                   />
                 );
              })}
            </svg>

            {/* Render Nodes */}
            {nodes.map((node) => (
              <div
                key={node.id}
                className={`
                  absolute w-[200px] bg-card border rounded-lg shadow-lg p-4 cursor-pointer hover:ring-2 hover:ring-primary/50 transition-all group
                  ${node.status === 'running' ? 'border-primary ring-2 ring-primary/30' : 'border-border'}
                `}
                style={{ left: node.x, top: node.y }}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className={`p-2 rounded-md ${
                    node.status === 'success' ? 'bg-primary/10 text-primary' :
                    node.status === 'running' ? 'bg-blue-500/10 text-blue-500' :
                    'bg-secondary text-muted-foreground'
                  }`}>
                    <node.icon className="h-5 w-5" />
                  </div>
                  <Button variant="ghost" size="icon" className="h-6 w-6 -mr-2 text-muted-foreground hover:text-foreground">
                    <MoreHorizontal className="h-4 w-4" />
                  </Button>
                </div>
                
                <h4 className="font-medium text-sm text-foreground mb-1">{node.label}</h4>
                <p className="text-xs text-muted-foreground font-mono mb-3">{node.type.toUpperCase()}</p>
                
                <div className="flex items-center justify-between pt-2 border-t border-border/50">
                  {node.status === 'success' && (
                    <span className="flex items-center text-[10px] text-primary font-mono">
                      <CheckCircle2 className="h-3 w-3 mr-1" /> 1.2s
                    </span>
                  )}
                  {node.status === 'running' && (
                    <span className="flex items-center text-[10px] text-blue-500 font-mono animate-pulse">
                      <Clock className="h-3 w-3 mr-1" /> Processing...
                    </span>
                  )}
                  {node.status === 'pending' && (
                    <span className="flex items-center text-[10px] text-muted-foreground font-mono">
                      Waiting
                    </span>
                  )}
                  <span className="text-[10px] text-muted-foreground font-mono">ID: {node.id}</span>
                </div>

                {/* Connection Points */}
                <div className="absolute top-1/2 -left-1.5 w-3 h-3 bg-border rounded-full border-2 border-background" />
                <div className="absolute top-1/2 -right-1.5 w-3 h-3 bg-primary rounded-full border-2 border-background shadow-[0_0_8px_#10B981]" />
              </div>
            ))}
          </div>

          {/* Floating Controls */}
          <div className="absolute bottom-6 right-6 flex flex-col gap-2">
            <Button size="icon" variant="secondary" className="rounded-full shadow-lg">
              <Plus className="h-5 w-5" />
            </Button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
