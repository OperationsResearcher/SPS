# -*- coding: utf-8 -*-
"""TEK KURUMUN TÜM VERİSİ: envanter ve iki veritabanı arasında satır satır kıyas (YALNIZ YEREL DB'ler).

AMAÇ: Yayın'daki kritik kurum verisi (ör. KMF) deploy ÖNCESİ yerele yedeklenir (pg_dump -> ayrı yerel DB),
deploy SONRASI aynı yöntemle tekrar çekilir ve bu araç iki kopyayı karşılaştırır: kayıp / değişen / eklenen satır.

NASIL "KURUMUN VERİSİ" BULUNUR (tablo listesi YOK, bilerek — bkz. docs/VERI-CEKME-YAYIN-YEREL.md):
  1. Tohum: `tenants.id`; `tenant_id` kolonu olan her tablo; `tenants`'a FK veren her kolon.
  2. Kapanım: sahibi bilinen satırlara FK ile bağlı çocuk satırlar, sabit noktaya kadar tekrar (aşağı yön;
     ebeveyne/global kataloğa YUKARI yayılmaz). `kpi_data` gibi tenant_id'siz tablolar böyle yakalanır.
  3. Emniyet ağı: FK'siz `*_id` kolonları (ör. `kpi_data_audits.kpi_data_id`) sahibi bilinen satırı
     gösteriyorsa UYARI olarak listelenir — şema FK tanımlamamış olabilir, kapsam dışı kalmasın.

GÜVENLİK: yalnız localhost'a bağlanır (Yayın'a doğrudan bağlantı YOK; Yayın'dan yalnız salt-okunur pg_dump gelir).
Kapanım TEMP tablolarla hesaplanır (oturum bitince kaybolur); hiçbir kalıcı yazma yoktur.

Kullanım:
    python scripts/ops/kurum_veri_kiyas.py envanter kokpitim_yayin_oncesi --kurum KMF
    python scripts/ops/kurum_veri_kiyas.py kiyas kokpitim_yayin_oncesi kokpitim_yayin_sonrasi --kurum KMF
Çıkış kodu: 0 = kayıp yok, 2 = KAYIP satır var, 3 = beklenmeyen kapsam sorunu (kurum bulunamadı vb.)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.parse
from collections import defaultdict
from pathlib import Path

import psycopg2
import psycopg2.extras

ROOT = Path(__file__).resolve().parents[2]
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Migration'ların BİLEREK değiştirdiği (tablo, kolon) çiftleri: bu farklar "beklenen" sayılır, listelenir ama
# alarm vermez. Buraya YENİ bir şey eklemek için migration'da gerekçe olmalı (ör. docs/kontrol/YAYIN-HAZIRLIK-*.md).
BEKLENEN_KOLON_DEGISIMI = {
    ("kpi_data", "user_id"): "e9669: yetim user_id NULL'a çekilir (ölçüm korunur)",
    ("kpi_data", "period_type"): "e9669: period_type normalize",
    ("individual_performance_indicators", "is_active"): "ux01: mükerrer aktif bireysel PG pasifleşir",
    ("individual_performance_indicators", "plan_year_id"): "bi01: bireysel PG yılı kaynak süreç PG'sine hizalanır",
    ("risk_heatmap_items", "source_type"): "b7d3: elle girilmiş risklerin kaynak eşlemesi",
    ("risk_heatmap_items", "project_id"): "hd01: project_id backfill",
    # Yıl bazlı veri geçişi (yilbazli_faz1_2/1_4/1_5; docs/yilbazli/): KMF gibi yılsız kurumlar için
    ("kpi_data", "process_kpi_id"): "Faz 1.5: ölçüm yılın PG kopyasına yeniden bağlanır (kayıp değil)",
    ("plan_years", "template_source_id"): "Faz 1.2: clone zinciri şablon yılını işaretler",
    ("process_kpis", "is_included"): "Faz 1.4: kpi_year_configs.is_included=false varlığa taşınır (K15)",
}
# plan_year_id backfill'i (a1f2/yb16) birçok tabloda NULL -> değer; herhangi bir tabloda beklenen:
BEKLENEN_HER_TABLODA = {"plan_year_id": "yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı", "updated_at": "zaman damgası"}


def dsn_for(dbname: str) -> dict:
    uri = ""
    for line in (ROOT / ".env").read_text(encoding="utf-8").splitlines():
        if line.startswith("SQLALCHEMY_DATABASE_URI="):
            uri = line.split("=", 1)[1].strip().strip("\"'")
    u = urllib.parse.urlparse(uri.replace("postgresql+psycopg2", "postgresql"))
    if u.hostname not in ("localhost", "127.0.0.1", "::1"):
        raise SystemExit(f"Yalnız yerel DB'ler (host={u.hostname}). Yayın'a doğrudan bağlanılmaz.")
    return dict(host=u.hostname, port=u.port or 5432, user=u.username,
                password=urllib.parse.unquote(u.password or ""), dbname=dbname)


def baglan(dbname: str):
    c = psycopg2.connect(**dsn_for(dbname))
    c.autocommit = False
    return c


def tenant_bul(cur, kurum: str, tenant_id: int | None):
    if tenant_id:
        cur.execute("select id, name, short_name from tenants where id=%s", (tenant_id,))
    else:
        cur.execute("select id, name, short_name from tenants where upper(short_name)=upper(%s) or name ilike %s order by id",
                    (kurum, f"%{kurum}%"))
    rows = cur.fetchall()
    if len(rows) != 1:
        raise SystemExit(f"Kurum '{kurum}' bulunamadı/çoklu eşleşme: {rows}")
    return rows[0]


def introspect(cur):
    cur.execute("select table_name from information_schema.tables where table_schema='public' and table_type='BASE TABLE' order by 1")
    tablolar = [r[0] for r in cur.fetchall()]
    cur.execute("select table_name, column_name, data_type from information_schema.columns where table_schema='public' order by table_name, ordinal_position")
    kolonlar = defaultdict(list)
    for t, c, dt in cur.fetchall():
        kolonlar[t].append((c, dt))
    cur.execute("""
        SELECT cl.relname, array_agg(a.attname ORDER BY k.ord)
          FROM pg_constraint c JOIN pg_class cl ON cl.oid=c.conrelid JOIN pg_namespace n ON n.oid=cl.relnamespace
          CROSS JOIN LATERAL unnest(c.conkey) WITH ORDINALITY k(attnum, ord)
          JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum
         WHERE c.contype='p' AND n.nspname='public' GROUP BY cl.relname, c.oid""")
    pk = {r[0]: list(r[1]) for r in cur.fetchall()}
    cur.execute("""
        SELECT cl.relname, pl.relname,
          (SELECT array_agg(a.attname ORDER BY k.ord) FROM unnest(c.conkey) WITH ORDINALITY k(attnum, ord)
             JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.attnum),
          (SELECT array_agg(a.attname ORDER BY k.ord) FROM unnest(c.confkey) WITH ORDINALITY k(attnum, ord)
             JOIN pg_attribute a ON a.attrelid=c.confrelid AND a.attnum=k.attnum)
          FROM pg_constraint c JOIN pg_class cl ON cl.oid=c.conrelid JOIN pg_class pl ON pl.oid=c.confrelid
          JOIN pg_namespace n ON n.oid=cl.relnamespace WHERE c.contype='f' AND n.nspname='public'""")
    fks = [(a, b, list(c), list(d)) for a, b, c, d in cur.fetchall()]
    return tablolar, kolonlar, pk, fks


def kapanim(cur, T: int, tablolar, kolonlar, fks):
    """Kurumun sahip olduğu satırların ctid'lerini TEMP tablolara yazar; {tablo: sayı} döndürür."""
    ad = {t: f"_o_{i}" for i, t in enumerate(tablolar)}
    for t in tablolar:
        cur.execute(f'create temp table {ad[t]} (t tid)')
    # tohum
    for t in tablolar:
        kolon_adlari = [c for c, _ in kolonlar[t]]
        kosullar = []
        if t == "tenants":
            kosullar.append(("id", T))
        if "tenant_id" in kolon_adlari:
            kosullar.append(("tenant_id", T))
        for child, parent, ccols, _ in fks:
            if child == t and parent == "tenants" and len(ccols) == 1 and ccols[0] != "tenant_id":
                kosullar.append((ccols[0], T))
        for col, val in kosullar:
            cur.execute(f'insert into {ad[t]} select ctid from "{t}" x where "{col}"=%s and not exists (select 1 from {ad[t]} o where o.t=x.ctid)', (val,))
    # sabit nokta
    sayi = lambda t: (cur.execute(f"select count(*) from {ad[t]}"), cur.fetchone()[0])[1]
    for _ in range(40):
        degisti = False
        for child, parent, ccols, pcols in fks:
            if sayi(parent) == 0:
                continue
            kosul = " and ".join(f'c."{a}" = p."{b}"' for a, b in zip(ccols, pcols))
            cur.execute(
                f'insert into {ad[child]} select distinct c.ctid from "{child}" c join "{parent}" p on {kosul} '
                f'join {ad[parent]} op on op.t = p.ctid where not exists (select 1 from {ad[child]} x where x.t = c.ctid)')
            if cur.rowcount:
                degisti = True
        if not degisti:
            break
    return ad, {t: sayi(t) for t in tablolar}


