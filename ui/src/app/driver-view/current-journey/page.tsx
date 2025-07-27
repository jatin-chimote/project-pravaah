
"use client";

import { useState, useEffect, useRef, useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { MapPin, Clock, Milestone, Search, Navigation, X, ShieldAlert, Camera, Send } from 'lucide-react';
import { DriverMap } from '@/components/dashboard/driver-map';
import { useToast } from '@/hooks/use-toast';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger, DialogFooter, DialogClose } from '@/components/ui/dialog';
import { Textarea } from '@/components/ui/textarea';
import { reportHazard } from '@/ai/flows/report-hazard-flow';
import { Alert, AlertTitle, AlertDescription } from '@/components/ui/alert';

const API_KEY = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY;

function HazardReportDialog({ currentPosition }: { currentPosition: { lat: number; lng: number } | null }) {
    const [isOpen, setIsOpen] = useState(false);
    const [hasCameraPermission, setHasCameraPermission] = useState<boolean | null>(null);
    const [isSubmitting, setIsSubmitting] = useState(false);
    const [description, setDescription] = useState('');
    const [capturedImage, setCapturedImage] = useState<string | null>(null);
    const videoRef = useRef<HTMLVideoElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const { toast } = useToast();

    useEffect(() => {
        let stream: MediaStream | null = null;

        const getCameraPermission = async () => {
            if (!isOpen) return;

            if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
                console.error('Camera API not supported');
                setHasCameraPermission(false);
                toast({
                    variant: 'destructive',
                    title: 'Camera Not Supported',
                    description: 'Your browser does not support camera access.',
                });
                return;
            }

            try {
                stream = await navigator.mediaDevices.getUserMedia({ video: true });
                setHasCameraPermission(true);
                if (videoRef.current) {
                    videoRef.current.srcObject = stream;
                }
            } catch (error) {
                console.error('Error accessing camera:', error);
                setHasCameraPermission(false);
                toast({
                    variant: 'destructive',
                    title: 'Camera Access Denied',
                    description: 'Please enable camera permissions in your browser settings.',
                });
            }
        };

        getCameraPermission();
        
        return () => {
             if (stream) {
                stream.getTracks().forEach(track => track.stop());
            }
        }

    }, [isOpen, toast]);

    const handleCapture = () => {
        if (!videoRef.current || !canvasRef.current) return;
        const video = videoRef.current;
        const canvas = canvasRef.current;
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const context = canvas.getContext('2d');
        if (context) {
            context.drawImage(video, 0, 0, video.videoWidth, video.videoHeight);
            setCapturedImage(canvas.toDataURL('image/jpeg'));
        }
    };

    const handleSubmit = async () => {
        if (!capturedImage) {
            toast({ title: "Error", description: "Please capture an image first.", variant: "destructive" });
            return;
        }
        if (!description) {
            toast({ title: "Error", description: "Please enter a description.", variant: "destructive" });
            return;
        }
        if (!currentPosition) {
            toast({ title: "Error", description: "Could not determine your location.", variant: "destructive" });
            return;
        }

        setIsSubmitting(true);
        try {
            const result = await reportHazard({
                photoDataUri: capturedImage,
                description,
                location: currentPosition
            });
            toast({ title: "Success", description: result.message });
            setCapturedImage(null);
            setDescription('');
            setIsOpen(false); // Close dialog on success
        } catch (error) {
            console.error("Failed to submit hazard report:", error);
            toast({ title: "Submission Failed", description: "Could not submit hazard report. Please try again.", variant: "destructive" });
        } finally {
            setIsSubmitting(false);
        }
    };


    return (
        <Dialog open={isOpen} onOpenChange={(open) => { 
            setIsOpen(open);
            if (!open) {
                setCapturedImage(null);
                setDescription('');
            }
        }}>
            <DialogTrigger asChild>
                <Button variant="destructive" className="w-full mt-2">
                    <ShieldAlert className="mr-2 h-4 w-4" /> Report Hazard
                </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
                <DialogHeader>
                    <DialogTitle>Report a Hazard</DialogTitle>
                    <DialogDescription>
                        Capture a photo of the hazard and provide a brief description.
                    </DialogDescription>
                </DialogHeader>
                <div className="grid gap-4 py-4">
                    <div className="relative aspect-video w-full">
                        {capturedImage ? (
                            <img src={capturedImage} alt="Captured Hazard" className="w-full rounded-md" />
                        ) : (
                            <video ref={videoRef} className="w-full aspect-video rounded-md bg-muted" autoPlay muted playsInline />
                        )}
                        {hasCameraPermission === false && (
                             <Alert variant="destructive" className="mt-2">
                                <AlertTitle>Camera Access Required</AlertTitle>
                                <AlertDescription>
                                    Please allow camera access to report a hazard.
                                </AlertDescription>
                            </Alert>
                        )}
                    </div>
                     <canvas ref={canvasRef} className="hidden" />

                     {capturedImage ? (
                         <Button onClick={() => setCapturedImage(null)}>
                            <Camera className="mr-2 h-4 w-4" /> Retake Photo
                        </Button>
                     ) : (
                        <Button onClick={handleCapture} disabled={!hasCameraPermission}>
                            <Camera className="mr-2 h-4 w-4" /> Capture Photo
                        </Button>
                     )}
                    
                    <Textarea 
                        placeholder="Describe the hazard (e.g., pothole, debris, accident)." 
                        value={description}
                        onChange={(e) => setDescription(e.target.value)}
                    />

                </div>
                <DialogFooter>
                    <DialogClose asChild>
                         <Button type="button" variant="secondary">Cancel</Button>
                    </DialogClose>
                    <Button onClick={handleSubmit} disabled={!capturedImage || !description || isSubmitting}>
                        {isSubmitting ? 'Submitting...' : <><Send className="mr-2 h-4 w-4" /> Submit Report</>}
                    </Button>
                </DialogFooter>
            </DialogContent>
        </Dialog>
    )
}

