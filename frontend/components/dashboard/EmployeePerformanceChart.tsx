'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { EmployeePerformance } from '@/lib/mock-dashboard-data';

interface EmployeePerformanceChartProps {
  data: EmployeePerformance[];
}

export function EmployeePerformanceChart({ data }: EmployeePerformanceChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Çalışan Performansı</CardTitle>
        <CardDescription>Çalışanların tamamladığı ve aktif görevleri</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis 
              dataKey="name" 
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={100}
            />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="completedTasks" fill="#10b981" name="Tamamlanan Görevler" />
            <Bar dataKey="activeTasks" fill="#3b82f6" name="Aktif Görevler" />
          </BarChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

