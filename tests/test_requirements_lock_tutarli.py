# -*- coding: utf-8 -*-
"""requirements.lock ile requirements.txt ayrışmasın (Dockerfile kilidi kurar).

Her kök bağımlılık kilitte olmalı ve sabitlenen sürüm kökteki kısıtı sağlamalı; Dockerfile kilidi
kopyalamalı (yalnız requirements.txt'i değil). Kilit yenileme: python scripts/ops/kilit_uret.py
"""
import re
from pathlib import Path

from packaging.requirements import Requirement
from packaging.utils import canonicalize_name

KOK = Path(__file__).resolve().parent.parent


def _kokler():
    out = []
    for satir in (KOK / "requirements.txt").read_text("utf-8").splitlines():
        satir = satir.split("#")[0].strip()
        if satir and not satir.startswith(("-", "http")):
            out.append(Requirement(satir))
    return out


def _kilit():
    d = {}
    for satir in (KOK / "requirements.lock").read_text("utf-8").splitlines():
        satir = satir.strip()
        if satir and not satir.startswith("#"):
            ad, _, surum = satir.partition("==")
            d[canonicalize_name(ad)] = surum.strip()
    return d


def test_her_kok_bagimlilik_kilitte_ve_kisiti_saglar():
    kilit = _kilit()
    eksik, uyumsuz = [], []
    for r in _kokler():
        ad = canonicalize_name(r.name)
        if ad not in kilit:
            eksik.append(r.name)
        elif r.specifier and not r.specifier.contains(kilit[ad], prereleases=True):
            uyumsuz.append(f"{r.name}{r.specifier} ↔ kilit {kilit[ad]}")
    assert not eksik, f"kilitte yok (kilit_uret.py çalıştır): {eksik}"
    assert not uyumsuz, f"kilit kök kısıtı bozuyor: {uyumsuz}"


def test_test_gereksinimleri_kokle_celismez():
    """requirements-test.txt'teki sabitler requirements.txt ile aynı paketi farklı sürümde sabitlememeli."""
    kok = {canonicalize_name(r.name): r for r in _kokler() if str(r.specifier).startswith("==")}
    cakisan = []
    for satir in (KOK / "requirements-test.txt").read_text("utf-8").splitlines():
        satir = satir.split("#")[0].strip()
        if not satir or satir.startswith("-"):
            continue
        r = Requirement(satir)
        k = kok.get(canonicalize_name(r.name))
        if k and str(k.specifier) != str(r.specifier):
            cakisan.append(f"{r.name}: test {r.specifier} ↔ kök {k.specifier}")
    assert not cakisan, cakisan


def test_dockerfile_kilidi_kurar():
    d = (KOK / "Dockerfile").read_text("utf-8")
    assert re.search(r"COPY\s+requirements\.lock", d) and re.search(r"pip install[^\n]*-r requirements\.lock", d)
