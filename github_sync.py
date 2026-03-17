"""
Kokpitim — GitHub Sync Script
Kullanim: python github_sync.py
Kiro terminalinden veya direkt calistir.
"""

import subprocess
import sys
import os
from datetime import datetime

# ============================================================
# AYARLAR — Bir kez yaz, bir daha dokunma
# ============================================================
PROJE_KLASORU = os.path.dirname(os.path.abspath(__file__))  # Scriptin oldugu klasor
REMOTE_URL = "https://github.com/OperationsResearcher/SPS.git"
GITHUB_KULLANICI = "OperationsResearcher"
REPO_ADI = "SPS"
VARSAYILAN_BRANCH = "main"
# ============================================================


def run(cmd, hata_kritik=True):
    """Komutu calistir, sonucu don."""
    result = subprocess.run(
        cmd, shell=True, capture_output=True, text=True, cwd=PROJE_KLASORU
    )
    if result.returncode != 0 and hata_kritik:
        print(f"\n❌ HATA: {cmd}")
        print(result.stderr.strip())
        sys.exit(1)
    return result


def baslik(metin):
    print(f"\n{'=' * 60}")
    print(f"  {metin}")
    print(f"{'=' * 60}")


def adim(no, toplam, metin):
    print(f"\n[{no}/{toplam}] {metin}...")


def kontrol_gitignore():
    """gitignore var mi ve .env icinde mi?"""
    gitignore_yolu = os.path.join(PROJE_KLASORU, ".gitignore")
    if not os.path.exists(gitignore_yolu):
        print("❌ .gitignore bulunamadi!")
        print("   Lutfen once .gitignore dosyasini proje klasorune koy.")
        sys.exit(1)
    print("✅ .gitignore mevcut.")

    with open(gitignore_yolu, "r", encoding="utf-8", errors="replace") as f:
        icerik = f.read()
    if ".env" not in icerik:
        print("⚠️  UYARI: .env .gitignore icinde gorunmuyor!")
        onay = input("   Yine de devam etmek istiyor musun? (e/h): ").strip().lower()
        if onay != "e":
            print("İptal edildi.")
            sys.exit(0)
    else:
        print("✅ .env ignore'da, guvenli.")


def kontrol_env_staged():
    """Staged dosyalarda .env var mi?"""
    result = run("git status --short", hata_kritik=False)
    if ".env" in result.stdout:
        print("\n🚨 TEHLİKE: .env dosyasi commit listesinde!")
        print("   Sifreleriniz aciga cikabilir. Iptal ediliyor.")
        run("git rm -r --cached .", hata_kritik=False)
        sys.exit(1)
    print("✅ .env staged degil, guvenli.")


def git_kullanici_kontrol():
    """Git kullanici bilgileri ayarli mi?"""
    email = run("git config user.email", hata_kritik=False).stdout.strip()
    name = run("git config user.name", hata_kritik=False).stdout.strip()

    if not email or not name:
        print("⚠️  Git kullanici bilgileri eksik.")
        email = input("   GitHub email adresin: ").strip()
        name = input("   Adiniz Soyadiniz: ").strip()
        run(f'git config --global user.email "{email}"')
        run(f'git config --global user.name "{name}"')
        print("✅ Kullanici bilgileri kaydedildi.")
    else:
        print(f"✅ Git kullanici: {name} <{email}>")


def remote_ayarla():
    """Remote origin'i ayarla veya guncelle."""
    mevcut = run("git remote get-url origin", hata_kritik=False).stdout.strip()
    if mevcut == REMOTE_URL:
        print(f"✅ Remote zaten dogru: {REMOTE_URL}")
    else:
        run("git remote remove origin", hata_kritik=False)
        run(f"git remote add origin {REMOTE_URL}")
        print(f"✅ Remote ayarlandi: {REMOTE_URL}")


def ilk_push_mu():
    """Bu ilk push mu yoksa guncelleme mi?"""
    result = run("git log --oneline -1", hata_kritik=False)
    return result.returncode != 0 or result.stdout.strip() == ""


def main():
    os.chdir(PROJE_KLASORU)

    baslik("Kokpitim — GitHub Sync")
    print(f"  Klasor : {PROJE_KLASORU}")
    print(f"  Repo   : {REMOTE_URL}")
    print(f"  Zaman  : {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Kontroller
    print("\n--- Ön Kontroller ---")
    kontrol_gitignore()
    git_kullanici_kontrol()

    # Commit mesaji
    print()
    commit_msg = input("Commit mesaji (bos birak = 'sync: tasklog guncellendi'): ").strip()
    if not commit_msg:
        commit_msg = f"sync: tasklog guncellendi — {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    ilk = ilk_push_mu()
    adim_sayisi = 6 if ilk else 5

    # 1. Git init (sadece ilk seferde)
    if ilk:
        adim(1, adim_sayisi, "Git baslatiliyor")
        run("git init")
        run(f"git branch -M {VARSAYILAN_BRANCH}")
        print("✅ Git baslatildi.")

    # 2. Dosyaları ekle
    adim(2 if ilk else 1, adim_sayisi, "Degisiklikler ekleniyor")
    result = run("git status --short", hata_kritik=False)
    if not result.stdout.strip():
        print("ℹ️  Degisiklik yok, push atlanacak.")
        sonuc_yazdir()
        return
    print(result.stdout.strip())
    run("git add .")
    kontrol_env_staged()
    print("✅ Dosyalar eklendi.")

    # 3. Commit
    adim(3 if ilk else 2, adim_sayisi, "Commit yapiliyor")
    result = run(f'git commit -m "{commit_msg}"', hata_kritik=False)
    if result.returncode != 0:
        print("ℹ️  Commit edilecek degisiklik yok.")
    else:
        print(f"✅ Commit: {commit_msg}")

    # 4. Remote ayarla
    adim(4 if ilk else 3, adim_sayisi, "Remote kontrol ediliyor")
    remote_ayarla()

    # 5. Pull (ilk pushta unrelated histories ile)
    adim(5 if ilk else 4, adim_sayisi, "GitHub'dan son hali cekiliyor")
    if ilk:
        run(
            f"git pull origin {VARSAYILAN_BRANCH} --allow-unrelated-histories --no-edit",
            hata_kritik=False,
        )
    else:
        run(f"git pull origin {VARSAYILAN_BRANCH} --no-edit", hata_kritik=False)
    print("✅ Pull tamamlandi.")

    # 6. Push
    adim(6 if ilk else 5, adim_sayisi, "GitHub'a push ediliyor")
    result = run(
        f"git push -u origin {VARSAYILAN_BRANCH}", hata_kritik=False
    )
    if result.returncode != 0:
        print(f"❌ Push basarisiz!\n{result.stderr.strip()}")
        print("\nManuel dene: git push -u origin main")
        sys.exit(1)
    print("✅ Push tamamlandi!")

    sonuc_yazdir(commit_msg)


def sonuc_yazdir(commit_msg=""):
    baslik("TAMAMLANDI!")
    print(f"  Repo  : https://github.com/{GITHUB_KULLANICI}/{REPO_ADI}")
    if commit_msg:
        print(f"  Commit: {commit_msg}")
    print()
    print("  TASKLOG raw link — Claude'a her oturumda bu linki yapistir:")
    print(f"  https://raw.githubusercontent.com/{GITHUB_KULLANICI}/{REPO_ADI}/main/docs/TASKLOG.md")
    print()


if __name__ == "__main__":
    main()
