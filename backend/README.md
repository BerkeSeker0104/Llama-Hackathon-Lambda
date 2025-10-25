# Product Manager AI Assistant - Backend

EXACT implementation from prototype notebook with Firebase integration.

## Features

✅ **PDF Parsing** - LlamaParse (num_workers=4, language="tr")  
✅ **Project Analysis** - Llama 4 Scout (temp=0.0, max_tokens=4096)  
✅ **Task Generation** - Llama 4 Maverick (temp=0.1)  
✅ **Auto-Assignment** - Llama 4 Maverick (temp=0.2)  
✅ **Chat Orchestrator** - 10 tools with LangChain  
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

### Health

- `GET /health` - Health check
- `GET /` - API info

## Demo Flow

1. Upload `4-Mesut_Kara_Mobil_Uygulama_Sozlesmesi.pdf`
2. View analysis (should match prototype Cell 7 output)
3. Generate tasks (should match prototype Cell 9 output)
4. Chat: "Hangi projelerim var?"
5. Chat: "Bu görevi ata: API Endpoint Uptime İyileştirmesi"

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

