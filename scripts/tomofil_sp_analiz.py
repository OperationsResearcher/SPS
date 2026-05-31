"""Tomofil (tenant 27) stratejik plan dönemleri arası değişim analizi."""
import sys
sys.path.insert(0, 'c:/kokpitim')
from app import create_app
from extensions import db
from sqlalchemy import text

TENANT_ID = 27
OUT_MD = r"c:\kokpitim\docs\rapor\29mayis_tomofil_sp_analiz.md"

app = create_app()
with app.app_context():
    plan_years = db.session.execute(text("""
        SELECT id, year, name FROM plan_years
        WHERE tenant_id=:t ORDER BY year
    """), {"t": TENANT_ID}).fetchall()

    def fetch_strategies(py_id):
        return {r.code or f"#{r.id}": r.title for r in db.session.execute(text("""
            SELECT id, code, title FROM strategies
            WHERE tenant_id=:t AND plan_year_id=:py AND is_active=true
            ORDER BY code
        """), {"t": TENANT_ID, "py": py_id}).fetchall()}

    def fetch_sub_strategies(py_id):
        return {(r.scode, r.code or f"#{r.id}"): r.title for r in db.session.execute(text("""
            SELECT ss.id, ss.code, ss.title, s.code as scode
            FROM sub_strategies ss
            JOIN strategies s ON s.id = ss.strategy_id
            WHERE s.tenant_id=:t AND s.plan_year_id=:py AND ss.is_active=true
        """), {"t": TENANT_ID, "py": py_id}).fetchall()}

    def fetch_processes(py_id):
        return {r.code or r.name: r.name for r in db.session.execute(text("""
            SELECT id, code, name FROM processes
            WHERE tenant_id=:t AND plan_year_id=:py AND is_active=true
            ORDER BY code
        """), {"t": TENANT_ID, "py": py_id}).fetchall()}

    def fetch_links(py_id):
        return [(r.pcode, r.pname, r.scode, r.sscode, r.contribution_pct) for r in db.session.execute(text("""
            SELECT p.code as pcode, p.name as pname,
                   s.code as scode, ss.code as sscode,
                   psl.contribution_pct
            FROM process_sub_strategy_links psl
            JOIN processes p ON p.id = psl.process_id
            JOIN sub_strategies ss ON ss.id = psl.sub_strategy_id
            JOIN strategies s ON s.id = ss.strategy_id
            WHERE p.tenant_id=:t AND p.plan_year_id=:py AND p.is_active=true
        """), {"t": TENANT_ID, "py": py_id}).fetchall()]

    data = {}
    for py in plan_years:
        data[py.year] = {
            "name": py.name,
            "strategies": fetch_strategies(py.id),
            "sub_strategies": fetch_sub_strategies(py.id),
            "processes": fetch_processes(py.id),
            "links": fetch_links(py.id),
        }

    lines = ["# Tomofil Stratejik Plan Analizi — Yıllar Arası Değişim",
             "",
             f"**Kurum:** Tomofil Otomotiv Sanayi ve Ticaret A.Ş.  ",
             f"**Tarih:** 2026-05-29  ",
             f"**Kapsam:** {min(data)}–{max(data)} stratejik plan dönemleri  ",
             ""]

    # Genel özet tablosu
    lines.append("## 1. Genel Özet")
    lines.append("")
    lines.append("| Yıl | Strateji | Alt Strateji | Süreç | Süreç-AltStrateji Bağı |")
    lines.append("|---|---:|---:|---:|---:|")
    for y in sorted(data):
        d = data[y]
        lines.append(f"| **{y}** | {len(d['strategies'])} | {len(d['sub_strategies'])} | {len(d['processes'])} | {len(d['links'])} |")
    lines.append("")

    # Yıl bazlı strateji isim listesi
    lines.append("## 2. Yıl Bazlı Strateji Başlıkları")
    lines.append("")
    for y in sorted(data):
        d = data[y]
        lines.append(f"### {y} — {d['name']}")
        if not d['strategies']:
            lines.append("_Strateji tanımlı değil._")
        else:
            for code, title in sorted(d['strategies'].items()):
                lines.append(f"- **{code}** — {title}")
        lines.append("")

    # Yıllar arası diff
    lines.append("## 3. Yıllar Arası Değişim (Diff)")
    lines.append("")
    years = sorted(data)
    for i in range(1, len(years)):
        prev_y, cur_y = years[i-1], years[i]
        prev, cur = data[prev_y], data[cur_y]

        s_prev = set(prev['strategies'].keys())
        s_cur = set(cur['strategies'].keys())
        ss_prev = set(prev['sub_strategies'].keys())
        ss_cur = set(cur['sub_strategies'].keys())
        p_prev = set(prev['processes'].keys())
        p_cur = set(cur['processes'].keys())

        lines.append(f"### {prev_y} → {cur_y}")
        lines.append("")
        lines.append(f"**Strateji:** {len(s_prev)} → {len(s_cur)}  ·  "
                     f"eklenen **{len(s_cur - s_prev)}**, çıkarılan **{len(s_prev - s_cur)}**, korunan **{len(s_prev & s_cur)}**")
        added_s = sorted(s_cur - s_prev)
        removed_s = sorted(s_prev - s_cur)
        if added_s:
            lines.append("")
            lines.append("- **Eklenen stratejiler:**")
            for c in added_s:
                lines.append(f"  - `{c}` — {cur['strategies'][c]}")
        if removed_s:
            lines.append("")
            lines.append("- **Çıkarılan stratejiler:**")
            for c in removed_s:
                lines.append(f"  - `{c}` — {prev['strategies'][c]}")
        lines.append("")
        lines.append(f"**Alt Strateji:** {len(ss_prev)} → {len(ss_cur)}  ·  "
                     f"eklenen **{len(ss_cur - ss_prev)}**, çıkarılan **{len(ss_prev - ss_cur)}**")
        added_ss = sorted(ss_cur - ss_prev)
        removed_ss = sorted(ss_prev - ss_cur)
        if added_ss[:10]:
            lines.append("")
            lines.append(f"- **Eklenen alt stratejiler (ilk 10 / toplam {len(added_ss)}):**")
            for k in added_ss[:10]:
                lines.append(f"  - `{k[0]} / {k[1]}` — {cur['sub_strategies'][k]}")
        if removed_ss[:10]:
            lines.append("")
            lines.append(f"- **Çıkarılan alt stratejiler (ilk 10 / toplam {len(removed_ss)}):**")
            for k in removed_ss[:10]:
                lines.append(f"  - `{k[0]} / {k[1]}` — {prev['sub_strategies'][k]}")
        lines.append("")
        lines.append(f"**Süreç:** {len(p_prev)} → {len(p_cur)}  ·  "
                     f"eklenen **{len(p_cur - p_prev)}**, çıkarılan **{len(p_prev - p_cur)}**, korunan **{len(p_prev & p_cur)}**")
        added_p = sorted(p_cur - p_prev)
        removed_p = sorted(p_prev - p_cur)
        if added_p[:15]:
            lines.append("")
            lines.append(f"- **Eklenen süreçler (ilk 15 / toplam {len(added_p)}):**")
            for c in added_p[:15]:
                lines.append(f"  - `{c}` — {cur['processes'][c]}")
        if removed_p[:15]:
            lines.append("")
            lines.append(f"- **Çıkarılan süreçler (ilk 15 / toplam {len(removed_p)}):**")
            for c in removed_p[:15]:
                lines.append(f"  - `{c}` — {prev['processes'][c]}")
        lines.append("")
        lines.append(f"**Süreç-Alt Strateji Bağı:** {len(prev['links'])} → {len(cur['links'])} "
                     f"(net değişim {len(cur['links']) - len(prev['links']):+d})")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Sürekli ve geçici süreç listesi
    lines.append("## 4. Süreç Sürekliliği")
    lines.append("")
    all_year_keys = [set(data[y]['processes'].keys()) for y in years]
    if all_year_keys:
        always = set.intersection(*all_year_keys)
        union = set.union(*all_year_keys)
        once_only = {k for k in union if sum(1 for s in all_year_keys if k in s) == 1}
        lines.append(f"- Tüm {len(years)} yıl boyunca **kesintisiz var olan** süreç sayısı: **{len(always)}**")
        lines.append(f"- Sadece **tek bir yılda** görülen süreç sayısı: **{len(once_only)}**")
        lines.append(f"- Toplam farklı süreç (tüm yıllar birleşimi): **{len(union)}**")
        lines.append("")
        sample_always = sorted(always)[:20]
        if sample_always:
            lines.append(f"**Çekirdek (her yıl korunan) süreçler — örnek {len(sample_always)} adet:**")
            for c in sample_always:
                lines.append(f"- `{c}` — {data[years[-1]]['processes'].get(c) or data[years[0]]['processes'].get(c)}")
            lines.append("")

    # Çıkarımlar
    lines.append("## 5. Stratejik Çıkarımlar")
    lines.append("")
    lines.append("Bu bölüm yıllar arası diff sayılarından otomatik çıkarılan gözlemleri içerir; "
                 "kurum içi yorum gerektirir.")
    lines.append("")
    # En büyük değişim olan yılı bul
    biggest = None
    for i in range(1, len(years)):
        prev_y, cur_y = years[i-1], years[i]
        prev, cur = data[prev_y], data[cur_y]
        diff = (
            len(set(cur['strategies']) - set(prev['strategies'])) +
            len(set(prev['strategies']) - set(cur['strategies'])) +
            len(set(cur['processes']) - set(prev['processes'])) +
            len(set(prev['processes']) - set(cur['processes']))
        )
        if biggest is None or diff > biggest[0]:
            biggest = (diff, prev_y, cur_y)
    if biggest:
        lines.append(f"- En büyük yapısal değişim **{biggest[1]} → {biggest[2]}** geçişinde yaşanmış "
                     f"(toplam {biggest[0]} strateji+süreç eklenmesi/çıkarılması).")
    avg_strat = sum(len(data[y]['strategies']) for y in years) / max(len(years), 1)
    lines.append(f"- Ortalama yıllık strateji sayısı: **{avg_strat:.1f}**")
    avg_proc = sum(len(data[y]['processes']) for y in years) / max(len(years), 1)
    lines.append(f"- Ortalama yıllık süreç sayısı: **{avg_proc:.1f}**")
    lines.append("")
    lines.append("> _Bu rapor otomatik üretildi (`scripts/tomofil_sp_analiz.py`)._")

    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print("MD yazildi:", OUT_MD, "satir:", len(lines))
