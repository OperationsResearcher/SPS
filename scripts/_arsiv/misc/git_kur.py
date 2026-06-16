import os
import subprocess

def run_cmd(command, ignore_error=False):
    print(f"⏳ Calistiriliyor: {command}")
    try:
        subprocess.run(command, check=True, shell=True)
        print("✅ Basarili.")
    except subprocess.CalledProcessError:
        if not ignore_error:
            print(f"❌ HATA: '{command}' komutu calistirilamadi!")
            exit(1)
        else:
            print("ℹ️ (Bu adim atlandi, sorun yok)")

print("--- SPS GITHUB OTOMATIK KURULUM ROBOTU ---")

# 1. .gitignore Dosyasini Garantiye Al (Veritabani Kacmasin)
gitignore_icerik = """
.venv/
venv/
__pycache__/
*.pyc
.vscode/
.env
*.db
*.sqlite
*.sqlite3
instance/
SPS_DATA/
*.log
"""
with open(".gitignore", "w") as f:
    f.write(gitignore_icerik.strip())
print("✅ .gitignore dosyasi guvenli hale getirildi.")

# 2. Kullanicidan Linki Iste
repo_url = input("\n👉 Lutfen GitHub Repo Linkini yapistirin (https://...): ").strip()

if not repo_url.startswith("https://github.com"):
    print("❌ HATA: Gecerli bir GitHub linki girmediniz!")
    exit(1)

# 3. Git Komutlarini Sirayla Calistir
commands = [
    "git init",
    "git add .",
    'git commit -m "SPS Proje Ilk Yukleme"',
    "git branch -M main",
    "git remote remove origin",  # Eskisi varsa siler (Hata verirse onemseme)
    f"git remote add origin {repo_url}",
    "git push -u origin main"
]

print("\n🚀 Yukleme basliyor...\n")

for cmd in commands:
    # Remote remove komutu hata verebilir (eger yoksa), onu gormezden gel diyoruz
    if "remote remove" in cmd:
        run_cmd(cmd, ignore_error=True)
    else:
        run_cmd(cmd)

print("\n🎉 TEBRIKLER! Kodlariniz GitHub'a yuklendi.")
print("Artik sunucuya gecip 'GUNCELLE.bat' butonunu yapabiliriz.")