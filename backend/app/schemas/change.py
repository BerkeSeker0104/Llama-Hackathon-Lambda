from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ChangeRequestBase(BaseModel):
    change_text: str
    project_id: str

class ChangeRequestCreate(ChangeRequestBase):
    pass

class ChangeRequestUpdate(BaseModel):
    change_text: Optional[str] = None
    status: Optional[str] = None

class ChangeRequest(ChangeRequestBase):
    change_id: str
    classification: Dict[str, Any]
    status: str
    action_taken: Optional[str] = None
    applied_at: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

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
