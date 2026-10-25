@echo off
echo ========================================================
echo   SPS GELISTIRME VE SENKRONIZASYON ARACI
echo ========================================================
echo.

:: 1. Sanal ortami aktif et
call .venv\Scripts\activate

:: 2. Kullanicidan mesaj al
set /p msg="Yapilan degisiklik nedir? (Orn: yeni tablo eklendi): "
if "%msg%"=="" set msg="Otomatik guncelleme"

echo.
echo [1/4] Migration dosyasi hazirlaniyor...
py -m flask db migrate -m "%msg%"

:: 3. YEREL DB (SQLite) Guncelle
echo.
echo [2/4] YEREL (SQLite) veritabani guncelleniyor...
:: Gecici olarak local ayarlara zorla
set DATABASE_URL=sqlite:///spsv2.db
py -m flask db upgrade

:: 4. SUPABASE (Canli) Guncelle
echo.
echo [3/4] CANLI (Supabase) veritabani guncelleniyor...
:: Supabase Pooler Adresi (Sifre dahil)
set DATABASE_URL=postgresql://postgres.xeurenvaugtwtqandzje:UM949tMW04t08BiT@aws-1-eu-west-1.pooler.supabase.com:6543/postgres
py -m flask db upgrade

:: 5. Kodlari GitHub'a Gonder
echo.
echo [4/4] Kodlar GitHub'a gonderiliyor...
git add .
git commit -m "%msg%"
git push origin main

echo.
echo ========================================================
echo   ISLEM BASARIYLA TAMAMLANDI! 
echo ========================================================
timeout /t 10