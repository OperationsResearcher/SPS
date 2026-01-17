# -*- coding: utf-8 -*-
"""
Muda Hunter Service - Süreç Verimsizliği Analizi
V65.0 - Waste Eliminator
"""
from models import db, Surec, SurecPerformansGostergesi, PerformansGostergeVeri, MudaFinding
from sqlalchemy import func, and_, or_
from datetime import datetime, timedelta


class MudaAnalyzerService:
    """Muda (İsraf) Analiz Servisi - Süreç verimsizliğini tespit eder"""
    
    # 7 Muda Tipi
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
    def analyze_process_inefficiency(surec_id, kurum_id):
        """Bir sürecin verimsizlik analizini yapar"""
        findings = []
        
        try:
            surec = Surec.query.filter_by(id=surec_id, kurum_id=kurum_id).first()
            if not surec:
                return findings
            
            # 1. Bekleme (Waiting) - Performans göstergeleri hedef altında
            waiting_findings = MudaAnalyzerService._analyze_waiting(surec)
            findings.extend(waiting_findings)
            
            # 2. Hata/Kusur (Defects) - Hedefleri tutturamayan PG'ler
            defect_findings = MudaAnalyzerService._analyze_defects(surec)
            findings.extend(defect_findings)
            
            # 3. Aşırı İşleme (Overprocessing) - Gereksiz adımlar veya fazla detay
            overprocessing_findings = MudaAnalyzerService._analyze_overprocessing(surec)
            findings.extend(overprocessing_findings)
            
            # 4. Aşırı Üretim (Overproduction) - Gereksiz çıktılar
            overproduction_findings = MudaAnalyzerService._analyze_overproduction(surec)
            findings.extend(overproduction_findings)
            
        except Exception as e:
            print(f"Muda analiz hatası: {e}")
        
        return findings
    
    @staticmethod
    def _analyze_waiting(surec):
        """Bekleme (Waiting) analizi - Hedefin altında kalan performans göstergeleri"""
        findings = []
        
        try:
            # Son 3 ayın verilerini analiz et
            three_months_ago = datetime.utcnow() - timedelta(days=90)
            
            pgs = SurecPerformansGostergesi.query.filter_by(surec_id=surec.id).all()
            
            for pg in pgs:
                # Son verileri getir
                recent_data = PerformansGostergeVeri.query.filter(
                    PerformansGostergeVeri.bireysel_pg_id == pg.id,
                    PerformansGostergeVeri.veri_tarihi >= three_months_ago
                ).order_by(PerformansGostergeVeri.veri_tarihi.desc()).limit(3).all()
                
                if len(recent_data) >= 2:
                    # Son 2-3 veriyi kontrol et
                    below_target_count = sum(1 for d in recent_data if d.gerceklesen_deger < d.hedef_deger)
                    
                    if below_target_count >= 2:
                        avg_below = sum(
                            ((d.hedef_deger - d.gerceklesen_deger) / d.hedef_deger * 100)
                            for d in recent_data if d.gerceklesen_deger < d.hedef_deger
                        ) / below_target_count if below_target_count > 0 else 0
                        
                        findings.append({
                            'type': 'waiting',
                            'title': f'{pg.gosterge_adi} - Hedef Altında Performans',
                            'description': f'{pg.gosterge_adi} performans göstergesi son dönemde hedefin %{avg_below:.1f} altında gerçekleşiyor. Bu bekleme ve gecikme kaynaklı verimsizlik göstergesidir.',
                            'severity': 'high' if avg_below > 20 else 'medium',
                            'estimated_waste_hours': None,
                            'related_pg_id': pg.id
                        })
        
        except Exception as e:
            print(f"Waiting analiz hatası: {e}")
        
        return findings
    
    @staticmethod
    def _analyze_defects(surec):
        """Hata/Kusur (Defects) analizi - Tutarsız veya düşük performans"""
        findings = []
        
        try:
            pgs = SurecPerformansGostergesi.query.filter_by(surec_id=surec.id).all()
            
            for pg in pgs:
                # Varyasyon analizi - performansta büyük dalgalanmalar
                recent_data = PerformansGostergeVeri.query.filter(
                    PerformansGostergeVeri.bireysel_pg_id == pg.id
                ).order_by(PerformansGostergeVeri.veri_tarihi.desc()).limit(6).all()
                
                if len(recent_data) >= 4:
                    values = [d.gerceklesen_deger for d in recent_data]
                    if pg.hedef_deger and pg.hedef_deger > 0:
                        # Varyasyon katsayısı
                        avg_value = sum(values) / len(values)
                        variance = sum((v - avg_value) ** 2 for v in values) / len(values)
                        std_dev = variance ** 0.5
                        cv = (std_dev / avg_value * 100) if avg_value > 0 else 0
                        
                        if cv > 30:  # %30'dan fazla varyasyon
                            findings.append({
                                'type': 'defects',
                                'title': f'{pg.gosterge_adi} - Yüksek Varyasyon',
                                'description': f'{pg.gosterge_adi} performans göstergesinde %{cv:.1f} varyasyon tespit edildi. Bu tutarsızlık hata veya kalite sorunlarına işaret edebilir.',
                                'severity': 'medium',
                                'estimated_waste_hours': None,
                                'related_pg_id': pg.id
                            })
        
        except Exception as e:
            print(f"Defects analiz hatası: {e}")
        
        return findings
    
    @staticmethod
    def _analyze_overprocessing(surec):
        """Aşırı İşleme (Overprocessing) analizi - Gereksiz karmaşıklık"""
        findings = []
        
        try:
            # Çok fazla performans göstergesi = aşırı işleme işareti
            pg_count = SurecPerformansGostergesi.query.filter_by(surec_id=surec.id).count()
            
            if pg_count > 10:
                findings.append({
                    'type': 'overprocessing',
                    'title': f'{surec.ad} - Aşırı İşleme',
                    'description': f'Süreçte {pg_count} performans göstergesi bulunuyor. Bu sayı optimumun üzerinde olabilir ve gereksiz karmaşıklık yaratıyor olabilir.',
                    'severity': 'low',
                    'estimated_waste_hours': pg_count * 0.5,  # Her fazla PG için 0.5 saat
                    'related_pg_id': None
                })
        
        except Exception as e:
            print(f"Overprocessing analiz hatası: {e}")
        
        return findings
    
    @staticmethod
    def _analyze_overproduction(surec):
        """Aşırı Üretim (Overproduction) analizi - Gereksiz çıktılar"""
        findings = []
        
        try:
            # Süreç aktif mi kontrol et
            if surec.durum == 'pasif':
                findings.append({
                    'type': 'overproduction',
                    'title': f'{surec.ad} - Pasif Süreç',
                    'description': 'Bu süreç pasif durumda. Eğer artık kullanılmıyorsa, süreç çıktıları aşırı üretim sayılabilir.',
                    'severity': 'low',
                    'estimated_waste_hours': None,
                    'related_pg_id': None
                })
        
        except Exception as e:
            print(f"Overproduction analiz hatası: {e}")
        
        return findings
    
    @staticmethod
    def get_efficiency_score(kurum_id):
        """Kurumun genel verimlilik skorunu hesaplar (0-100)"""
        try:
            surecler = Surec.query.filter_by(kurum_id=kurum_id).all()
            
            if not surecler:
                return 100  # Süreç yoksa mükemmel skor
            
            total_score = 0
            surec_count = 0
            
            for surec in surecler:
                # Her süreç için verimlilik skoru
                findings = MudaAnalyzerService.analyze_process_inefficiency(surec.id, kurum_id)
                
                # Finding sayısına göre skor hesapla
                if len(findings) == 0:
                    surec_score = 100
                elif len(findings) <= 2:
                    surec_score = 80
                elif len(findings) <= 4:
                    surec_score = 60
                elif len(findings) <= 6:
                    surec_score = 40
                else:
                    surec_score = 20
                
                total_score += surec_score
                surec_count += 1
            
            return round(total_score / surec_count, 2) if surec_count > 0 else 100
        
        except Exception as e:
            print(f"Efficiency score hesaplama hatası: {e}")
            return 0





