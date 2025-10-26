from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class TaskBase(BaseModel):
    task_title: str
    task_detail: str
    task_stack: str
    department: str
    source: str
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    blocked_reason: Optional[str] = None
    priority: Optional[str] = "medium"  # low, medium, high, critical
    start_date: Optional[str] = None  # ISO date
    due_date: Optional[str] = None  # ISO date
    dependencies: Optional[List[str]] = []  # task_id'ler

class TaskCreate(TaskBase):
    project_id: str

class TaskUpdate(BaseModel):
    task_title: Optional[str] = None
    task_detail: Optional[str] = None
    task_stack: Optional[str] = None
    department: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    task_attended_to: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    assignment_reason: Optional[str] = None

class Task(TaskBase):
    task_id: str
    project_id: str
    task_attended_to: Optional[str] = None
    assigned_employee_id: Optional[str] = None
    assignment_reason: Optional[str] = None
    status: str = "not_started"  # not_started, in_progress, blocked, completed
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class TaskAssignment(BaseModel):
    task_title: str
    project_id: Optional[str] = None

class TaskAssignmentResult(BaseModel):
    status: str
    task_title: str
    assigned_to: str
    reason: str
