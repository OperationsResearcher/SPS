import json,sys,subprocess,io
from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo
sp=sys.argv[1]
Y=json.load(open(sp+"/yeni_msgid.json",encoding="utf-8"))
M=json.load(open(sp+"/map.json",encoding="utf-8"))
p="translations/en/LC_MESSAGES/messages.po";m=p[:-2]+"mo"
def ekle(text):
    nl="\r\n" if "\r\n" in text else "\n"
    blok=""
    for mid,loc in Y:
        if mid not in M: print("CEVIRISIZ:",mid); continue
        blok+=nl+"".join("#. "+l+nl for l in loc[:1])+("#, python-format"+nl if "%(" in mid else "")+"msgid "+json.dumps(mid,ensure_ascii=False)+nl+"msgstr "+json.dumps(M[mid],ensure_ascii=False)+nl
    return text.rstrip("\r\n")+nl+blok
def mo(b):
    c=read_po(io.BytesIO(b),locale="en"); o=io.BytesIO(); write_mo(o,c); return o.getvalue(),c
def mevcut_id(text): 
    c=read_po(io.BytesIO(text.encode("utf-8")),locale="en"); return {x.id for x in c if x.id}
w=open(p,"rb").read().decode("utf-8"); var=mevcut_id(w)
Y[:]=[y for y in Y if y[0] not in var]
w=ekle(w); open(p,"wb").write(w.encode("utf-8")); open(m,"wb").write(mo(w.encode("utf-8"))[0])
h=subprocess.run(["git","show","HEAD:"+p],capture_output=True).stdout.decode("utf-8")
hv=mevcut_id(h); Y[:]=[y for y in Y if y[0] not in hv]
h=ekle(h); mb,_=mo(h.encode("utf-8"))
for path,data in ((p,h.encode("utf-8")),(m,mb)):
    x=subprocess.run(["git","hash-object","-w","--stdin"],input=data,capture_output=True).stdout.decode().strip()
    subprocess.run(["git","update-index","--cacheinfo","100644,"+x+","+path],check=True)
print("eklendi")
