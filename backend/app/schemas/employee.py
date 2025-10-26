from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class EmployeeBase(BaseModel):
    firstName: str
    lastName: str
    role: str
    techStack: List[str]
    currentWorkload: str
    availability_status: Optional[str] = "available"  # available, unavailable, limited
    unavailable_until: Optional[str] = None  # ISO date
    unavailable_reason: Optional[str] = None
    current_task_ids: Optional[List[str]] = []

class EmployeeCreate(EmployeeBase):
    department: str
    team: str

class EmployeeUpdate(BaseModel):
    firstName: Optional[str] = None
    lastName: Optional[str] = None
    role: Optional[str] = None
    techStack: Optional[List[str]] = None
    currentWorkload: Optional[str] = None

class Employee(EmployeeBase):
    id: str
    department: str
    team: str
    name: str
    
    class Config:
        from_attributes = True

class EmployeeInfo(Employee):
    pass

class DepartmentWorkload(BaseModel):
    department: str
    total_employees: int
    workload_distribution: Dict[str, int]
    employees: List[Dict[str, Any]]

class EmployeeList(BaseModel):
    total_employees: int
    employees: List[Employee]
