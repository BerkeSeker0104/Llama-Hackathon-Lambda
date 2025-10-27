from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import uuid
import json
from app.orchestrator import ChatOrchestrator
from app.groq_client import GroqAgent
from app.firebase_db import FirebaseDatabase
from app.schemas.chat import ConfirmationRequest, ConfirmationResponse

router = APIRouter()

# Lazy loading
_db_client = None
_agent_client = None
_orchestrator = None

def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

def get_orchestrator():
    global _orchestrator, _agent_client
    if _orchestrator is None:
        _agent_client = GroqAgent()
        _orchestrator = ChatOrchestrator(db_client=get_db(), agent_client=_agent_client)
    return _orchestrator

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(chat_message: ChatMessage):
    """
    AI asistanıyla sohbet et.
    """
    try:
        # Session ID oluştur veya kullan
        session_id = chat_message.session_id or f"session_{uuid.uuid4().hex[:8]}"
        
        # Orchestrator ile mesajı işle
        ai_response = get_orchestrator().handle_message(session_id, chat_message.message)
        
        return ChatResponse(
            response=ai_response,
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat hatası: {str(e)}")

@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """
    Belirli bir session'ın chat geçmişini getir.
    """
    try:
        messages = db_client.get_chat_history(session_id)
        return {"session_id": session_id, "messages": messages}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat geçmişi getirme hatası: {str(e)}")

@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    """
    Belirli bir session'ın chat geçmişini temizle.
    """
    try:
        # Firebase'de chat history'yi temizle
        db_client = get_db()
        db_client.db.collection('chat_history').document(session_id).delete()
        return {"message": f"Chat geçmişi temizlendi: {session_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat geçmişi temizleme hatası: {str(e)}")

@router.post("/confirm-action", response_model=ConfirmationResponse)
async def confirm_action(confirmation: ConfirmationRequest):
    """
    Kullanıcı onayını işler ve gerekli aksiyonu gerçekleştirir.
    """
    try:
        orchestrator = get_orchestrator()
        
        # Onay verisini işle
        response = orchestrator.handle_confirmation(
            session_id=confirmation.session_id,
            confirmation_data=confirmation.action_data,
            confirmed=confirmation.confirmed
        )
        
        return ConfirmationResponse(
            success=True,
            message=response,
            data={"action_type": confirmation.action_type, "confirmed": confirmation.confirmed}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Onay işleme hatası: {str(e)}")

@router.get("/categories")
async def get_chat_categories():
    """
    Chat kategorilerini ve örnek prompt'ları getirir.
    """
    try:
        # Firebase'den proje ve çalışan verilerini al
        db_client = get_db()
        projects = db_client.list_projects()
        company_data = db_client.get_company_structure()
        
        # Dinamik kategoriler oluştur
        categories = []
        
        # Çalışan isimlerini al
        employees = []
        if company_data and company_data.get("companyStructure"):
            for dept in company_data.get("companyStructure", {}).get("departments", []):
                for team in dept.get("teams", []):
                    for emp in team.get("employees", []):
                        employees.append(f"{emp.get('firstName')} {emp.get('lastName')}")
        
        # Eğer company structure'dan çalışan bulunamazsa, employees API'sinden al
        if not employees:
            try:
                employees_data = db_client.list_employees()
                employees = [emp.get("name", "Çalışan") for emp in employees_data[:5]]
            except:
                employees = ["Ahmet Yılmaz", "Zeynep Kaya", "Mehmet Demir"]
        
        # Proje isimlerini al
        project_names = []
        if projects:
            project_names = [p.get("project_name", "Proje") for p in projects[:5]]
        else:
            project_names = ["İş Zekası Dashboard", "Mobil Bankacılık Uygulaması", "E-ticaret Platformu"]
        
        # 1. Proje Durumu ve Risk Analizi
        project_analysis_prompts = []
        for i, project in enumerate(project_names[:3]):
            project_analysis_prompts.extend([
                f"{project} projesinin mevcut durumunu analiz et",
                f"{project} projesinin risklerini değerlendir",
                f"{project} projesinin gecikme riski nedir?",
                f"{project} projesi için sprint planı oluştur"
            ])
        
        categories.append({
            "category": "Proje Durumu ve Risk Analizi",
            "prompts": project_analysis_prompts,
            "type": "project_analysis"
        })
        
        # 2. Sprint Planlama ve Revizyon
        sprint_prompts = []
        for i, project in enumerate(project_names[:2]):
            sprint_prompts.extend([
                f"{project} için 2 haftalık sprint planı oluştur",
                f"{project} sprint planını revize et, 3 gün gecikme var",
                f"{project} sprint sağlık durumunu analiz et"
            ])
        sprint_prompts.extend([
            "Sprint kapasitesini hesapla",
            "Sprint hedeflerini belirle",
            "Acil durum sprint revizyonu yap"
        ])
        
        categories.append({
            "category": "Sprint Planlama ve Revizyon",
            "prompts": sprint_prompts,
            "type": "sprint_planning"
        })
        
        # 3. Görev Yönetimi ve Atama
        task_prompts = []
        for i, employee in enumerate(employees[:3]):
            task_prompts.extend([
                f"{employee} için görev ataması yap",
                f"{employee} görevlerini yeniden ata",
                f"{employee} iş yükünü analiz et"
            ])
        task_prompts.extend([
            "Hangi çalışanlar müsait?",
            "Bu görevi en uygun kişiye ata",
            "Tüm görevleri listele",
            "Görev önceliklerini güncelle",
            "Görev durumlarını kontrol et"
        ])
        
        categories.append({
            "category": "Görev Yönetimi ve Atama",
            "prompts": task_prompts,
            "type": "task_management"
        })
        
        # 4. Acil Durum Yönetimi
        emergency_prompts = []
        for i, employee in enumerate(employees[:3]):
            emergency_prompts.extend([
                f"{employee} acil durumu var, 5 gün çalışamayacak. Görevlerini yeniden ata.",
                f"{employee} izne çıktı, görevlerini başkasına ver.",
                f"{employee} hastalandı, görevlerini yeniden planla."
            ])
        emergency_prompts.extend([
            "Acil durum yönetimi protokolünü devreye sok",
            "Kritik görevleri yeniden önceliklendir",
            "Acil durum sprint revizyonu yap"
        ])
        
        categories.append({
            "category": "Acil Durum Yönetimi",
            "prompts": emergency_prompts,
            "type": "emergency_management"
        })
        
        # 5. Kaynak ve Performans Analizi
        resource_prompts = [
            "Çalışan iş yükünü analiz et",
            "Hangi departmanlar yoğun?",
            "Kaynak dağılımını optimize et",
            "Çalışan kapasitesini hesapla",
            "İş yükü dengesini kontrol et",
            "Proje performansını analiz et",
            "Sprint sağlık durumunu analiz et"
        ]
        categories.append({
            "category": "Kaynak ve Performans Analizi",
            "prompts": resource_prompts,
            "type": "resource_analysis"
        })
        
        # Eğer veri yoksa varsayılan kategoriler
        if not categories:
            categories = [
                {
                    "category": "Acil Durum Yönetimi",
                    "prompts": [
                        "Mert Koç acil durumu var, 5 gün çalışamayacak. Görevlerini yeniden ata.",
                        "Ayşe Yılmaz izne çıktı, görevlerini başkasına ver.",
                    ]
                },
                {
                    "category": "Sprint Planlama",
                    "prompts": [
                        "Bu proje için 2 haftalık sprint planı oluştur",
                        "Sprint planını revize et, 3 gün gecikme var",
                        "Sprint sağlık durumunu analiz et",
                    ]
                },
                {
                    "category": "Gecikme Tahmini",
                    "prompts": [
                        "Proje zamanında biter mi?",
                        "Hangi görevler gecikme riski taşıyor?",
                        "Bu projenin risk analizi nedir?",
                    ]
                },
                {
                    "category": "Görev Yönetimi",
                    "prompts": [
                        "Hangi çalışanlar müsait?",
                        "Bu görevi en uygun kişiye ata",
                        "Tüm görevleri listele",
                    ]
                }
            ]
        
        return {"categories": categories}
        
    except Exception as e:
        # Hata durumunda varsayılan kategorileri döndür
        return {
            "categories": [
                {
                    "category": "Acil Durum Yönetimi",
                    "prompts": [
                        "Mert Koç acil durumu var, 5 gün çalışamayacak. Görevlerini yeniden ata.",
                        "Ayşe Yılmaz izne çıktı, görevlerini başkasına ver.",
                    ]
                },
                {
                    "category": "Sprint Planlama",
                    "prompts": [
                        "Bu proje için 2 haftalık sprint planı oluştur",
                        "Sprint planını revize et, 3 gün gecikme var",
                        "Sprint sağlık durumunu analiz et",
                    ]
                },
                {
                    "category": "Gecikme Tahmini",
                    "prompts": [
                        "Proje zamanında biter mi?",
                        "Hangi görevler gecikme riski taşıyor?",
                        "Bu projenin risk analizi nedir?",
                    ]
                },
                {
                    "category": "Görev Yönetimi",
                    "prompts": [
                        "Hangi çalışanlar müsait?",
                        "Bu görevi en uygun kişiye ata",
                        "Tüm görevleri listele",
                    ]
                }
            ]
        }
