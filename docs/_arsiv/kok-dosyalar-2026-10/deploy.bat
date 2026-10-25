@echo off
color 0A
echo ========================================================
echo  GITHUB DEPLOYMENT BASLATILIYOR... (Gelistirme Ortami)
echo ========================================================
echo.

:: 1. Gereksiz __pycache__ dosyalarini temizle (Proje sismesin)
echo [1/4] Cop dosyalar temizleniyor...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"

:: 2. Tum degisiklikleri sahneye al
echo [2/4] Degisiklikler ekleniyor (git add)...
git add .

:: 3. Kullanicidan commit mesaji iste (Bos gecilirse otomatik tarih atar)
echo.
set /p commit_msg="[3/4] Commit mesaji girin (Bos birakmak icin Enter): "

if "%commit_msg%"=="" (
    set commit_msg=Otomatik Guncelleme - %date% %time%
)

:: 4. Commit ve Push islemi
echo.
echo [4/4] Github'a gonderiliyor...
git commit -m "%commit_msg%"
git push origin main

echo.
echo ========================================================
echo  ISLEM BASARIYLA TAMAMLANDI! 
echo ========================================================
timeout /t 5