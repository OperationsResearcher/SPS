# -*- coding: utf-8 -*-
"""
KalDer kurumunu, KalDerAdmin kullanıcısını ve bu kuruma/kullanıcıya ait
tüm verileri sistemden kalıcı olarak siler.

Çalıştırma: py scripts/remove_kalder_completely.py
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from __init__ import create_app
from extensions import db
from models import (
    Kurum,
    User,
    AnaStrateji,
    AltStrateji,
    Surec,
    SurecPerformansGostergesi,
    SurecFaaliyet,
    BireyselPerformansGostergesi,
    BireyselFaaliyet,
    PerformansGostergeVeri,
    PerformansGostergeVeriAudit,
    FaaliyetTakip,
    FavoriKPI,
    StrategyProcessMatrix,
    StrategyMapLink,
    AnalysisItem,
    TowsMatrix,
    Deger,
    EtikKural,
    KalitePolitikasi,
    Notification,
    Feedback,
    UserActivityLog,
    Note,
    DashboardLayout,
    KullaniciYetki,
    OzelYetki,
)
from models.process import surec_uyeleri, surec_liderleri, surec_alt_stratejiler, process_owners

KALDER_KURUM_AD = "KalDer"
KALDER_ADMIN_USERNAME = "KalDerAdmin"


def main():
    app = create_app()
    with app.app_context():
        kurum = Kurum.query.filter(Kurum.kisa_ad.ilike(KALDER_KURUM_AD)).first()
        if not kurum:
            print("KalDer kurumu bulunamadı. Zaten silinmiş olabilir.")
            return 0
        user = User.query.filter(User.username == KALDER_ADMIN_USERNAME, User.kurum_id == kurum.id).first()
        kurum_id = kurum.id
        user_id = user.id if user else None

        print("KalDer ve KalDerAdmin ile ilgili tüm veriler siliniyor...")

        # 1) PerformansGostergeVeriAudit (PerformansGostergeVeri üzerinden)
        bireysel_pg_ids = [r.id for r in BireyselPerformansGostergesi.query.filter_by(user_id=user_id).all()] if user_id else []
        if bireysel_pg_ids:
            pg_veri_ids = [r.id for r in PerformansGostergeVeri.query.filter(PerformansGostergeVeri.bireysel_pg_id.in_(bireysel_pg_ids)).all()]
            if pg_veri_ids:
                PerformansGostergeVeriAudit.query.filter(PerformansGostergeVeriAudit.pg_veri_id.in_(pg_veri_ids)).delete(synchronize_session=False)
            PerformansGostergeVeri.query.filter(PerformansGostergeVeri.bireysel_pg_id.in_(bireysel_pg_ids)).delete(synchronize_session=False)

        # 2) BireyselPerformansGostergesi (KalDerAdmin)
        if user_id:
            BireyselPerformansGostergesi.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            BireyselFaaliyet.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            FaaliyetTakip.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            FavoriKPI.query.filter_by(user_id=user_id).delete(synchronize_session=False)

        # 3) KalDer süreçleri ve bağlı KPI'lar
        surec_ids = [s.id for s in Surec.query.filter_by(kurum_id=kurum_id).all()]
        if surec_ids:
            FavoriKPI.query.filter(FavoriKPI.surec_pg_id.in_(
                db.session.query(SurecPerformansGostergesi.id).filter(SurecPerformansGostergesi.surec_id.in_(surec_ids))
            )).delete(synchronize_session=False)
            SurecPerformansGostergesi.query.filter(SurecPerformansGostergesi.surec_id.in_(surec_ids)).delete(synchronize_session=False)
            SurecFaaliyet.query.filter(SurecFaaliyet.surec_id.in_(surec_ids)).delete(synchronize_session=False)
            StrategyProcessMatrix.query.filter(StrategyProcessMatrix.process_id.in_(surec_ids)).delete(synchronize_session=False)

        # 4) AnaStrateji / AltStrateji (KalDer)
        ana_ids = [a.id for a in AnaStrateji.query.filter_by(kurum_id=kurum_id).all()]
        if ana_ids:
            StrategyMapLink.query.filter(
                db.or_(
                    StrategyMapLink.source_id.in_(ana_ids),
                    StrategyMapLink.target_id.in_(ana_ids)
                )
            ).delete(synchronize_session=False)
            AltStrateji.query.filter(AltStrateji.ana_strateji_id.in_(ana_ids)).delete(synchronize_session=False)
            AnaStrateji.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)

        # 5) Süreç – junction tabloları (raw SQL ile)
        if surec_ids:
            db.session.execute(surec_uyeleri.delete().where(surec_uyeleri.c.surec_id.in_(surec_ids)))
            db.session.execute(surec_liderleri.delete().where(surec_liderleri.c.surec_id.in_(surec_ids)))
            db.session.execute(surec_alt_stratejiler.delete().where(surec_alt_stratejiler.c.surec_id.in_(surec_ids)))
            db.session.execute(process_owners.delete().where(process_owners.c.process_id.in_(surec_ids)))
        Surec.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)

        # 6) Diğer kurum verileri (KalDer)
        AnalysisItem.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
        TowsMatrix.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
        Deger.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
        EtikKural.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)
        KalitePolitikasi.query.filter_by(kurum_id=kurum_id).delete(synchronize_session=False)

        # 7) KalDerAdmin kullanıcıya ait kayıtlar
        if user_id:
            Notification.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            Feedback.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            UserActivityLog.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            Note.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            DashboardLayout.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            KullaniciYetki.query.filter_by(user_id=user_id).delete(synchronize_session=False)
            OzelYetki.query.filter(db.or_(OzelYetki.kullanici_id == user_id, OzelYetki.veren_kullanici_id == user_id)).delete(synchronize_session=False)
            User.query.filter_by(id=user_id).delete(synchronize_session=False)

        # 8) KalDer kurumu
        Kurum.query.filter_by(id=kurum_id).delete(synchronize_session=False)

        db.session.commit()
        print("Tamamlandı: KalDer kurumu, KalDerAdmin kullanıcısı ve ilgili tüm veriler silindi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
