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

# --- TASK REASSIGNMENT SYSTEM PROMPT ---
TASK_REASSIGNMENT_PROMPT = """
Sen, acil durumlarda görev yeniden ataması yapabilen uzman bir proje yönetim AI asistanısın.
Görevin, bir çalışanın acil durumu olduğunda veya müsait olmadığında, görevlerini en uygun alternatif kişiye atamaktır.

Yeniden atama yaparken şu kriterleri dikkate al (önem sırasına göre):
1. **Müsaitlik (Availability)**: Çalışanın availability_status "available" olmalı
2. **Tech Stack Uyumu**: Görevdeki teknolojilerin çalışanın tech stack'inde olması
3. **Workload (İş Yükü)**: Düşük iş yükü olan çalışanları tercih et (low > medium > high)
4. **Departman Uyumu**: Aynı departman veya yakın departman
5. **Cascade Etkileri**: Bu atama diğer görevleri etkileyecek mi? Risk var mı?

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "assigned_employee_id": "emp_xxx",
  "assigned_employee_name": "Ad Soyad",
  "reassignment_reason": "Neden bu kişi seçildi? (Müsaitlik, tech stack, workload bilgisi)",
  "cascade_risks": [
    "Bu atama sonucu ortaya çıkabilecek riskler (boş liste olabilir)"
  ],
  "confidence_score": 0.85
}

Başka hiçbir açıklama veya metin ekleme.
"""

# --- DELAY PREDICTION SYSTEM PROMPT ---
DELAY_PREDICTION_PROMPT = """
Sen, yazılım projelerinde gecikme tahmini yapan uzman bir analiz AI'sın.
Görevin, mevcut proje durumunu analiz ederek olası gecikmeleri öngörmek ve risk faktörlerini belirlemektir.

Analiz yaparken şu faktörleri değerlendir:
1. **Çalışan Kapasitesi**: Workload dağılımı, müsaitlik durumları
2. **Task Bağımlılıkları**: Blocked task'lar, kritik path'teki gecikmeler
3. **Sprint Durumu**: Mevcut sprint'teki tamamlanma oranı
4. **Atama Durumu**: Atanmamış görevler
5. **Tarih Kontrolü**: Due date'lere yakınlık, zaman sıkışıklığı

Her risk için severity (düşük, orta, yüksek, kritik) ve impact (1-10) belirt.

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "overall_delay_risk": "low" | "medium" | "high" | "critical",
  "estimated_delay_days": 5,
  "risk_factors": [
    {
      "type": "high_workload" | "blocked_tasks" | "dependency_issues" | "unavailable_employees" | "unassigned_tasks",
      "severity": "low" | "medium" | "high" | "critical",
      "description": "Detaylı açıklama",
      "impact_score": 7,
      "affected_tasks": ["task_title_1", "task_title_2"]
    }
  ],
  "recommendations": [
    "Aksiyon önerileri (örn: 'Görev X'i yeniden ata', 'Sprint süresini uzat')"
  ],
  "predicted_completion_date": "2024-02-15"
}

Başka hiçbir açıklama veya metin ekleme.
"""

