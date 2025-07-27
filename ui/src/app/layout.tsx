import type { Metadata } from 'next';
import './globals.css';
import { AppSidebar } from '@/components/dashboard/app-sidebar';
import { SidebarProvider } from '@/components/ui/sidebar';
import { Toaster } from '@/components/ui/toaster';
import { AppHeader } from '@/components/dashboard/app-header';

export const metadata: Metadata = {
  title: 'Pravaah - AI-Powered Urban Mobility',
  description: 'Pravaah: An AI-powered urban mobility management system aimed at reducing traffic congestion in Indian cities.',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="font-body antialiased">
        <SidebarProvider>
            <div className="relative flex min-h-screen w-full">
              <AppSidebar />
              <div className="flex flex-col w-full">
                <AppHeader />
                <main className="flex-1 p-4 md:p-6 lg:p-8 bg-background overflow-auto">
                  {children}
                </main>
              </div>
            </div>
            <Toaster />
        </SidebarProvider>
      </body>
    </html>
  );
}
