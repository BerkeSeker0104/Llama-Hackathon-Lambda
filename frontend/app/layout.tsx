'use client';

import type { Metadata } from "next";
import "./globals.css";
import { Providers } from './providers';
import { Toaster } from '@/components/ui/toaster';
import { Sidebar } from '@/components/Sidebar';
import { NotificationHeader } from '@/components/NotificationHeader';
import { Search } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body className="antialiased">
        <Providers>
          <div className="flex h-screen bg-black overflow-hidden">
            <Sidebar />
            
            <div className="flex-1 flex flex-col overflow-hidden">
              {/* Header */}
              <header className="bg-black border-b border-white/10 px-8 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-4 flex-1 max-w-2xl">
                    <div className="relative flex-1">
                      <Search size={18} className="absolute left-3 top-1/2 -translate-y-1/2 text-white/40" />
                      <Input 
                        placeholder="Search projects, tasks, or team members..." 
                        className="pl-10 bg-black border-white/10 text-white placeholder:text-white/40"
                      />
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <NotificationHeader />
                    <div className="flex items-center gap-3">
                      <Avatar className="w-9 h-9">
                        <AvatarImage src="/woman-1254454_1280.jpg" alt="Ceren Arın" />
                        <AvatarFallback className="bg-[#38FF5D] text-black">
                          CA
                        </AvatarFallback>
                      </Avatar>
                      <div className="text-white">
                        <div className="text-sm font-medium">Ceren Arın</div>
                        <div className="text-xs text-white/60">Project Manager</div>
                      </div>
                    </div>
                  </div>
                </div>
              </header>

              {/* Main Content */}
              <main className="flex-1 overflow-y-auto p-8">
                <div className="max-w-[1800px] mx-auto">
                  {children}
                </div>
              </main>
            </div>
          </div>
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
