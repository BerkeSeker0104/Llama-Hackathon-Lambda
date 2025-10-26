from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, classify_change_request

router = APIRouter()

_db_client = None
def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

class ChangeRequestRequest(BaseModel):
    change_text: str
    project_id: Optional[str] = None

class ChangeRequestResponse(BaseModel):
    status: str
    change_id: str
    message: str
    classification: Dict[str, Any]

class ChangeApplyRequest(BaseModel):
    change_id: str
    action: str  # "extend_timeline", "descope", "fixed_budget_partial"

class ChangeApplyResponse(BaseModel):
    status: str
    message: str
    new_plan: Optional[Dict[str, Any]] = None

@router.get("/{project_id}")
async def get_change_requests(project_id: str):
    """
    Projeye ait değişiklik taleplerini listele.
    """
    try:
        changes = get_db().get_change_requests(project_id)
        return {"change_requests": changes}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik talepleri getirme hatası: {str(e)}")

@router.get("/{project_id}/{change_id}")
async def get_change_request(project_id: str, change_id: str):
    """
    Belirli bir değişiklik talebinin detaylarını getir.
    """
    try:
        changes = get_db().get_change_requests(project_id)
        change = next((c for c in changes if c.get("change_id") == change_id), None)
        
        if not change:
            raise HTTPException(status_code=404, detail="Değişiklik talebi bulunamadı")
        
        return change
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik talebi detayı getirme hatası: {str(e)}")

@router.post("/classify", response_model=ChangeRequestResponse)
async def classify_change(request: ChangeRequestRequest):
    """
    Değişiklik talebini sınıflandır.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # classify_change_request tool'unu çağır (LangChain tool - .invoke() kullan)
        result = classify_change_request.invoke({
            "change_text": request.change_text,
            "project_id": request.project_id
        })
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return ChangeRequestResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik sınıflandırma hatası: {str(e)}")

@router.post("/apply", response_model=ChangeApplyResponse)
async def apply_change(request: ChangeApplyRequest):
    """
    Değişiklik talebini uygula.
    """
    try:
        # Değişiklik talebini al
        change_ref = get_db().db.collection('change_requests').document(request.change_id)
        change_doc = change_ref.get()
        
        if not change_doc.exists:
            raise HTTPException(status_code=404, detail="Değişiklik talebi bulunamadı")
        
        change_data = change_doc.to_dict()
        project_id = change_data.get("project_id")
        classification = change_data.get("classification", {})
        
        if not project_id:
            raise HTTPException(status_code=400, detail="Proje ID bulunamadı")
        
        # Değişiklik türüne göre işlem yap
        if request.action == "extend_timeline":
            # Timeline uzatma
            timeline_impact = classification.get("timeline_impact_days", 0)
            message = f"Timeline {timeline_impact} gün uzatıldı"
            
        elif request.action == "descope":
            # Kapsam daraltma
            affected_tasks = classification.get("affected_tasks", [])
            message = f"Kapsam daraltıldı, {len(affected_tasks)} görev çıkarıldı"
            
        elif request.action == "fixed_budget_partial":
            # Sabit bütçe, kısmi teslimat
            budget_impact = classification.get("budget_impact_percentage", 0)
            message = f"Sabit bütçe korundu, %{budget_impact} kısmi teslimat"
            
        else:
            raise HTTPException(status_code=400, detail="Geçersiz aksiyon")
        
        # Değişiklik durumunu güncelle
        change_data["status"] = "applied"
        change_data["action_taken"] = request.action
        from datetime import datetime
        change_data["applied_at"] = datetime.utcnow().isoformat()
        
        change_ref.update(change_data)
        
        # Sprint planını yeniden düzenle (eğer gerekirse)
        new_plan = None
        if request.action in ["extend_timeline", "descope"]:
            # Sprint replan yap
            from app.tools import replan_sprints
            inject_dependencies(get_db(), "api_session")
            
            delays = classification.get("timeline_impact_days", 0) if request.action == "extend_timeline" else 0
            vacation_days = 0
            
            replan_result = replan_sprints(project_id, vacation_days, delays)
            import json
            replan_data = json.loads(replan_result)
            
            if "new_plan" in replan_data:
                new_plan = replan_data["new_plan"]
        
        return ChangeApplyResponse(
            status="success",
            message=message,
            new_plan=new_plan
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik uygulama hatası: {str(e)}")

@router.put("/{change_id}/status")
async def update_change_status(change_id: str, status: str):
    """
    Değişiklik talebi durumunu güncelle.
    """
    try:
        # Değişiklik talebini güncelle
        change_ref = get_db().db.collection('change_requests').document(change_id)
        change_doc = change_ref.get()
        
        if not change_doc.exists:
            raise HTTPException(status_code=404, detail="Değişiklik talebi bulunamadı")
        
        change_ref.update({"status": status})
        
        return {"message": f"Değişiklik talebi durumu güncellendi: {status}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik talebi durumu güncelleme hatası: {str(e)}")

@router.delete("/{change_id}")
async def delete_change_request(change_id: str):
    """
    Değişiklik talebini sil.
    """
    try:
        # Değişiklik talebini sil
        get_db().db.collection('change_requests').document(change_id).delete()
        
        return {"message": f"Değişiklik talebi silindi: {change_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Değişiklik talebi silme hatası: {str(e)}")
