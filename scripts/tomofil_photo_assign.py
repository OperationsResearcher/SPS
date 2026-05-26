"""Tomofil çalışanları için profil fotoğraflarını cinsiyete göre eşleştir.

Kullanım:
    python scripts/tomofil_photo_assign.py            # dry-run plan
    python scripts/tomofil_photo_assign.py --apply    # rename
"""
from __future__ import annotations

import re
import shutil
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PHOTOS_DIR = ROOT / "docs" / "tomofil" / "fotos"
USERS_FILE = ROOT / "data" / "tomofil_users.txt"


# Türkçe cinsiyet (kullanıcı isimleri için)
TR_FEMALE = {
    "ayşe","fatma","zeynep","elif","merve","büşra","esra","hatice","emine",
    "gülay","gül","şule","selin","cansu","esin","sibel","pınar","ebru","burcu",
    "aslı","ceren","damla","derya","dilek","duygu","eda","ela","ezgi","filiz",
    "gamze","gizem","hande","hilal","idil","irem","kübra","leyla","melike",
    "melis","meltem","mine","müge","nazan","neslihan","nesrin","nilgün",
    "nilüfer","nur","nurcan","oya","özge","özlem","pelin","reyhan","sema",
    "senem","serap","serpil","sevgi","sevil","sevtap","seyhan","sinem","songül",
    "tuba","tuğçe","tülay","tülin","ülkü","yasemin","yeliz","yıldız","zerrin",
    "aslıhan","esma","nurdan","sıla","ferda","handan","gülsüm","gülşen",
    "şeyma","şebnem","ayda","ayça","ayla","aslıhan","aysel","ayten","ayşegül",
    "bahar","banu","beste","beyza","binnaz","cemile","ceyda","cevahir","çiğdem",
    "dudu","dürdane","ebrar","emel","emine","ezel","fadime","ferda","feride",
    "feryal","figen","funda","gizem","gülbin","gönül","gözde","gülnur","günay",
    "hanife","hülya","ilknur","inci","ipek","jale","kıvılcım","lale","leman",
    "mediha","melahat","meral","mualla","müjde","müjgan","müşerref","nadide",
    "nalan","nazlı","nefise","neşe","neval","nevin","nigar","nihal","nuray",
    "perihan","pervin","rana","saadet","sare","selen","selma","semra","sertap",
    "sevda","sevim","sevinç","sezen","şükran","şükriye","ümran","yaprak","zehra",
    "zeliha","ezgisu","asuman","gönül","handan","gülsüm","hülya",
}

TR_MALE = {
    "ahmet","mehmet","mustafa","ali","hasan","hüseyin","ibrahim","ismail","osman",
    "ömer","yusuf","salih","talat","hakan","murat","bülent","cem","emre","erdem",
    "erhan","erkan","ferhat","gökhan","halil","kemal","levent","mert","mesut",
    "metin","muhammed","nurettin","onur","orhan","ozan","recep","selim","selçuk",
    "serdar","serkan","şahin","şenol","tamer","tarık","taylan","tayfun","tuncer",
    "turgut","uğur","ufuk","ümit","yalçın","yaşar","zafer","volkan","barış",
    "burak","caner","doğan","devrim","eren","görkem","halit","ihsan","kerem",
    "koray","korhan","mahmut","necip","polat","ramazan","safa","samet","sedat",
    "sefa","tolga","tufan","veli","okan","okay","yavuz","rasim","yıldırım",
    "yiğit","ercan","ertan","engin","erdoğan","fikret","haluk","kadir","kazım",
    "berk","can","fatih","feyzi","gökay","güray","gürkan","ilker","ismet","kaan",
    "kayhan","kürşat","mahir","ömür","raşit","remzi","rıdvan","rıza","sefer",
    "şükrü","tahir","teoman","yakup","yalın","yıldırım","zekeriya","doruk",
    "kuzey","kıvanç","berkay","kerim","umut","burhan","celal","ender","ertuğrul",
    "evren","fadıl","ferdi","fethi","fuat","gencer","gökhan","gültekin","haldun",
    "harun","hayati","hıdır","hilmi","hüsamettin","kemalettin","kenan","macit",
    "mehdi","mete","mithat","muharrem","muzaffer","müfit","naci","nazmi","nedim",
    "okay","rıfat","saim","sait","saner","savaş","selami","semih","sertaç","seyit",
    "soner","süleyman","tarcan","tekin","temel","timur","tuğrul","tuncay","tunç",
    "turhan","ünal","vahit","vedat","veysel","yetkin","ziya",
}


