export type Vehicle = {
  id: string;
  vehicleNumber: string;
  displayName: string;
  type: 'Bus' | 'Minivan' | 'Sedan';
  capacity: number;
  liveStatus: 'Idle' | 'En Route' | 'Maintenance';
  driverId?: string;
  driverName?: string;
};

export type Driver = {
  id: string;
  fullName: string;
  employeeId: string;
  contactNumber: string;
  primaryVehicleId?: string;
};

export type Route = {
  id: string;
  routeName: string;
  waypoints: {
    stopNumber: number;
    lat: number;
    lng: number;
    stopName: string;
  }[];
};

export type Journey = {
  id: string;
  routeId: string;
  routeName: string;
  vehicleId: string;
  vehicleName: string;
  driverId: string;
  driverName: string;
  status: 'Scheduled' | 'Ongoing' | 'Completed' | 'Cancelled';
  scheduledStartTime: string;
  actualStartTime?: string;
  predictedEndTime?: string;
};

export type Alert = {
  id: string;
  journeyId: string;
  timestamp: string;
  alertType: 'Predictive Gridlock' | 'Heavy Traffic' | 'Road Closure';
  message: string;
  recommendedAction: string;
  newRouteId?: string;
  status: 'Issued' | 'Dismissed' | 'Acted';
};

export type User = {
  id: string;
  email: string;
  fullName: string;
  role: 'Admin' | 'Manager' | 'Viewer';
  createdAt: string;
};

export type Client = {
  id: string;
  clientName: string;
  subscriptionStatus: 'Active' | 'Inactive' | 'Trial';
  createdAt: string;
};

export type DriverJourney = {
  id: string;
  routeName: string;
  source: string;
  destination: string;
  vehicle: string;
  scheduledTime: string;
  status: 'Pending' | 'Ongoing' | 'Completed' | 'Cancelled';
};
