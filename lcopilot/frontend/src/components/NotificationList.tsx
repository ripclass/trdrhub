import React from 'react';
import { Bell, CheckCircle, AlertTriangle, Clock, X } from 'lucide-react';

interface Notification {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  status: 'success' | 'warning' | 'info' | 'error';
  read: boolean;
}

interface NotificationListProps {
  notifications: Notification[];
  onMarkAsRead?: (id: string) => void;
  onDismiss?: (id: string) => void;
  maxItems?: number;
}

const NotificationList: React.FC<NotificationListProps> = ({
  notifications,
  onMarkAsRead,
  onDismiss,
  maxItems = 10,
}) => {
  const getStatusIcon = (status: Notification['status']) => {
    switch (status) {
      case 'success':
        return <CheckCircle size={16} className="text-green-500" />;
      case 'warning':
        return <AlertTriangle size={16} className="text-yellow-500" />;
      case 'error':
        return <AlertTriangle size={16} className="text-red-500" />;
      default:
        return <Bell size={16} className="text-blue-500" />;
    }
  };

  const getStatusBadge = (status: Notification['status']) => {
    switch (status) {
      case 'success':
        return 'status-badge status-verified';
      case 'warning':
        return 'status-badge status-warning';
      case 'error':
        return 'status-badge status-high';
      default:
        return 'status-badge status-low';
    }
  };

  const formatTimestamp = (timestamp: Date) => {
    const now = new Date();
    const diff = now.getTime() - timestamp.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return timestamp.toLocaleDateString();
  };

  const displayNotifications = notifications.slice(0, maxItems);

  if (displayNotifications.length === 0) {
    return (
      <div className="card p-6 text-center">
        <Bell size={48} className="mx-auto text-gray-300 mb-4" />
        <p className="text-gray-500">No notifications</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {displayNotifications.map((notification) => (
        <div
          key={notification.id}
          className={`card p-4 transition-all ${
            !notification.read ? 'border-l-4 border-l-primary-500 bg-green-50' : ''
          }`}
        >
          <div className="flex items-start gap-3">
            <div className="flex-shrink-0 mt-0.5">
              {getStatusIcon(notification.status)}
            </div>

            <div className="flex-1 min-w-0">
              <div className="flex items-start justify-between gap-2">
                <h4 className="text-sm font-medium text-gray-900 truncate">
                  {notification.title}
                </h4>
                <div className="flex items-center gap-2 flex-shrink-0">
                  <span className={getStatusBadge(notification.status)}>
                    {notification.status}
                  </span>
                  {onDismiss && (
                    <button
                      onClick={() => onDismiss(notification.id)}
                      className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                      aria-label="Dismiss notification"
                    >
                      <X size={14} />
                    </button>
                  )}
                </div>
              </div>

              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                {notification.message}
              </p>

              <div className="flex items-center justify-between mt-2">
                <div className="flex items-center gap-1 text-xs text-gray-500">
                  <Clock size={12} />
                  <span>{formatTimestamp(notification.timestamp)}</span>
                </div>

                {!notification.read && onMarkAsRead && (
                  <button
                    onClick={() => onMarkAsRead(notification.id)}
                    className="text-xs text-green-600 hover:text-green-700 font-medium"
                  >
                    Mark as read
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}

      {notifications.length > maxItems && (
        <div className="text-center py-2">
          <p className="text-sm text-gray-500">
            Showing {maxItems} of {notifications.length} notifications
          </p>
        </div>
      )}
    </div>
  );
};

export default NotificationList;