def fksiz_baglantilar(cur, ad, sayilar, tablolar, kolonlar, pk, fks):
    """Emniyet ağı: FK'siz *_id kolonu sahip olunan satırı gösteriyor ama satır kapanımda yoksa uyar."""
    fk_kolonlari = {(c, col) for c, _, cc, _ in fks for col in cc}
    uyarilar = []
    for t in tablolar:
        for col, dt in kolonlar[t]:
            if dt not in ("integer", "bigint", "smallint") or not col.endswith("_id") or (t, col) in fk_kolonlari:
                continue
            taban = col[:-3]
            adaylar = {taban, taban + "s", taban + "es", re.sub(r"y$", "ies", taban)}
            for p in adaylar:
                if p in ad and sayilar.get(p, 0) > 0 and pk.get(p) == ["id"]:
                    cur.execute(
                        f'select count(*) from "{t}" x where x."{col}" in (select pp.id from "{p}" pp join {ad[p]} o on o.t = pp.ctid) '
                        f'and not exists (select 1 from {ad[t]} o2 where o2.t = x.ctid)')
                    n = cur.fetchone()[0]
                    if n:
                        # Kapsam dışı kalmasın: bu satırlar da kuruma ait sayılır (emniyet ağı), ayrıca raporlanır.
                        cur.execute(
                            f'insert into {ad[t]} select x.ctid from "{t}" x where x."{col}" in '
                            f'(select pp.id from "{p}" pp join {ad[p]} o on o.t = pp.ctid) '
                            f'and not exists (select 1 from {ad[t]} o2 where o2.t = x.ctid)')
                        uyarilar.append({"tablo": t, "kolon": col, "ebeveyn": p, "satir": n})
    return uyarilar


