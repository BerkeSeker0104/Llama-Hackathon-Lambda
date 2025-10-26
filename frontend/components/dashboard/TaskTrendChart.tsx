'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { TaskTrend } from '@/lib/mock-dashboard-data';

interface TaskTrendChartProps {
  data: TaskTrend[];
}

export function TaskTrendChart({ data }: TaskTrendChartProps) {
  return (
    <Card className="bg-black border-white/10">
      <CardHeader>
        <CardTitle className="text-white">Görev Trendi</CardTitle>
        <CardDescription className="text-white/60">Son 7 günlük görev oluşturma ve tamamlanma durumu</CardDescription>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#ffffff20" />
            <XAxis dataKey="date" tick={{ fill: '#ffffff60' }} />
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
            <Line 
              type="monotone" 
              dataKey="completed" 
              stroke="#38FF5D" 
              strokeWidth={2}
              name="Tamamlanan"
            />
            <Line 
              type="monotone" 
              dataKey="created" 
              stroke="#00A8FF" 
              strokeWidth={2}
              name="Oluşturulan"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}

