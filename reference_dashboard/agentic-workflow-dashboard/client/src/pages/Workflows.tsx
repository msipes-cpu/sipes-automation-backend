import { useState } from "react";
import { Link } from "wouter";
import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  Play, 
  Pause, 
  Settings, 
  Plus, 
  Search, 
  Filter, 
  MoreVertical,
  GitBranch,
  Clock,
  Maximize2,
  CheckCircle2,
  AlertCircle
} from "lucide-react";
import { Input } from "@/components/ui/input";

const workflows = [
  { 
    id: "WF-001", 
    name: "Client Onboarding Automation", 
    description: "Contract generation -> Slack channel -> Welcome email -> Task assignment",
    status: "active",
    lastRun: "2 mins ago",
    successRate: "98%",
    nodes: 12
  },
  { 
    id: "WF-002", 
    name: "Inbound Lead Enrichment", 
    description: "Webhook -> Clearbit -> CRM Update -> Slack Notify",
    status: "active",
    lastRun: "15 mins ago",
    successRate: "99.5%",
    nodes: 8
  },
  { 
    id: "WF-003", 
    name: "Monthly Reporting Cycle", 
    description: "Data fetch -> PDF Gen -> Email -> Archive",
    status: "paused",
    lastRun: "2 days ago",
    successRate: "100%",
    nodes: 15
  },
  { 
    id: "WF-004", 
    name: "Cold Outreach Sequence", 
    description: "List import -> Email 1 -> Wait -> Check Reply -> Email 2",
    status: "error",
    lastRun: "4 hours ago",
    successRate: "85%",
    nodes: 24
  }
];

export default function Workflows() {
  const [activeTab, setActiveTab] = useState("list");

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground tracking-tight">Workflows</h1>
            <p className="text-muted-foreground mt-1">Manage and monitor your agentic processes</p>
          </div>
          <Button className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_15px_rgba(16,185,129,0.4)]">
            <Plus className="mr-2 h-4 w-4" />
            New Workflow
          </Button>
        </div>

        <Tabs defaultValue="list" className="w-full" onValueChange={setActiveTab}>
          <div className="flex items-center justify-between mb-4">
            <TabsList className="bg-card border border-border">
              <TabsTrigger value="list">All Workflows</TabsTrigger>
              <TabsTrigger value="visual">Visual Editor (Demo)</TabsTrigger>
            </TabsList>
            
            <div className="flex items-center gap-2">
              <div className="relative w-64 hidden md:block">
                <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
                <Input placeholder="Search workflows..." className="pl-8 bg-card border-border" />
              </div>
              <Button variant="outline" size="icon" className="border-border">
                <Filter className="h-4 w-4" />
              </Button>
            </div>
          </div>

          <TabsContent value="list" className="space-y-4">
            <div className="grid grid-cols-1 gap-4">
              {workflows.map((wf) => (
                <Card key={wf.id} className="bg-card/40 border-border/50 hover:border-primary/30 transition-all group">
                  <CardContent className="p-6">
                    <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                      <div className="flex items-start gap-4">
                        {/* Visual Flow Preview */}
                        <Link href={`/workflow/${wf.id}`}>
                        <div 
                          className="relative w-32 h-24 rounded-md overflow-hidden border border-border/50 shrink-0 cursor-pointer hover:border-primary/50 transition-all group/preview hidden sm:block"
                        >
                          <img 
                            src="/images/workflow-visualization.jpg" 
                            alt="Flow Preview" 
                            className="w-full h-full object-cover opacity-50 group-hover/preview:opacity-100 transition-opacity scale-150" 
                          />
                          <div className="absolute inset-0 flex items-center justify-center opacity-0 group-hover/preview:opacity-100 transition-opacity bg-black/40 backdrop-blur-[1px]">
                            <Maximize2 className="h-5 w-5 text-white drop-shadow-md" />
                          </div>
                          <div className={`absolute bottom-1 right-1 w-2 h-2 rounded-full ${
                            wf.status === 'active' ? 'bg-primary shadow-[0_0_4px_#10B981]' : 
                            wf.status === 'paused' ? 'bg-yellow-500' : 
                            'bg-destructive'
                          }`} />
                        </div>
                        </Link>

                        <div>
                          <div className="flex items-center gap-3">
                            <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors">
                              {wf.name}
                            </h3>
                            <Badge variant="outline" className={`
                              uppercase text-[10px] font-bold tracking-wider
                              ${wf.status === 'active' ? 'border-primary/30 text-primary' : 
                                wf.status === 'paused' ? 'border-yellow-500/30 text-yellow-500' : 
                                'border-destructive/30 text-destructive'}
                            `}>
                              {wf.status}
                            </Badge>
                          </div>
                          <p className="text-sm text-muted-foreground mt-1 font-mono">
                            {wf.description}
                          </p>
                          <div className="flex items-center gap-4 mt-3 text-xs text-muted-foreground">
                            <span className="flex items-center gap-1">
                              <Clock className="h-3 w-3" /> Last run: {wf.lastRun}
                            </span>
                            <span className="flex items-center gap-1">
                              <CheckCircle2 className="h-3 w-3" /> Success: {wf.successRate}
                            </span>
                            <span className="flex items-center gap-1">
                              <GitBranch className="h-3 w-3" /> Nodes: {wf.nodes}
                            </span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center gap-2 self-end md:self-center">
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Play className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <Settings className="h-4 w-4" />
                        </Button>
                        <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                          <MoreVertical className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          <TabsContent value="visual" className="h-[600px] relative rounded-lg border border-border overflow-hidden bg-[#0B1120]">
            {/* Visual Editor Mockup */}
            <div className="absolute inset-0 bg-[url('/images/workflow-visualization.jpg')] bg-cover bg-center opacity-80"></div>
            
            {/* Overlay UI */}
            <div className="absolute top-4 left-4 bg-card/90 backdrop-blur border border-border p-4 rounded-lg shadow-xl max-w-xs">
              <h3 className="font-bold text-foreground mb-1">Client Onboarding Flow</h3>
              <p className="text-xs text-muted-foreground mb-3">Visualizing live execution path</p>
              <div className="space-y-2">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Status</span>
                  <span className="text-primary font-mono">RUNNING</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Current Step</span>
                  <span className="text-foreground font-mono">Generate Contract</span>
                </div>
                <div className="flex items-center justify-between text-xs">
                  <span className="text-muted-foreground">Duration</span>
                  <span className="text-foreground font-mono">12.4s</span>
                </div>
              </div>
            </div>

            <div className="absolute bottom-4 right-4 flex gap-2">
              <Button size="sm" variant="secondary" className="shadow-lg">
                <Plus className="h-4 w-4 mr-2" /> Add Node
              </Button>
              <Button size="sm" className="bg-primary text-primary-foreground shadow-lg shadow-primary/20">
                <Play className="h-4 w-4 mr-2" /> Test Run
              </Button>
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
