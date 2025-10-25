from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, analyze_project_text, generate_tasks_from_project, list_projects, get_project_details

router = APIRouter()
db_client = FirebaseDatabase()

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
        inject_dependencies(db_client, "api_session")
        
        # list_projects tool'unu çağır
        result = list_projects()
        import json
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje listesi getirme hatası: {str(e)}")

@router.get("/{project_id}")
async def get_project(project_id: str):
    """
    Belirli bir projenin detaylarını getir.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # get_project_details tool'unu çağır
        result = get_project_details(project_id)
        import json
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje detayı getirme hatası: {str(e)}")

@router.post("/analyze", response_model=ProjectAnalysisResponse)
async def analyze_project(request: ProjectAnalysisRequest):
    """
    Proje dokümanını analiz et.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # analyze_project_text tool'unu çağır
        result = analyze_project_text(request.project_text, request.project_name)
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
        inject_dependencies(db_client, "api_session")
        
        # generate_tasks_from_project tool'unu çağır
        result = generate_tasks_from_project(project_id)
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
        project = db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
        
        # Aktif projeyi ayarla
        db_client.set_active_project("api_session", project_id)
        
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
        project = db_client.get_project(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proje bulunamadı")
        
        # Projeyi sil
        db_client.db.collection('projects').document(project_id).delete()
        
        return {"message": f"Proje silindi: {project_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proje silme hatası: {str(e)}")
