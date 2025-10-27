from pydantic import BaseModel
from typing import Dict, Any, Optional, List

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str
    requires_confirmation: Optional[bool] = False
    confirmation_data: Optional[Dict[str, Any]] = None

class ConfirmationRequest(BaseModel):
    session_id: str
    action_type: str  # "assign_task", "reassign_task", "update_availability", "replan_sprints"
    action_data: Dict[str, Any]
    confirmed: bool

class ConfirmationResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None
    alternatives: Optional[List[Dict[str, Any]]] = None
    risks: Optional[List[str]] = None

class TaskAssignmentConfirmation(BaseModel):
    task_title: str
    project_id: str
    suggested_employee: Dict[str, Any]
    alternatives: List[Dict[str, Any]]
    assignment_reason: str
    confidence_score: float
    potential_risks: List[str]

class TaskReassignmentConfirmation(BaseModel):
    task_title: str
    project_id: str
    from_employee: str
    to_employee: Dict[str, Any]
    reassignment_reason: str
    cascade_risks: List[str]
    confidence_score: float

class AvailabilityUpdateConfirmation(BaseModel):
    employee_id: str
    employee_name: str
    new_status: str
    unavailable_until: Optional[str] = None
    reason: str
    affected_tasks: List[Dict[str, Any]]
    reassignment_needed: bool

class SprintReplanConfirmation(BaseModel):
    project_id: str
    vacation_days: int
    delays: int
    affected_sprints: List[Dict[str, Any]]
    new_timeline: Dict[str, Any]
    risks: List[str]
