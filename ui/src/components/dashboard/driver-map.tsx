
"use client"

import { APIProvider, Map, AdvancedMarker, useMap, Pin } from "@vis.gl/react-google-maps";
import { useEffect, useState, useMemo } from "react";
import { Navigation } from "lucide-react";

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

interface DriverMapProps {
    routes: any[];
    selectedRouteIndex: number;
    onRouteSelect: (index: number) => void;
    currentPosition: { lat: number; lng: number } | null;
    destinationPosition: { lat: number, lng: number } | null;
    currentHeading: number | null;
    isNavigating: boolean;
}

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

const RoutePolylines = ({ encodedPolyline, currentPosition }: { encodedPolyline: string, currentPosition: { lat: number, lng: number } }) => {
    const map = useMap();
    const [traveledPolyline, setTraveledPolyline] = useState<google.maps.Polyline | null>(null);
    const [remainingPolyline, setRemainingPolyline] = useState<google.maps.Polyline | null>(null);

    const decodedPath = useMemo(() => {
        if (!window.google || !window.google.maps.geometry) return [];
        return google.maps.geometry.encoding.decodePath(encodedPolyline);
    }, [encodedPolyline]);

    useEffect(() => {
        if (!map || decodedPath.length === 0 || !currentPosition) return;

        traveledPolyline?.setMap(null);
        remainingPolyline?.setMap(null);

        if (!window.google || !window.google.maps.geometry) return;

        const currentLatLng = new google.maps.LatLng(currentPosition.lat, currentPosition.lng);

        let closestPointIndex = -1;
        let minDistance = Infinity;

        decodedPath.forEach((point, index) => {
            const distance = google.maps.geometry.spherical.computeDistanceBetween(currentLatLng, point);
            if (distance < minDistance) {
                minDistance = distance;
                closestPointIndex = index;
            }
        });
        
        if (closestPointIndex === -1) return;

        const traveledPath = decodedPath.slice(0, closestPointIndex + 1);
        traveledPath.push(currentLatLng); 
        const remainingPath = [currentLatLng, ...decodedPath.slice(closestPointIndex)];


        const newTraveledPolyline = new google.maps.Polyline({
            path: traveledPath,
            strokeColor: "#808080",
            strokeOpacity: 0.7,
            strokeWeight: 6,
            zIndex: 1,
        });

        const newRemainingPolyline = new google.maps.Polyline({
            path: remainingPath,
            strokeColor: "#4285F4",
            strokeOpacity: 0.8,
            strokeWeight: 6,
            zIndex: 2,
        });

        newTraveledPolyline.setMap(map);
        newRemainingPolyline.setMap(map);

        setTraveledPolyline(newTraveledPolyline);
        setRemainingPolyline(newRemainingPolyline);

        return () => {
            newTraveledPolyline.setMap(null);
            newRemainingPolyline.setMap(null);
        };

    }, [map, decodedPath, currentPosition]);


    return null;
}


const FullRoutePolylines = ({ routes, selectedRouteIndex, onRouteSelect }: { routes: any[], selectedRouteIndex: number, onRouteSelect: (index: number) => void }) => {
    const map = useMap();
    const [polylines, setPolylines] = useState<google.maps.Polyline[]>([]);

    useEffect(() => {
        if (!map || !window.google || !window.google.maps.geometry) return;

        // Clear existing polylines
        polylines.forEach(p => p.setMap(null));

        if(routes.length === 0) {
            setPolylines([]);
            return;
        }

        const newPolylines: google.maps.Polyline[] = [];
        const bounds = new google.maps.LatLngBounds();

        routes.forEach((route, index) => {
            if (!route.polyline || !route.polyline.encodedPolyline) return;
            
            const isSelected = index === selectedRouteIndex;
            const decodedPath = google.maps.geometry.encoding.decodePath(route.polyline.encodedPolyline);
            
            const polyline = new google.maps.Polyline({
                path: decodedPath,
                strokeColor: isSelected ? "#4285F4" : "#808080",
                strokeOpacity: isSelected ? 0.9 : 0.7,
                strokeWeight: isSelected ? 8 : 6,
                zIndex: isSelected ? 3 : 2,
                clickable: !isSelected
            });

            if (!isSelected) {
                google.maps.event.clearInstanceListeners(polyline);
                polyline.addListener('click', () => {
                    onRouteSelect(index);
                });
            }

            polyline.setMap(map);
            newPolylines.push(polyline);
            decodedPath.forEach(latLng => bounds.extend(latLng));
        })

        if (!bounds.isEmpty()) {
            map.fitBounds(bounds, 50); // 50px padding
        }

        setPolylines(newPolylines);

        return () => {
            newPolylines.forEach(p => {
                google.maps.event.clearInstanceListeners(p);
                p.setMap(null);
            });
        };
    }, [map, routes, selectedRouteIndex, onRouteSelect]);

    return null;
}

