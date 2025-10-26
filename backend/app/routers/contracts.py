from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
import json
from app.firebase_db import FirebaseDatabase

router = APIRouter()

_db_client = None
def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

# TASK ASSIGNMENT SYSTEM PROMPT
TASK_ASSIGNMENT_PROMPT = """
Sen, bir şirketin insan kaynakları ve proje yönetimi için görev atama yapan uzman bir AI asistanısın.
Görevin, verilen bir TASK'ı (görev) ve şirketin çalışan listesini inceleyip, bu görevi EN UYGUN kişiye atamaktır.

Atama yaparken şu kriterleri dikkate al (önem sırasına göre):
1. **Tech Stack Uyumu**: Görevde belirtilen teknolojilerin çalışanın tech stack'inde olması (EN ÖNEMLİ)
2. **Workload (İş Yükü)**: Düşük iş yükü olan çalışanları tercih et (low > medium > high)
3. **Departman/Team Uyumu**: Görevin departmanı ile çalışanın departmanı uyumlu olmalı
4. **Role/Seniority**: Görevin karmaşıklığına uygun deneyim seviyesi

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "assigned_employee_id": "emp_xxx",
  "assigned_employee_name": "Ad Soyad",
  "assignment_reason": "Kısa açıklama: Bu kişi neden seçildi? (tech stack uyumu, iş yükü, departman bilgisi)"
}

Başka hiçbir açıklama veya metin ekleme.
"""

def _auto_assign_task_to_employee(task: Dict[str, Any], all_employees: List[Dict[str, Any]], groq_service) -> Optional[Dict[str, Any]]:
    """
    Bir task'ı AI kullanarak en uygun çalışana atar.
    
    Args:
        task: Task bilgileri
        all_employees: Tüm çalışanlar listesi
        groq_service: Groq AI servisi
        
    Returns:
        Atama bilgileri veya None
    """
    try:
        user_prompt = f"""
GÖREV BİLGİLERİ:
- Başlık: {task.get('task_title')}
- Detay: {task.get('task_detail')}
- Gerekli Teknolojiler: {task.get('task_stack')}
- Departman: {task.get('department')}

MEVCUT ÇALIŞANLAR:
{json.dumps(all_employees, indent=2, ensure_ascii=False)}

Lütfen bu görevi EN UYGUN çalışana ata. Sadece JSON formatında yanıt ver.
"""
        
        completion = groq_service.client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_ASSIGNMENT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        assignment_result = json.loads(completion.choices[0].message.content)
        return assignment_result
        
    except Exception as e:
        print(f"[Auto Assign] Hata: {str(e)}")
        return None

class ContractAnalysisRequest(BaseModel):
    contract_text: str
    contract_name: str = "Contract Document"

class ContractAnalysisResponse(BaseModel):
    status: str
    contract_id: str
    message: str
    analysis: Dict[str, Any]

class ContractResponse(BaseModel):
    contract_id: str
    contract_name: str
    contract_text: str
    analysis: Dict[str, Any]
    status: str
    created_at: str

