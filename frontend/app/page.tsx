'use client';

import { MetricCard } from '@/components/dashboard/MetricCard';
import { EmployeePerformanceChart } from '@/components/dashboard/EmployeePerformanceChart';
import { TaskTrendChart } from '@/components/dashboard/TaskTrendChart';
import { ProjectProgressList } from '@/components/dashboard/ProjectProgressList';
import { RecentActivities } from '@/components/dashboard/RecentActivities';
import { getMockDashboardData } from '@/lib/mock-dashboard-data';
import { CheckCircle2, ListTodo, Users, Briefcase } from 'lucide-react';

export default function Home() {
  const dashboardData = getMockDashboardData();

  return (
    <div className="min-h-screen bg-linear-to-b from-background to-muted">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-2">Tella Dashboard</h1>
          <p className="text-muted-foreground">
            Proje yönetimi ve ekip performansı özeti
          </p>
        </div>

        {/* Metrics Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Toplam Görev"
            value={dashboardData.metrics.totalTasks}
            icon={ListTodo}
            description="Sistemdeki tüm görevler"
          />
          <MetricCard
            title="Tamamlanan Görev"
            value={dashboardData.metrics.completedTasks}
            icon={CheckCircle2}
            description={`${Math.round((dashboardData.metrics.completedTasks / dashboardData.metrics.totalTasks) * 100)}% tamamlanma oranı`}
          />
          <MetricCard
            title="Aktif Çalışan"
            value={dashboardData.metrics.activeEmployees}
            icon={Users}
            description="Görev üzerinde çalışan"
          />
          <MetricCard
            title="Toplam Proje"
            value={dashboardData.metrics.totalProjects}
            icon={Briefcase}
            description="Aktif projeler"
          />
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <EmployeePerformanceChart data={dashboardData.employeePerformance} />
          <TaskTrendChart data={dashboardData.taskTrend} />
        </div>

        {/* Bottom Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ProjectProgressList projects={dashboardData.projectProgress} />
          <RecentActivities activities={dashboardData.recentActivities} />
        </div>
      </div>
    </div>
  );
}
