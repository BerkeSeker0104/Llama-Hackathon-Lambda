# 🚀 Tella - AI-Powered Project Management Assistant

> **Intelligent contract analysis, automated task generation, and smart resource allocation powered by Llama 4 AI models**

[![Next.js](https://img.shields.io/badge/Next.js-16-black?style=for-the-badge&logo=next.js)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Firebase](https://img.shields.io/badge/Firebase-10.7-orange?style=for-the-badge&logo=firebase)](https://firebase.google.com/)
[![Llama 4](https://img.shields.io/badge/Llama_4-Scout_&_Maverick-blue?style=for-the-badge&logo=meta)](https://groq.com/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0-blue?style=for-the-badge&logo=typescript)](https://www.typescriptlang.org/)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-4.0-38B2AC?style=for-the-badge&logo=tailwind-css)](https://tailwindcss.com/)

<div align="center">

*Transform your project management with AI-powered contract analysis, intelligent task generation, and automated resource allocation*

[🎯 Features](#-key-features) • [⚡ Quick Start](#-quick-start) • [📚 Documentation](#-documentation) • [🤝 Contributing](#-contributing) • [📄 License](#-license)

</div>

## 📋 Table of Contents

- [🎯 Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [⚡ Quick Start](#-quick-start)
- [🔧 Installation](#-installation)
- [📖 Usage Guide](#-usage-guide)
- [🔌 API Documentation](#-api-documentation)
- [🚀 Deployment](#-deployment)
- [🐛 Troubleshooting](#-troubleshooting)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🎯 Key Features

### 🤖 **Advanced AI Contract Analysis v2.0**
- **📄 Intelligent PDF Processing:** LlamaParse-powered document extraction with multi-language support
- **🎯 Smart Project Name Extraction:** AI automatically extracts project names from contract content
- **🔍 Comprehensive Analysis Engine:** Llama 4 Scout-powered deep analysis
  - **Missing Information Detection:** 5-10 critical gaps (technical, security, process)
  - **Risk Assessment:** 5-8 detailed risk analysis (technical, temporal, financial, legal)
  - **Legal Concern Identification:** Ambiguous terms, one-sided conditions detection
  - **Budget & Payment Terms:** Automatic extraction and analysis
  - **Milestone Tracking:** Key deliverables and intermediate checkpoints
- **📋 Scope Item Extraction:** Detailed breakdown of all project requirements
- **⚙️ Technology Stack Detection:** Automatic identification of required tech stack

### 🎯 **Intelligent Task Management v2.0**
- **📝 Scope-Based Task Generation:** Each scope item becomes a dedicated task
  - Llama 4 Maverick-powered intelligent task creation
  - Priority-based task extraction from scope items
  - Infrastructure, integration, testing, deployment tasks
  - **Guaranteed 8-15 detailed tasks per project**
- **👥 Smart Auto-Assignment:** Tasks automatically assigned during contract analysis
  - Tech stack compatibility matching
  - Workload balancing across team members
  - Department and role alignment
  - Detailed assignment reasoning for each task
- **📊 Advanced Task Details:**
  - Estimated hours calculation
  - Priority level assignment
  - Source reference (which scope item generated the task)
  - Comprehensive descriptions (what, how, why)
- **📈 Status Tracking:** Pending, Assigned, Completed workflow

### 👥 **Team Management & Resource Allocation**
- **👤 Employee Directory:** 14 employees across 5 departments
- **🎯 Skill Matching:** Tech stack-based employee matching
- **📊 Workload Tracking:** Low/Medium/High workload indicators
- **📈 Department Analytics:** Department-wise workload distribution

### 💬 **AI Chat Interface**
- **🔧 12-Tool Integration:** Project, task, sprint, and employee queries
- **🌐 Natural Language Processing:** Turkish language command understanding
- **⚡ Real-time Responses:** Instant AI-powered assistance
- **🔗 Tool Orchestration:** LangChain-powered tool management

### 📊 **Project Management Dashboard**
- **📋 Project Overview:** Complete project listing and management
- **🔍 Detailed Analysis:** Risk, missing information, and contradiction analysis
- **✅ Acceptance Criteria:** Automatically determined project criteria
- **⏱️ Timeline Estimation:** AI-powered project duration predictions

### 🏃 **Sprint Planning & Management**
- **🤖 Automated Sprint Creation:** Llama 4 Maverick-powered intelligent sprint planning
- **🔗 Dependency Management:** Task dependency-based sprint distribution
- **🔄 Dynamic Revision:** Holiday and delay-aware plan updates
- **⚖️ Workload Balancing:** Balanced task distribution across sprints

## 🏗️ Architecture

### 🖥️ **Backend Stack**
```yaml
Framework: FastAPI 0.104+
Database: Firebase Firestore
Authentication: Firebase Admin SDK
PDF Processing: LlamaParse API
AI Models: Groq API (Llama 4)
Orchestration: LangChain
Language: Python 3.12+
```

### 🎨 **Frontend Stack**
```yaml
Framework: Next.js 16
Language: TypeScript 5.0
Styling: Tailwind CSS 4.0
UI Components: shadcn/ui
State Management: TanStack Query
HTTP Client: Axios
```

### 🤖 **AI Models**
```yaml
Contract Analysis: Llama 4 Scout (17B-16e)
Task Generation: Llama 4 Maverick (17B-128e)
Sprint Planning: Llama 4 Maverick (17B-128e)
Chat Interface: Llama 4 Maverick (17B-128e)
```

### 🔧 **Infrastructure**
```yaml
Database: Firebase Firestore
File Storage: Firebase Storage
API Hosting: Railway/Render
Frontend Hosting: Vercel
CDN: Vercel Edge Network
```

## ⚡ Quick Start

Get Tella up and running in under 5 minutes!

```bash
# Clone the repository
git clone https://github.com/yourusername/Llama-Hackathon-Lambda.git
cd Llama-Hackathon-Lambda

# Start with Docker (Recommended)
docker-compose up -d

# Or follow manual installation below
```

## 🔧 Installation

### 📋 **Prerequisites**

- **Python 3.12+** - Backend runtime
- **Node.js 18+** - Frontend runtime
- **Firebase Account** - Database and storage
- **Groq API Key** - Llama 4 model access
- **LlamaParse API Key** - PDF processing

### 🚀 **Step 1: Clone Repository**

```bash
git clone https://github.com/yourusername/Llama-Hackathon-Lambda.git
cd Llama-Hackathon-Lambda
```

### 🖥️ **Step 2: Backend Setup**

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env.example .env
```

**Configure your `.env` file:**

```env
# AI Services
GROQ_API_KEY=your_groq_api_key_here
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key_here

# Firebase Configuration
FIREBASE_PROJECT_ID=lambda-59fe8
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@lambda-59fe8.iam.gserviceaccount.com
FIREBASE_STORAGE_BUCKET=lambda-59fe8.firebasestorage.app

# Server Configuration
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

**Start the backend server:**

```bash
uvicorn app.main:app --reload
```

✅ Backend running at: `http://localhost:8000`

### 🎨 **Step 3: Frontend Setup**

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

✅ Frontend running at: `http://localhost:3000`

### 🌱 **Step 4: Load Demo Data (Optional)**

```bash
cd backend
source venv/bin/activate
python seed_data.py
```

**Demo data includes:**
- 👥 14 employees across 5 departments
- 📊 3 sample projects with full analysis
- ✅ 22 tasks with smart assignments

## 📖 Usage Guide

### 🚀 **Quick Start Workflow**

#### 1️⃣ **Access the Dashboard**
```
🌐 Open: http://localhost:3000
```

#### 2️⃣ **Upload & Analyze Contract**
- Click **"Upload Contract"** button
- Select your PDF contract file
- Click **"Upload & Analyze"**
- 🤖 AI automatically creates tasks and assigns them to team members

#### 3️⃣ **Review Analysis Results**
- You'll be redirected to the project detail page
- View generated tasks and assignments
- Explore 3 tabs: **Overview**, **Analysis**, **Acceptance Criteria**

#### 4️⃣ **Manage Tasks**
- Click **"View Tasks"** to see all generated tasks
- Review automatic assignments with detailed reasoning
- Use **"Auto Assign"** for any unassigned tasks

#### 5️⃣ **AI Chat Assistant**
Navigate to the chat page and try these commands:

```bash
# Project Management
"Hangi projelerim var?"
"E-Ticaret Platformu projesinin detaylarını göster"
"Mobil Bankacılık projesine geç"

# Team Management
"Backend departmanındaki çalışanları listele"
"Ahmet Yılmaz'ın iş yükü nasıl?"
"Frontend ekibinin mevcut görevleri neler?"

# Task Management
"Bu proje için sprint planı oluştur"
"5 gün tatil var, sprint planını güncelle"
"Görev atamalarını yeniden değerlendir"
```

### 🎯 **Advanced Features**

#### 📊 **Contract Analysis Deep Dive**
- **Risk Assessment:** Comprehensive risk analysis with mitigation strategies
- **Missing Information:** Detailed gap analysis with recommendations
- **Legal Concerns:** Identification of potentially problematic clauses
- **Budget Analysis:** Automatic extraction of financial terms and milestones

#### 🎯 **Smart Task Management**
- **Dependency Mapping:** Automatic task dependency identification
- **Priority Scoring:** AI-powered task prioritization
- **Resource Optimization:** Workload balancing across team members
- **Progress Tracking:** Real-time task status updates

#### 🏃 **Sprint Planning**
- **Intelligent Sprint Creation:** AI-powered sprint planning with optimal task distribution
- **Dynamic Replanning:** Automatic adjustment for holidays and delays
- **Capacity Management:** Team capacity-aware sprint planning

## 🔌 API Documentation

### 🏥 **Health & Status**
```http
GET /health
```
**Response:** Server health status and version information

### 📊 **Projects**
```http
GET    /api/projects              # List all projects
GET    /api/projects/{id}         # Get project details
POST   /api/projects              # Create new project
```

### ✅ **Tasks**
```http
GET    /api/projects/{id}/tasks   # Get project tasks
POST   /api/tasks/{id}/assign     # Assign task to employee
```

### 👥 **Employees**
```http
GET    /api/employees                           # List all employees
GET    /api/employees/department/{dept}        # Get employees by department
GET    /api/employees/workload/{dept}          # Get department workload
```

### 💬 **AI Chat**
```http
POST   /api/chat                    # Send message to AI assistant
GET    /api/chat/history/{session}  # Get chat history
```

### 📄 **Contracts**
```http
POST   /api/contracts/upload                      # Upload PDF contract
POST   /api/contracts/{id}/analyze?auto_assign=true  # Analyze & auto-assign
POST   /api/contracts/{id}/auto-assign-tasks      # Auto-assign existing tasks
GET    /api/contracts                             # List all contracts
GET    /api/contracts/{id}                        # Get contract details
DELETE /api/contracts/{id}                        # Delete contract
```

### 🏃 **Sprints**
```http
POST   /api/sprints/generate          # Generate sprint plan
POST   /api/sprints/replan            # Revise sprint plan
GET    /api/sprints/{project_id}      # Get project sprints
GET    /api/sprints/{project_id}/{sprint_id}  # Get sprint details
```

### 📚 **Interactive Documentation**
- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

## 🚀 Deployment

### 🖥️ **Backend Deployment**

#### **Option 1: Railway (Recommended)**
```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Deploy from backend directory
cd backend
railway init
railway up
```

**Railway Configuration (`railway.json`):**
```json
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

#### **Option 2: Render**
```bash
# 1. Connect your GitHub repository
# 2. Set build command: pip install -r requirements.txt
# 3. Set start command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Required Environment Variables:**
```env
GROQ_API_KEY=your_groq_api_key
LLAMA_CLOUD_API_KEY=your_llama_cloud_api_key
FIREBASE_PROJECT_ID=lambda-59fe8
FIREBASE_PRIVATE_KEY=your_firebase_private_key
FIREBASE_CLIENT_EMAIL=your_firebase_client_email
FIREBASE_STORAGE_BUCKET=lambda-59fe8.firebasestorage.app
CORS_ORIGINS=https://your-frontend-domain.vercel.app
```

### 🎨 **Frontend Deployment**

#### **Vercel (Recommended)**
```bash
# 1. Install Vercel CLI
npm install -g vercel

# 2. Deploy from frontend directory
cd frontend
vercel

# 3. Set environment variables
vercel env add NEXT_PUBLIC_API_URL
```

**Environment Variables:**
```env
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
```

**Build Settings:**
- **Framework:** Next.js
- **Build Command:** `npm run build`
- **Output Directory:** `.next`
- **Install Command:** `npm install`

### 🐳 **Docker Deployment**

```bash
# Build and run with Docker Compose
docker-compose up -d

# Or build individual containers
docker build -t tella-backend ./backend
docker build -t tella-frontend ./frontend
```

## 🐛 Troubleshooting

### 🖥️ **Backend Issues**

#### **Module Import Error**
```bash
# Problem: ModuleNotFoundError: No module named 'app'
# Solution: Ensure you're in the backend directory
cd backend
python -m uvicorn app.main:app --reload
```

#### **Firebase Connection Error**
```bash
# Problem: Firebase connection failed
# Solution: Check environment variables and credentials
cat .env
# Verify Firebase private key has proper newlines (\n)
```

#### **API Rate Limiting**
```bash
# Problem: Groq API rate limit exceeded
# Solution: Check API key or wait for rate limit reset
# Groq Console: https://console.groq.com
```

### 🎨 **Frontend Issues**

#### **404 Not Found Errors**
```bash
# Problem: All pages return 404
# Solution: Clear Next.js cache and restart
rm -rf .next
npm run dev
```

#### **API Connection Refused**
```bash
# Problem: Cannot connect to backend
# Solution: Verify backend is running
curl http://localhost:8000/health
```

#### **Module Resolution Errors**
```bash
# Problem: Module not found errors
# Solution: Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### 🌱 **Demo Data Issues**

#### **Seed Script Fails**
```bash
# Problem: Seed data script fails
# Solution: Activate virtual environment
cd backend
source venv/bin/activate
python seed_data.py
```

### 🔧 **Common Solutions**

#### **Port Already in Use**
```bash
# Kill process using port 8000
lsof -ti:8000 | xargs kill -9
# Or use different port
uvicorn app.main:app --port 8001
```

#### **Firebase Permission Denied**
```bash
# Check Firebase project permissions
# Ensure service account has proper roles
# Verify project ID matches your Firebase project
```

#### **CORS Issues**
```bash
# Add your frontend URL to CORS_ORIGINS
CORS_ORIGINS=http://localhost:3000,https://your-domain.vercel.app
```

## 📁 Project Structure

```
Llama-Hackathon-Lambda/
├── 📁 backend/                    # FastAPI Backend
│   ├── 📁 app/
│   │   ├── 📄 main.py            # FastAPI application
│   │   ├── 📄 firebase_db.py     # Firebase integration
│   │   ├── 📄 orchestrator.py    # AI orchestrator
│   │   ├── 📄 tools.py           # LangChain tools
│   │   ├── 📁 routers/           # API route handlers
│   │   ├── 📁 schemas/           # Pydantic models
│   │   └── 📁 services/          # External service integrations
│   ├── 📄 seed_data.py           # Demo data script
│   ├── 📄 requirements.txt       # Python dependencies
│   └── 📄 .env                   # Environment variables
├── 📁 frontend/                   # Next.js Frontend
│   ├── 📁 app/                   # Next.js app directory
│   │   ├── 📄 page.tsx           # Home page
│   │   ├── 📄 layout.tsx         # Root layout
│   │   ├── 📁 projects/          # Project pages
│   │   ├── 📁 chat/              # AI chat interface
│   │   ├── 📁 employees/         # Employee management
│   │   └── 📁 contracts/         # Contract upload
│   ├── 📁 components/            # React components
│   │   ├── 📁 ui/                # shadcn/ui components
│   │   └── 📁 dashboard/         # Dashboard components
│   ├── 📁 lib/                   # Utility functions
│   │   ├── 📄 api.ts             # API client
│   │   └── 📄 utils.ts           # Helper functions
│   └── 📁 hooks/                 # Custom React hooks
└── 📄 README.md                  # Project documentation
```

## 🗺️ Roadmap

### ✅ **Completed Features**

#### **Sprint 1-3: Core Foundation**
- ✅ Contract analysis with LlamaParse
- ✅ AI-powered task generation
- ✅ Smart auto-assignment system
- ✅ Chat interface with 12 tools
- ✅ Employee management system
- ✅ Demo data and seeding

#### **Sprint 4: Enhanced UX**
- ✅ Toast notification system
- ✅ AI-powered sprint planning
- ✅ Dynamic sprint revision
- ✅ Complete API documentation
- ✅ Firebase integration
- ✅ Tool orchestration

#### **Sprint 5: Automation**
- ✅ Automatic task assignment during contract analysis
- ✅ AI-driven tech stack matching
- ✅ Workload balancing algorithms
- ✅ Assignment reasoning system

#### **Sprint 6: Advanced AI v2.0**
- ✅ Intelligent project name extraction
- ✅ Enhanced missing information detection (5-10 items)
- ✅ Comprehensive risk analysis (5-8 risks, 6 categories)
- ✅ Legal concern identification
- ✅ Budget and payment terms extraction
- ✅ Scope-based task generation (8-15 tasks guaranteed)
- ✅ Advanced AI prompts (82 + 90 lines)

### 🚀 **Upcoming Features**

- [ ] **User Authentication & Authorization**
- [ ] **Multi-Company Support**
- [ ] **Advanced Sprint Analytics**
- [ ] **Change Order Management**
- [ ] **Real-time Collaboration**
- [ ] **Email Notifications**
- [ ] **Mobile Application**
- [ ] **Advanced Analytics Dashboard**
- [ ] **Integration APIs (Jira, Slack, etc.)**
- [ ] **Custom AI Model Training**

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Make your changes**
4. **Commit your changes**
   ```bash
   git commit -m 'Add amazing feature'
   ```
5. **Push to the branch**
   ```bash
   git push origin feature/amazing-feature
   ```
6. **Open a Pull Request**

### 📋 **Contribution Guidelines**

- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass
- Follow conventional commit messages

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 👥 Team

- **🤖 AI Assistant** - Full Stack Development & Architecture
- **🧠 Llama 4 Scout** - Contract Analysis & Risk Assessment
- **⚡ Llama 4 Maverick** - Task Generation & Sprint Planning

## 🆘 Support

Need help? We're here for you:

- 📧 **Email:** support@tella-ai.com
- 💬 **Discord:** [Join our community](https://discord.gg/tella-ai)
- 📚 **Documentation:** [docs.tella-ai.com](https://docs.tella-ai.com)
- 🐛 **Issues:** [GitHub Issues](https://github.com/yourusername/Llama-Hackathon-Lambda/issues)

## 🙏 Acknowledgments

Special thanks to our amazing partners and open-source contributors:

- [**Groq**](https://groq.com/) - Llama 4 model access and inference
- [**LlamaParse**](https://www.llamaindex.ai/) - Advanced PDF parsing capabilities
- [**Firebase**](https://firebase.google.com/) - Backend infrastructure and database
- [**Vercel**](https://vercel.com/) - Frontend hosting and deployment
- [**shadcn/ui**](https://ui.shadcn.com/) - Beautiful UI component library
- [**Next.js**](https://nextjs.org/) - React framework
- [**FastAPI**](https://fastapi.tiangolo.com/) - Python web framework

---

<div align="center">

**🚀 Made with ❤️ using Llama 4 Scout & Maverick**

[![Star this repo](https://img.shields.io/github/stars/yourusername/Llama-Hackathon-Lambda?style=social)](https://github.com/yourusername/Llama-Hackathon-Lambda)
[![Fork this repo](https://img.shields.io/github/forks/yourusername/Llama-Hackathon-Lambda?style=social)](https://github.com/yourusername/Llama-Hackathon-Lambda/fork)

</div>
