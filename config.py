import os
from dotenv import load_dotenv

# .env dosyasini yukle
load_dotenv()


class Config:
    # --- VERITABANI AYARLARI (HIBRIT YAPI) ---
    # .env dosyasinda DATABASE_URL varsa onu kullanir (Prod/Supabase)
    # Yoksa yerel SQLite dosyasini kullanir (Local/Dev)
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'spsv2.db'))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Guvenlik
    SECRET_KEY = os.getenv('SECRET_KEY', 'varsayilan-guvensiz-anahtar-degistir')
    DEBUG = True


# __init__.py dosyasinin aradigi fonksiyon:
def get_config(config_name=None):
    return Config
