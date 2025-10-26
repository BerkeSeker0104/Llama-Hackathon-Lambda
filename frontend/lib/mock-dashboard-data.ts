export interface DashboardMetrics {
  totalTasks: number;
  completedTasks: number;
  activeEmployees: number;
  totalProjects: number;
}

export interface EmployeePerformance {
  name: string;
  completedTasks: number;
  activeTasks: number;
}

export interface TaskTrend {
  date: string;
  completed: number;
  created: number;
}

export interface ProjectProgress {
  name: string;
  progress: number;
  status: 'on-track' | 'at-risk' | 'delayed';
  dueDate: string;
  department: string;
}

export interface RecentActivity {
  type: 'task_completed' | 'task_assigned' | 'project_created' | 'sprint_started';
  description: string;
  timestamp: string;
  employee?: string;
}

export interface DashboardData {
  metrics: DashboardMetrics;
  employeePerformance: EmployeePerformance[];
  taskTrend: TaskTrend[];
  projectProgress: ProjectProgress[];
  recentActivities: RecentActivity[];
}

// Mock data generator
export const getMockDashboardData = (): DashboardData => {
  // Generate dates for the last 7 days
  const last7Days = Array.from({ length: 7 }, (_, i) => {
    const date = new Date();
    date.setDate(date.getDate() - (6 - i));
    return date.toLocaleDateString('tr-TR', { month: 'short', day: 'numeric' });
  });

  return {
    metrics: {
      totalTasks: 156,
      completedTasks: 89,
      activeEmployees: 24,
      totalProjects: 8,
    },
    employeePerformance: [
      { name: 'Ahmet Yılmaz', completedTasks: 12, activeTasks: 3 },
      { name: 'Ayşe Demir', completedTasks: 15, activeTasks: 2 },
      { name: 'Mehmet Kaya', completedTasks: 9, activeTasks: 4 },
      { name: 'Zeynep Aksoy', completedTasks: 11, activeTasks: 2 },
      { name: 'Can Özdemir', completedTasks: 8, activeTasks: 3 },
      { name: 'Elif Çelik', completedTasks: 13, activeTasks: 1 },
      { name: 'Burak Şahin', completedTasks: 7, activeTasks: 5 },
      { name: 'Selin Yurt', completedTasks: 14, activeTasks: 2 },
    ],
    taskTrend: [
      { date: last7Days[0], completed: 8, created: 12 },
      { date: last7Days[1], completed: 12, created: 10 },
      { date: last7Days[2], completed: 15, created: 8 },
      { date: last7Days[3], completed: 10, created: 15 },
      { date: last7Days[4], completed: 13, created: 11 },
      { date: last7Days[5], completed: 16, created: 9 },
      { date: last7Days[6], completed: 15, created: 14 },
    ],
    projectProgress: [
      {
        name: 'E-Ticaret Platformu',
        progress: 75,
        status: 'on-track',
        dueDate: '15 Kas',
        department: 'Frontend',
      },
      {
        name: 'Mobil Uygulama Geliştirme',
        progress: 45,
        status: 'at-risk',
        dueDate: '20 Kas',
        department: 'Mobile',
      },
      {
        name: 'CRM Sistemi Entegrasyonu',
        progress: 90,
        status: 'on-track',
        dueDate: '10 Kas',
        department: 'Backend',
      },
      {
        name: 'Veri Analiz Dashboard',
        progress: 30,
        status: 'delayed',
        dueDate: '25 Kas',
        department: 'Data Science',
      },
      {
        name: 'API Gateway Güncelleme',
        progress: 65,
        status: 'on-track',
        dueDate: '18 Kas',
        department: 'DevOps',
      },
    ],
    recentActivities: [
      {
        type: 'task_completed',
        description: 'Kullanıcı profil sayfası tamamlandı',
        timestamp: '5 dakika önce',
        employee: 'Ayşe Demir',
      },
      {
        type: 'task_assigned',
        description: 'API dokümantasyonu görevi atandı',
        timestamp: '15 dakika önce',
        employee: 'Mehmet Kaya',
      },
      {
        type: 'sprint_started',
        description: 'Sprint 3 başlatıldı',
        timestamp: '2 saat önce',
      },
      {
        type: 'task_completed',
        description: 'Database migration tamamlandı',
        timestamp: '3 saat önce',
        employee: 'Can Özdemir',
      },
      {
        type: 'project_created',
        description: 'Yeni proje oluşturuldu: Payment Gateway',
        timestamp: '5 saat önce',
      },
      {
        type: 'task_completed',
        description: 'UI komponenti refactor edildi',
        timestamp: '6 saat önce',
        employee: 'Elif Çelik',
      },
    ],
  };
};

