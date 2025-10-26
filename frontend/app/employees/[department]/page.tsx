'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { employeesApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { ArrowLeft, Users } from 'lucide-react';

export default function DepartmentWorkloadPage({ params }: { params: Promise<{ department: string }> }) {
  const { department } = use(params);
  
  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees', department],
    queryFn: async () => {
      const response = await employeesApi.getByDepartment(department);
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

  const workloadCounts = employees
    ? employees.reduce(
        (acc: any, emp: any) => {
          const level = emp.current_workload || 'low';
          acc[level] = (acc[level] || 0) + 1;
          return acc;
        },
        { low: 0, medium: 0, high: 0 }
      )
    : { low: 0, medium: 0, high: 0 };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild>
          <Link href="/employees">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold">{department} Departmanı</h1>
      </div>

      <div className="grid md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-green-600">Düşük İş Yükü</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{workloadCounts.low}</p>
            <p className="text-sm text-muted-foreground">çalışan</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-yellow-600">Orta İş Yükü</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{workloadCounts.medium}</p>
            <p className="text-sm text-muted-foreground">çalışan</p>
          </CardContent>
        </Card>
        <Card>
          <CardHeader>
            <CardTitle className="text-red-600">Yüksek İş Yükü</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-4xl font-bold">{workloadCounts.high}</p>
            <p className="text-sm text-muted-foreground">çalışan</p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Takım Üyeleri
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {employees?.map((employee: any) => (
              <div
                key={employee.employee_id}
                className="flex items-center justify-between p-4 border rounded-lg"
              >
                <div>
                  <p className="font-semibold">{employee.name}</p>
                  <p className="text-sm text-muted-foreground">{employee.seniority}</p>
                  {employee.tech_stack && (
                    <div className="flex flex-wrap gap-1 mt-2">
                      {employee.tech_stack.slice(0, 3).map((tech: string) => (
                        <span
                          key={tech}
                          className="px-2 py-0.5 bg-secondary text-secondary-foreground text-xs rounded"
                        >
                          {tech}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
                <div>
                  <span
                    className={`px-3 py-1 rounded-full text-sm font-semibold ${
                      employee.current_workload === 'high'
                        ? 'bg-red-100 text-red-700'
                        : employee.current_workload === 'medium'
                        ? 'bg-yellow-100 text-yellow-700'
                        : 'bg-green-100 text-green-700'
                    }`}
                  >
                    {employee.current_workload === 'high' ? 'Yüksek' : 
                     employee.current_workload === 'medium' ? 'Orta' : 'Düşük'}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