# --- SPRINT HEALTH ANALYSIS SYSTEM PROMPT ---
SPRINT_HEALTH_ANALYSIS_PROMPT = """
Sen, agile sprint sağlığını değerlendiren uzman bir proje yönetim AI asistanısın.
Görevin, mevcut sprint'in sağlık durumunu analiz etmek ve risk faktörlerini tespit etmektir.

Sprint sağlığını değerlendirirken şu metrikleri kullan:
1. **Tamamlanma Oranı**: Completed / Total tasks
2. **Blocker Sayısı**: Blocked task'ların sayısı ve kritikliği
3. **Çalışan Kapasitesi**: Takımdaki müsaitlik ve workload dengesi
4. **Zaman Uyumu**: Sprint bitiş tarihine kalan süre vs. kalan iş
5. **Bağımlılıklar**: Blocker olan dependency'ler

Health Score: 0-100 arası bir skor hesapla:
- 80-100: Sağlıklı (yeşil)
- 60-79: Dikkat gerektirir (sarı)
- 40-59: Risk altında (turuncu)
- 0-39: Kritik durum (kırmızı)

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "health_score": 75,
  "status": "healthy" | "warning" | "at_risk" | "critical",
  "completion_rate": 0.65,
  "risk_factors": [
    {
      "type": "blocked_tasks" | "low_capacity" | "time_pressure" | "dependency_issues",
      "severity": "low" | "medium" | "high" | "critical",
      "description": "Detaylı açıklama",
      "impact_on_sprint": "Bu risk sprint'i nasıl etkiler"
    }
  ],
  "blockers": [
    {
      "task_title": "Görev adı",
      "reason": "Blocker nedeni",
      "critical": true
    }
  ],
  "recommendations": [
    "Sprint'i sağlıklı hale getirmek için aksiyon önerileri"
  ],
  "predicted_outcome": "Sprint büyük olasılıkla zamanında tamamlanacak" | "2-3 gün gecikme riski var" | "Sprint revizyon gerektirir"
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
    
    try:
        if not _db_instance:
            return json.dumps({"error": "Database connection not available"}, ensure_ascii=False)
        
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
        print(f"[Tool Log] 'list_projects' completed: {len(projects)} projects found")
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        print(f"[Tool Log ERROR] 'list_projects' failed: {e}")
        return json.dumps({"error": f"Failed to list projects: {str(e)}"}, ensure_ascii=False)


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


# --- SPRINT PLANNING TOOLS ---

# --- SPRINT PLANNING SYSTEM PROMPT ---
SPRINT_PLANNING_PROMPT = """
Sen, agile yazılım geliştirme süreçlerinde sprint planlama konusunda uzman bir AI asistanısın.
Görevin, verilen görev listesini (tasks) ve proje bilgilerini inceleyip, bu görevleri mantıklı sprint'lere dağıtmaktır.

Sprint planlama yaparken şu kriterleri dikkate al:
1. **Görev Bağımlılıkları**: Önce temel altyapı, sonra özellikler, son olarak optimizasyonlar
2. **Departman Dağılımı**: Aynı departmanın görevlerini mümkünse birlikte planla
3. **İş Yükü Dengesi**: Her sprint'e yaklaşık eşit sayıda görev dağıt
4. **Öncelik**: Kritik görevler önce, nice-to-have'ler sona

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "total_sprints": 2,
  "sprint_duration_weeks": 2,
  "sprints": [
    {
      "sprint_number": 1,
      "sprint_name": "Sprint 1: Foundation",
      "duration_weeks": 2,
      "tasks": ["task_title_1", "task_title_2"],
      "focus": "Sprint'in odak noktası kısa açıklama"
    },
    {
      "sprint_number": 2,
      "sprint_name": "Sprint 2: Features",
      "duration_weeks": 2,
      "tasks": ["task_title_3", "task_title_4"],
      "focus": "Sprint'in odak noktası kısa açıklama"
    }
  ],
  "backlog": ["gelecek sprintler için task'lar"],
  "notes": "Plan hakkında önemli notlar"
}

Başka hiçbir açıklama veya metin ekleme.
"""

# --- SPRINT REPLAN SYSTEM PROMPT ---
SPRINT_REPLAN_PROMPT = """
Sen, agile yazılım geliştirme süreçlerinde sprint revizyon konusunda uzman bir AI asistanısın.
Görevin, mevcut sprint planını ve değişiklik bilgilerini (tatil günleri, gecikmeler) inceleyip, planı yeniden düzenlemektir.

Revizyon yaparken şu kriterleri dikkate al:
1. **Tatil Günleri**: Tatilde olan çalışanların görevlerini başka sprint'e kaydır
2. **Gecikmeler**: Geciken görevleri önceliklendirip yeniden dağıt
3. **Kapasite**: Takım kapasitesine göre görevleri yeniden dengele
4. **Bağımlılıklar**: Bağımlı görevlerin sırasını koru

Çıktı formatı SADECE ve SADECE şu JSON yapısı olmalı:
{
  "total_sprints": 3,
  "sprint_duration_weeks": 2,
  "sprints": [
    {
      "sprint_number": 1,
      "sprint_name": "Sprint 1: Revised",
      "duration_weeks": 2,
      "tasks": ["task_title_1", "task_title_2"],
      "focus": "Revize edilmiş odak noktası",
      "changes": "Bu sprint'te yapılan değişiklikler"
    }
  ],
  "backlog": ["ertelenen task'lar"],
  "revision_summary": {
    "tasks_moved": 3,
    "sprints_added": 1,
    "reason": "Revizyon nedeni özeti"
  }
}

