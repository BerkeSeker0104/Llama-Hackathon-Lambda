from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, analyze_contract_document

router = APIRouter()
db_client = FirebaseDatabase()

class ContractAnalysisRequest(BaseModel):
    contract_text: str
    contract_name: str = "Contract Document"

class ContractAnalysisResponse(BaseModel):
    status: str
    contract_id: str
    message: str
    analysis: Dict[str, Any]

class ContractResponse(BaseModel):
    contract_id: str
    contract_name: str
    contract_text: str
    analysis: Dict[str, Any]
    status: str
    created_at: str

@router.get("/")
async def get_contracts():
    """
    Tüm sözleşmeleri listele.
    """
    try:
        contracts = db_client.list_contracts()
        return {"contracts": contracts}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme listesi getirme hatası: {str(e)}")

@router.get("/{contract_id}")
async def get_contract(contract_id: str):
    """
    Belirli bir sözleşmenin detaylarını getir.
    """
    try:
        contract = db_client.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        return contract
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme detayı getirme hatası: {str(e)}")

@router.post("/upload")
async def upload_contract(file: UploadFile = File(...)):
    """
    PDF sözleşme dosyasını yükle.
    """
    try:
        # Dosya boyutunu kontrol et (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="Dosya boyutu çok büyük (max 10MB)")
        
        # Dosya tipini kontrol et
        if not file.content_type == "application/pdf":
            raise HTTPException(status_code=400, detail="Sadece PDF dosyaları kabul edilir")
        
        # Dosyayı oku
        file_content = await file.read()
        
        # Firebase Storage'a yükle
        file_path = f"contracts/{uuid.uuid4().hex}.pdf"
        file_url = db_client.upload_file(file_path, file_content, "application/pdf")
        
        # Contract kaydı oluştur
        contract_id = f"contract_{uuid.uuid4().hex[:8]}"
        contract_data = {
            "contract_name": file.filename,
            "file_path": file_path,
            "file_url": file_url,
            "status": "uploaded",
            "file_size": file.size
        }
        db_client.save_contract(contract_id, contract_data)
        
        return {
            "contract_id": contract_id,
            "file_url": file_url,
            "message": "Sözleşme başarıyla yüklendi"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme yükleme hatası: {str(e)}")

@router.post("/analyze", response_model=ContractAnalysisResponse)
async def analyze_contract(request: ContractAnalysisRequest):
    """
    Sözleşme metnini analiz et.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # analyze_contract_document tool'unu çağır
        result = analyze_contract_document(request.contract_text, request.contract_name)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return ContractAnalysisResponse(**result_data)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme analiz hatası: {str(e)}")

@router.post("/{contract_id}/convert-to-project")
async def convert_contract_to_project(contract_id: str):
    """
    Sözleşmeyi projeye dönüştür.
    """
    try:
        # Sözleşmeyi al
        contract = db_client.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        # Sözleşme metnini al
        contract_text = contract.get("contract_text", "")
        if not contract_text:
            raise HTTPException(status_code=400, detail="Sözleşme metni bulunamadı")
        
        # Proje analizi yap
        from app.tools import analyze_project_text
        inject_dependencies(db_client, "api_session")
        
        result = analyze_project_text(contract_text, contract.get("contract_name", "Contract Project"))
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        # Sözleşme durumunu güncelle
        contract["status"] = "converted_to_project"
        contract["project_id"] = result_data["project_id"]
        db_client.save_contract(contract_id, contract)
        
        return {
            "message": "Sözleşme başarıyla projeye dönüştürüldü",
            "project_id": result_data["project_id"],
            "analysis": result_data["analysis"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme dönüştürme hatası: {str(e)}")

@router.delete("/{contract_id}")
async def delete_contract(contract_id: str):
    """
    Sözleşmeyi sil.
    """
    try:
        # Sözleşmeyi al
        contract = db_client.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Sözleşme bulunamadı")
        
        # Dosyayı Storage'dan sil
        if contract.get("file_path"):
            try:
                blob = db_client.bucket.blob(contract["file_path"])
                blob.delete()
            except:
                pass  # Dosya zaten silinmiş olabilir
        
        # Sözleşmeyi sil
        db_client.db.collection('contracts').document(contract_id).delete()
        
        return {"message": f"Sözleşme silindi: {contract_id}"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sözleşme silme hatası: {str(e)}")
