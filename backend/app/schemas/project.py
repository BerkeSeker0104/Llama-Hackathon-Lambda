from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class ProjectBase(BaseModel):
    detailedDescription: str
    department: str
    techStack: List[str]
    acceptanceCriteria: List[str]

class ProjectCreate(ProjectBase):
    project_name: Optional[str] = "New Project"

class ProjectUpdate(BaseModel):
    detailedDescription: Optional[str] = None
    department: Optional[str] = None
    techStack: Optional[List[str]] = None
    acceptanceCriteria: Optional[List[str]] = None

class Project(ProjectBase):
    project_id: str
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class ProjectAnalysis(BaseModel):
    missingInfo: List[str]
    risks: List[str]
    contradictions: List[str]

class ProjectCriticalAnalysis(BaseModel):
    criticalAnalysis: ProjectAnalysis

class ProjectTimeline(BaseModel):
    startDate: Optional[str] = None
    endDate: Optional[str] = None

class ProjectAnalysisResult(BaseModel):
    detailedDescription: str
    criticalAnalysis: ProjectCriticalAnalysis
    department: str
    techStack: List[str]
    timeline: ProjectTimeline
    acceptanceCriteria: List[str]
