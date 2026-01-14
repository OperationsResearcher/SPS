# -*- coding: utf-8 -*-
from __init__ import create_app

app = create_app()

with app.app_context():
    from services.project_analytics import calculate_surec_saglik_skoru
    
    try:
        result = calculate_surec_saglik_skoru(4, 2025)
        if result:
            print('Skor:', result.get('skor'))
            print('Detaylar:', result.get('detaylar'))
            print('Durum:', result.get('durum'))
        else:
            print('Result: None')
    except Exception as e:
        import traceback
        print('HATA:', str(e))
        traceback.print_exc()
