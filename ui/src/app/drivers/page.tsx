import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function DriversPage() {
  return (
    <div>
        <h1 className="text-2xl font-bold">Drivers Management</h1>
        <p className="text-muted-foreground">Manage your team of drivers.</p>
         <Card className="mt-4">
            <CardHeader>
                <CardTitle>Coming Soon</CardTitle>
                <CardDescription>This section is under construction.</CardDescription>
            </CardHeader>
            <CardContent>
                <p>The interface for managing drivers will be available here shortly.</p>
            </CardContent>
        </Card>
    </div>
  );
}
