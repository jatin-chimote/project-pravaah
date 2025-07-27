"use client";

import { useState } from 'react';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { MoreHorizontal, PlusCircle, Trash2, FilePenLine } from "lucide-react";
import { mockVehicles } from "@/lib/mock-data";
import type { Vehicle } from "@/lib/types";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { AlertDialog, AlertDialogAction, AlertDialogCancel, AlertDialogContent, AlertDialogDescription, AlertDialogFooter, AlertDialogHeader, AlertDialogTitle } from '@/components/ui/alert-dialog';

const initialVehicles = mockVehicles;

export default function VehiclesPage() {
    const [vehicles, setVehicles] = useState<Vehicle[]>(initialVehicles);
    const [isFormOpen, setIsFormOpen] = useState(false);
    const [isDeleteAlertOpen, setIsDeleteAlertOpen] = useState(false);
    const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);

    const handleAddClick = () => {
        setSelectedVehicle(null);
        setIsFormOpen(true);
    };
    
    const handleEditClick = (vehicle: Vehicle) => {
        setSelectedVehicle(vehicle);
        setIsFormOpen(true);
    };

    const handleDeleteClick = (vehicle: Vehicle) => {
        setSelectedVehicle(vehicle);
        setIsDeleteAlertOpen(true);
    };

    const confirmDelete = () => {
        if(selectedVehicle) {
            setVehicles(vehicles.filter(v => v.id !== selectedVehicle.id));
        }
        setIsDeleteAlertOpen(false);
        setSelectedVehicle(null);
    }
    
    const handleFormSubmit = (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        const formData = new FormData(e.currentTarget);
        const vehicleData = Object.fromEntries(formData.entries()) as Omit<Vehicle, 'id' | 'liveStatus' | 'capacity'> & { capacity: string };

        if (selectedVehicle) {
            // Edit vehicle
            const updatedVehicle = { ...selectedVehicle, ...vehicleData, capacity: Number(vehicleData.capacity) };
            setVehicles(vehicles.map(v => v.id === selectedVehicle.id ? updatedVehicle : v));
        } else {
            // Add new vehicle
            const newVehicle: Vehicle = {
                id: `V${Math.floor(Math.random() * 1000)}`,
                ...vehicleData,
                capacity: Number(vehicleData.capacity),
                liveStatus: 'Idle'
            };
            setVehicles([newVehicle, ...vehicles]);
        }
        setIsFormOpen(false);
        setSelectedVehicle(null);
    };

    const getStatusBadge = (status: Vehicle['liveStatus']) => {
        switch (status) {
            case 'En Route':
                return <Badge variant="default" className="bg-green-500 hover:bg-green-600">En Route</Badge>;
            case 'Idle':
                return <Badge variant="secondary">Idle</Badge>;
            case 'Maintenance':
                return <Badge variant="destructive">Maintenance</Badge>;
        }
    };

    return (
        <>
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Vehicles</h1>
                    <p className="text-muted-foreground">Manage your fleet of vehicles.</p>
                </div>
                <Button onClick={handleAddClick}>
                    <PlusCircle className="mr-2 h-4 w-4" />
                    Add Vehicle
                </Button>
            </div>
            <Card>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Vehicle ID</TableHead>
                                <TableHead>Display Name</TableHead>
                                <TableHead>Type</TableHead>
                                <TableHead>Capacity</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Driver</TableHead>
                                <TableHead><span className="sr-only">Actions</span></TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {vehicles.map((vehicle) => (
                                <TableRow key={vehicle.id}>
                                    <TableCell className="font-medium">{vehicle.id}</TableCell>
                                    <TableCell>{vehicle.displayName}</TableCell>
                                    <TableCell>{vehicle.type}</TableCell>
                                    <TableCell>{vehicle.capacity}</TableCell>
                                    <TableCell>{getStatusBadge(vehicle.liveStatus)}</TableCell>
                                    <TableCell>{vehicle.driverName || 'Unassigned'}</TableCell>
                                    <TableCell>
                                        <DropdownMenu>
                                            <DropdownMenuTrigger asChild>
                                                <Button aria-haspopup="true" size="icon" variant="ghost">
                                                    <MoreHorizontal className="h-4 w-4" />
                                                    <span className="sr-only">Toggle menu</span>
                                                </Button>
                                            </DropdownMenuTrigger>
                                            <DropdownMenuContent align="end">
                                                <DropdownMenuItem onSelect={() => handleEditClick(vehicle)}>
                                                    <FilePenLine className="mr-2 h-4 w-4" /> Edit
                                                </DropdownMenuItem>
                                                <DropdownMenuItem onSelect={() => handleDeleteClick(vehicle)} className="text-destructive">
                                                    <Trash2 className="mr-2 h-4 w-4" /> Delete
                                                </DropdownMenuItem>
                                            </DropdownMenuContent>
                                        </DropdownMenu>
                                    </TableCell>
                                </TableRow>
                            ))}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            <Dialog open={isFormOpen} onOpenChange={setIsFormOpen}>
                <DialogContent>
                    <DialogHeader>
                        <DialogTitle>{selectedVehicle ? 'Edit Vehicle' : 'Add New Vehicle'}</DialogTitle>
                        <DialogDescription>
                            Fill in the details below to {selectedVehicle ? 'update the' : 'add a new'} vehicle.
                        </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleFormSubmit} className="grid gap-4 py-4">
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="displayName" className="text-right">Display Name</Label>
                            <Input id="displayName" name="displayName" defaultValue={selectedVehicle?.displayName} className="col-span-3" required/>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="vehicleNumber" className="text-right">Vehicle No.</Label>
                            <Input id="vehicleNumber" name="vehicleNumber" defaultValue={selectedVehicle?.vehicleNumber} className="col-span-3" required/>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="type" className="text-right">Type</Label>
                            <Select name="type" defaultValue={selectedVehicle?.type} required>
                                <SelectTrigger className="col-span-3">
                                    <SelectValue placeholder="Select vehicle type" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectItem value="Bus">Bus</SelectItem>
                                    <SelectItem value="Minivan">Minivan</SelectItem>
                                    <SelectItem value="Sedan">Sedan</SelectItem>
                                </SelectContent>
                            </Select>
                        </div>
                        <div className="grid grid-cols-4 items-center gap-4">
                            <Label htmlFor="capacity" className="text-right">Capacity</Label>
                            <Input id="capacity" name="capacity" type="number" defaultValue={selectedVehicle?.capacity} className="col-span-3" required/>
                        </div>
                        <DialogFooter>
                            <Button type="submit">{selectedVehicle ? 'Save Changes' : 'Create Vehicle'}</Button>
                        </DialogFooter>
                    </form>
                </DialogContent>
            </Dialog>

            <AlertDialog open={isDeleteAlertOpen} onOpenChange={setIsDeleteAlertOpen}>
                <AlertDialogContent>
                    <AlertDialogHeader>
                        <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                        <AlertDialogDescription>
                            This action cannot be undone. This will permanently delete the vehicle
                            <span className="font-bold"> {selectedVehicle?.displayName}</span>.
                        </AlertDialogDescription>
                    </AlertDialogHeader>
                    <AlertDialogFooter>
                        <AlertDialogCancel>Cancel</AlertDialogCancel>
                        <AlertDialogAction onClick={confirmDelete} className="bg-destructive hover:bg-destructive/90">Delete</AlertDialogAction>
                    </AlertDialogFooter>
                </AlertDialogContent>
            </AlertDialog>
        </>
    );
}
