import { StatCard } from "@/components/dashboard/stat-card";
import { MapView } from "@/components/dashboard/map-view";
import { RecentAlerts } from "@/components/dashboard/recent-alerts";
import {
  Activity,
  AlertTriangle,
  GitFork,
  Truck,
  Fuel,
} from "lucide-react";

export default function DashboardPage() {
  return (
    <div className="flex flex-col gap-6">
      <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-5">
        <StatCard
          title="Active Vehicles"
          value="1,204"
          icon={<Truck className="h-4 w-4 text-muted-foreground" />}
          change="+20.1% from last month"
        />
        <StatCard
          title="Ongoing Journeys"
          value="87"
          icon={<GitFork className="h-4 w-4 text-muted-foreground" />}
          change="+15 since last hour"
        />
        <StatCard
          title="Active Alerts"
          value="23"
          icon={<AlertTriangle className="h-4 w-4 text-muted-foreground" />}
          change="+5 in the last hour"
        />
        <StatCard
          title="Avg. Route Completion"
          value="92.5%"
          icon={<Activity className="h-4 w-4 text-muted-foreground" />}
          change="-1.2% from yesterday"
        />
        <StatCard
          title="Fuel Saved (Est.)"
          value="452 L"
          icon={<Fuel className="h-4 w-4 text-muted-foreground" />}
          change="+45 L today"
        />
      </div>
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <MapView />
        </div>
        <div className="lg:col-span-1">
          <RecentAlerts />
        </div>
      </div>
    </div>
  );
}
