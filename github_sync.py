"""
Kokpitim — GitHub Sync Script
Kullanim:
  Manuel   : python github_sync.py
  Otomatik : python github_sync.py "TASK-001: surec modulu tamamlandi"
"""

import subprocess
import sys
import os
import re
from datetime import datetime

# ============================================================
# AYARLAR — Bir kez yaz, bir daha dokunma
# ============================================================
PROJE_KLASORU = os.path.dirname(os.path.abspath(__file__))
REMOTE_URL = "https://github.com/OperationsResearcher/SPS.git"
GITHUB_KULLANICI = "OperationsResearcher"
REPO_ADI = "SPS"
VARSAYILAN_BRANCH = "main"
OTOMATIK_MOD = False
# ============================================================


def run(cmd, hata_kritik=True):
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=PROJE_KLASORU
    )
    if result.returncode != 0 and hata_kritik:
        print(f"\nHATA: {cmd}")
        print(result.stderr.strip())
        sys.exit(1)
    return result


def baslik(metin):
    print(f"\n{'=' * 60}")
    print(f"  {metin}")
    print(f"{'=' * 60}")


def adim(metin):
    print(f"\n-> {metin}...")


def kontrol_gitignore():
    gitignore_yolu = os.path.join(PROJE_KLASORU, ".gitignore")
    if not os.path.exists(gitignore_yolu):
        print("HATA: .gitignore bulunamadi!")
        sys.exit(1)
    with open(gitignore_yolu, "r", encoding="utf-8") as f:
        icerik = f.read()
    if ".env" not in icerik:
        print("UYARI: .env .gitignore icinde degil!")
        if OTOMATIK_MOD:
            print("Otomatik modda guvenlik riski nedeniyle iptal edildi.")
            sys.exit(1)
        onay = input("Yine de devam? (e/h): ").strip().lower()
        if onay != "e":
            sys.exit(0)
    else:
        print("OK: .env ignore'da, guvenli.")


def kontrol_env_staged():
    result = run("git status --short", hata_kritik=False)
    for satir in result.stdout.splitlines():
        if ".env" in satir and not satir.strip().startswith("?"):
            print("TEHLIKE: .env staged listesinde! Iptal ediliyor.")
            run("git rm -r --cached .", hata_kritik=False)
            sys.exit(1)


def git_kullanici_kontrol():
    email = run("git config user.email", hata_kritik=False).stdout.strip()
    name = run("git config user.name", hata_kritik=False).stdout.strip()
    if not email or not name:
        if OTOMATIK_MOD:
            print("HATA: Git kullanici bilgileri eksik!")
            print("  git config --global user.email 'email@adresin.com'")
            print("  git config --global user.name 'Adiniz'")
            sys.exit(1)
        email = input("GitHub email: ").strip()
        name = input("Adiniz Soyadiniz: ").strip()
        run(f'git config --global user.email "{email}"')
        run(f'git config --global user.name "{name}"')
        print("OK: Kullanici bilgileri kaydedildi.")
    else:
        print(f"OK: Git kullanici: {name} <{email}>")


def remote_ayarla():
    mevcut = run("git remote get-url origin", hata_kritik=False).stdout.strip()
    if mevcut == REMOTE_URL:
        print("OK: Remote dogru.")
    else:
        run("git remote remove origin", hata_kritik=False)
        run(f"git remote add origin {REMOTE_URL}")
        print(f"OK: Remote ayarlandi: {REMOTE_URL}")


