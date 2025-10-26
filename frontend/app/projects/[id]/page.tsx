'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { projectsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Link from 'next/link';
import { ArrowLeft, AlertTriangle, CheckCircle } from 'lucide-react';

export default function ProjectDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  
  const { data: project, isLoading } = useQuery({
    queryKey: ['project', id],
    queryFn: async () => {
      const response = await projectsApi.get(id);
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse">
          <div className="h-8 bg-muted rounded w-1/4 mb-6"></div>
          <div className="h-64 bg-muted rounded"></div>
        </div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="container mx-auto px-4 py-8">
        <Card className="p-12 text-center">
          <h3 className="text-lg font-semibold mb-2">Proje bulunamadı</h3>
          <Button asChild>
            <Link href="/projects">Projelere Dön</Link>
          </Button>
        </Card>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/projects">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold">{project.project_name || 'Proje Detayları'}</h1>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="analysis">Analiz</TabsTrigger>
          <TabsTrigger value="criteria">Kabul Kriterleri</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Proje Bilgileri</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <h3 className="font-semibold mb-2">Açıklama</h3>
                <p className="text-muted-foreground">{project.detailedDescription}</p>
              </div>
              <div>
                <h3 className="font-semibold mb-2">Departman</h3>
                <span className="px-3 py-1 bg-primary/10 text-primary rounded">
                  {project.department}
                </span>
              </div>
              {project.tech_stack && (
                <div>
                  <h3 className="font-semibold mb-2">Teknoloji Yığını</h3>
                  <div className="flex flex-wrap gap-2">
                    {project.tech_stack.map((tech: string) => (
                      <span key={tech} className="px-3 py-1 bg-secondary text-secondary-foreground rounded">
                        {tech}
                      </span>
                    ))}
                  </div>
                </div>
              )}
              <div>
                <h3 className="font-semibold mb-2">Zaman Çizelgesi</h3>
                <p className="text-muted-foreground">{project.estimated_duration || 'Belirtilmedi'}</p>
              </div>
            </CardContent>
          </Card>

          <div className="grid grid-cols-2 gap-4">
            <Button asChild>
              <Link href={`/projects/${id}/tasks`}>Görevleri Görüntüle</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href={`/projects/${id}/sprints`}>Sprint Yönetimi</Link>
            </Button>
          </div>
        </TabsContent>

        <TabsContent value="analysis" className="space-y-6">
          {project.critical_analysis && (
            <>
              {project.critical_analysis.risks && (
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-orange-500" />
                      Riskler
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {project.critical_analysis.risks.map((risk: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-orange-500">•</span>
                          <span>{risk}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {project.critical_analysis.missing_information && (
                <Card>
                  <CardHeader>
                    <CardTitle>Eksik Bilgiler</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {project.critical_analysis.missing_information.map((info: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-muted-foreground">•</span>
                          <span>{info}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}

              {project.critical_analysis.contradictions && (
                <Card>
                  <CardHeader>
                    <CardTitle>Çelişkiler</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <ul className="space-y-2">
                      {project.critical_analysis.contradictions.map((contradiction: string, i: number) => (
                        <li key={i} className="flex items-start gap-2">
                          <span className="text-red-500">•</span>
                          <span>{contradiction}</span>
                        </li>
                      ))}
                    </ul>
                  </CardContent>
                </Card>
              )}
            </>
          )}
        </TabsContent>

        <TabsContent value="criteria" className="space-y-6">
          {project.acceptance_criteria && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <CheckCircle className="h-5 w-5 text-green-500" />
                  Kabul Kriterleri
                </CardTitle>
              </CardHeader>
              <CardContent>
                <ul className="space-y-3">
                  {project.acceptance_criteria.map((criteria: string, i: number) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle className="h-5 w-5 text-green-500 mt-0.5" />
                      <span>{criteria}</span>
                    </li>
                  ))}
                </ul>
              </CardContent>
            </Card>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
