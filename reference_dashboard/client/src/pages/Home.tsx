import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Activity, 
  CheckCircle2, 
  AlertTriangle, 
  Clock, 
  ArrowUpRight, 
  Play, 
  MoreHorizontal,
  Zap,
  Server,
  Database
} from "lucide-react";
import DashboardLayout from "@/components/DashboardLayout";
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: '00:00', success: 40, error: 2 },
  { name: '04:00', success: 30, error: 1 },
  { name: '08:00', success: 85, error: 5 },
  { name: '12:00', success: 120, error: 3 },
  { name: '16:00', success: 90, error: 4 },
  { name: '20:00', success: 65, error: 2 },
  { name: '23:59', success: 45, error: 1 },
];

const recentWorkflows = [
  { id: "WF-2948", name: "Client Onboarding - ABC Corp", status: "running", time: "2m ago", step: "Generating Contract" },
  { id: "WF-2947", name: "Lead Enrichment - Batch 402", status: "completed", time: "15m ago", step: "Done" },
  { id: "WF-2946", name: "Slack Notification Sync", status: "failed", time: "42m ago", step: "API Timeout" },
  { id: "WF-2945", name: "Daily Report Generation", status: "completed", time: "1h ago", step: "Done" },
  { id: "WF-2944", name: "New Lead Sequence", status: "completed", time: "1h ago", step: "Done" },
];

