
"use client";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { mockDriverJourneys } from "@/lib/mock-data";
import type { DriverJourney } from "@/lib/types";
import { Play, Check, XCircle, Ban } from "lucide-react";
import Link from "next/link";


export default function AllJourneysPage() {

    const getStatusBadge = (status: DriverJourney['status']) => {
        switch (status) {
            case 'Ongoing':
                return <Badge variant="default" className="bg-blue-500 hover:bg-blue-600">Ongoing</Badge>;
            case 'Pending':
                return <Badge variant="secondary">Pending</Badge>;
            case 'Completed':
                return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Completed</Badge>;
            case 'Cancelled':
                 return <Badge variant="destructive">Cancelled</Badge>;
        }
    };
    
    const getActionIcon = (status: DriverJourney['status']) => {
        switch (status) {
            case 'Ongoing':
                return <Link href="/driver-view/current-journey"><Button size="sm" variant="outline"><Play className="mr-2 h-4 w-4"/>Resume</Button></Link>;
            case 'Pending':
                 return <Link href="/driver-view/current-journey"><Button size="sm"><Play className="mr-2 h-4 w-4"/>Start</Button></Link>;
            case 'Completed':
                return <div className="flex items-center text-green-600"><Check className="mr-2 h-4 w-4"/>Done</div>;
            case 'Cancelled':
                return <div className="flex items-center text-red-600"><Ban className="mr-2 h-4 w-4"/>Cancelled</div>;
        }
    }

    return (
        <div className="flex flex-col gap-4">
            <div>
                <h1 className="text-2xl font-bold">All Journeys</h1>
                <p className="text-muted-foreground">Your scheduled journeys for the day.</p>
            </div>
            <Card>
                <CardContent className="pt-6">
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Route</TableHead>
                                <TableHead>Source</TableHead>
                                <TableHead>Destination</TableHead>
                                <TableHead>Vehicle</TableHead>
                                <TableHead>Time</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Action</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {mockDriverJourneys.map((journey) => (
                                <TableRow key={journey.id}>
                                    <TableCell className="font-medium">{journey.routeName}</TableCell>
                                    <TableCell>{journey.source}</TableCell>
                                    <TableCell>{journey.destination}</TableCell>
                                    <TableCell>{journey.vehicle}</TableCell>
                                    <TableCell>{journey.scheduledTime}</TableCell>
                                    <TableCell>{getStatusBadge(journey.status)}</TableCell>
                                    <TableCell>{getActionIcon(journey.status)}</TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>
        </div>
    );
}

