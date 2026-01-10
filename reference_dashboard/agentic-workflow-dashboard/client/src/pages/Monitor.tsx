import DashboardLayout from "@/components/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { ScrollArea } from "@/components/ui/scroll-area";
import { 
  Activity, 
  Server, 
  Database, 
  Globe, 
  Cpu, 
  HardDrive,
  Wifi,
  Terminal
} from "lucide-react";

const logs = [
  { time: "10:42:15", level: "INFO", source: "Worker-01", message: "Job WF-2948 started processing" },
  { time: "10:42:16", level: "DEBUG", source: "API-Gateway", message: "Request received: POST /v1/hooks/catch/..." },
  { time: "10:42:18", level: "INFO", source: "Worker-01", message: "Node 'Generate Contract' executed successfully (1.2s)" },
  { time: "10:42:19", level: "WARN", source: "DB-Pool", message: "Connection pool utilization > 80%" },
  { time: "10:42:21", level: "INFO", source: "Worker-02", message: "Job WF-2947 completed" },
  { time: "10:42:25", level: "ERROR", source: "Worker-03", message: "Slack API connection timeout (30s)" },
  { time: "10:42:26", level: "INFO", source: "System", message: "Auto-scaling triggered: Spawning Worker-04" },
  { time: "10:42:30", level: "INFO", source: "Worker-01", message: "Job WF-2948 completed" },
];

export default function Monitor() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground tracking-tight">Live Monitor</h1>
          <p className="text-muted-foreground mt-1">Real-time system telemetry and logs</p>
        </div>

        {/* Infrastructure Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card className="bg-card/40 border-border/50">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-3 rounded-full bg-primary/10 text-primary">
                <Cpu className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">CPU Usage</p>
                <h3 className="text-2xl font-mono font-bold text-foreground">42%</h3>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-card/40 border-border/50">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-3 rounded-full bg-blue-500/10 text-blue-500">
                <HardDrive className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Memory</p>
                <h3 className="text-2xl font-mono font-bold text-foreground">2.4 GB</h3>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-card/40 border-border/50">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-3 rounded-full bg-purple-500/10 text-purple-500">
                <Database className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">DB Connections</p>
                <h3 className="text-2xl font-mono font-bold text-foreground">84/100</h3>
              </div>
            </CardContent>
          </Card>
          
          <Card className="bg-card/40 border-border/50">
            <CardContent className="p-6 flex items-center gap-4">
              <div className="p-3 rounded-full bg-green-500/10 text-green-500">
                <Wifi className="h-6 w-6" />
              </div>
              <div>
                <p className="text-sm text-muted-foreground">API Latency</p>
                <h3 className="text-2xl font-mono font-bold text-foreground">45ms</h3>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Live Logs */}
        <Card className="bg-[#0B1120] border-border">
          <CardHeader className="border-b border-border/50 py-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Terminal className="h-5 w-5 text-primary" />
                <CardTitle className="font-mono text-lg">System Logs</CardTitle>
              </div>
              <Badge variant="outline" className="font-mono text-xs border-primary/30 text-primary animate-pulse">
                LIVE
              </Badge>
            </div>
          </CardHeader>
          <CardContent className="p-0">
            <ScrollArea className="h-[500px] w-full p-4">
              <div className="space-y-1 font-mono text-sm">
                {logs.map((log, i) => (
                  <div key={i} className="flex gap-4 hover:bg-white/5 p-1 rounded transition-colors">
                    <span className="text-muted-foreground w-20 shrink-0">{log.time}</span>
                    <span className={`w-16 shrink-0 font-bold ${
                      log.level === 'INFO' ? 'text-blue-400' :
                      log.level === 'WARN' ? 'text-yellow-400' :
                      log.level === 'ERROR' ? 'text-red-400' :
                      'text-gray-400'
                    }`}>
                      {log.level}
                    </span>
                    <span className="text-purple-400 w-24 shrink-0">{log.source}</span>
                    <span className="text-foreground/90">{log.message}</span>
                  </div>
                ))}
                {/* Simulated future logs */}
                <div className="flex gap-4 p-1 opacity-50">
                  <span className="text-muted-foreground w-20 shrink-0">...</span>
                </div>
              </div>
            </ScrollArea>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
