"""PDF export utility testleri."""
import pytest

from app.utils.pdf_export import make_pdf, kvp_table


def test_pdf_basic_render():
    pdf = make_pdf(
        title="Test Raporu",
        sections=[
            {"heading": "Bölüm 1", "body": "Bu bir test."},
        ],
    )
    assert isinstance(pdf, bytes)
    assert pdf.startswith(b"%PDF-")
    assert len(pdf) > 1000


def test_pdf_with_tenant_and_footer():
    pdf = make_pdf(
        title="Stratejik Plan",
        sections=[{"heading": "Vizyon", "body": "2030 hedefi"}],
        tenant_name="Tomofil Otomotiv A.Ş.",
        footer="Sayfa 1 / 1",
    )
    assert pdf.startswith(b"%PDF-")


def test_pdf_with_table():
    rows = kvp_table([("Süreç", 14), ("KPI", 50), ("Çalışan", 100)])
    pdf = make_pdf(
        title="Özet",
        sections=[{"heading": "Genel", "table": rows}],
    )
    assert pdf.startswith(b"%PDF-")


def test_pdf_multipage():
    """Çoklu sayfa için page_break flag'i."""
    pdf = make_pdf(
        title="Çoklu Bölüm",
        sections=[
            {"heading": "Bölüm 1", "body": "İçerik 1", "page_break": True},
            {"heading": "Bölüm 2", "body": "İçerik 2"},
        ],
    )
    assert pdf.startswith(b"%PDF-")


def test_pdf_turkish_chars():
    """Türkçe karakter test'i — font sorunsuz olmalı."""
    pdf = make_pdf(
        title="Türkçe Başlık ŞİĞÜÇÖŞ",
        sections=[{"heading": "İçerik", "body": "Ğümüş, çamlıçevre, ışık."}],
    )
    assert pdf.startswith(b"%PDF-")


def test_kvp_table_format():
    rows = kvp_table([("A", 1), ("B", "text")])
    assert rows[0] == ["Alan", "Değer"]
    assert rows[1] == ["A", "1"]
    assert rows[2] == ["B", "text"]


def test_empty_sections_ok():
    """Section listesi boş olsa bile PDF üretilmeli."""
    pdf = make_pdf(title="Boş", sections=[])
    assert pdf.startswith(b"%PDF-")
