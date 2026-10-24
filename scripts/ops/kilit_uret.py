# -*- coding: utf-8 -*-
"""requirements.lock üretir: requirements.txt kökünden bağımlılık kapanımı, KURULU (test edilen) sürümlerle.

`pip-compile` "en son sürüm" çözer; burada amaç tersi: bu makinede testlerin geçtiği sürümleri dondurmak.
Kullanım: python scripts/ops/kilit_uret.py   (Yerel venv'de, testler yeşilken)
Kurulu olmayan kök paketler (örn. yedeği kodda olan pyotp) EKSIK listesinde uyarılır, kilide yazılmaz;
ELLE_SABIT'e sürümüyle eklenir.
"""
from __future__ import annotations

from importlib import metadata
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

KOK = Path(__file__).resolve().parents[2]
ELLE_SABIT = {"pyotp": "2.9.0"}  # Yerelde kurulu değil; kodda yedeği var, sunucuda kurulu olmalı.


def main() -> int:
    kokler = []
    for satir in (KOK / "requirements.txt").read_text("utf-8").splitlines():
        satir = satir.split("#")[0].strip()
        if not satir or satir.startswith(("-", "http")):
            continue
        kokler.append(canonicalize_name(Requirement(satir).name))
    dists = {canonicalize_name(d.metadata["Name"]): d for d in metadata.distributions()}
    gorulen: dict[str, str] = {}
    eksik: list[str] = []

    def yuru(ad: str) -> None:
        if ad in gorulen:
            return
        d = dists.get(ad)
        if d is None:
            eksik.append(ad)
            return
        gorulen[ad] = d.version
        for r in d.requires or []:
            try:
                req = Requirement(r)
            except Exception:
                continue
            if req.marker and not req.marker.evaluate({"extra": ""}):
                continue
            yuru(canonicalize_name(req.name))

    for k in kokler:
        yuru(k)
    for ad, surum in ELLE_SABIT.items():
        if ad in eksik:
            gorulen[ad] = surum
            eksik.remove(ad)
    out = KOK / "requirements.lock"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("# requirements.lock — requirements.txt kökünden bağımlılık kapanımı, TEST EDİLEN sürümlerle sabit.\n")
        f.write("# Kurulum: pip install -r requirements.lock | Yenileme: python scripts/ops/kilit_uret.py | Tarama: pip-audit -r requirements.lock\n")
        for ad in sorted(gorulen):
            f.write(f"{ad}=={gorulen[ad]}\n")
    print(f"kök {len(kokler)} · kilit {len(gorulen)} paket · kurulu olmayan: {eksik or 'yok'}")
    return 1 if eksik else 0


if __name__ == "__main__":
    raise SystemExit(main())
