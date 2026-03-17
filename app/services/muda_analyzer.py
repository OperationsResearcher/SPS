# -*- coding: utf-8 -*-
"""
Muda Analyzer Service - Süreç Verimsizlik Analizi
7 Muda tipi ile süreç verimsizlik analizi.
Eski proje muda_analyzer adaptasyonu (tenant_id, Process, ProcessKpi, KpiData).
"""
from datetime import datetime, timezone, timedelta

from app.models import db
from app.models.process import Process, ProcessKpi, KpiData


def _safe_float(val):
    """String veya sayıyı float'a çevirir; hata durumunda None."""
    if val is None:
        return None
    if isinstance(val, (int, float)):
        return float(val)
    s = str(val).strip().replace(',', '.')
    if not s:
        return None
    try:
        return float(s)
    except (ValueError, TypeError):
        return None


class MudaAnalyzerService:
    """Muda (İsraf) Analiz Servisi - Süreç verimsizliğini tespit eder"""

    MUDA_TYPES = {
        'overproduction': 'Aşırı Üretim',
        'waiting': 'Bekleme',
        'transport': 'Taşıma/Nakliye',
        'overprocessing': 'Aşırı İşleme',
        'inventory': 'Stok/Envanter',
        'motion': 'Hareket',
        'defects': 'Hata/Kusur'
    }

    @staticmethod
    def analyze_process_inefficiency(process_id: int, tenant_id: int) -> list:
        """Bir sürecin verimsizlik analizini yapar."""
        findings = []
        try:
            process = Process.query.filter_by(
                id=process_id,
                tenant_id=tenant_id,
                is_active=True
            ).first()
            if not process:
                return findings

            findings.extend(MudaAnalyzerService._analyze_waiting(process))
            findings.extend(MudaAnalyzerService._analyze_defects(process))
            findings.extend(MudaAnalyzerService._analyze_overprocessing(process))
            findings.extend(MudaAnalyzerService._analyze_overproduction(process))
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[muda_analyzer] analyze_process_inefficiency hatası: {e}", exc_info=True)
        return findings

    @staticmethod
    def _analyze_waiting(process: Process) -> list:
        """Bekleme (Waiting) - Hedefin altında kalan performans göstergeleri."""
        findings = []
        try:
            three_months_ago = datetime.now(timezone.utc).date() - timedelta(days=90)
            kpis = ProcessKpi.query.filter_by(process_id=process.id, is_active=True).all()
            for kpi in kpis:
                recent = (
                    KpiData.query.filter(
                        KpiData.process_kpi_id == kpi.id,
                        KpiData.data_date >= three_months_ago,
                        KpiData.is_active == True
                    )
                    .order_by(KpiData.data_date.desc())
                    .limit(3)
                    .all()
                )
                if len(recent) >= 2:
                    below_count = 0
                    total_gap_pct = 0.0
                    for d in recent:
                        target = _safe_float(d.target_value) or _safe_float(kpi.target_value)
                        actual = _safe_float(d.actual_value)
                        if target is not None and actual is not None and target > 0 and actual < target:
                            below_count += 1
                            total_gap_pct += ((target - actual) / target) * 100
                    if below_count >= 2:
                        avg_below = total_gap_pct / below_count if below_count > 0 else 0
                        findings.append({
                            'type': 'waiting',
                            'title': f'{kpi.name} - Hedef Altında Performans',
                            'description': f'{kpi.name} performans göstergesi son dönemde hedefin %{avg_below:.1f} altında gerçekleşiyor. Bu bekleme ve gecikme kaynaklı verimsizlik göstergesidir.',
                            'severity': 'high' if avg_below > 20 else 'medium',
                            'estimated_waste_hours': None,
                            'related_kpi_id': kpi.id
                        })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[muda_analyzer] _analyze_waiting hatası: {e}")
        return findings

    @staticmethod
    def _analyze_defects(process: Process) -> list:
        """Hata/Kusur (Defects) - Tutarsız veya düşük performans / varyasyon."""
        findings = []
        try:
            kpis = ProcessKpi.query.filter_by(process_id=process.id, is_active=True).all()
            for kpi in kpis:
                recent = (
                    KpiData.query.filter(
                        KpiData.process_kpi_id == kpi.id,
                        KpiData.is_active == True
                    )
                    .order_by(KpiData.data_date.desc())
                    .limit(6)
                    .all()
                )
                if len(recent) >= 4:
                    values = []
                    for d in recent:
                        v = _safe_float(d.actual_value)
                        if v is not None:
                            values.append(v)
                    if len(values) >= 4:
                        avg = sum(values) / len(values)
                        variance = sum((v - avg) ** 2 for v in values) / len(values)
                        std_dev = (variance ** 0.5) if variance >= 0 else 0
                        cv = (std_dev / avg * 100) if avg and avg > 0 else 0
                        if cv > 30:
                            findings.append({
                                'type': 'defects',
                                'title': f'{kpi.name} - Yüksek Varyasyon',
                                'description': f'{kpi.name} performans göstergesinde %{cv:.1f} varyasyon tespit edildi. Bu tutarsızlık hata veya kalite sorunlarına işaret edebilir.',
                                'severity': 'medium',
                                'estimated_waste_hours': None,
                                'related_kpi_id': kpi.id
                            })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[muda_analyzer] _analyze_defects hatası: {e}")
        return findings

    @staticmethod
    def _analyze_overprocessing(process: Process) -> list:
        """Aşırı İşleme (Overprocessing) - Gereksiz karmaşıklık."""
        findings = []
        try:
            count = ProcessKpi.query.filter_by(process_id=process.id, is_active=True).count()
            if count > 10:
                findings.append({
                    'type': 'overprocessing',
                    'title': f'{process.name} - Aşırı İşleme',
                    'description': f'Süreçte {count} performans göstergesi bulunuyor. Bu sayı optimumun üzerinde olabilir ve gereksiz karmaşıklık yaratıyor olabilir.',
                    'severity': 'low',
                    'estimated_waste_hours': count * 0.5,
                    'related_kpi_id': None
                })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[muda_analyzer] _analyze_overprocessing hatası: {e}")
        return findings

    @staticmethod
    def _analyze_overproduction(process: Process) -> list:
        """Aşırı Üretim (Overproduction) - Pasif süreç vb."""
        findings = []
        try:
            if process.status and str(process.status).lower() in ('pasif', 'inactive'):
                findings.append({
                    'type': 'overproduction',
                    'title': f'{process.name} - Pasif Süreç',
                    'description': 'Bu süreç pasif durumda. Eğer artık kullanılmıyorsa, süreç çıktıları aşırı üretim sayılabilir.',
                    'severity': 'low',
                    'estimated_waste_hours': None,
                    'related_kpi_id': None
                })
        except Exception as e:
            import logging
            logging.getLogger(__name__).warning(f"[muda_analyzer] _analyze_overproduction hatası: {e}")
        return findings

    @staticmethod
    def get_efficiency_score(tenant_id: int) -> float:
        """Kiracının genel verimlilik skorunu hesaplar (0-100)."""
        try:
            processes = Process.query.filter_by(
                tenant_id=tenant_id,
                is_active=True
            ).all()
            if not processes:
                return 100.0
            total = 0.0
            for p in processes:
                findings = MudaAnalyzerService.analyze_process_inefficiency(p.id, tenant_id)
                if len(findings) == 0:
                    score = 100
                elif len(findings) <= 2:
                    score = 80
                elif len(findings) <= 4:
                    score = 60
                elif len(findings) <= 6:
                    score = 40
                else:
                    score = 20
                total += score
            return round(total / len(processes), 2)
        except Exception as e:
            return 0.0