def satirlari_al(cur, t, ad, kolonlar, pk, hizli=False):
    kol = [c for c, _ in kolonlar[t]]
    if hizli:  # yalnız anahtar kümesi (değer kıyası yok): büyük kurumlar için
        pkc = pk.get(t)
        if pkc:
            cur.execute(f'select {", ".join(chr(34)+c+chr(34)+"::text" for c in pkc)} from "{t}" x join {ad[t]} o on o.t = x.ctid')
            return {"|".join(str(v) for v in r): {} for r in cur.fetchall()}
        cur.execute(f'select md5(x::text) from "{t}" x join {ad[t]} o on o.t = x.ctid')
        return {"ROW:" + r[0] + f"#{i}": {} for i, r in enumerate(sorted(cur.fetchall()))}
    cur.execute(f'select {", ".join(chr(34)+c+chr(34)+"::text" for c in kol)} from "{t}" x join {ad[t]} o on o.t = x.ctid')
    rows = cur.fetchall()
    sonuc = {}
    pkc = pk.get(t)
    for r in rows:
        d = dict(zip(kol, r))
        anahtar = "|".join(str(d[c]) for c in pkc) if pkc else "ROW:" + "|".join("" if v is None else v for v in r)
        sonuc[anahtar] = d
    return sonuc


