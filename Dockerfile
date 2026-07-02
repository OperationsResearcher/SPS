# Production Flask uygulaması - Python 3.9 slim
FROM python:3.11-slim

# Çalışma dizini
WORKDIR /app

# Sistem bağımlılıkları (gerekirse)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları kopyala ve yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY . .

# Kalıcı veri dizinleri (volume ile mount edilecek)
RUN mkdir -p /app/data /app/instance

# Gunicorn ile PORT env'inde başlat (varsayılan 5000 — Yayın davranışı değişmez).
# run:app = run.py modülündeki app nesnesi
# PORT desteği eklendi (2026-07-02): Test/Demo ortamları host network modunda
# farklı portlarda (5050/5080) çalışması gerekirken CMD sabit 5000'e bind
# ediyordu — setup_test_env.sh'nin -e PORT=$APP_PORT satırı hiç etkisizdi.
ENV FLASK_ENV=production
ENV TRUST_PROXY=1

EXPOSE 5000
# Üretimde aralıklı takılan worker etkisini azaltmak için:
# - worker sayısı artırıldı
# - keep-alive düşürüldü
# - max-requests ile periyodik worker yenileme açıldı
CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT:-5000} --workers ${GUNICORN_WORKERS:-8} --threads ${GUNICORN_THREADS:-1} --timeout ${GUNICORN_TIMEOUT:-60} --graceful-timeout ${GUNICORN_GRACEFUL_TIMEOUT:-20} --keep-alive ${GUNICORN_KEEPALIVE:-2} --max-requests ${GUNICORN_MAX_REQUESTS:-1000} --max-requests-jitter ${GUNICORN_MAX_REQUESTS_JITTER:-100} run:app"]
