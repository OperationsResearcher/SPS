import sys,json; sys.path.insert(0,sys.argv[1])
from pw_ortak import *
SAY=["/desktop","/k-plan/strategy","/k-plan/process","/k-plan/process/222/karne","/k-plan/project","/k-plan/individual/scorecard","/k-report","/k-plan/strategy/periods","/profile","/admin/users","/admin/sub-tenants","/admin/araclar/hata-kontrolu","/settings/scheduled-reports","/k-report/initiative-bubble","/k-report/pi-project-impact","/k-plan/strategy/scenarios"]
ETK=r"""()=>{const r=[];document.querySelectorAll('input,select,textarea').forEach(e=>{
 if(['hidden','submit','button','checkbox','radio'].includes(e.type))return; const b=e.getBoundingClientRect(); if(b.width===0&&b.height===0)return;
 const ok=e.getAttribute('aria-label')||e.getAttribute('aria-labelledby')||e.title||(e.id&&document.querySelector('label[for="'+CSS.escape(e.id)+'"]'))||e.closest('label');
 if(!ok)r.push((e.tagName+'#'+(e.id||'')+'.'+(e.name||'')).slice(0,50)+' ph='+(e.placeholder||'').slice(0,20))});return r}"""
with sync_playwright() as p:
    b,ctx=baslat(p); pg=ctx.new_page(); giris(pg,"ux-admin@uxtest.local")
    # 3 modal istemi
    pg.goto(BASE+"/desktop",wait_until="networkidle")
    pg.evaluate("""()=>{window.__alert=0;window.alert=()=>{window.__alert++};window.confirm=()=>{window.__alert++;return true};
      window.__sonuc='bekliyor';openMcTextPrompt({title:'Test',label:'Not',requiredMessage:'Bu alan zorunludur.',textarea:true}).then(v=>window.__sonuc=v)}""")
    pg.wait_for_selector("#mc-prompt-input")
    pg.click(".mc-modal-footer .mc-btn-primary"); pg.wait_for_timeout(300)
    print("§3 bos gonder -> hata gorunur:",pg.is_visible("#mc-prompt-error"),"| metin:",pg.inner_text("#mc-prompt-error"),"| aria-invalid:",pg.get_attribute("#mc-prompt-input","aria-invalid"),"| odak girdi:",pg.evaluate("document.activeElement.id"))
    pg.keyboard.press("Escape"); pg.wait_for_timeout(300)
    print("§3 Esc kapatti:",pg.locator("#mc-prompt-input").count()==0,"| sonuc:",pg.evaluate("window.__sonuc"))
    pg.evaluate("()=>{openMcTextPrompt({title:'Test2',label:'Not',requiredMessage:'Zorunlu'}).then(v=>window.__sonuc=v)}"); pg.wait_for_selector("#mc-prompt-input")
    pg.fill("#mc-prompt-input","merhaba"); pg.keyboard.press("Enter"); pg.wait_for_timeout(400)
    print("§3 Enter gonderdi:",pg.evaluate("window.__sonuc"),"| alert/confirm cagrisi:",pg.evaluate("window.__alert"))
    # 4 odak halkasi
    pg.goto(BASE+"/desktop",wait_until="networkidle"); hal=[]
    for i in range(8):
        pg.keyboard.press("Tab"); hal.append(pg.evaluate("(()=>{const e=document.activeElement;const s=getComputedStyle(e);return (s.outlineStyle!=='none'&&parseFloat(s.outlineWidth)>0)||(s.boxShadow&&s.boxShadow!=='none')})()"))
    print("§4 Tab odak halkasi gorunen:",sum(hal),"/",len(hal))
    toplam=0
    for u in SAY:
        try: pg.goto(BASE+u,wait_until="networkidle",timeout=30000)
        except Exception: print(u,"yuklenemedi"); continue
        r=pg.evaluate(ETK); toplam+=len(r)
        if r: print("  etiketsiz",u,r[:5])
    print("§4 etiketsiz alan toplami (16 sayfa):",toplam)
    b.close()
    # mobil
    b,ctx=baslat(p,mobil=True); pg=ctx.new_page(); giris(pg,"ux-admin@uxtest.local")
    sor=[]
    for u in SAY:
        pg.goto(BASE+u,wait_until="networkidle",timeout=30000)
        t=pg.evaluate("document.documentElement.scrollWidth-document.documentElement.clientWidth")
        if t>0: sor.append((u,t))
    print("§4 mobil yatay tasma:",sor)
    pg.goto(BASE+"/k-plan/process/222/karne",wait_until="networkidle")
    print("§4 mobil karne input min font px:",pg.evaluate("Math.min(...[...document.querySelectorAll('input:not([type=hidden]),select')].filter(e=>e.getBoundingClientRect().width>0).map(e=>parseFloat(getComputedStyle(e).fontSize)))"))
    pg.screenshot(path=SP+"/s_mobil_karne.png"); b.close()
