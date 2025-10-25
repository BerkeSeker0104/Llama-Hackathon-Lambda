#!/usr/bin/env python3
"""
Seed data script for demo purposes
Türk isimleri ve gerçekçi verilerle 14 çalışan, 3 proje ve 30+ görev oluşturur
"""

import sys
import os
from datetime import datetime
import uuid

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.firebase_db import FirebaseDatabase

# Türk çalışan verileri
EMPLOYEES = [
    # Backend Department (4 kişi)
    {
        "employee_id": "emp_001",
        "name": "Ahmet Yılmaz",
        "department": "Backend",
        "seniority": "Senior",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"],
        "current_workload": "medium",
        "email": "ahmet.yilmaz@example.com"
    },
    {
        "employee_id": "emp_002",
        "name": "Zeynep Kaya",
        "department": "Backend",
        "seniority": "Mid-Level",
        "tech_stack": ["Node.js", "Express", "MongoDB", "GraphQL"],
        "current_workload": "low",
        "email": "zeynep.kaya@example.com"
    },
    {
        "employee_id": "emp_003",
        "name": "Mehmet Demir",
        "department": "Backend",
        "seniority": "Senior",
        "tech_stack": ["Python", "Django", "PostgreSQL", "Celery", "RabbitMQ"],
        "current_workload": "high",
        "email": "mehmet.demir@example.com"
    },
    {
        "employee_id": "emp_004",
        "name": "Ayşe Şahin",
        "department": "Backend",
        "seniority": "Junior",
        "tech_stack": ["Python", "Flask", "MySQL", "Redis"],
        "current_workload": "low",
        "email": "ayse.sahin@example.com"
    },
    
    # Frontend Department (3 kişi)
    {
        "employee_id": "emp_005",
        "name": "Can Özdemir",
        "department": "Frontend",
        "seniority": "Senior",
        "tech_stack": ["React", "TypeScript", "Next.js", "Tailwind CSS", "Redux"],
        "current_workload": "medium",
        "email": "can.ozdemir@example.com"
    },
    {
        "employee_id": "emp_006",
        "name": "Elif Arslan",
        "department": "Frontend",
        "seniority": "Mid-Level",
        "tech_stack": ["React", "JavaScript", "CSS", "Material-UI"],
        "current_workload": "low",
        "email": "elif.arslan@example.com"
    },
    {
        "employee_id": "emp_007",
        "name": "Burak Çelik",
        "department": "Frontend",
        "seniority": "Junior",
        "tech_stack": ["React", "TypeScript", "Tailwind CSS"],
        "current_workload": "low",
        "email": "burak.celik@example.com"
    },
    
    # Mobile Department (3 kişi)
    {
        "employee_id": "emp_008",
        "name": "Selin Yıldız",
        "department": "Mobile",
        "seniority": "Senior",
        "tech_stack": ["iOS", "Swift", "SwiftUI", "CoreData"],
        "current_workload": "high",
        "email": "selin.yildiz@example.com"
    },
    {
        "employee_id": "emp_009",
        "name": "Emre Aydın",
        "department": "Mobile",
        "seniority": "Mid-Level",
        "tech_stack": ["Android", "Kotlin", "Jetpack Compose", "Room"],
        "current_workload": "medium",
        "email": "emre.aydin@example.com"
    },
    {
        "employee_id": "emp_010",
        "name": "Deniz Koç",
        "department": "Mobile",
        "seniority": "Mid-Level",
        "tech_stack": ["Flutter", "Dart", "Firebase"],
        "current_workload": "low",
        "email": "deniz.koc@example.com"
    },
    
    # DevOps Department (2 kişi)
    {
        "employee_id": "emp_011",
        "name": "Murat Erdoğan",
        "department": "DevOps",
        "seniority": "Senior",
        "tech_stack": ["AWS", "Docker", "Kubernetes", "Terraform", "Jenkins"],
        "current_workload": "high",
        "email": "murat.erdogan@example.com"
    },
    {
        "employee_id": "emp_012",
        "name": "Gizem Aksoy",
        "department": "DevOps",
        "seniority": "Mid-Level",
        "tech_stack": ["Docker", "Kubernetes", "GitLab CI", "Prometheus"],
        "current_workload": "medium",
        "email": "gizem.aksoy@example.com"
    },
    
    # Data Science Department (2 kişi)
    {
        "employee_id": "emp_013",
        "name": "Onur Polat",
        "department": "Data Science",
        "seniority": "Senior",
        "tech_stack": ["Python", "TensorFlow", "PyTorch", "SQL", "Pandas"],
        "current_workload": "medium",
        "email": "onur.polat@example.com"
    },
    {
        "employee_id": "emp_014",
        "name": "Merve Yılmaz",
        "department": "Data Science",
        "seniority": "Mid-Level",
        "tech_stack": ["Python", "Scikit-learn", "SQL", "Tableau"],
        "current_workload": "low",
        "email": "merve.yilmaz@example.com"
    }
]

