@echo off
setlocal

echo [INFO] Kod cekiliyor...
git pull origin main
if errorlevel 1 goto :fail

echo [INFO] Virtual environment aktiv ediliyor...
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
) else (
    echo [ERROR] .venv bulunamadi. Lutfen once sanal ortam olusturun.
    exit /b 1
)

echo [INFO] Paketler guncelleniyor...
pip install -r requirements.txt
if errorlevel 1 goto :fail

echo [INFO] IIS reset...
iisreset
if errorlevel 1 goto :fail

echo [OK] SERVER_PULL tamamlandi.
exit /b 0

:fail
echo [ERROR] Islem basarisiz oldu.
exit /b 1
