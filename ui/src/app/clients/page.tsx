import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function ClientsPage() {
  return (
    <div>
        <h1 className="text-2xl font-bold">Clients Management</h1>
        <p className="text-muted-foreground">View and manage all clients (Global Admin only).</p>
        <Card className="mt-4">
            <CardHeader>
                <CardTitle>Coming Soon</CardTitle>
                <CardDescription>This section is under construction.</CardDescription>
            </CardHeader>
            <CardContent>
                <p>The interface for managing clients will be available here shortly.</p>
            </CardContent>
        </Card>
    </div>
  );
}