# Örnek projeler
PROJECTS = [
    {
        "project_id": "proj_ecommerce",
        "project_name": "E-Ticaret Platformu",
        "department": "Backend",
        "detailedDescription": "Yüksek trafikli bir e-ticaret platformu geliştirme projesi. Ürün kataloğu, sepet yönetimi, ödeme entegrasyonu ve sipariş takibi içerir.",
        "tech_stack": ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "AWS"],
        "estimated_duration": "6 ay",
        "critical_analysis": {
            "risks": [
                "Yüksek trafik dönemlerinde performans sorunları",
                "Ödeme entegrasyonu güvenlik riskleri",
                "Stok yönetimi senkronizasyon sorunları"
            ],
            "missing_information": [
                "Günlük beklenen kullanıcı sayısı",
                "Ödeme gateway tercihi",
                "Kargo entegrasyonu detayları"
            ],
            "contradictions": []
        },
        "acceptance_criteria": [
            "Saniyede 1000 istek işleyebilmeli",
            "Ödeme işlemleri PCI-DSS uyumlu olmalı",
            "Stok güncellemeleri gerçek zamanlı olmalı",
            "Mobil responsive tasarım"
        ]
    },
    {
        "project_id": "proj_banking",
        "project_name": "Mobil Bankacılık Uygulaması",
        "department": "Mobile",
        "detailedDescription": "iOS ve Android için güvenli mobil bankacılık uygulaması. Para transferi, fatura ödeme, hesap hareketleri ve yatırım işlemleri içerir.",
        "tech_stack": ["iOS", "Swift", "Android", "Kotlin", "REST API", "Biometric Auth"],
        "estimated_duration": "8 ay",
        "critical_analysis": {
            "risks": [
                "Biyometrik kimlik doğrulama güvenlik açıkları",
                "Offline mod veri senkronizasyonu",
                "Farklı cihazlarda uyumluluk sorunları"
            ],
            "missing_information": [
                "Desteklenecek minimum iOS/Android versiyonları",
                "Offline mod kapsamı",
                "Push notification stratejisi"
            ],
            "contradictions": []
        },
        "acceptance_criteria": [
            "Face ID / Touch ID entegrasyonu",
            "End-to-end şifreleme",
            "Offline mod desteği",
            "KVKK uyumlu veri saklama"
        ]
    },
    {
        "project_id": "proj_analytics",
        "project_name": "İş Zekası Dashboard",
        "department": "Data Science",
        "detailedDescription": "Satış, müşteri davranışı ve operasyonel metrikleri görselleştiren analitik dashboard. Gerçek zamanlı veri işleme ve tahminleme modelleri içerir.",
        "tech_stack": ["Python", "TensorFlow", "PostgreSQL", "React", "D3.js", "Apache Kafka"],
        "estimated_duration": "5 ay",
        "critical_analysis": {
            "risks": [
                "Büyük veri setlerinde performans düşüşü",
                "Model accuracy'sinin düşük olması",
                "Gerçek zamanlı veri pipeline karmaşıklığı"
            ],
            "missing_information": [
                "Veri kaynaklarının detayları",
                "Tahminleme model gereksinimleri",
                "Dashboard kullanıcı sayısı"
            ],
            "contradictions": []
        },
        "acceptance_criteria": [
            "Saniyede 10,000 event işleyebilmeli",
            "Tahminleme modeli %85+ accuracy",
            "Dashboard yükleme süresi < 2 saniye",
            "Özelleştirilebilir widget'lar"
        ]
    }
]

