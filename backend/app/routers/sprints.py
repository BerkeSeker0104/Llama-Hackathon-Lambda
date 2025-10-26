from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, generate_sprint_plan, replan_sprints, analyze_sprint_health
import logging

logger = logging.getLogger("uvicorn.error")

router = APIRouter()

# Lazy loading - sadece ihtiyaç olduğunda oluştur
_db_client = None

def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

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

@router.get("/project/{project_id}")
async def get_sprints(project_id: str):
    """
    Projeye ait sprintleri listele.
    """
    try:
        sprints = get_db().get_sprints(project_id)
        return {"sprints": sprints}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint listesi getirme hatası: {str(e)}")

@router.get("/project/{project_id}/sprint/{sprint_id}")
async def get_sprint(project_id: str, sprint_id: str):
    """
    Belirli bir sprintin detaylarını getir.
    """
    try:
        sprints = get_db().get_sprints(project_id)
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
        inject_dependencies(get_db(), "api_session")
        
        # generate_sprint_plan tool'unu çağır (LangChain tool olduğu için .invoke() kullan)
        result = generate_sprint_plan.invoke({
            "project_id": request.project_id,
            "sprint_duration_weeks": request.sprint_duration_weeks
        })
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
        inject_dependencies(get_db(), "api_session")
        
        # replan_sprints tool'unu çağır (LangChain tool olduğu için .invoke() kullan)
        result = replan_sprints.invoke({
            "project_id": request.project_id,
            "vacation_days": request.vacation_days,
            "delays": request.delays
        })
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
        sprint_ref = get_db().db.collection('sprints').document(sprint_id)
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
        get_db().db.collection('sprints').document(sprint_id).delete()
        
        return {"message": f"Sprint silindi: {sprint_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sprint silme hatası: {str(e)}")


# --- NEW DYNAMIC SPRINT MANAGEMENT ENDPOINTS ---

@router.get("/test-endpoint")
async def test_endpoint():
    """Test endpoint"""
    logger.error("TEST ENDPOINT CALLED!")
    return {"status": "ok", "message": "Test successful"}

@router.get("/{sprint_id}/health")
async def get_sprint_health(sprint_id: str, project_id: Optional[str] = None):
    """
    Sprint sağlık durumunu analiz eder ve döndürür.
    """
    logger.error(f"========== HEALTH CHECK START: {sprint_id} ==========")
    try:
        logger.error(f"[DEBUG] Getting health for sprint: {sprint_id}, project: {project_id}")
        
        # Eğer project_id verilmemişse, sprint'ten al
        if not project_id:
            sprint = get_db().get_sprint(sprint_id)
            if sprint:
                project_id = sprint.get("project_id")
                logger.error(f"[DEBUG] Retrieved project_id from sprint: {project_id}")
        
        if not project_id:
            logger.error(f"[ERROR] No project_id available for health check")
            raise HTTPException(status_code=400, detail="project_id gerekli")
        
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # analyze_sprint_health tool'unu çağır
        logger.error(f"[DEBUG] Calling analyze_sprint_health tool")
        result = analyze_sprint_health.invoke({
            "project_id": project_id,
            "sprint_id": sprint_id
        })
        
        logger.error(f"[DEBUG] Health analysis result received")
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            logger.error(f"[ERROR] Health analysis returned error: {result_data['error']}")
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return result_data
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Sprint sağlık analizi hatası: {str(e)}"
        full_traceback = traceback.format_exc()
        logger.error(f"\n{'='*80}")
        logger.error(f"[ERROR] HEALTH ANALYSIS FAILED")
        logger.error(f"Sprint ID: {sprint_id}")
        logger.error(f"Project ID: {project_id}")
        logger.error(f"Error: {error_detail}")
        logger.error(f"{'='*80}")
        logger.error(full_traceback)
        logger.error(f"{'='*80}\n")
        raise HTTPException(status_code=500, detail=error_detail)


