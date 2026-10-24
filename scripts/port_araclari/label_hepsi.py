import sys,subprocess
sys.path.insert(0,sys.argv[1])
import g_i18n as g
wip=set(l[3:].strip().replace("\\","/") for l in subprocess.run(["git","status","--short","ui/templates"],capture_output=True,text=True,encoding="utf-8").stdout.splitlines())
deg=[]
for f in sorted(g.ROOT.rglob("*.html")):
    rel=f.relative_to(g.ROOT).as_posix()
    if "ui/templates/platform/"+rel in wip: continue
    raw=f.read_bytes();bom=raw.startswith(b"\xef\xbb\xbf");t=raw.decode("utf-8-sig");crlf="\r\n" in t;t=t.replace("\r\n","\n")
    n=[0]
    def lab(m):
        v=m.group(2)
        if "_(" in v or not g.HARF.search(v): return m.group(0)
        n[0]+=1
        return f"{m.group(1)}_('{g.esc_s(g.norm(v))}')"
    t2=g.LABEL.sub(lab,t)
    if n[0]:
        f.write_bytes((b"\xef\xbb\xbf" if bom else b"")+(t2.replace("\n","\r\n") if crlf else t2).encode("utf-8")); deg.append((rel,n[0]))
print(len(deg),sum(n for _,n in deg)); print([r for r,_ in deg])
