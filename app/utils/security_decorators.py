# -*- coding: utf-8 -*-
"""
Kokpitim Security Decorators
SaaS mimarisinde kurumlar arası veri sızıntısını (IDOR) ve yetki ihlallerini
engellemek amacıyla tasarlanmış merkezi güvenlik mekanizmaları.
"""
from functools import wraps
from flask import request
from flask_login import current_user
from app.utils.errors import AuthorizationError, ResourceNotFoundError

def require_tenant_access(model_class, id_param_name='id', check_kurum_id=True):
    """
    Belirtilen model üzerinden, kullanıcının o kayda (veya o kurumun kayıtlarına) 
    erişim yetkisi olup olmadığını ORM seviyesinde kontrol eder.
    
    Kullanım Örneği:
        @app.route('/surec/<int:surec_id>')
        @require_tenant_access(Surec, id_param_name='surec_id')
        def get_surec(surec_id):
            ...
    
    Args:
        model_class: SQLAlchemy Model Sınıfı (Örn: Surec, Project, User)
        id_param_name: URL parametresindeki ID değişkeninin adı.
        check_kurum_id: Model üzerindeki kurum_id'ye bakarak tenant izolasyonu yapıp yapmayacağı.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Admin her şeye yetkilidir.
            if getattr(current_user, 'sistem_rol', None) == 'admin':
                return f(*args, **kwargs)

            resource_id = kwargs.get(id_param_name)
            if not resource_id:
                # URL'de ID yoksa bu dekoratörün işi değil, fonksiyona pasla.
                return f(*args, **kwargs)

            # Modeli bul
            resource = model_class.query.get(resource_id)
            if not resource:
                raise ResourceNotFoundError(f"İstenen {model_class.__name__} bulunamadı.")

            # Tenant (Kurum) İzolasyonu Kontrolü
            if check_kurum_id:
                # Modelde kurum_id özelliği var mı?
                if hasattr(resource, 'kurum_id'):
                    if resource.kurum_id != current_user.kurum_id:
                        raise AuthorizationError(f"Bu {model_class.__name__} kaydına erişim yetkiniz (Kurum uyumsuzluğu) bulunmamaktadır.")
                # Bazı modeller tenant'ı başka isimle tutabilir (Örn: project.kurum_id vs). 
                # Model bazlı özel izolasyon gerekiyorsa buraya eklenebilir.

            # İhtiyaç duyulursa f() fonksiyonuna objeyi `resource_obj` argümanı olarak da enjekte edebiliriz.
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def require_process_access(id_param_name='surec_id'):
    """
    Süreçlere özel hiyerarşik erişim kontrolü sağlar.
    Admin -> Sınırsız
    Kurum Yöneticisi / Üst Yönetim -> Kurum içerisindeki tüm süreçlere
    Standart Kullanıcı -> Sadece lideri veya üyesi olduğu süreçlere
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if getattr(current_user, 'sistem_rol', None) == 'admin':
                return f(*args, **kwargs)
                
            surec_id = kwargs.get(id_param_name)
            if not surec_id:
                return f(*args, **kwargs)
                
            from models import db, Surec, surec_liderleri, surec_uyeleri
            surec = Surec.query.get(surec_id)
            if not surec:
                raise ResourceNotFoundError("Süreç bulunamadı.")
                
            if current_user.sistem_rol in ['kurum_yoneticisi', 'ust_yonetim']:
                if surec.kurum_id != current_user.kurum_id:
                    raise AuthorizationError("Bu süreçte yetkiniz (Kurum uyumsuzluğu) yok.")
            else:
                lider_mi = db.session.query(surec_liderleri).filter(
                    surec_liderleri.c.surec_id == surec_id, 
                    surec_liderleri.c.user_id == current_user.id
                ).first() is not None
                
                uye_mi = db.session.query(surec_uyeleri).filter(
                    surec_uyeleri.c.surec_id == surec_id, 
                    surec_uyeleri.c.user_id == current_user.id
                ).first() is not None
                
                if not (lider_mi or uye_mi):
                    raise AuthorizationError("Bu süreçte yetkiniz (Lider/Üye değilsiniz) yok.")
                    
            return f(*args, **kwargs)
        return decorated_function
    return decorator