# Örnek görevler (her proje için)
TASKS = {
    "proj_ecommerce": [
        {
            "task_id": "task_ec_001",
            "title": "Ürün Kataloğu API Geliştirme",
            "detail": "RESTful API ile ürün listeleme, filtreleme ve arama endpoint'leri",
            "required_stack": ["Python", "FastAPI", "PostgreSQL"],
            "department": "Backend",
            "status": "assigned",
            "assigned_to": {
                "employee_id": "emp_001",
                "name": "Ahmet Yılmaz",
                "department": "Backend",
                "seniority": "Senior"
            },
            "assignment_reason": "Python ve FastAPI konusunda uzman, PostgreSQL deneyimi var"
        },
        {
            "task_id": "task_ec_002",
            "title": "Sepet Yönetimi Servisi",
            "detail": "Redis tabanlı sepet yönetimi, oturum kontrolü ve stok rezervasyonu",
            "required_stack": ["Python", "Redis", "FastAPI"],
            "department": "Backend",
            "status": "pending"
        },
        {
            "task_id": "task_ec_003",
            "title": "Ödeme Gateway Entegrasyonu",
            "detail": "İyzico/PayTR entegrasyonu, 3D Secure desteği, webhook yönetimi",
            "required_stack": ["Python", "FastAPI"],
            "department": "Backend",
            "status": "pending"
        },
        {
            "task_id": "task_ec_004",
            "title": "Sipariş Takip Sistemi",
            "detail": "Sipariş durumu yönetimi, kargo entegrasyonu, bildirim servisi",
            "required_stack": ["Python", "PostgreSQL", "Celery"],
            "department": "Backend",
            "status": "pending"
        },
        {
            "task_id": "task_ec_005",
            "title": "Admin Panel Frontend",
            "detail": "Ürün yönetimi, sipariş yönetimi ve raporlama arayüzü",
            "required_stack": ["React", "TypeScript", "Material-UI"],
            "department": "Frontend",
            "status": "assigned",
            "assigned_to": {
                "employee_id": "emp_005",
                "name": "Can Özdemir",
                "department": "Frontend",
                "seniority": "Senior"
            },
            "assignment_reason": "React ve TypeScript uzmanı, admin panel deneyimi var"
        },
        {
            "task_id": "task_ec_006",
            "title": "Müşteri Arayüzü Geliştirme",
            "detail": "Ürün listeleme, detay sayfası, sepet ve ödeme akışı",
            "required_stack": ["React", "Next.js", "Tailwind CSS"],
            "department": "Frontend",
            "status": "pending"
        },
        {
            "task_id": "task_ec_007",
            "title": "Docker & Kubernetes Setup",
            "detail": "Containerization, orchestration ve CI/CD pipeline kurulumu",
            "required_stack": ["Docker", "Kubernetes", "AWS"],
            "department": "DevOps",
            "status": "pending"
        },
        {
            "task_id": "task_ec_008",
            "title": "Performans Optimizasyonu",
            "detail": "Database indexing, caching stratejisi, load balancing",
            "required_stack": ["PostgreSQL", "Redis", "AWS"],
            "department": "DevOps",
            "status": "pending"
        }
    ],
    "proj_banking": [
        {
            "task_id": "task_mb_001",
            "title": "iOS Uygulama Geliştirme",
            "detail": "SwiftUI ile modern iOS uygulaması, Face ID entegrasyonu",
            "required_stack": ["iOS", "Swift", "SwiftUI"],
            "department": "Mobile",
            "status": "assigned",
            "assigned_to": {
                "employee_id": "emp_008",
                "name": "Selin Yıldız",
                "department": "Mobile",
                "seniority": "Senior"
            },
            "assignment_reason": "iOS ve SwiftUI konusunda uzman"
        },
        {
            "task_id": "task_mb_002",
            "title": "Android Uygulama Geliştirme",
            "detail": "Jetpack Compose ile modern Android uygulaması, biometric auth",
            "required_stack": ["Android", "Kotlin", "Jetpack Compose"],
            "department": "Mobile",
            "status": "assigned",
            "assigned_to": {
                "employee_id": "emp_009",
                "name": "Emre Aydın",
                "department": "Mobile",
                "seniority": "Mid-Level"
            },
            "assignment_reason": "Android ve Kotlin deneyimi var"
        },
        {
            "task_id": "task_mb_003",
            "title": "Backend API Geliştirme",
            "detail": "Bankacılık işlemleri için güvenli REST API",
            "required_stack": ["Python", "FastAPI", "PostgreSQL"],
            "department": "Backend",
            "status": "pending"
        },
        {
            "task_id": "task_mb_004",
            "title": "Güvenlik ve Şifreleme",
            "detail": "End-to-end encryption, secure storage, certificate pinning",
            "required_stack": ["iOS", "Android", "Cryptography"],
            "department": "Mobile",
            "status": "pending"
        },
        {
            "task_id": "task_mb_005",
            "title": "Offline Mod Implementasyonu",
            "detail": "Local database, sync stratejisi, conflict resolution",
            "required_stack": ["CoreData", "Room", "SQLite"],
            "department": "Mobile",
            "status": "pending"
        },
        {
            "task_id": "task_mb_006",
            "title": "Push Notification Servisi",
            "detail": "Firebase Cloud Messaging entegrasyonu, notification handling",
            "required_stack": ["Firebase", "iOS", "Android"],
            "department": "Mobile",
            "status": "pending"
        },
        {
            "task_id": "task_mb_007",
            "title": "CI/CD Pipeline Kurulumu",
            "detail": "Fastlane, TestFlight, Play Console otomasyonu",
            "required_stack": ["Fastlane", "GitLab CI", "Docker"],
            "department": "DevOps",
            "status": "pending"
        }
    ],
    "proj_analytics": [
        {
            "task_id": "task_an_001",
            "title": "Veri Pipeline Geliştirme",
            "detail": "Apache Kafka ile gerçek zamanlı veri akışı",
            "required_stack": ["Python", "Apache Kafka", "PostgreSQL"],
            "department": "Data Science",
            "status": "assigned",
            "assigned_to": {
                "employee_id": "emp_013",
                "name": "Onur Polat",
                "department": "Data Science",
                "seniority": "Senior"
            },
            "assignment_reason": "Big data ve stream processing deneyimi var"
        },
        {
            "task_id": "task_an_002",
            "title": "Tahminleme Modeli Geliştirme",
            "detail": "Satış tahmini için ML modeli, TensorFlow ile implementation",
            "required_stack": ["Python", "TensorFlow", "Pandas"],
            "department": "Data Science",
            "status": "pending"
        },
        {
            "task_id": "task_an_003",
            "title": "Dashboard Frontend",
            "detail": "React ve D3.js ile interaktif dashboard",
            "required_stack": ["React", "TypeScript", "D3.js"],
            "department": "Frontend",
            "status": "pending"
        },
        {
            "task_id": "task_an_004",
            "title": "Veri Görselleştirme",
            "detail": "Özelleştirilebilir widget'lar, chart library entegrasyonu",
            "required_stack": ["React", "D3.js", "Recharts"],
            "department": "Frontend",
            "status": "pending"
        },
        {
            "task_id": "task_an_005",
            "title": "API Gateway Geliştirme",
            "detail": "Dashboard için backend API, rate limiting, caching",
            "required_stack": ["Python", "FastAPI", "Redis"],
            "department": "Backend",
            "status": "pending"
        },
        {
            "task_id": "task_an_006",
            "title": "Model Training Pipeline",
            "detail": "Otomatik model eğitimi, versiyonlama, deployment",
            "required_stack": ["Python", "TensorFlow", "MLflow"],
            "department": "Data Science",
            "status": "pending"
        },
        {
            "task_id": "task_an_007",
            "title": "Monitoring ve Alerting",
            "detail": "Prometheus, Grafana ile sistem monitoring",
            "required_stack": ["Prometheus", "Grafana", "Docker"],
            "department": "DevOps",
            "status": "pending"
        }
    ]
}


