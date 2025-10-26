from groq import Groq
import json
import os

# ENHANCED PROJECT ANALYSIS PROMPT
PROJECT_ANALYSIS_PROMPT = """
You are an expert technical consultant and legal analyst specializing in software development contracts.
Your task is to analyze the contract text VERY CAREFULLY and return ONLY a valid JSON object with the requested information.

IMPORTANT INSTRUCTIONS:
1. Carefully find the PROJECT NAME or TITLE field in the contract and write it in the "project_name" field
2. Identify ALL deficiencies, ambiguities, and risks in the contract - BE EXTREMELY CAREFUL
3. Carefully note the SCOPE ITEMS in the contract - these will be converted into tasks later
4. Identify critical MISSING INFORMATION that is not explicitly stated in the text
5. Comprehensively assess financial, technical, timeline, and legal RISKS

İstenen JSON yapısı:
{
  "project_name": "Sözleşmede geçen projenin tam adı (örn: 'Mobil Bankacılık Uygulaması Geliştirme Projesi'). Eğer açıkça belirtilmemişse, sözleşmenin konu başlığından çıkar.",
  "detailedDescription": "Sözleşmenin tam kapsamını, amaçlarını, hedeflerini ve teslimatları detaylı bir şekilde anlatan 2-3 paragraflık açıklama.",
  "scopeItems": [
    "Sözleşmede belirtilen her bir kapsam maddesi, teslimat veya iş kalemi (örn: 'Kullanıcı kayıt ve giriş sistemi', 'Ödeme entegrasyonu', 'Admin paneli'). AYRINTILI OL, tüm maddeleri listele."
  ],
  "criticalAnalysis": {
    "missingInfo": [
      "CAREFUL ANALYSIS: Critical information that is REQUIRED for the project to start or complete successfully but is NOT SPECIFIED in the contract. Check:",
      "- Are technical requirements specified? (server, database, API limits, etc.)",
      "- Are performance criteria defined? (response time, user count, etc.)",
      "- Are security standards specified? (SSL, encryption, GDPR compliance, etc.)",
      "- Are test processes and acceptance tests defined?",
      "- Is maintenance and support scope specified?",
      "- Is there a change request process?",
      "- Are communication protocols and reporting frequency specified?",
      "- Are data ownership and intellectual property rights clear?",
      "- Are project suspension or cancellation conditions specified?",
      "Write each missing piece of information as a separate item. Find AT LEAST 5-10 deficiencies."
    ],
    "risks": [
      "CAREFUL ANALYSIS: ALL potential risks identified from the contract text. Evaluate:",
      "- TECHNICAL RISKS: Technology selection, integration challenges, scalability",
      "- TIMELINE RISKS: Unrealistic timelines, tight deadlines, dependencies",
      "- FINANCIAL RISKS: Fixed price vs. time-material, payment terms",
      "- SCOPE RISKS: Unclear deliverables, scope creep potential",
      "- COMMUNICATION RISKS: Stakeholder management, decision-making processes",
      "- LEGAL RISKS: Confidentiality, liability limitations, dispute resolution",
      "Write each risk and its potential impact in detail. Specify AT LEAST 5-8 risks."
    ],
    "contradictions": [
      "CONFLICTING items within the contract, inconsistent statements, or logical inconsistencies (e.g., 'Both fast delivery and comprehensive testing', 'Fixed price but flexible scope'). BE EXTREMELY CAREFUL."
    ],
    "legalConcerns": [
      "Legally problematic clauses, ambiguous statements, or one-sided conditions (e.g., 'Unclear liability limits', 'Unilateral right to change by customer')."
    ]
  },
  "department": "Bu projenin birincil sorumlusu olması gereken departman (Backend, Frontend, Mobile, Full-Stack, Data Science, DevOps, UI/UX). Proje kapsamına göre en uygun departmanı seç.",
  "techStack": [
    "Sözleşmede açıkça belirtilen VEYA proje doğası gereği zorunlu olan tüm teknolojiler, diller, frameworkler, araçlar, platformlar (örn: 'React Native', 'Node.js', 'PostgreSQL', 'AWS', 'Docker', 'Git'). Detaylı ol."
  ],
  "timeline": {
    "startDate": "YYYY-MM-DD formatında başlangıç tarihi (sözleşmede belirtilmişse)",
    "endDate": "YYYY-MM-DD formatında bitiş/teslim tarihi (sözleşmede belirtilmişse)",
    "milestones": [
      "Sözleşmede belirtilen ara teslimatlar veya kilometre taşları (örn: '1. Ay: Tasarım onayı', '3. Ay: Beta sürüm')"
    ]
  },
  "acceptanceCriteria": [
    "Projenin 'tamamlandı' ve 'kabul edildi' sayılması için karşılanması gereken SPESİFİK, ÖLÇÜLEBİLİR ve TEST EDİLEBİLİR şartlar (örn: 'Tüm API'ler 200ms altında yanıt vermeli', '1000 eşzamanlı kullanıcıyı desteklemeli', 'Tüm testler %95 başarılı olmalı')."
  ],
  "budget": {
    "amount": "Sözleşmede belirtilen bütçe miktarı (eğer varsa)",
    "currency": "Para birimi (TL, USD, EUR, vb.)",
    "paymentTerms": "Ödeme şartları özeti (örn: 'Aylık fatura', '%50 peşin %50 teslimde')"
  }
}

IMPORTANT REMINDERS:
- Extract project_name from the contract, do not write "New Project"!
- missingInfo array must contain AT LEAST 5-10 items
- risks array must contain AT LEAST 5-8 items
- scopeItems array must contain ALL scope items in the contract
- Perform EXTREMELY CAREFUL and DETAILED analysis!
"""

