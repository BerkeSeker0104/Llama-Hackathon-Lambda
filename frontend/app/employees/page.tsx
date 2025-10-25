'use client';

import { useQuery } from '@tanstack/react-query';
import { employeesApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { Users, Briefcase } from 'lucide-react';

export default function EmployeesPage() {
  const { data: employees, isLoading } = useQuery({
    queryKey: ['employees'],
    queryFn: async () => {
      const response = await employeesApi.list();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Çalışanlar</h1>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-muted rounded w-1/2"></div>
              </CardHeader>
            </Card>
          ))}
        </div>
      </div>
    );
  }

  const departments = employees
    ? [...new Set(employees.map((e: any) => e.department))]
    : [];

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">Çalışanlar</h1>

      {!employees || employees.length === 0 ? (
        <Card className="p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">Henüz çalışan yok</h3>
          <p className="text-muted-foreground">
            Çalışan verileri burada görünecek
          </p>
        </Card>
      ) : (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {departments.map((dept: string) => (
              <Button key={dept} asChild variant="outline" className="h-auto py-4">
                <Link href={`/employees/${dept}`}>
                  <div className="text-center w-full">
                    <Briefcase className="mx-auto h-6 w-6 mb-2" />
                    <p className="font-semibold">{dept}</p>
                    <p className="text-sm text-muted-foreground">
                      {employees.filter((e: any) => e.department === dept).length} üye
                    </p>
                  </div>
                </Link>
              </Button>
            ))}
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {employees.map((employee: any) => (
              <Card key={employee.employee_id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle>{employee.name}</CardTitle>
                  <CardDescription>
                    {employee.department} • {employee.seniority}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  {employee.tech_stack && (
                    <div>
                      <h4 className="text-sm font-semibold mb-2">Yetenekler</h4>
                      <div className="flex flex-wrap gap-2">
                        {employee.tech_stack.slice(0, 5).map((tech: string) => (
                          <span
                            key={tech}
                            className="px-2 py-1 bg-secondary text-secondary-foreground text-xs rounded"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-muted-foreground">İş Yükü</span>
                      <span
                        className={`font-semibold ${
                          employee.current_workload === 'high'
                            ? 'text-red-500'
                            : employee.current_workload === 'medium'
                            ? 'text-yellow-500'
                            : 'text-green-500'
                        }`}
                      >
                        {employee.current_workload === 'high' ? 'Yüksek' : 
                         employee.current_workload === 'medium' ? 'Orta' : 'Düşük'}
                      </span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </>
      )}
    </div>
  );
}
