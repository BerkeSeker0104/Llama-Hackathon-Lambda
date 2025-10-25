from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services.llamaparse_service import LlamaParseService
from app.services.groq_service import GroqService
from app.firebase_db import FirebaseDatabase
from app.orchestrator import ChatOrchestrator
from app.groq_client import GroqAgent
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import uuid
from datetime import datetime

app = FastAPI(
    title="Product Manager AI Assistant API",
    description="AI-powered project analysis, task management, and resource allocation - EXACT prototype implementation",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services (singleton pattern)
try:
    db = FirebaseDatabase()
    llamaparse = LlamaParseService()
    groq_service = GroqService()
    agent = GroqAgent()
    orchestrator = ChatOrchestrator(db_client=db, agent_client=agent)
    print("[Main] All services initialized successfully!")
except Exception as e:
    print(f"[Main ERROR] Service initialization failed: {e}")
    raise

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

# --- ROOT ENDPOINT ---

@app.get("/")
async def root():
    return {
        "message": "Product Manager AI Assistant API is running!",
        "version": "1.0.0",
        "features": [
            "PDF Parsing (LlamaParse)",
            "Project Analysis (Llama 4 Scout)",
            "Task Generation (Llama 4 Maverick)",
            "Auto-Assignment (Llama 4 Maverick)",
            "Chat Orchestrator"
        ]
    }

# --- CONTRACT ENDPOINTS (PROTOTIP WORKFLOW) ---

@app.post("/api/contracts/upload-and-analyze")
async def upload_and_analyze_contract(file: UploadFile = File(...)):
    """
    PROTOTIP WORKFLOW (EXACT):
    1. PDF upload
    2. LlamaParse parse (Cell 3)
    3. Groq analyze (Cell 6)
    4. Save to Firebase
    
    Demo PDF: 4-Mesut_Kara_Mobil_Uygulama_Sozlesmesi.pdf
    """
    if file.content_type != "application/pdf":
        raise HTTPException(400, "Only PDF files are allowed")
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        print(f"[API] Processing PDF: {file.filename}")
        
        # Step 1: Parse with LlamaParse (EXACT prototype Cell 3)
        parsed_text = llamaparse.parse_pdf(tmp_path)
        
        # Step 2: Analyze with Groq (EXACT prototype Cell 6)
        analysis = groq_service.analyze_project(parsed_text)
        
        # Step 3: Save to Firebase
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        db.save_contract(contract_id, {
            "contract_name": file.filename,
            "parsed_text": parsed_text,
            "analysis": analysis,
            "status": "analyzed",
            "created_at": datetime.utcnow().isoformat()
        })
        
        print(f"[API] Contract analyzed successfully: {contract_id}")
        
        return {
            "contract_id": contract_id,
            "analysis": analysis,
            "message": "Contract analyzed successfully",
            "parsed_text_length": len(parsed_text)
        }
        
    except Exception as e:
        print(f"[API ERROR] Contract analysis failed: {e}")
        raise HTTPException(500, f"Analysis failed: {str(e)}")
    
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@app.post("/api/contracts/{contract_id}/generate-tasks")
async def generate_tasks_from_contract(contract_id: str):
    """
    PROTOTIP WORKFLOW (EXACT):
    1. Get contract analysis
    2. Generate tasks with Groq (Cell 9)
    3. Save tasks to Firebase
    """
    contract = db.get_contract(contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    
    try:
        print(f"[API] Generating tasks for contract: {contract_id}")
        
        # Generate tasks (EXACT prototype Cell 9)
        tasks = groq_service.generate_tasks(contract["analysis"])
        
        # Save tasks
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        db.save_project(project_id, contract["analysis"])
        db.save_tasks(project_id, tasks)
        
        print(f"[API] Tasks generated successfully: {len(tasks)} tasks")
        
        return {
            "project_id": project_id,
            "contract_id": contract_id,
            "tasks": tasks,
            "total_tasks": len(tasks),
            "message": "Tasks generated successfully"
        }
        
    except Exception as e:
        print(f"[API ERROR] Task generation failed: {e}")
        raise HTTPException(500, f"Task generation failed: {str(e)}")


@app.get("/api/contracts")
async def list_contracts():
    """Tüm sözleşmeleri listeler."""
    try:
        contracts = db.list_contracts()
        return {
            "total_contracts": len(contracts),
            "contracts": contracts
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to list contracts: {str(e)}")


@app.get("/api/contracts/{contract_id}")
async def get_contract_details(contract_id: str):
    """Sözleşme detaylarını getirir."""
    contract = db.get_contract(contract_id)
    if not contract:
        raise HTTPException(404, "Contract not found")
    
    return contract


# --- CHAT ENDPOINT (ORCHESTRATOR) ---

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Orchestrator chat endpoint
    Uses all 10 tools from prototype
    """
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    
    try:
        print(f"[API] Chat request: {request.message[:50]}...")
        response = orchestrator.handle_message(session_id, request.message)
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
        
    except Exception as e:
        print(f"[API ERROR] Chat failed: {e}")
        raise HTTPException(500, f"Chat failed: {str(e)}")


# --- PROJECT ENDPOINTS ---

@app.get("/api/projects")
async def list_projects():
    """Tüm projeleri listeler."""
    try:
        projects = db.list_projects()
        return {
            "total_projects": len(projects),
            "projects": projects
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to list projects: {str(e)}")


@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    """Proje detaylarını getirir."""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    return project


@app.get("/api/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str):
    """Proje görevlerini listeler."""
    try:
        tasks = db.get_tasks(project_id)
        return {
            "project_id": project_id,
            "total_tasks": len(tasks),
            "tasks": tasks
        }
    except Exception as e:
        raise HTTPException(500, f"Failed to get tasks: {str(e)}")


# --- HEALTH CHECK ---

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "firebase": "connected",
            "llamaparse": "ready",
            "groq": "ready",
            "orchestrator": "ready"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
