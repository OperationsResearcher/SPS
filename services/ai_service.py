# -*- coding: utf-8 -*-
"""
AI Karar Destek Servisi
V51.0 - AI Karar Destek Asistanı
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from models import db, User, Surec, SurecPerformansGostergesi, PerformansGostergeVeri, Project, Task
from sqlalchemy import func, and_


class AIService:
    """AI Karar Destek Servisi - Kural tabanlı analiz ve öneriler"""
    
    @staticmethod
    def get_insights_for_user(user_id: int, kurum_id: int) -> List[Dict[str, Any]]:
        """
        Kullanıcı için AI insight'ları getirir.
        
        Args:
            user_id: Kullanıcı ID'si
            kurum_id: Kurum ID'si
        
        Returns:
            AI insight'ları içeren liste (max 10 öğe). Her öğe şu yapıda:
            {
                'type': str,      # 'info', 'warning', 'error'
                'title': str,     # Başlık
                'message': str,   # Mesaj
                'priority': int,  # Öncelik (yüksek sayı = yüksek öncelik)
                'action_url': str, # Aksiyon URL'i (opsiyonel)
                'icon': str       # Icon class (opsiyonel)
            }
        """
        insights = []
        
        try:
            # 1. Süreç performans analizi
            process_insights = AIService._analyze_process_performance(user_id, kurum_id)
            insights.extend(process_insights)
            
            # 2. Görev analizi
            task_insights = AIService._analyze_tasks(user_id)
            insights.extend(task_insights)
            
            # 3. Proje analizi
            project_insights = AIService._analyze_projects(user_id, kurum_id)
            insights.extend(project_insights)
            
            # 4. Genel öneriler
            general_insights = AIService._get_general_recommendations(user_id, kurum_id)
            insights.extend(general_insights)
            
        except Exception as e:
            print(f"AI insight hatası: {e}")
        
        # Önem sırasına göre sırala (önemli olanlar önce)
        insights.sort(key=lambda x: x.get('priority', 0), reverse=True)
        
        return insights[:10]  # En fazla 10 insight döndür
    
    @staticmethod
    def _analyze_process_performance(user_id: int, kurum_id: int) -> List[Dict[str, Any]]:
        """
        Süreç performans analizi yapar ve insight'lar üretir.
        
        Args:
            user_id: Kullanıcı ID'si
            kurum_id: Kurum ID'si
        
        Returns:
            Süreç performansı ile ilgili insight'lar listesi
        """
        insights = []
        
        try:
            # Kullanıcının lider olduğu süreçleri bul
            user = User.query.get(user_id)
            if not user:
                return insights
            
            # Süreç liderlerini kontrol et
            from models import surec_liderleri
            lider_surec_ids = db.session.query(surec_liderleri.c.surec_id).filter(
                surec_liderleri.c.user_id == user_id
            ).all()
            lider_surec_ids = [sid[0] for sid in lider_surec_ids]
            
            if not lider_surec_ids:
                return insights
            
            # Son 30 günün performans verilerini analiz et
            son_30_gun = datetime.now() - timedelta(days=30)
            
            # Eager loading ile süreçleri ve PG'lerini tek seferde çek
            surecler = Surec.query.filter(Surec.id.in_(lider_surec_ids[:5])).all()
            
            # Tüm PG'leri tek seferde çek (batch loading)
            surec_id_list = [s.id for s in surecler]
            if surec_id_list:
                all_pglers = SurecPerformansGostergesi.query.filter(
                    SurecPerformansGostergesi.surec_id.in_(surec_id_list)
                ).all()
                # Süreç ID'sine göre grupla
                pglers_by_surec = {}
                for pg in all_pglers:
                    if pg.surec_id not in pglers_by_surec:
                        pglers_by_surec[pg.surec_id] = []
                    pglers_by_surec[pg.surec_id].append(pg)
            
            for surec in surecler:
                # Süreç PG'lerini önceden çekilmiş listeden al
                pgler = pglers_by_surec.get(surec.id, [])
                
                # Süreç PG'leri için genel bilgilendirme
                if len(pgler) > 0:
                    insights.append({
                        'type': 'info',
                        'title': f'{surec.ad} Süreci',
                        'message': f'{surec.ad} sürecinde {len(pgler)} performans göstergesi tanımlı. Süreç karnesinden detaylı performans takibini yapabilirsiniz.',
                        'priority': 1,
                        'action_url': f'/surec-karnesi?surec_id={surec_id}',
                        'icon': 'fa-chart-line'
                    })
        except Exception as e:
            print(f"Süreç performans analizi hatası: {e}")
        
        return insights
    
    @staticmethod
    def _analyze_tasks(user_id: int) -> List[Dict[str, Any]]:
        """
        Kullanıcının görevlerini analiz eder ve insight'lar üretir.
        
        Args:
            user_id: Kullanıcı ID'si
        
        Returns:
            Görevler ile ilgili insight'lar listesi
        """
        insights = []
        
        try:
            # Kullanıcıya atanmış görevler
            gorevler = Task.query.filter_by(assigned_to=user_id).all()
            
            # Bitiş tarihi yaklaşan görevler
            bugun = datetime.now().date()
            yakin_bitis_tarihi = bugun + timedelta(days=3)
            
            yakin_gorevler = [g for g in gorevler 
                             if g.due_date and bugun <= g.due_date <= yakin_bitis_tarihi
                             and g.status != 'completed']
            
            if yakin_gorevler:
                insights.append({
                    'type': 'warning',
                    'title': f'{len(yakin_gorevler)} Görev Bitiş Tarihi Yaklaşıyor',
                    'message': f'{len(yakin_gorevler)} görevinizin bitiş tarihi 3 gün içinde.',
                    'priority': 2,
                    'action_url': '/gorevlerim',
                    'icon': 'fa-calendar-check'
                })
            
            # Geciken görevler
            geciken_gorevler = [g for g in gorevler 
                               if g.due_date and g.due_date < bugun 
                               and g.status != 'completed']
            
            if geciken_gorevler:
                insights.append({
                    'type': 'danger',
                    'title': f'{len(geciken_gorevler)} Geciken Görev',
                    'message': f'{len(geciken_gorevler)} göreviniz bitiş tarihini geçti.',
                    'priority': 5,
                    'action_url': '/gorevlerim',
                    'icon': 'fa-exclamation-circle'
                })
        except Exception as e:
            print(f"Görev analizi hatası: {e}")
        
        return insights
    
    @staticmethod
    def _analyze_projects(user_id, kurum_id):
        """Proje analizi"""
        insights = []
        
        try:
            # Kullanıcının üyesi olduğu projeler
            from models import project_members
            proje_ids = db.session.query(project_members.c.project_id).filter(
                project_members.c.user_id == user_id
            ).all()
            proje_ids = [pid[0] for pid in proje_ids]
            
            if not proje_ids:
                return insights
            
            projeler = Project.query.filter(Project.id.in_(proje_ids)).all()
            
            # Risk altındaki projeler (ilerleme düşük, bitiş yakın)
            bugun = datetime.now().date()
            risk_projeler = []
            
            for proje in projeler:
                if proje.end_date and proje.end_date <= bugun + timedelta(days=30):
                    # İlerleme hesapla
                    toplam_gorev = Task.query.filter_by(project_id=proje.id).count()
                    tamamlanan_gorev = Task.query.filter(
                        Task.project_id == proje.id,
                        Task.status.in_(['Tamamlandı', 'completed'])
                    ).count()
                    
                    ilerleme = (tamamlanan_gorev / toplam_gorev * 100) if toplam_gorev > 0 else 0
                    
                    if ilerleme < 50:
                        risk_projeler.append(proje)
            
            if risk_projeler:
                insights.append({
                    'type': 'warning',
                    'title': f'{len(risk_projeler)} Proje Risk Altında',
                    'message': f'{len(risk_projeler)} projenizde ilerleme düşük ve bitiş tarihi yakın.',
                    'priority': 3,
                    'action_url': '/projeler',
                    'icon': 'fa-project-diagram'
                })
        except Exception as e:
            print(f"Proje analizi hatası: {e}")
        
        return insights
    
    @staticmethod
    def _get_general_recommendations(user_id: int, kurum_id: int) -> List[Dict[str, Any]]:
        """Genel öneriler"""
        insights = []
        
        try:
            # Veri girişi önerisi
            insights.append({
                'type': 'info',
                'title': 'Düzenli Veri Girişi',
                'message': 'Performans göstergeleri için düzenli veri girişi yapmanız önerilir.',
                'priority': 1,
                'action_url': '/surec-karnesi',
                'icon': 'fa-info-circle'
            })
        except Exception as e:
            print(f"Genel öneriler hatası: {e}")
        
        return insights
    
    @staticmethod
    def ask_question(user_id, question, context=None):
        """Kullanıcı sorusuna AI yanıtı"""
        # Basit kural tabanlı yanıt sistemi
        question_lower = question.lower()
        
        # Soru tipine göre yanıt üret
        if 'süreç' in question_lower or 'performans' in question_lower:
            return {
                'answer': 'Süreç performansınızı Süreç Karnesi sayfasından görüntüleyebilirsiniz. Performans göstergeleri ve trendler hakkında detaylı bilgi almak için ilgili süreç seçimini yapabilirsiniz.',
                'suggestions': ['Süreç Karnesi', 'Performans Göstergeleri']
            }
        
        elif 'görev' in question_lower or 'task' in question_lower:
            return {
                'answer': 'Görevlerinizi "Görevlerim" sayfasından görüntüleyebilirsiniz. Geciken görevler ve yaklaşan bitiş tarihleri için dashboard\'u kontrol edebilirsiniz.',
                'suggestions': ['Görevlerim', 'Dashboard']
            }
        
        elif 'proje' in question_lower:
            return {
                'answer': 'Projelerinizi "Proje Yönetimi" sayfasından görüntüleyebilirsiniz. Proje detayları, ilerleme durumu ve görevler hakkında bilgi alabilirsiniz.',
                'suggestions': ['Proje Yönetimi', 'Proje Detayları']
            }
        
        else:
            return {
                'answer': 'Size nasıl yardımcı olabilirim? Sistem kullanımı, süreç yönetimi veya görev takibi hakkında sorularınızı yanıtlayabilirim.',
                'suggestions': ['Süreç Karnesi', 'Görevlerim', 'Dashboard']
            }

