from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uuid
from app.firebase_db import FirebaseDatabase
from app.tools import inject_dependencies, list_employees, get_employee_info, get_department_workload, update_employee_availability

router = APIRouter()

_db_client = None
def get_db():
    global _db_client
    if _db_client is None:
        _db_client = FirebaseDatabase()
    return _db_client

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
        inject_dependencies(get_db(), "api_session")
        
        # list_employees tool'unu çağır (LangChain tool - .invoke() kullan)
        result = list_employees.invoke({"department": department})
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
        inject_dependencies(get_db(), "api_session")
        
        # get_employee_info tool'unu çağır (LangChain tool - .invoke() kullan)
        result = get_employee_info.invoke({"employee_id": employee_id})
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
        inject_dependencies(get_db(), "api_session")
        
        # get_department_workload tool'unu çağır (LangChain tool - .invoke() kullan)
        result = get_department_workload.invoke({"department": department})
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
        company_data = get_db().get_company_structure()
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
        get_db().save_company_structure(company_data)
        
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
        company_data = get_db().get_company_structure()
        if not company_data:
            raise HTTPException(status_code=404, detail="Şirket yapısı bulunamadı")
        
        # Çalışanı bul ve güncelle
        for department in company_data.get("companyStructure", {}).get("departments", []):
            for team in department.get("teams", []):
                for employee in team.get("employees", []):
                    if employee["id"] == employee_id:
                        employee["currentWorkload"] = workload
                        get_db().save_company_structure(company_data)
                        return {"message": f"Çalışan iş yükü güncellendi: {workload}"}
        
        raise HTTPException(status_code=404, detail="Çalışan bulunamadı")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan iş yükü güncelleme hatası: {str(e)}")


# --- NEW DYNAMIC SPRINT MANAGEMENT ENDPOINTS ---

class EmployeeAvailabilityUpdate(BaseModel):
    status: str  # available, unavailable, limited
    unavailable_until: Optional[str] = None  # ISO date
    reason: Optional[str] = None


@router.put("/{employee_id}/availability")
async def update_availability(employee_id: str, data: EmployeeAvailabilityUpdate):
    """
    Çalışan müsaitlik durumunu günceller.
    """
    try:
        # Tools'a dependency injection yap
        inject_dependencies(get_db(), "api_session")
        
        # update_employee_availability tool'unu çağır
        result = update_employee_availability.invoke({
            "employee_id": employee_id,
            "status": data.status,
            "unavailable_until": data.unavailable_until,
            "reason": data.reason
        })
        
        import json
        result_data = json.loads(result)
        
        if "error" in result_data:
            raise HTTPException(status_code=400, detail=result_data["error"])
        
        return result_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Müsaitlik güncelleme hatası: {str(e)}")


@router.get("/{employee_id}/tasks")
async def get_employee_tasks(employee_id: str):
    """
    Bir çalışanın aktif görevlerini getirir.
    """
    try:
        tasks = get_db().get_employee_tasks(employee_id)
        
        return {
            "employee_id": employee_id,
            "total_tasks": len(tasks),
            "tasks": tasks
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Çalışan görevleri getirme hatası: {str(e)}")
