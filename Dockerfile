# Production Flask uygulaması - Python 3.9 slim
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (gerekirse)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Kalıcı veri dizinleri (volume ile mount edilecek)
RUN mkdir -p /app/data /app/instance

# Gunicorn ile 5000 portunda başlat
# run:app = run.py modülündeki app nesnesi
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--threads", "2", "run:app"]
