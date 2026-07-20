"""Yıl bazlı Faz 1.2 — yılsız kayıtları ilk yıla bağla + clone zinciri üret.

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.2 · SORULAR.md T2, T9, S11
         + kullanıcı kararı K13 (2026-07-20)

  K13 — KMF gibi tamamen yılsız kurumlar: mevcut kayıtlar kurumun İLK plan
        yılına bağlanır, sonra clone_full_plan_year ile sonraki yıllar
        zincirleme üretilir. Tomofil'deki (düzgün clone edilmiş kurum) yapının
        aynısı elde edilir.

NEDEN BÖYLE (ölçüm 2026-07-20):
    Tomofil #27  → her yılda kendi süreç/PG kopyası var (2020-2026, ~10 süreç
                   31 PG/yıl). T9 hedefi ZATEN karşılanıyor, dokunulmaz.
    KMF #16      → 11 süreç + 146 PG TAMAMEN YILSIZ; 7 plan yılı boş.
                   Ama kpi_data'sı 2020-2026'ya yayılmış.
    Default #1   → 2 süreç + 42 PG yılsız; 2021-2026 zinciri Faz 1.3'te üretildi.

    Yılsız kayıtları tek bir yıla bağlayıp bırakmak T2'yi ("yıl devrinde her şey
    kopyalanır") ihlal ederdi: kurum 2025'e veri girmek istediğinde PG kopyası
    olmazdı. Bu yüzden bağlama + zincirleme klonlama birlikte yapılır.

ÖNEMLİ — bu script IDEMPOTENT DEĞİL sayılmalı:
    clone_full_plan_year hedef yılda kayıt varsa onu ÇOĞALTIR (unique kısıt yok).
    Bu yüzden her yıl için "zaten klonlanmış mı" kontrolü yapılır ve dolu yıl
    ATLANIR. Yine de tekrar çalıştırmadan önce kontrol modunda bakın.

KULLANIM:
    python scripts/ops/yilbazli_faz1_2_clone_zinciri.py            # KONTROL
    python scripts/ops/yilbazli_faz1_2_clone_zinciri.py --calistir # uygula
"""
from __future__ import annotations

import argparse
import sys

sys.path.insert(0, ".")

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from app import create_app  # noqa: E402
from extensions import db  # noqa: E402
from sqlalchemy import text  # noqa: E402


# Yılsız kaydı ilk plan yılına bağlarken kullanılacak tablolar.
# (tablo, tenant'a ulaşan WHERE parçası)
BAGLANACAK = [
    ("processes", "tenant_id = :t"),
    ("strategies", "tenant_id = :t"),
    ("process_kpis",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :t)"),
    ("sub_strategies",
     "strategy_id IN (SELECT id FROM strategies WHERE tenant_id = :t)"),
    ("process_activities",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :t)"),
    ("process_sub_strategy_links",
     "process_id IN (SELECT id FROM processes WHERE tenant_id = :t)"),
]


def _c():
    """Taze bağlantı.

    clone_full_plan_year sonunda db.session.commit() yapıyor
    (plan_year_service.py:891). Commit, tutulan Connection nesnesini KAPATIR
    -> "This Connection is closed". Bu yüzden bağlantı saklanmaz, her sorguda
    session'dan yeniden alınır. Servis değiştirilmedi: onu çağıran başka
    yerler var (sihirbaz, yıl devri) ve commit davranışı onlar için doğru.
    """
    return db.session.connection()


def _ilk_plan_yili(tenant_id: int):
    return _c().execute(text("""
        SELECT id, year FROM plan_years
         WHERE tenant_id = :t ORDER BY year ASC LIMIT 1
    """), {"t": tenant_id}).first()


def _yil_dolu_mu(tenant_id: int, py_id: int) -> tuple[int, int]:
    """(süreç, PG) sayısı — clone gerekip gerekmediğini belirler.

    DOLULUK ÖLÇÜTÜ = SÜREÇ SAYISI (PG değil). Ölçüm (2026-07-20): KMF'de 2020'ye
    3, 2025'e 2 PG bağlıydı ama SÜREÇ sıfırdı — önceki kısmi clone denemesinin
    kalıntısı. PG'ye bakan bir ölçüt bu yılları "dolu" sayıp atlar, zincir kırılır
    ve 2020 kaynak alınınca boş klon üretilirdi.
    """
    surec = _c().execute(text("""
        SELECT COUNT(*) FROM processes WHERE tenant_id = :t AND plan_year_id = :p
    """), {"t": tenant_id, "p": py_id}).scalar()
    pg = _c().execute(text("""
        SELECT COUNT(*) FROM process_kpis pk
          JOIN processes p ON p.id = pk.process_id
         WHERE p.tenant_id = :t AND pk.plan_year_id = :p
    """), {"t": tenant_id, "p": py_id}).scalar()
    return surec, pg


