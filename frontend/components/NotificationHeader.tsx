'use client';

import { NotificationPanel } from './NotificationPanel';
import { getMockNotifications, getUnreadNotificationCount } from '@/lib/mock-dashboard-data';
import { useState } from 'react';

export function NotificationHeader() {
  const [notifications, setNotifications] = useState(() => getMockNotifications());
  const unreadCount = getUnreadNotificationCount(notifications);

  const handleMarkAllAsRead = () => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  };

  const handleNotificationClick = () => {
    // Handle notification click
  };

  return (
    <NotificationPanel
      notifications={notifications}
      unreadCount={unreadCount}
      onNotificationClick={handleNotificationClick}
      onMarkAllAsRead={handleMarkAllAsRead}
    />
  );
}
