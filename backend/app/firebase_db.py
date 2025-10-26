import firebase_admin
from firebase_admin import credentials, firestore, storage
from app.base_db import BaseDatabase
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import uuid

class FirebaseDatabase(BaseDatabase):
    """
    Firebase Firestore implementation of BaseDatabase
    Project ID: lambda-59fe8
    """
    def __init__(self):
        if not firebase_admin._apps:
            # Initialize Firebase Admin SDK
            cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
            
            if cred_path and os.path.exists(cred_path):
                # Use JSON file
                print(f"[FirebaseDB] Using credentials from file: {cred_path}")
                cred = credentials.Certificate(cred_path)
            else:
                # Use environment variables (for deployment)
                cred_dict = {
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID", "lambda-59fe8"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL")
                }
                cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred, {
                'storageBucket': os.getenv("FIREBASE_STORAGE_BUCKET", "lambda-59fe8.firebasestorage.app")
            })
            print("[FirebaseDB Info] Firebase initialized for project: lambda-59fe8")
        
        self.db = firestore.client()
        self.bucket = storage.bucket()
        print("[FirebaseDB Info] FirebaseDatabase başlatıldı.")
    
    # --- CHAT HISTORY METHODS ---
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Verilen ID'ye ait tüm konuşma geçmişini getirir."""
        doc_ref = self.db.collection("chat_history").document(session_id)
        doc = doc_ref.get()
        
        if doc.exists:
            data = doc.to_dict()
            return data.get("messages", [])
        else:
            # İlk mesaj için boş döküman oluştur
            doc_ref.set({"messages": [], "created_at": datetime.utcnow().isoformat()})
            return []
    
    def save_message(self, session_id: str, message: Dict[str, Any]):
        """Bir mesajı (user, assistant, tool) konuşma geçmişine kaydeder."""
        doc_ref = self.db.collection("chat_history").document(session_id)
        
        # Timestamp ekle
        message_with_timestamp = {
            **message,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Check if document exists, if not create it
        doc = doc_ref.get()
        if not doc.exists:
            doc_ref.set({
                "messages": [message_with_timestamp],
                "created_at": datetime.utcnow().isoformat()
            })
        else:
            # Array'e ekle
            doc_ref.update({
                "messages": firestore.ArrayUnion([message_with_timestamp])
            })
    
    # --- PROJECT METHODS ---
    def save_project(self, project_id: str, project_data: Dict[str, Any]):
        """Proje verisini kaydeder."""
        # Field name mapping: Groq service'den gelen camelCase field isimlerini snake_case'e dönüştür
        normalized_project = {
            "project_id": project_id,
            "project_name": project_data.get("projectName", project_data.get("project_name", "Yeni Proje")),
            "department": project_data.get("department", ""),
            "detailedDescription": project_data.get("detailedDescription", ""),
            "tech_stack": project_data.get("techStack", project_data.get("tech_stack", [])),
            "estimated_duration": project_data.get("estimatedDuration", project_data.get("estimated_duration", "")),
            "acceptance_criteria": project_data.get("acceptanceCriteria", project_data.get("acceptance_criteria", [])),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Critical analysis alanını dönüştür
        if "criticalAnalysis" in project_data:
            critical_analysis = project_data["criticalAnalysis"]
            normalized_project["critical_analysis"] = {
                "risks": critical_analysis.get("risks", []),
                "missing_information": critical_analysis.get("missingInfo", critical_analysis.get("missing_information", [])),
                "contradictions": critical_analysis.get("contradictions", [])
            }
        elif "critical_analysis" in project_data:
            normalized_project["critical_analysis"] = project_data["critical_analysis"]
        
        self.db.collection("projects").document(project_id).set(normalized_project, merge=True)
        print(f"[FirebaseDB] Proje kaydedildi: {project_id}")
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Proje verisini getirir."""
        doc = self.db.collection("projects").document(project_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """Tüm projeleri listeler."""
        projects = []
        docs = self.db.collection("projects").stream()
        
        for doc in docs:
            project_data = doc.to_dict()
            projects.append(project_data)
        
        return projects
    
    def set_active_project(self, session_id: str, project_id: str):
        """Aktif projeyi ayarlar."""
        self.db.collection("active_projects").document(session_id).set({
            "project_id": project_id,
            "updated_at": datetime.utcnow().isoformat()
        })
        print(f"[FirebaseDB] Aktif proje ayarlandı: {project_id} (session: {session_id})")
    
    def get_active_project(self, session_id: str) -> Optional[str]:
        """Aktif proje ID'sini getirir."""
        doc = self.db.collection("active_projects").document(session_id).get()
        
        if doc.exists:
            return doc.to_dict().get("project_id")
        return None
    
    # --- TASK METHODS ---
    def save_tasks(self, project_id: str, tasks: List[Dict[str, Any]]):
        """Görevleri kaydeder."""
        # Her görevi ayrı bir belge olarak kaydet
        tasks_collection = self.db.collection("projects").document(project_id).collection("tasks")
        
        for task in tasks:
            task_id = task.get("task_id", f"task_{uuid.uuid4().hex[:8]}")
            
            # Field name mapping: Groq service'den gelen field isimlerini frontend'in beklediği isimlere dönüştür
            task_stack = task.get("task_stack", task.get("required_stack", []))
            # Eğer string ise, virgülle ayırarak array'e çevir
            if isinstance(task_stack, str):
                task_stack = [tech.strip() for tech in task_stack.split(",") if tech.strip()]
            
            normalized_task = {
                "task_id": task_id,
                "project_id": project_id,
                "title": task.get("task_title", task.get("title", "")),
                "detail": task.get("task_detail", task.get("detail", "")),
                "required_stack": task_stack if isinstance(task_stack, list) else [],
                "department": task.get("department", ""),
                "source": task.get("source", ""),
                "status": task.get("status", "pending"),
                "assigned_to": task.get("assigned_to"),
                "task_attended_to": task.get("task_attended_to", ""),
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            tasks_collection.document(task_id).set(normalized_task, merge=True)
        
        print(f"[FirebaseDB] Görevler kaydedildi: {project_id}, toplam {len(tasks)} görev")
    
    def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Proje görevlerini getirir."""
        tasks = []
        tasks_collection = self.db.collection("projects").document(project_id).collection("tasks")
        docs = tasks_collection.stream()
        
        for doc in docs:
            task_data = doc.to_dict()
            tasks.append(task_data)
        
        return tasks
    
    # --- COMPANY STRUCTURE METHODS ---
    def save_company_structure(self, company_data: Dict[str, Any]):
        """Şirket yapısını kaydeder."""
        company_with_meta = {
            **company_data,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.db.collection("settings").document("company_structure").set(company_with_meta, merge=True)
        print(f"[FirebaseDB] Şirket yapısı kaydedildi")
    
    def get_company_structure(self) -> Optional[Dict[str, Any]]:
        """Şirket yapısını getirir."""
        doc = self.db.collection("settings").document("company_structure").get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    # --- CONTRACT METHODS (NEW) ---
    def save_contract(self, contract_id: str, contract_data: Dict[str, Any]):
        """Sözleşme verisini kaydeder."""
        contract_with_meta = {
            **contract_data,
            "contract_id": contract_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.db.collection("contracts").document(contract_id).set(contract_with_meta, merge=True)
        print(f"[FirebaseDB] Sözleşme kaydedildi: {contract_id}")
    
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Sözleşme verisini getirir."""
        doc = self.db.collection("contracts").document(contract_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def list_contracts(self) -> List[Dict[str, Any]]:
        """Tüm sözleşmeleri listeler."""
        contracts = []
        docs = self.db.collection("contracts").stream()
        
        for doc in docs:
            contract_data = doc.to_dict()
            contracts.append(contract_data)
        
        return contracts
    
    def upload_file(self, file_path: str, file_content: bytes, content_type: str) -> str:
        """
        Dosyayı Firebase Storage'a yükler ve public URL'ini döner.
        
        Args:
            file_path: Storage'daki hedef dosya yolu (örn: "contracts/abc123.pdf")
            file_content: Dosya içeriği (bytes)
            content_type: MIME tipi (örn: "application/pdf")
        
        Returns:
            Dosyanın public URL'si
        """
        try:
            # Blob oluştur
            blob = self.bucket.blob(file_path)
            
            # Dosyayı yükle
            blob.upload_from_string(file_content, content_type=content_type)
            
            # Public yap
            blob.make_public()
            
            # Public URL'i döner
            print(f"[FirebaseDB] Dosya yüklendi: {file_path}")
            return blob.public_url
            
        except Exception as e:
            print(f"[FirebaseDB ERROR] Dosya yükleme hatası: {e}")
            raise
    
    # --- SPRINT METHODS (NEW) ---
    def save_sprint(self, project_id: str, sprint_data: Dict[str, Any]):
        """Sprint planını kaydeder."""
        sprint_id = sprint_data.get("sprint_id", f"sprint_{uuid.uuid4().hex[:8]}")
        sprint_with_meta = {
            **sprint_data,
            "sprint_id": sprint_id,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Sprint'i hem projects/project_id/sprints altına hem de sprints koleksiyonuna kaydet
        self.db.collection("projects").document(project_id).collection("sprints").document(sprint_id).set(sprint_with_meta, merge=True)
        self.db.collection("sprints").document(sprint_id).set(sprint_with_meta, merge=True)
        
        print(f"[FirebaseDB] Sprint kaydedildi: {sprint_id} (project: {project_id})")
    
    def get_sprints(self, project_id: str) -> List[Dict[str, Any]]:
        """Projeye ait tüm sprintleri getirir."""
        sprints = []
        sprints_collection = self.db.collection("projects").document(project_id).collection("sprints")
        docs = sprints_collection.order_by("created_at", direction=firestore.Query.DESCENDING).stream()
        
        for doc in docs:
            sprint_data = doc.to_dict()
            sprints.append(sprint_data)
        
        return sprints
    
    def get_sprint(self, sprint_id: str) -> Optional[Dict[str, Any]]:
        """Sprint verisini getirir."""
        doc = self.db.collection("sprints").document(sprint_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def update_sprint_status(self, sprint_id: str, status: str):
        """Sprint durumunu günceller."""
        self.db.collection("sprints").document(sprint_id).update({
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        })
        print(f"[FirebaseDB] Sprint durumu güncellendi: {sprint_id} -> {status}")
    
    # --- EMPLOYEE METHODS ---
    def list_employees(self) -> List[Dict[str, Any]]:
        """Tüm çalışanları listeler."""
        employees = []
        docs = self.db.collection("employees").stream()
        
        for doc in docs:
            employee_data = doc.to_dict()
            employees.append(employee_data)
        
        return employees
    
    def get_employee(self, employee_id: str) -> Optional[Dict[str, Any]]:
        """Çalışan verisini getirir."""
        doc = self.db.collection("employees").document(employee_id).get()
        
        if doc.exists:
            return doc.to_dict()
        return None
    
    def get_employees_by_department(self, department: str) -> List[Dict[str, Any]]:
        """Departmana göre çalışanları getirir."""
        employees = []
        docs = self.db.collection("employees").where("department", "==", department).stream()
        
        for doc in docs:
            employee_data = doc.to_dict()
            employees.append(employee_data)
        
        return employees
    
    # --- NEW DYNAMIC SPRINT MANAGEMENT METHODS ---
    
    def update_employee_availability(self, employee_id: str, status: str, until_date: Optional[str] = None, reason: Optional[str] = None):
        """
        Çalışan müsaitlik durumunu günceller.
        
        Args:
            employee_id: Çalışan ID'si
            status: available, unavailable, limited
            until_date: ISO formatında tarih (opsiyonel)
            reason: Unavailable olma nedeni (opsiyonel)
        """
        company_structure = self.get_company_structure()
        if not company_structure:
            raise ValueError("Şirket yapısı bulunamadı")
        
        # Çalışanı bul ve güncelle
        updated = False
        for dept in company_structure.get("companyStructure", {}).get("departments", []):
            for team in dept.get("teams", []):
                for i, employee in enumerate(team.get("employees", [])):
                    if employee.get("id") == employee_id:
                        team["employees"][i]["availability_status"] = status
                        if until_date:
                            team["employees"][i]["unavailable_until"] = until_date
                        if reason:
                            team["employees"][i]["unavailable_reason"] = reason
                        updated = True
                        break
                if updated:
                    break
            if updated:
                break
        
        if updated:
            self.save_company_structure(company_structure)
            print(f"[FirebaseDB] Çalışan müsaitliği güncellendi: {employee_id} -> {status}")
        else:
            raise ValueError(f"Çalışan bulunamadı: {employee_id}")
    
    def get_employee_tasks(self, employee_id: str) -> List[Dict[str, Any]]:
        """
        Bir çalışana atanmış tüm görevleri getirir.
        
        Args:
            employee_id: Çalışan ID'si
            
        Returns:
            Görev listesi
        """
        tasks = []
        
        # Tüm projeleri al
        projects = self.list_projects()
        
        for project in projects:
            project_id = project.get("project_id")
            if project_id:
                project_tasks = self.get_tasks(project_id)
                # Bu çalışana atanmış görevleri filtrele
                for task in project_tasks:
                    if task.get("assigned_employee_id") == employee_id:
                        tasks.append(task)
        
        return tasks
    
    def update_task_dates(self, task_id: str, project_id: str, start_date: Optional[str] = None, due_date: Optional[str] = None):
        """
        Görev tarihlerini günceller.
        
        Args:
            task_id: Görev ID'si
            project_id: Proje ID'si
            start_date: Başlangıç tarihi (ISO format)
            due_date: Bitiş tarihi (ISO format)
        """
        task_ref = self.db.collection("projects").document(project_id).collection("tasks").document(task_id)
        
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        if start_date:
            update_data["start_date"] = start_date
        if due_date:
            update_data["due_date"] = due_date
        
        task_ref.update(update_data)
        print(f"[FirebaseDB] Görev tarihleri güncellendi: {task_id}")
    
    def update_task_status(self, task_id: str, project_id: str, status: str, blocked_reason: Optional[str] = None):
        """
        Görev durumunu günceller.
        
        Args:
            task_id: Görev ID'si
            project_id: Proje ID'si
            status: not_started, in_progress, blocked, completed
            blocked_reason: Eğer status=blocked ise, nedeni
        """
        task_ref = self.db.collection("projects").document(project_id).collection("tasks").document(task_id)
        
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        if blocked_reason:
            update_data["blocked_reason"] = blocked_reason
        
        task_ref.update(update_data)
        print(f"[FirebaseDB] Görev durumu güncellendi: {task_id} -> {status}")
    
    def reassign_task(self, task_id: str, project_id: str, new_employee_id: str, new_employee_name: str, reassignment_reason: str):
        """
        Görevi yeni bir çalışana atar.
        
        Args:
            task_id: Görev ID'si
            project_id: Proje ID'si
            new_employee_id: Yeni çalışan ID'si
            new_employee_name: Yeni çalışan adı
            reassignment_reason: Yeniden atama nedeni
        """
        task_ref = self.db.collection("projects").document(project_id).collection("tasks").document(task_id)
        
        task_ref.update({
            "assigned_employee_id": new_employee_id,
            "task_attended_to": new_employee_name,
            "assignment_reason": reassignment_reason,
            "reassigned_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        print(f"[FirebaseDB] Görev yeniden atandı: {task_id} -> {new_employee_name}")
    
    def get_sprint_by_number(self, project_id: str, sprint_number: int) -> Optional[Dict[str, Any]]:
        """
        Proje içinde sprint numarasına göre sprint getirir.
        
        Args:
            project_id: Proje ID'si
            sprint_number: Sprint numarası
            
        Returns:
            Sprint verisi veya None
        """
        sprints_collection = self.db.collection("projects").document(project_id).collection("sprints")
        docs = sprints_collection.where("current_sprint_number", "==", sprint_number).limit(1).stream()
        
        for doc in docs:
            return doc.to_dict()
        
        return None
    
    def calculate_sprint_dates(self, start_date: str, sprint_duration_weeks: int, total_sprints: int) -> List[Dict[str, str]]:
        """
        Sprint tarihlerini hesaplar.
        
        Args:
            start_date: Başlangıç tarihi (ISO format)
            sprint_duration_weeks: Sprint süresi (hafta)
            total_sprints: Toplam sprint sayısı
            
        Returns:
            Her sprint için start_date ve end_date içeren liste
        """
        from datetime import datetime, timedelta
        
        sprint_dates = []
        current_start = datetime.fromisoformat(start_date)
        
        for i in range(total_sprints):
            sprint_end = current_start + timedelta(weeks=sprint_duration_weeks)
            
            sprint_dates.append({
                "sprint_number": i + 1,
                "start_date": current_start.isoformat()[:10],
                "end_date": sprint_end.isoformat()[:10]
            })
            
            current_start = sprint_end
        
        return sprint_dates
    
    def update_sprint_health(self, sprint_id: str, health_score: float, risk_factors: List[Dict[str, Any]]):
        """
        Sprint sağlık skorunu ve risk faktörlerini günceller.
        
        Args:
            sprint_id: Sprint ID'si
            health_score: Sağlık skoru (0-100)
            risk_factors: Risk faktörleri listesi
        """
        self.db.collection("sprints").document(sprint_id).update({
            "health_score": health_score,
            "risk_factors": risk_factors,
            "health_updated_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        
        print(f"[FirebaseDB] Sprint sağlık skoru güncellendi: {sprint_id} -> {health_score}")