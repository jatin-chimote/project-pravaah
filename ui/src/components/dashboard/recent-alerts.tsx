import {
  Avatar,
  AvatarFallback,
  AvatarImage,
} from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { mockAlerts } from "@/lib/mock-data";
import { AlertTriangle, CheckCircle, Info } from "lucide-react";

export function RecentAlerts() {
    const getIcon = (type: string) => {
        switch (type) {
            case 'Predictive Gridlock':
                return <AlertTriangle className="h-5 w-5 text-destructive" />;
            case 'Heavy Traffic':
                return <Info className="h-5 w-5 text-accent" />;
            case 'Road Closure':
                return <CheckCircle className="h-5 w-5 text-green-500" />;
            default:
                return <Info className="h-5 w-5 text-muted-foreground" />;
        }
    }
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Recent Alerts</CardTitle>
        <CardDescription>
          AI-generated alerts and recommendations.
        </CardDescription>
      </CardHeader>
      <CardContent className="grid gap-6">
        {mockAlerts.slice(0, 3).map((alert) => (
          <div key={alert.id} className="flex items-center gap-4">
            <div className="rounded-full bg-secondary p-2">
                {getIcon(alert.alertType)}
            </div>
            <div className="grid gap-1">
              <p className="text-sm font-medium leading-none">{alert.alertType}</p>
              <p className="text-sm text-muted-foreground">{alert.message}</p>
            </div>
            <div className="ml-auto font-medium">
                <Button variant="ghost" size="sm">View</Button>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
