# -*- coding: utf-8 -*-
"""pybasla.py — Yerel geliştirme sunucusunu TEMİZ başlat.

Sorun (memory: yerel 5001 stale süreç tuzağı): Ctrl+C Flask'i her zaman
öldürmez; debug reloader iki süreç açar; 5001'de eski kod dinlemeye devam
eder → yeni başlatınca çift dinleyici → eski koddan rastgele 500.

Bu script:
  1. 5001 portunu dinleyen TÜM süreçleri bulur ve öldürür (netstat + taskkill).
  2. app.py çalıştıran artık python süreçlerini de tarar (reloader child dahil).
  3. Port serbest kalana kadar bekler.
  4. .venv python'uyla tek temiz `app.py` başlatır (terminale bağlı).

Kullanım:
    python pybasla.py
veya .venv ile:
    .venv\\Scripts\\python.exe pybasla.py

Yalnızca YEREL (127.0.0.1:5001). Windows'a özgü (netstat/taskkill/wmic).
"""
import os
import subprocess
import sys
import time

PORT = 5001
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
APP_FILE = os.path.join(PROJECT_ROOT, "app.py")
VENV_PYTHON = os.path.join(PROJECT_ROOT, ".venv", "Scripts", "python.exe")


def say(msg):
    """Konsola güvenli yaz — cp1254'e sığmayan karakterde çökme (UnicodeEncodeError yerine)."""
    enc = getattr(sys.stdout, "encoding", None) or "utf-8"
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode(enc, errors="replace").decode(enc, errors="replace"))


def _run(cmd):
    """Komutu çalıştır, (stdout) döndür; hata olursa boş string."""
    try:
        out = subprocess.run(
            cmd, capture_output=True, text=True, shell=isinstance(cmd, str),
            timeout=15,
        )
        return out.stdout or ""
    except Exception:
        return ""


def pids_on_port(port):
    """netstat ile bu portu DİNLEYEN (local adres :port) PID'leri bul.

    Satır formatı: TCP  <local>  <remote>  <STATE>  <PID>
    Yalnızca local adresi ':port' ile biten LISTENING/ESTABLISHED satırlar.
    """
    pids = set()
    out = _run("netstat -ano")
    suffix = f":{port}"
    for line in out.splitlines():
        parts = line.split()
        # TCP/UDP satırı + en az 5 alan (UDP'de state olmayabilir)
        if len(parts) < 4 or parts[0].upper() not in ("TCP", "UDP"):
            continue
        local = parts[1]
        if not local.endswith(suffix):
            continue  # remote :port (giden bağlantı) — atla
        pid = parts[-1]
        if pid.isdigit() and pid != "0":
            pids.add(pid)
    return pids


def pids_running_app():
    """app.py çalıştıran python süreçlerini bul (reloader child dahil).

    wmic Windows 11'de kaldırıldı → PowerShell CIM kullanılır. Çıktıyı CSV
    (ProcessId,CommandLine) olarak alıp app.py geçenleri süzeriz.
    """
    pids = set()
    self_pid = str(os.getpid())
    ps_cmd = (
        "Get-CimInstance Win32_Process -Filter \"name='python.exe' or name='pythonw.exe'\" "
        "| ForEach-Object { \"$($_.ProcessId)`t$($_.CommandLine)\" }"
    )
    out = _run(["powershell", "-NoProfile", "-Command", ps_cmd])
    for line in out.splitlines():
        if "\t" not in line:
            continue
        pid, _, cmdline = line.partition("\t")
        low = cmdline.lower()
        if "app.py" not in low or "pybasla.py" in low:
            continue
        pid = pid.strip()
        if pid.isdigit() and pid != self_pid:
            pids.add(pid)
    return pids


def kill(pid):
    _run(f"taskkill /F /PID {pid} /T")


def main():
    say("[pybasla] 5001 portu temizleniyor...")

    targets = pids_on_port(PORT) | pids_running_app()
    self_pid = str(os.getpid())
    targets.discard(self_pid)

    if targets:
        for pid in sorted(targets):
            say(f"  [oldur] PID {pid}")
            kill(pid)
        # Port serbest kalsin
        for _ in range(20):  # en fazla ~10 sn
            time.sleep(0.5)
            if not pids_on_port(PORT):
                break
        kalan = pids_on_port(PORT)
        if kalan:
            say(f"  [uyari] hala dinleyen var: {kalan} - yine de baslatiliyor.")
        else:
            say("  [tamam] port serbest.")
    else:
        say("  [tamam] 5001'de calisan surec yok.")

    # Python yorumlayıcı: .venv varsa onu kullan
    python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else sys.executable
    say(f"[pybasla] baslatiliyor: app.py -> http://127.0.0.1:{PORT}")
    say("-" * 60)

    # Terminale bağlı çalıştır (loglar görünür, Ctrl+C ile durur)
    try:
        subprocess.run([python, APP_FILE], cwd=PROJECT_ROOT)
    except KeyboardInterrupt:
        say("\n[pybasla] durduruldu.")


if __name__ == "__main__":
    main()
