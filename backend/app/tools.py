import json
from typing import Dict, Any, Optional
from langchain_core.tools import tool
from groq import Groq
import os
import uuid

# This will be injected by the orchestrator
_db_instance = None
_session_id = None

def inject_dependencies(db_instance, session_id: str):
    """Orchestrator tarafından çağrılır, tools'a DB erişimi verir."""
    global _db_instance, _session_id
    _db_instance = db_instance
    _session_id = session_id

# --- PROJECT ANALYSIS SYSTEM PROMPT ---
PROJECT_ANALYSIS_PROMPT = """
Sen, bir ürün yöneticisi tarafından yazılan kodlama projesi görevlerini (task) analiz eden kıdemli bir teknik analiz uzmanısın.
Görevin, sana verilen görev metnini analiz etmek ve SADECE ve SADECE 
istenen bilgileri içeren geçerli bir JSON nesnesi döndürmektir. 
Başka hiçbir açıklama, selamlama veya yorum yapma.

Çıkarım yapman, metindeki belirsizlikleri fark etmen ve teknik gereksinimleri tahmin etmen gerekiyor.

İstenen JSON yapısı şu şekilde olmalıdır:
{
  "detailedDescription": "Metinden çıkarılan, projenin tam kapsamını ve temel hedeflerini detaylıca anlatan bir paragraf.",
  "criticalAnalysis": {
    "missingInfo": [
      "Projenin netleşmesi için metinde bulunmayan kritik eksik bilgiler. Eğer eksik bilgi yoksa boş bir dizi [] döndür."
    ],
    "risks": [
      "Metindeki ifadelere dayanarak öngörülen teknik veya operasyonel riskler. Eğer belirgin bir risk yoksa boş bir dizi [] döndür."
    ],
    "contradictions": [
      "Metin içinde birbiriyle çelişen ifadeler veya hedefler. Eğer çelişki yoksa boş bir dizi [] döndür."
    ]
  },
  "department": "Bu görevin birincil sorumlusu olması gereken departman veya ekip (örn: 'Backend', 'Frontend', 'Data Science', 'DevOps', 'Mobile'). Metinden bu çıkarımı yap.",
  "techStack": [
    "Metinde açıkça belirtilen veya görevin doğası gereği zorunlu olduğu çıkarımı yapılan teknolojiler."
  ],
  "timeline": {
    "startDate": "YYYY-MM-DD formatında projenin tahmini başlangıç tarihi (eğer metinde spesifik bir tarih varsa, yoksa null)",
    "endDate": "YYYY-MM-DD formatında projenin teslim tarihi (eğer metinde spesifik bir tarih varsa, yoksa null)"
  },
  "acceptanceCriteria": [
    "Görevin 'tamamlandı' sayılması için karşılanması gereken spesifik, ölçülebilir ve test edilebilir şartlar."
  ]
}
"""

# --- TASK GENERATION SYSTEM PROMPT ---
TASK_GENERATION_PROMPT = """
Sen, deneyimli bir proje yöneticisi ve görev çıkarıcı AI asistanısın.
Amacın, verilen proje dokümanını (açıklama, teslimatlar, kabul kriterleri) inceleyip, bu projede yapılması gereken önemli görevleri belirlemektir.
Çıktı SADECE ve SADECE aşağıdaki JSON formatında, bir görev dizisi (array) olmalı. Başka hiçbir açıklama ekleme.

[
  {
    "task_title": "Görevin kısa başlığı",
    "task_detail": "Bu görevde yapılması gereken önemli işin kısa açıklaması.",
    "task_stack": "Bu görevde kullanılacak teknolojiler, diller veya frameworkler.",
    "source": "Bu görevin hangi teslimat/maddeden çıkarıldığı.",
    "task_attended_to": "",
    "department": "Bu görev hangi departmana aitse (karşıdan verilen 'department' bilgisini BURADA TEKRARLA, LLM URETME)."
  }
]

Kurallar:
- Gereksiz görev ekleme, anlamlı ve iş üretilecek düzeyde spesifik görevler çıkar.
- Her görevin 'source' alanında dayandığı maddeyi ya da türünü belirt.
- Görevlerde teknolojiler ve önemli çıkacak adımları belirt.
- DİKKAT: 'department' alanı sadece gelen proje verisinden (department) alınmalı.
"""

