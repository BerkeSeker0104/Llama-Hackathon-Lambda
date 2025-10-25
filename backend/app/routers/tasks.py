from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, list_tasks, assign_task_to_employee

router = APIRouter()
db_client = FirebaseDatabase()

class TaskAssignmentRequest(BaseModel):
    task_title: str
    project_id: Optional[str] = None

class TaskAssignmentResponse(BaseModel):
    status: str
    task_title: str
    assigned_to: str
    reason: str

@router.get("/")
async def get_tasks(project_id: Optional[str] = None):
    """
    Proje görevlerini listele.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # list_tasks tool'unu çağır
        result = list_tasks(project_id)
        import json
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev listesi getirme hatası: {str(e)}")

@router.get("/{task_id}")
async def get_task(task_id: str):
    """
    Belirli bir görevin detaylarını getir.
    """
    try:
        # Task'ı bul
        tasks_ref = db_client.db.collection('tasks').where('task_id', '==', task_id).stream()
        tasks = [doc.to_dict() for doc in tasks_ref]
        
        if not tasks:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")
        
        return tasks[0]
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev detayı getirme hatası: {str(e)}")

@router.post("/assign", response_model=TaskAssignmentResponse)
async def assign_task(request: TaskAssignmentRequest):
    """
    Görevi en uygun çalışana ata.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # assign_task_to_employee tool'unu çağır
        result = assign_task_to_employee(request.task_title, request.project_id)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return TaskAssignmentResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev atama hatası: {str(e)}")

@router.put("/{task_id}/status")
async def update_task_status(task_id: str, status: str):
    """
    Görev durumunu güncelle.
    """
    try:
        # Task'ı bul ve güncelle
        task_ref = db_client.db.collection('tasks').where('task_id', '==', task_id).stream()
        tasks = [doc for doc in task_ref]
        
        if not tasks:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")
        
        # Task'ı güncelle
        task_doc = tasks[0]
        task_doc.reference.update({"status": status})
        
        return {"message": f"Görev durumu güncellendi: {status}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev durumu güncelleme hatası: {str(e)}")

@router.delete("/{task_id}")
async def delete_task(task_id: str):
    """
    Görevi sil.
    """
    try:
        # Task'ı bul ve sil
        task_ref = db_client.db.collection('tasks').where('task_id', '==', task_id).stream()
        tasks = [doc for doc in task_ref]
        
        if not tasks:
            raise HTTPException(status_code=404, detail="Görev bulunamadı")
        
        # Task'ı sil
        tasks[0].reference.delete()
        
        return {"message": f"Görev silindi: {task_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Görev silme hatası: {str(e)}")