def tasklog_latest_olustur():
    """docs/TASKLOG.md dosyasindan son 10 task blogunu üretip TASKLOG-latest.md'ye yazar."""
    tasklog_path = os.path.join(PROJE_KLASORU, "docs", "TASKLOG.md")
    latest_path = os.path.join(PROJE_KLASORU, "docs", "TASKLOG-latest.md")

    if not os.path.exists(tasklog_path):
        print("UYARI: docs/TASKLOG.md bulunamadi, TASKLOG-latest.md uretilemedi.")
        return

    with open(tasklog_path, "r", encoding="utf-8") as f:
        content = f.read()

    # "## TASK-" ile baslayan bloklari ayikla
    starts = list(re.finditer(r"^## TASK-", content, flags=re.MULTILINE))
    blocks = []
    for i, match in enumerate(starts):
        start = match.start()
        end = starts[i + 1].start() if i + 1 < len(starts) else len(content)
        blocks.append(content[start:end].strip())

    # TASKLOG en yeni üstte tutuldugu icin "son 10" burada ilk 10 bloktur
    latest_blocks = blocks[:10]

    output = "# TASKLOG — Son 10 Task\n"
    if latest_blocks:
        output += "\n\n".join(latest_blocks).rstrip() + "\n"
    else:
        output += "\n"

    # UTF-8, BOM'suz yazim
    with open(latest_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(output)

    print("OK: docs/TASKLOG-latest.md guncellendi.")


def main():
    global OTOMATIK_MOD
    os.chdir(PROJE_KLASORU)

    if len(sys.argv) > 1:
        OTOMATIK_MOD = True
        commit_msg = " ".join(sys.argv[1:])
        baslik("Kokpitim — Otomatik GitHub Push")
        print(f"  Commit : {commit_msg}")
        print(f"  Zaman  : {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    else:
        OTOMATIK_MOD = False
        baslik("Kokpitim — GitHub Sync (Manuel)")
        print(f"  Repo  : {REMOTE_URL}")
        print(f"  Zaman : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    print()
    kontrol_gitignore()
    git_kullanici_kontrol()
    tasklog_latest_olustur()

    if not OTOMATIK_MOD:
        print()
        commit_msg = input("Commit mesaji (bos birak = otomatik): ").strip()
        if not commit_msg:
            commit_msg = f"sync: manuel guncelleme — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    adim("Degisiklikler kontrol ediliyor")
    result = run("git status --short", hata_kritik=False)
    if not result.stdout.strip():
        print("Degisiklik yok, push atlanacak.")
        sonuc_yazdir()
        return
    print(result.stdout.strip())

    adim("Dosyalar ekleniyor")
    # 1) Önce TASKLOG-latest dosyasını açıkça stage et
    run('git add "docs/TASKLOG-latest.md"', hata_kritik=False)
    latest_stage = run('git status --short -- "docs/TASKLOG-latest.md"', hata_kritik=False).stdout.strip()
    if latest_stage:
        print(f"OK: TASKLOG-latest stage durumu: {latest_stage}")
    else:
        print("OK: TASKLOG-latest stage edildi (ayri degisiklik yok).")

    # 2) Sonra kalan tüm dosyaları stage et
    run("git add .")
    kontrol_env_staged()
    print("OK: Dosyalar eklendi.")

    adim("Commit yapiliyor")
    result = run(f'git commit -m "{commit_msg}"', hata_kritik=False)
    if result.returncode != 0:
        print("Commit edilecek degisiklik yok.")
    else:
        print(f"OK: Commit: {commit_msg}")

    adim("Remote kontrol ediliyor")
    remote_ayarla()

    adim("GitHub'dan son hal cekiliyor")
    run(f"git pull origin {VARSAYILAN_BRANCH} --no-edit", hata_kritik=False)
    print("OK: Pull tamamlandi.")

    adim("GitHub'a push ediliyor")
    result = run(f"git push -u origin {VARSAYILAN_BRANCH}", hata_kritik=False)
    if result.returncode != 0:
        print(f"HATA: Push basarisiz!\n{result.stderr.strip()}")
        sys.exit(1)
    print("OK: Push tamamlandi!")

    sonuc_yazdir(commit_msg)


def sonuc_yazdir(commit_msg=""):
    baslik("TAMAMLANDI!")
    print(f"  Repo  : https://github.com/{GITHUB_KULLANICI}/{REPO_ADI}")
    if commit_msg:
        print(f"  Commit: {commit_msg}")
    print()
    print("  TASKLOG raw link:")
    print(f"  https://raw.githubusercontent.com/{GITHUB_KULLANICI}/{REPO_ADI}/main/docs/TASKLOG.md")
    print()


if __name__ == "__main__":
    main()
