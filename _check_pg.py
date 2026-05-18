import sys, os
sys.path.insert(0, '.')
os.environ.setdefault('FLASK_ENV', 'development')

from app import create_app
app = create_app()
with app.app_context():
    from app.models.process import ProcessKpi, Process
    from sqlalchemy import text

    # SR2 sürecini bul
    procs = Process.query.filter(Process.code.like('%SR2%')).all()
    print(f"SR2 süreçleri: {[(p.id, p.code, p.name) for p in procs]}")

    # Process 55'i bul
    p = Process.query.get(55)
    if p:
        print(f"\nSüreç 55: {p.code} - {p.name}")
        kpis = ProcessKpi.query.filter_by(process_id=55, is_active=True).all()
        for k in kpis:
            if 'EFQM' in (k.name or '') or 'efqm' in (k.name or '').lower():
                print(f"\n  KPI: {k.id} - {k.name}")
                print(f"  target_value: {k.target_value!r}")
                print(f"  direction: {getattr(k, 'direction', 'YOK')!r}")
                print(f"  basari_puani_araliklari: {getattr(k, 'basari_puani_araliklari', 'YOK')!r}")
                print(f"  score_ranges: {getattr(k, 'score_ranges', 'YOK')!r}")
                # Tüm alanları listele
                print(f"  Tüm alanlar: {[c.name for c in k.__table__.columns]}")
