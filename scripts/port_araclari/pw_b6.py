import sys,json; sys.path.insert(0,sys.argv[1])
from pw_ortak import *
JS="""async ([u,b])=>{const t=document.querySelector('meta[name=csrf-token]').content;
 const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':t},body:JSON.stringify(b)});
 let j=null;try{j=await r.json()}catch(e){} return [r.status,j]}"""
def post(pg,u,b): return pg.evaluate(JS,[u,b])
with sync_playwright() as p:
    for e in ("ux-bos@uxtest.local","ux-dolu@uxtest.local"):
        b,ctx=baslat(p); pg=ctx.new_page(); giris(pg,e); pg.goto(BASE+"/k-plan/strategy",wait_until="networkidle")
        print("==",e)
        s=post(pg,"/k-plan/strategy/api/strategy/add",{"title":"UXTEST Strateji","code":"UX1"}); print(" SP strateji ekle:",s[0],(s[1] or {}).get("code") or (s[1] or {}).get("message"))
        k=post(pg,"/organization/api/add-strategy",{"title":"UXTEST Kurum Stratejisi","code":"UX2"}); print(" Kurum strateji ekle:",k[0],(k[1] or {}).get("code") or (k[1] or {}).get("message"))
        sid=(s[1] or {}).get("id") or ((s[1] or {}).get("data") or {}).get("id")
        if s[0]==200 and sid:
            a=post(pg,"/k-plan/strategy/api/sub-strategy/add",{"strategy_id":sid,"title":"UXTEST Alt","code":"UX1.1"}); print(" SP alt strateji ekle:",a[0],(a[1] or {}).get("message"))
            ks=post(pg,"/organization/api/add-sub-strategy",{"strategy_id":sid,"title":"UXTEST Kurum Alt","code":"UX1.2"}); print(" Kurum alt ekle:",ks[0],(ks[1] or {}).get("message"))
        b.close()
