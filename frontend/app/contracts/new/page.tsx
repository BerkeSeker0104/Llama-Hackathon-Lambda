'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { contractsApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle } from 'lucide-react';
import { useRouter } from 'next/navigation';

export default function NewContractPage() {
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'analyzing' | 'success' | 'error'>('idle');
  const [errorMessage, setErrorMessage] = useState('');
  const [projectId, setProjectId] = useState('');
  const [assignedCount, setAssignedCount] = useState(0);
  const [totalTasks, setTotalTasks] = useState(0);

  const uploadMutation = useMutation({
    mutationFn: async (formData: FormData) => {
      setUploadStatus('uploading');
      const uploadResponse = await contractsApi.upload(formData);
      const contractId = uploadResponse.data.contract_id;
      
      setUploadStatus('analyzing');
      const analyzeResponse = await contractsApi.analyze(contractId);
      return analyzeResponse.data;
    },
    onSuccess: (data) => {
      setUploadStatus('success');
      setProjectId(data.project_id);
      setAssignedCount(data.assigned_count || 0);
      setTotalTasks(data.total_tasks || 0);
      setTimeout(() => {
        router.push(`/projects/${data.project_id}`);
      }, 2000);
    },
    onError: (error: any) => {
      setUploadStatus('error');
      setErrorMessage(error.response?.data?.detail || 'Bir hata oluştu');
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      if (selectedFile.type !== 'application/pdf') {
        setErrorMessage('Lütfen sadece PDF dosyası yükleyin');
        return;
      }
      if (selectedFile.size > 10 * 1024 * 1024) {
        setErrorMessage('Dosya boyutu 10MB\'dan küçük olmalıdır');
        return;
      }
      setFile(selectedFile);
      setErrorMessage('');
    }
  };

  const handleUpload = () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    uploadMutation.mutate(formData);
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-2xl">
      <h1 className="text-3xl font-bold mb-6">Sözleşme Yükle</h1>

      <Card>
        <CardHeader>
          <CardTitle>Proje Sözleşmesi Analizi</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {uploadStatus === 'idle' && (
            <>
              <div className="border-2 border-dashed border-muted rounded-lg p-8 text-center">
                <Upload className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
                <p className="text-lg font-semibold mb-2">PDF Dosyası Yükleyin</p>
                <p className="text-sm text-muted-foreground mb-4">
                  Proje sözleşmenizi yükleyin ve AI ile analiz edin
                </p>
                <input
                  type="file"
                  accept=".pdf"
                  onChange={handleFileChange}
                  className="hidden"
                  id="file-upload"
                />
                <label htmlFor="file-upload">
                  <Button asChild>
                    <span>Dosya Seç</span>
                  </Button>
                </label>
              </div>

              {file && (
                <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-primary" />
                    <div>
                      <p className="font-semibold">{file.name}</p>
                      <p className="text-sm text-muted-foreground">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button onClick={handleUpload}>
                    Yükle ve Analiz Et
                  </Button>
                </div>
              )}

              {errorMessage && (
                <div className="flex items-center gap-2 p-4 bg-red-50 text-red-700 rounded-lg">
                  <AlertCircle className="h-5 w-5" />
                  <p>{errorMessage}</p>
                </div>
              )}
            </>
          )}

          {uploadStatus === 'uploading' && (
            <div className="text-center py-8">
              <Loader2 className="mx-auto h-12 w-12 text-primary animate-spin mb-4" />
              <p className="text-lg font-semibold">Dosya yükleniyor...</p>
              <p className="text-sm text-muted-foreground">Lütfen bekleyin</p>
            </div>
          )}

          {uploadStatus === 'analyzing' && (
            <div className="text-center py-8">
              <Loader2 className="mx-auto h-12 w-12 text-primary animate-spin mb-4" />
              <p className="text-lg font-semibold">Sözleşme analiz ediliyor...</p>
              <p className="text-sm text-muted-foreground mb-2">
                AI sözleşmenizi inceliyor, görevler oluşturuluyor
              </p>
              <p className="text-xs text-muted-foreground">
                ✨ Görevler otomatik olarak uygun çalışanlara atanıyor
              </p>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="text-center py-8">
              <CheckCircle className="mx-auto h-12 w-12 text-green-500 mb-4" />
              <p className="text-lg font-semibold text-green-700">Analiz tamamlandı!</p>
              <div className="space-y-2 mb-4">
                <p className="text-sm text-muted-foreground">
                  ✅ {totalTasks} görev oluşturuldu
                </p>
                {assignedCount > 0 && (
                  <p className="text-sm text-muted-foreground">
                    👥 {assignedCount} görev otomatik olarak atandı
                  </p>
                )}
                <p className="text-sm text-muted-foreground mt-2">
                  Proje detaylarına yönlendiriliyorsunuz...
                </p>
              </div>
              <Button onClick={() => router.push(`/projects/${projectId}`)}>
                Projeyi Görüntüle
              </Button>
            </div>
          )}

          {uploadStatus === 'error' && (
            <div className="text-center py-8">
              <AlertCircle className="mx-auto h-12 w-12 text-red-500 mb-4" />
              <p className="text-lg font-semibold text-red-700">Bir hata oluştu</p>
              <p className="text-sm text-muted-foreground mb-4">{errorMessage}</p>
              <Button onClick={() => setUploadStatus('idle')}>
                Tekrar Dene
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Nasıl Çalışır?</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3">
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                1
              </span>
              <div>
                <p className="font-semibold">PDF Yükleyin</p>
                <p className="text-sm text-muted-foreground">
                  Proje sözleşmenizi veya iş tanımınızı yükleyin
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                2
              </span>
              <div>
                <p className="font-semibold">AI Analizi</p>
                <p className="text-sm text-muted-foreground">
                  Yapay zeka sözleşmeyi analiz eder, riskleri ve eksikleri tespit eder
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                3
              </span>
              <div>
                <p className="font-semibold">Görev Oluşturma</p>
                <p className="text-sm text-muted-foreground">
                  Otomatik olarak görevler oluşturulur ve teknoloji yığını belirlenir
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-primary text-primary-foreground text-sm font-bold">
                4
              </span>
              <div>
                <p className="font-semibold">✨ Otomatik Atama (YENİ!)</p>
                <p className="text-sm text-muted-foreground">
                  AI, tech stack uyumu ve iş yüküne göre görevleri otomatik olarak en uygun çalışanlara atar
                </p>
              </div>
            </li>
          </ol>
        </CardContent>
      </Card>
    </div>
  );
}

