# -*- coding: utf-8 -*-
"""
Yerel DB ile VM (sps-web) KMF tenant sayimlarini karsilastirir; Markdown rapor yazar.

  py scripts/kmf_compare_local_vm.py
  py scripts/kmf_compare_local_vm.py --out backups/kmf_hybrid_sync/kmf_compare.md
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROWS = [
    ("kullanici", "Kullanici"),
    ("surec", "Surec"),
    ("pg", "PG (process_kpis)"),
    ("pgv", "PGV (kpi_data, silinmemis)"),
    ("plan_years", "plan_years"),
    ("strateji", "Strateji"),
    ("alt_strateji", "Alt strateji"),
]


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


def _local_counts(tid: int) -> dict:
    cmd = [sys.executable, str(ROOT / "scripts" / "kmf_task084_counts.py"), str(tid)]
    p = subprocess.run(cmd, capture_output=True, text=True, check=True, cwd=str(ROOT))
    return json.loads(p.stdout.strip())


def _vm_counts(tid: int, vm: str, zone: str, container: str) -> dict:
    g = _gcloud_executable()
    if not g:
        raise FileNotFoundError("gcloud bulunamadi")
    helper = ROOT / "scripts" / "kmf_task084_counts.py"
    vm_path = "/tmp/kmf_task084_counts.py"
    subprocess.run(
        [g, "compute", "scp", str(helper), f"{vm}:{vm_path}", f"--zone={zone}"],
        check=True,
    )
    inner = (
        f"sudo docker cp {vm_path} {container}:{vm_path} "
        f"&& sudo docker exec {container} bash -lc "
        f"'cd /app && python3 {vm_path} {tid}'"
    )
    p = subprocess.run(
        [g, "compute", "ssh", vm, f"--zone={zone}", "--command", inner],
        capture_output=True,
        text=True,
        check=True,
    )
    out = p.stdout.strip()
    if not out:
        raise RuntimeError(f"VM stdout bos: stderr={p.stderr!r}")
    return json.loads(out)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tenant-id", type=int, default=16)
    ap.add_argument("--vm", default="sps-server-v2")
    ap.add_argument("--zone", default="europe-west3-c")
    ap.add_argument("--container", default="sps-web")
    ap.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Markdown cikti (varsayılan: backups/kmf_hybrid_sync/kmf_compare_<utc>.md)",
    )
    args = ap.parse_args()
    tid = args.tenant_id

    loc = _local_counts(tid)
    vm = _vm_counts(tid, args.vm, args.zone, args.container)

    lines = [
        "# KMF veri karsilastirma (tenant "
        f"{tid}: {loc.get('tenant') and loc['tenant'].get('name', '')})",
        "",
        f"- Olusturulma (UTC): `{datetime.now(timezone.utc).isoformat()}`",
        f"- Yerel: uygulama `SQLALCHEMY_DATABASE_URI`",
        f"- VM: `{args.container}` @ `{args.vm}`",
        "",
        "| Metrik | Yerel | VM | Esit |",
        "| --- | ---: | ---: | :---: |",
    ]
    for key, label in ROWS:
        a = loc.get(key)
        b = vm.get(key)
        eq = "evet" if a == b else "**HAYIR**"
        lines.append(f"| {label} | {a} | {b} | {eq} |")

    lines.extend(
        [
            "",
            "## Ham JSON",
            "",
            "### Yerel",
            "",
            "```json",
            json.dumps(loc, ensure_ascii=False, indent=2),
            "```",
            "",
            "### VM",
            "",
            "```json",
            json.dumps(vm, ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )
    md = "\n".join(lines)
    outp = args.out or (
        ROOT
        / "backups"
        / "kmf_hybrid_sync"
        / f"kmf_compare_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.md"
    )
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(md, encoding="utf-8")
    print(md)
    print("\n---\nRapor:", outp.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