const CurrentLocationMarker = ({ position, heading, isNavigating }: { position: {lat: number, lng: number}, heading: number | null, isNavigating: boolean}) => {
    if (!isNavigating || heading === null) {
        return <AdvancedMarker position={position} title={"Your Location"} />;
    }
    
    return (
        <AdvancedMarker position={position} title={"Your Location"}>
            <div
                className="w-8 h-8 rounded-full bg-primary flex items-center justify-center border-2 border-white shadow-lg"
                style={{ transform: `rotate(${heading}deg)` }}
            >
                <Navigation className="w-5 h-5 text-primary-foreground fill-current" />
            </div>
        </AdvancedMarker>
    );
};

const DestinationMarker = ({ position }: { position: {lat: number, lng: number}}) => {
    return (
        <AdvancedMarker position={position} title={"Destination"}>
            <Pin
                background={'#D93025'}
                borderColor={'#A52714'}
                glyphColor={'#FFFFFF'}
            />
        </AdvancedMarker>
    );
}


function MapComponent({ routes, selectedRouteIndex, onRouteSelect, currentPosition, destinationPosition, currentHeading, isNavigating }: DriverMapProps) {
    const map = useMap();
    const encodedPolyline = routes[selectedRouteIndex]?.polyline?.encodedPolyline;

    useEffect(() => {
        if (map && currentPosition) {
            if (isNavigating) {
                map.setCenter(currentPosition);
                map.setZoom(17); 
            }
        }
    }, [currentPosition, map, isNavigating]);

    return (
        <>
            {currentPosition && <CurrentLocationMarker position={currentPosition} heading={currentHeading} isNavigating={isNavigating} />}
            {destinationPosition && <DestinationMarker position={destinationPosition} />}
            {isNavigating && encodedPolyline && currentPosition ? (
                <RoutePolylines encodedPolyline={encodedPolyline} currentPosition={currentPosition} />
            ) : (
                <FullRoutePolylines routes={routes} selectedRouteIndex={selectedRouteIndex} onRouteSelect={onRouteSelect}/>
            )}
            <TrafficLayer />
        </>
    );
}


export function DriverMap(props: DriverMapProps) {
    if (!API_KEY) {
        return (
             <div className="flex h-full w-full flex-col items-center justify-center bg-muted p-4 text-center">
                <p className="font-semibold">Google Maps API Key is missing.</p>
                <p className="text-sm text-muted-foreground mt-2">To display the map, please create a `.env.local` file in your project's root directory and add your Google Maps API key as `NEXT_PUBLIC_GOOGLE_MAPS_API_KEY=YOUR_API_KEY`.</p>
             </div>
        );
    }

    if (!props.currentPosition) {
        return <div className="flex h-full w-full items-center justify-center bg-muted">Getting current location...</div>
    }

    return (
        <APIProvider apiKey={API_KEY} libraries={['geometry', 'routes']}>
            <Map
                defaultCenter={props.currentPosition}
                defaultZoom={15}
                mapId="driver-map"
                className="h-full w-full"
                gestureHandling={'greedy'}
            >
                <MapComponent {...props} />
            </Map>
        </APIProvider>
    )
}
