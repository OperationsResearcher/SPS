import re,sys,html,subprocess
sys.path.insert(0,sys.argv[1])
import g_i18n as g
from pathlib import Path
wip=set(l[3:].strip().replace("\\","/") for l in subprocess.run(["git","status","--short","ui/templates"],capture_output=True,text=True,encoding="utf-8").stdout.splitlines())
tot=0;rows=[]
for f in sorted(g.ROOT.rglob("*.html")):
    rel=f.relative_to(g.ROOT).as_posix()
    if "ui/templates/platform/"+rel in wip: continue
    t=f.read_bytes().decode("utf-8-sig").replace("\r\n","\n")
    maske=g.KORUMA.sub(lambda m:"\x00"*len(m.group(0)),t)
    n=0
    for m in g.METIN.finditer(maske):
        s,e=m.start(1),m.end(1)
        if "\x00" in maske[s:e]: continue
        txt=g.norm(t[s:e])
        if len(txt)>=2 and g.HARF.search(txt) and not re.fullmatch(r"[\W\d_]*",txt): n+=1
    for m in g.ATTR.finditer(maske):
        if "\x00" in maske[m.start():m.end()]: continue
        txt=g.norm(t[m.start(2):m.end(2)])
        if g.HARF.search(txt) and not re.fullmatch(r"[\W\d_]*",txt): n+=1
    if n: rows.append((n,rel)); tot+=n
rows.sort(reverse=True)
print("toplam",tot,"dosya",len(rows)); print(rows[:25])
