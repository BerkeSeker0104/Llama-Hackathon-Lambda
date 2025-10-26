import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  description?: string;
  trend?: {
    value: number;
    isPositive: boolean;
  };
}

export function MetricCard({ title, value, icon: Icon, description, trend }: MetricCardProps) {
  return (
    <Card className="bg-black border-white/10 hover:border-[#38FF5D]/50 transition-all">
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-white">{title}</CardTitle>
        <div className="w-10 h-10 bg-[#38FF5D]/20 rounded-lg flex items-center justify-center">
          <Icon className="h-5 w-5 text-[#38FF5D]" />
        </div>
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold text-white">{value}</div>
        {description && (
          <p className="text-xs text-white/60 mt-1">{description}</p>
        )}
        {trend && (
          <p className={`text-xs mt-1 ${trend.isPositive ? 'text-[#38FF5D]' : 'text-red-400'}`}>
            {trend.isPositive ? '+' : ''}{trend.value}% önceki aya göre
          </p>
        )}
      </CardContent>
    </Card>
  );
}

