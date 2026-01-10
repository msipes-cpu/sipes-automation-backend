import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { 
  AlertTriangle, 
  RefreshCw, 
  CheckCircle, 
  XCircle, 
  Terminal, 
  ExternalLink,
  Clock,
  Filter
} from "lucide-react";

const errors = [
  {
    id: "ERR-8921",
    severity: "critical",
    workflow: "Client Onboarding - ABC Corp",
    node: "Slack Channel Create",
    message: "Failed to create channel: 'name_taken'",
    timestamp: "10 mins ago",
    status: "open",
    details: "The channel name 'client-abc-corp' already exists in the workspace. Slack API returned error code 409."
  },
  {
    id: "ERR-8920",
    severity: "warning",
    workflow: "Lead Enrichment",
    node: "Clearbit API",
    message: "Rate limit approaching (95%)",
    timestamp: "45 mins ago",
    status: "resolved",
    details: "API usage is high. Consider upgrading plan or throttling requests."
  },
  {
    id: "ERR-8919",
    severity: "critical",
    workflow: "Cold Outreach Sequence",
    node: "Gmail Send",
    message: "Authentication failed: Token expired",
    timestamp: "2 hours ago",
    status: "open",
    details: "OAuth refresh token is invalid. Re-authentication required for user msipes@sipesautomation.com."
  }
];

export default function Errors() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
          <div>
            <h1 className="text-3xl font-display font-bold text-foreground tracking-tight">Error Center</h1>
            <p className="text-muted-foreground mt-1">Diagnose and resolve automation failures</p>
          </div>
          <div className="flex gap-2">
            <Button variant="outline" className="border-border">
              <Filter className="mr-2 h-4 w-4" /> Filter
            </Button>
            <Button variant="outline" className="border-border">
              <CheckCircle className="mr-2 h-4 w-4" /> Resolve All
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Error List */}
          <div className="lg:col-span-1 space-y-4">
            {errors.map((error) => (
              <div 
                key={error.id}
                className={`
                  p-4 rounded-lg border cursor-pointer transition-all
                  ${error.status === 'open' 
                    ? 'bg-card border-l-4 border-l-destructive border-y-border border-r-border shadow-lg' 
                    : 'bg-card/50 border-border opacity-70'}
                `}
              >
                <div className="flex justify-between items-start mb-2">
                  <Badge 
                    variant={error.severity === 'critical' ? 'destructive' : 'secondary'}
                    className="uppercase text-[10px] font-bold"
                  >
                    {error.severity}
                  </Badge>
                  <span className="text-xs text-muted-foreground font-mono">{error.timestamp}</span>
                </div>
                <h4 className="font-medium text-foreground text-sm mb-1">{error.message}</h4>
                <p className="text-xs text-muted-foreground mb-3">{error.workflow}</p>
                <div className="flex items-center justify-between">
                  <span className="text-xs font-mono text-muted-foreground">{error.id}</span>
                  {error.status === 'open' && (
                    <Badge variant="outline" className="text-xs border-destructive/30 text-destructive">
                      Needs Action
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Detail View */}
          <Card className="lg:col-span-2 bg-card border-border h-fit sticky top-6">
            <CardHeader className="border-b border-border/50 pb-4">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <CardTitle className="text-xl">Failed to create channel: 'name_taken'</CardTitle>
                    <Badge variant="destructive">CRITICAL</Badge>
                  </div>
                  <CardDescription className="font-mono text-xs">
                    ID: ERR-8921 • Workflow: Client Onboarding - ABC Corp • Node: Slack Channel Create
                  </CardDescription>
                </div>
                <Button variant="ghost" size="icon">
                  <ExternalLink className="h-4 w-4" />
                </Button>
              </div>
            </CardHeader>
            <CardContent className="pt-6 space-y-6">
              {/* Context */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                  <AlertTriangle className="h-4 w-4 text-destructive" />
                  Error Details
                </h4>
                <div className="bg-destructive/10 border border-destructive/20 rounded-md p-4 text-sm text-destructive-foreground">
                  The channel name 'client-abc-corp' already exists in the workspace. Slack API returned error code 409.
                </div>
              </div>

              {/* Technical Logs */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-foreground flex items-center gap-2">
                  <Terminal className="h-4 w-4 text-primary" />
                  Stack Trace
                </h4>
                <div className="bg-[#0B1120] border border-border rounded-md p-4 font-mono text-xs text-muted-foreground overflow-x-auto">
                  <p className="text-green-400">$ slack.channels.create({'{'} name: "client-abc-corp" {'}'})</p>
                  <p className="text-red-400 mt-1">{'>'} Error: name_taken</p>
                  <p className="pl-4">at SlackClient.createChannel (/app/nodes/Slack.js:42:15)</p>
                  <p className="pl-4">at processTicksAndRejections (internal/process/task_queues.js:95:5)</p>
                  <p className="pl-4">at async WorkflowEngine.executeNode (/app/engine.js:156:22)</p>
                </div>
              </div>

              {/* Suggested Actions */}
              <div className="space-y-3 pt-4 border-t border-border/50">
                <h4 className="text-sm font-medium text-foreground">Recommended Actions</h4>
                <div className="flex gap-3">
                  <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
                    <RefreshCw className="mr-2 h-4 w-4" />
                    Retry with Suffix
                  </Button>
                  <Button variant="secondary">
                    Ignore & Continue
                  </Button>
                  <Button variant="outline" className="border-destructive/30 text-destructive hover:bg-destructive/10">
                    <XCircle className="mr-2 h-4 w-4" />
                    Abort Workflow
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  <span className="text-primary">AI Suggestion:</span> Appending a random suffix (e.g., -1) usually resolves naming conflicts.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
