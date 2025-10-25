import type { Metadata } from "next";
import "./globals.css";
import { Providers } from './providers';
import { Toaster } from '@/components/ui/toaster';
import Link from 'next/link';

export const metadata: Metadata = {
  title: "Proje Yöneticisi AI Asistanı",
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
                <Link href="/" className="text-xl font-bold">
                  PM AI Asistanı
                </Link>
                <div className="flex gap-4">
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