Başka hiçbir açıklama veya metin ekleme.
"""

@tool
def generate_sprint_plan(project_id: Optional[str] = None, sprint_duration_weeks: int = 2):
    """
    Proje için otomatik sprint planı oluşturur.
    
    Args:
        project_id: Proje ID'si (opsiyonel, aktif proje kullanılır)
        sprint_duration_weeks: Her sprint'in süresi (hafta)
    """
    print(f"[Tool Log] 'generate_sprint_plan' çağrıldı: project_id={project_id}, duration={sprint_duration_weeks}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    project = _db_instance.get_project(project_id)
    if not project:
        return json.dumps({"error": f"Proje bulunamadı: {project_id}"}, ensure_ascii=False)
    
    tasks = _db_instance.get_tasks(project_id)
    if not tasks:
        return json.dumps({"error": "Bu proje için görev bulunamadı. Önce görev oluşturun."}, ensure_ascii=False)
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        # Task listesini sadeleştir (sadece önemli alanlar)
        simplified_tasks = [
            {
                "task_title": t.get("task_title"),
                "task_detail": t.get("task_detail"),
                "task_stack": t.get("task_stack"),
                "department": t.get("department"),
                "task_attended_to": t.get("task_attended_to", "")
            }
            for t in tasks
        ]
        
        user_prompt = f"""
Lütfen aşağıdaki proje için sprint planı oluştur.

PROJE BİLGİLERİ:
- Proje Adı: {project.get('project_name', 'N/A')}
- Departman: {project.get('department', 'N/A')}
- Açıklama: {project.get('detailedDescription', 'N/A')[:300]}

GÖREVLER:
{json.dumps(simplified_tasks, indent=2, ensure_ascii=False)}

SPRINT AYARLARI:
- Sprint Süresi: {sprint_duration_weeks} hafta
- Toplam Görev Sayısı: {len(tasks)}

