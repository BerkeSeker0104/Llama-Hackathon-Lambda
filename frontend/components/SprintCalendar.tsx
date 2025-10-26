'use client';

import { useMemo } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

interface CalendarEvent {
  id: string;
  title: string;
  start: string;
  end: string;
  type: 'sprint' | 'task';
  status: string;
  priority?: string;
  assignee?: string;
  description?: string;
}

interface SprintCalendarProps {
  events: CalendarEvent[];
}

export function SprintCalendar({ events }: SprintCalendarProps) {
  // Sprint'leri ve task'ları ayır
  const { sprints, tasks } = useMemo(() => {
    const sprints = events.filter((e) => e.type === 'sprint');
    const tasks = events.filter((e) => e.type === 'task');
    return { sprints, tasks };
  }, [events]);

  // Renk belirleme fonksiyonları
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500';
      case 'in_progress':
        return 'bg-blue-500';
      case 'blocked':
        return 'bg-red-500';
      case 'not_started':
      case 'pending':
        return 'bg-gray-400';
      default:
        return 'bg-gray-400';
    }
  };

  const getPriorityColor = (priority?: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-600';
      case 'high':
        return 'bg-orange-500';
      case 'medium':
        return 'bg-yellow-500';
      case 'low':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('tr-TR', { 
      month: 'short', 
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatDateRange = (startStr: string, endStr: string) => {
    const start = new Date(startStr);
    const end = new Date(endStr);
    const startFormatted = start.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short' });
    const endFormatted = end.toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' });
    return `${startFormatted} - ${endFormatted}`;
  };

  const getStatusText = (status: string) => {
    const statusMap: Record<string, string> = {
      completed: 'Tamamlandı',
      in_progress: 'Devam Ediyor',
      blocked: 'Bloke',
      not_started: 'Başlamadı',
      pending: 'Bekliyor',
      planned: 'Planlandı',
    };
    return statusMap[status] || status;
  };

  if (events.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Sprint Takvimi</CardTitle>
        </CardHeader>
        <CardContent className="py-12 text-center text-muted-foreground">
          <div className="flex flex-col items-center gap-3">
            <div className="text-4xl">📅</div>
            <p className="text-lg font-medium">Takvimde gösterilecek etkinlik bulunamadı</p>
            <p className="text-sm">Sprint planı oluşturulduktan sonra takvim burada görünecek</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Sprint Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Sprint Takvimi</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {sprints.map((sprint) => (
              <div key={sprint.id} className="border-l-4 border-primary pl-4 pb-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-semibold text-lg">{sprint.title}</h3>
                  <Badge variant="outline">{getStatusText(sprint.status)}</Badge>
                </div>
                <p className="text-sm font-medium text-muted-foreground mb-2">
                  📅 {formatDateRange(sprint.start, sprint.end)}
                </p>
                {sprint.description && (
                  <p className="text-sm text-muted-foreground italic mb-3">{sprint.description}</p>
                )}
                
                {/* Sprint içindeki task'lar */}
                <div className="mt-4 space-y-2">
                  {tasks
                    .filter((task) => {
                      const taskStart = new Date(task.start);
                      const sprintStart = new Date(sprint.start);
                      const sprintEnd = new Date(sprint.end);
                      return taskStart >= sprintStart && taskStart <= sprintEnd;
                    })
                    .map((task) => (
                      <div
                        key={task.id}
                        className="bg-muted p-3 rounded-lg flex items-center justify-between"
                      >
                        <div className="flex items-center gap-3 flex-1">
                          <div
                            className={`w-2 h-2 rounded-full ${getStatusColor(task.status)}`}
                          />
                          <div className="flex-1">
                            <p className="font-medium text-sm">{task.title}</p>
                            <p className="text-xs text-muted-foreground">
                              👤 {task.assignee || 'Atanmamış'} • 📅 {formatDateRange(task.start, task.end)}
                            </p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          {task.priority && (
                            <Badge
                              className={`${getPriorityColor(task.priority)} text-white text-xs`}
                            >
                              {task.priority}
                            </Badge>
                          )}
                          <Badge variant="secondary" className="text-xs">
                            {getStatusText(task.status)}
                          </Badge>
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Durum Göstergeleri</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-green-500" />
              <span className="text-sm">Tamamlandı</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-blue-500" />
              <span className="text-sm">Devam Ediyor</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-red-500" />
              <span className="text-sm">Bloke</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full bg-gray-400" />
              <span className="text-sm">Başlamadı</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