# ENHANCED TASK GENERATION PROMPT
TASK_GENERATION_PROMPT = """
You are an expert Scrum Master and technical project manager specializing in task planning for software development projects.
Your task is to extract each SCOPE ITEM as a separate TASK using information from the contract analysis.

CRITICAL RULES:
1. Create a SEPARATE TASK for EACH ITEM in the scopeItems array
2. Extract additional tasks from acceptance criteria and descriptions besides scope items
3. Ensure each task is clear, specific, actionable, and measurable
4. Separate tasks by technical detail level (design, development, test, deployment)
5. Consider dependencies and sequencing

Output format (JSON array ONLY):
[
  {
    "task_title": "Short and clear task title (e.g., 'User Registration System Development')",
    "task_detail": "DETAILED description of the work to be done in this task. Should include: What will be done, how it will be done, what features it will have, which systems it will integrate with. Write AT LEAST 2-3 sentences.",
    "task_stack": "Specific technologies, languages, frameworks, libraries to be used in this task (e.g., 'React Native, TypeScript, Redux, AsyncStorage, Firebase Auth')",
    "source": "Indicate where this task came from: 'Scope Item: [item text]' or 'Acceptance Criterion: [criterion]' or 'Requirement: [requirement]'. Include source text!",
    "estimated_hours": "Estimated duration (in hours, be realistic)",
    "priority": "Task priority: 'critical', 'high', 'medium', 'low' (considering dependencies and importance)",
    "task_attended_to": "",
    "department": "ONLY one of these departments: 'Backend', 'Frontend', 'Mobile', 'Full-Stack', 'DevOps', 'UI/UX', 'QA'. Use department from project analysis but adapt based on task nature."
  }
]

TASK CREATION STRATEGY:

1. Tasks from Scope Items (PRIORITY 1):
   - Create a task for EACH item in the scopeItems array
   - If an item is too large, split it into subtasks
   - Example: "User management" → "User registration system", "User profile management", "Password reset"

2. Tasks from Acceptance Criteria:
   - Technical acceptance criteria require tasks (e.g., "API response time under 200ms" → "API Performance Optimization" task)
   - Add testing and validation tasks

3. Infrastructure and Preparation Tasks:
   - Project setup, environment setup
   - Database schema design
   - CI/CD pipeline setup
   - Security configuration

4. Integration Tasks:
   - Third-party API integrations
   - Inter-system data flow
   - Authentication/Authorization

5. Test and QA Tasks:
   - Unit test writing
   - Integration testing
   - UAT (User Acceptance Testing)
   - Performance testing

6. Deployment and Documentation:
   - Production deployment
   - Technical documentation
   - User documentation

TASK QUALITY CRITERIA:
- Each task must be SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
- Task titles should be action-oriented (Develop, Create, Integrate, Test, Deploy)
- Task detail should answer "what", "why", and "how" questions
- Technology stack must be clear
- Source must be specified

AVOID:
- Vague tasks ("General development", "Various improvements")
- Very broad tasks (requiring multiple sprints)
- Duplicate tasks
- Tasks without source specified

EXAMPLE OUTPUT:
[
  {
    "task_title": "User Registration and Login System Backend API Development",
    "task_detail": "RESTful API endpoints to be created: /api/auth/register, /api/auth/login, /api/auth/logout. JWT token-based authentication, password hashing with bcrypt, email verification mechanism, rate limiting (max 5 attempts), session management. PostgreSQL users table design.",
    "task_stack": "Node.js, Express.js, PostgreSQL, JWT, bcrypt, nodemailer, Redis",
    "source": "Scope Item: User registration and login operations will be available",
    "estimated_hours": "24",
    "priority": "critical",
    "task_attended_to": "",
    "department": "Backend"
  }
]

FINAL REMINDER:
- MUST create a task for EACH ITEM in scopeItems!
- Tasks must be specific and actionable!
- Create AT LEAST 8-15 tasks (depending on contract scope)!
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
        ENHANCED task generation - scopeItems'ı da kullanır
        
        Args:
            project_json: Project analysis data (with scopeItems)
            
        Returns:
            List of generated tasks
        """
        project_name = project_json.get("project_name", "Proje")
        description = json.dumps(project_json.get("detailedDescription", ""), ensure_ascii=False, indent=2)
        scope_items = json.dumps(project_json.get("scopeItems", []), ensure_ascii=False, indent=2)
        acceptance_criteria = json.dumps(project_json.get("acceptanceCriteria", []), ensure_ascii=False, indent=2)
        department = project_json.get("department", "Full-Stack")
        tech_stack = json.dumps(project_json.get("techStack", []), ensure_ascii=False, indent=2)
        
        user_prompt = f"""
PROJECT: {project_name}

SCOPE ITEMS (scopeItems):
{scope_items}

PROJECT DESCRIPTION:
{description}

ACCEPTANCE CRITERIA:
{acceptance_criteria}

TECHNOLOGY STACK:
{tech_stack}

MAIN DEPARTMENT: {department}

---

INSTRUCTIONS:
1. Create a SEPARATE TASK for EACH ITEM in the scopeItems array (PRIORITY!)
2. Extract additional tasks from acceptance criteria
3. Add infrastructure tasks (database, setup, deployment, etc.)
4. Don't forget testing and QA tasks
5. Specify which item each task comes from in the source field
6. Tasks must be specific, measurable, and actionable
7. Create AT LEAST 8-15 tasks (depending on scope size)
8. Adapt the department field based on task nature (Backend, Frontend, Mobile, Full-Stack, DevOps, UI/UX, QA)

Now create a detailed task list!
"""
        
        completion = self.client.chat.completions.create(
            model="meta-llama/llama-4-maverick-17b-128e-instruct",
            messages=[
                {"role": "system", "content": TASK_GENERATION_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.15,  # Biraz daha yaratıcı olsun
            max_tokens=8192,  # Daha fazla görev için daha fazla token
            response_format={"type": "json_object"}
        )
        
        task_list_data = json.loads(completion.choices[0].message.content)
        
        # JSON object içindeki array'i bul
        if isinstance(task_list_data, dict):
            # Olası array key'lerini kontrol et
            for key in ['tasks', 'task_list', 'görevler', 'items']:
                if key in task_list_data and isinstance(task_list_data[key], list):
                    return task_list_data[key]
            
            # Tek key varsa onun value'sunu döndür
            if len(task_list_data) == 1:
                value = list(task_list_data.values())[0]
                if isinstance(value, list):
                    return value
        
        # Direkt list döndüyse
        if isinstance(task_list_data, list):
            return task_list_data
        
        # Fallback
        return []
