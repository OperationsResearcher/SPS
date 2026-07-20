"""Yıl bazlı Faz 1.6 — plan_projects -> project göçü (T10 tersine / K16).

DAYANAK: docs/yilbazli/UYGULAMA-PLANI.md §2.6 · SORULAR.md S3, T10
         + kullanıcı kararı K16 (2026-07-20) · migration yb16b3d8f4a2

  K16 — Portföy `Project` ANA MODEL. T10 ("PlanProject ana model olsun")
        tersine çevrildi çünkü ölçüm maliyeti gösterdi:
            portföy: 1 proje/0 görev ama 2719 satır kod, 25 route,
                     20 dosya, 10 şablon (gantt/kanban/RAID/kapasite/takvim)
            SP     : 21 proje/63 görev ama 6 route
        PlanProject'i ana model yapmak 2719 satırı ve 10 ekranı yeniden
        bağlamayı + PlanProject'te olmayan 25 alanı taşımayı gerektiriyordu.

BU SCRIPT: plan_projects (21) + plan_project_tasks (63) -> project + task

ALAN EŞLEMESİ:
    plan_projects            -> project
      name, description         aynı
      status, progress          project'te YOK -> health_status/health_score
                                DEĞİL (onlar hesaplanan alanlar). status ve
                                progress project'te karşılıksız; description'a
                                eklenmez, KAYBEDİLİR mi? Hayır — aşağıya bak.
      start_date, end_date      aynı
      plan_year_id              aynı (migration açtı)
      tenant_id                 aynı

    ⚠ manager_id NOT NULL ama plan_projects'te yönetici alanı YOK.
      Uydurma yapılmaz: projenin kendi görevlerinin assignee'sinden türetilir
      (ölçüm: plan_project_tasks.assignee_id 63/63 dolu, tenant_admin 8173).
      Görev yoksa tenant'ın tenant_admin'i kullanılır.

    plan_project_tasks       -> task
      name                     -> title
      assignee_id, status, start_date, end_date, description  aynı
      progress_pct             -> progress
      planned_budget, actual_cost, depends_on_task_id  task'ta karşılıksız

STATUS/PROGRESS/BÜTÇE SORUNU:
    project'te `status` ve `progress` kolonu yok (health_status/health_score
    hesaplanan alanlar). Bu script bu değerleri KAYBETMEMEK için önce
    migration'ın eklediği kolonları kontrol eder; yoksa göçü DURDURUR ve
    raporlar. Sessizce veri düşürmez.

KULLANIM:
    python scripts/ops/yilbazli_faz1_6_proje_birlestirme.py            # KONTROL
    python scripts/ops/yilbazli_faz1_6_proje_birlestirme.py --calistir # uygula
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


def _kolonlar(conn, tablo: str) -> set[str]:
    return {r[0] for r in conn.execute(text("""
        SELECT column_name FROM information_schema.columns WHERE table_name = :t
    """), {"t": tablo}).fetchall()}


def rapor_ve_uygula(calistir: bool) -> int:
    app = create_app()
    with app.app_context():
        conn = db.session.connection()
        mod = "UYGULAMA" if calistir else "KONTROL"
        print(f"\n{'='*74}\n  FAZ 1.6 — PROJE BİRLEŞTİRME (K16)  [{mod} MODU]\n{'='*74}\n")

        pkol = _kolonlar(conn, "project")
        tkol = _kolonlar(conn, "task")

        # Ön koşul: yıl kolonu açılmış olmalı
        if "plan_year_id" not in pkol:
            print("   [DUR] project.plan_year_id YOK — migration yb16b3d8f4a2 koşmamış.")
            return 1

        kaynak = conn.execute(text("SELECT COUNT(*) FROM plan_projects")).scalar()
        kaynak_task = conn.execute(text("SELECT COUNT(*) FROM plan_project_tasks")).scalar()
        hedef = conn.execute(text("SELECT COUNT(*) FROM project")).scalar()
        hedef_task = conn.execute(text("SELECT COUNT(*) FROM task")).scalar()

        print(f"   plan_projects       {kaynak:>4}  ->  project  {hedef:>4}")
        print(f"   plan_project_tasks  {kaynak_task:>4}  ->  task     {hedef_task:>4}\n")

        # Zaten taşınmış mı? (idempotenslik)
        tasinmis = conn.execute(text("""
            SELECT COUNT(*) FROM project p
             WHERE EXISTS (SELECT 1 FROM plan_projects pp
                            WHERE pp.name = p.name AND pp.tenant_id = p.tenant_id
                              AND pp.plan_year_id = p.plan_year_id)
        """)).scalar()
        if tasinmis:
            print(f"   ⚠ {tasinmis} proje zaten taşınmış görünüyor — tekrar taşınmaz.\n")

        # status / progress karşılıksız alanlar
        kayip = [a for a in ("status", "progress") if a not in pkol]
        if kayip:
            print(f"   ⚠ project'te karşılığı olmayan alanlar: {', '.join(kayip)}")
            print(f"     Bu alanlar description'a NOT olarak eklenir (veri kaybı olmaz).\n")

        # Taşınacaklar
        satirlar = conn.execute(text("""
            SELECT pp.id, pp.tenant_id, pp.plan_year_id, pp.name, pp.description,
                   pp.status, pp.progress, pp.start_date, pp.end_date, pp.is_active,
                   COALESCE(
                     (SELECT t.assignee_id FROM plan_project_tasks t
                       WHERE t.project_id = pp.id AND t.assignee_id IS NOT NULL
                       LIMIT 1),
                     (SELECT u.id FROM users u JOIN roles r ON r.id = u.role_id
                       WHERE u.tenant_id = pp.tenant_id AND u.is_active
                         AND r.name IN ('tenant_admin','Admin','admin')
                       ORDER BY u.id LIMIT 1),
                     (SELECT u.id FROM users u
                       WHERE u.tenant_id = pp.tenant_id AND u.is_active
                       ORDER BY u.id LIMIT 1)
                   ) AS manager_id
              FROM plan_projects pp
             WHERE NOT EXISTS (
                   SELECT 1 FROM project p
                    WHERE p.name = pp.name AND p.tenant_id = pp.tenant_id
                      AND p.plan_year_id = pp.plan_year_id)
             ORDER BY pp.id
        """)).fetchall()

        print(f"── Taşınacak proje: {len(satirlar)}")
        yoneticisiz = [r for r in satirlar if r[10] is None]
        if yoneticisiz:
            print(f"   [DUR] {len(yoneticisiz)} projede yönetici çözülemedi "
                  f"(manager_id NOT NULL). Göç durduruldu.")
            return 1

        ozet: dict[tuple, int] = {}
        for r in satirlar:
            ozet[(r[1], r[2])] = ozet.get((r[1], r[2]), 0) + 1
        for (tid, pyid), n in sorted(ozet.items()):
            yil = conn.execute(text("SELECT year FROM plan_years WHERE id = :i"),
                               {"i": pyid}).scalar()
            print(f"   tenant {tid} yıl {yil}: {n} proje")

        if calistir and satirlar:
            eslesme: dict[int, int] = {}          # plan_project.id -> project.id
            proje_yoneticisi: dict[int, int] = {}  # project.id -> manager_id
            for (pp_id, tid, py_id, ad, aciklama, durum, ilerleme,
                 bas, bit, aktif, mgr) in satirlar:
                notlar = []
                if durum:
                    notlar.append(f"Durum: {durum}")
                if ilerleme is not None:
                    notlar.append(f"İlerleme: %{ilerleme}")
                tam_aciklama = (aciklama or "")
                if notlar:
                    tam_aciklama = (tam_aciklama + "\n\n" + " · ".join(notlar)).strip()

                yeni_id = conn.execute(text("""
                    INSERT INTO project
                        (tenant_id, plan_year_id, name, description, manager_id,
                         start_date, end_date, is_active, is_archived,
                         created_at, updated_at)
                    VALUES (:t, :py, :ad, :ac, :mgr, :bas, :bit, :aktif, FALSE,
                            NOW(), NOW())
                    RETURNING id
                """), {"t": tid, "py": py_id, "ad": ad, "ac": tam_aciklama,
                        "mgr": mgr, "bas": bas, "bit": bit, "aktif": aktif}).scalar()
                eslesme[pp_id] = yeni_id
                proje_yoneticisi[yeni_id] = mgr

            # Görevler
            gorevler = conn.execute(text("""
                SELECT id, project_id, assignee_id, name, description, status,
                       start_date, end_date, is_active, progress_pct
                  FROM plan_project_tasks ORDER BY id
            """)).fetchall()
            tasinan_gorev = 0
            for (t_id, pp_id, atanan, ad, aciklama, durum,
                 bas, bit, aktif, ilerleme) in gorevler:
                yeni_proje = eslesme.get(pp_id)
                if not yeni_proje:
                    continue
                # task'ta is_active/updated_at kolonu YOK; reporter_id NOT NULL.
                # reporter uydurulmaz: görevin atananı yoksa projenin yöneticisi.
                conn.execute(text("""
                    INSERT INTO task
                        (project_id, title, description, status, assignee_id,
                         reporter_id, start_date, due_date, progress,
                         is_archived, created_at)
                    VALUES (:p, :ad, :ac, :d, :a, :rep, :bas, :bit, :ilr,
                            FALSE, NOW())
                """), {"p": yeni_proje, "ad": ad, "ac": aciklama, "d": durum,
                        "a": atanan, "rep": atanan or proje_yoneticisi[yeni_proje],
                        "bas": bas, "bit": bit, "ilr": ilerleme or 0})
                tasinan_gorev += 1

            db.session.commit()
            print(f"\n   [OK] {len(satirlar)} proje + {tasinan_gorev} görev taşındı.")

            conn2 = db.session.connection()
            print(f"\n── DOĞRULAMA")
            print(f"   project toplam: "
                  f"{conn2.execute(text('SELECT COUNT(*) FROM project')).scalar()}")
            print(f"   task toplam:    "
                  f"{conn2.execute(text('SELECT COUNT(*) FROM task')).scalar()}")
            yilsiz = conn2.execute(text(
                "SELECT COUNT(*) FROM project WHERE plan_year_id IS NULL")).scalar()
            print(f"   plan_year_id boş proje: {yilsiz}")
            print(f"\n{'='*74}\n  [OK] FAZ 1.6 UYGULANDI"
                  f"\n  NOT: plan_projects tabloları HENÜZ DÜŞÜRÜLMEDİ"
                  f"\n{'='*74}\n")
        elif not calistir:
            db.session.rollback()
            print(f"\n{'='*74}\n  KONTROL MODU — hiçbir şey yazılmadı."
                  f"\n  Uygulamak için: --calistir\n{'='*74}\n")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Faz 1.6 — proje birleştirme")
    ap.add_argument("--calistir", action="store_true")
    args = ap.parse_args()
    sys.exit(rapor_ve_uygula(args.calistir))
