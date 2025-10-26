'use client';

import { use, useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { tasksApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft, CheckCircle, Clock, User } from 'lucide-react';

export default function TasksPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const queryClient = useQueryClient();
  const [assigningTaskId, setAssigningTaskId] = useState<string | null>(null);

  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks', id],
    queryFn: async () => {
      const response = await tasksApi.list(id);
      return response.data;
    },
  });

  const assignMutation = useMutation({
    mutationFn: (taskId: string) => tasksApi.assign(taskId),
    onSuccess: async (response) => {
      queryClient.invalidateQueries({ queryKey: ['tasks', id] });
      setAssigningTaskId(null);
      
      // Toast notification
      const { toast } = await import('@/hooks/use-toast');
      toast({
        title: "Görev başarıyla atandı!",
        description: response.data.assigned_to ? 
          `${response.data.assigned_to.name} görevine atandı.` : 
          "Görev atama tamamlandı.",
        variant: "success",
      });
    },
    onError: async (error: any) => {
      setAssigningTaskId(null);
      
      // Error toast
      const { toast } = await import('@/hooks/use-toast');
      toast({
        title: "Atama başarısız",
        description: error.response?.data?.detail || "Bir hata oluştu",
        variant: "destructive",
      });
    },
  });

  const handleAssign = (taskId: string) => {
    setAssigningTaskId(taskId);
    assignMutation.mutate(taskId);
  };

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <div className="animate-pulse space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-muted rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/projects/${id}`}>
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold">Görevler</h1>
      </div>

      {!tasks || tasks.length === 0 ? (
        <Card className="p-12 text-center">
          <Clock className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Henüz görev yok</h3>
          <p className="text-muted-foreground">
            Proje analizi sonrasında görevler burada görünecek
          </p>
        </Card>
      ) : (
        <div className="space-y-4">
          {tasks.map((task: any) => (
            <Card key={task.task_id} className="hover:shadow-md transition-shadow">
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <CardTitle className="mb-2">{task.title}</CardTitle>
                    <CardDescription>{task.detail}</CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    {task.status === 'assigned' ? (
                      <span className="flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
                        <CheckCircle className="h-4 w-4" />
                        Atandı
                      </span>
                    ) : (
                      <span className="flex items-center gap-1 px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                        <Clock className="h-4 w-4" />
                        Beklemede
                      </span>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {task.required_stack && (
                    <div>
                      <h4 className="text-sm font-semibold mb-2">Gerekli Teknolojiler</h4>
                      <div className="flex flex-wrap gap-2">
                        {task.required_stack.map((tech: string) => (
                          <span key={tech} className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded">
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {task.assigned_to && (
                    <div className="flex items-center gap-2 p-3 bg-muted rounded-lg">
                      <User className="h-5 w-5 text-muted-foreground" />
                      <div>
                        <p className="font-semibold">{task.assigned_to.name}</p>
                        <p className="text-sm text-muted-foreground">
                          {task.assigned_to.department} • {task.assigned_to.seniority}
                        </p>
                        {task.assignment_reason && (
                          <p className="text-sm text-muted-foreground mt-1">
                            Sebep: {task.assignment_reason}
                          </p>
                        )}
                      </div>
                    </div>
                  )}

                  {task.status !== 'assigned' && (
                    <Button
                      onClick={() => handleAssign(task.task_id)}
                      disabled={assigningTaskId === task.task_id}
                      className="w-full"
                    >
                      {assigningTaskId === task.task_id ? 'Atanıyor...' : 'Otomatik Ata'}
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
