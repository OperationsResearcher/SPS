import sys; sys.path.insert(0,sys.argv[1])
from pw_ortak import *
SAYFALAR=["/k-report","/desktop","/k-plan/strategy/exec-dashboard","/k-plan/process","/k-plan/strategy","/k-plan/strategy/periods","/k-plan/individual/scorecard","/k-plan/project","/profile","/admin/users","/admin/araclar/loglar","/admin/araclar/hata-kontrolu","/admin/sub-tenants","/admin/sub-tenants/usage","/holding/dashboard","/k-report/initiative-bubble","/k-report/pi-project-impact","/settings/scheduled-reports","/admin/tenants","/k-plan/strategy/menu"]
def tara(tema,email,mobil=False,lang=None,etiket=""):
    sonuc=[]
    with sync_playwright() as p:
        b,ctx=baslat(p,tema,mobil,lang); pg=ctx.new_page()
        giris(pg,email)
        hata=[];kirik=[]
        pg.on("console",lambda m:hata.append(m.text[:120]) if m.type=="error" else None)
        pg.on("pageerror",lambda e:hata.append("PAGEERR "+str(e)[:120]))
        pg.on("response",lambda r:kirik.append(f"{r.status} {r.url[len(BASE):][:70]}") if r.status>=400 else None)
        for u in SAYFALAR:
            hata.clear();kirik.clear()
            try:
                r=pg.goto(BASE+u,wait_until="networkidle",timeout=30000); st=r.status if r else 0
            except Exception as e: st="TIMEOUT"
            if tema=="dark": pg.evaluate("document.documentElement.classList.add('dark')")
            tasma=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
            ad=u.strip("/").replace("/","_")
            pg.screenshot(path=f"{SP}/{os.environ.get('OUT','yeni')}/s_{etiket}{ad}.png",full_page=False)
            sonuc.append((u,st,pg.url[len(BASE):] if pg.url.startswith(BASE) else pg.url,len(set(hata)),sorted(set(kirik))[:4],sorted(set(hata))[:2],tasma))
        b.close()
    return sonuc
if __name__=="__main__":
    tema=sys.argv[2]; mobil=len(sys.argv)>3 and sys.argv[3]=="mobil"
    for r in tara(tema,"ux-admin@uxtest.local",mobil,None,tema+("_m_" if mobil else "_")): print(r)
