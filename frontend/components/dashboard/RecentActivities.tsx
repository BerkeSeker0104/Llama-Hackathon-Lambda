import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { RecentActivity } from '@/lib/mock-dashboard-data';
import { CheckCircle2, UserPlus, FolderPlus, PlayCircle } from 'lucide-react';

interface RecentActivitiesProps {
  activities: RecentActivity[];
}

export function RecentActivities({ activities }: RecentActivitiesProps) {
  const getActivityIcon = (type: RecentActivity['type']) => {
    switch (type) {
      case 'task_completed':
        return <CheckCircle2 className="h-4 w-4 text-green-600" />;
      case 'task_assigned':
        return <UserPlus className="h-4 w-4 text-blue-600" />;
      case 'project_created':
        return <FolderPlus className="h-4 w-4 text-purple-600" />;
      case 'sprint_started':
        return <PlayCircle className="h-4 w-4 text-orange-600" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-gray-600" />;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Son Aktiviteler</CardTitle>
        <CardDescription>Sistemdeki son hareketler</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <div key={index} className="flex gap-3">
              <div className="mt-0.5">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium leading-none">
                  {activity.description}
                </p>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <span>{activity.timestamp}</span>
                  {activity.employee && (
                    <>
                      <span>•</span>
                      <span className="font-medium">{activity.employee}</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