@router.get("/{sprint_id}/calendar-events")
async def get_sprint_calendar_events(sprint_id: str):
    """
    Sprint'e ait takvim olaylarını getirir (sprint ve task'lar).
    """
    logger.error(f"========== CALENDAR EVENTS START: {sprint_id} ==========")
    try:
        logger.error(f"[DEBUG] Getting calendar events for sprint: {sprint_id}")
        
        # Sprint bilgilerini al
        sprint = get_db().get_sprint(sprint_id)
        if not sprint:
            logger.error(f"[ERROR] Sprint not found: {sprint_id}")
            raise HTTPException(status_code=404, detail=f"Sprint bulunamadı: {sprint_id}")
        
        logger.error(f"[DEBUG] Sprint found: {sprint.get('sprint_id')}")
        
        project_id = sprint.get("project_id")
        if not project_id:
            logger.error(f"[ERROR] Sprint has no project_id: {sprint}")
            raise HTTPException(status_code=400, detail="Sprint proje bilgisi eksik")
        
        logger.error(f"[DEBUG] Project ID: {project_id}")
        
        # Sprint planını al
        sprint_plan = sprint.get("plan")
        if not sprint_plan:
            logger.error(f"[WARNING] Sprint has no plan, returning empty events")
            return {
                "sprint_id": sprint_id,
                "project_id": project_id,
                "total_events": 0,
                "events": [],
                "message": "Bu sprint için plan bulunamadı"
            }
        
        logger.error(f"[DEBUG] Sprint plan found: {list(sprint_plan.keys())}")
        sprints_list = sprint_plan.get("sprints", [])
        
        if not sprints_list:
            logger.error(f"[WARNING] Sprint plan has no sprints array")
            return {
                "sprint_id": sprint_id,
                "project_id": project_id,
                "total_events": 0,
                "events": [],
                "message": "Sprint planında sprint bilgisi bulunamadı"
            }
        
        logger.error(f"[DEBUG] Found {len(sprints_list)} sprints in plan")
        
        # Görevleri al
        tasks = get_db().get_tasks(project_id) or []
        logger.error(f"[DEBUG] Found {len(tasks)} tasks for project")
        if tasks:
            # İlk task'ın field'larını göster
            first_task = tasks[0]
            logger.error(f"[DEBUG] First task fields: {list(first_task.keys())}")
            logger.error(f"[DEBUG] First task title: '{first_task.get('title')}'")
            logger.error(f"[DEBUG] First task assigned_to (type: {type(first_task.get('assigned_to')).__name__}): {first_task.get('assigned_to')}")
            logger.error(f"[DEBUG] First task task_attended_to (type: {type(first_task.get('task_attended_to')).__name__}): {first_task.get('task_attended_to')}")
            # Tüm task isimlerini göster
            task_names = [t.get("task_title") or t.get("title") or t.get("task_id") for t in tasks]
            logger.error(f"[DEBUG] All task names: {task_names}")
        
        # Takvim olaylarını oluştur
        events = []
        
        import datetime
        # Sprint genel başlangıç tarihi
        sprint_start_date = sprint.get("start_date")
        if not sprint_start_date:
            sprint_start_date = datetime.date.today().isoformat()
            logger.error(f"[DEBUG] No start_date found, using today: {sprint_start_date}")
        else:
            logger.error(f"[DEBUG] Sprint start_date: {sprint_start_date}")
        
        # Sprint event'lerini ekle - her sprint'i ardışık olarak hesapla
        # Tarih string'ini datetime'a dönüştür (sadece tarih varsa da çalışır)
        try:
            current_start = datetime.datetime.fromisoformat(sprint_start_date)
            logger.error(f"[DEBUG] Parsed start date as datetime: {current_start}")
        except ValueError as e:
            logger.error(f"[DEBUG] Failed to parse as datetime, trying as date: {e}")
            try:
                # Eğer sadece tarih varsa (YYYY-MM-DD), datetime'a çevir
                date_obj = datetime.date.fromisoformat(sprint_start_date)
                current_start = datetime.datetime.combine(date_obj, datetime.time.min)
                logger.error(f"[DEBUG] Parsed start date as date: {current_start}")
            except Exception as parse_error:
                logger.error(f"[ERROR] Failed to parse start_date: {parse_error}")
                # Fallback: bugün
                current_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
                logger.error(f"[DEBUG] Using fallback start date: {current_start}")
        
        for sp in sprints_list:
            sprint_number = sp.get("sprint_number", 1)
            sprint_name = sp.get("sprint_name", f"Sprint {sprint_number}")
            duration_weeks = sp.get("duration_weeks", 2)
            
            # Bu sprint'in bitiş tarihi
            current_end = current_start + datetime.timedelta(weeks=duration_weeks)
            
            events.append({
                "id": f"{sprint_id}_{sprint_number}",
                "title": sprint_name,
                "start": current_start.isoformat(),
                "end": current_end.isoformat(),
                "type": "sprint",
                "status": sprint.get("status", "planned"),
                "description": sp.get("focus", "")
            })
            
            # Bu sprint'teki task'ları ekle
            sprint_tasks = sp.get("tasks", [])
            task_count = len(sprint_tasks)
            logger.error(f"[DEBUG] Sprint {sprint_number} has {task_count} tasks: {sprint_tasks[:3] if len(sprint_tasks) > 3 else sprint_tasks}")
            
            for idx, task_identifier in enumerate(sprint_tasks):
                # Eğer task_title_X formatındaysa, index'e göre al
                if isinstance(task_identifier, str) and task_identifier.startswith("task_title_"):
                    try:
                        task_index = int(task_identifier.split("_")[-1]) - 1
                        if 0 <= task_index < len(tasks):
                            task = tasks[task_index]
                            logger.error(f"[DEBUG] Resolved placeholder '{task_identifier}' to task[{task_index}]: '{task.get('title')}'")
                        else:
                            task = None
                            logger.error(f"[DEBUG] Placeholder '{task_identifier}' index out of range")
                    except (ValueError, IndexError) as e:
                        task = None
                        logger.error(f"[DEBUG] Failed to parse placeholder '{task_identifier}': {e}")
                else:
                    # Task'ı bul - hem task_id, hem title, hem task_title ile kontrol et
                    task = next((t for t in tasks if 
                        task_identifier == t.get("task_id") or 
                        task_identifier == t.get("title") or 
                        task_identifier == t.get("task_title") or
                        t.get("title", "").lower() == task_identifier.lower()), None)
                    logger.error(f"[DEBUG] Looking for task '{task_identifier}': {'FOUND' if task else 'NOT FOUND'}")
                if task:
                    # Task tarihleri varsa kullan, yoksa sprint içinde eşit dağıt
                    if task.get("start_date") and task.get("due_date"):
                        task_start = task.get("start_date")
                        task_end = task.get("due_date")
                    else:
                        # Task'ları sprint içinde eşit aralıklarla dağıt
                        days_per_task = (duration_weeks * 7) / max(task_count, 1)
                        task_start_offset = int(idx * days_per_task)
                        task_end_offset = int((idx + 1) * days_per_task)
                        
                        task_start = (current_start + datetime.timedelta(days=task_start_offset)).isoformat()
                        task_end = (current_start + datetime.timedelta(days=task_end_offset)).isoformat()
                    
                    # Atanan kişiyi bul - önce assigned_to, sonra task_attended_to
                    assignee_data = task.get("assigned_to") or task.get("task_attended_to") or "Atanmamış"
                    
                    # Eğer assignee bir dict ise, name field'ını al
                    if isinstance(assignee_data, dict):
                        assignee = assignee_data.get("name", "Atanmamış")
                    else:
                        assignee = assignee_data if assignee_data else "Atanmamış"
                    
                    events.append({
                        "id": task.get("task_id", f"task_{idx}"),
                        "title": task.get("title", task_identifier),
                        "start": task_start,
                        "end": task_end,
                        "type": "task",
                        "status": task.get("status", "pending"),
                        "priority": task.get("priority", "medium"),
                        "assignee": assignee
                    })
                    logger.error(f"[DEBUG] ✅ Added task to calendar: '{task.get('title')}' → Assignee: {assignee}")
            
            # Bir sonraki sprint için başlangıç tarihini güncelle
            current_start = current_end
        
        logger.error(f"[DEBUG] Total events created: {len(events)} (Sprints: {len([e for e in events if e['type'] == 'sprint'])}, Tasks: {len([e for e in events if e['type'] == 'task'])})")
        
        return {
            "sprint_id": sprint_id,
            "project_id": project_id,
            "total_events": len(events),
            "events": events
        }
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        error_detail = f"Sprint takvim olayları getirme hatası: {str(e)}"
        full_traceback = traceback.format_exc()
        logger.error(f"\n{'='*80}")
        logger.error(f"[ERROR] CALENDAR EVENTS FAILED")
        logger.error(f"Sprint ID: {sprint_id}")
        logger.error(f"Error: {error_detail}")
        logger.error(f"{'='*80}")
        logger.error(full_traceback)
        logger.error(f"{'='*80}\n")
        raise HTTPException(status_code=500, detail=error_detail)
