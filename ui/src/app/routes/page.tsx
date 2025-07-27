import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function RoutesPage() {
  return (
    <div>
        <h1 className="text-2xl font-bold">Routes Management</h1>
        <p className="text-muted-foreground">Define and manage vehicle routes.</p>
        <Card className="mt-4">
            <CardHeader>
                <CardTitle>Coming Soon</CardTitle>
                <CardDescription>This section is under construction.</CardDescription>
            </CardHeader>
            <CardContent>
                <p>The interface for managing routes, including map previews, will be available here shortly.</p>
            </CardContent>
        </Card>
    </div>
  );
}
