# -*- coding: utf-8 -*-
"""Yedekleme servisi — rotasyon, arşiv kapsamı, hata dayanıklılığı.

Bu servis %0 kapsamdaydı ama YIKICI iş yapıyor: eski yedekleri siler
(`_rotate`) ve DB'yi geri yükler (`restore_db`). Yedek kaybı sessiz olur —
fark edildiğinde geri dönüş noktası çoktan gitmiştir.

pg_dump/pg_restore çağrıları gerçek binary ister; testler subprocess'i
taklit eder (mock). Amaç servisin KENDİ mantığını doğrulamak: hangi dosya
silinir, hangi dosya arşive girer, hata olunca ne olur.
"""
import os
import time

import pytest

from app.services import yedekleme_service as ys


# ─── Rotasyon: yedek SİLEN kod ───────────────────────────────────────────────

def _dosya_yaz(dirpath, ad, mtime_offset=0):
    p = os.path.join(dirpath, ad)
    with open(p, "w", encoding="utf-8") as f:
        f.write("x")
    if mtime_offset:
        t = time.time() + mtime_offset
        os.utime(p, (t, t))
    return p


def test_rotate_en_yeni_n_dosyayi_korur(tmp_path):
    """keep=3 → en yeni 3 kalır, eskiler silinir."""
    d = str(tmp_path)
    for i in range(6):
        _dosya_yaz(d, f"db_{i}.dump", mtime_offset=-i * 100)  # 0 en yeni

    silinen = ys._rotate(d, "db_*.dump", keep=3)

    kalan = sorted(os.listdir(d))
    assert silinen == 3
    assert kalan == ["db_0.dump", "db_1.dump", "db_2.dump"], (
        f"En yeni 3 dosya kalmalıydı, kalan: {kalan}"
    )


def test_rotate_esik_altinda_hicbir_seyi_silmez(tmp_path):
    """Dosya sayısı keep'ten azsa hiçbir şey silinmemeli (veri kaybı yok)."""
    d = str(tmp_path)
    for i in range(3):
        _dosya_yaz(d, f"db_{i}.dump", mtime_offset=-i * 100)

    silinen = ys._rotate(d, "db_*.dump", keep=14)

    assert silinen == 0
    assert len(os.listdir(d)) == 3


def test_rotate_yalnizca_desene_uyani_siler(tmp_path):
    """Desen izolasyonu: db_*.dump rotasyonu kod arşivlerine DOKUNMAMALI."""
    d = str(tmp_path)
    for i in range(4):
        _dosya_yaz(d, f"db_{i}.dump", mtime_offset=-i * 100)
    for i in range(4):
        _dosya_yaz(d, f"code_tam_{i}.tar.gz", mtime_offset=-i * 100)

    ys._rotate(d, "db_*.dump", keep=1)

    kalanlar = os.listdir(d)
    assert len([f for f in kalanlar if f.startswith("db_")]) == 1
    assert len([f for f in kalanlar if f.startswith("code_tam_")]) == 4, (
        "Kod arşivleri DB rotasyonundan etkilenmemeli"
    )


# ─── Arşiv kapsamı: neyi yedekler, neyi dışlar ───────────────────────────────

def test_iter_code_files_gurultu_dizinlerini_dislar(tmp_path):
    """.git/__pycache__/node_modules arşive girmemeli."""
    root = tmp_path
    (root / "app.py").write_text("kod", encoding="utf-8")
    for kotu in (".git", "__pycache__", "node_modules", ".venv"):
        d = root / kotu
        d.mkdir()
        (d / "dosya.txt").write_text("x", encoding="utf-8")

    rels = {rel for rel, _full in ys._iter_code_files(str(root), None)}

    assert "app.py" in rels
    for kotu in (".git", "__pycache__", "node_modules", ".venv"):
        assert not any(r.startswith(kotu) for r in rels), f"{kotu} dışlanmalıydı"


def test_iter_code_files_yedek_icinde_yedek_almaz(tmp_path):
    """instance/yedekler arşive girmemeli (backup-of-backup şişmesi)."""
    root = tmp_path
    (root / "app.py").write_text("kod", encoding="utf-8")
    yd = root / "instance" / "yedekler"
    yd.mkdir(parents=True)
    (yd / "db_eski.dump").write_text("kocaman", encoding="utf-8")
    up = root / "instance" / "uploads"
    up.mkdir(parents=True)
    (up / "kullanici.png").write_text("resim", encoding="utf-8")

    rels = {rel for rel, _full in ys._iter_code_files(str(root), None)}

    assert not any("yedekler" in r for r in rels), "yedekler/ arşive girmemeli"
    assert "instance/uploads/kullanici.png" in rels, "uploads/ yedeklenmeli (kullanıcı verisi)"


