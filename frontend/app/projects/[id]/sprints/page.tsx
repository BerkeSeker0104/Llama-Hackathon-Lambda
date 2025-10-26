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
  Settings,
  ExternalLink,
} from 'lucide-react';
import Image from 'next/image';

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
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" size="icon" asChild className="text-white hover:bg-white/10">
          <Link href={`/projects/${projectId}`}>
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <h1 className="text-3xl font-bold text-white">Sprint Yönetimi</h1>
      </div>

      {/* Actions */}
      <div className="flex gap-4 mb-6">
        <Button
          onClick={() => generateSprintMutation.mutate()}
          disabled={generateSprintMutation.isPending}
          className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90"
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
          className="border-white/10 text-white hover:bg-white/5"
        >
          <RefreshCw className={`mr-2 h-4 w-4 ${isRefreshing ? 'animate-spin' : ''}`} />
          {isRefreshing ? 'Yenileniyor...' : 'Analizi Yenile'}
        </Button>
      </div>

      {sprintsLoading ? (
        <div className="animate-pulse space-y-4">
          <div className="h-32 bg-white/10 rounded"></div>
          <div className="h-64 bg-white/10 rounded"></div>
        </div>
      ) : generateSprintMutation.isPending ? (
        <Card className="p-12 text-center bg-black border-white/10">
          <div className="flex flex-col items-center gap-4">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-[#38FF5D]"></div>
            <h3 className="text-lg font-semibold text-white">Sprint Planı Oluşturuluyor...</h3>
            <p className="text-sm text-white/60">
              AI görevleri analiz ediyor ve sprint&apos;lere dağıtıyor
            </p>
          </div>
        </Card>
      ) : sprints.length === 0 ? (
        <Card className="p-12 text-center bg-black border-white/10">
          <h3 className="text-lg font-semibold mb-2 text-white">Sprint Planı Bulunamadı</h3>
          <p className="text-white/60 mb-4">
            Başlamak için bir sprint planı oluşturun
          </p>
          <Button 
            onClick={() => generateSprintMutation.mutate()}
            disabled={generateSprintMutation.isPending}
            className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90"
          >
            {generateSprintMutation.isPending ? 'Oluşturuluyor...' : 'Sprint Planı Oluştur'}
          </Button>
          {generateSprintMutation.isError && (
            <p className="text-red-400 text-sm mt-4">
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
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <div className="flex items-center justify-between">
                    <CardTitle className="flex items-center gap-2 text-white">
                      <Activity className="h-5 w-5" />
                      Sprint Sağlık Durumu
                    </CardTitle>
                    <div
                      className={`text-3xl font-bold ${
                        healthData.analysis.health_score >= 80
                          ? 'text-[#38FF5D]'
                          : healthData.analysis.health_score >= 60
                          ? 'text-yellow-400'
                          : healthData.analysis.health_score >= 40
                          ? 'text-orange-400'
                          : 'text-red-400'
                      }`}
                    >
                      {healthData.analysis.health_score}/100
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm font-medium text-white">Durum: </span>
                      <Badge
                        className={
                          healthData.analysis.status === 'healthy'
                            ? 'bg-[#38FF5D]/20 text-[#38FF5D] border-[#38FF5D]/30'
                            : healthData.analysis.status === 'warning'
                            ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                            : 'bg-red-500/20 text-red-400 border-red-500/30'
                        }
                      >
                        {healthData.analysis.status}
                      </Badge>
                    </div>
                    <div>
                      <span className="text-sm font-medium text-white">Tamamlanma Oranı: </span>
                      <span className="text-lg font-semibold text-white">
                        {(healthData.analysis.completion_rate * 100).toFixed(0)}%
                      </span>
                    </div>
                    {healthData.analysis.predicted_outcome && (
                      <div className="bg-white/10 p-3 rounded-lg">
                        <p className="text-sm font-medium mb-1 text-white">Tahmin:</p>
                        <p className="text-sm text-white/60">
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
              <Card className="bg-black border-white/10">
                <CardContent className="py-12 text-center">
                  <div className="animate-pulse text-white/60">Takvim yükleniyor...</div>
                </CardContent>
              </Card>
            )}
            {calendarError && (
              <Card className="border-red-500/30 bg-red-500/10">
                <CardContent className="py-6">
                  <p className="text-red-400 font-medium">❌ Takvim yüklenirken hata oluştu</p>
                  <p className="text-sm text-red-300 mt-2">
                    {calendarError instanceof Error ? calendarError.message : 'Bilinmeyen hata'}
                  </p>
                  <p className="text-xs text-red-400 mt-2">Backend konsolunu kontrol edin</p>
                </CardContent>
              </Card>
            )}
            {calendarData && !calendarError && <SprintCalendar events={calendarData.events} />}
          </div>

          {/* Sidebar - Risk Indicators */}
          <div className="space-y-6">
            {/* Risk Factors */}
            {riskData?.analysis && (
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <AlertTriangle className="h-5 w-5 text-orange-400" />
                    Proje Riskleri
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <span className="text-sm font-medium text-white">Risk Seviyesi: </span>
                      <Badge
                        className={
                          riskData.analysis.overall_delay_risk === 'critical'
                            ? 'bg-red-500/20 text-red-400 border-red-500/30'
                            : riskData.analysis.overall_delay_risk === 'high'
                            ? 'bg-orange-500/20 text-orange-400 border-orange-500/30'
                            : riskData.analysis.overall_delay_risk === 'medium'
                            ? 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30'
                            : 'bg-[#38FF5D]/20 text-[#38FF5D] border-[#38FF5D]/30'
                        }
                      >
                        {riskData.analysis.overall_delay_risk}
                      </Badge>
                    </div>
                    {riskData.analysis.estimated_delay_days > 0 && (
                      <div className="bg-red-500/10 border border-red-500/30 p-3 rounded-lg">
                        <p className="text-sm font-medium text-red-400">
                          Tahmini Gecikme: {riskData.analysis.estimated_delay_days} gün
                        </p>
                      </div>
                    )}
                    <div>
                      <h4 className="text-sm font-medium mb-2 text-white">Risk Faktörleri:</h4>
                      <div className="space-y-2">
                        {riskData.analysis.risk_factors.map((risk: { type: string; severity: string; description: string; impact_score: number }, i: number) => (
                          <div
                            key={i}
                            className={`border p-2 rounded-lg ${
                              risk.severity === 'critical'
                                ? 'bg-red-500/10 border-red-500/30'
                                : risk.severity === 'high'
                                ? 'bg-orange-500/10 border-orange-500/30'
                                : risk.severity === 'medium'
                                ? 'bg-yellow-500/10 border-yellow-500/30'
                                : 'bg-[#38FF5D]/10 border-[#38FF5D]/30'
                            }`}
                          >
                            <p className="text-sm font-medium text-white">{risk.description}</p>
                            <div className="flex items-center gap-2 mt-1">
                              <span className="text-xs text-white/60">
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

            {/* Google Calendar Integration */}
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Image 
                    src="/Google_Calendar_icon_(2015-2020).svg" 
                    alt="Google Calendar" 
                    width={24} 
                    height={24}
                    className="w-6 h-6"
                  />
                  Google Calendar Entegrasyonu
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-white/60">Durum:</span>
                    <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      Beklemede
                    </Badge>
                  </div>
                  <p className="text-sm text-white/60">
                    Sprint etkinliklerini Google Calendar ile senkronize edin
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full border-[#38FF5D]/30 text-[#38FF5D] hover:bg-[#38FF5D]/10"
                    onClick={() => {
                      // Mock function - will be implemented later
                      alert('Görevler Google Calendar\'a gönderiliyor... (Mock)');
                    }}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Görevleri Gönder
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Jira Integration */}
            <Card className="bg-black border-white/10">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-white">
                  <Image 
                    src="/jira.png" 
                    alt="Jira" 
                    width={32} 
                    height={32}
                    className="w-8 h-8"
                  />
                  Jira Entegrasyonu
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-white/60">Durum:</span>
                    <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                      Beklemede
                    </Badge>
                  </div>
                  <p className="text-sm text-white/60">
                    Görevleri Jira ile senkronize edin ve takip edin
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full border-[#38FF5D]/30 text-[#38FF5D] hover:bg-[#38FF5D]/10"
                    onClick={() => {
                      // Mock function - will be implemented later
                      alert('Görevler Jira\'ya gönderiliyor... (Mock)');
                    }}
                  >
                    <ExternalLink className="w-4 h-4 mr-2" />
                    Görevleri Gönder
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Recommendations */}
            {(healthData?.analysis?.recommendations ||
              riskData?.analysis?.recommendations) && (
              <Card className="bg-black border-white/10">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2 text-white">
                    <TrendingUp className="h-5 w-5 text-[#38FF5D]" />
                    Öneriler
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2">
                    {(healthData?.analysis?.recommendations || [])
                      .concat(riskData?.analysis?.recommendations || [])
                      .map((rec: string, i: number) => (
                        <li key={i} className="text-sm flex items-start gap-2 text-white/80">
                          <span className="text-[#38FF5D] mt-0.5">•</span>
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