# --- TASK ASSIGNMENT SYSTEM PROMPT ---
TASK_ASSIGNMENT_PROMPT = """
Sen, bir şirketin insan kaynakları ve proje yönetimi için görev atama yapan uzman bir AI asistanısın.
Görevin, verilen bir TASK'ı (görev) ve şirketin çalışan listesini inceleyip, bu görevi EN UYGUN kişiye atamaktır.

Atama yaparken şu kriterleri dikkate al (önem sırasına göre):
1. **Tech Stack Uyumu**: Görevde belirtilen teknolojilerin çalışanın tech stack'inde olması
2. **Workload (İş Yükü)**: Düşük iş yükü olan çalışanları tercih et (low > medium > high)
3. **Departman/Team Uyumu**: Görevin departmanı ile çalışanın departmanı uyumlu olmalı
4. **Role/Seniority**: Görevin karmaşıklığına uygun deneyim seviyesi

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "assigned_employee_id": "emp_xxx",
  "assigned_employee_name": "Ad Soyad",
  "assignment_reason": "Kısa açıklama: Bu kişi neden seçildi?"
}

Başka hiçbir açıklama veya metin ekleme.
"""

# --- PROJECT TOOLS ---

@tool
def list_projects():
    """
    Tüm projeleri listeler.
    """
    print(f"[Tool Log] 'list_projects' çağrıldı")
    
    projects = _db_instance.list_projects()
    active_project_id = _db_instance.get_active_project(_session_id)
    
    result = {
        "total_projects": len(projects),
        "active_project_id": active_project_id,
        "projects": [
            {
                "project_id": p.get("project_id"),
                "project_name": p.get("project_name", "N/A"),
                "detailedDescription": p.get("detailedDescription", "N/A")[:150]
            }
            for p in projects
        ]
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def get_project_details(project_id: Optional[str] = None):
    """
    Belirtilen projenin detaylarını getirir. 
    project_id belirtilmezse aktif projeyi kullanır.
    """
    print(f"[Tool Log] 'get_project_details' çağrıldı: project_id={project_id}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı. Lütfen bir proje seçin."}, ensure_ascii=False)
    
    project = _db_instance.get_project(project_id)
    if not project:
        return json.dumps({"error": f"Proje bulunamadı: {project_id}"}, ensure_ascii=False)
    
    return json.dumps(project, ensure_ascii=False)


