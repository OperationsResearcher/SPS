# -*- coding: utf-8 -*-
"""Demo baseline yönetimi — operatör CLI (KURALLAR §8.4).

YALNIZCA demo ortamında (KOKPITIM_DEMO_MODE=1) çalışır; aksi halde servis
guard'ı RuntimeError atar. Yerel/Test/Yayın'da çalıştırılması güvenlidir
(no-op / hata) çünkü servis demo flag'ini şart koşar.

Kullanım (demo container içinde):
    python -m scripts.demo_baseline snapshot   # mevcut Tomofil'i baseline olarak dondur
    python -m scripts.demo_baseline restore     # Tomofil'i baseline'a geri yükle (manuel)
    python -m scripts.demo_baseline status       # baseline var mı, tablo sayısı

Tipik kurulum sırası:
    1. Yerel Tomofil verisi demo DB'ye yüklenir (operatör, pg_dump/psql)
    2. python -m scripts.demo_baseline snapshot   ← başlangıç noktası kaydedilir
    3. Demo akışı artık her oturum sonunda bu noktaya döner
"""
import sys


def main(argv):
    cmd = (argv[1] if len(argv) > 1 else "status").lower()

    from dotenv import load_dotenv
    load_dotenv()
    from app import create_app
    app = create_app()

    if not app.config.get("KOKPITIM_DEMO_MODE"):
        print("HATA: KOKPITIM_DEMO_MODE=1 değil. Bu script yalnızca demo ortamında çalışır.")
        return 2

    with app.app_context():
        from app.services import demo_reset_service as svc
        if cmd == "snapshot":
            print("→ Tomofil verisi baseline olarak donduruluyor…")
            svc.snapshot_baseline()
            print("✓ baseline snapshot alındı.")
        elif cmd == "restore":
            ok = svc.restore_baseline()
            print("✓ baseline'a geri yüklendi." if ok else "⚠ baseline yok — önce snapshot.")
        elif cmd == "status":
            exists = svc.baseline_exists()
            print(f"baseline şema ({svc.BASELINE_SCHEMA}): {'VAR' if exists else 'YOK'}")
        else:
            print(f"Bilinmeyen komut: {cmd}  (snapshot | restore | status)")
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
