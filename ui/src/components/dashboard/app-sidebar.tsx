
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Sidebar,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarSeparator,
  SidebarMenuSub,
  SidebarMenuSubButton,
} from "@/components/ui/sidebar";
import {
  LayoutDashboard,
  Truck,
  UserCircle,
  Map as MapIcon,
  GitFork,
  Siren,
  Users,
  Building,
  Settings,
  Globe,
  ChevronDown,
  CircleDot,
  List,
} from "lucide-react";
import { AppLogo } from "@/components/icons";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { cn } from "@/lib/utils";

const menuItems = [
  { href: "/", label: "Dashboard", icon: LayoutDashboard },
  { href: "/vehicles", label: "Vehicles", icon: Truck },
  { href: "/drivers", label: "Drivers", icon: UserCircle },
  { href: "/routes", label: "Routes", icon: MapIcon },
  { href: "/journeys", label: "Journeys", icon: GitFork },
  { href: "/alerts", label: "Alerts", icon: Siren },
];

const driverViewSubItems = [
    { href: "/driver-view/current-journey", label: "Current Journey", icon: CircleDot },
    { href: "/driver-view/all-journeys", label: "All Journeys", icon: List },
];

const adminMenuItems = [
    { href: "/users", label: "Users", icon: Users },
    { href: "/clients", label: "Clients", icon: Building },
];

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar collapsible="icon" variant="sidebar">
      <SidebarHeader className="h-14 items-center justify-center p-2 group-data-[collapsible=icon]:h-10 group-data-[collapsible=icon]:justify-center">
        <Link href="/" className="flex items-center gap-2 font-bold text-primary-foreground">
          <AppLogo className="h-6 w-6 text-primary" />
          <span className="text-lg group-data-[collapsible=icon]:hidden">Pravaah</span>
        </Link>
      </SidebarHeader>
      <SidebarMenu className="flex-1 p-2">
        {menuItems.map((item) => (
          <SidebarMenuItem key={item.href}>
            <SidebarMenuButton
              href={item.href}
              isActive={pathname === item.href}
              tooltip={item.label}
            >
              <item.icon />
              <span>{item.label}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}

        <Collapsible asChild>
            <SidebarMenuItem>
                <CollapsibleTrigger asChild>
                    <SidebarMenuButton
                        href="#"
                        isActive={pathname.startsWith("/driver-view")}
                        tooltip="Driver View"
                        className="justify-between group-data-[collapsible=icon]:justify-center"
                    >
                        <Globe />
                        <span className="group-data-[collapsible=icon]:hidden">Driver View</span>
                        <ChevronDown className="h-4 w-4 group-data-[collapsible=icon]:hidden transition-transform [&[data-state=open]]:-rotate-180" />
                    </SidebarMenuButton>
                </CollapsibleTrigger>
                 <CollapsibleContent asChild>
                    <SidebarMenuSub>
                        {driverViewSubItems.map((item) => (
                            <li key={item.href}>
                                <SidebarMenuSubButton
                                    href={item.href}
                                    isActive={pathname === item.href}
                                >
                                    <item.icon/>
                                    <span>{item.label}</span>
                                </SidebarMenuSubButton>
                            </li>
                        ))}
                    </SidebarMenuSub>
                </CollapsibleContent>
            </SidebarMenuItem>
        </Collapsible>
        
        <SidebarSeparator className="my-2"/>
        {adminMenuItems.map((item) => (
          <SidebarMenuItem key={item.href}>
            <SidebarMenuButton
              href={item.href}
              isActive={pathname === item.href}
              tooltip={item.label}
            >
              <item.icon />
              <span>{item.label}</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        ))}
      </SidebarMenu>
      <SidebarFooter className="p-2">
        <SidebarMenuItem>
            <SidebarMenuButton href="#" tooltip="Settings">
              <Settings />
              <span>Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
      </SidebarFooter>
    </Sidebar>
  );
}