@tool
def analyze_project_text(project_text: str, project_name: str = "New Project"):
    """
    Proje dokümanından çıkarılan metni analiz eder ve yapılandırılmış proje verisi oluşturur.
    Analiz sonucu veritabanına kaydedilir.
    
    Args:
        project_text: Analiz edilecek proje dokümanı metni
        project_name: Proje için bir isim (opsiyonel)
    """
    print(f"[Tool Log] 'analyze_project_text' çağrıldı: project_name={project_name}")
    
    try:
        # Groq client oluştur
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        # Proje analizi yap
        messages = [
            {"role": "system", "content": PROJECT_ANALYSIS_PROMPT},
            {"role": "user", "content": f"""Aşağıda bir dökümandan çıkarılmış metin bulunmaktadır. 
Lütfen bu metni sistem talimatlarında belirtilen JSON formatında analiz et:

--- METİN BAŞLANGICI ---
{project_text}
--- METİN SONU ---
"""}
        ]
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=0.0,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        analyzed_data = json.loads(completion.choices[0].message.content)
        analyzed_data["project_name"] = project_name
        
        # Proje ID'si oluştur
        project_id = f"project_{uuid.uuid4().hex[:8]}"
        
        # Proje verisini kaydet
        _db_instance.save_project(project_id, analyzed_data)
        _db_instance.set_active_project(_session_id, project_id)
        
        return json.dumps({
            "status": "success",
            "project_id": project_id,
            "message": f"Proje başarıyla analiz edildi ve kaydedildi: {project_id}",
            "analysis": analyzed_data
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Analiz hatası: {str(e)}"}, ensure_ascii=False)


@tool
def generate_tasks_from_project(project_id: Optional[str] = None):
    """
    Bir projeden otomatik olarak görev listesi oluşturur.
    """
    print(f"[Tool Log] 'generate_tasks_from_project' çağrıldı: project_id={project_id}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    project = _db_instance.get_project(project_id)
    if not project:
        return json.dumps({"error": f"Proje bulunamadı: {project_id}"}, ensure_ascii=False)
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        description = json.dumps(project.get("detailedDescription", ""), ensure_ascii=False, indent=2)
        acceptance_criteria = json.dumps(project.get("acceptanceCriteria", []), ensure_ascii=False, indent=2)
        department = json.dumps(project.get("department", ""), ensure_ascii=False, indent=2)
        
        user_prompt = f"""
Lütfen aşağıdaki proje bilgileri için bir görev listesi oluştur.
DİKKAT: Her görevin "department" alanı SADECE aşağıda verilen 'department' değerine eşit olmalı.

Proje Açıklaması:
{description}

Kabul Kriterleri:
{acceptance_criteria}

Departman:
{department}

Talimat: Tüm dokümandan mantıklı, yapılabilir, gereksiz tekrar içermeyen bir görev listesi çıkar.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_GENERATION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        task_list_data = json.loads(completion.choices[0].message.content)
        
        # Bazen anahtar altına gömülü gelebilir
        if isinstance(task_list_data, dict) and len(task_list_data) == 1:
            task_list = list(task_list_data.values())[0]
        else:
            task_list = task_list_data
        
        # Görevleri kaydet
        _db_instance.save_tasks(project_id, task_list)
        
        return json.dumps({
            "status": "success",
            "project_id": project_id,
            "total_tasks": len(task_list),
            "tasks": task_list
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Görev oluşturma hatası: {str(e)}"}, ensure_ascii=False)


@tool
def assign_task_to_employee(task_title: str, project_id: Optional[str] = None):
    """
    Belirli bir görevi en uygun çalışana atar.
    
    Args:
        task_title: Atanacak görevin başlığı
        project_id: Proje ID'si (opsiyonel)
    """
    print(f"[Tool Log] 'assign_task_to_employee' çağrıldı: task_title={task_title}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    tasks = _db_instance.get_tasks(project_id)
    if not tasks:
        return json.dumps({"error": "Bu proje için görev bulunamadı."}, ensure_ascii=False)
    
    # Görevi bul
    task = None
    for t in tasks:
        if t.get("task_title") == task_title:
            task = t
            break
    
    if not task:
        return json.dumps({"error": f"Görev bulunamadı: {task_title}"}, ensure_ascii=False)
    
    # Çalışanları al
    company_data = _db_instance.get_company_structure()
    if not company_data:
        return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
    
    # Tüm çalışanları düz listeye çevir
    all_employees = []
    for department in company_data.get("companyStructure", {}).get("departments", []):
        dept_name = department["name"]
        for team in department.get("teams", []):
            team_name = team["name"]
            for employee in team.get("employees", []):
                all_employees.append({
                    **employee,
                    "department": dept_name,
                    "team": team_name
                })
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        user_prompt = f"""
GÖREV BİLGİLERİ:
- Başlık: {task['task_title']}
- Detay: {task['task_detail']}
- Gerekli Teknolojiler: {task['task_stack']}
- Departman: {task['department']}

MEVCUT ÇALIŞANLAR:
{json.dumps(all_employees, indent=2, ensure_ascii=False)}

Lütfen bu görevi EN UYGUN çalışana ata. Sadece JSON formatında yanıt ver.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_ASSIGNMENT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        assignment_result = json.loads(completion.choices[0].message.content)
        
        # Görevi güncelle
        task["task_attended_to"] = assignment_result["assigned_employee_name"]
        task["assigned_employee_id"] = assignment_result["assigned_employee_id"]
        task["assignment_reason"] = assignment_result["assignment_reason"]
        
        _db_instance.save_tasks(project_id, tasks)
        
        return json.dumps({
            "status": "success",
            "task_title": task_title,
            "assigned_to": assignment_result["assigned_employee_name"],
            "reason": assignment_result["assignment_reason"]
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Atama hatası: {str(e)}"}, ensure_ascii=False)


@tool
def list_tasks(project_id: Optional[str] = None):
    """
    Bir projenin tüm görevlerini listeler.
    """
    print(f"[Tool Log] 'list_tasks' çağrıldı: project_id={project_id}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    tasks = _db_instance.get_tasks(project_id)
    
    result = {
        "project_id": project_id,
        "total_tasks": len(tasks),
        "tasks": tasks
    }
    return json.dumps(result, ensure_ascii=False)


# --- EMPLOYEE TOOLS ---

@tool
def list_employees(department: Optional[str] = None):
    """
    Şirketteki tüm çalışanları listeler. 
    department belirtilirse sadece o departmanı gösterir.
    """
    print(f"[Tool Log] 'list_employees' çağrıldı: department={department}")
    
    company_data = _db_instance.get_company_structure()
    if not company_data:
        return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
    
    all_employees = []
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        dept_name = dept["name"]
        
        # Eğer department filtresi varsa ve eşleşmiyorsa atla
        if department and dept_name != department:
            continue
        
        for team in dept.get("teams", []):
            for employee in team.get("employees", []):
                all_employees.append({
                    "id": employee["id"],
                    "name": f"{employee['firstName']} {employee['lastName']}",
                    "role": employee["role"],
                    "department": dept_name,
                    "team": team["name"],
                    "techStack": employee["techStack"],
                    "workload": employee["currentWorkload"]
                })
    
    result = {
        "total_employees": len(all_employees),
        "employees": all_employees
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def get_employee_info(employee_id: str):
    """
    Belirli bir çalışanın detaylı bilgilerini getirir.
    """
    print(f"[Tool Log] 'get_employee_info' çağrıldı: employee_id={employee_id}")
    
    company_data = _db_instance.get_company_structure()
    if not company_data:
        return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
    
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        dept_name = dept["name"]
        for team in dept.get("teams", []):
            team_name = team["name"]
            for employee in team.get("employees", []):
                if employee["id"] == employee_id:
                    result = {
                        **employee,
                        "name": f"{employee['firstName']} {employee['lastName']}",
                        "department": dept_name,
                        "team": team_name
                    }
                    return json.dumps(result, ensure_ascii=False)
    
    return json.dumps({"error": f"Çalışan bulunamadı: {employee_id}"}, ensure_ascii=False)


@tool
def get_department_workload(department: str):
    """
    Belirli bir departmanın toplam iş yükünü ve çalışan dağılımını gösterir.
    """
    print(f"[Tool Log] 'get_department_workload' çağrıldı: department={department}")
    
    company_data = _db_instance.get_company_structure()
    if not company_data:
        return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
    
    workload_stats = {
        "low": 0,
        "medium": 0,
        "high": 0
    }
    employees_list = []
    
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        if dept["name"] != department:
            continue
        
        for team in dept.get("teams", []):
            for employee in team.get("employees", []):
                workload = employee["currentWorkload"]
                workload_stats[workload] += 1
                employees_list.append({
                    "id": employee["id"],
                    "name": f"{employee['firstName']} {employee['lastName']}",
                    "role": employee["role"],
                    "team": team["name"],
                    "workload": workload
                })
    
    result = {
        "department": department,
        "total_employees": len(employees_list),
        "workload_distribution": workload_stats,
        "employees": employees_list
    }
    return json.dumps(result, ensure_ascii=False)


@tool
def switch_active_project(project_id: str):
    """
    Aktif projeyi değiştirir.
    """
    print(f"[Tool Log] 'switch_active_project' çağrıldı: project_id={project_id}")
    
    project = _db_instance.get_project(project_id)
    if not project:
        return json.dumps({"error": f"Proje bulunamadı: {project_id}"}, ensure_ascii=False)
    
    _db_instance.set_active_project(_session_id, project_id)
    return json.dumps({
        "status": "success",
        "message": f"Aktif proje değiştirildi: {project_id}",
        "description": project.get("detailedDescription", "N/A")[:100]
    }, ensure_ascii=False)


# --- LangChain Tool Registry ---

def get_all_tools():
    """
    Tüm LangChain tool nesnelerini döndürür.
    """
    return [
        list_projects,
        get_project_details,
        analyze_project_text,
        generate_tasks_from_project,
        assign_task_to_employee,
        list_tasks,
        list_employees,
        get_employee_info,
        get_department_workload,
        switch_active_project
    ]

def _get_available_tools_dict():
    """
    Her LangChain tool'u bir dict'e ekle.
    """
    tools = get_all_tools()
    return {tool.name: tool for tool in tools}

# Tool name -> tool object mapping
available_tools = _get_available_tools_dict()
