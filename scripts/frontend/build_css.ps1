# Tailwind CSS derleme (TASK-236)
# Ne zaman: template/JS'te yeni Tailwind utility class kullanıldığında.
# Gereksinim: Node.js (npx). Çıktı: ui/static/platform/css/tailwind.css
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot
npx -y tailwindcss@3.4.17 -c tailwind.config.js -i tailwind.input.css -o ..\..\ui\static\platform\css\tailwind.css --minify
Write-Host "OK: ui/static/platform/css/tailwind.css guncellendi"
