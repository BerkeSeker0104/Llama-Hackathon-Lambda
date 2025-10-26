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
        return <CheckCircle2 className="h-4 w-4 text-[#38FF5D]" />;
      case 'task_assigned':
        return <UserPlus className="h-4 w-4 text-[#00A8FF]" />;
      case 'project_created':
        return <FolderPlus className="h-4 w-4 text-[#8B5CF6]" />;
      case 'sprint_started':
        return <PlayCircle className="h-4 w-4 text-[#F59E0B]" />;
      default:
        return <CheckCircle2 className="h-4 w-4 text-white/60" />;
    }
  };

  return (
    <Card className="bg-black border-white/10">
      <CardHeader>
        <CardTitle className="text-white">Son Aktiviteler</CardTitle>
        <CardDescription className="text-white/60">Sistemdeki son hareketler</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {activities.map((activity, index) => (
            <div key={index} className="flex gap-3">
              <div className="mt-0.5">
                {getActivityIcon(activity.type)}
              </div>
              <div className="flex-1 space-y-1">
                <p className="text-sm font-medium leading-none text-white">
                  {activity.description}
                </p>
                <div className="flex items-center gap-2 text-xs text-white/60">
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

