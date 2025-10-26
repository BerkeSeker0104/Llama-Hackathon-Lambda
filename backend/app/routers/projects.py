from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, analyze_project_text, generate_tasks_from_project, list_projects, get_project_details, predict_project_delays
import logging

logger = logging.getLogger("uvicorn.error")
router = APIRouter()

_db_client = None
def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

class ProjectAnalysisRequest(BaseModel):
    project_text: str
    project_name: str = "New Project"

class ProjectAnalysisResponse(BaseModel):
    status: str
    project_id: str
    message: str
    analysis: Dict[str, Any]

class TaskGenerationResponse(BaseModel):
    status: str
    project_id: str
    total_tasks: int
    tasks: List[Dict[str, Any]]

@router.get("/")
async def get_projects():
    """
    Tüm projeleri listele.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # list_projects tool'unu çağır (LangChain tool - .invoke() kullan)
        result = list_projects.invoke({})
        import json
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje listesi getirme hatası: {str(e)}")


# --- ÖNEMLİ: Özel path'leri /{project_id} catch-all'dan ÖNCE tanımla ---

@router.get("/{project_id}/risk-analysis")
async def get_project_risk_analysis(project_id: str):
    """
    Proje için gecikme riski analizi yapar.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # predict_project_delays tool'unu çağır
        result = predict_project_delays.invoke({
            "project_id": project_id
        })
        
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return result_data
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Proje risk analizi hatası: {str(e)}\n{traceback.format_exc()}"
        print(f"[ERROR] {error_detail}")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{project_id}/calendar-view")
async def get_project_calendar_view(project_id: str):
    """
    Projenin tüm sprint ve görevlerini takvim formatında getirir.
    """
    try:
        # Projeyi kontrol et
        project = get_db().get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
        
        # Sprint'leri al
        sprints = get_db().get_sprints(project_id)
        if not sprints:
            return {
                "project_id": project_id,
                "project_name": project.get("project_name"),
                "events": [],
                "message": "Bu proje için sprint planı bulunamadı"
            }
        
        # En son sprint'i al
        latest_sprint = sprints[0]
        sprint_id = latest_sprint.get("sprint_id")
        
        # Sprint takvim olaylarını al (sprints router'dan kodu tekrar kullan)
        sprint_plan = latest_sprint.get("plan", {})
        sprints_list = sprint_plan.get("sprints", [])
        tasks = get_db().get_tasks(project_id)
        
        events = []
        import datetime
        
        for sp in sprints_list:
            sprint_number = sp.get("sprint_number", 1)
            sprint_name = sp.get("sprint_name", f"Sprint {sprint_number}")
            start_date = latest_sprint.get("start_date") or datetime.date.today().isoformat()
            duration_weeks = sp.get("duration_weeks", 2)
            
            start = datetime.datetime.fromisoformat(start_date)
            end = start + datetime.timedelta(weeks=duration_weeks * sprint_number)
            start_offset = start + datetime.timedelta(weeks=duration_weeks * (sprint_number - 1))
            
            events.append({
                "id": f"{sprint_id}_{sprint_number}",
                "title": sprint_name,
                "start": start_offset.isoformat(),
                "end": end.isoformat(),
                "type": "sprint",
                "status": latest_sprint.get("status", "planned"),
                "description": sp.get("focus", "")
            })
            
            # Sprint task'ları ekle
            sprint_tasks = sp.get("tasks", [])
            for task_title in sprint_tasks:
                task = next((t for t in tasks if t.get("task_title", t.get("title")) == task_title), None)
                if task:
                    task_start = task.get("start_date", start_offset.isoformat())
                    task_end = task.get("due_date", (start_offset + datetime.timedelta(days=7)).isoformat())
                    
                    events.append({
                        "id": task.get("task_id"),
                        "title": task_title,
                        "start": task_start,
                        "end": task_end,
                        "type": "task",
                        "status": task.get("status", "pending"),
                        "priority": task.get("priority", "medium"),
                        "assignee": task.get("task_attended_to", "Atanmamış")
                    })
        
        return {
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "total_events": len(events),
            "events": events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje takvim görünümü getirme hatası: {str(e)}")


@router.get("/{project_id}")
async def get_project(project_id: str):
    """
    Belirli bir projenin detaylarını getir.
    """
    try:
        logger.error(f"[DEBUG] get_project called for: {project_id}")
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # get_project_details tool'unu çağır (LangChain tool olduğu için .invoke() kullan)
        result = get_project_details.invoke({"project_id": project_id})
        logger.error(f"[DEBUG] get_project_details returned: {type(result)}")
        import json
        parsed = json.loads(result)
        logger.error(f"[DEBUG] Returning project data")
        return parsed
        
    except Exception as e:
        import traceback
        logger.error(f"[ERROR] get_project failed: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Proje detayı getirme hatası: {str(e)}")

@router.post("/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project(request: ProjectAnalysisRequest):
    """
    Proje dokümanını analiz et.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # analyze_project_text tool'unu çağır (LangChain tool - .invoke() kullan)
        result = analyze_project_text.invoke({
            "project_text": request.project_text,
            "project_name": request.project_name
        })
        import json
        result_data = json.loads(result)
        
        return ProjectAnalysisResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje analiz hatası: {str(e)}")

@router.post("/{project_id}/generate-tasks", response_model=TaskGenerationResponse)
async def generate_tasks(project_id: str):
    """
    Projeden görev listesi oluştur.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # generate_tasks_from_project tool'unu çağır (LangChain tool - .invoke() kullan)
        result = generate_tasks_from_project.invoke({"project_id": project_id})
        import json
        result_data = json.loads(result)
        
        return TaskGenerationResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev oluşturma hatası: {str(e)}")

@router.put("/{project_id}/active")
async def set_active_project(project_id: str):
    """
    Aktif projeyi ayarla.
    """
    try:
        # Proje var mı kontrol et
        project = get_db().get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
        
        # Aktif projeyi ayarla
        get_db().set_active_project("api_session", project_id)
        
        return {"message": f"Aktif proje ayarlandı: {project_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Aktif proje ayarlama hatası: {str(e)}")

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """
    Projeyi sil.
    """
    try:
        # Proje var mı kontrol et
        project = get_db().get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
        
        # Projeyi sil
        get_db().db.collection('projects').document(project_id).delete()
        
        return {"message": f"Proje silindi: {project_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje silme hatası: {str(e)}")
