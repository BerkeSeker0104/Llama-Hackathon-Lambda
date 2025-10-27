from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from app.services.llamaparse_service import LlamaParseService
from app.services.groq_service import GroqService
from app.firebase_db import FirebaseDatabase
from app.orchestrator import ChatOrchestrator
from app.groq_client import GroqAgent
from app.routers import sprints, contracts, projects, tasks, employees, chat
from pydantic import BaseModel
from typing import Optional, Dict, Any
import tempfile
import os
import uuid
import json
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

# Include routers
app.include_router(projects.router, prefix="/api/projects", tags=["projects"])
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(employees.router, prefix="/api/employees", tags=["employees"])
app.include_router(sprints.router, prefix="/api/sprints", tags=["sprints"])
app.include_router(contracts.router, prefix="/api/contracts", tags=["contracts"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])

# Pydantic Models

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_confirmation: Optional[bool] = False
    confirmation_data: Optional[Dict[str, Any]] = None

# ROOT ENDPOINT

@app.get("/")
async def root():
    return {
        "message": "Product Manager AI Assistant API is running!",
        "version": "1.0.0",
        "features": [
            "PDF Parsing (LlamaParse)",
            "Project Analysis (Llama 4 Scout)",
            "Critical Analysis (Eksikler, Riskler, Çelişkiler)",
            "Task Generation (Llama 4 Maverick)",
            "Auto-Assignment (Llama 4 Maverick)",
            "Sprint Planning (Llama 4 Maverick)",
            "Dynamic Sprint Revision (Tatil, Gecikme Yönetimi)",
            "Chat Orchestrator (12 Tools)"
        ],
        "ai_models": {
            "analysis": "meta-llama/llama-4-scout-17b-16e-instruct",
            "task_generation": "meta-llama/llama-4-maverick-17b-128e-instruct",
            "assignment": "meta-llama/llama-4-maverick-17b-128e-instruct",
            "sprint_planning": "meta-llama/llama-4-maverick-17b-128e-instruct"
        }
    }

# CONTRACT ENDPOINTS
# Note: Contract endpoints moved to routers/contracts.py
# All contract operations are now handled by the contracts router


# CHAT ENDPOINT (ORCHESTRATOR)

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_assistant(request: ChatRequest):
    """
    Orchestrator chat endpoint.
    Uses all 10 tools from prototype.
    """
    session_id = request.session_id or f"session_{uuid.uuid4().hex[:8]}"
    
    try:
        print(f"[API] Chat request: {request.message[:50]}...")
        response_data = orchestrator.handle_message(session_id, request.message)
        
        return ChatResponse(
            response=response_data.get("response", "Bir sorun oluştu."),
            session_id=session_id,
            requires_confirmation=response_data.get("requires_confirmation", False),
            confirmation_data=response_data.get("confirmation_data", None)
        )
        
    except Exception as e:
        print(f"[API ERROR] Chat failed: {e}")
        raise HTTPException(500, f"Chat failed: {str(e)}")


# PROJECT ENDPOINTS

@app.get("/api/projects")
async def list_projects():
    """
    List all projects.
    """
    try:
        projects = db.list_projects()
        return projects
    except Exception as e:
        raise HTTPException(500, f"Failed to list projects: {str(e)}")


@app.get("/api/projects/{project_id}")
async def get_project_details(project_id: str):
    """
    Get project details by ID.
    """
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    return project


@app.get("/api/projects/{project_id}/tasks")
async def get_project_tasks(project_id: str):
    """
    Get all tasks for a project.
    """
    try:
        tasks = db.get_tasks(project_id)
        return tasks
    except Exception as e:
        raise HTTPException(500, f"Failed to get tasks: {str(e)}")


@app.post("/api/tasks/{task_id}/assign")
async def assign_task_to_best_employee(task_id: str):
    """
    Automatically assign a task to the most suitable employee.
    Uses Llama 4 Maverick to find the best match.
    """
    try:
        # Task'ı bul
        all_projects = db.list_projects()
        task = None
        task_project_id = None
        
        for project in all_projects:
            project_id = project.get("project_id")
            project_tasks = db.get_tasks(project_id)
            for t in project_tasks:
                if t.get("task_id") == task_id:
                    task = t
                    task_project_id = project_id
                    break
            if task:
                break
        
        if not task:
            raise HTTPException(404, f"Task not found: {task_id}")
        
        # Check if task is already assigned
        if task.get("assigned_to"):
            return {
                "message": "Task already assigned",
                "task_id": task_id,
                "assigned_to": task.get("assigned_to")
            }
        
        # Get all employees
        employees = db.list_employees()
        
        if not employees:
            raise HTTPException(400, "No employees found in database")
        
        # Find best employee using Groq
        from app.tools import TASK_ASSIGNMENT_PROMPT
        from groq import Groq
        import os
        
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        user_prompt = f"""
TASK INFORMATION:
- Task ID: {task.get('task_id')}
- Title: {task.get('title', task.get('task_title', 'N/A'))}
- Detail: {task.get('detail', task.get('task_detail', 'N/A'))}
- Required Technologies: {task.get('required_stack', task.get('task_stack', []))}
- Department: {task.get('department', 'N/A')}

AVAILABLE EMPLOYEES:
{json.dumps(employees, indent=2, ensure_ascii=False)}

Please assign this task to the MOST SUITABLE employee. Respond only in JSON format.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_ASSIGNMENT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        assignment_result = json.loads(completion.choices[0].message.content)
        
        # Find employee information
        assigned_employee = None
        for emp in employees:
            if emp.get("employee_id") == assignment_result.get("assigned_employee_id"):
                assigned_employee = emp
                break
        
        if not assigned_employee:
            raise HTTPException(400, f"Employee not found: {assignment_result.get('assigned_employee_id')}")
        
        # Update task
        task["status"] = "assigned"
        task["assigned_to"] = {
            "employee_id": assigned_employee.get("employee_id"),
            "name": assigned_employee.get("name"),
            "department": assigned_employee.get("department"),
            "seniority": assigned_employee.get("seniority")
        }
        task["assignment_reason"] = assignment_result.get("assignment_reason", "Automatically assigned by AI")
        
        # Save to database
        db.save_tasks(task_project_id, [task])
        
        print(f"[API] Task assigned successfully: {task_id} -> {assigned_employee.get('name')}")
        
        return {
            "status": "success",
            "task_id": task_id,
            "assigned_to": task["assigned_to"],
            "assignment_reason": task["assignment_reason"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[API ERROR] Task assignment failed: {e}")
        raise HTTPException(500, f"Task assignment failed: {str(e)}")


# EMPLOYEE ENDPOINTS

@app.get("/api/employees")
async def list_employees():
    """
    List all employees.
    """
    try:
        employees = db.list_employees()
        return employees
    except Exception as e:
        raise HTTPException(500, f"Failed to list employees: {str(e)}")


@app.get("/api/employees/{employee_id}")
async def get_employee_details(employee_id: str):
    """
    Get employee details by ID.
    """
    employee = db.get_employee(employee_id)
    if not employee:
        raise HTTPException(404, "Employee not found")
    
    return employee


@app.get("/api/employees/department/{department}")
async def get_employees_by_department(department: str):
    """
    Get employees by department.
    """
    try:
        employees = db.get_employees_by_department(department)
        return employees
    except Exception as e:
        raise HTTPException(500, f"Failed to get employees by department: {str(e)}")


# HEALTH CHECK

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
