import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { AlertCircle } from "lucide-react";

export default function NotFound() {
  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-background">
      <div className="text-center space-y-6 p-8">
        <div className="flex justify-center">
          <AlertCircle className="h-24 w-24 text-destructive opacity-80" />
        </div>
        <h1 className="text-4xl font-display font-bold text-foreground">404</h1>
        <p className="text-xl text-muted-foreground">System module not found</p>
        <Link href="/">
          <Button size="lg" className="mt-4 bg-primary text-primary-foreground">
            Return to Mission Control
          </Button>
        </Link>
      </div>
    </div>
  );
}
