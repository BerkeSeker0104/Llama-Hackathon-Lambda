'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TaskTrend } from '@/lib/mock-dashboard-data';

interface TaskTrendChartProps {
  data: TaskTrend[];
}

export function TaskTrendChart({ data }: TaskTrendChartProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Görev Trendi</CardTitle>
        <CardDescription>Son 7 günlük görev oluşturma ve tamamlanma durumu</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line 
              type="monotone" 
              dataKey="completed" 
              stroke="#10b981" 
              strokeWidth={2}
              name="Tamamlanan"
            />
            <Line 
              type="monotone" 
              dataKey="created" 
              stroke="#3b82f6" 
              strokeWidth={2}
              name="Oluşturulan"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

