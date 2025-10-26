'use client';

import { use } from 'react';
import { useQuery } from '@tanstack/react-query';
import { employeesApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import Image from 'next/image';
import { ArrowLeft, Users } from 'lucide-react';

// Function to get profile image based on name
const getProfileImage = (name: string) => {
  // Complete mapping of all employee names to specific images
  const imageMapping: { [key: string]: string } = {
    // Male employees - each gets a unique erkek image
    'Ahmet Yılmaz': '/erkek/erkek1.png',
    'Mehmet Demir': '/erkek/erkek2.png',
    'Can Özdemir': '/erkek/erkek3.png',
    'Burak Çelik': '/erkek/erkek4.png',
    'Emre Aydın': '/erkek/erkek5.png',
    'Deniz Koç': '/erkek/erkek6.png',
    'Murat Erdoğan': '/erkek/erkek7.png',
    'Onur Polat': '/erkek/erkek8.png',
    
    // Female employees - each gets a unique kadın image
    'Zeynep Kaya': '/kadın/kadın1.png',
    'Ayşe Şahin': '/kadın/kadın2.png',
    'Elif Arslan': '/kadın/kadın3.png',
    'Selin Yıldız': '/kadın/kadın4.png',
    'Gizem Aksoy': '/kadın/kadın5.png',
    'Merve Yılmaz': '/kadın/kadın6.png',
  };
  
  // Return mapped image or default fallback
  return imageMapping[name] || '/erkek/erkek1.png';
};

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
                <div className="flex items-center space-x-4">
                  <div className="relative">
                    <Image
                      src={getProfileImage(employee.name)}
                      alt={employee.name}
                      width={50}
                      height={50}
                      className="rounded-full object-cover border-2 border-gray-200"
                    />
                  </div>
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
