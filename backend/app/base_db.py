from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseDatabase(ABC):
    """
    Veritabanı işlemleri için soyut temel sınıf (arayüz).
    Bu, LocalDatabase'den FirebaseDatabase'e geçişi kolaylaştırır.
    """
    
    # --- CHAT HISTORY METHODS ---
    @abstractmethod
    def get_chat_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Verilen ID'ye ait tüm konuşma geçmişini getirir."""
        pass

    @abstractmethod
    def save_message(self, session_id: str, message: Dict[str, Any]):
        """Bir mesajı (user, assistant, tool) konuşma geçmişine kaydeder."""
        pass
    
    # --- PROJECT METHODS ---
    @abstractmethod
    def save_project(self, project_id: str, project_data: Dict[str, Any]):
        """Proje verisini kaydeder."""
        pass
    
    @abstractmethod
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Proje verisini getirir."""
        pass
    
    @abstractmethod
    def list_projects(self) -> List[Dict[str, Any]]:
        """Tüm projeleri listeler."""
        pass
    
    @abstractmethod
    def set_active_project(self, session_id: str, project_id: str):
        """Aktif projeyi ayarlar."""
        pass
    
    @abstractmethod
    def get_active_project(self, session_id: str) -> Optional[str]:
        """Aktif proje ID'sini getirir."""
        pass
    
    # --- TASK METHODS ---
    @abstractmethod
    def save_tasks(self, project_id: str, tasks: List[Dict[str, Any]]):
        """Görevleri kaydeder."""
        pass
    
    @abstractmethod
    def get_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """Proje görevlerini getirir."""
        pass
    
    # --- COMPANY STRUCTURE METHODS ---
    @abstractmethod
    def save_company_structure(self, company_data: Dict[str, Any]):
        """Şirket yapısını kaydeder."""
        pass
    
    @abstractmethod
    def get_company_structure(self) -> Optional[Dict[str, Any]]:
        """Şirket yapısını getirir."""
        pass
    
    # --- CONTRACT METHODS (NEW) ---
    @abstractmethod
    def save_contract(self, contract_id: str, contract_data: Dict[str, Any]):
        """Sözleşme verisini kaydeder."""
        pass
    
    @abstractmethod
    def get_contract(self, contract_id: str) -> Optional[Dict[str, Any]]:
        """Sözleşme verisini getirir."""
        pass
    
    @abstractmethod
    def list_contracts(self) -> List[Dict[str, Any]]:
        """Tüm sözleşmeleri listeler."""
        pass
    
    # --- SPRINT METHODS (NEW) ---
    @abstractmethod
    def save_sprint(self, project_id: str, sprint_data: Dict[str, Any]):
        """Sprint planını kaydeder."""
        pass
    
    @abstractmethod
    def get_sprints(self, project_id: str) -> List[Dict[str, Any]]:
        """Projeye ait tüm sprintleri getirir."""
        pass
    
    @abstractmethod
    def get_sprint(self, sprint_id: str) -> Optional[Dict[str, Any]]:
        """Sprint verisini getirir."""
        pass
    
    @abstractmethod
    def update_sprint_status(self, sprint_id: str, status: str):
        """Sprint durumunu günceller."""
        pass