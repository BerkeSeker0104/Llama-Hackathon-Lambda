'use client';

import { use, useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dynamicSprintApi, sprintsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SprintCalendar } from '@/components/SprintCalendar';
import Link from 'next/link';
import {
  ArrowLeft,
  AlertTriangle,
  Activity,
  TrendingUp,
  Calendar,
  RefreshCw,
} from 'lucide-react';

export default function SprintDashboardPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id: projectId } = use(params);
  const [selectedSprintId, setSelectedSprintId] = useState<string | null>(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const queryClient = useQueryClient();

  // Fetch sprints for the project
  const { data: sprintsData, isLoading: sprintsLoading } = useQuery({
    queryKey: ['sprints', projectId],
    queryFn: async () => {
      const response = await sprintsApi.list(projectId);
      return response.data;
    },
  });

  // Fetch calendar events for the selected sprint
  const { data: calendarData, isLoading: calendarLoading, error: calendarError, refetch: refetchCalendar } = useQuery({
    queryKey: ['calendar-events', selectedSprintId],
    queryFn: async () => {
      if (!selectedSprintId) return null;
      const response = await sprintsApi.getCalendarEvents(selectedSprintId);
      return response.data;
    },
    enabled: !!selectedSprintId,
    retry: 1,
  });

  // Fetch sprint health analysis
  const { data: healthData, refetch: refetchHealth } = useQuery({
    queryKey: ['sprint-health', selectedSprintId],
    queryFn: async () => {
      if (!selectedSprintId) return null;
      const response = await sprintsApi.getHealth(selectedSprintId, projectId);
      return response.data;
    },
    enabled: !!selectedSprintId,
  });

  // Fetch project risk analysis
  const { data: riskData, refetch: refetchRisk } = useQuery({
    queryKey: ['project-risk', projectId],
    queryFn: async () => {
      const response = await dynamicSprintApi.getRiskAnalysis(projectId);
      return response.data;
    },
  });

  // Generate sprint plan mutation
  const generateSprintMutation = useMutation({
    mutationFn: () => sprintsApi.generate(projectId, 2),
    onSuccess: (response) => {
      queryClient.invalidateQueries({ queryKey: ['sprints', projectId] });
      queryClient.invalidateQueries({ queryKey: ['calendar-events'] });
      queryClient.invalidateQueries({ queryKey: ['sprint-health'] });
      // Select the newly created sprint
      if (response.data?.sprint_id) {
        setSelectedSprintId(response.data.sprint_id);
      }
    },
  });

  // Select the first sprint by default
  const sprints = sprintsData?.sprints || [];
  
  // Use useEffect to set the initial sprint selection
  useEffect(() => {
    if (!selectedSprintId && sprints.length > 0) {
      setSelectedSprintId(sprints[0].sprint_id);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sprintsData]);

  // Get health score color
  const getHealthColor = (score?: number) => {
    if (!score) return 'text-gray-500';
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    if (score >= 40) return 'text-orange-600';
    return 'text-red-600';
  };

  // Get risk severity color
  const getRiskColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'high':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'low':
        return 'bg-green-100 text-green-800 border-green-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild>
          <Link href={`/projects/${projectId}`}>
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold">Sprint Yönetimi</h1>
      </div>

      {/* Actions */}
      <div className="flex gap-4 mb-6">
        <Button
          onClick={() => generateSprintMutation.mutate()}
          disabled={generateSprintMutation.isPending}
        >
          <Calendar className="mr-2 h-4 w-4" />
          {generateSprintMutation.isPending ? 'Oluşturuluyor...' : 'Sprint Planı Oluştur'}
        </Button>
        <Button
          variant="outline"
          disabled={isRefreshing}
          onClick={async () => {
            setIsRefreshing(true);
            try {
              // Cache'i temizle ve yeniden yükle
              await Promise.all([
                refetchHealth(),
                refetchCalendar(),
                refetchRisk(),
              ]);
            } finally {
              setIsRefreshing(false);
            }
          }}
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Yenileniyor...' : 'Analizi Yenile'}
        </Button>
      </div>

      {sprintsLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-muted rounded"></div>
          <div className="h-64 bg-muted rounded"></div>
        </div>
      ) : generateSprintMutation.isPending ? (
        <Card className="p-12 text-center">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
            <h3 className="text-lg font-semibold">Sprint Planı Oluşturuluyor...</h3>
            <p className="text-sm text-muted-foreground">
              AI görevleri analiz ediyor ve sprint&apos;lere dağıtıyor
            </p>
          </div>
        </Card>
      ) : sprints.length === 0 ? (
        <Card className="p-12 text-center">
          <h3 className="text-lg font-semibold mb-2">Sprint Planı Bulunamadı</h3>
          <p className="text-muted-foreground mb-4">
            Başlamak için bir sprint planı oluşturun
          </p>
          <Button 
            onClick={() => generateSprintMutation.mutate()}
            disabled={generateSprintMutation.isPending}
          >
            {generateSprintMutation.isPending ? 'Oluşturuluyor...' : 'Sprint Planı Oluştur'}
          </Button>
          {generateSprintMutation.isError && (
            <p className="text-red-600 text-sm mt-4">
              ❌ Hata: {generateSprintMutation.error instanceof Error ? generateSprintMutation.error.message : 'Bilinmeyen hata'}
            </p>
          )}
        </Card>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Content - Calendar */}
          <div className="lg:col-span-2 space-y-6">
            {/* Sprint Health Card */}
            {healthData?.analysis && (
              <Card>
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2">
                      <Activity className="h-5 w-5" />
                      Sprint Sağlık Durumu
                    </CardTitle>
                    <div
                      className={`text-3xl font-bold ${getHealthColor(
                        healthData.analysis.health_score
                      )}`}
                    >
                      {healthData.analysis.health_score}/100
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm font-medium">Durum: </span>
                      <Badge
                        className={
                          healthData.analysis.status === 'healthy'
                            ? 'bg-green-100 text-green-800'
                            : healthData.analysis.status === 'warning'
                            ? 'bg-yellow-100 text-yellow-800'
                            : 'bg-red-100 text-red-800'
                        }
                      >
                        {healthData.analysis.status}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-sm font-medium">Tamamlanma Oranı: </span>
                      <span className="text-lg font-semibold">
                        {(healthData.analysis.completion_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    {healthData.analysis.predicted_outcome && (
                      <div className="bg-muted p-3 rounded-lg">
                        <p className="text-sm font-medium mb-1">Tahmin:</p>
                        <p className="text-sm text-muted-foreground">
                          {healthData.analysis.predicted_outcome}
                        </p>
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Calendar */}
            {calendarLoading && (
              <Card>
                <CardContent className="py-12 text-center">
                  <div className="animate-pulse">Takvim yükleniyor...</div>
                </CardContent>
              </Card>
            )}
            {calendarError && (
              <Card className="border-red-300 bg-red-50">
                <CardContent className="py-6">
                  <p className="text-red-800 font-medium">❌ Takvim yüklenirken hata oluştu</p>
                  <p className="text-sm text-red-600 mt-2">
                    {calendarError instanceof Error ? calendarError.message : 'Bilinmeyen hata'}
                  </p>
                  <p className="text-xs text-red-500 mt-2">Backend konsolunu kontrol edin</p>
                </CardContent>
              </Card>
            )}
            {calendarData && !calendarError && <SprintCalendar events={calendarData.events} />}
          </div>

          {/* Sidebar - Risk Indicators */}
          <div className="space-y-6">
            {/* Risk Factors */}
            {riskData?.analysis && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <AlertTriangle className="h-5 w-5 text-orange-500" />
                    Proje Riskleri
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm font-medium">Risk Seviyesi: </span>
                      <Badge
                        className={getRiskColor(riskData.analysis.overall_delay_risk)}
                      >
                        {riskData.analysis.overall_delay_risk}
                      </Badge>
                    </div>
                    {riskData.analysis.estimated_delay_days > 0 && (
                      <div className="bg-red-50 border border-red-200 p-3 rounded-lg">
                        <p className="text-sm font-medium text-red-800">
                          Tahmini Gecikme: {riskData.analysis.estimated_delay_days} gün
                        </p>
                      </div>
                    )}
                    <div>
                      <h4 className="text-sm font-medium mb-2">Risk Faktörleri:</h4>
                      <div className="space-y-2">
                        {riskData.analysis.risk_factors.map((risk: { type: string; severity: string; description: string; impact_score: number }, i: number) => (
                          <div
                            key={i}
                            className={`border p-2 rounded-lg ${getRiskColor(
                              risk.severity
                            )}`}
                          >
                            <p className="text-sm font-medium">{risk.description}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge variant="outline" className="text-xs">
                                {risk.type}
                              </Badge>
                              <span className="text-xs">
                                Etki: {risk.impact_score}/10
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Recommendations */}
            {(healthData?.analysis?.recommendations ||
              riskData?.analysis?.recommendations) && (
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <TrendingUp className="h-5 w-5 text-blue-500" />
                    Öneriler
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {(healthData?.analysis?.recommendations || [])
                      .concat(riskData?.analysis?.recommendations || [])
                      .map((rec: string, i: number) => (
                        <li key={i} className="text-sm flex items-start gap-2">
                          <span className="text-blue-500 mt-0.5">•</span>
                          <span>{rec}</span>
                        </li>
                      ))}
                  </ul>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

