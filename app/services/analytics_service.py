"""
Analytics Service
Sprint 10-12: Analytics ve Raporlama
Gelişmiş analitik ve raporlama servisi
"""

from extensions import db
from app.services.date_sovereign import resolve_request_year
from app.services.score_engine_service import compute_pg_score
from app.models.process import Process, ProcessKpi, KpiData
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
from sqlalchemy import func, and_, or_
from collections import defaultdict

# pandas ağır kütüphane — ilk kullanımda yükle
def _pd():
    import pandas as pd
    return pd

class AnalyticsService:
    """Analytics ve raporlama servisi"""
    
    @staticmethod
    def get_performance_trend(
        process_id: int,
        kpi_id: int,
        start_date: datetime,
        end_date: datetime,
        frequency: str = 'monthly'
    ) -> Dict:
        """
        KPI performans trendi
        
        Args:
            process_id: Süreç ID
            kpi_id: KPI ID
            start_date: Başlangıç tarihi
            end_date: Bitiş tarihi
            frequency: Frekans (daily, weekly, monthly, quarterly)
        
        Returns:
            Trend verisi (dates, actual_values, target_values, performance_rates)
        """
        _empty = {'dates': [], 'actual_values': [], 'target_values': [], 'performance_rates': []}
        try:
            kpi_data = KpiData.query.filter(
                KpiData.process_kpi_id == kpi_id,
                KpiData.data_date.between(start_date, end_date),
                KpiData.is_active.is_(True)
            ).order_by(KpiData.data_date).all()
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"[analytics] KPI trend sorgu hatası: {e}")
            return _empty

        if not kpi_data:
            return _empty
        
        # DataFrame'e çevir
        pd = _pd()
        df = pd.DataFrame([{
            'date': d.data_date,
            'actual': d.actual_value,
            'target': d.target_value
        } for d in kpi_data])

        # actual_value/target_value DB'de String(100) — sayısal işlemler (mean,
        # bölme) öncesi güvenli dönüşüm; ayrıştırılamayan değer NaN olur.
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
        df['actual'] = pd.to_numeric(df['actual'], errors='coerce')
        df['target'] = pd.to_numeric(df['target'], errors='coerce')
        df = df.dropna(subset=['date'])
        if df.empty:
            return _empty

        # Frekansa göre grupla
        if frequency == 'daily':
            grouped = df
        elif frequency == 'weekly':
            df['week'] = df['date'].dt.to_period('W')
            grouped = df.groupby('week').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['week'].dt.start_time
        elif frequency == 'monthly':
            df['month'] = df['date'].dt.to_period('M')
            grouped = df.groupby('month').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['month'].dt.start_time
        elif frequency == 'quarterly':
            df['quarter'] = df['date'].dt.to_period('Q')
            grouped = df.groupby('quarter').agg({
                'actual': 'mean',
                'target': 'mean'
            }).reset_index()
            grouped['date'] = grouped['quarter'].dt.start_time
        else:
            grouped = df
        
        # Performans oranını hesapla (hedef 0/NaN → sonsuz/NaN'ı temizle)
        grouped['performance_rate'] = (grouped['actual'] / grouped['target'] * 100)
        grouped['performance_rate'] = (
            grouped['performance_rate']
            .replace([float('inf'), float('-inf')], pd.NA)
            .round(2)
        )

        def _clean(series):
            return [None if pd.isna(v) else v for v in series.tolist()]

        return {
            'dates': grouped['date'].dt.strftime('%Y-%m-%d').tolist(),
            'actual_values': _clean(grouped['actual']),
            'target_values': _clean(grouped['target']),
            'performance_rates': _clean(grouped['performance_rate'])
        }

    
    @staticmethod
    def get_process_health_score(process_id: int, year: int = None) -> Dict:
        """
        Süreç sağlık skoru
        
        Returns:
            {
                'overall_score': 85.5,
                'kpi_scores': [...],
                'status': 'good',
                'recommendations': [...]
            }
        """
        if year is None:
            # S8: K-Radar/Analiz artık yıl seçimini onurlandırır
            year = resolve_request_year()
        
        # Süreç KPI'larını çek
        kpis = ProcessKpi.query.filter_by(
            process_id=process_id,
            is_active=True
        ).all()
        
        if not kpis:
            return {
                'overall_score': 0,
                'kpi_scores': [],
                'status': 'no_data',
                'recommendations': ['KPI tanımlanmamış']
            }
        
        # Tüm KPI'ların en son verisini tek sorguda topla (N+1 önlemi)
        #
        # B4 (2026-07-21): `year` yukarıda resolve_request_year() ile çözülüyor
        # ama BU SORGUDA HİÇ KULLANILMIYORDU — değişken kullanılmadan ölüyordu.
        # Ölçüm: yıl filtresiz "en son veri" seçiminde 118 KPI hâlâ 2020
        # verisiyle puanlanıyordu; KPI'ların yalnız %12'si 2026'ya bakıyordu.
        # Kullanıcı 2026'yı seçse bile aynı skoru görüyordu.
        #
        # Ayrıca `data_date <= bugün` sınırı yoktu → DB'deki 22.579 gelecek
        # tarihli aktif satır "en son" seçiliyordu.
        _kpi_ids = [k.id for k in kpis]
        _latest_by_kid = {}
        if _kpi_ids:
            _q = KpiData.query.filter(
                KpiData.process_kpi_id.in_(_kpi_ids),
                KpiData.is_active.is_(True),
                KpiData.data_date <= date.today(),
            )
            if year:
                _q = _q.filter(KpiData.year == year)
            for d in _q.order_by(
                KpiData.process_kpi_id, KpiData.data_date.desc()
            ).all():
                if d.process_kpi_id not in _latest_by_kid:
                    _latest_by_kid[d.process_kpi_id] = d

        kpi_scores = []
        total_weight = 0
        weighted_score = 0

        from app.utils.numeric import safe_float

        for kpi in kpis:
            latest_data = _latest_by_kid.get(kpi.id)
            if not latest_data:
                continue
            tgt = safe_float(latest_data.target_value)
            act = safe_float(latest_data.actual_value)
            if tgt is None or act is None or tgt <= 0:
                continue
            # B3 (2026-07-21): `kpi.direction` HİÇ OKUNMUYORDU → 604 aktif
            # `Decreasing` PG tam ters puanlanıyordu:
            #   hedef=10, gerçekleşen=50 (KÖTÜ) → 500.0 → 'excellent'
            #   hedef=10, gerçekleşen=2  (İYİ)  →  20.0 → 'critical'
            # Maliyet/hata/şikâyet göstergeleri tersine okunuyordu. Kardeş
            # motorlar (compute_pg_score, process_health_service) doğru
            # yapıyordu; bu motora yazılmamıştı.
            #
            # Üst sınır kırpması da yoktu → tek sapan KPI ağırlıklı ortalamayı
            # 500'e taşıyabiliyordu. compute_pg_score her ikisini de halleder.
            performance = compute_pg_score(tgt, act, kpi.direction or 'Increasing')
            if performance is None:
                continue
            weight = kpi.weight or 1

            kpi_scores.append({
                'kpi_id': kpi.id,
                'kpi_name': kpi.name,
                'performance': round(performance, 2),
                'weight': weight,
                'status': AnalyticsService._get_performance_status(performance)
            })

            weighted_score += performance * weight
            total_weight += weight
        
        overall_score = round(weighted_score / total_weight, 2) if total_weight > 0 else 0
        status = AnalyticsService._get_performance_status(overall_score)
        recommendations = AnalyticsService._generate_recommendations(kpi_scores, overall_score)
        
        return {
            'overall_score': overall_score,
            'kpi_scores': kpi_scores,
            'status': status,
            'recommendations': recommendations
        }
    
    @staticmethod
    def _get_performance_status(performance: float) -> str:
        """Performans durumu"""
        if performance >= 100:
            return 'excellent'
        elif performance >= 90:
            return 'good'
        elif performance >= 80:
            return 'fair'
        elif performance >= 70:
            return 'poor'
        else:
            return 'critical'
    
    @staticmethod
    def _generate_recommendations(kpi_scores: List[Dict], overall_score: float) -> List[str]:
        """Öneriler oluştur"""
        recommendations = []
        
        # Genel durum
        if overall_score < 70:
            recommendations.append('Acil aksiyon gerekiyor: Genel performans kritik seviyede')
        elif overall_score < 80:
            recommendations.append('Dikkat: Performans hedefin altında')
        elif overall_score >= 100:
            recommendations.append('Tebrikler! Tüm hedefler aşıldı')
        
        # Düşük performanslı KPI'lar
        poor_kpis = [k for k in kpi_scores if k['performance'] < 80]
        if poor_kpis:
            recommendations.append(f'{len(poor_kpis)} KPI hedefin altında: {", ".join([k["kpi_name"] for k in poor_kpis[:3]])}')
        
        # Yüksek ağırlıklı düşük performanslı KPI'lar
        critical_kpis = [k for k in kpi_scores if k['performance'] < 70 and k['weight'] > 5]
        if critical_kpis:
            recommendations.append(f'Yüksek öncelikli KPI\'lar kritik seviyede: {", ".join([k["kpi_name"] for k in critical_kpis])}')
        
        return recommendations
    
    @staticmethod
    def get_comparative_analysis(
        process_ids: List[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[int] = None,
    ) -> Dict:
        """
        Süreçler arası karşılaştırmalı analiz

        Args:
            tenant_id: Verilirse yalnız o kuruma ait süreçler döner.
            start_date / end_date: ŞU AN KULLANILMIYOR (gövdede hiç okunmuyor).
                Zorunluyken iki çağıran (`micro/modules/analiz/routes.py:155`
                ve `micro/modules/api/routes.py:244`) bunları geçirmiyordu →
                `TypeError` → dıştaki except → sessizce 500. Opsiyonel
                yapıldı; imza korunuyor ki mevcut 2 çağrı da bozulmasın.

        Returns:
            {
                'processes': [...],
                'comparison_data': {...}
            }
        """
        # Toplu süreç çekimi (N+1 önlemi)
        #
        # B13 (2026-07-21): Burada tenant filtresi yoktu ve kod yorumu bunu
        # açıkça çağırana devrediyordu ("caller sorumluluğu"). Çıktı
        # `process_name` ve `process_code` döndürdüğü için başka kurumun
        # süreç adı/kodu sızabiliyordu. S2/S3 ile aynı desen: savunmanın
        # çağırana bırakılması. Filtre artık burada.
        _q = Process.query.filter(Process.id.in_(process_ids)) if process_ids else None
        if _q is not None and tenant_id is not None:
            _q = _q.filter(Process.tenant_id == tenant_id)
        _procs_by_id = {p.id: p for p in _q.all()} if _q is not None else {}

        comparison_data = []

        for process_id in process_ids:
            process = _procs_by_id.get(process_id)
            if not process:
                continue

            health = AnalyticsService.get_process_health_score(process_id)
            
            comparison_data.append({
                'process_id': process_id,
                'process_name': process.name,
                'process_code': process.code,
                'overall_score': health['overall_score'],
                'status': health['status'],
                'kpi_count': len(health['kpi_scores'])
            })
        
        # Sıralama (en yüksek skordan en düşüğe)
        comparison_data.sort(key=lambda x: x['overall_score'], reverse=True)
        
        return {
            'processes': comparison_data,
            'best_performer': comparison_data[0] if comparison_data else None,
            'worst_performer': comparison_data[-1] if comparison_data else None,
            'average_score': round(sum([p['overall_score'] for p in comparison_data]) / len(comparison_data), 2) if comparison_data else 0
        }
    
    @staticmethod
    def get_anomaly_detection(
        kpi_id: int,
        lookback_days: int = 90,
        threshold: float = 2.0
    ) -> Dict:
        """
        Anomali tespiti (basit istatistiksel yöntem)
        
        Args:
            kpi_id: KPI ID
            lookback_days: Geriye bakış günü
            threshold: Standart sapma eşiği
        
        Returns:
            Anomali verisi
        """
        start_date = datetime.now() - timedelta(days=lookback_days)
        
        kpi_data = KpiData.query.filter(
            KpiData.process_kpi_id == kpi_id,
            KpiData.data_date >= start_date,
            KpiData.is_active.is_(True)
        ).order_by(KpiData.data_date).all()
        
        if len(kpi_data) < 10:
            return {
                'anomalies': [],
                'message': 'Yeterli veri yok (minimum 10 veri noktası gerekli)'
            }
        
        # DataFrame'e çevir
        df = _pd().DataFrame([{
            'date': d.data_date,
            'value': d.actual_value
        } for d in kpi_data])
        
        # İstatistikler
        mean = df['value'].mean()
        std = df['value'].std()
        
        # Anomalileri tespit et (z-score yöntemi)
        df['z_score'] = (df['value'] - mean) / std
        df['is_anomaly'] = df['z_score'].abs() > threshold
        
        anomalies = df[df['is_anomaly']].to_dict('records')
        
        return {
            'anomalies': [{
                'date': a['date'].strftime('%Y-%m-%d'),
                'value': a['value'],
                'z_score': round(a['z_score'], 2),
                'deviation': round(((a['value'] - mean) / mean) * 100, 2)
            } for a in anomalies],
            'statistics': {
                'mean': round(mean, 2),
                'std': round(std, 2),
                'min': round(df['value'].min(), 2),
                'max': round(df['value'].max(), 2)
            }
        }
    
    @staticmethod
    def get_forecast(
        process_id: int,
        periods: int = 3,
        method: str = 'moving_average'
    ) -> Dict:
        """SÜREÇ tahmini — kanonik motor `forecast_service`'e devreder (TASK-256).

        ⚠️ İMZA DEĞİŞTİ: eskiden `kpi_id` bekliyordu ama çağıran route
        (`analiz_api_forecast`) `process_id` geçiriyordu — analiz ekranında
        kullanıcı SÜREÇ seçiyor. Sonuç: 380 süreçten 366'sında hiç veri
        bulunamıyordu ("Yeterli veri yok"), ID'si çakışan 14'ünde ise BAŞKA
        bir KPI'ın tahmini gösteriliyordu. Kardeş servis
        `get_process_health_score(process_id)` ile de tutarsızdı.
        Artık süreç ID'si alınır ve sürecin KPI'ları üzerinden hesaplanır.

        2026-07-15 öncesi bu fonksiyonun kendi implementasyonu vardı ve
        GERÇEK VERİYLE PATLIYORDU:
          - `'value': d.actual_value` ham METİN veriyordu; pandas `.mean()`
            string kolonda `'81.79'+'70.29'+'87.83'` → `'81.7970.2987.83'`
            birleştirip TypeError fırlatıyordu (gerçek KPI ile doğrulandı).
          - `linear_trend` dalı da aynı sebeple kırıktı (string çıkarma).
          - Çağıran route hatayı `except` ile yutuyordu → kullanıcı yalnız
            "Tahmin verisi alınamadı" görüyor, sebebi hiç anlaşılmıyordu.

        Artık tek kanonik motor var: `forecast_service.forecast_kpi`
        (linear regression + %95 güven aralığı + R², saf Python, testli).
        Bu sarmalayıcı yalnız çıktı biçimini koruyor — `analiz.js` mevcut
        alan adlarını (`forecast[].date/forecast_value/confidence`) bekliyor.

        `method` parametresi artık YÖNTEM SEÇMİYOR (tek motor var); geriye
        dönük uyumluluk için imzada kalıyor ve çıktıda raporlanıyor.
        """
        from sqlalchemy import func
        from app.services.forecast_service import forecast_kpi

        # Sürecin EN ÇOK VERİYE sahip KPI'ı seçilir.
        # Neden tek KPI? Süreç birden çok KPI taşır ve bunlar farklı birimlerde
        # olabilir (adet, %, TL) — toplayıp ortalamak anlamsız sayı üretir.
        # En çok ölçümü olan KPI hem en güvenilir trendi verir hem de kullanıcı
        # için sürecin "ana göstergesi" olma ihtimali en yüksek olandır.
        # Çıktıda hangi KPI kullanıldığı raporlanır (kpi_id/kpi_name) — kullanıcı
        # neye baktığını bilmeli.
        kpi_satiri = (
            db.session.query(ProcessKpi.id, ProcessKpi.name, func.count(KpiData.id).label('n'))
            .outerjoin(KpiData, (KpiData.process_kpi_id == ProcessKpi.id) & (KpiData.is_active.is_(True)))
            .filter(ProcessKpi.process_id == process_id)
            .group_by(ProcessKpi.id, ProcessKpi.name)
            .order_by(func.count(KpiData.id).desc())
            .first()
        )

        if not kpi_satiri or not kpi_satiri.n:
            return {
                'forecast': [],
                'method': method,
                'historical_data': [],
                'message': 'Bu süreçte tahmin için veri girilmiş gösterge yok',
            }

        kpi_id = kpi_satiri.id
        sonuc = forecast_kpi(kpi_id, periods_ahead=periods)

        if not sonuc.get('success'):
            return {
                'forecast': [],
                'method': method,
                'kpi_id': kpi_id,
                'kpi_name': kpi_satiri.name,
                'historical_data': [],
                'message': sonuc.get('message', 'Yeterli veri yok (minimum 3 veri noktası gerekli)'),
            }

        # Son gerçek veri tarihi — tahmin tarihleri buradan ileri sayılır.
        # forecast_service dönem etiketi ("T+1") üretir, takvim tarihi değil;
        # analiz ekranı tarih beklediği için burada türetilir (~30 gün/dönem).
        son_veri = (
            KpiData.query
            .filter(KpiData.process_kpi_id == kpi_id, KpiData.is_active.is_(True))
            .order_by(KpiData.data_date.desc())
            .first()
        )
        son_tarih = son_veri.data_date if son_veri else datetime.now().date()

        # R² → güven etiketi. Eski kod sabit 'medium'/'low' yazıyordu (veriye
        # bakmadan); artık modelin gerçek uyumunu yansıtıyor.
        r2 = sonuc.get('r_squared') or 0
        guven = 'high' if r2 >= 0.7 else 'medium' if r2 >= 0.4 else 'low'

        forecast = []
        for i, p in enumerate(sonuc.get('forecast', []), start=1):
            forecast.append({
                'date': (son_tarih + timedelta(days=30 * i)).strftime('%Y-%m-%d'),
                'forecast_value': p['value'],
                'confidence': guven,
                'confidence_low': p.get('confidence_low'),
                'confidence_high': p.get('confidence_high'),
            })

        return {
            'forecast': forecast,
            'method': method,
            # Hangi göstergeye bakıldığı görünür olmalı — süreçte birden çok
            # KPI varsa kullanıcı hangisinin tahmin edildiğini bilmeli.
            'kpi_id': kpi_id,
            'kpi_name': kpi_satiri.name,
            'r_squared': sonuc.get('r_squared'),
            'trend_direction': sonuc.get('trend_direction'),
            'samples': sonuc.get('samples'),
            'historical_data': [
                {'date': h['label'], 'value': h['value']}
                for h in sonuc.get('history', [])[-6:]
            ]
        }
