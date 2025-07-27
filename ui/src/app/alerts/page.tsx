
"use client";

import { useState, useEffect } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { mockAlerts } from "@/lib/mock-data";
import type { Alert } from "@/lib/types";
import { GitCommit, Trash2, Clock } from "lucide-react";

function AlertCard({ alert }: { alert: Alert }) {
    const [displayTime, setDisplayTime] = useState('');

    useEffect(() => {
        // This function will now only run on the client, after hydration
        const timeAgo = (dateString: string) => {
            const date = new Date(dateString);
            const now = new Date();
            const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
            
            let interval = seconds / 31536000;
            if (interval > 1) return Math.floor(interval) + " years ago";
            interval = seconds / 2592000;
            if (interval > 1) return Math.floor(interval) + " months ago";
            interval = seconds / 86400;
            if (interval > 1) return Math.floor(interval) + " days ago";
            interval = seconds / 3600;
            if (interval > 1) return Math.floor(interval) + " hours ago";
            interval = seconds / 60;
            if (interval > 1) return Math.floor(interval) + " minutes ago";
            return Math.floor(seconds) + " seconds ago";
        };

        setDisplayTime(timeAgo(alert.timestamp));
    }, [alert.timestamp]);

    const getStatusBadge = (status: Alert['status']) => {
        switch (status) {
            case 'Issued':
                return <Badge variant="destructive">Issued</Badge>;
            case 'Acted':
                return <Badge variant="default">Acted</Badge>;
            case 'Dismissed':
                return <Badge variant="secondary">Dismissed</Badge>;
        }
    };

    return (
        <Card>
            <CardHeader>
                <div className="flex justify-between items-start">
                    <div>
                        <CardTitle className="text-lg">{alert.alertType}</CardTitle>
                        <CardDescription>For Journey ID: {alert.journeyId}</CardDescription>
                    </div>
                    {getStatusBadge(alert.status)}
                </div>
            </CardHeader>
            <CardContent>
                <p className="text-sm">{alert.message}</p>
                <p className="mt-2 text-sm font-semibold text-primary">
                    Recommended Action: <span className="font-normal text-foreground">{alert.recommendedAction}</span>
                </p>
                {displayTime && (
                    <div className="mt-4 flex items-center text-xs text-muted-foreground">
                        <Clock className="mr-1.5 h-3 w-3" />
                        {displayTime}
                    </div>
                )}
            </CardContent>
            <CardFooter className="flex justify-end gap-2">
                <Button variant="outline">
                    <Trash2 className="mr-2 h-4 w-4" />
                    Dismiss
                </Button>
                <Button disabled={!alert.newRouteId}>
                    <GitCommit className="mr-2 h-4 w-4" />
                    Apply Reroute
                </Button>
            </CardFooter>
        </Card>
    );
}


export default function AlertsPage() {
    return (
        <div className="flex flex-col gap-4">
            <div>
                <h1 className="text-2xl font-bold">Alerts Panel</h1>
                <p className="text-muted-foreground">AI-Generated alerts for proactive traffic management.</p>
            </div>
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {mockAlerts.map((alert) => (
                    <AlertCard key={alert.id} alert={alert} />
                ))}
            </div>
        </div>
    );
}