def tara(dbname, kurum, tenant_id, satir_al=False, hizli=False):
    conn = baglan(dbname)
    cur = conn.cursor()
    T, tad, tkisa = tenant_bul(cur, kurum, tenant_id)
    tablolar, kolonlar, pk, fks = introspect(cur)
    ad, sayilar = kapanim(cur, T, tablolar, kolonlar, fks)
    uyar = fksiz_baglantilar(cur, ad, sayilar, tablolar, kolonlar, pk, fks)
    for t in tablolar:  # FK'siz eklemeler sonrası güncel sayılar
        cur.execute(f"select count(*) from {ad[t]}")
        sayilar[t] = cur.fetchone()[0]
    veri = {}
    if satir_al:
        for t in tablolar:
            if sayilar[t]:
                veri[t] = satirlari_al(cur, t, ad, kolonlar, pk, hizli)
    cur.execute("select version_num from alembic_version")
    rev = [r[0] for r in cur.fetchall()]
    conn.rollback()
    conn.close()
    return dict(db=dbname, tenant_id=T, ad=tad, kisa=tkisa, alembic=rev, sayilar={t: n for t, n in sayilar.items() if n},
                kolonlar={t: [c for c, _ in kolonlar[t]] for t in sayilar if sayilar[t]}, pk=pk, uyarilar=uyar, veri=veri,
                toplam_tablo=len(tablolar))


def md_envanter(s):
    satirlar = sorted(s["sayilar"].items(), key=lambda x: -x[1])
    o = [f"## Envanter: {s['ad']} (id={s['tenant_id']}) — DB `{s['db']}` (alembic {', '.join(s['alembic'])})", "",
         f"{len(satirlar)} / {s['toplam_tablo']} tabloda kuruma ait satır var; toplam **{sum(n for _, n in satirlar)}** satır.", "",
         "| Tablo | Satır | PK |", "|---|---:|---|"]
    for t, n in satirlar:
        o.append(f"| `{t}` | {n} | {', '.join(s['pk'].get(t, [])) or '**PK YOK**'} |")
    if s["uyarilar"]:
        o += ["", "### ⚠ FK'siz bağlantılar (şema FK tanımlamamış; bu satırlar emniyet ağıyla kapsama EKLENDİ)", "", "| Tablo.kolon | Ebeveyn | FK'siz eklenen satır |", "|---|---|---:|"]
        for u in s["uyarilar"]:
            o.append(f"| `{u['tablo']}.{u['kolon']}` | `{u['ebeveyn']}` | {u['satir']} |")
    return "\n".join(o)


def kiyasla(a, b):
    """a = ÖNCE, b = SONRA. Kayıp = a'da olup b'de olmayan PK."""
    rapor = {"kayip": {}, "eklenen": {}, "degisen": {}, "beklenen": {}, "yeni_kolon": {}, "sayi": {}}
    for t in sorted(set(a["veri"]) | set(b["veri"])):
        ra, rb = a["veri"].get(t, {}), b["veri"].get(t, {})
        rapor["sayi"][t] = (len(ra), len(rb))
        kayip = [k for k in ra if k not in rb]
        eklenen = [k for k in rb if k not in ra]
        if kayip:
            rapor["kayip"][t] = kayip
        if eklenen:
            rapor["eklenen"][t] = eklenen
        ortak_kol = [c for c in a["kolonlar"].get(t, []) if c in b["kolonlar"].get(t, [])]
        yeni = [c for c in b["kolonlar"].get(t, []) if c not in a["kolonlar"].get(t, [])]
        if yeni:
            rapor["yeni_kolon"][t] = yeni
        fark = defaultdict(list)
        for k in ra:
            if k in rb:
                for c in ortak_kol:
                    if ra[k].get(c) != rb[k].get(c):
                        fark[c].append((k, ra[k].get(c), rb[k].get(c)))
        for c, liste in fark.items():
            sebep = BEKLENEN_KOLON_DEGISIMI.get((t, c)) or BEKLENEN_HER_TABLODA.get(c)
            (rapor["beklenen"] if sebep else rapor["degisen"]).setdefault(t, {})[c] = (len(liste), liste[:3], sebep)
    return rapor


