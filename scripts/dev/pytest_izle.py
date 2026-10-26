# -*- coding: utf-8 -*-
"""Pytest'i ilerleme göstergesi ve takılma bekçisiyle koşturur.

Kullanım (kök dizinden):
    python scripts/dev/pytest_izle.py                      # tüm testler, 4 işçi
    python scripts/dev/pytest_izle.py tests/test_x.py -k abc
    python scripts/dev/pytest_izle.py -n 8 --takilma 90    # 8 işçi, 90 sn sessizlikte uyar
    python scripts/dev/pytest_izle.py --oldur 300          # 300 sn hiç ilerleme yoksa durdur

Her ~10 sn'de tek satır durum yazar:  % · biten/toplam · geçen süre · tahmini kalan · son ilerleme · hata sayısı.
Hiçbir test sonucu --takilma sn boyunca gelmezse UYARI verir ve pytest'in son çıktı satırlarını gösterir.
--oldur verilirse o kadar sn ilerleme yoksa süreci durdurur.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import threading
import time

# xdist: "[gw0] [ 11%] PASSED yol::test"   ·   tek işlem: "yol::test PASSED [ 11%]"
_RES = r"(PASSED|FAILED|ERROR|SKIPPED|XFAIL|XPASS)"
RESULT_A = re.compile(r"^(?:\[gw\d+\]\s+)?(?:\[\s*\d+%\]\s+)?" + _RES + r"\s+(\S+::\S+)")
RESULT_B = re.compile(r"^(\S+::\S+)\s+" + _RES)
TOTAL = re.compile(r"(\d+) workers? \[(\d+) items?\]|collected (\d+) items?")


def fmt(sec: float) -> str:
    sec = int(max(sec, 0))
    return f"{sec // 60}:{sec % 60:02d}"


def main() -> int:
    ap = argparse.ArgumentParser(add_help=True, allow_abbrev=False)
    ap.add_argument("-n", default="4", help="işçi sayısı (varsayılan 4; 0 = tek işlem)")
    ap.add_argument("--takilma", type=int, default=120, help="bu kadar sn sonuç gelmezse UYARI")
    ap.add_argument("--oldur", type=int, default=0, help="bu kadar sn sonuç gelmezse süreci durdur (0 = kapalı)")
    args, rest = ap.parse_known_args()

    cmd = [sys.executable, "-u", "-m", "pytest", "-p", "no:cacheprovider", "-v", "--no-header", "-rf"]
    if args.n != "0":
        cmd += ["-n", args.n]
    cmd += rest or ["tests"]

    start = last = time.time()
    state = {"total": 0, "done": 0, "failed": 0, "last": time.time(), "warned": False, "tail": []}
    failures: list[str] = []
    lock = threading.Lock()

    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
                            encoding="utf-8", errors="replace", bufsize=1)

    def reader():
        for raw in proc.stdout:
            line = raw.rstrip("\n")
            m = TOTAL.search(line)
            with lock:
                if m and not state["total"]:
                    state["total"] = int(m.group(2) or m.group(3))
                ma, mb = RESULT_A.match(line), RESULT_B.match(line)
                r = (ma.group(2), ma.group(1)) if ma else ((mb.group(1), mb.group(2)) if mb else None)
                if r:
                    name, res = r
                    state["done"] += 1
                    state["last"] = time.time()
                    state["warned"] = False
                    if res in ("FAILED", "ERROR"):
                        state["failed"] += 1
                        failures.append(name)
                else:
                    state["tail"].append(line)
                    state["tail"] = state["tail"][-40:]

    t = threading.Thread(target=reader, daemon=True)
    t.start()

    try:
        while proc.poll() is None:
            time.sleep(10)
            with lock:
                done, total = state["done"], state["total"]
                el = time.time() - start
                since = time.time() - state["last"]
                pct = f"{100 * done // total:3d}%" if total else "  ?%"
                eta = fmt(el / done * (total - done)) if done and total else "?"
                print(f"[izle] {pct} · {done}/{total or '?'} test · geçen {fmt(el)} · tahmini kalan {eta} · "
                      f"son ilerleme {int(since)} sn önce · hata {state['failed']}", flush=True)
                if since >= args.takilma and not state["warned"]:
                    state["warned"] = True
                    print(f"[izle] UYARI: {int(since)} sn'dir sonuç gelmedi — yavaş/takılmış test olabilir "
                          f"(pytest.ini: test başına timeout 120 sn).", flush=True)
                    for ln in state["tail"][-6:]:
                        print("        ", ln[:160], flush=True)
                if args.oldur and since >= args.oldur:
                    print(f"[izle] {int(since)} sn ilerleme yok — süreç durduruluyor.", flush=True)
                    proc.kill()
                    break
    except KeyboardInterrupt:
        proc.kill()
        print("[izle] kesildi.")
        return 130

    t.join(timeout=5)
    el = time.time() - start
    print(f"[izle] BİTTİ · {state['done']}/{state['total'] or '?'} test · {fmt(el)} · hata {state['failed']} · çıkış kodu {proc.returncode}")
    for name in failures:
        print("   BAŞARISIZ:", name)
    return proc.returncode or 0


if __name__ == "__main__":
    raise SystemExit(main())
