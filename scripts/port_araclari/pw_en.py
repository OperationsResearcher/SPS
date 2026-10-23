import sys,json; sys.path.insert(0,sys.argv[1])
from pw_ortak import *
SAY=["/desktop","/k-plan/strategy","/k-plan/process","/k-plan/process/222/karne","/k-plan/project","/k-plan/individual/scorecard","/k-report","/k-plan/strategy/periods","/k-plan/strategy/exec-dashboard","/profile","/admin/users","/k-plan/strategy/menu","/settings/scheduled-reports","/k-plan/strategy/kaskad","/k-plan/strategy/okr","/k-plan/strategy/cascade"]
JSX=r"""()=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
while(n=w.nextNode()){const p=n.parentElement;if(!p||['SCRIPT','STYLE','NOSCRIPT'].includes(p.tagName))continue;
 const t=n.textContent.trim();if(t.length<3||!/[çğıöşüÇĞİÖŞÜ]/.test(t))continue;
 const r=p.getBoundingClientRect();if(r.width===0&&r.height===0)continue;out.push(t.slice(0,70))}
 [...document.querySelectorAll('[placeholder],[title],[aria-label]')].forEach(e=>{for(const a of ['placeholder','title','aria-label']){const v=e.getAttribute(a);if(v&&/[çğıöşüÇĞİÖŞÜ]/.test(v))out.push('@'+a+': '+v.slice(0,60))}});
 return [...new Set(out)]}"""
with sync_playwright() as p:
    b,ctx=baslat(p,lang="en"); pg=ctx.new_page(); giris(pg,"ux-admin@uxtest.local")
    pg.goto(BASE+"/desktop?lang=en",wait_until="networkidle")
    toplam=0
    for u in SAY:
        try: pg.goto(BASE+u+("&" if "?" in u else "?")+"lang=en",wait_until="networkidle",timeout=30000)
        except Exception as e: print(u,"HATA",str(e)[:60]); continue
        r=pg.evaluate(JSX); toplam+=len(r)
        for x in r:
            if not x.startswith("@title: 2025"): print("  ",u.split("/")[-1][:14],"|"," ".join(x.split())[:150])
    print("TOPLAM",toplam); b.close()
