from groq import Groq
import json
import os

# EXACT PROMPTS FROM PROTOTYPE (Cell 5)
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
      "Projenin netleşmesi veya başlaması için metinde bulunmayan, kritik öneme sahip eksik bilgiler (örn: 'Başarı metrikleri tanımlanmamış', 'Hedef kullanıcı kitlesi belirsiz'). Eğer eksik bilgi yoksa boş bir dizi [] döndür."
    ],
    "risks": [
      "Metindeki ifadelere dayanarak öngörülen teknik veya operasyonel riskler (örn: 'Zaman çizelgesi, istenen özellikler için çok sıkışık', 'Belirtilen teknoloji ile entegrasyon zorluğu riski'). Eğer belirgin bir risk yoksa boş bir dizi [] döndür."
    ],
    "contradictions": [
      "Metin içinde birbiriyle çelişen ifadeler veya hedefler (örn: 'Hem 'minimum maliyet' hem de 'en yüksek performanslı altyapı' isteniyor'). Eğer çelişki yoksa boş bir dizi [] döndür."
    ]
  },
  "department": "Bu görevin birincil sorumlusu olması gereken departman veya ekip (örn: 'Backend', 'Frontend', 'Data Science', 'DevOps', 'Mobile'). Metinden bu çıkarımı yap.",
  "techStack": [
    "Metinde açıkça belirtilen veya görevin doğası gereği zorunlu olduğu çıkarımı yapılan teknolojiler, diller veya frameworkler (örn: 'Python', 'React', 'Node.js', 'PostgreSQL', 'AWS Lambda')."
  ],
  "timeline": {
    "startDate": "YYYY-MM-DD formatında projenin tahmini başlangıç tarihi (eğer metinde spesifik bir tarih varsa, yoksa null)",
    "endDate": "YYYY-MM-DD formatında projenin teslim tarihi (eğer metinde spesifik bir tarih varsa, yoksa null)"
  },
  "acceptanceCriteria": [
    "Görevin 'tamamlandı' sayılması için karşılanması gereken spesifik, ölçülebilir ve test edilebilir şartlar (örn: 'Tüm API endpointleri %99.9 uptime sağlamalı', 'Sayfa yüklenme hızı 3 saniyenin altında olmalı', 'Kullanıcı girişi 100ms içinde gerçekleşmeli')."
  ]
}
"""

# TASK GENERATION PROMPT (Cell 9)
TASK_GENERATION_PROMPT = """
Sen, deneyimli bir proje yöneticisi ve görev çıkarıcı AI asistanısın.
Amacın, verilen proje dokümanını (açıklama, teslimatlar, kabul kriterleri) inceleyip, bu projede yapılması gereken önemli görevleri belirlemektir.
Çıktı SADECE ve SADECE aşağıdaki JSON formatında, bir görev dizisi (array) olmalı. Başka hiçbir açıklama ekleme.

[
  {
    "task_title": "Görevin kısa başlığı - örn: Backend API tasarımı",
    "task_detail": "Bu görevde yapılması gereken önemli işin kısa açıklaması.",
    "task_stack": "Bu görevde kullanılacak teknolojiler, diller veya frameworkler (örn: 'Python', 'React', 'Node.js', 'PostgreSQL', 'AWS Lambda').",
    "source": "Bu görevin hangi teslimat/maddeden çıkarıldığı (örn: milestone, acceptanceCriteria, vs. - varsa).",
    "task_attended_to": "",
    "department": "Bu görev hangi departmana aitse (karşıdan verilen 'department' bilgisini BURADA TEKRARLA, LLM URETME)."
  }
]

Kurallar:
- Gereksiz görev ekleme, anlamlı ve iş üretilecek düzeyde spesifik görevler çıkar.
- Her görevin 'source' alanında dayandığı maddeyi ya da türünü belirt (örn: 'milestone', 'acceptanceCriteria', ya da 'description').
- Görevlerde teknolojiler ve önemli çıkacak adımları belirt.
- DİKKAT: 'department' alanı sadece gelen proje verisinden (department) alınmalı, kendi başına yeni üretmemelisin, olduğu gibi ata.
"""

class GroqService:
    """
    Groq AI service - EXACT implementation from prototype
    """
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment")
        
        self.client = Groq(api_key=self.api_key)
    
    def analyze_project(self, parsed_text: str) -> dict:
        """
        EXACT implementation from Cell 6
        
        Args:
            parsed_text: Parsed PDF text content
            
        Returns:
            Project analysis JSON
        """
        messages = [
            {"role": "system", "content": PROJECT_ANALYSIS_PROMPT},
            {"role": "user", "content": f"""Aşağıda bir dökümandan çıkarılmış metin bulunmaktadır. 
Lütfen bu metni sistem talimatlarında belirtilen JSON formatında analiz et:

--- METİN BAŞLANGICI ---
{parsed_text}
--- METİN SONU ---
"""}
        ]
        
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=messages,
            temperature=0.0,  # EXACT from prototype
            max_tokens=4096,  # EXACT from prototype
            response_format={"type": "json_object"}
        )
        
        return json.loads(completion.choices[0].message.content)
    
    def generate_tasks(self, project_json: dict) -> list:
        """
        EXACT implementation from Cell 9
        
        Args:
            project_json: Project analysis data
            
        Returns:
            List of generated tasks
        """
        description = json.dumps(project_json.get("detailedDescription", ""), ensure_ascii=False, indent=2)
        acceptance_criteria = json.dumps(project_json.get("acceptanceCriteria", []), ensure_ascii=False, indent=2)
        department = json.dumps(project_json.get("department", ""), ensure_ascii=False, indent=2)
        
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
        
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_GENERATION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,  # EXACT from prototype
            response_format={"type": "json_object"}
        )
        
        task_list_data = json.loads(completion.choices[0].message.content)
        
        # EXACT logic from prototype
        if isinstance(task_list_data, dict) and len(task_list_data) == 1:
            return list(task_list_data.values())[0]
        return task_list_data