def test_iter_code_files_pyc_dislar(tmp_path):
    root = tmp_path
    (root / "app.py").write_text("kod", encoding="utf-8")
    (root / "app.pyc").write_text("derlenmis", encoding="utf-8")

    rels = {rel for rel, _full in ys._iter_code_files(str(root), None)}

    assert "app.py" in rels
    assert "app.pyc" not in rels


def test_iter_code_files_fark_modu_yalniz_yenileri_alir(tmp_path):
    """baseline_mtime verilirse yalnız sonradan değişenler (fark yedeği)."""
    root = tmp_path
    eski = root / "eski.py"
    eski.write_text("x", encoding="utf-8")
    baseline = time.time()
    os.utime(str(eski), (baseline - 500, baseline - 500))

    yeni = root / "yeni.py"
    yeni.write_text("x", encoding="utf-8")
    os.utime(str(yeni), (baseline + 500, baseline + 500))

    rels = {rel for rel, _full in ys._iter_code_files(str(root), baseline)}

    assert "yeni.py" in rels
    assert "eski.py" not in rels


def test_make_code_archive_gercek_tar_uretir(tmp_path):
    """Arşiv gerçekten okunabilir tar.gz olmalı (bozuk yedek = yedek yok)."""
    import tarfile
    root = tmp_path / "repo"
    root.mkdir()
    (root / "a.py").write_text("icerik", encoding="utf-8")
    out = str(tmp_path / "cikti.tar.gz")

    ys._repo_root_orig = ys._repo_root
    try:
        ys._repo_root = lambda: str(root)
        size, cnt = ys.make_code_archive(out, None)
    finally:
        ys._repo_root = ys._repo_root_orig

    assert cnt == 1 and size > 0
    with tarfile.open(out, "r:gz") as t:
        assert t.getnames() == ["a.py"]


# ─── Bağlantı ayrıştırma ─────────────────────────────────────────────────────

def test_db_conn_postgres_olmayan_uriyi_reddeder(app):
    """SQLite URI ile yedek almaya çalışmak sessizce boş dosya üretmemeli."""
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
    with pytest.raises(RuntimeError, match="PostgreSQL"):
        ys._db_conn(app)


def test_db_conn_sifreyi_env_e_koyar_uriden_ayristirir(app):
    """Parola PGPASSWORD ile geçilmeli (komut satırında görünmemeli)."""
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "postgresql://kullanici:gizli%40123@sunucu:5433/veritabani"
    )
    conn, env = ys._db_conn(app)

    assert conn == {"host": "sunucu", "port": "5433", "user": "kullanici", "dbname": "veritabani"}
    assert env["PGPASSWORD"] == "gizli@123", "URL-encoded parola çözülmeli"


# ─── Hata dayanıklılığı ──────────────────────────────────────────────────────

def test_dump_db_pg_dump_hatasini_yutmaz(app, monkeypatch):
    """pg_dump patlarsa RuntimeError yükselmeli — sessiz başarısızlık = yedek yok."""
    app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://u:p@h:5432/d"

    class _Sonuc:
        returncode = 1
        stderr = "connection refused"
        stdout = ""

    monkeypatch.setattr(ys.subprocess, "run", lambda *a, **k: _Sonuc())
    with pytest.raises(RuntimeError, match="pg_dump"):
        ys.dump_db(app, "/tmp/olmayan.dump")


def test_run_auto_backup_db_patlasa_da_kod_yedegini_alir(app, monkeypatch, tmp_path):
    """DB yedeği başarısızsa iş durmamalı: kod yedeği yine alınmalı, hata raporlanmalı."""
    monkeypatch.setattr(ys, "auto_dir", lambda _app: str(tmp_path))
    monkeypatch.setattr(ys, "_state_path", lambda _app: str(tmp_path / "_state.json"))

    def _patla(*a, **k):
        raise RuntimeError("pg_dump yok")

    def _sahte_arsiv(path, _baseline):
        with open(path, "w", encoding="utf-8") as f:
            f.write("arsiv")
        return 5, 5  # (boyut, dosya_sayisi)

    monkeypatch.setattr(ys, "dump_db", _patla)
    monkeypatch.setattr(ys, "make_code_archive", _sahte_arsiv)

    sonuc = ys.run_auto_backup(app)

    assert sonuc["db"] is None, "DB yedeği alınamamalıydı"
    assert any("DB:" in e for e in sonuc["errors"]), "DB hatası raporlanmalı"
    assert sonuc["code"] is not None, "DB patlasa bile kod yedeği alınmalı"
