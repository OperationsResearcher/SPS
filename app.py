# -*- coding: utf-8 -*-
"""
Flask Uygulama Giriş Noktası
"""
from dotenv import load_dotenv
load_dotenv()  # .env dosyasını yükle

from __init__ import create_app
import atexit

app = create_app()

# Uygulama kapanırken scheduler'ı temiz şekilde kapat
def cleanup():
    from services.task_reminder_scheduler import shutdown_scheduler
    shutdown_scheduler()

atexit.register(cleanup)

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)

