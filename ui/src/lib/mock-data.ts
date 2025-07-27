import { Vehicle, Driver, Route, Journey, Alert, User, Client, DriverJourney } from './types';

export const mockVehicles: Vehicle[] = [
  { id: 'V001', vehicleNumber: 'MH12AB1234', displayName: 'City Bus 1', type: 'Bus', capacity: 50, liveStatus: 'En Route', driverId: 'D001', driverName: 'Ramesh Kumar' },
  { id: 'V002', vehicleNumber: 'KA01CD5678', displayName: 'Metro Feeder 5', type: 'Minivan', capacity: 15, liveStatus: 'En Route', driverId: 'D002', driverName: 'Sita Sharma' },
  { id: 'V003', vehicleNumber: 'DL03EF9012', displayName: 'City Bus 2', type: 'Bus', capacity: 50, liveStatus: 'Idle', driverId: 'D003', driverName: 'Amit Patel' },
  { id: 'V004', vehicleNumber: 'TN04GH3456', displayName: 'Airport Shuttle', type: 'Minivan', capacity: 20, liveStatus: 'Maintenance', driverId: 'D004', driverName: 'Priya Singh' },
  { id: 'V005', vehicleNumber: 'UP05IJ7890', displayName: 'Rapid Transit 3', type: 'Bus', capacity: 60, liveStatus: 'Idle' },
];

export const mockDrivers: Driver[] = [
    { id: 'D001', fullName: 'Ramesh Kumar', employeeId: 'EMP101', contactNumber: '+919876543210', primaryVehicleId: 'V001' },
    { id: 'D002', fullName: 'Sita Sharma', employeeId: 'EMP102', contactNumber: '+919876543211', primaryVehicleId: 'V002' },
    { id: 'D003', fullName: 'Amit Patel', employeeId: 'EMP103', contactNumber: '+919876543212', primaryVehicleId: 'V003' },
    { id: 'D004', fullName: 'Priya Singh', employeeId: 'EMP104', contactNumber: '+919876543213', primaryVehicleId: 'V004' },
];

export const mockRoutes: Route[] = [
    { id: 'R01', routeName: 'Downtown Loop', waypoints: [{ stopNumber: 1, lat: 12.9716, lng: 77.5946, stopName: 'City Center' }, { stopNumber: 2, lat: 12.9784, lng: 77.5978, stopName: 'Main Square' }] },
    { id: 'R02', routeName: 'Tech Park Express', waypoints: [{ stopNumber: 1, lat: 12.9592, lng: 77.6438, stopName: 'IT Hub' }, { stopNumber: 2, lat: 12.9279, lng: 77.6271, stopName: 'Residential Area' }] },
];

export const mockJourneys: Journey[] = [
    { id: 'J001', routeId: 'R01', routeName: 'Downtown Loop', vehicleId: 'V001', vehicleName: 'City Bus 1', driverId: 'D001', driverName: 'Ramesh Kumar', status: 'Ongoing', scheduledStartTime: '2024-08-15T09:00:00Z', actualStartTime: '2024-08-15T09:02:00Z', predictedEndTime: '2024-08-15T10:05:00Z' },
    { id: 'J002', routeId: 'R02', routeName: 'Tech Park Express', vehicleId: 'V002', vehicleName: 'Metro Feeder 5', driverId: 'D002', driverName: 'Sita Sharma', status: 'Scheduled', scheduledStartTime: '2024-08-15T09:30:00Z' },
    { id: 'J003', routeId: 'R01', routeName: 'Downtown Loop', vehicleId: 'V003', vehicleName: 'City Bus 2', driverId: 'D003', driverName: 'Amit Patel', status: 'Completed', scheduledStartTime: '2024-08-15T08:00:00Z', actualStartTime: '2024-08-15T08:00:00Z' },
];

export const mockAlerts: Alert[] = [
  { id: 'A001', journeyId: 'J001', timestamp: '2024-08-15T10:00:00Z', alertType: 'Predictive Gridlock', message: 'Potential gridlock on MG Road in 15 mins.', recommendedAction: 'Reroute via Brigade Road.', newRouteId: 'R01-ALT', status: 'Issued' },
  { id: 'A002', journeyId: 'J001', timestamp: '2024-08-15T09:55:00Z', alertType: 'Heavy Traffic', message: 'Heavy traffic near Indiranagar junction.', recommendedAction: 'Proceed with caution. Minor delay expected.', status: 'Acted' },
  { id: 'A003', journeyId: 'J002', timestamp: '2024-08-15T09:35:00Z', alertType: 'Road Closure', message: 'Road closed for event at Koramangala.', recommendedAction: 'Reroute applied automatically.', newRouteId: 'R02-ALT-2', status: 'Dismissed' },
];

export const mockUsers: User[] = [
    { id: 'U01', email: 'admin@urbanflow.com', fullName: 'Global Admin', role: 'Admin', createdAt: '2023-01-15T10:00:00Z' },
    { id: 'U02', email: 'manager@citycorp.com', fullName: 'CityCorp Manager', role: 'Manager', createdAt: '2023-02-20T11:30:00Z' },
    { id: 'U03', email: 'viewer@citycorp.com', fullName: 'CityCorp Viewer', role: 'Viewer', createdAt: '2023-03-10T09:00:00Z' },
];

export const mockClients: Client[] = [
    { id: 'C01', clientName: 'CityCorp Transport', subscriptionStatus: 'Active', createdAt: '2023-01-10T12:00:00Z' },
    { id: 'C02', clientName: 'Metro Connect', subscriptionStatus: 'Trial', createdAt: '2023-05-01T14:00:00Z' },
    { id: 'C03', clientName: 'State Roadways', subscriptionStatus: 'Inactive', createdAt: '2022-11-20T18:00:00Z' },
];

export const mockDriverJourneys: DriverJourney[] = [
    { id: 'DJ001', routeName: 'R01 - Downtown Loop', source: 'City Center', destination: 'Main Square', vehicle: 'V001 - City Bus 1', scheduledTime: '09:00 AM', status: 'Ongoing'},
    { id: 'DJ002', routeName: 'R02 - Tech Park Express', source: 'IT Hub', destination: 'Residential Area', vehicle: 'V002 - Metro Feeder 5', scheduledTime: '11:30 AM', status: 'Pending'},
    { id: 'DJ003', routeName: 'R03 - Airport Run', source: 'City Center', destination: 'International Airport', vehicle: 'V004 - Airport Shuttle', scheduledTime: '02:00 PM', status: 'Pending'},
    { id: 'DJ004', routeName: 'R01 - Downtown Loop', source: 'City Center', destination: 'Main Square', vehicle: 'V001 - City Bus 1', scheduledTime: '04:00 PM', status: 'Completed'},
    { id: 'DJ005', routeName: 'R04 - Crosstown', source: 'East Suburb', destination: 'West Suburb', vehicle: 'V005 - Rapid Transit 3', scheduledTime: '06:30 PM', status: 'Cancelled'},
];