export default function DriverViewPage() {
  const [destination, setDestination] = useState('');
  const [routes, setRoutes] = useState<any[]>([]);
  const [selectedRouteIndex, setSelectedRouteIndex] = useState(0);

  const [currentPosition, setCurrentPosition] = useState<{ lat: number; lng: number } | null>(null);
  const [destinationPosition, setDestinationPosition] = useState<{ lat: number; lng: number } | null>(null);
  const [currentHeading, setCurrentHeading] = useState<number | null>(null);
  const [isNavigating, setIsNavigating] = useState(false);
  const watchId = useRef<number | null>(null);
  const updateInterval = useRef<NodeJS.Timeout | null>(null);
  const { toast } = useToast();

  const selectedRoute = useMemo(() => {
    if (routes.length === 0) return null;
    return routes[selectedRouteIndex];
  }, [routes, selectedRouteIndex]);
  
  const tripInfo = useMemo(() => {
    if (!selectedRoute) return { eta: '--', distance: '--', destination: 'N/A' };
    
    const durationString = selectedRoute.duration || '0s';
    const durationInSeconds = parseInt(durationString.replace('s', ''), 10);
    
    const hours = Math.floor(durationInSeconds / 3600);
    const minutes = Math.floor((durationInSeconds % 3600) / 60);

    let etaString = '';
    if (hours > 0) {
      etaString += `${hours} hr `;
    }
    if (minutes > 0 || hours === 0) {
      etaString += `${minutes} min`;
    }
    
    if (etaString.trim() === '') {
      etaString = '0 min';
    }

    return {
      eta: etaString.trim(),
      distance: `${(selectedRoute.distanceMeters / 1000).toFixed(2)} km`,
      destination: destination,
    }

  }, [selectedRoute, destination]);

  useEffect(() => {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                setCurrentPosition({
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                });
            },
            () => {
                toast({ title: "Location Error", description: "Could not get your current location. Please enable location services.", variant: "destructive" });
                setCurrentPosition({ lat: 12.9716, lng: 77.5946 }); // Fallback to Bangalore
            }
        );
    } else {
        toast({ title: "Location Error", description: "Geolocation is not supported by this browser.", variant: "destructive" });
        setCurrentPosition({ lat: 12.9716, lng: 77.5946 }); // Fallback to Bangalore
    }
    
    return () => {
        if (watchId.current) {
            navigator.geolocation.clearWatch(watchId.current);
        }
        if (updateInterval.current) {
            clearInterval(updateInterval.current);
        }
    };
  }, [toast]);
  
  useEffect(() => {
    if (isNavigating) {
      watchId.current = navigator.geolocation.watchPosition(
        (position) => {
          setCurrentPosition({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          setCurrentHeading(position.coords.heading);
        },
        () => {
          toast({ title: "Location Error", description: "Could not get your current location. Please enable location services.", variant: "destructive" });
          setIsNavigating(false);
        },
        { enableHighAccuracy: true }
      );

      // Update ETA and distance every 30 seconds
      updateInterval.current = setInterval(() => {
        handleSearch(true);
      }, 30000);

    } else {
      if (watchId.current) {
        navigator.geolocation.clearWatch(watchId.current);
        watchId.current = null;
      }
      if (updateInterval.current) {
        clearInterval(updateInterval.current);
        updateInterval.current = null;
      }
      setCurrentHeading(null);
    }
  }, [isNavigating, toast]);

  const handleSearch = async (isBackgroundUpdate = false) => {
    if (!API_KEY) {
        if (!isBackgroundUpdate) toast({ title: "API Key Error", description: "Google Maps API Key is missing.", variant: "destructive" });
        return;
    }
    if (!destination) {
        if (!isBackgroundUpdate) toast({ title: "Input Error", description: "Please enter a destination.", variant: "destructive" });
        return;
    }
    if (!currentPosition) {
        if (!isBackgroundUpdate) toast({ title: "Location Error", description: "Could not get your current location to calculate the route.", variant: "destructive" });
        return;
    }

    try {
        const response = await fetch(`https://routes.googleapis.com/directions/v2:computeRoutes`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': API_KEY,
                'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline,routes.legs.endLocation.latLng'
            },
            body: JSON.stringify({
                origin: { location: { latLng: { latitude: currentPosition.lat, longitude: currentPosition.lng } } },
                destination: { address: destination },
                travelMode: 'DRIVE',
                routingPreference: 'TRAFFIC_AWARE',
                computeAlternativeRoutes: true,
                routeModifiers: {
                    avoidTolls: false,
                    avoidHighways: false,
                    avoidFerries: false,
                },
            })
        });

        const data = await response.json();
        
        if (data.routes && data.routes.length > 0) {
          if (!isBackgroundUpdate) {
            setRoutes(data.routes);
            setSelectedRouteIndex(0);
            const endLocation = data.routes[0]?.legs?.[0]?.endLocation?.latLng;
            if(endLocation) {
              setDestinationPosition({ lat: endLocation.latitude, lng: endLocation.longitude });
            }
          } else {
            setRoutes(prevRoutes => {
              const newRoutes = [...prevRoutes];
              newRoutes[0] = { ...newRoutes[0], ...data.routes[0] };
              return newRoutes;
            });
          }
        } else if (data.error) {
            if (!isBackgroundUpdate) toast({ title: "Routing Error", description: data.error.message || "Could not find a route to the destination.", variant: "destructive" });
        } else {
             if (!isBackgroundUpdate) toast({ title: "Routing Error", description: "Could not find a route to the destination.", variant: "destructive" });
        }
    } catch(err) {
        if (!isBackgroundUpdate) toast({ title: "Routing Error", description: "An unexpected error occurred while fetching the route.", variant: "destructive" });
    }
  };
  
  const handleNavigationToggle = () => {
    if (!selectedRoute) {
        toast({ title: "Navigation Error", description: "Please set a destination first.", variant: "destructive" });
        return;
    }
    setIsNavigating(!isNavigating);
  };

  return (
    <div className="flex h-full w-full flex-col gap-4 lg:flex-row">
      <div className="flex-1 lg:order-2">
        <Card className="h-full">
            <CardHeader>
                <CardTitle>Live Map</CardTitle>
            </CardHeader>
            <CardContent>
                <div className="aspect-video w-full overflow-hidden rounded-lg">
                    <DriverMap 
                        routes={routes}
                        selectedRouteIndex={selectedRouteIndex}
                        onRouteSelect={setSelectedRouteIndex}
                        currentPosition={currentPosition} 
                        destinationPosition={destinationPosition}
                        currentHeading={currentHeading}
                        isNavigating={isNavigating} 
                    />
                </div>
            </CardContent>
        </Card>
      </div>
      <div className="w-full lg:order-1 lg:w-80">
        <Card>
          <CardHeader>
            <CardTitle>Trip Details</CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-4">
            <div className="flex items-center gap-2">
              <Input
                type="text"
                placeholder="Enter destination..."
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                className="flex-1"
                disabled={isNavigating}
              />
              <Button onClick={() => handleSearch()} size="icon" disabled={isNavigating}>
                <Search className="h-4 w-4" />
              </Button>
            </div>
            
            <div className="grid gap-4">
                <div className="flex items-center gap-3">
                    <MapPin className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <p className="text-sm text-muted-foreground">Destination</p>
                        <p className="font-semibold">{tripInfo.destination}</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Clock className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <p className="text-sm text-muted-foreground">Estimated Time</p>
                        <p className="font-semibold">{tripInfo.eta}</p>
                    </div>
                </div>
                <div className="flex items-center gap-3">
                    <Milestone className="h-5 w-5 text-muted-foreground" />
                    <div>
                        <p className="text-sm text-muted-foreground">Distance</p>
                        <p className="font-semibold">{tripInfo.distance}</p>
                    </div>
                </div>
            </div>

            <Button size="lg" className="w-full mt-2" onClick={handleNavigationToggle} variant={isNavigating ? 'destructive' : 'default'}>
                {isNavigating ? <><X className="mr-2 h-4 w-4" />Stop Navigation</> : <><Navigation className="mr-2 h-4 w-4" />Start Navigation</>}
            </Button>

            <HazardReportDialog currentPosition={currentPosition} />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

    