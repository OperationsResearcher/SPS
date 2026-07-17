"""risk_heatmap_items.source_id + FK + kaynak eşleme (TASK-276, katman Faz 5)

KATMAN MİMARİSİ İLKESİ: "Her risk bir kaynağa bağlı."
Kaynak = GENİŞ tanım {SWOT, PESTEL, süreç, proje} — kurumsal-genel riskler zorla
projeye değil, doğdukları stratejik analize bağlanır.

ÖLÇÜM (2026-07-17) — yol haritasının iddiası DÜZELTİLDİ:
    Plan: "70 manual risk = 35 gerçek × 2 (test kurumu ID kayması)"
    Gerçek: 70 = **5 eşsiz risk × 7 plan yılı × 2 kurum**
      Hammadde Fiyat Artışı · Kur Riski · Anahtar Yetenek Kaybı ·
      Tedarik Zinciri Kesintisi · Teknoloji Geliştirme Gecikmesi
    Hepsi aynı gün (2026-05-26), aynı probability/impact/rpn → seed verisi.
    "35 gerçek risk" diye bir şey yok; eşlenecek 5 tür var.

    Kullanıcı kararı: 5 türü eşle, migration 70 satırı otomatik doldursun.

source_type ZATEN "kaynak" anlamında tasarlanmış — UI seçenekleri bunu doğruluyor
(risk_management.html: manual/process/project/pestel/swot/porter). Tenant 28'in
"Finansal"/"Operasyonel" değerleri bu listede YOK: seed ederken kategori sanılıp
yanlış doldurulmuş. Bu migration onları DÜZELTMEZ — yalnız `manual` olanları
eşler; t28 verisi ayrı karar (bkz. ENDPOINT-SOZLESMESI.md §Faz 5).

Bu migration:
  1. source_id kolonu ekler (nullable — kaynak kaydın PK'si)
  2. 5 risk türünü geniş-kaynağa eşler (source_type='manual' → gerçek kaynak)
  3. source_id'yi FK YAPMAZ — bilinçli, aşağıda gerekçesi

NEDEN source_id'ye FK YOK (yol haritası "source_id + FK ekle" diyordu):
    source_id POLİMORFİKTİR — source_type'a göre farklı tabloyu işaret eder
    (swot → sp_swot_items, pestel → sp_pestel_items, process → processes,
    project → projects). Tek kolona 4 farklı tabloya FK konulamaz; Postgres
    bunu desteklemez. Alternatifler (4 ayrı nullable FK kolonu, ya da ayrı
    bağlantı tablosu) şema kararı gerektirir — bu migration'ın kapsamı değil.
    source_id + source_type çifti uygulama katmanında doğrulanır.

Revision ID: b7d3e1f4a920
Revises: c927a97a2fef
Create Date: 2026-07-17
"""
from alembic import op
import sqlalchemy as sa


revision = "b7d3e1f4a920"
down_revision = "c927a97a2fef"
branch_labels = None
depends_on = None


# 5 seed riskinin geniş-kaynağa eşlemesi (hedef tasarım §Karar 3'teki örneklerle
# birebir: "Kur Riski → PESTEL (Ekonomik)", "Yetenek Kaybı → SWOT (Zayıflık)",
# "Tedarik Kesintisi → süreç").
_ESLEME = [
    ("Kur Riski", "pestel"),                      # Ekonomik dış faktör
    ("Hammadde Fiyat Artışı", "pestel"),          # Ekonomik dış faktör
    ("Anahtar Yetenek Kaybı", "swot"),            # İç zayıflık
    ("Tedarik Zinciri Kesintisi", "process"),     # Süreç riski
    ("Teknoloji Geliştirme Gecikmesi", "project"),  # Proje riski
]


def upgrade():
    # ── 1) source_id kolonu ────────────────────────────────────────────────
    op.add_column(
        "risk_heatmap_items",
        sa.Column("source_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_risk_heatmap_items_source",
        "risk_heatmap_items",
        ["source_type", "source_id"],
    )

    # ── 2) 5 türü geniş-kaynağa eşle ───────────────────────────────────────
    # source_id NULL kalır: seed riskleri somut bir SWOT/PESTEL kaydından
    # doğmadı, tür düzeyinde eşleniyor. Kullanıcı ekranda kaynağı seçince
    # source_id dolar (yeni kayıtlarda zorunlu — routes_risk.py).
    conn = op.get_bind()
    for baslik, kaynak in _ESLEME:
        conn.execute(
            sa.text("""
                UPDATE risk_heatmap_items
                   SET source_type = :kaynak, updated_at = NOW()
                 WHERE source_type = 'manual' AND title = :baslik
            """),
            {"kaynak": kaynak, "baslik": baslik},
        )

    # Eşlemede olmayan 'manual' kalırsa görünür kalsın — sessizce 'other'a
    # itmek veriyi saklar. Kalan varsa sonraki kontrol yakalar.


def downgrade():
    conn = op.get_bind()
    for baslik, kaynak in _ESLEME:
        conn.execute(
            sa.text("""
                UPDATE risk_heatmap_items
                   SET source_type = 'manual', updated_at = NOW()
                 WHERE source_type = :kaynak AND title = :baslik
            """),
            {"kaynak": kaynak, "baslik": baslik},
        )
    op.drop_index("ix_risk_heatmap_items_source", table_name="risk_heatmap_items")
    op.drop_column("risk_heatmap_items", "source_id")