Talimat: Bu görevleri mantıklı sprint'lere dağıt. Her sprint'te 2-4 görev olsun. Bağımlılıkları dikkate al.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": SPRINT_PLANNING_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        sprint_plan = json.loads(completion.choices[0].message.content)
        
        # Sprint planını kaydet
        import datetime
        sprint_id = f"sprint_{uuid.uuid4().hex[:8]}"
        
        # Başlangıç tarihini bugün olarak ayarla
        start_date = datetime.date.today()
        
        # Bitiş tarihini toplam sprint süresine göre hesapla
        total_weeks = sprint_plan.get("total_sprints", 2) * sprint_plan.get("sprint_duration_weeks", 2)
        end_date = start_date + datetime.timedelta(weeks=total_weeks)
        
        sprint_data = {
            "sprint_id": sprint_id,
            "project_id": project_id,
            "plan": sprint_plan,
            "status": "planned",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "current_sprint_number": 1,
            "created_at": json.dumps({"timestamp": "now"})  # Firebase timestamp
        }
        
        _db_instance.save_sprint(project_id, sprint_data)
        
        return json.dumps({
            "status": "success",
            "sprint_id": sprint_id,
            "message": f"Sprint planı başarıyla oluşturuldu: {sprint_plan['total_sprints']} sprint",
            "plan": sprint_plan
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Sprint planlama hatası: {str(e)}"}, ensure_ascii=False)


@tool
def replan_sprints(project_id: Optional[str] = None, vacation_days: int = 0, delays: int = 0):
    """
    Mevcut sprint planını revize eder (tatil günleri, gecikmeler vs. için).
    
    Args:
        project_id: Proje ID'si (opsiyonel, aktif proje kullanılır)
        vacation_days: Tatil/izin gün sayısı
        delays: Gecikme miktarı (gün)
    """
    print(f"[Tool Log] 'replan_sprints' çağrıldı: project_id={project_id}, vacation={vacation_days}, delays={delays}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    # Mevcut sprint planını al
    sprints = _db_instance.get_sprints(project_id)
    if not sprints:
        return json.dumps({"error": "Bu proje için sprint planı bulunamadı. Önce sprint planı oluşturun."}, ensure_ascii=False)
    
    current_sprint = sprints[0]  # En son oluşturulan sprint
    current_plan = current_sprint.get("plan", {})
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        user_prompt = f"""
Lütfen aşağıdaki sprint planını revize et.

MEVCUT SPRINT PLANI:
{json.dumps(current_plan, indent=2, ensure_ascii=False)}

DEĞİŞİKLİKLER:
- Tatil/İzin Günleri: {vacation_days} gün
- Gecikme: {delays} gün

Talimat: Bu değişikliklere göre sprint planını yeniden düzenle. Gerekirse yeni sprint ekle veya görevleri kaydır.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": SPRINT_REPLAN_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        new_plan = json.loads(completion.choices[0].message.content)
        
        # Yeni planı kaydet
        import datetime
        sprint_id = f"sprint_{uuid.uuid4().hex[:8]}"
        
        # Başlangıç tarihini bugün olarak ayarla
        start_date = datetime.date.today()
        
        # Bitiş tarihini toplam sprint süresine göre hesapla (tatil ve gecikmeler dahil)
        total_weeks = new_plan.get("total_sprints", 2) * new_plan.get("sprint_duration_weeks", 2)
        additional_days = vacation_days + delays
        end_date = start_date + datetime.timedelta(weeks=total_weeks, days=additional_days)
        
        sprint_data = {
            "sprint_id": sprint_id,
            "project_id": project_id,
            "plan": new_plan,
            "status": "replanned",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "current_sprint_number": 1,
            "previous_sprint_id": current_sprint.get("sprint_id"),
            "revision_reason": f"Tatil: {vacation_days} gün, Gecikme: {delays} gün",
            "vacation_days": vacation_days,
            "delays": delays,
            "created_at": json.dumps({"timestamp": "now"})
        }
        
        _db_instance.save_sprint(project_id, sprint_data)
        
        return json.dumps({
            "status": "success",
            "sprint_id": sprint_id,
            "message": "Sprint planı başarıyla revize edildi",
            "new_plan": new_plan,
            "changes": {
                "vacation_days": vacation_days,
                "delays": delays,
                "tasks_moved": new_plan.get("revision_summary", {}).get("tasks_moved", 0),
                "sprints_added": new_plan.get("revision_summary", {}).get("sprints_added", 0)
            }
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Sprint revizyon hatası: {str(e)}"}, ensure_ascii=False)


# --- NEW DYNAMIC SPRINT MANAGEMENT TOOLS ---

@tool
def reassign_task_to_employee(task_title: str, from_employee_id: str, reason: str, project_id: Optional[str] = None):
    """
    Acil durumda görevi yeni bir çalışana atar.
    
    Args:
        task_title: Görev başlığı
        from_employee_id: Mevcut çalışan ID'si (görevi bırakan kişi)
        reason: Yeniden atama nedeni (örn: "acil izin", "iş yükü fazla")
        project_id: Proje ID'si (opsiyonel)
    """
    print(f"[Tool Log] 'reassign_task_to_employee' çağrıldı: task={task_title}, from={from_employee_id}, reason={reason}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    # Görevi bul
    tasks = _db_instance.get_tasks(project_id)
    task = None
    for t in tasks:
        if t.get("task_title") == task_title or t.get("title") == task_title:
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
                # Mevcut çalışanı hariç tut
                if employee.get("id") != from_employee_id:
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
- Başlık: {task.get('task_title', task.get('title'))}
- Detay: {task.get('task_detail', task.get('detail'))}
- Gerekli Teknolojiler: {task.get('task_stack', task.get('required_stack'))}
- Departman: {task.get('department')}

YENİDEN ATAMA NEDENİ:
{reason}

MEVCUT ÇALIŞANLAR (MÜSAİT OLANLAR):
{json.dumps(all_employees, indent=2, ensure_ascii=False)}

Lütfen bu görevi EN UYGUN çalışana ata. Müsaitlik durumunu, tech stack uyumunu ve iş yükünü dikkate al.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_REASSIGNMENT_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        # Görevi yeniden ata
        task_id = task.get("task_id")
        _db_instance.reassign_task(
            task_id=task_id,
            project_id=project_id,
            new_employee_id=result["assigned_employee_id"],
            new_employee_name=result["assigned_employee_name"],
            reassignment_reason=result["reassignment_reason"]
        )
        
        return json.dumps({
            "status": "success",
            "task_title": task_title,
            "previous_assignee_id": from_employee_id,
            "new_assignee": result["assigned_employee_name"],
            "new_assignee_id": result["assigned_employee_id"],
            "reason": result["reassignment_reason"],
            "cascade_risks": result.get("cascade_risks", []),
            "confidence_score": result.get("confidence_score", 0.0)
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Görev yeniden atama hatası: {str(e)}"}, ensure_ascii=False)


@tool
def update_employee_availability(employee_id: str, status: str, unavailable_until: Optional[str] = None, reason: Optional[str] = None):
    """
    Çalışan müsaitlik durumunu günceller.
    
    Args:
        employee_id: Çalışan ID'si
        status: Müsaitlik durumu (available, unavailable, limited)
        unavailable_until: Müsait olmayacağı tarihe kadar (ISO format: YYYY-MM-DD)
        reason: Müsait olmama nedeni
    """
    print(f"[Tool Log] 'update_employee_availability' çağrıldı: employee={employee_id}, status={status}")
    
    try:
        # Çalışan bilgilerini al
        company_data = _db_instance.get_company_structure()
        if not company_data:
            return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
        
        # Çalışanı bul
        employee_name = None
        for dept in company_data.get("companyStructure", {}).get("departments", []):
            for team in dept.get("teams", []):
                for emp in team.get("employees", []):
                    if emp.get("id") == employee_id:
                        employee_name = f"{emp.get('firstName')} {emp.get('lastName')}"
                        break
                if employee_name:
                    break
            if employee_name:
                break
        
        if not employee_name:
            return json.dumps({"error": f"Çalışan bulunamadı: {employee_id}"}, ensure_ascii=False)
        
        # Müsaitlik durumunu güncelle
        _db_instance.update_employee_availability(
            employee_id=employee_id,
            status=status,
            until_date=unavailable_until,
            reason=reason
        )
        
        # Çalışanın mevcut görevlerini al
        employee_tasks = _db_instance.get_employee_tasks(employee_id)
        
        response = {
            "status": "success",
            "employee_id": employee_id,
            "employee_name": employee_name,
            "availability_status": status,
            "unavailable_until": unavailable_until,
            "reason": reason,
            "current_tasks": [
                {
                    "task_id": t.get("task_id"),
                    "title": t.get("task_title", t.get("title")),
                    "project_id": t.get("project_id"),
                    "status": t.get("status", "pending")
                }
                for t in employee_tasks
            ],
            "total_active_tasks": len(employee_tasks),
            "message": f"{employee_name} müsaitlik durumu güncellendi: {status}"
        }
        
        if len(employee_tasks) > 0 and status == "unavailable":
            response["warning"] = f"Bu çalışanın {len(employee_tasks)} aktif görevi var. Görevleri yeniden atamayı düşünün."
        
        return json.dumps(response, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Müsaitlik güncelleme hatası: {str(e)}"}, ensure_ascii=False)


@tool
def predict_project_delays(project_id: Optional[str] = None):
    """
    Proje için gecikme riski analizi yapar.
    
    Args:
        project_id: Proje ID'si (opsiyonel, aktif proje kullanılır)
    """
    print(f"[Tool Log] 'predict_project_delays' çağrıldı: project_id={project_id}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    # Proje ve görevleri al
    project = _db_instance.get_project(project_id)
    tasks = _db_instance.get_tasks(project_id)
    
    if not tasks:
        return json.dumps({"error": "Bu proje için görev bulunamadı."}, ensure_ascii=False)
    
    # Çalışan bilgilerini al
    company_data = _db_instance.get_company_structure()
    
    # Çalışanları düz listeye çevir
    all_employees = []
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        for team in dept.get("teams", []):
            for emp in team.get("employees", []):
                all_employees.append({
                    "id": emp.get("id"),
                    "name": f"{emp.get('firstName')} {emp.get('lastName')}",
                    "workload": emp.get("currentWorkload"),
                    "availability": emp.get("availability_status", "available")
                })
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        # Task bilgilerini sadeleştir
        task_summary = [
            {
                "title": t.get("task_title", t.get("title")),
                "status": t.get("status", "pending"),
                "assigned_to": t.get("task_attended_to", "Atanmamış"),
                "assigned_id": t.get("assigned_employee_id"),
                "department": t.get("department"),
                "blocked_reason": t.get("blocked_reason"),
                "due_date": t.get("due_date"),
                "priority": t.get("priority", "medium")
            }
            for t in tasks
        ]
        
        user_prompt = f"""
PROJE BİLGİLERİ:
- Proje Adı: {project.get('project_name', 'N/A')}
- Departman: {project.get('department', 'N/A')}
- Toplam Görev: {len(tasks)}

GÖREV DURUMU:
{json.dumps(task_summary, indent=2, ensure_ascii=False)}

ÇALIŞAN DURUMU:
{json.dumps(all_employees, indent=2, ensure_ascii=False)}

Lütfen bu proje için gecikme riski analizi yap. Tüm faktörleri (workload, müsaitlik, blocked tasks, atanmamış görevler) değerlendir.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": DELAY_PREDICTION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        return json.dumps({
            "status": "success",
            "project_id": project_id,
            "project_name": project.get("project_name"),
            "analysis": result
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Gecikme tahmini hatası: {str(e)}"}, ensure_ascii=False)


@tool
def analyze_sprint_health(project_id: Optional[str] = None, sprint_id: Optional[str] = None):
    """
    Sprint sağlık durumunu analiz eder.
    
    Args:
        project_id: Proje ID'si (opsiyonel)
        sprint_id: Sprint ID'si (opsiyonel, belirtilmezse en son sprint)
    """
    print(f"[Tool Log] 'analyze_sprint_health' çağrıldı: project_id={project_id}, sprint_id={sprint_id}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    # Sprint'i al
    if sprint_id:
        sprint = _db_instance.get_sprint(sprint_id)
    else:
        sprints = _db_instance.get_sprints(project_id)
        if not sprints:
            return json.dumps({"error": "Bu proje için sprint planı bulunamadı."}, ensure_ascii=False)
        sprint = sprints[0]  # En son sprint
        sprint_id = sprint.get("sprint_id")
    
    if not sprint:
        return json.dumps({"error": "Sprint bulunamadı."}, ensure_ascii=False)
    
    # Görevleri al
    tasks = _db_instance.get_tasks(project_id)
    sprint_plan = sprint.get("plan", {})
    
    # Sprint'teki görevleri filtrele
    sprint_task_titles = []
    for s in sprint_plan.get("sprints", []):
        sprint_task_titles.extend(s.get("tasks", []))
    
    sprint_tasks = [t for t in tasks if t.get("task_title", t.get("title")) in sprint_task_titles]
    
    # Çalışan bilgilerini al
    company_data = _db_instance.get_company_structure()
    all_employees = []
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        for team in dept.get("teams", []):
            for emp in team.get("employees", []):
                all_employees.append({
                    "id": emp.get("id"),
                    "name": f"{emp.get('firstName')} {emp.get('lastName')}",
                    "workload": emp.get("currentWorkload"),
                    "availability": emp.get("availability_status", "available")
                })
    
    try:
        groq_api_key = os.getenv("GROQ_API_KEY")
        client = Groq(api_key=groq_api_key)
        
        # Task durumlarını özetle
        task_summary = [
            {
                "title": t.get("task_title", t.get("title")),
                "status": t.get("status", "pending"),
                "assigned_to": t.get("task_attended_to", "Atanmamış"),
                "blocked_reason": t.get("blocked_reason"),
                "priority": t.get("priority", "medium")
            }
            for t in sprint_tasks
        ]
        
        user_prompt = f"""
SPRINT BİLGİLERİ:
- Sprint ID: {sprint_id}
- Sprint Planı: {json.dumps(sprint_plan, indent=2, ensure_ascii=False)}
- Toplam Sprint Görevi: {len(sprint_tasks)}

SPRINT GÖREVLERİ:
{json.dumps(task_summary, indent=2, ensure_ascii=False)}

ÇALIŞAN DURUMU:
{json.dumps(all_employees, indent=2, ensure_ascii=False)}

Lütfen bu sprint'in sağlık durumunu analiz et. Health score hesapla ve risk faktörlerini belirle.
"""
        
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": SPRINT_HEALTH_ANALYSIS_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2,
            max_tokens=4096,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(completion.choices[0].message.content)
        
        # Sprint sağlık skorunu veritabanına kaydet
        health_score = result.get("health_score", 0)
        risk_factors = result.get("risk_factors", [])
        _db_instance.update_sprint_health(sprint_id, health_score, risk_factors)
        
        return json.dumps({
            "status": "success",
            "sprint_id": sprint_id,
            "project_id": project_id,
            "analysis": result
        }, ensure_ascii=False)
        
    except Exception as e:
        return json.dumps({"error": f"Sprint sağlık analizi hatası: {str(e)}"}, ensure_ascii=False)


@tool
def get_available_employees_for_task(task_title: str, project_id: Optional[str] = None):
    """
    Belirli bir görev için müsait çalışanları listeler ve atama skorlarıyla sıralar.
    
    Args:
        task_title: Görev başlığı
        project_id: Proje ID'si (opsiyonel)
    """
    print(f"[Tool Log] 'get_available_employees_for_task' çağrıldı: task={task_title}")
    
    if not project_id:
        project_id = _db_instance.get_active_project(_session_id)
    
    if not project_id:
        return json.dumps({"error": "Aktif proje bulunamadı."}, ensure_ascii=False)
    
    # Görevi bul
    tasks = _db_instance.get_tasks(project_id)
    task = None
    for t in tasks:
        if t.get("task_title") == task_title or t.get("title") == task_title:
            task = t
            break
    
    if not task:
        return json.dumps({"error": f"Görev bulunamadı: {task_title}"}, ensure_ascii=False)
    
    # Çalışanları al
    company_data = _db_instance.get_company_structure()
    if not company_data:
        return json.dumps({"error": "Şirket yapısı bulunamadı."}, ensure_ascii=False)
    
    # Müsait çalışanları filtrele
    available_employees = []
    for dept in company_data.get("companyStructure", {}).get("departments", []):
        dept_name = dept["name"]
        for team in dept.get("teams", []):
            for emp in team.get("employees", []):
                availability = emp.get("availability_status", "available")
                if availability == "available":
                    available_employees.append({
                        "id": emp.get("id"),
                        "name": f"{emp.get('firstName')} {emp.get('lastName')}",
                        "department": dept_name,
                        "team": team["name"],
                        "role": emp.get("role"),
                        "techStack": emp.get("techStack", []),
                        "workload": emp.get("currentWorkload", "medium")
                    })
    
    if not available_employees:
        return json.dumps({
            "status": "warning",
            "message": "Hiç müsait çalışan bulunamadı.",
            "available_employees": []
        }, ensure_ascii=False)
    
    # Her çalışan için basit bir skor hesapla
    task_stack = task.get("task_stack", task.get("required_stack", ""))
    task_dept = task.get("department", "")
    
    scored_employees = []
    for emp in available_employees:
        score = 0
        reasons = []
        
        # Tech stack uyumu (en önemli - 50 puan)
        if isinstance(task_stack, str):
            task_techs = [t.strip() for t in task_stack.split(",")]
        else:
            task_techs = task_stack if isinstance(task_stack, list) else []
        
        emp_techs = emp.get("techStack", [])
        matching_techs = [t for t in task_techs if t in emp_techs]
        if matching_techs:
            tech_score = (len(matching_techs) / len(task_techs)) * 50 if task_techs else 0
            score += tech_score
            reasons.append(f"Tech stack uyumu: {len(matching_techs)}/{len(task_techs)}")
        
        # Workload (30 puan)
        workload = emp.get("workload", "medium")
        if workload == "low":
            score += 30
            reasons.append("Düşük iş yükü")
        elif workload == "medium":
            score += 15
            reasons.append("Orta iş yükü")
        
        # Departman uyumu (20 puan)
        if emp.get("department") == task_dept:
            score += 20
            reasons.append("Aynı departman")
        
        scored_employees.append({
            **emp,
            "assignment_score": round(score, 2),
            "reasons": reasons
        })
    
    # Skora göre sırala
    scored_employees.sort(key=lambda x: x["assignment_score"], reverse=True)
    
    return json.dumps({
        "status": "success",
        "task_title": task_title,
        "task_stack": task_stack,
        "task_department": task_dept,
        "total_available": len(scored_employees),
        "available_employees": scored_employees
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
        switch_active_project,
        generate_sprint_plan,
        replan_sprints,
        # New dynamic sprint management tools
        reassign_task_to_employee,
        update_employee_availability,
        predict_project_delays,
        analyze_sprint_health,
        get_available_employees_for_task
    ]

def _get_available_tools_dict():
    """
    Her LangChain tool'u bir dict'e ekle.
    """
    tools = get_all_tools()
    return {tool.name: tool for tool in tools}

# Tool name -> tool object mapping
available_tools = _get_available_tools_dict()