def rapor_ve_uygula(calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        from app.services.plan_year_service import clone_full_plan_year
        from app.models.plan_year import PlanYear

        mod = "UYGULAMA" if calistir else "KONTROL"
        print(f"\n{'='*72}\n  FAZ 1.2 — CLONE ZİNCİRİ  [{mod} MODU]\n{'='*72}\n")

        tenants = _c().execute(text(
            "SELECT id, name FROM tenants WHERE is_active ORDER BY id")).fetchall()

        for tid, tname in tenants:
            ilk = _ilk_plan_yili(tid)
            if not ilk:
                continue
            ilk_py_id, ilk_yil = ilk

            # Bu kurumda yılsız kayıt var mı?
            yilsiz = {}
            for tab, where in BAGLANACAK:
                n = _c().execute(text(
                    f"SELECT COUNT(*) FROM {tab} WHERE plan_year_id IS NULL AND {where}"
                ), {"t": tid}).scalar()
                if n:
                    yilsiz[tab] = n

            yillar = _c().execute(text("""
                SELECT id, year FROM plan_years WHERE tenant_id = :t ORDER BY year
            """), {"t": tid}).fetchall()
            # Doluluk = süreç sayısı (bkz. _yil_dolu_mu docstring'i)
            bos_yillar = [(pid, yr) for pid, yr in yillar
                          if _yil_dolu_mu(tid, pid)[0] == 0]

            if not yilsiz and not bos_yillar:
                continue

            ad = (tname or "")[:26]
            print(f"── tenant {tid:>3} {ad}  (ilk yıl {ilk_yil})")

            # ── 1) Yılsız kayıtları ilk yıla bağla ──────────────────────
            if yilsiz:
                print(f"   1) yılsız kayıtlar -> {ilk_yil}:")
                for tab, n in yilsiz.items():
                    print(f"      {tab:30} {n:>4} satır")
                    if calistir:
                        where = dict(BAGLANACAK)[tab]
                        _c().execute(text(f"""
                            UPDATE {tab} SET plan_year_id = :p
                             WHERE plan_year_id IS NULL AND {where}
                        """), {"t": tid, "p": ilk_py_id})
            else:
                print(f"   1) yılsız kayıt yok")

            # ── 2) Boş yılları zincirleme klonla (T2) ───────────────────
            # İleri VE geri: zincir normalde ileriye akar (2020→2021→…), ama
            # kurumun ilk plan yılı boş, sonraki yılı dolu olabilir.
            # Ölçüm (2026-07-20): Eskişehir #28 — 2025 boş ama 204 satır verisi
            # var; yapı 2026'da. K11 ile 2025 üretilmişti. Sadece ileri
            # klonlanırsa 2025 boş kalır ve o verinin bağlanacağı PG kopyası
            # hiç doğmaz (T12 remap'te açıkta kalırdı).
            hedef = list(bos_yillar)
            if hedef:
                print(f"   2) boş yıllar klonlanacak: "
                      f"{', '.join(str(y) for _, y in hedef)}")
                if calistir:
                    db.session.flush()
                    # Zincir sırayla ilerler: her adım bir öncekinin ÇIKTISINI
                    # kaynak alır, bu yüzden kaynak her turda TAZE okunur.
                    for py_id, yr in sorted(hedef, key=lambda x: x[1]):
                        # Kaynak: önce bir ÖNCEKİ dolu yıl (normal zincir, T2).
                        # Yoksa en yakın SONRAKİ dolu yıl (geriye klonlama —
                        # yukarıdaki Eskişehir durumu).
                        onceki = _c().execute(text("""
                            SELECT py.id, py.year FROM plan_years py
                             WHERE py.tenant_id = :t AND py.year < :y
                               AND EXISTS (SELECT 1 FROM processes p
                                            WHERE p.plan_year_id = py.id)
                             ORDER BY py.year DESC LIMIT 1
                        """), {"t": tid, "y": yr}).first()
                        if not onceki:
                            onceki = _c().execute(text("""
                                SELECT py.id, py.year FROM plan_years py
                                 WHERE py.tenant_id = :t AND py.year > :y
                                   AND EXISTS (SELECT 1 FROM processes p
                                                WHERE p.plan_year_id = py.id)
                                 ORDER BY py.year ASC LIMIT 1
                            """), {"t": tid, "y": yr}).first()
                        if not onceki:
                            print(f"      {yr}: dolu kaynak yıl yok, atlandı")
                            continue
                        src_id, src_yil = onceki
                        s, p = _yil_dolu_mu(tid, src_id)
                        if s == 0:
                            print(f"      {yr}: kaynak {src_yil} boş, atlandı")
                            continue
                        # Hedef PlanYear kaydı ZATEN VAR (Faz 1.3'te üretildi).
                        # SİLİP yeniden yaratmak ona bağlı satırları yetim
                        # bırakırdı (ölçüm: KMF'de 13 individual_performance_
                        # indicators). into_existing ile mevcut kayda klonlanır.
                        src = db.session.get(PlanYear, src_id)
                        hedef_py = db.session.get(PlanYear, py_id)
                        yeni = clone_full_plan_year(
                            src, yr, into_existing=hedef_py
                        )
                        db.session.flush()
                        s2, p2 = _yil_dolu_mu(tid, yeni.id)
                        yon = "geriye" if src_yil > yr else "ileriye"
                        print(f"      {yr}: {src_yil}'den klonlandı ({yon}) -> "
                              f"{s2} süreç, {p2} PG")
            else:
                print(f"   2) klonlanacak boş yıl yok")
            print()

        if calistir:
            db.session.commit()
            print(f"{'='*72}\n  [OK] FAZ 1.2 UYGULANDI\n{'='*72}\n")
        else:
            db.session.rollback()
            print(f"{'='*72}\n  KONTROL MODU — hiçbir şey yazılmadı."
                  f"\n  Uygulamak için: --calistir\n{'='*72}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.2 — clone zinciri")
    ap.add_argument("--calistir", action="store_true")
    args = ap.parse_args()
    sys.exit(rapor_ve_uygula(args.calistir))
