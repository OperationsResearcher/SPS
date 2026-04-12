# -*- coding: utf-8 -*-
"""
KMF (varsayılan tenant 16) hibrit senkron:

1) VM'den tam tenant yedeği (gzip JSON) alınır; ``plan_years`` tablosu yükten çıkarılır.
2) Yerelde ``restore_tenant_data`` ile geri yüklenir — ``plan_years`` anahtarı olmadığı için
   mevcut yerel plan yılı satırları silinmez, diğer tablolar VM ile değiştirilir.
3) **Geri yüklemeden önce** yereldeki ``plan_years`` satırları okunur ve VM'e yazılır (ID çakışması konteyner betiğinde ele alınır).

Önkoşul: ``gcloud`` PATH'te; ``gcloud auth`` ve VM erişimi. Yerelde ``SQLALCHEMY_DATABASE_URI`` (PostgreSQL).

Kullanım (repo kökünden):
  py scripts/kmf_hybrid_sync.py
  py scripts/kmf_hybrid_sync.py --dry-run
  py scripts/kmf_hybrid_sync.py --skip-vm-push   # yalnızca VM -> yerel
"""
from __future__ import annotations

import argparse
import gzip
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _gcloud_executable() -> str | None:
    for name in ("gcloud", "gcloud.cmd", "gcloud.exe"):
        p = shutil.which(name)
        if p:
            return p
    for base in (
        Path(r"C:\Program Files (x86)\Google\Cloud SDK\google-cloud-sdk\bin"),
        Path(r"C:\Program Files\Google\Cloud SDK\google-cloud-sdk\bin"),
    ):
        for name in ("gcloud.cmd", "gcloud.exe"):
            cand = base / name
            if cand.is_file():
                return str(cand)
    return None


def _run(cmd: list[str], dry: bool) -> None:
    if dry:
        print("[dry-run]", " ".join(cmd))
        return
    subprocess.run(cmd, check=True)


