import re,subprocess,sys
sys.path.insert(0,sys.argv[1])
from g_arac import *
def efektif(text,css):
    text=text.replace("\r\n","\n")
    mk=KORUMA.sub(lambda m:"\x00"*len(m.group(0)),text)
    r=[]
    for m in ETIKET.finditer(mk):
        if m.group(1)=='link' and 'platform/css/g_' in text[m.start():m.end()]: continue
        t=text[m.start():m.end()]
        if "\x00" in mk[m.start():m.end()]: r.append((m.group(1),"J",)); continue
        sm=STIL.search(t); st=norm(sm.group(1)) if sm else ""
        cm=SINIF.search(t); cl=[]
        if cm:
            for c in cm.group(1).split():
                if c in css: st=(st+" "+css[c]).strip()
                else: cl.append(c)
        r.append((m.group(1),st,tuple(cl)))
    return r
bad=0
for rel,cssad in zip(sys.argv[2::2],sys.argv[3::2]):
    p="ui/templates/platform/"+rel
    old=subprocess.run(["git","show","HEAD:"+p],capture_output=True).stdout.decode("utf-8-sig")
    new=open(p,"rb").read().decode("utf-8-sig")
    css={}
    for l in open("ui/static/platform/css/"+cssad,encoding="utf-8"):
        m=re.match(r"\.(\S+?)\.\1 \{ (.*) \}",l.strip())
        if m: css[m.group(1)]=m.group(2)
    a=efektif(old,{});b=efektif(new,css)
    ok=len(a)==len(b) and all(x==y for x,y in zip(a,b))
    print(rel,"ESIT" if ok else "FARKLI",len(a),len(b))
    if not ok:
        bad+=1
        for x,y in zip(a,b):
            if x!=y: print(" ",x,"\n ",y);break
sys.exit(bad)
