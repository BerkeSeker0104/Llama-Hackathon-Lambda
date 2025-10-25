from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, generate_sprint_plan, replan_sprints

router = APIRouter()
db_client = FirebaseDatabase()

class SprintGenerationRequest(BaseModel):
    project_id: Optional[str] = None
    sprint_duration_weeks: int = 2

class SprintReplanRequest(BaseModel):
    project_id: Optional[str] = None
    vacation_days: int = 0
    delays: int = 0

class SprintResponse(BaseModel):
    status: str
    sprint_id: str
    message: str
    plan: Dict[str, Any]

class SprintReplanResponse(BaseModel):
    status: str
    sprint_id: str
    message: str
    new_plan: Dict[str, Any]
    changes: Dict[str, int]

@router.get("/{project_id}")
async def get_sprints(project_id: str):
    """
    Projeye ait sprintleri listele.
    """
    try:
        sprints = db_client.get_sprints(project_id)
        return {"sprints": sprints}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint listesi getirme hatası: {str(e)}")

@router.get("/{project_id}/{sprint_id}")
async def get_sprint(project_id: str, sprint_id: str):
    """
    Belirli bir sprintin detaylarını getir.
    """
    try:
        sprints = db_client.get_sprints(project_id)
        sprint = next((s for s in sprints if s.get("sprint_id") == sprint_id), None)
        
        if not sprint:
            raise HTTPException(status_code=404, detail="Sprint bulunamadı")
        
        return sprint
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint detayı getirme hatası: {str(e)}")

@router.post("/generate", response_model=SprintResponse)
async def generate_sprint(request: SprintGenerationRequest):
    """
    Sprint planı oluştur.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # generate_sprint_plan tool'unu çağır
        result = generate_sprint_plan(request.project_id, request.sprint_duration_weeks)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return SprintResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint planlama hatası: {str(e)}")

@router.post("/replan", response_model=SprintReplanResponse)
async def replan_sprint(request: SprintReplanRequest):
    """
    Sprint planını yeniden düzenle.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # replan_sprints tool'unu çağır
        result = replan_sprints(request.project_id, request.vacation_days, request.delays)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return SprintReplanResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint yeniden planlama hatası: {str(e)}")

@router.put("/{sprint_id}/tasks")
async def update_sprint_tasks(sprint_id: str, tasks: List[str]):
    """
    Sprint görevlerini güncelle.
    """
    try:
        # Sprint'i bul
        sprint_ref = db_client.db.collection('sprints').document(sprint_id)
        sprint_doc = sprint_ref.get()
        
        if not sprint_doc.exists:
            raise HTTPException(status_code=404, detail="Sprint bulunamadı")
        
        # Sprint planını güncelle
        sprint_data = sprint_doc.to_dict()
        if "plan" in sprint_data:
            # Görevleri sprintlere dağıt
            sprint_data["plan"]["sprint1"]["tasks"] = tasks[:len(tasks)//2] if len(tasks) > 1 else tasks
            sprint_data["plan"]["sprint2"]["tasks"] = tasks[len(tasks)//2:] if len(tasks) > 1 else []
            sprint_data["plan"]["backlog"] = []
        
        sprint_ref.update(sprint_data)
        
        return {"message": f"Sprint görevleri güncellendi: {sprint_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint görev güncelleme hatası: {str(e)}")

@router.delete("/{sprint_id}")
async def delete_sprint(sprint_id: str):
    """
    Sprint'i sil.
    """
    try:
        # Sprint'i sil
        db_client.db.collection('sprints').document(sprint_id).delete()
        
        return {"message": f"Sprint silindi: {sprint_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint silme hatası: {str(e)}")