# Foto dosya adı → cinsiyet (manuel, kapsamlı sınıflandırma)
# Anahtar: filename'in '-' veya '_' ile bölündüğünde ilk parça (lowercased)
# Bilinmeyen / stüdyo / belirsiz → "U"
PHOTO_GENDER = {
    # Female (kadın)
    "aatik": "F", "aiony": "F", "anastasia": "F", "batel": "F", "christina": "F",
    "diana": "F", "fleur": "F", "irene": "F", "jessica": "F", "leilani": "F",
    "nora": "F", "nour": "F", "rachel": "F", "rita": "F", "sarah": "F",
    "ulla": "F", "vicky": "F", "roth": "F",  # roth-melinda is female
    "good": "F",  # good-faces var ama belirsiz; havuza eklemek için F atadım
    # Male (erkek)
    "abdul": "M", "abdullah": "M", "albert": "M", "alex": "M", "ali": "M",
    "alef": "M", "almos": "M", "andrey": "M", "aurelien": "M", "austin": "M",
    "behrouz": "M", "ben": "M", "bishesh": "M", "carlos": "M", "cesar": "M",
    "charles": "M", "charlesdeluvio": "M", "christian": "M", "christopher": "M",
    "connor": "M", "craig": "M", "dane": "M", "daniel": "M", "daniil": "M",
    "darshan": "M", "derick": "M", "diego": "M", "dorrell": "M", "dragos": "M",
    "ehsan": "M", "elizeu": "M", "erik": "M", "esref": "M", "ethan": "M",
    "filipp": "M", "francesco": "M", "fred": "M", "gabriel": "M", "gift": "M",
    "harps": "M", "houcine": "M", "humphrey": "M", "ian": "M", "imansyah": "M",
    "jack": "M", "jake": "M", "jassir": "M", "jeremie": "M", "jimmy": "M",
    "joe": "M", "jonas": "M", "jorik": "M", "joseph": "M", "juri": "M",
    "jurica": "M", "karsten": "M", "kirill": "M", "lance": "M", "laurence": "M",
    "ludovic": "M", "ludvig": "M", "mario": "M", "mason": "M", "mathias": "M",
    "michael": "M", "midas": "M", "mohammad": "M", "morten": "M", "mostafa": "M",
    "naim": "M", "nartan": "M", "nenad": "M", "nicolas": "M", "omid": "M",
    "ospan": "M", "paul": "M", "petr": "M", "philip": "M", "raphael": "M",
    "robert": "M", "ryan": "M", "samuel": "M", "sander": "M", "sergio": "M",
    "slav": "M", "stefan": "M", "thierry": "M", "usman": "M", "vince": "M",
    "wassim": "M", "wellington": "M", "yogendra": "M", "zahir": "M",
    "zulmaury": "M", "prince": "M", "taylor": "M",
    # Belirsiz / stüdyo (havuzdan otomatik dağıtım için U)
    "bailey": "U", "compagnons": "U", "ha": "U", "linkedin": "U", "nonsap": "U",
    "nrd": "U", "podmatch": "U", "the": "U",
}


def normalize(s: str) -> str:
    s = s.strip().lower()
    s = s.replace("ı","i").replace("İ","i").replace("ğ","g").replace("ş","s")
    s = s.replace("ç","c").replace("ö","o").replace("ü","u")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if not unicodedata.combining(c))
    return s


def tr_gender(first_name: str) -> str:
    n = first_name.strip().lower()
    if n in TR_FEMALE: return "F"
    if n in TR_MALE: return "M"
    nn = normalize(first_name)
    if nn in {normalize(x) for x in TR_FEMALE}: return "F"
    if nn in {normalize(x) for x in TR_MALE}: return "M"
    return "U"


def photo_first(filename: str) -> str:
    stem = Path(filename).stem
    return re.split(r"[-_\s.]+", stem)[0].lower()


