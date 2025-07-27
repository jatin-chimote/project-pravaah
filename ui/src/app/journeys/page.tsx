import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function JourneysPage() {
  return (
    <div>
        <h1 className="text-2xl font-bold">Journeys Management</h1>
        <p className="text-muted-foreground">Schedule and track vehicle journeys.</p>
        <Card className="mt-4">
            <CardHeader>
                <CardTitle>Coming Soon</CardTitle>
                <CardDescription>This section is under construction.</CardDescription>
            </CardHeader>
            <CardContent>
                <p>The interface for scheduling and tracking journeys will be available here shortly.</p>
            </CardContent>
        </Card>
    </div>
  );
}
