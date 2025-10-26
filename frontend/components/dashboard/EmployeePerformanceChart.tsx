'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EmployeePerformance } from '@/lib/mock-dashboard-data';

interface EmployeePerformanceChartProps {
  data: EmployeePerformance[];
}

export function EmployeePerformanceChart({ data }: EmployeePerformanceChartProps) {
  return (
    <Card className="bg-black border-white/10">
      <CardHeader>
        <CardTitle className="text-white">Çalışan Performansı</CardTitle>
        <CardDescription className="text-white/60">Çalışanların tamamladığı ve aktif görevleri</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12, fill: '#ffffff60' }}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis tick={{ fill: '#ffffff60' }} />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a1a1a', 
                border: '1px solid #ffffff1a',
                borderRadius: '8px',
                color: '#ffffff'
              }} 
            />
            <Legend />
            <Bar dataKey="completedTasks" fill="#38FF5D" name="Tamamlanan Görevler" />
            <Bar dataKey="activeTasks" fill="#00A8FF" name="Aktif Görevler" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

