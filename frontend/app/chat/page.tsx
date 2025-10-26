'use client';

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatApi } from '@/lib/api';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Send, Bot, User } from 'lucide-react';

// Örnek konuşma senaryoları
const CONVERSATION_EXAMPLES = [
  {
    category: 'Acil Durum Yönetimi',
    prompts: [
      'Mert Koç acil durumu var, 5 gün çalışamayacak. Görevlerini yeniden ata.',
      'Ayşe Yılmaz izne çıktı, görevlerini başkasına ver.',
    ],
  },
  {
    category: 'Sprint Planlama',
    prompts: [
      'Bu proje için 2 haftalık sprint planı oluştur',
      'Sprint planını revize et, 3 gün gecikme var',
      'Sprint sağlık durumunu analiz et',
    ],
  },
  {
    category: 'Gecikme Tahmini',
    prompts: [
      'Proje zamanında biter mi?',
      'Hangi görevler gecikme riski taşıyor?',
      'Bu projenin risk analizi nedir?',
    ],
  },
  {
    category: 'Görev Yönetimi',
    prompts: [
      'Hangi çalışanlar müsait?',
      'Bu görevi en uygun kişiye ata',
      'Tüm görevleri listele',
    ],
  },
];

export default function ChatPage() {
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [input, setInput] = useState('');
  const [showExamples, setShowExamples] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const sendMutation = useMutation({
    mutationFn: (message: string) => chatApi.sendMessage(sessionId, message),
    onSuccess: (response) => {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: response.data.response },
      ]);
    },
  });

  const handleSend = (message?: string) => {
    const messageToSend = message || input;
    if (!messageToSend.trim()) return;

    setMessages((prev) => [...prev, { role: 'user', content: messageToSend }]);
    sendMutation.mutate(messageToSend);
    setInput('');
    setShowExamples(false);
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

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Header */}
      <div className="border-b bg-card px-6 py-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center">
            <Bot className="h-6 w-6 text-primary-foreground" />
          </div>
          <div>
            <h1 className="text-xl font-semibold">Tella AI Asistanı</h1>
            <p className="text-sm text-muted-foreground">Dinamik Sprint Yönetimi</p>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Chat Area */}
        <div className="flex-1 flex flex-col">
          <div className="flex-1 overflow-y-auto p-6">
            {messages.length === 0 && showExamples ? (
              <div className="max-w-4xl mx-auto">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-4">
                    <Bot className="h-8 w-8 text-primary" />
                  </div>
                  <h2 className="text-2xl font-bold mb-2">Proje Yönetimi Asistanınız</h2>
                  <p className="text-muted-foreground">
                    Aşağıdaki kategorilerden birini seçerek başlayabilirsiniz
                  </p>
                </div>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  {CONVERSATION_EXAMPLES.map((category) => (
                    <Card key={category.category} className="overflow-hidden">
                      <CardHeader className="pb-3">
                        <CardTitle className="text-lg flex items-center gap-2">
                          <div className="w-2 h-2 rounded-full bg-primary"></div>
                          {category.category}
                        </CardTitle>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        {category.prompts.map((prompt, i) => (
                          <button
                            key={i}
                            onClick={() => handleExampleClick(prompt)}
                            className="w-full text-left p-3 rounded-lg border hover:bg-muted/50 hover:border-primary/50 transition-all duration-200 text-sm group"
                          >
                            <span className="group-hover:text-primary transition-colors">
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
                <div className="text-center text-muted-foreground">
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
                      <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center shrink-0">
                        <Bot className="h-5 w-5 text-primary-foreground" />
                      </div>
                    )}
                    <div
                      className={`max-w-[75%] rounded-2xl px-4 py-3 ${
                        message.role === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted border'
                      }`}
                    >
                      <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
                    </div>
                    {message.role === 'user' && (
                      <div className="w-10 h-10 rounded-full bg-secondary flex items-center justify-center shrink-0">
                        <User className="h-5 w-5" />
                      </div>
                    )}
                  </div>
                ))}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>

          {/* Input Area */}
          <div className="border-t bg-card p-6">
            <div className="max-w-4xl mx-auto">
              <div className="flex gap-3">
                <div className="flex-1 relative">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && handleSend()}
                    placeholder="Mesajınızı yazın..."
                    className="w-full px-4 py-3 pr-12 rounded-xl border border-input bg-background focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-all"
                    disabled={sendMutation.isPending}
                  />
                  <Button
                    onClick={handleButtonSend}
                    disabled={!input.trim() || sendMutation.isPending}
                    size="icon"
                    className="absolute right-2 top-1/2 -translate-y-1/2 h-8 w-8 rounded-lg"
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
