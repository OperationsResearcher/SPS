import sys,json; sys.path.insert(0,sys.argv[1])
from pw_ortak import *
from PIL import Image
im=Image.new("RGB",(300,300),(80,120,200)); im.save(sys.argv[1]+"/foto.png"); im.save(sys.argv[1]+"/foto.jpg"); im.save(sys.argv[1]+"/foto.webp")
open(sys.argv[1]+"/sahte.png","wb").write(b"not an image at all")
with sync_playwright() as p:
    b,ctx=baslat(p); pg=ctx.new_page(); giris(pg,"ux-admin@uxtest.local")
    hata=[]; pg.on("pageerror",lambda e:hata.append(str(e)[:100]))
    pg.goto(BASE+"/profile",wait_until="networkidle")
    for f in ("foto.png","foto.jpg","foto.webp","sahte.png"):
        with pg.expect_response(lambda r:"photo" in r.url or "avatar" in r.url or "profile" in r.url and r.request.method=="POST",timeout=15000) as ri:
            pg.set_input_files("#profilePhotoInput",sys.argv[1]+"/"+f)
        r=ri.value
        try: j=r.json()
        except Exception: j=None
        print("foto",f,r.status,(j or {}).get("message") or j)
        pg.wait_for_timeout(500)
        # Swal kapat
        try: pg.keyboard.press("Escape")
        except Exception: pass
    # XSS: alert tetiklenir mi
    dialogs=[]; pg.on("dialog",lambda d:(dialogs.append(d.message),d.dismiss()))
    pg.goto(BASE+"/k-plan/strategy",wait_until="networkidle")
    JS="""async ([u,b])=>{const t=document.querySelector('meta[name=csrf-token]').content;const r=await fetch(u,{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':t},body:JSON.stringify(b)});return [r.status,(await r.json())]}"""
    s=pg.evaluate(JS,["/k-plan/strategy/api/strategy/add",{"title":"<img src=x onerror=alert(1)>XSS<script>alert(2)</script>","code":"XS1","description":"<script>alert(3)</script>"}])
    print("xss ekle:",s[0],s[1].get("message"))
    pg.goto(BASE+"/k-plan/strategy",wait_until="networkidle"); pg.wait_for_timeout(1500)
    print("xss: alert tetiklendi mi:",dialogs, "| sayfada ham <script> metni:", pg.evaluate("document.body.innerHTML.includes('<script>alert(2)')"))
    pg.goto(BASE+"/k-plan/strategy/kaskad",wait_until="networkidle"); pg.wait_for_timeout(1000); print("xss kaskad alert:",dialogs)
    print("pageerror:",hata[:3])
    b.close()
    # oran sinirlama: yanlis parola
    b,ctx=baslat(p); pg=ctx.new_page(); kodlar=[]
    for i in range(9):
        pg.goto(BASE+"/login"); pg.fill('input[name="email"]',"ux-nobody@uxtest.local"); pg.fill('input[name="password"]',"yanlis")
        with pg.expect_navigation(): pg.click('button[type="submit"]')
        kodlar.append(pg.evaluate("document.body.innerText.slice(0,0)")+str(pg.url.split('/')[-1]))
    print("yanlis giris sonuc sayfalari:",kodlar[:3],"...",kodlar[-1], "| son metin:",pg.evaluate("document.body.innerText").replace("\n"," ")[:120])
    b.close()