def seed_employees(db: FirebaseDatabase):
    """Çalışan verilerini Firebase'e yükle"""
    print("\n🔄 Çalışan verileri yükleniyor...")
    
    for employee in EMPLOYEES:
        # Firebase'e kaydet
        db.db.collection("employees").document(employee["employee_id"]).set({
            **employee,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        })
        print(f"  ✅ {employee['name']} ({employee['department']}) eklendi")
    
    # Company structure'ı da kaydet
    departments = {}
    for emp in EMPLOYEES:
        dept = emp["department"]
        if dept not in departments:
            departments[dept] = []
        departments[dept].append({
            "employee_id": emp["employee_id"],
            "name": emp["name"],
            "seniority": emp["seniority"],
            "tech_stack": emp["tech_stack"]
        })
    
    db.save_company_structure({"departments": departments})
    print(f"\n✅ {len(EMPLOYEES)} çalışan başarıyla yüklendi!")


def seed_projects(db: FirebaseDatabase):
    """Proje verilerini Firebase'e yükle"""
    print("\n🔄 Proje verileri yükleniyor...")
    
    for project in PROJECTS:
        db.save_project(project["project_id"], project)
        print(f"  ✅ {project['project_name']} eklendi")
    
    print(f"\n✅ {len(PROJECTS)} proje başarıyla yüklendi!")


