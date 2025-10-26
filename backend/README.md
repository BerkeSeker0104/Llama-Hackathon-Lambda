# Tella - Product Manager AI Assistant - Backend

EXACT implementation from prototype notebook with Firebase integration.

## 🚀 AI Features (COMPLETE)

✅ **PDF Parsing** - LlamaParse (num_workers=4, language="tr")  
✅ **Project Analysis** - Llama 4 Scout (temp=0.0, max_tokens=4096)  
✅ **Critical Analysis** - Eksikler, Riskler, Çelişkiler Tespiti  
✅ **Task Generation** - Llama 4 Maverick (temp=0.1)  
✅ **Auto-Assignment** - Llama 4 Maverick (temp=0.2)  
✅ **Sprint Planning** - Llama 4 Maverick (temp=0.2) 🆕  
✅ **Dynamic Sprint Revision** - Tatil, Gecikme Yönetimi 🆕  
✅ **Chat Orchestrator** - 12 tools with LangChain  
✅ **Firebase** - Firestore + Storage (lambda-59fe8)

## Setup

### 1. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select project: **lambda-59fe8**
3. Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Download JSON file
6. Copy credentials to `.env`:

```bash
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@lambda-59fe8.iam.gserviceaccount.com
```

### 3. Enable Firebase Services

- **Firestore Database**: Create in test mode
- **Storage**: Enable for PDF uploads
- **Authentication**: Enable Email/Password (optional)

### 4. Run Server

```bash
uvicorn app.main:app --reload
```

API will be available at: http://localhost:8000

## API Endpoints

### Contracts

- `POST /api/contracts/upload-and-analyze` - Upload PDF & analyze (EXACT prototype workflow)
- `POST /api/contracts/{id}/generate-tasks` - Generate tasks from contract
- `GET /api/contracts` - List all contracts
- `GET /api/contracts/{id}` - Get contract details

### Chat

- `POST /api/chat` - Chat with orchestrator (10 tools)

### Projects

- `GET /api/projects` - List all projects
- `GET /api/projects/{id}` - Get project details
- `GET /api/projects/{id}/tasks` - Get project tasks

### Sprints 🆕

- `POST /api/sprints/generate` - Generate sprint plan (AI-powered)
- `POST /api/sprints/replan` - Revise sprint plan (AI-powered)
- `GET /api/sprints/{project_id}` - Get project sprints
- `GET /api/sprints/{project_id}/{sprint_id}` - Get sprint details

### Employees

- `GET /api/employees` - List all employees
- `GET /api/employees/{department}` - List employees by department

### Health

- `GET /health` - Health check
- `GET /` - API info

## 📋 Complete Demo Flow (Prototip İş Akışı)

### 1️⃣ PDF Yükleme ve Analiz
```bash
POST /api/contracts/upload-and-analyze
# PDF yükle → LlamaParse ile parse et → Llama 4 Scout ile analiz et
# Çıktı: detailedDescription, criticalAnalysis (missingInfo, risks, contradictions), department, techStack, timeline, acceptanceCriteria
```

### 2️⃣ Task Oluşturma
```bash
POST /api/contracts/{contract_id}/generate-tasks
# Analiz sonucundan otomatik task'lar oluştur (Llama 4 Maverick)
# Çıktı: task_title, task_detail, task_stack, department için görev listesi
```

### 3️⃣ Task Atama (Chat ile)
```bash
POST /api/chat
{
  "message": "Bu görevi ata: API Endpoint Uptime İyileştirmesi"
}
# AI otomatik en uygun çalışanı bulur (tech stack, workload, department)
```

### 4️⃣ Sprint Planlama (Yeni! 🆕)
```bash
POST /api/sprints/generate
{
  "project_id": "project_abc123",
  "sprint_duration_weeks": 2
}
# Task'ları mantıklı sprint'lere dağıt (bağımlılıklar, öncelikler)
# Çıktı: Sprint 1, Sprint 2, Backlog
```

### 5️⃣ Dinamik Sprint Revizyon (Yeni! 🆕)
```bash
POST /api/sprints/replan
{
  "project_id": "project_abc123",
  "vacation_days": 5,
  "delays": 3
}
# Tatil günleri ve gecikmelere göre sprint planını revize et
# Çıktı: Yeni sprint planı, kaydırılan görevler, eklenen sprint'ler
```

### 6️⃣ Chat ile Tüm İşlemleri Yönetme
```bash
POST /api/chat
# "Hangi projelerim var?"
# "Proje detaylarını göster"
# "Görev listesi nedir?"
# "Mobil departmanındaki çalışanları listele"
# "Bu proje için sprint planı oluştur"
# "5 gün tatil var, sprint planını güncelle"
```

## Architecture

```
FastAPI Backend
├── LlamaParse Service (EXACT prototype)
├── Groq Service (EXACT prompts)
├── Firebase DB (lambda-59fe8)
├── Orchestrator (10 tools)
└── API Routes
```

## Environment Variables

See `.env.example` for all required variables.

## Troubleshooting

### Firebase Connection Error

Make sure `FIREBASE_PRIVATE_KEY` has proper newlines (`\n`).

### LlamaParse Timeout

Large PDFs may take 30+ seconds. This is normal.

### Groq API Rate Limit

Free tier has rate limits. Wait a few seconds between requests.

