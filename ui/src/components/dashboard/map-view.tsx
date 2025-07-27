
"use client"

import { APIProvider, Map, useMap } from "@vis.gl/react-google-maps";
import { useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

const TrafficLayer = () => {
    const map = useMap();

    useEffect(() => {
        if (!map) return;

        const trafficLayer = new google.maps.TrafficLayer();
        trafficLayer.setMap(map);

        return () => {
            trafficLayer.setMap(null);
        };
    }, [map]);

    return null;
}

export function MapView() {
    if (!API_KEY) {
        return (
            <Card className="h-full">
                <CardHeader>
                    <CardTitle>Live Traffic Map</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="flex aspect-video w-full flex-col items-center justify-center rounded-lg bg-muted p-4 text-center">
                        <p className="font-semibold">Google Maps API Key is missing.</p>
                        <p className="text-sm text-muted-foreground mt-2">To display the map, please create a `.env.local` file in your project's root directory and add your Google Maps API key as `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_API_KEY`.</p>
                    </div>
                </CardContent>
            </Card>
        )
    }
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle>Live Traffic Map</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="aspect-video w-full overflow-hidden rounded-lg">
            <APIProvider apiKey={API_KEY}>
                <Map
                    defaultCenter={{ lat: 12.9716, lng: 77.5946 }} // Default to Bangalore
                    defaultZoom={12}
                    mapId="dashboard-map"
                    className="h-full w-full"
                >
                    <TrafficLayer />
                </Map>
            </APIProvider>
        </div>
      </CardContent>
    </Card>
  );
}