def seed_tasks(db: FirebaseDatabase):
    """Görev verilerini Firebase'e yükle"""
    print("\n🔄 Görev verileri yükleniyor...")
    
    total_tasks = 0
    for project_id, tasks in TASKS.items():
        db.save_tasks(project_id, tasks)
        print(f"  ✅ {project_id}: {len(tasks)} görev eklendi")
        total_tasks += len(tasks)
    
    print(f"\n✅ Toplam {total_tasks} görev başarıyla yüklendi!")


def main():
    """Ana seed fonksiyonu"""
    print("\n" + "="*60)
    print("🌱 DEMO DATA SEED SCRIPT")
    print("="*60)
    
    # Firebase bağlantısı
    print("\n🔌 Firebase'e bağlanılıyor...")
    db = FirebaseDatabase()
    print("✅ Firebase bağlantısı başarılı!")
    
    # Komut satırı argümanları
    if len(sys.argv) > 1:
        if "--employees" in sys.argv:
            seed_employees(db)
        if "--projects" in sys.argv:
            seed_projects(db)
        if "--tasks" in sys.argv:
            seed_tasks(db)
    else:
        # Hepsini yükle
        seed_employees(db)
        seed_projects(db)
        seed_tasks(db)
    
    print("\n" + "="*60)
    print("✅ SEED İŞLEMİ TAMAMLANDI!")
    print("="*60)
    print("\n📊 Özet:")
    print(f"  - {len(EMPLOYEES)} çalışan")
    print(f"  - {len(PROJECTS)} proje")
    print(f"  - {sum(len(tasks) for tasks in TASKS.values())} görev")
    print("\n🚀 Artık uygulamayı test edebilirsiniz!")
    print("   http://localhost:3000\n")


if __name__ == "__main__":
    main()

