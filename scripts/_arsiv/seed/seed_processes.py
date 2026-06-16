import sys
import os

# Base directory support
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db
from app.models.core import Tenant, User, Role
from app.models.process import Process, ProcessKpi, ProcessActivity
from datetime import datetime, date

def seed_data():
    app = create_app()
    with app.app_context():
        # Get first tenant
        tenant = Tenant.query.first()
        if not tenant:
            print("No tenant found. Please run core seed first.")
            return

        # Check if already seeded
        if Process.query.filter_by(tenant_id=tenant.id).first():
            print("Processes already seeded for this tenant.")
            return

        # Add Processes
        hr_process = Process(
            tenant_id=tenant.id,
            code="HR-01",
            name="İnsan Kaynakları Yönetimi",
            description="Personel alımı, eğitimi ve bordro süreçlerini kapsar.",
            document_no="DOK-HR-001",
            revision_no="V1",
            progress=45
        )
        
        it_process = Process(
            tenant_id=tenant.id,
            code="IT-01",
            name="Bilgi İşlem ve Altyapı",
            description="Sistem güvenliği, donanım tedariği ve yazılım desteği süreçleri.",
            document_no="DOK-IT-101",
            revision_no="V3",
            progress=80
        )
        
        db.session.add(hr_process)
        db.session.add(it_process)
        db.session.commit()
        
        # Add KPIs
        kpi1 = ProcessKpi(
            process_id=hr_process.id,
            name="Yeni Personel Oryantasyon Süresi",
            code="PG-HR-01",
            target_value="5",
            unit="Gün",
            period="Aylık",
            weight=30
        )
        
        kpi2 = ProcessKpi(
            process_id=it_process.id,
            name="Sistem Ayakta Kalma Oranı",
            code="PG-IT-01",
            target_value="99.9",
            unit="%",
            period="Yıllık",
            weight=70
        )
        
        db.session.add(kpi1)
        db.session.add(kpi2)
        
        # Add Activities
        act1 = ProcessActivity(
            process_id=hr_process.id,
            name="Eğitim Materyallerinin Güncellenmesi",
            description="Yeni dönem oryantasyon videolarının çekilmesi.",
            status="Devam Ediyor",
            progress=50
        )
        
        db.session.add(act1)
        db.session.commit()
        
        print("Processes seeded successfully.")

if __name__ == "__main__":
    seed_data()
