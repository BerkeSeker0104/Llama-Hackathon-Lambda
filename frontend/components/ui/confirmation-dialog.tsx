'use client';

import { useState } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { CheckCircle, XCircle, AlertTriangle, User, Clock, Shield } from 'lucide-react';

interface ConfirmationDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  onReject: () => void;
  data: {
    type: string;
    title: string;
    details: any;
  };
  loading?: boolean;
}

export function ConfirmationDialog({
  isOpen,
  onClose,
  onConfirm,
  onReject,
  data,
  loading = false
}: ConfirmationDialogProps) {
  if (!isOpen) return null;

  const renderTaskAssignment = () => {
    const { details } = data;
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <User className="h-5 w-5 text-[#38FF5D]" />
          <div>
            <h3 className="font-semibold text-white">Görev Ataması</h3>
            <p className="text-sm text-white/60">{details.task_title}</p>
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white/80">Önerilen Kişi:</span>
            <span className="text-white font-medium">{details.assigned_to}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-white/80">Güven Skoru:</span>
            <Badge variant={details.confidence_score > 0.8 ? "default" : "secondary"}>
              %{Math.round(details.confidence_score * 100)}
            </Badge>
          </div>

          <div>
            <span className="text-white/80 mb-2 block">Gerekçe:</span>
            <p className="text-sm text-white/90">{details.reason}</p>
          </div>

          {details.alternatives && details.alternatives.length > 0 && (
            <div>
              <span className="text-white/80 mb-2 block">Alternatif Adaylar:</span>
              <div className="space-y-2">
                {details.alternatives.slice(0, 3).map((alt: any, index: number) => (
                  <div key={index} className="flex items-center justify-between text-sm">
                    <span className="text-white/70">{alt.name}</span>
                    <span className="text-white/50">{alt.reason}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {details.potential_risks && details.potential_risks.length > 0 && (
            <div>
              <span className="text-white/80 mb-2 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-yellow-500" />
                Potansiyel Riskler:
              </span>
              <ul className="space-y-1">
                {details.potential_risks.map((risk: string, index: number) => (
                  <li key={index} className="text-sm text-yellow-200 flex items-center gap-2">
                    <span className="w-1 h-1 bg-yellow-500 rounded-full"></span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderTaskReassignment = () => {
    const { details } = data;
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Clock className="h-5 w-5 text-orange-500" />
          <div>
            <h3 className="font-semibold text-white">Görev Yeniden Ataması</h3>
            <p className="text-sm text-white/60">{details.task_title}</p>
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-4 space-y-3">
          <div className="flex items-center justify-between">
            <span className="text-white/80">Yeni Atanan:</span>
            <span className="text-white font-medium">{details.new_assignee}</span>
          </div>
          
          <div className="flex items-center justify-between">
            <span className="text-white/80">Güven Skoru:</span>
            <Badge variant={details.confidence_score > 0.8 ? "default" : "secondary"}>
              %{Math.round(details.confidence_score * 100)}
            </Badge>
          </div>

          <div>
            <span className="text-white/80 mb-2 block">Gerekçe:</span>
            <p className="text-sm text-white/90">{details.reason}</p>
          </div>

          {details.cascade_risks && details.cascade_risks.length > 0 && (
            <div>
              <span className="text-white/80 mb-2 flex items-center gap-2">
                <AlertTriangle className="h-4 w-4 text-red-500" />
                Cascade Etkileri:
              </span>
              <ul className="space-y-1">
                {details.cascade_risks.map((risk: string, index: number) => (
                  <li key={index} className="text-sm text-red-200 flex items-center gap-2">
                    <span className="w-1 h-1 bg-red-500 rounded-full"></span>
                    {risk}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  };

  const renderGenericConfirmation = () => {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-3">
          <Shield className="h-5 w-5 text-blue-500" />
          <div>
            <h3 className="font-semibold text-white">Aksiyon Onayı</h3>
            <p className="text-sm text-white/60">{data.title}</p>
          </div>
        </div>

        <div className="bg-white/5 rounded-lg p-4">
          <pre className="text-sm text-white/90 whitespace-pre-wrap">
            {JSON.stringify(data.details, null, 2)}
          </pre>
        </div>
      </div>
    );
  };

  const renderContent = () => {
    switch (data.type) {
      case 'task_assignment':
        return renderTaskAssignment();
      case 'task_reassignment':
        return renderTaskReassignment();
      default:
        return renderGenericConfirmation();
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <Card className="w-full max-w-2xl bg-black border-white/20">
        <CardHeader className="border-b border-white/10">
          <CardTitle className="text-white flex items-center gap-2">
            <CheckCircle className="h-5 w-5 text-[#38FF5D]" />
            Onay Gerekiyor
          </CardTitle>
        </CardHeader>
        
        <CardContent className="p-6">
          {renderContent()}
          
          <div className="flex gap-3 mt-6 pt-4 border-t border-white/10">
            <Button
              onClick={onConfirm}
              disabled={loading}
              className="flex-1 bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90"
            >
              {loading ? (
                <div className="flex items-center gap-2">
                  <div className="w-4 h-4 border-2 border-black/30 border-t-black rounded-full animate-spin"></div>
                  İşleniyor...
                </div>
              ) : (
                <div className="flex items-center gap-2">
                  <CheckCircle className="h-4 w-4" />
                  Onayla
                </div>
              )}
            </Button>
            
            <Button
              onClick={onReject}
              disabled={loading}
              variant="outline"
              className="flex-1 border-white/20 text-white hover:bg-white/10"
            >
              <div className="flex items-center gap-2">
                <XCircle className="h-4 w-4" />
                Reddet
              </div>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
