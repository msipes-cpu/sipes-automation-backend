import DashboardLayout from "@/components/DashboardLayout";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { 
  User, 
  Lock, 
  Bell, 
  Globe, 
  CreditCard,
  Key,
  Webhook
} from "lucide-react";

export default function Settings() {
  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-display font-bold text-foreground tracking-tight">Settings</h1>
          <p className="text-muted-foreground mt-1">Configure your workspace and integrations</p>
        </div>

        <Tabs defaultValue="general" className="w-full">
          <div className="flex flex-col md:flex-row gap-6">
            <TabsList className="flex-col h-auto items-start w-full md:w-64 bg-card border border-border p-2 space-y-1">
              <TabsTrigger value="general" className="w-full justify-start px-3 py-2">
                <User className="mr-2 h-4 w-4" /> General
              </TabsTrigger>
              <TabsTrigger value="integrations" className="w-full justify-start px-3 py-2">
                <Webhook className="mr-2 h-4 w-4" /> Integrations
              </TabsTrigger>
              <TabsTrigger value="api" className="w-full justify-start px-3 py-2">
                <Key className="mr-2 h-4 w-4" /> API Keys
              </TabsTrigger>
              <TabsTrigger value="notifications" className="w-full justify-start px-3 py-2">
                <Bell className="mr-2 h-4 w-4" /> Notifications
              </TabsTrigger>
              <TabsTrigger value="billing" className="w-full justify-start px-3 py-2">
                <CreditCard className="mr-2 h-4 w-4" /> Billing
              </TabsTrigger>
            </TabsList>

            <div className="flex-1">
              <TabsContent value="general" className="space-y-6 mt-0">
                <Card className="bg-card/40 border-border/50">
                  <CardHeader>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>Update your account details</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid gap-2">
                      <Label htmlFor="name">Display Name</Label>
                      <Input id="name" defaultValue="Michael Sipes" className="bg-background border-border" />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="email">Email Address</Label>
                      <Input id="email" defaultValue="msipes@sipesautomation.com" className="bg-background border-border" />
                    </div>
                    <div className="grid gap-2">
                      <Label htmlFor="agency">Agency Name</Label>
                      <Input id="agency" defaultValue="Sipes Automation" className="bg-background border-border" />
                    </div>
                    <Button className="bg-primary text-primary-foreground">Save Changes</Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="api" className="space-y-6 mt-0">
                <Card className="bg-card/40 border-border/50">
                  <CardHeader>
                    <CardTitle>API Access</CardTitle>
                    <CardDescription>Manage keys for external access to your dashboard</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="space-y-4">
                      <div className="flex items-center justify-between p-4 border border-border rounded-lg bg-background/50">
                        <div>
                          <p className="font-medium">Production Key</p>
                          <p className="text-xs text-muted-foreground font-mono mt-1">sk_live_...8921</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">Roll Key</Button>
                          <Button variant="destructive" size="sm">Revoke</Button>
                        </div>
                      </div>
                      <div className="flex items-center justify-between p-4 border border-border rounded-lg bg-background/50">
                        <div>
                          <p className="font-medium">Test Key</p>
                          <p className="text-xs text-muted-foreground font-mono mt-1">sk_test_...4421</p>
                        </div>
                        <div className="flex gap-2">
                          <Button variant="outline" size="sm">Roll Key</Button>
                          <Button variant="destructive" size="sm">Revoke</Button>
                        </div>
                      </div>
                    </div>
                    <Button className="w-full border-dashed border-2 border-border bg-transparent hover:bg-accent hover:text-accent-foreground text-muted-foreground">
                      <Key className="mr-2 h-4 w-4" /> Generate New Key
                    </Button>
                  </CardContent>
                </Card>
              </TabsContent>

              <TabsContent value="notifications" className="space-y-6 mt-0">
                <Card className="bg-card/40 border-border/50">
                  <CardHeader>
                    <CardTitle>Alert Preferences</CardTitle>
                    <CardDescription>Configure how and when you get notified</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label className="text-base">Critical Errors</Label>
                        <p className="text-sm text-muted-foreground">
                          Receive immediate alerts for workflow failures
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <Separator className="bg-border" />
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label className="text-base">Daily Digest</Label>
                        <p className="text-sm text-muted-foreground">
                          Summary of daily automation performance
                        </p>
                      </div>
                      <Switch defaultChecked />
                    </div>
                    <Separator className="bg-border" />
                    <div className="flex items-center justify-between">
                      <div className="space-y-0.5">
                        <Label className="text-base">Slack Integration</Label>
                        <p className="text-sm text-muted-foreground">
                          Send alerts to #automation-alerts channel
                        </p>
                      </div>
                      <Switch />
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </div>
          </div>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
