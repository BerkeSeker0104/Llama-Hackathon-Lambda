'use client';

import { useState } from 'react';
import { Bell, Check, CheckCheck, AlertCircle, CheckCircle2, Clock, MessageSquare, FolderKanban, Calendar, AlertTriangle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Notification } from '@/lib/mock-dashboard-data';
import { cn } from '@/lib/utils';

interface NotificationPanelProps {
  notifications: Notification[];
  unreadCount: number;
  onNotificationClick?: (notification: Notification) => void;
  onMarkAllAsRead?: () => void;
}

const getNotificationIcon = (type: Notification['type']) => {
  switch (type) {
    case 'task_assigned':
      return <AlertCircle className="h-4 w-4 text-blue-500" />;
    case 'task_completed':
      return <CheckCircle2 className="h-4 w-4 text-green-500" />;
    case 'task_due_soon':
      return <Clock className="h-4 w-4 text-orange-500" />;
    case 'project_update':
      return <FolderKanban className="h-4 w-4 text-purple-500" />;
    case 'sprint_reminder':
      return <Calendar className="h-4 w-4 text-yellow-500" />;
    case 'comment':
      return <MessageSquare className="h-4 w-4 text-cyan-500" />;
    default:
      return <Bell className="h-4 w-4 text-white/60" />;
  }
};

const getPriorityColor = (priority: Notification['priority']) => {
  switch (priority) {
    case 'high':
      return 'border-l-red-500';
    case 'medium':
      return 'border-l-yellow-500';
    case 'low':
      return 'border-l-blue-500';
    default:
      return 'border-l-white/20';
  }
};

export function NotificationPanel({
  notifications,
  unreadCount,
  onNotificationClick,
  onMarkAllAsRead,
}: NotificationPanelProps) {
  const [isOpen, setIsOpen] = useState(false);

  const handleNotificationClick = (notification: Notification) => {
    onNotificationClick?.(notification);
    if (notification.link) {
      window.location.href = notification.link;
    }
  };

  return (
    <Popover open={isOpen} onOpenChange={setIsOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          className="text-white/60 hover:text-white hover:bg-white/5 relative"
        >
          <Bell size={20} />
          {unreadCount > 0 && (
            <span className="absolute top-1 right-1 w-2 h-2 bg-[#38FF5D] rounded-full"></span>
          )}
        </Button>
      </PopoverTrigger>
      <PopoverContent align="end" className="w-[380px] p-0">
        <div className="flex flex-col max-h-[500px]">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-white/10">
            <div className="flex items-center gap-2">
              <Bell size={18} className="text-white" />
              <h3 className="font-semibold text-white">Bildirimler</h3>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 text-xs font-medium bg-[#38FF5D] text-black rounded-full">
                  {unreadCount}
                </span>
              )}
            </div>
            {unreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                className="text-xs text-white/60 hover:text-white"
                onClick={onMarkAllAsRead}
              >
                <CheckCheck size={14} className="mr-1" />
                Tümünü Oku
              </Button>
            )}
          </div>

          {/* Notification List */}
          <div className="overflow-y-auto max-h-[400px]">
            {notifications.length === 0 ? (
              <div className="p-8 text-center">
                <Bell className="h-12 w-12 text-white/20 mx-auto mb-3" />
                <p className="text-white/60 text-sm">Bildirim yok</p>
              </div>
            ) : (
              <div className="divide-y divide-white/10">
                {notifications.map((notification) => (
                  <div
                    key={notification.id}
                    className={cn(
                      'p-4 hover:bg-white/5 cursor-pointer transition-colors border-l-4',
                      !notification.read ? 'bg-white/5' : 'bg-transparent',
                      getPriorityColor(notification.priority)
                    )}
                    onClick={() => handleNotificationClick(notification)}
                  >
                    <div className="flex gap-3">
                      <div className="mt-1 flex-shrink-0">
                        {getNotificationIcon(notification.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-start justify-between gap-2">
                          <h4 className="font-medium text-white text-sm line-clamp-1">
                            {notification.title}
                          </h4>
                          {!notification.read && (
                            <div className="h-2 w-2 bg-[#38FF5D] rounded-full flex-shrink-0 mt-1"></div>
                          )}
                        </div>
                        <p className="text-sm text-white/70 mt-1 line-clamp-2">
                          {notification.message}
                        </p>
                        <p className="text-xs text-white/50 mt-2">
                          {notification.timestamp}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="p-3 border-t border-white/10">
              <Button
                variant="ghost"
                size="sm"
                className="w-full text-sm text-white/60 hover:text-white"
              >
                Tümünü Görüntüle
              </Button>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}