export default function Home() {
  return (
    <DashboardLayout>
      <div className="space-y-8">
        {/* Header Section */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground tracking-tight">Mission Control</h1>
            <p className="text-muted-foreground mt-1 font-mono text-sm">System Status: <span className="text-primary">OPERATIONAL</span> | Uptime: 99.98%</p>
          </div>
          <div className="flex gap-3">
            <Button variant="outline" className="border-primary/20 hover:bg-primary/10 hover:text-primary">
              <Clock className="mr-2 h-4 w-4" />
              Last 24 Hours
            </Button>
            <Button className="bg-primary text-primary-foreground hover:bg-primary/90 shadow-[0_0_15px_rgba(16,185,129,0.4)]">
              <Play className="mr-2 h-4 w-4" />
              Trigger Workflow
            </Button>
          </div>
        </div>

        {/* KPI Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-card/50 border-primary/20 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Total Executions</CardTitle>
              <Zap className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">2,845</div>
              <p className="text-xs text-muted-foreground mt-1">
                <span className="text-primary flex items-center inline-block">
                  <ArrowUpRight className="h-3 w-3 mr-1" /> +12.5%
                </span> from yesterday
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 border-primary/20 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Success Rate</CardTitle>
              <CheckCircle2 className="h-4 w-4 text-primary" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono text-primary">98.2%</div>
              <p className="text-xs text-muted-foreground mt-1">
                Target: 99.0%
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 border-destructive/20 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Critical Errors</CardTitle>
              <AlertTriangle className="h-4 w-4 text-destructive" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono text-destructive">3</div>
              <p className="text-xs text-muted-foreground mt-1">
                Requires attention
              </p>
            </CardContent>
          </Card>
          
          <Card className="bg-card/50 border-primary/20 backdrop-blur-sm">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">Time Saved</CardTitle>
              <Clock className="h-4 w-4 text-blue-400" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold font-mono">42.5 hrs</div>
              <p className="text-xs text-muted-foreground mt-1">
                Est. Value: <span className="text-primary">$4,250</span>
              </p>
            </CardContent>
          </Card>
        </div>

        {/* Main Chart & System Health */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Activity Chart */}
          <Card className="lg:col-span-2 border-border/50 bg-card/40">
            <CardHeader>
              <CardTitle>Workflow Activity</CardTitle>
              <CardDescription>Real-time execution volume over last 24 hours</CardDescription>
            </CardHeader>
            <CardContent className="pl-2">
              <div className="h-[300px] w-full">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={data}>
                    <defs>
                      <linearGradient id="colorSuccess" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorError" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#EF4444" stopOpacity={0.3}/>
                        <stop offset="95%" stopColor="#EF4444" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" vertical={false} />
                    <XAxis 
                      dataKey="name" 
                      stroke="#64748B" 
                      fontSize={12} 
                      tickLine={false} 
                      axisLine={false} 
                    />
                    <YAxis 
                      stroke="#64748B" 
                      fontSize={12} 
                      tickLine={false} 
                      axisLine={false} 
                      tickFormatter={(value) => `${value}`} 
                    />
                    <Tooltip 
                      contentStyle={{ backgroundColor: '#0F172A', borderColor: '#1E293B', color: '#F8FAFC' }}
                      itemStyle={{ color: '#F8FAFC' }}
                    />
                    <Area 
                      type="monotone" 
                      dataKey="success" 
                      stroke="#10B981" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorSuccess)" 
                    />
                    <Area 
                      type="monotone" 
                      dataKey="error" 
                      stroke="#EF4444" 
                      strokeWidth={2}
                      fillOpacity={1} 
                      fill="url(#colorError)" 
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </div>
            </CardContent>
          </Card>

          {/* System Health */}
          <Card className="border-border/50 bg-card/40">
            <CardHeader>
              <CardTitle>System Health</CardTitle>
              <CardDescription>Live infrastructure status</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-muted-foreground">
                    <Server className="h-4 w-4 mr-2" /> API Gateway
                  </div>
                  <span className="text-primary font-mono text-xs">ONLINE</span>
                </div>
                <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[98%] rounded-full shadow-[0_0_10px_#10B981]" />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-muted-foreground">
                    <Database className="h-4 w-4 mr-2" /> Database
                  </div>
                  <span className="text-primary font-mono text-xs">ONLINE</span>
                </div>
                <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-primary w-[100%] rounded-full shadow-[0_0_10px_#10B981]" />
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center text-muted-foreground">
                    <Activity className="h-4 w-4 mr-2" /> Worker Nodes
                  </div>
                  <span className="text-yellow-500 font-mono text-xs">HIGH LOAD</span>
                </div>
                <div className="h-1.5 w-full bg-secondary rounded-full overflow-hidden">
                  <div className="h-full bg-yellow-500 w-[85%] rounded-full shadow-[0_0_10px_#F59E0B]" />
                </div>
              </div>

              <div className="pt-4 border-t border-border/50">
                <div className="rounded-md bg-primary/10 border border-primary/20 p-3">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <Activity className="h-5 w-5 text-primary animate-pulse" />
                    </div>
                    <div className="ml-3 flex-1 md:flex md:justify-between">
                      <p className="text-sm text-primary-foreground">
                        System performing optimally. Auto-scaling enabled.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Recent Workflows Table */}
        <Card className="border-border/50 bg-card/40">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Live Execution Log</CardTitle>
              <CardDescription>Real-time stream of agent activities</CardDescription>
            </div>
            <Button variant="ghost" size="sm" className="text-muted-foreground">View All</Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentWorkflows.map((wf) => (
                <div key={wf.id} className="flex items-center justify-between p-4 rounded-lg border border-border/40 bg-card/30 hover:bg-card/50 transition-colors group">
                  <div className="flex items-center gap-4">
                    <div className={`
                      w-2 h-2 rounded-full shadow-[0_0_8px_currentColor]
                      ${wf.status === 'running' ? 'bg-blue-500 text-blue-500 animate-pulse' : 
                        wf.status === 'completed' ? 'bg-primary text-primary' : 
                        'bg-destructive text-destructive'}
                    `} />
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-foreground">{wf.name}</span>
                        <Badge variant="outline" className="font-mono text-[10px] h-5 border-border/50 text-muted-foreground">
                          {wf.id}
                        </Badge>
                      </div>
                      <div className="text-sm text-muted-foreground mt-0.5 flex items-center gap-2">
                        <span className="font-mono text-xs">{wf.time}</span>
                        <span>•</span>
                        <span>{wf.step}</span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4">
                    <Badge 
                      variant={wf.status === 'failed' ? 'destructive' : 'secondary'}
                      className={`uppercase text-[10px] tracking-wider font-bold ${
                        wf.status === 'running' ? 'bg-blue-500/10 text-blue-400 border-blue-500/20' : 
                        wf.status === 'completed' ? 'bg-primary/10 text-primary border-primary/20' : ''
                      }`}
                    >
                      {wf.status}
                    </Badge>
                    <Button variant="ghost" size="icon" className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <MoreHorizontal className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
