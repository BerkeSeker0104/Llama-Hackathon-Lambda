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
        
        # Array'e ekle
        doc_ref.update({
            "messages": firestore.ArrayUnion([message_with_timestamp])
        })
    
    # --- PROJECT METHODS ---
    def save_project(self, project_id: str, project_data: Dict[str, Any]):
        """Proje verisini kaydeder."""
        project_with_meta = {
            **project_data,
            "project_id": project_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        self.db.collection("projects").document(project_id).set(project_with_meta, merge=True)
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
            task_with_meta = {
                **task,
                "task_id": task_id,
                "project_id": project_id,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            tasks_collection.document(task_id).set(task_with_meta, merge=True)
        
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
