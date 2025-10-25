from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, list_employees, get_employee_info, get_department_workload

router = APIRouter()
db_client = FirebaseDatabase()

class EmployeeResponse(BaseModel):
    id: str
    name: str
    role: str
    department: str
    team: str
    techStack: List[str]
    workload: str

class DepartmentWorkloadResponse(BaseModel):
    department: str
    total_employees: int
    workload_distribution: Dict[str, int]
    employees: List[Dict[str, Any]]

@router.get("/")
async def get_employees(department: Optional[str] = None):
    """
    Çalışanları listele.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # list_employees tool'unu çağır
        result = list_employees(department)
        import json
        return json.loads(result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan listesi getirme hatası: {str(e)}")

@router.get("/{employee_id}")
async def get_employee(employee_id: str):
    """
    Belirli bir çalışanın detaylarını getir.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # get_employee_info tool'unu çağır
        result = get_employee_info(employee_id)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=404, detail=result_data["error"])
        
        return result_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan detayı getirme hatası: {str(e)}")

@router.get("/departments/{department}/workload")
async def get_department_workload(department: str):
    """
    Departman iş yükünü getir.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(db_client, "api_session")
        
        # get_department_workload tool'unu çağır
        result = get_department_workload(department)
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=404, detail=result_data["error"])
        
        return result_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Departman iş yükü getirme hatası: {str(e)}")

@router.post("/import")
async def import_employees(csv_data: str):
    """
    CSV'den çalışan verilerini içe aktar.
    """
    try:
        import csv
        import io
        
        # CSV'yi parse et
        csv_reader = csv.DictReader(io.StringIO(csv_data))
        employees = []
        
        for row in csv_reader:
            employee = {
                "id": f"emp_{uuid.uuid4().hex[:8]}",
                "firstName": row.get("firstName", ""),
                "lastName": row.get("lastName", ""),
                "role": row.get("role", ""),
                "department": row.get("department", ""),
                "team": row.get("team", ""),
                "techStack": row.get("techStack", "").split(",") if row.get("techStack") else [],
                "currentWorkload": row.get("workload", "medium")
            }
            employees.append(employee)
        
        # Şirket yapısını güncelle
        company_data = db_client.get_company_structure()
        if not company_data:
            # Yeni şirket yapısı oluştur
            company_data = {
                "companyStructure": {
                    "departments": []
                }
            }
        
        # Departmanları grupla
        departments = {}
        for emp in employees:
            dept_name = emp["department"]
            if dept_name not in departments:
                departments[dept_name] = {
                    "name": dept_name,
                    "teams": {}
                }
            
            team_name = emp["team"]
            if team_name not in departments[dept_name]["teams"]:
                departments[dept_name]["teams"][team_name] = {
                    "name": team_name,
                    "employees": []
                }
            
            departments[dept_name]["teams"][team_name]["employees"].append(emp)
        
        # Yapıyı güncelle
        company_data["companyStructure"]["departments"] = list(departments.values())
        db_client.save_company_structure(company_data)
        
        return {"message": f"{len(employees)} çalışan başarıyla içe aktarıldı"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan içe aktarma hatası: {str(e)}")

@router.put("/{employee_id}/workload")
async def update_employee_workload(employee_id: str, workload: str):
    """
    Çalışan iş yükünü güncelle.
    """
    try:
        # Çalışanı bul ve güncelle
        company_data = db_client.get_company_structure()
        if not company_data:
            raise HTTPException(status_code=404, detail="Şirket yapısı bulunamadı")
        
        # Çalışanı bul ve güncelle
        for department in company_data.get("companyStructure", {}).get("departments", []):
            for team in department.get("teams", []):
                for employee in team.get("employees", []):
                    if employee["id"] == employee_id:
                        employee["currentWorkload"] = workload
                        db_client.save_company_structure(company_data)
                        return {"message": f"Çalışan iş yükü güncellendi: {workload}"}
        
        raise HTTPException(status_code=404, detail="Çalışan bulunamadı")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan iş yükü güncelleme hatası: {str(e)}")
