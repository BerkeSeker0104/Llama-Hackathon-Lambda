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
        return 'bg-[#38FF5D]/20 text-[#38FF5D] border-[#38FF5D]/30';
      case 'at-risk':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
      case 'delayed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      default:
        return 'bg-white/10 text-white/60 border-white/20';
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
    <Card className="bg-black border-white/10">
      <CardHeader>
        <CardTitle className="text-white">Proje İlerlemeleri</CardTitle>
        <CardDescription className="text-white/60">Aktif projelerin tamamlanma durumu</CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {projects.map((project, index) => (
          <div key={index} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="flex-1">
                <h4 className="text-sm font-semibold text-white">{project.name}</h4>
                <p className="text-xs text-white/60">{project.department}</p>
              </div>
              <Badge className={getStatusColor(project.status)} variant="outline">
                {getStatusText(project.status)}
              </Badge>
            </div>
            <div className="flex items-center gap-2">
              <Progress value={project.progress} className="flex-1" />
              <span className="text-sm font-medium w-12 text-right text-white">{project.progress}%</span>
            </div>
            <div className="flex items-center gap-1 text-xs text-white/60">
              <Calendar className="h-3 w-3" />
              <span>Bitiş: {project.dueDate}</span>
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}

