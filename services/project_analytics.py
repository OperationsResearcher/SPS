# -*- coding: utf-8 -*-
"""
Proje Yönetimi Analitik Servisleri
Süreç Sağlık Skoru hesaplama ve diğer analitik işlemler
"""
from datetime import date
from flask import current_app
from models import (
    db, Surec, Project, Task, TaskImpact, BireyselPerformansGostergesi,
    PerformansGostergeVeri, SurecPerformansGostergesi, ProjectRisk
)
from sqlalchemy import func, and_


def calculate_surec_saglik_skoru(surec_id, yil=None):
    """
    Bir sürecin sağlık skorunu hesaplar
    
    Skor hesaplama formülü:
    - Proje Tamamlama Oranı: %25 ağırlık
    - Geciken Görev Oranı: %25 ağırlık (düşük = iyi)
    - PG Hedef Ulaşma Oranı: %35 ağırlık
    - Risk Faktörü: %15 ağırlık (yüksek risk = düşük skor)
    
    Returns:
        dict: {
            'skor': float (0-100 arası),
            'detaylar': {
                'proje_tamamlama_orani': float,
                'geciken_gorev_orani': float,
                'pg_hedef_ulasma_orani': float
            },
            'durum': str ('iyi', 'orta', 'kötü')
        }
    """
    if yil is None:
        from datetime import datetime
        yil = datetime.now().year

    def _parse_float_tr(value):
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return float(value)
        text = str(value).strip()
        if not text:
            return None
        text = text.replace(' ', '').replace('%', '')
        # 1.234,56 -> 1234.56
        if ',' in text and '.' in text:
            text = text.replace('.', '').replace(',', '.')
        else:
            text = text.replace(',', '.')
        try:
            return float(text)
        except ValueError:
            return None
    
    try:
        surec = Surec.query.get(surec_id)
        if not surec:
            return None
        
        # 1. Proje Tamamlama Oranı (%25) - Optimize edilmiş
        # Association table üzerinden bağlı projeleri bul (arşivlenmiş projeler hariç)
        from models import project_related_processes
        bagli_proje_ids = db.session.query(project_related_processes.c.project_id).filter(
            project_related_processes.c.surec_id == surec_id
        ).all()
        bagli_proje_ids = [row[0] for row in bagli_proje_ids]
        bagli_projeler = Project.query.filter(
            Project.id.in_(bagli_proje_ids),
            Project.is_archived == False
        ).all() if bagli_proje_ids else []
        
        proje_tamamlama_orani = None
        toplam_gorev_sayisi = 0
        acik_gorev_sayisi = 0
        geciken_gorev_sayisi = 0
        if bagli_projeler:
            # Performans optimizasyonu: Tüm görevleri tek sorguda getir
            proje_id_list = [p.id for p in bagli_projeler]
            all_proje_tasks = Task.query.filter(Task.project_id.in_(proje_id_list)).all()
            tasks_by_project = {}
            for task in all_proje_tasks:
                if task.project_id not in tasks_by_project:
                    tasks_by_project[task.project_id] = []
                tasks_by_project[task.project_id].append(task)

            # Proje bazında ortalama tamamlama oranı (görevi olan projeler üzerinden)
            proje_oranlari = []
            for proje in bagli_projeler:
                proje_gorevleri = tasks_by_project.get(proje.id, [])
                if proje_gorevleri:
                    tamamlanan = sum(1 for g in proje_gorevleri if g.status == 'Tamamlandı')
                    proje_oranlari.append((tamamlanan / len(proje_gorevleri)) * 100)
            if proje_oranlari:
                proje_tamamlama_orani = sum(proje_oranlari) / len(proje_oranlari)

            # 2. Görev Zamanında Oranı (geciken düşük = iyi) - açık görevler üzerinden
            bugun = date.today()
            toplam_gorev_sayisi = len(all_proje_tasks)
            acik_gorevler = [g for g in all_proje_tasks if g.status != 'Tamamlandı']
            acik_gorev_sayisi = len(acik_gorevler)
            geciken_gorev_sayisi = len([g for g in acik_gorevler if g.due_date and g.due_date < bugun])
        
        # Gecikme oranı ve cezası (raporlama için)
        gecikme_cezasi = 0.0
        geciken_gorev_orani = None  # UI tarafında bar, "yüksek=iyi" bekliyor
        if toplam_gorev_sayisi and toplam_gorev_sayisi > 0:
            if acik_gorev_sayisi > 0:
                gecikme_orani = (geciken_gorev_sayisi / acik_gorev_sayisi) * 100
                geciken_gorev_orani = max(0.0, 100.0 - gecikme_orani)  # Zamanında görev oranı
            else:
                # Tüm görevler tamamlandıysa gecikme yok kabul edilir
                geciken_gorev_orani = 100.0
            gecikme_cezasi = min(20.0, ((100.0 - (geciken_gorev_orani or 0.0)) * 0.2))
        
        # 3. PG Hedef Ulaşma Oranı (%40)
        surec_pgleri = SurecPerformansGostergesi.query.filter_by(surec_id=surec_id).all()
        pg_hedef_ulasma_orani = None
        
        if surec_pgleri:
            pg_skorlari = []
            for surec_pg in surec_pgleri:
                hedef = _parse_float_tr(surec_pg.hedef_deger)
                if not hedef or hedef <= 0:
                    continue

                bireysel_pgler = BireyselPerformansGostergesi.query.filter_by(
                    kaynak_surec_pg_id=surec_pg.id,
                    kaynak='Süreç'
                ).all()
                if not bireysel_pgler:
                    continue

                toplam_gerceklesen = 0.0
                veri_var = False
                for bpg in bireysel_pgler:
                    en_son_veri = PerformansGostergeVeri.query.filter_by(
                        bireysel_pg_id=bpg.id,
                        yil=yil
                    ).order_by(PerformansGostergeVeri.veri_tarihi.desc()).first()
                    if not en_son_veri or en_son_veri.gerceklesen_deger is None:
                        continue
                    gerceklesen = _parse_float_tr(en_son_veri.gerceklesen_deger)
                    if gerceklesen is None:
                        continue
                    toplam_gerceklesen += gerceklesen
                    veri_var = True

                if veri_var:
                    pg_skorlari.append(min(100.0, (toplam_gerceklesen / hedef) * 100.0))

            if pg_skorlari:
                pg_hedef_ulasma_orani = sum(pg_skorlari) / len(pg_skorlari)
        
        # 4. Risk Faktörü - Kritik risk cezası (%15 direkt düşüş) - Optimize edilmiş
        risk_faktoru = 100.0  # Varsayılan: risk yoksa tam skor
        kritik_risk_var_mi = False  # En az bir kritik risk var mı?
        kritik_risk_sayisi = 0
        
        if bagli_projeler:
            # Performans optimizasyonu: Tüm riskleri tek sorguda getir
            proje_id_list = [p.id for p in bagli_projeler]
            all_risks = ProjectRisk.query.filter(
                and_(
                    ProjectRisk.project_id.in_(proje_id_list),
                    ProjectRisk.status == 'Aktif'
                )
            ).all()
            risks_by_project = {}
            for risk in all_risks:
                if risk.project_id not in risks_by_project:
                    risks_by_project[risk.project_id] = []
                risks_by_project[risk.project_id].append(risk)
            
            toplam_risk_skoru = 0.0
            proje_sayisi_riskli = 0
            
            for proje in bagli_projeler:
                # Projenin aktif risklerini bul (optimize edilmiş)
                aktif_risks = risks_by_project.get(proje.id, [])
                
                if aktif_risks:
                    # Yüksek riskli (Kırmızı bölge: risk_score >= 15) risklerin sayısı
                    yuksek_riskli = [r for r in aktif_risks if r.risk_score >= 15]
                    kritik_riskli = [r for r in aktif_risks if r.risk_score >= 20]
                    
                    # Kritik risk kontrolü: En az bir kritik risk varsa işaretle
                    if kritik_riskli:
                        kritik_risk_var_mi = True
                        kritik_risk_sayisi += len(kritik_riskli)
                    
                    # Risk skoru: Kritik riskler daha fazla ceza verir
                    proje_risk_skoru = 100.0
                    if kritik_riskli:
                        # Her kritik risk için -20 puan
                        proje_risk_skoru -= len(kritik_riskli) * 20
                    elif yuksek_riskli:
                        # Her yüksek risk için -10 puan
                        proje_risk_skoru -= len(yuksek_riskli) * 10
                    
                    proje_risk_skoru = max(0, proje_risk_skoru)
                    toplam_risk_skoru += proje_risk_skoru
                    proje_sayisi_riskli += 1
            
            if proje_sayisi_riskli > 0:
                risk_faktoru = toplam_risk_skoru / proje_sayisi_riskli
            else:
                risk_faktoru = 100.0  # Risk yoksa tam skor
        
        # Ağırlıklı skor hesapla (yalnızca veri olan bileşenlerle)
        components = []
        if proje_tamamlama_orani is not None:
            components.append((proje_tamamlama_orani, 0.25))
        if geciken_gorev_orani is not None:
            components.append((geciken_gorev_orani, 0.25))
        if pg_hedef_ulasma_orani is not None:
            components.append((pg_hedef_ulasma_orani, 0.35))
        if bagli_projeler:
            # Proje yoksa risk bileşeni de yok kabul edilir
            components.append((risk_faktoru, 0.15))

        veri_yok = False
        if not components:
            agirlikli_skor = 0.0
            veri_yok = True
        else:
            weight_sum = sum(w for _, w in components)
            agirlikli_skor = sum(v * w for v, w in components) / (weight_sum or 1.0)
        
        # Skoru 0-100 aralığında sınırla
        agirlikli_skor = max(0, min(100, agirlikli_skor))
        
        # Durum belirleme
        if veri_yok:
            durum = 'orta'
        elif agirlikli_skor >= 80:
            durum = 'iyi'
        elif agirlikli_skor >= 50:
            durum = 'orta'
        else:
            durum = 'kotu'
        
        # Skor kırıcı etkenleri belirle (top 2)
        etkenler = []
        if geciken_gorev_sayisi > 0:
            etkenler.append({
                'etken': 'Geciken Görev',
                'deger': f'{geciken_gorev_sayisi} görev',
                'etki': f'-%{round(gecikme_cezasi, 1)}',
                'etki_sayi': -gecikme_cezasi  # Sıralama için sayısal değer
            })
        if kritik_risk_var_mi:
            etkenler.append({
                'etken': 'Kritik Risk',
                'deger': f'{kritik_risk_sayisi} risk',
                'etki': '-%15.0',
                'etki_sayi': -15.0  # Sıralama için sayısal değer
            })
        if proje_tamamlama_orani < 70:
            etkenler.append({
                'etken': 'Düşük Tamamlanma',
                'deger': f'%{round(proje_tamamlama_orani, 1)}',
                'etki': f'%{round(proje_tamamlama_orani, 1)}',
                'etki_sayi': proje_tamamlama_orani - 70  # Ne kadar düşükse o kadar negatif
            })
        if pg_hedef_ulasma_orani < 70:
            etkenler.append({
                'etken': 'PG Hedef Ulaşma',
                'deger': f'%{round(pg_hedef_ulasma_orani, 1)}',
                'etki': f'%{round(pg_hedef_ulasma_orani, 1)}',
                'etki_sayi': pg_hedef_ulasma_orani - 70  # Ne kadar düşükse o kadar negatif
            })
        
        # En çok etki eden top 2 etkeni seç (en düşük etki_sayi = en kötü)
        top_etkenler = sorted(etkenler, key=lambda x: x.get('etki_sayi', 0))[:2]
        # etki_sayi'yi temizle (UI'a gönderme)
        for etken in top_etkenler:
            etken.pop('etki_sayi', None)
        
        return {
            'skor': round(agirlikli_skor, 2),
            'detaylar': {
                'proje_tamamlama_orani': round(proje_tamamlama_orani, 2) if proje_tamamlama_orani is not None else None,
                'geciken_gorev_orani': round(geciken_gorev_orani, 2) if geciken_gorev_orani is not None else None,
                'pg_hedef_ulasma_orani': round(pg_hedef_ulasma_orani, 2) if pg_hedef_ulasma_orani is not None else None,
                'risk_faktoru': round(risk_faktoru, 2),
                'gecikme_cezasi': round(gecikme_cezasi, 2),
                'kritik_risk_cezasi': 15.0 if kritik_risk_var_mi else 0.0,
                'geciken_gorev_sayisi': geciken_gorev_sayisi,
                'kritik_risk_sayisi': kritik_risk_sayisi,
                'toplam_gorev_sayisi': toplam_gorev_sayisi,
                'acik_gorev_sayisi': acik_gorev_sayisi,
                'bagli_proje_sayisi': len(bagli_projeler),
                'veri_yok': veri_yok
            },
            'durum': durum,
            'yil': yil,
            'top_etkenler': top_etkenler  # En çok puan kıran top 2 etken
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Süreç sağlık skoru hesaplama hatası: {e}')
        return None


























