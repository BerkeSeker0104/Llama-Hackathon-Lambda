import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { ProjectProgress } from '@/lib/mock-dashboard-data';
import { Badge } from '@/components/ui/badge';
import { Calendar } from 'lucide-react';

interface ProjectProgressListProps {
  projects: ProjectProgress[];
}

export function ProjectProgressList({ projects }: ProjectProgressListProps) {
  const getStatusColor = (status: ProjectProgress['status']) => {
    switch (status) {
      case 'on-track':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'at-risk':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'delayed':
        return 'bg-red-100 text-red-800 border-red-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getStatusText = (status: ProjectProgress['status']) => {
    switch (status) {
      case 'on-track':
        return 'Yolunda';
      case 'at-risk':
        return 'Risk Altında';
      case 'delayed':
        return 'Gecikmiş';
      default:
        return status;
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>Proje İlerlemeleri</CardTitle>
        <CardDescription>Aktif projelerin tamamlanma durumu</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {projects.map((project, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h4 className="text-sm font-semibold">{project.name}</h4>
                <p className="text-xs text-muted-foreground">{project.department}</p>
              </div>
              <Badge className={getStatusColor(project.status)} variant="outline">
                {getStatusText(project.status)}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Progress value={project.progress} className="flex-1" />
              <span className="text-sm font-medium w-12 text-right">{project.progress}%</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-muted-foreground">
              <Calendar className="h-3 w-3" />
              <span>Bitiş: {project.dueDate}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

