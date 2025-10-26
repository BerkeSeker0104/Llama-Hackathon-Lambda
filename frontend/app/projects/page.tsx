'use client';

import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Briefcase, Clock } from 'lucide-react';

export default function ProjectsPage() {
  const { data: projects, isLoading } = useQuery({
    queryKey: ['projects'],
    queryFn: async () => {
      const response = await projectsApi.list();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white mb-6">Projeler</h1>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-white/10 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-white/10 rounded w-1/2"></div>
              </CardHeader>
              <CardContent>
                <div className="h-20 bg-white/10 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold text-white">Projeler</h1>
        <Button asChild className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
          <Link href="/contracts/new">Yeni Proje</Link>
        </Button>
      </div>

      {!projects || projects.length === 0 ? (
        <Card className="p-12 text-center">
          <Briefcase className="mx-auto h-12 w-12 text-white/60 mb-4" />
          <h3 className="text-lg font-semibold mb-2 text-white">Henüz proje yok</h3>
          <p className="text-white/60 mb-4">
            İlk projenizi oluşturmak için bir sözleşme yükleyin
          </p>
          <Button asChild className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
            <Link href="/contracts/new">Sözleşme Yükle</Link>
          </Button>
        </Card>
      ) : (
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project: any) => (
            <Card key={project.project_id} className="hover:border-[#38FF5D]/50 transition-all">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Briefcase className="h-5 w-5" />
                  {project.project_name || 'İsimsiz Proje'}
                </CardTitle>
                <CardDescription className="text-white/60">
                  {project.department || 'Departman yok'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-white/60 line-clamp-3 mb-4">
                  {project.detailedDescription || 'Açıklama yok'}
                </p>
                {project.tech_stack && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {project.tech_stack.slice(0, 3).map((tech: string) => (
                      <span
                        key={tech}
                        className="px-2 py-1 bg-[#38FF5D]/20 text-[#38FF5D] text-xs rounded"
                      >
                        {tech}
                      </span>
                    ))}
                  </div>
                )}
                <div className="flex items-center gap-2 text-sm text-white/60 mb-4">
                  <Clock className="h-4 w-4" />
                  {project.estimated_duration || 'Süre belirlenmedi'}
                </div>
                <Button asChild className="w-full bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
                  <Link href={`/projects/${project.project_id}`}>Detayları Gör</Link>
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}