@router.get("/")
async def get_contracts():
    """
    Tüm sözleşmeleri listele.
    """
    try:
        contracts = get_db().list_contracts()
        return {"contracts": contracts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme listesi getirme hatası: {str(e)}")

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """
    Belirli bir sözleşmenin detaylarını getir.
    """
    try:
        contract = get_db().get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        return contract
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme detayı getirme hatası: {str(e)}")

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    PDF sözleşme dosyasını yükle.
    """
    try:
        # Dosya tipini kontrol et
        if not file.content_type == "application/pdf":
            raise HTTPException(status_code=400, detail="Sadece PDF dosyaları kabul edilir")
        
        # Dosyayı oku
        file_content = await file.read()
        
        # Dosya boyutunu kontrol et (max 10MB)
        file_size = len(file_content)
        if file_size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (max 10MB)")
        
        # Firebase Storage'a yükle
        file_path = f"contracts/{uuid.uuid4().hex}.pdf"
        file_url = get_db().upload_file(file_path, file_content, "application/pdf")
        
        # Contract kaydı oluştur
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        contract_data = {
            "contract_name": file.filename,
            "file_path": file_path,
            "file_url": file_url,
            "status": "uploaded",
            "file_size": file_size
        }
        get_db().save_contract(contract_id, contract_data)
        
        return {
            "contract_id": contract_id,
            "file_url": file_url,
            "message": "Sözleşme başarıyla yüklendi"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme yükleme hatası: {str(e)}")

@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    """
    Sözleşme metnini analiz et (metin bazlı).
    """
    try:
        from app.services.groq_service import GroqService
        
        groq_service = GroqService()
        
        # Sözleşmeyi analiz et
        analysis = groq_service.analyze_project(request.contract_text)
        
        # Proje oluştur
        tasks = groq_service.generate_tasks(analysis)
        
        # Proje ID oluştur ve kaydet
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        get_db().save_project(project_id, analysis)
        get_db().save_tasks(project_id, tasks)
        
        # Contract kaydet
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        get_db().save_contract(contract_id, {
            "contract_name": request.contract_name,
            "contract_text": request.contract_text,
            "analysis": analysis,
            "project_id": project_id,
            "status": "analyzed"
        })
        
        return ContractAnalysisResponse(
            status="success",
            contract_id=contract_id,
            message="Sözleşme başarıyla analiz edildi",
            analysis=analysis
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme analiz hatası: {str(e)}")

@router.post("/{contract_id}/analyze")
async def analyze_uploaded_contract(contract_id: str, auto_assign: bool = True):
    """
    Yüklenmiş bir sözleşmeyi analiz et, projeye dönüştür ve otomatik task ataması yap.
    
    Args:
        contract_id: Sözleşme ID'si
        auto_assign: True ise taskları otomatik olarak çalışanlara atar (varsayılan: True)
    """
    try:
        # Sözleşmeyi al
        contract = get_db().get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        # Dosya URL'sini al
        file_url = contract.get("file_url")
        if not file_url:
            raise HTTPException(status_code=400, detail="Sözleşme dosyası bulunamadı")
        
        # LlamaParse ile parse et
        from app.services.llamaparse_service import LlamaParseService
        from app.services.groq_service import GroqService
        import tempfile
        import os
        import requests
        
        llamaparse = LlamaParseService()
        groq_service = GroqService()
        
        # Dosyayı indir
        response = requests.get(file_url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Dosya indirilemedi")
        
        # Geçici dosya oluştur
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            tmp_path = tmp.name
        
        try:
            # Parse et
            parsed_text = llamaparse.parse_pdf(tmp_path)
            
            # Analiz et
            analysis = groq_service.analyze_project(parsed_text)
            
            # Proje adını belirle (AI'dan gelen öncelikli)
            if not analysis.get("project_name") or analysis.get("project_name") == "Yeni Proje":
                # AI bulamadıysa sözleşme adını kullan
                contract_name = contract.get("contract_name", "Sözleşme Projesi")
                # .pdf uzantısını temizle
                if contract_name.lower().endswith('.pdf'):
                    contract_name = contract_name[:-4]
                analysis["project_name"] = contract_name
            
            print(f"[Contract Analysis] Proje adı belirlendi: {analysis['project_name']}")
            
            # Tasklar oluştur
            tasks = groq_service.generate_tasks(analysis)
            
            # Projeyi kaydet
            project_id = f"project_{uuid.uuid4().hex[:8]}"
            get_db().save_project(project_id, analysis)
            
            # Otomatik atama yapılacaksa
            assignment_results = []
            if auto_assign:
                print(f"[Contract Analysis] {len(tasks)} task için otomatik atama başlatılıyor...")
                
                # Şirket yapısını al
                company_data = get_db().get_company_structure()
                if company_data:
                    # Tüm çalışanları düz listeye çevir
                    all_employees = []
                    for department in company_data.get("companyStructure", {}).get("departments", []):
                        dept_name = department["name"]
                        for team in department.get("teams", []):
                            team_name = team["name"]
                            for employee in team.get("employees", []):
                                all_employees.append({
                                    **employee,
                                    "department": dept_name,
                                    "team": team_name
                                })
                    
                    # Her task için uygun çalışan bul ve ata
                    for i, task in enumerate(tasks):
                        try:
                            # Task ID oluştur
                            task["task_id"] = f"task_{uuid.uuid4().hex[:8]}"
                            task["status"] = "pending"
                            task["project_id"] = project_id
                            
                            # AI ile atama yap
                            assigned_employee = _auto_assign_task_to_employee(
                                task, all_employees, groq_service
                            )
                            
                            if assigned_employee:
                                task["task_attended_to"] = assigned_employee["assigned_employee_name"]
                                task["assigned_employee_id"] = assigned_employee["assigned_employee_id"]
                                task["assignment_reason"] = assigned_employee["assignment_reason"]
                                
                                assignment_results.append({
                                    "task_title": task["task_title"],
                                    "assigned_to": assigned_employee["assigned_employee_name"],
                                    "reason": assigned_employee["assignment_reason"]
                                })
                                
                                print(f"[Contract Analysis] Task {i+1}/{len(tasks)} atandı: {task['task_title']} -> {assigned_employee['assigned_employee_name']}")
                            else:
                                task["task_attended_to"] = ""
                                task["assigned_employee_id"] = None
                                print(f"[Contract Analysis] Task {i+1}/{len(tasks)} atanamadı: {task['task_title']}")
                        
                        except Exception as e:
                            print(f"[Contract Analysis] Task atama hatası: {str(e)}")
                            task["task_attended_to"] = ""
                            task["assigned_employee_id"] = None
                else:
                    print("[Contract Analysis] Şirket yapısı bulunamadı, atama yapılamıyor")
            else:
                # Otomatik atama kapalıysa, task'lara sadece ID ve status ekle
                for task in tasks:
                    task["task_id"] = f"task_{uuid.uuid4().hex[:8]}"
                    task["status"] = "pending"
                    task["project_id"] = project_id
                    task["task_attended_to"] = ""
                    task["assigned_employee_id"] = None
            
            # Taskları kaydet
            get_db().save_tasks(project_id, tasks)
            
            # Sözleşmeyi güncelle
            contract["status"] = "analyzed"
            contract["project_id"] = project_id
            contract["parsed_text"] = parsed_text
            contract["analysis"] = analysis
            get_db().save_contract(contract_id, contract)
            
            response_data = {
                "status": "success",
                "contract_id": contract_id,
                "project_id": project_id,
                "message": "Sözleşme başarıyla analiz edildi",
                "analysis": analysis,
                "total_tasks": len(tasks),
                "tasks": tasks
            }
            
            if auto_assign and assignment_results:
                response_data["assignments"] = assignment_results
                response_data["assigned_count"] = len(assignment_results)
                response_data["message"] = f"Sözleşme analiz edildi ve {len(assignment_results)} task otomatik olarak atandı"
            
            return response_data
            
        finally:
            # Geçici dosyayı sil
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme analiz hatası: {str(e)}")

@router.post("/{contract_id}/convert-to-project")
async def convert_contract_to_project(contract_id: str):
    """
    Sözleşmeyi projeye dönüştür.
    """
    try:
        # Sözleşmeyi al
        contract = get_db().get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        # Sözleşme metnini al
        contract_text = contract.get("contract_text", "")
        if not contract_text:
            raise HTTPException(status_code=400, detail="Sözleşme metni bulunamadı")
        
        # Proje analizi yap
        from app.tools import analyze_project_text
        inject_dependencies(get_db(), "api_session")
        
        result = analyze_project_text(contract_text, contract.get("contract_name", "Contract Project"))
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        # Sözleşme durumunu güncelle
        contract["status"] = "converted_to_project"
        contract["project_id"] = result_data["project_id"]
        get_db().save_contract(contract_id, contract)
        
        return {
            "message": "Sözleşme başarıyla projeye dönüştürüldü",
            "project_id": result_data["project_id"],
            "analysis": result_data["analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme dönüştürme hatası: {str(e)}")

@router.post("/{contract_id}/auto-assign-tasks")
async def auto_assign_contract_tasks(contract_id: str):
    """
    Sözleşmeye ait taskları otomatik olarak çalışanlara atar.
    Bu endpoint, daha önce oluşturulmuş ama atanmamış tasklar için kullanılır.
    """
    try:
        # Sözleşmeyi al
        contract = get_db().get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        project_id = contract.get("project_id")
        if not project_id:
            raise HTTPException(status_code=400, detail="Bu sözleşme henüz analiz edilmemiş")
        
        # Taskları al
        tasks = get_db().get_tasks(project_id)
        if not tasks:
            raise HTTPException(status_code=404, detail="Bu proje için task bulunamadı")
        
        # Groq service oluştur
        from app.services.groq_service import GroqService
        groq_service = GroqService()
        
        # Şirket yapısını al
        company_data = get_db().get_company_structure()
        if not company_data:
            raise HTTPException(status_code=400, detail="Şirket yapısı bulunamadı")
        
        # Tüm çalışanları düz listeye çevir
        all_employees = []
        for department in company_data.get("companyStructure", {}).get("departments", []):
            dept_name = department["name"]
            for team in department.get("teams", []):
                team_name = team["name"]
                for employee in team.get("employees", []):
                    all_employees.append({
                        **employee,
                        "department": dept_name,
                        "team": team_name
                    })
        
        # Her task için atama yap
        assignment_results = []
        unassigned_count = 0
        already_assigned_count = 0
        
        for i, task in enumerate(tasks):
            # Zaten atanmış mı kontrol et
            if task.get("assigned_employee_id"):
                already_assigned_count += 1
                continue
            
            try:
                # AI ile atama yap
                assigned_employee = _auto_assign_task_to_employee(
                    task, all_employees, groq_service
                )
                
                if assigned_employee:
                    task["task_attended_to"] = assigned_employee["assigned_employee_name"]
                    task["assigned_employee_id"] = assigned_employee["assigned_employee_id"]
                    task["assignment_reason"] = assigned_employee["assignment_reason"]
                    
                    assignment_results.append({
                        "task_title": task["task_title"],
                        "assigned_to": assigned_employee["assigned_employee_name"],
                        "reason": assigned_employee["assignment_reason"]
                    })
                    
                    print(f"[Auto Assign] Task {i+1}/{len(tasks)} atandı: {task['task_title']} -> {assigned_employee['assigned_employee_name']}")
                else:
                    unassigned_count += 1
                    print(f"[Auto Assign] Task {i+1}/{len(tasks)} atanamadı: {task['task_title']}")
            
            except Exception as e:
                unassigned_count += 1
                print(f"[Auto Assign] Task atama hatası: {str(e)}")
        
        # Güncellenmiş taskları kaydet
        get_db().save_tasks(project_id, tasks)
        
        return {
            "status": "success",
            "contract_id": contract_id,
            "project_id": project_id,
            "total_tasks": len(tasks),
            "already_assigned": already_assigned_count,
            "newly_assigned": len(assignment_results),
            "unassigned": unassigned_count,
            "assignments": assignment_results,
            "message": f"{len(assignment_results)} task başarıyla atandı"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Otomatik atama hatası: {str(e)}")


@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Sözleşmeyi sil.
    """
    try:
        # Sözleşmeyi al
        contract = get_db().get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        # Dosyayı Storage'dan sil
        if contract.get("file_path"):
            try:
                blob = get_db().bucket.blob(contract["file_path"])
                blob.delete()
            except:
                pass  # Dosya zaten silinmiş olabilir
        
        # Sözleşmeyi sil
        get_db().db.collection('contracts').document(contract_id).delete()
        
        return {"message": f"Sözleşme silindi: {contract_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme silme hatası: {str(e)}")
