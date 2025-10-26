# Tella - Proje Yöneticisi AI Asistanı

Yapay zeka destekli proje analizi, görev yönetimi ve otomatik kaynak tahsisi platformu

[![Next.js](https://img.shields.io/badge/Next.js-16-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-10.7-orange)](https://firebase.google.com/)
[![Llama 4](https://img.shields.io/badge/Llama_4-Scout_&_Maverick-blue)](https://groq.com/)

## İçindekiler

- [Özellikler](#özellikler)
- [Teknoloji Stack](#teknoloji-stack)
- [Kurulum](#kurulum)
- [Kullanım](#kullanım)
- [API Dokümantasyonu](#api-dokümantasyonu)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

## Özellikler

### 1. Gelişmiş Sözleşme Analizi v2.0
- **PDF Yükleme:** LlamaParse ile PDF'den metin çıkarma
- **Akıllı Proje Adı Çıkarımı:** AI sözleşmeden proje adını otomatik çıkarıyor
- **Aşırı Dikkatli Analiz:** Llama 4 Scout ile kapsamlı analiz
  - EN AZ 5-10 eksiklik tespiti (teknik, güvenlik, süreç, vb.)
  - EN AZ 5-8 risk analizi (teknik, zamansal, finansal, yasal)
  - Hukuki endişeler (belirsiz ifadeler, tek taraflı koşullar)
  - Bütçe ve ödeme şartları çıkarımı
  - Kilometre taşları ve ara teslimatlar
- **Kapsam Maddesi Çıkarımı:** Tüm scope items detaylı şekilde belirleniyor
- **Teknoloji Çıkarımı:** Gerekli tech stack'i otomatik belirleme

### 2. Gelişmiş Görev Yönetimi v2.0
- **Kapsam Tabanlı Görev Oluşturma:** Her kapsam maddesi ayrı bir görev oluyor
  - Llama 4 Maverick ile akıllı task generation
  - scopeItems'dan öncelikli görev çıkarımı
  - Altyapı, entegrasyon, test, deployment görevleri
  - EN AZ 8-15 detaylı görev oluşturma
- **Akıllı Otomatik Atama:** Sözleşme analizi sırasında görevler otomatik olarak çalışanlara atanır
  - Tech stack uyumuna göre atama
  - İş yükü dengelemesi
  - Departman ve rol uyumu
  - Her atama için detaylı açıklama
- **Gelişmiş Görev Detayları:**
  - Tahmini süre (estimated_hours)
  - Öncelik seviyesi (priority)
  - Kaynak referansı (source - hangi maddeden geldiği)
  - Detaylı açıklamalar (ne, nasıl, neden)
- **Durum Takibi:** Pending, Assigned, Completed durumları

### 3. Çalışan Yönetimi
- **Çalışan Dizini:** 14 çalışan, 5 departman
- **Yetenek Eşleştirme:** Tech stack bazlı eşleştirme
- **İş Yükü Takibi:** Düşük/Orta/Yüksek iş yükü göstergeleri
- **Departman Analizi:** Departman bazlı iş yükü dağılımı

### 4. AI Sohbet Arayüzü
- **12 Tool Entegrasyonu:** Proje, görev, sprint ve çalışan sorguları
- **Doğal Dil İşleme:** Türkçe komutları anlama
- **Gerçek Zamanlı:** Anında yanıtlar
- **Tool Orchestration:** LangChain ile tool yönetimi

### 5. Proje Yönetimi
- **Proje Listesi:** Tüm projeleri görüntüleme
- **Detaylı Analiz:** Risk, eksik bilgi ve çelişki analizi
- **Kabul Kriterleri:** Otomatik belirlenen kriterler
- **Timeline Tahmini:** Proje süresi tahminleri

### 6. Sprint Planlama
- **Otomatik Sprint Oluşturma:** Llama 4 Maverick ile akıllı sprint planı
- **Bağımlılık Yönetimi:** Görev bağımlılıklarına göre sprint dağıtımı
- **Dinamik Revizyon:** Tatil günleri ve gecikmelere göre plan güncelleme
- **İş Yükü Dengeleme:** Sprint'ler arası dengeli görev dağılımı

## Teknoloji Stack

### Backend
```
FastAPI          - REST API framework
Firebase         - Database & Auth (lambda-59fe8)
LlamaParse       - PDF to text conversion
Groq API         - Llama 4 model access
LangChain        - Tool orchestration
Python 3.12      - Programming language
```

### Frontend
```
Next.js 16       - React framework
TypeScript       - Type safety
TanStack Query   - Data fetching & caching
shadcn/ui        - UI component library
Tailwind CSS     - Styling
Axios            - HTTP client
```

### AI Models
```
Llama 4 Scout (17B-16e)       - Contract analysis & critical analysis
Llama 4 Maverick (17B-128e)   - Task generation, assignment & sprint planning
```

## Kurulum

### Ön Gereksinimler

- Python 3.12+
- Node.js 18+
- Firebase hesabı
- Groq API key
- LlamaParse API key

### 1. Repository'yi Klonlayın

```bash
git clone <repository-url>
cd Llama-Hackathon-Lambda
```

### 2. Backend Kurulumu

```bash
cd backend

# Virtual environment oluştur
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# .env dosyasını oluştur
cp env.example .env
```

**.env dosyasını düzenleyin:**

```env
GROQ_API_KEY=your_groq_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here
FIREBASE_CREDENTIALS_PATH=./lambda-59fe8-firebase-adminsdk.json
FIREBASE_PROJECT_ID=lambda-59fe8
FIREBASE_STORAGE_BUCKET=lambda-59fe8.firebasestorage.app
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Firebase credentials dosyasını yerleştirin:**

```bash
# Firebase console'dan indirdiğiniz JSON dosyasını backend/ klasörüne kopyalayın
cp /path/to/your/firebase-adminsdk.json ./
```

**Backend'i başlatın:**

```bash
uvicorn app.main:app --reload
```

Backend şu adreste çalışacak: `http://localhost:8000`

### 3. Frontend Kurulumu

```bash
cd frontend

# Bağımlılıkları yükle
npm install

# Development server'ı başlat
npm run dev
```

Frontend şu adreste çalışacak: `http://localhost:3000`

### 4. Seed Data Yükleme (Opsiyonel)

Demo için örnek verileri yükleyin:

```bash
cd backend
source venv/bin/activate
python seed_data.py
```

Bu komut şunları yükler:
- 14 çalışan (5 departman)
- 3 örnek proje
- 22 görev (bazıları atanmış)

## Kullanım

### Hızlı Başlangıç

1. **Ana Sayfayı Açın**
   ```
   http://localhost:3000
   ```

2. **Sözleşme Yükleyin**
   - "Sözleşme Yükle" butonuna tıklayın
   - PDF dosyasını seçin
   - "Yükle ve Analiz Et" butonuna tıklayın
   - AI otomatik olarak taskları oluşturup çalışanlara atayacak

3. **Analiz Sonuçlarını Görüntüleyin**
   - Otomatik olarak proje detay sayfasına yönlendirileceksiniz
   - Kaç görev oluşturuldu ve atandığını göreceksiniz
   - 3 sekme: Genel Bakış, Analiz, Kabul Kriterleri

4. **Görevleri Görüntüleyin**
   - "Görevleri Görüntüle" butonuna tıklayın
   - Otomatik oluşturulan ve atanmış görevleri görün
   - Her görev için atama nedeni açıklanır

5. **İlave Atamalar (Opsiyonel)**
   - Eğer bazı görevler atanmamışsa
   - "Otomatik Ata" butonuna tıklayın
   - AI en uygun çalışanı otomatik olarak atayacak

### AI Sohbet Kullanımı

Chat sayfasında şu komutları deneyebilirsiniz:

```
"Hangi projelerim var?"
"Backend departmanındaki çalışanları listele"
"Ahmet Yılmaz'ın iş yükü nasıl?"
"E-Ticaret Platformu projesinin görevlerini göster"
"Mobil Bankacılık projesine geç"
```

## API Dokümantasyonu

### Backend Endpoints

**Health Check:**
```bash
GET /health
```

**Projects:**
```bash
GET    /api/projects           # Tüm projeleri listele
GET    /api/projects/{id}      # Proje detayı
POST   /api/projects           # Yeni proje oluştur
```

**Tasks:**
```bash
GET    /api/projects/{id}/tasks    # Proje görevleri
POST   /api/tasks/{id}/assign      # Görev ata
```

**Employees:**
```bash
GET    /api/employees                      # Tüm çalışanlar
GET    /api/employees/department/{dept}   # Departman çalışanları
GET    /api/employees/workload/{dept}     # Departman iş yükü
```

**Chat:**
```bash
POST   /api/chat                    # Mesaj gönder
GET    /api/chat/history/{session}  # Sohbet geçmişi
```

**Contracts:**
```bash
POST   /api/contracts/upload                      # PDF yükle
POST   /api/contracts/{id}/analyze?auto_assign=true  # Analiz et ve otomatik ata
POST   /api/contracts/{id}/auto-assign-tasks      # Mevcut taskları otomatik ata
GET    /api/contracts                             # Tüm sözleşmeler
GET    /api/contracts/{id}                        # Sözleşme detayı
DELETE /api/contracts/{id}                        # Sözleşme sil
```

**Sprints:**
```bash
POST   /api/sprints/generate          # Sprint planı oluştur
POST   /api/sprints/replan            # Sprint planını revize et
GET    /api/sprints/{project_id}      # Proje sprint'leri
GET    /api/sprints/{project_id}/{sprint_id}  # Sprint detayı
```

**Swagger UI:** `http://localhost:8000/docs`

## Deployment

### Backend Deployment (Railway/Render)

1. **Railway:**
   ```bash
   # railway.json oluştur
   {
     "build": {
       "builder": "NIXPACKS"
     },
     "deploy": {
       "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
       "restartPolicyType": "ON_FAILURE"
     }
   }
   ```

2. **Environment Variables:**
   - `GROQ_API_KEY`
   - `LLAMA_CLOUD_API_KEY`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_PRIVATE_KEY`
   - `FIREBASE_CLIENT_EMAIL`
   - `FIREBASE_STORAGE_BUCKET`
   - `CORS_ORIGINS`

### Frontend Deployment (Vercel)

1. **Vercel'e Deploy:**
   ```bash
   cd frontend
   vercel
   ```

2. **Environment Variables:**
   ```env
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   ```

3. **Build Settings:**
   - Framework: Next.js
   - Build Command: `npm run build`
   - Output Directory: `.next`

## Troubleshooting

### Backend Sorunları

**Problem:** `ModuleNotFoundError: No module named 'app'`
```bash
# Çözüm: Backend dizininde olduğunuzdan emin olun
cd backend
python -m uvicorn app.main:app --reload
```

**Problem:** `Firebase connection error`
```bash
# Çözüm: .env dosyasını ve credentials'ı kontrol edin
cat .env
ls -la lambda-59fe8-firebase-adminsdk.json
```

**Problem:** `Groq API rate limit`
```bash
# Çözüm: API key'inizi kontrol edin veya rate limit'i bekleyin
# Groq console: https://console.groq.com
```

### Frontend Sorunları

**Problem:** `404 Not Found on all pages`
```bash
# Çözüm: .next klasörünü temizleyin ve yeniden başlatın
rm -rf .next
npm run dev
```

**Problem:** `API connection refused`
```bash
# Çözüm: Backend'in çalıştığını kontrol edin
curl http://localhost:8000/health
```

**Problem:** `Module not found errors`
```bash
# Çözüm: node_modules'ü yeniden yükleyin
rm -rf node_modules package-lock.json
npm install
```

### Seed Data Sorunları

**Problem:** `Seed script fails`
```bash
# Çözüm: Virtual environment'ı aktifleştirin
source venv/bin/activate
python seed_data.py
```

## Proje Yapısı

```
Llama-Hackathon-Lambda/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app
│   │   ├── firebase_db.py       # Firebase integration
│   │   ├── orchestrator.py      # AI orchestrator
│   │   ├── tools.py             # LangChain tools
│   │   └── services/
│   │       └── llamaparse_service.py
│   ├── seed_data.py             # Demo data script
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── app/
│   │   ├── page.tsx             # Home page
│   │   ├── layout.tsx           # Root layout
│   │   ├── projects/            # Projects pages
│   │   ├── chat/                # Chat page
│   │   ├── employees/           # Employees pages
│   │   └── contracts/           # Contract upload
│   ├── components/
│   │   └── ui/                  # shadcn/ui components
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   └── utils.ts
│   └── hooks/
│       └── use-toast.ts
└── README.md                    # Bu dosya
```

## Roadmap

### Tamamlanan (Sprint 1-3)
- Contract analysis
- Task generation
- Auto-assignment
- Chat interface
- Employee management
- Demo data

### Sprint 4 (Tamamlandı)
- Toast notifications
- Sprint Planning AI
- Dynamic Sprint Revision
- Complete documentation
- Firebase integration
- 12 Tool orchestration

### Sprint 5 (Tamamlandı)
- Otomatik Task Atama Sistemi
  - Sözleşme analizi sırasında tasklar otomatik olarak atanır
  - AI tech stack uyumu ve iş yüküne göre karar verir
  - Her atama için açıklama sağlanır
- Frontend otomatik atama bildirimleri
- Manuel otomatik atama endpoint'i

### Sprint 6 (Tamamlandı) v2.0
- AI Analiz Sistemi Tamamen Yenilendi
  - Akıllı proje adı çıkarımı
  - Aşırı dikkatli eksiklik tespiti (5-10 madde)
  - Kapsamlı risk analizi (5-8 risk, 6 kategori)
  - Hukuki endişe tespiti
  - Bütçe ve ödeme şartları çıkarımı
- Kapsam Bazlı Görev Oluşturma
  - Her kapsam maddesi ayrı görev oluyor
  - 8-15 detaylı görev garantisi
  - Tahmini süre ve öncelik belirleme
  - Kaynak referanslı görevler
- Gelişmiş AI prompt'ları (82 + 90 satır)

### Gelecek Özellikler
- [ ] User authentication
- [ ] Multi-company support
- [ ] Advanced sprint analytics
- [ ] Change order management
- [ ] Advanced analytics dashboard
- [ ] Email notifications
- [ ] Mobile app
- [ ] Real-time collaboration

## Katkıda Bulunma

1. Fork edin
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit edin (`git commit -m 'Add amazing feature'`)
4. Push edin (`git push origin feature/amazing-feature`)
5. Pull Request açın

## Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## Ekip

- AI Assistant - Full Stack Development
- Llama 4 Scout - Contract Analysis
- Llama 4 Maverick - Task Generation & Assignment

## Destek

Sorularınız için:
- Email: support@example.com
- Discord: [Discord Link]
- Docs: [Documentation Link]

## Teşekkürler

- [Groq](https://groq.com/) - Llama 4 model access
- [LlamaParse](https://www.llamaindex.ai/) - PDF parsing
- [Firebase](https://firebase.google.com/) - Backend infrastructure
- [Vercel](https://vercel.com/) - Frontend hosting
- [shadcn/ui](https://ui.shadcn.com/) - UI components

---

Made with Llama 4 Scout & Maverick
