'use client';

import { LayoutDashboard, FolderKanban, Users, ExternalLink, MessageCircle } from "lucide-react";
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';

interface SidebarProps {
  className?: string;
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname();

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, href: '/' },
    { id: 'chat', label: 'Chat', icon: MessageCircle, href: '/chat' },
    { id: 'projects', label: 'Projects', icon: FolderKanban, href: '/projects' },
    { id: 'teams', label: 'Teams', icon: Users, href: '/employees' },
  ];

  const integrations = [
    { 
      id: 'jira', 
      label: 'Jira', 
      icon: '/jira.png', 
      href: '#',
      isImage: true 
    },
    { 
      id: 'google-calendar', 
      label: 'Google Calendar', 
      icon: '/Google_Calendar_icon_(2015-2020).svg', 
      href: '#',
      isImage: true 
    },
  ];

  return (
    <div className={`w-64 bg-black border-r border-white/10 h-screen flex flex-col ${className || ''}`}>
      <div className="p-6 border-b border-white/10">
        <h1 className="text-xl text-white">Tella</h1>
        <p className="text-xs text-white/60 mt-1">AI Project Management</p>
      </div>
      
      <nav className="flex-1 p-4">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = pathname === item.href || 
            (item.id === 'dashboard' && pathname === '/') ||
            (item.id === 'chat' && pathname.startsWith('/chat')) ||
            (item.id === 'projects' && pathname.startsWith('/projects')) ||
            (item.id === 'teams' && pathname.startsWith('/employees'));
          
          return (
            <Link
              key={item.id}
              href={item.href}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all ${
                isActive 
                  ? 'bg-[#38FF5D] text-black' 
                  : 'text-white/60 hover:bg-white/10 hover:text-white'
              }`}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Integration Buttons */}
      <div className="p-4 border-t border-white/10">
        <h3 className="text-xs text-white/40 mb-3 font-medium">INTEGRATIONS</h3>
        {integrations.map((integration) => (
          <a
            key={integration.id}
            href={integration.href}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-all text-white/60 hover:bg-white/10 hover:text-white group"
          >
            {integration.isImage ? (
              <Image
                src={integration.icon}
                alt={integration.label}
                width={20}
                height={20}
                className="object-contain"
              />
            ) : (
              <ExternalLink size={20} />
            )}
            <span className="flex-1">{integration.label}</span>
            <ExternalLink size={14} className="opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
        ))}
      </div>
    </div>
  );
}
