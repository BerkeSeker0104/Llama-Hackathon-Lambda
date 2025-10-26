import type { Metadata } from "next";
import "./globals.css";
import { Providers } from './providers';
import { Toaster } from '@/components/ui/toaster';
import Link from 'next/link';
import Image from 'next/image';

export const metadata: Metadata = {
  title: "Tella - Proje Yöneticisi AI Asistanı",
  description: "Yapay zeka destekli proje analizi, görev yönetimi ve kaynak tahsisi",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body className="antialiased">
        <Providers>
          <nav className="border-b">
            <div className="container mx-auto px-4 py-4">
              <div className="flex items-center justify-between">
                <Link href="/" className="flex items-center gap-3">
                  <Image 
                    src="/tella_logo.png" 
                    alt="Tella Logo" 
                    width={150} 
                    height={40}
                    className="h-8 w-auto"
                    priority
                  />
                </Link>
                <div className="flex gap-4">
                  <Link href="/" className="hover:text-primary transition">
                    Dashboard
                  </Link>
                  <Link href="/projects" className="hover:text-primary transition">
                    Projeler
                  </Link>
                  <Link href="/chat" className="hover:text-primary transition">
                    Sohbet
                  </Link>
                  <Link href="/employees" className="hover:text-primary transition">
                    Çalışanlar
                  </Link>
                </div>
              </div>
            </div>
          </nav>
          {children}
          <Toaster />
        </Providers>
      </body>
    </html>
  );
}
