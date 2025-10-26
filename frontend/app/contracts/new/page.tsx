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
    <div className="max-w-2xl mx-auto space-y-6">
      <h1 className="text-3xl font-bold text-white mb-6">Sözleşme Yükle</h1>

      <Card>
        <CardHeader>
          <CardTitle className="text-white">Proje Sözleşmesi Analizi</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {uploadStatus === 'idle' && (
            <>
              <div className="border-2 border-dashed border-white/20 rounded-lg p-8 text-center">
                <Upload className="mx-auto h-12 w-12 text-white/60 mb-4" />
                <p className="text-lg font-semibold mb-2 text-white">PDF Dosyası Yükleyin</p>
                <p className="text-sm text-white/60 mb-4">
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
                  <Button asChild className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
                    <span>Dosya Seç</span>
                  </Button>
                </label>
              </div>

              {file && (
                <div className="flex items-center justify-between p-4 bg-white/10 rounded-lg">
                  <div className="flex items-center gap-3">
                    <FileText className="h-8 w-8 text-[#38FF5D]" />
                    <div>
                      <p className="font-semibold text-white">{file.name}</p>
                      <p className="text-sm text-white/60">
                        {(file.size / 1024 / 1024).toFixed(2)} MB
                      </p>
                    </div>
                  </div>
                  <Button onClick={handleUpload} className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
                    Yükle ve Analiz Et
                  </Button>
                </div>
              )}

              {errorMessage && (
                <div className="flex items-center gap-2 p-4 bg-red-500/20 text-red-400 rounded-lg">
                  <AlertCircle className="h-5 w-5" />
                  <p>{errorMessage}</p>
                </div>
              )}
            </>
          )}

          {uploadStatus === 'uploading' && (
            <div className="text-center py-8">
              <Loader2 className="mx-auto h-12 w-12 text-[#38FF5D] animate-spin mb-4" />
              <p className="text-lg font-semibold text-white">Dosya yükleniyor...</p>
              <p className="text-sm text-white/60">Lütfen bekleyin</p>
            </div>
          )}

          {uploadStatus === 'analyzing' && (
            <div className="text-center py-8">
              <Loader2 className="mx-auto h-12 w-12 text-[#38FF5D] animate-spin mb-4" />
              <p className="text-lg font-semibold text-white">Sözleşme analiz ediliyor...</p>
              <p className="text-sm text-white/60 mb-2">
                AI sözleşmenizi inceliyor, görevler oluşturuluyor
              </p>
              <p className="text-xs text-white/60">
                ✨ Görevler otomatik olarak uygun çalışanlara atanıyor
              </p>
            </div>
          )}

          {uploadStatus === 'success' && (
            <div className="text-center py-8">
              <CheckCircle className="mx-auto h-12 w-12 text-[#38FF5D] mb-4" />
              <p className="text-lg font-semibold text-white">Analiz tamamlandı!</p>
              <div className="space-y-2 mb-4">
                <p className="text-sm text-white/60">
                  ✅ {totalTasks} görev oluşturuldu
                </p>
                {assignedCount > 0 && (
                  <p className="text-sm text-white/60">
                    👥 {assignedCount} görev otomatik olarak atandı
                  </p>
                )}
                <p className="text-sm text-white/60 mt-2">
                  Proje detaylarına yönlendiriliyorsunuz...
                </p>
              </div>
              <Button onClick={() => router.push(`/projects/${projectId}`)} className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
                Projeyi Görüntüle
              </Button>
            </div>
          )}

          {uploadStatus === 'error' && (
            <div className="text-center py-8">
              <AlertCircle className="mx-auto h-12 w-12 text-red-400 mb-4" />
              <p className="text-lg font-semibold text-red-400">Bir hata oluştu</p>
              <p className="text-sm text-white/60 mb-4">{errorMessage}</p>
              <Button onClick={() => setUploadStatus('idle')} className="bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90">
                Tekrar Dene
              </Button>
            </div>
          )}
        </CardContent>
      </Card>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle className="text-white">Nasıl Çalışır?</CardTitle>
        </CardHeader>
        <CardContent>
          <ol className="space-y-3">
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#38FF5D] text-black text-sm font-bold">
                1
              </span>
              <div>
                <p className="font-semibold text-white">PDF Yükleyin</p>
                <p className="text-sm text-white/60">
                  Proje sözleşmenizi veya iş tanımınızı yükleyin
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#38FF5D] text-black text-sm font-bold">
                2
              </span>
              <div>
                <p className="font-semibold text-white">AI Analizi</p>
                <p className="text-sm text-white/60">
                  Yapay zeka sözleşmeyi analiz eder, riskleri ve eksikleri tespit eder
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#38FF5D] text-black text-sm font-bold">
                3
              </span>
              <div>
                <p className="font-semibold text-white">Görev Oluşturma</p>
                <p className="text-sm text-white/60">
                  Otomatik olarak görevler oluşturulur ve teknoloji yığını belirlenir
                </p>
              </div>
            </li>
            <li className="flex items-start gap-3">
              <span className="flex items-center justify-center w-6 h-6 rounded-full bg-[#38FF5D] text-black text-sm font-bold">
                4
              </span>
              <div>
                <p className="font-semibold text-white">✨ Otomatik Atama (YENİ!)</p>
                <p className="text-sm text-white/60">
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

