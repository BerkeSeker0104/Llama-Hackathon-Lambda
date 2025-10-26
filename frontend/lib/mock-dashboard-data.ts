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

export interface Notification {
  id: string;
  type: 'task_assigned' | 'task_completed' | 'task_due_soon' | 'project_update' | 'sprint_reminder' | 'comment';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  priority: 'low' | 'medium' | 'high';
  link?: string;
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

// Mock notifications data
export const getMockNotifications = (): Notification[] => {
  return [
    {
      id: '1',
      type: 'task_assigned',
      title: 'Yeni Görev Atandı',
      message: 'API dokümantasyonu görevi size atandı',
      timestamp: '5 dakika önce',
      read: false,
      priority: 'high',
      link: '/projects/1/tasks',
    },
    {
      id: '2',
      type: 'task_due_soon',
      title: 'Yaklaşan Görev',
      message: 'Database migration görevi 2 saat içinde sona eriyor',
      timestamp: '1 saat önce',
      read: false,
      priority: 'high',
      link: '/projects/1/tasks',
    },
    {
      id: '3',
      type: 'task_completed',
      title: 'Görev Tamamlandı',
      message: 'Ayşe Demir kullanıcı profil sayfası görevini tamamladı',
      timestamp: '2 saat önce',
      read: false,
      priority: 'medium',
      link: '/projects/1/tasks',
    },
    {
      id: '4',
      type: 'project_update',
      title: 'Proje Güncellemesi',
      message: 'E-Ticaret Platformu projesi %75 tamamlandı',
      timestamp: '3 saat önce',
      read: true,
      priority: 'medium',
      link: '/projects/1',
    },
    {
      id: '5',
      type: 'sprint_reminder',
      title: 'Sprint Hatırlatıcı',
      message: 'Sprint 3 yarın başlıyor. Görevlerinizi kontrol edin',
      timestamp: '5 saat önce',
      read: true,
      priority: 'low',
      link: '/projects/1/sprints',
    },
    {
      id: '6',
      type: 'comment',
      title: 'Yeni Yorum',
      message: 'Mehmet Kaya, kod review işleminize yorum ekledi',
      timestamp: '6 saat önce',
      read: true,
      priority: 'low',
      link: '/projects/1/tasks',
    },
    {
      id: '7',
      type: 'task_assigned',
      title: 'Yeni Görev Atandı',
      message: 'UI komponenti refactor görevi size atandı',
      timestamp: '1 gün önce',
      read: true,
      priority: 'medium',
      link: '/projects/2/tasks',
    },
    {
      id: '8',
      type: 'project_update',
      title: 'Risk Uyarısı',
      message: 'Mobil Uygulama Geliştirme projesi risk altında',
      timestamp: '2 gün önce',
      read: true,
      priority: 'high',
      link: '/projects/3',
    },
  ];
};

export const getUnreadNotificationCount = (notifications: Notification[]): number => {
  return notifications.filter(n => !n.read).length;
};

