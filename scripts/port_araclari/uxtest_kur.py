import json,secrets,sys
from werkzeug.security import generate_password_hash
from app import create_app
from extensions import db
from app.models.core import Tenant, User, Role
from app.models.plan_year import PlanYear
from app.models.saas import SubscriptionPackage
app=create_app()
pw=secrets.token_urlsafe(10)+"Aa1"
with app.app_context():
    pkg=SubscriptionPackage.query.first()
    rid=Role.query.filter_by(name="tenant_admin").first().id
    std=Role.query.filter_by(name="standard_user").first()
    if not std:
        std=Role(name="standard_user",description="UXTEST standart kullanici"); db.session.add(std); db.session.flush()
    out={"pw":pw}
    def mk(name,short,email,role,years):
        t=Tenant.query.filter_by(short_name=short).first()
        if not t:
            t=Tenant(name=name,short_name=short,is_active=True,tenant_type="normal",package_id=pkg.id if pkg else None,max_user_count=20,plan_year_enabled=True)
            db.session.add(t); db.session.flush()
        for y in years:
            if not PlanYear.query.filter_by(tenant_id=t.id,year=y).first():
                db.session.add(PlanYear(tenant_id=t.id,year=y,name=str(y),status="active"))
        u=User.query.filter_by(email=email).first()
        if not u:
            u=User(email=email,first_name="UXTEST",last_name=short,tenant_id=t.id,role_id=role,password_hash=generate_password_hash(pw),is_active=True)
            db.session.add(u)
        else:
            u.password_hash=generate_password_hash(pw)
        db.session.flush(); return t.id
    out["bos_tenant"]=mk("UXTEST Bos Kurum","uxbos","ux-bos@uxtest.local",rid,[])
    out["dolu_tenant"]=mk("UXTEST Dolu Kurum","uxdolu","ux-dolu@uxtest.local",rid,[2026])
    mk("UXTEST Dolu Kurum","uxdolu","ux-std@uxtest.local",std.id,[2026])
    db.session.commit()
    json.dump(out,open(sys.argv[1]+"/uxtest.json","w"))
    print(out["bos_tenant"],out["dolu_tenant"])
