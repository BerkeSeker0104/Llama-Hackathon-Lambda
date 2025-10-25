from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SprintBase(BaseModel):
    project_id: str
    sprint_duration_weeks: int

class SprintCreate(SprintBase):
    pass

class SprintUpdate(BaseModel):
    sprint_duration_weeks: Optional[int] = None
    status: Optional[str] = None

class Sprint(SprintBase):
    sprint_id: str
    plan: Dict[str, Any]
    status: str
    original_sprint_id: Optional[str] = None
    vacation_days: Optional[int] = None
    delays: Optional[int] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

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
