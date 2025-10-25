from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class ContractBase(BaseModel):
    contract_name: str
    contract_text: Optional[str] = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    contract_name: Optional[str] = None
    contract_text: Optional[str] = None
    status: Optional[str] = None

class Contract(ContractBase):
    contract_id: str
    file_path: Optional[str] = None
    file_url: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    status: str
    project_id: Optional[str] = None
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True

class ContractAnalysis(BaseModel):
    ambiguities: List[Dict[str, Any]]
    risks: List[Dict[str, Any]]
    riskScore: int
    missingInfo: List[str]

class ContractAnalysisRequest(BaseModel):
    contract_text: str
    contract_name: str = "Contract Document"

class ContractAnalysisResponse(BaseModel):
    status: str
    contract_id: str
    message: str
    analysis: ContractAnalysis