def md_kiyas(a, b, r):
    kayip_toplam = sum(len(v) for v in r["kayip"].values())
    o = [f"# Kıyas: {a['ad']} — ÖNCE `{a['db']}` (alembic {', '.join(a['alembic'])}) ↔ SONRA `{b['db']}` (alembic {', '.join(b['alembic'])})", "",
         f"**SONUÇ: {'✅ KAYIP YOK' if not kayip_toplam else '🔴 KAYIP: ' + str(kayip_toplam) + ' satır'}** — "
         f"toplam satır önce {sum(x for x, _ in r['sayi'].values())} → sonra {sum(y for _, y in r['sayi'].values())}", ""]
    if r["kayip"]:
        o += ["## 🔴 Kayıp satırlar (ÖNCE'de var, SONRA'da yok)", "", "| Tablo | Kayıp | Örnek PK |", "|---|---:|---|"]
        for t, ks in r["kayip"].items():
            o.append(f"| `{t}` | {len(ks)} | {', '.join(ks[:5])} |")
    if r["degisen"]:
        o += ["", "## 🟠 Beklenmeyen değerler değişmiş (İNCELE)", "", "| Tablo.kolon | Satır | Örnek (pk: önce → sonra) |", "|---|---:|---|"]
        for t, cs in r["degisen"].items():
            for c, (n, ornek, _) in cs.items():
                o.append(f"| `{t}.{c}` | {n} | " + "; ".join(f"{k}: {x!r} → {y!r}" for k, x, y in ornek)[:160] + " |")
    if r["eklenen"]:
        o += ["", "## 🟡 Eklenen satırlar (canlı kullanımdan olabilir)", "", "| Tablo | Eklenen |", "|---|---:|"]
        for t, ks in r["eklenen"].items():
            o.append(f"| `{t}` | {len(ks)} |")
    if r["beklenen"]:
        o += ["", "## 🟢 Beklenen (migration kaynaklı) değişimler", "", "| Tablo.kolon | Satır | Sebep |", "|---|---:|---|"]
        for t, cs in r["beklenen"].items():
            for c, (n, _, sebep) in cs.items():
                o.append(f"| `{t}.{c}` | {n} | {sebep} |")
    if r["yeni_kolon"]:
        o += ["", "## ℹ Yeni kolonlar (SONRA'da var)", "", ", ".join(f"`{t}`: {', '.join(c)}" for t, c in r["yeni_kolon"].items())]
    if b["uyarilar"] or a["uyarilar"]:
        o += ["", "## ⚠ FK'siz bağlantı uyarıları (ÖNCE / SONRA)", ""]
        for s in (a, b):
            for u in s["uyarilar"]:
                o.append(f"- `{s['db']}`: `{u['tablo']}.{u['kolon']}` → `{u['ebeveyn']}`: {u['satir']} satır kapanım dışı")
    return "\n".join(o), kayip_toplam


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="komut", required=True)
    e = sp.add_parser("envanter"); e.add_argument("db"); e.add_argument("--kurum", default="KMF"); e.add_argument("--tenant-id", type=int)
    e.add_argument("--out")
    k = sp.add_parser("kiyas"); k.add_argument("once"); k.add_argument("sonra"); k.add_argument("--kurum", default="KMF")
    k.add_argument("--tenant-id", type=int); k.add_argument("--out")
    k.add_argument("--hizli", action="store_true", help="yalnız PK kümesi + satır sayısı (değer kıyası yok; büyük kurumlar)")
    a = ap.parse_args()
    if a.komut == "envanter":
        s = tara(a.db, a.kurum, a.tenant_id)
        m = md_envanter(s)
        print(m)
        if a.out:
            Path(a.out).write_text(m + "\n", encoding="utf-8")
        return 0
    s1 = tara(a.once, a.kurum, a.tenant_id, satir_al=True, hizli=a.hizli)
    s2 = tara(a.sonra, a.kurum, a.tenant_id, satir_al=True, hizli=a.hizli)
    r = kiyasla(s1, s2)
    m, kayip = md_kiyas(s1, s2, r)
    print(m)
    if a.out:
        Path(a.out).write_text(m + "\n", encoding="utf-8")
    return 2 if kayip else 0


if __name__ == "__main__":
    sys.exit(main())