def main():
    apply_mode = "--apply" in sys.argv

    # Kullanıcılar
    users = []
    with USERS_FILE.open(encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) >= 3 and parts[0].isdigit() and parts[1].lower() != "tomofil":
                users.append((int(parts[0]), parts[1].strip(), parts[2].strip()))
    users.sort(key=lambda u: (u[1], u[2]))

    user_f, user_m, user_u = [], [], []
    for u in users:
        g = tr_gender(u[1])
        (user_f if g == "F" else user_m if g == "M" else user_u).append(u)

    # Fotolar
    photo_f, photo_m, photo_u = [], [], []
    skip = []
    for p in sorted(PHOTOS_DIR.iterdir()):
        if not p.is_file() or p.suffix.lower() not in {".jpg",".jpeg",".png",".webp"}:
            continue
        # Zaten Türkçe adlı (Talat Konuk.jpg gibi) atla
        if re.match(r"^[A-ZĞÜŞİÖÇ][a-zğüşıöç]+\s[A-ZĞÜŞİÖÇ]", p.stem):
            skip.append(p.name); continue
        first = photo_first(p.name)
        g = PHOTO_GENDER.get(first, "U")
        (photo_f if g == "F" else photo_m if g == "M" else photo_u).append(p)

    print(f"\n=== Kullanıcılar ({len(users)}) ===")
    print(f"  K: {len(user_f)}  E: {len(user_m)}  Belirsiz: {len(user_u)} {[u[1] for u in user_u]}")
    print(f"\n=== Fotoğraflar ({len(photo_f)+len(photo_m)+len(photo_u)}) ===")
    print(f"  K: {len(photo_f)}  E: {len(photo_m)}  Belirsiz: {len(photo_u)}  Atlanan: {len(skip)}")

    # Belirsiz fotoları eksiğe dağıt
    pu = list(photo_u)
    need_f = max(0, len(user_f) - len(photo_f))
    need_m = max(0, len(user_m) - len(photo_m))
    # Sıraya: önce ihtiyaca göre, sonra kalan
    moved_to_f = 0
    while need_f > 0 and pu:
        photo_f.append(pu.pop(0)); need_f -= 1; moved_to_f += 1
    moved_to_m = 0
    while need_m > 0 and pu:
        photo_m.append(pu.pop(0)); need_m -= 1; moved_to_m += 1
    print(f"  Belirsizden K havuzuna: {moved_to_f}, E havuzuna: {moved_to_m}, Kalan: {len(pu)}")

    # Eşleştir
    assignments = []
    overflow = []
    for pool_u, pool_p in [(user_m, photo_m), (user_f, photo_f)]:
        for uid, first, last in pool_u:
            if pool_p:
                src = pool_p.pop(0)
                assignments.append((uid, first, last, src, f"{first} {last}{src.suffix.lower()}"))
            else:
                overflow.append((uid, first, last))

    # Belirsiz kullanıcılar için kalan tüm fotolar
    leftover = photo_m + photo_f + pu
    for uid, first, last in user_u:
        if leftover:
            src = leftover.pop(0)
            assignments.append((uid, first, last, src, f"{first} {last}{src.suffix.lower()}"))
        else:
            overflow.append((uid, first, last))

    print(f"\n=== Eşleştirme ===")
    print(f"  Eşleşen: {len(assignments)}  Foto yetersiz: {len(overflow)}  Kalan foto: {len(leftover)}")
    if overflow:
        print(f"  Foto eksik: {[(o[1],o[2]) for o in overflow]}")

    if not apply_mode:
        print("\n--- Önizleme (ilk 20) ---")
        for uid, f, l, src, new in assignments[:20]:
            print(f"  {src.name}  →  {new}")
        print(f"\n... ({len(assignments)} toplam) ...\n--apply ile yeniden adlandır")
        return

    # Apply
    rename_log = ROOT / "data" / "tomofil_photo_rename_log.csv"
    rename_log.parent.mkdir(parents=True, exist_ok=True)
    with rename_log.open("w", encoding="utf-8") as f:
        f.write("user_id,first,last,original,new\n")
        for uid, first, last, src, new in assignments:
            dst = src.parent / new
            base, ext = dst.stem, dst.suffix
            i = 1
            while dst.exists() and dst.name != src.name:
                dst = src.parent / f"{base} ({i}){ext}"
                i += 1
            shutil.move(str(src), str(dst))
            f.write(f"{uid},{first},{last},{src.name},{dst.name}\n")
    print(f"\n✓ {len(assignments)} dosya rename edildi. Log: {rename_log}")


if __name__ == "__main__":
    main()
