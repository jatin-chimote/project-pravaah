import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function UsersPage() {
  return (
    <div>
        <h1 className="text-2xl font-bold">Users Management</h1>
        <p className="text-muted-foreground">Manage users and their roles for your client.</p>
        <Card className="mt-4">
            <CardHeader>
                <CardTitle>Coming Soon</CardTitle>
                <CardDescription>This section is under construction.</CardDescription>
            </CardHeader>
            <CardContent>
                <p>The interface for managing users will be available here shortly.</p>
            </CardContent>
        </Card>
    </div>
  );
}
