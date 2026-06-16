"""Uygulama baslatma testi — mapper hatasi olmadan yuklenmeli."""
import os
os.environ['FLASK_ENV'] = 'development'

try:
    from __init__ import create_app
    app = create_app()
    with app.app_context():
        from app.models.core import User, Tenant
        from models import User as LegacyUser
        print(f"app.models.core.User tablename  : {User.__tablename__}")
        print(f"models.LegacyUser tablename     : {LegacyUser.__tablename__}")
        print(f"Same class?                     : {User is LegacyUser}")
        # Sorgu dene
        u_count = User.query.count()
        print(f"User.query.count()              : {u_count}")
        lu_count = LegacyUser.query.count()
        print(f"LegacyUser.query.count()        : {lu_count}")
    print("\nOK: Uygulama basarıyla basladi, mapper hatasi yok.")
except Exception as e:
    import traceback
    print(f"\nHATA: {e}")
    traceback.print_exc()
