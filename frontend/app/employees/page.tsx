'use client';

import { useQuery } from '@tanstack/react-query';
import { employeesApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import Image from 'next/image';
import { Users, Briefcase } from 'lucide-react';

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
      <div className="space-y-6">
        <h1 className="text-3xl font-bold text-white mb-6">Çalışanlar</h1>
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-white/10 rounded w-3/4 mb-2"></div>
                <div className="h-4 bg-white/10 rounded w-1/2"></div>
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
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white mb-6">Çalışanlar</h1>

      {!employees || employees.length === 0 ? (
        <Card className="p-12 text-center">
          <Users className="mx-auto h-12 w-12 text-white/60 mb-4" />
          <h3 className="text-lg font-semibold mb-2 text-white">Henüz çalışan yok</h3>
          <p className="text-white/60">
            Çalışan verileri burada görünecek
          </p>
        </Card>
      ) : (
        <>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {departments.map((dept: string) => (
              <Button key={dept} asChild variant="outline" className="h-auto py-4 border-white/10 hover:border-[#38FF5D]/50 text-white">
                <Link href={`/employees/${dept}`}>
                  <div className="text-center w-full">
                    <Briefcase className="mx-auto h-6 w-6 mb-2" />
                    <p className="font-semibold">{dept}</p>
                    <p className="text-sm text-white/60">
                      {employees.filter((e: any) => e.department === dept).length} üye
                    </p>
                  </div>
                </Link>
              </Button>
            ))}
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {employees.map((employee: any) => (
              <Card key={employee.employee_id} className="hover:border-[#38FF5D]/50 transition-all">
                <CardHeader>
                  <div className="flex items-center space-x-4">
                    <div className="relative">
                      <Image
                        src={getProfileImage(employee.name)}
                        alt={employee.name}
                        width={60}
                        height={60}
                        className="rounded-full object-cover border-2 border-[#38FF5D]/30"
                      />
                    </div>
                    <div>
                      <CardTitle className="text-white">{employee.name}</CardTitle>
                      <CardDescription className="text-white/60">
                        {employee.department} • {employee.seniority}
                      </CardDescription>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  {employee.tech_stack && (
                    <div>
                      <h4 className="text-sm font-semibold mb-2 text-white">Yetenekler</h4>
                      <div className="flex flex-wrap gap-2">
                        {employee.tech_stack.slice(0, 5).map((tech: string) => (
                          <span
                            key={tech}
                            className="px-2 py-1 bg-[#38FF5D]/20 text-[#38FF5D] text-xs rounded"
                          >
                            {tech}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                  <div className="mt-4">
                    <div className="flex items-center justify-between text-sm mb-4">
                      <span className="text-white/60">İş Yükü</span>
                      <span
                        className={`font-semibold ${
                          employee.current_workload === 'high'
                            ? 'text-red-400'
                            : employee.current_workload === 'medium'
                            ? 'text-yellow-400'
                            : 'text-[#38FF5D]'
                        }`}
                      >
                        {employee.current_workload === 'high' ? 'Yüksek' : 
                         employee.current_workload === 'medium' ? 'Orta' : 'Düşük'}
                      </span>
                    </div>
                    
                    {/* İletişim butonları */}
                    <div className="flex gap-2">
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1 border-white/20 hover:border-red-500/50 hover:text-red-400 hover:bg-red-500/10 transition-all"
                        onClick={() => window.open(`mailto:${employee.email || 'test@example.com'}`, '_blank')}
                      >
                        <Image
                          src="/32px-Gmail_icon_(2020).svg.png"
                          alt="Gmail"
                          width={16}
                          height={16}
                          className="mr-2"
                        />
                        Gmail
                      </Button>
                      <Button 
                        size="sm" 
                        variant="outline" 
                        className="flex-1 border-white/20 hover:border-blue-500/50 hover:text-blue-400 hover:bg-blue-500/10 transition-all"
                        onClick={() => window.open(`https://teams.microsoft.com/l/chat/0/0?users=${employee.email || 'test@example.com'}`, '_blank')}
                      >
                        <Image
                          src="/32px-Microsoft_Office_Teams_(2018–present).svg.png"
                          alt="Teams"
                          width={16}
                          height={16}
                          className="mr-2"
                        />
                        Teams
                      </Button>
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
