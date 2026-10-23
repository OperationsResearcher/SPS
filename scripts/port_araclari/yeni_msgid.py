import sys,json
from babel.messages.pofile import read_po
sp=sys.argv[1]
pot=read_po(open(sp+"/yeni.pot","rb"))
en=read_po(open("translations/en/LC_MESSAGES/messages.po","rb"),locale="en")
mevcut={m.id for m in en if m.id}
yeni=[m for m in pot if m.id and isinstance(m.id,str) and m.id not in mevcut]
json.dump([[m.id,[f"{a}:{b}" for a,b in m.locations][:2]] for m in yeni],open(sp+"/yeni_msgid.json","w",encoding="utf-8"),ensure_ascii=False)
print(len(yeni))
for i,m in enumerate(yeni): print(i,json.dumps(m.id,ensure_ascii=False))