def main() -> int:
    ap = argparse.ArgumentParser(description="KMF: VM verisi (plan_years hariç) -> yerel; plan_years -> VM")
    ap.add_argument("--tenant-id", type=int, default=16)
    ap.add_argument("--zone", default="europe-west3-c")
    ap.add_argument("--vm", default="sps-server-v2")
    ap.add_argument("--container", default="sps-web")
    ap.add_argument(
        "--workdir",
        type=Path,
        default=None,
        help="Ara dosyalar (varsayılan: backups/kmf_hybrid_sync)",
    )
    ap.add_argument("--skip-download", action="store_true", help="workdir içindeki .json.gz kullan")
    ap.add_argument("--skip-local-restore", action="store_true")
    ap.add_argument("--skip-vm-push", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    gcloud_bin = _gcloud_executable()
    need_gcloud = (not args.skip_download) or (
        not args.skip_local_restore and not args.skip_vm_push
    )
    if not args.dry_run and need_gcloud and not gcloud_bin:
        print("gcloud bulunamadi. Google Cloud SDK kurun veya PATH'e ekleyin.", file=sys.stderr)
        return 1

    tid = args.tenant_id
    workdir = args.workdir or (ROOT / "backups" / "kmf_hybrid_sync")
    workdir.mkdir(parents=True, exist_ok=True)
    gz_name = f"kmf_tenant_{tid}.json.gz"
    gz_local = workdir / gz_name
    export_helper = ROOT / "scripts" / "ops" / "vm_export_tenant_gzip.py"
    apply_helper = ROOT / "scripts" / "ops" / "vm_apply_plan_years.py"
    vm_host_gz = f"/tmp/{gz_name}"
    container_gz = f"/tmp/{gz_name}"

    if not args.skip_download:
        assert gcloud_bin is not None
        _run(
            [
                gcloud_bin,
                "compute",
                "scp",
                str(export_helper),
                f"{args.vm}:/tmp/vm_export_tenant_gzip.py",
                f"--zone={args.zone}",
            ],
            args.dry_run,
        )
        inner = (
            f"sudo docker cp /tmp/vm_export_tenant_gzip.py {args.container}:/tmp/ "
            f"&& sudo docker exec {args.container} bash -lc "
            f"'cd /app && python3 /tmp/vm_export_tenant_gzip.py {tid} {container_gz}' "
            f"&& sudo docker cp {args.container}:{container_gz} {vm_host_gz}"
        )
        _run(
            [gcloud_bin, "compute", "ssh", args.vm, f"--zone={args.zone}", "--command", inner],
            args.dry_run,
        )
        _run(
            [
                gcloud_bin,
                "compute",
                "scp",
                f"{args.vm}:{vm_host_gz}",
                str(gz_local),
                f"--zone={args.zone}",
            ],
            args.dry_run,
        )
    elif not gz_local.is_file():
        print(f"Eksik dosya: {gz_local} (--skip-download)", file=sys.stderr)
        return 1

    if args.dry_run:
        print("[dry-run] yerel restore ve VM push atlanmadi (sadece komutlar yukarida)")
        return 0

    raw = gz_local.read_bytes()
    payload = json.loads(gzip.decompress(raw).decode("utf-8"))
    tables = payload.setdefault("tables", {})
    # VM'deki plan_years geri yüklemeye dahil edilmez (anahtar tamamen kalkmalı).
    tables.pop("plan_years", None)

    if not args.skip_local_restore:
        from app import create_app
        from services.tenant_backup_service import (
            _coerce_row_bind_params,
            _serialize,
            restore_tenant_data,
        )
        from sqlalchemy import text

        from extensions import db

        app = create_app()
        with app.app_context():
            res = db.session.execute(
                text("SELECT * FROM plan_years WHERE tenant_id = :tid ORDER BY year"),
                {"tid": tid},
            )
            cols = list(res.keys())
            local_plan_rows = [
                {c: _serialize(val) for c, val in zip(cols, row)} for row in res.fetchall()
            ]
            if not local_plan_rows:
                fb = workdir / f"plan_years_from_vm_tenant_{tid}.json"
                if fb.is_file():
                    local_plan_rows = json.loads(fb.read_text(encoding="utf-8")).get("rows") or []
            (workdir / f"plan_years_tenant_{tid}_for_vm.json").write_text(
                json.dumps({"tenant_id": tid, "rows": local_plan_rows}, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

            out = restore_tenant_data(payload)
            # Tenant satiri silinip eklenince plan_years CASCADE ile silinir; snapshot'i geri yaz.
            if local_plan_rows:
                for r in sorted(local_plan_rows, key=lambda x: int(x["id"])):
                    ts = r.get("template_source_id")
                    bind = _coerce_row_bind_params(
                        {
                            "id": int(r["id"]),
                            "tenant_id": tid,
                            "year": int(r["year"]),
                            "name": r.get("name"),
                            "status": r.get("status") or "active",
                            "template_source_id": ts,
                            "created_at": r.get("created_at"),
                            "closed_at": r.get("closed_at"),
                        }
                    )
                    db.session.execute(
                        text(
                            "INSERT INTO plan_years "
                            '(id, tenant_id, year, name, status, template_source_id, created_at, closed_at) '
                            "VALUES (:id, :tenant_id, :year, :name, :status, :template_source_id, "
                            ":created_at, :closed_at) ON CONFLICT (id) DO NOTHING"
                        ),
                        bind,
                    )
                try:
                    db.session.execute(
                        text(
                            "SELECT setval(pg_get_serial_sequence('plan_years', 'id'), "
                            "(SELECT COALESCE(MAX(id), 1) FROM plan_years))"
                        )
                    )
                except Exception:
                    pass
                db.session.commit()
                (workdir / f"plan_years_tenant_{tid}_for_vm.json").write_text(
                    json.dumps({"tenant_id": tid, "rows": local_plan_rows}, ensure_ascii=False, indent=2),
                    encoding="utf-8",
                )

            (workdir / "local_restore_report.json").write_text(
                json.dumps(out, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print("Yerel restore:", json.dumps(out, ensure_ascii=False)[:2000])

    if not args.skip_local_restore and not args.skip_vm_push:
        rows_path_local = workdir / f"plan_years_only_tenant_{tid}.json"
        snap = json.loads((workdir / f"plan_years_tenant_{tid}_for_vm.json").read_text(encoding="utf-8"))
        local_plan_rows = snap.get("rows") or []
        rows_path_local.write_text(
            json.dumps({"tenant_id": tid, "rows": local_plan_rows}, ensure_ascii=False),
            encoding="utf-8",
        )
        vm_rows = f"/tmp/plan_years_only_tenant_{tid}.json"
        assert gcloud_bin is not None
        _run(
            [
                gcloud_bin,
                "compute",
                "scp",
                str(apply_helper),
                f"{args.vm}:/tmp/vm_apply_plan_years.py",
                f"--zone={args.zone}",
            ],
            False,
        )
        _run(
            [
                gcloud_bin,
                "compute",
                "scp",
                str(rows_path_local),
                f"{args.vm}:{vm_rows}",
                f"--zone={args.zone}",
            ],
            False,
        )
        inner2 = (
            f"sudo docker cp /tmp/vm_apply_plan_years.py {args.container}:/tmp/ "
            f"&& sudo docker cp {vm_rows} {args.container}:{vm_rows} "
            f"&& sudo docker exec {args.container} bash -lc "
            f"'cd /app && python3 /tmp/vm_apply_plan_years.py {vm_rows}'"
        )
        _run(
            [gcloud_bin, "compute", "ssh", args.vm, f"--zone={args.zone}", "--command", inner2],
            False,
        )
        if not local_plan_rows:
            print("UYARI: Yerel plan_years bos oldugu icin VM'e gonderilecek satir yoktu.", file=sys.stderr)
    elif args.skip_local_restore and not args.skip_vm_push:
        print(
            "VM push atlandi: --skip-local-restore ile plan_years anlik yedek alinmadi.",
            file=sys.stderr,
        )

    print("Tamam. Calisma dizini:", workdir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
