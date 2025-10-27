'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Send, Bot, User, AlertTriangle, CheckCircle, Clock, Users, TrendingUp } from 'lucide-react';
import { ConfirmationDialog } from '@/components/ui/confirmation-dialog';


export default function ChatPage() {
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [messages, setMessages] = useState<Array<{ 
    role: string; 
    content: string; 
    requires_confirmation?: boolean;
    confirmation_data?: any;
  }>>([]);
  const [input, setInput] = useState('');
  const [showExamples, setShowExamples] = useState(true);
  const [categories, setCategories] = useState<Array<{
    category: string;
    prompts: string[];
  }>>([]);
  const [pendingConfirmation, setPendingConfirmation] = useState<{
    type: string;
    title: string;
    details: any;
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Kategorileri yükle
  useEffect(() => {
    const loadCategories = async () => {
      try {
        const response = await chatApi.getCategories();
        setCategories(response.data.categories || []);
      } catch (error) {
        console.error('Kategoriler yüklenirken hata:', error);
        // Varsayılan kategoriler
        setCategories([
          {
            category: "Acil Durum Yönetimi",
            prompts: [
              "Mert Koç acil durumu var, 5 gün çalışamayacak. Görevlerini yeniden ata.",
              "Ayşe Yılmaz izne çıktı, görevlerini başkasına ver.",
            ]
          },
          {
            category: "Sprint Planlama",
            prompts: [
              "Bu proje için 2 haftalık sprint planı oluştur",
              "Sprint planını revize et, 3 gün gecikme var",
              "Sprint sağlık durumunu analiz et",
            ]
          },
          {
            category: "Gecikme Tahmini",
            prompts: [
              "Proje zamanında biter mi?",
              "Hangi görevler gecikme riski taşıyor?",
              "Bu projenin risk analizi nedir?",
            ]
          },
          {
            category: "Görev Yönetimi",
            prompts: [
              "Hangi çalışanlar müsait?",
              "Bu görevi en uygun kişiye ata",
              "Tüm görevleri listele",
            ]
          }
        ]);
      }
    };

    loadCategories();
  }, []);

  const sendMutation = useMutation({
    mutationFn: (message: string) => chatApi.sendMessage(sessionId, message),
    onSuccess: (response) => {
      const assistantMessage = {
        role: 'assistant' as const,
        content: response.data.response,
        requires_confirmation: response.data.requires_confirmation || false,
        confirmation_data: response.data.confirmation_data || null
      };
      
      setMessages((prev) => [...prev, assistantMessage]);
      
      // Eğer onay gerekiyorsa dialog'u göster
      if (response.data.requires_confirmation && response.data.confirmation_data) {
        const confirmationData = response.data.confirmation_data;
        setPendingConfirmation({
          type: confirmationData.confirmation_type || 'general',
          title: 'Aksiyon Onayı',
          details: confirmationData.tool_result || {}
        });
      }
    },
    onError: (error: any) => {
      console.error('Mesaj gönderme hatası:', error);
      const errorMessage = {
        role: 'assistant' as const,
        content: `Üzgünüm, bir hata oluştu: ${error.response?.data?.detail || error.message || 'Bilinmeyen hata'}. Lütfen tekrar deneyin.`,
        requires_confirmation: false,
        confirmation_data: null
      };
      setMessages((prev) => [...prev, errorMessage]);
    },
  });

  const confirmMutation = useMutation({
    mutationFn: ({ actionType, actionData, confirmed }: { 
      actionType: string; 
      actionData: any; 
      confirmed: boolean 
    }) => chatApi.confirmAction(sessionId, actionType, actionData, confirmed),
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.message },
      ]);
      setPendingConfirmation(null);
    },
    onError: (error: any) => {
      console.error('Onay işleme hatası:', error);
      const errorMessage = {
        role: 'assistant' as const,
        content: `Onay işlemi sırasında hata oluştu: ${error.response?.data?.detail || error.message || 'Bilinmeyen hata'}. Lütfen tekrar deneyin.`,
        requires_confirmation: false,
        confirmation_data: null
      };
      setMessages((prev) => [...prev, errorMessage]);
      setPendingConfirmation(null);
    },
  });

  const handleSend = (message?: string) => {
    const messageToSend = message || input;
    if (!messageToSend.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: messageToSend }]);
    sendMutation.mutate(messageToSend);
    setInput('');
  };

  const handleExampleClick = (prompt: string) => {
    setInput(prompt);
    handleSend(prompt);
  };

  const handleButtonSend = () => {
    if (input.trim()) {
      handleSend();
    }
  };

  const handleConfirm = () => {
    if (pendingConfirmation) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.confirmation_data) {
        confirmMutation.mutate({
          actionType: lastMessage.confirmation_data.tool_name,
          actionData: lastMessage.confirmation_data,
          confirmed: true
        });
      }
    }
  };

  const handleReject = () => {
    if (pendingConfirmation) {
      const lastMessage = messages[messages.length - 1];
      if (lastMessage?.confirmation_data) {
        confirmMutation.mutate({
          actionType: lastMessage.confirmation_data.tool_name,
          actionData: lastMessage.confirmation_data,
          confirmed: false
        });
      }
    }
  };

  const handleCloseConfirmation = () => {
    setPendingConfirmation(null);
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-screen flex flex-col bg-black">
      {/* Header */}
      <div className="border-b border-white/10 bg-black px-6 py-4 shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#38FF5D] flex items-center justify-center">
            <Bot className="h-6 w-6 text-black" />
          </div>
          <div>
            <h1 className="text-xl font-semibold text-white">Tella AI Asistanı</h1>
            <p className="text-sm text-white/60">Dinamik Sprint Yönetimi</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-h-0">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="flex-1 p-6 overflow-y-auto">
            {messages.length === 0 && showExamples ? (
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-6">
                  <div className="w-16 h-16 rounded-full bg-[#38FF5D]/20 flex items-center justify-center mx-auto mb-4">
                    <Bot className="h-8 w-8 text-[#38FF5D]" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2 text-white">Proje Yönetimi Asistanınız</h2>
                  <p className="text-white/60">
                    Aşağıdaki kategorilerden birini seçerek başlayabilirsiniz
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {categories.map((category) => (
                    <Card key={category.category} className="overflow-hidden h-fit">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg flex items-center gap-2 text-white">
                          <div className="w-2 h-2 rounded-full bg-[#38FF5D]"></div>
                          {category.category}
                        </CardTitle>
                        {category.type && (
                          <div className="text-xs text-white/60 mt-1">
                            {category.type === 'project_analysis' && 'Proje bazlı analiz'}
                            {category.type === 'sprint_planning' && 'Sprint planlama ve revizyon'}
                            {category.type === 'task_management' && 'Görev atama ve yönetimi'}
                            {category.type === 'emergency_management' && 'Acil durum yönetimi'}
                            {category.type === 'resource_analysis' && 'Kaynak ve performans analizi'}
                          </div>
                        )}
                      </CardHeader>
                      <CardContent className="space-y-2">
                        {category.prompts.map((prompt, i) => (
                          <button
                            key={i}
                            onClick={() => handleExampleClick(prompt)}
                            className="w-full text-left p-3 rounded-lg border border-white/10 hover:bg-white/5 hover:border-[#38FF5D]/50 transition-all duration-200 text-sm group text-white"
                          >
                            <span className="group-hover:text-[#38FF5D] transition-colors">
                              {prompt}
                            </span>
                          </button>
                        ))}
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </div>
            ) : messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <div className="text-center text-white/60">
                  <Bot className="mx-auto h-12 w-12 mb-4" />
                  <p className="text-lg">AI asistanı ile sohbete başlayın</p>
                </div>
              </div>
            ) : (
              <div className="max-w-4xl mx-auto space-y-6">
                {messages.map((message, i) => (
                  <div
                    key={i}
                    className={`flex gap-4 ${
                      message.role === 'user' ? 'justify-end' : 'justify-start'
                    }`}
                  >
                    {message.role === 'assistant' && (
                      <div className="w-10 h-10 rounded-full bg-[#38FF5D] flex items-center justify-center shrink-0">
                        <Bot className="h-5 w-5 text-black" />
                      </div>
                    )}
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-[#38FF5D] text-black'
                          : 'bg-white/10 border border-white/20 text-white'
                      }`}
                    >
                      <div className="whitespace-pre-wrap leading-relaxed">
                        {message.requires_confirmation ? (
                          <div className="space-y-3">
                            <div className="flex items-center gap-2 text-[#38FF5D]">
                              <AlertTriangle className="h-4 w-4" />
                              <span className="text-sm font-medium">Onay Gerekli</span>
                            </div>
                            <div className="text-sm text-white/90">
                              {message.content}
                            </div>
                          </div>
                        ) : (
                          <div className="space-y-2">
                            {message.content.includes('**') ? (
                              <div className="space-y-2">
                                {message.content.split('\n').map((line, lineIndex) => {
                                  if (line.startsWith('**') && line.endsWith('**')) {
                                    const title = line.replace(/\*\*/g, '');
                                    return (
                                      <h4 key={lineIndex} className="font-semibold text-[#38FF5D] text-sm">
                                        {title}
                                      </h4>
                                    );
                                  } else if (line.startsWith('- ')) {
                                    const item = line.replace('- ', '');
                                    return (
                                      <div key={lineIndex} className="flex items-start gap-2 text-sm">
                                        <span className="w-1 h-1 bg-white/60 rounded-full mt-2 shrink-0"></span>
                                        <span>{item}</span>
                                      </div>
                                    );
                                  } else if (line.startsWith('   ')) {
                                    // Indented lines (sub-items)
                                    const item = line.trim();
                                    return (
                                      <div key={lineIndex} className="flex items-start gap-2 text-sm ml-4">
                                        <span className="w-1 h-1 bg-white/40 rounded-full mt-2 shrink-0"></span>
                                        <span className="text-white/80">{item}</span>
                                      </div>
                                    );
                                  } else if (line.trim()) {
                                    return (
                                      <p key={lineIndex} className="text-sm">
                                        {line}
                                      </p>
                                    );
                                  }
                                  return null;
                                })}
                              </div>
                            ) : (
                              <p>{message.content}</p>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-10 h-10 rounded-full bg-white/10 flex items-center justify-center shrink-0">
                        <User className="h-5 w-5 text-white" />
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area - Always visible at bottom */}
        <div className="border-t border-white/10 bg-black p-6 shrink-0 sticky bottom-0">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-3">
              <div className="flex-1 relative">
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                  placeholder="Mesajınızı yazın..."
                  className="w-full px-4 py-3 pr-12 rounded-xl border border-white/10 bg-black text-white placeholder:text-white/40 focus:outline-none focus:ring-2 focus:ring-[#38FF5D] focus:border-transparent transition-all"
                  disabled={sendMutation.isPending}
                />
                <Button
                  onClick={handleButtonSend}
                  disabled={!input.trim() || sendMutation.isPending}
                  size="icon"
                  className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-lg bg-[#38FF5D] text-black hover:bg-[#38FF5D]/90"
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        </div>
      </div>

      {/* Confirmation Dialog */}
      <ConfirmationDialog
        isOpen={!!pendingConfirmation}
        onClose={handleCloseConfirmation}
        onConfirm={handleConfirm}
        onReject={handleReject}
        data={pendingConfirmation || { type: '', title: '', details: {} }}
        loading={confirmMutation.isPending}
      />
    </div>
  );
}
