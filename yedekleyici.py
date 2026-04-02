"""
Kokpitim Yedekleyici — PostgreSQL + SQLite destekli, dogrulamali yedekleme.

- backup: Tam yedek (kod + DB dump), sonra dogrulama
- restore: Geri yukleme, oncesi/sonrasi kontroller
- verify: Yedek zip icerigini dogrula (restore yapmadan)

PostgreSQL icin pg_dump ve psql PATH'te olmali.
Windows: PostgreSQL kurulumundan bin/ klasorunu PATH'e ekleyin.
"""
import argparse
import datetime
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from urllib.parse import urlparse


EXCLUDE_DIRS = {
    ".venv",
    ".git",
    "__pycache__",
    ".vscode",
    ".idea",
    "Yedekler",
    ".gemini",
    ".tmp",
    "node_modules",
}
EXCLUDE_EXTENSIONS = {".log", ".tmp", ".pyc", ".pyo"}


def resolve_db_uri() -> str:
    from dotenv import load_dotenv

    load_dotenv()
    return os.environ.get("SQLALCHEMY_DATABASE_URI", "").strip()


def is_postgres_uri(uri: str) -> bool:
    u = (uri or "").strip().lower()
    return u.startswith("postgresql://") or u.startswith("postgresql+")


def make_backup_dirs(base_dir: str) -> str:
    backup_dir = os.path.join(base_dir, "Yedekler")
    os.makedirs(backup_dir, exist_ok=True)
    return backup_dir


def _pg_bin(tool: str) -> str:
    """pg_dump/psql yolunu dondur. PG_BIN env, PATH, Windows varsayilan kurulum."""
    exe = tool + (".exe" if os.name == "nt" else "")
    pg_bin = os.environ.get("PG_BIN", "").strip().rstrip("/\\")
    if pg_bin and os.path.isdir(pg_bin):
        full = os.path.join(pg_bin, exe)
        if os.path.isfile(full):
            return full
    which = shutil.which(tool) or shutil.which(exe)
    if which:
        return which
    if os.name == "nt":
        for base in (os.environ.get("ProgramFiles"), os.environ.get("ProgramFiles(x86)")):
            if not base:
                continue
            pg_root = os.path.join(base, "PostgreSQL")
            if not os.path.isdir(pg_root):
                continue
            try:
                versions = sorted(os.listdir(pg_root), reverse=True)
            except OSError:
                continue
            for ver in versions:
                cand = os.path.join(pg_root, ver, "bin", exe)
                if os.path.isfile(cand):
                    return cand
    return tool


def run_pg_dump(db_uri: str, output_sql_path: str, extra_args: list | None = None) -> None:
    parsed = urlparse(db_uri)
    if not parsed.hostname or not parsed.path:
        raise RuntimeError("PostgreSQL URI parse edilemedi.")

    db_name = parsed.path.lstrip("/").split("?")[0]
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    pg_dump_cmd = _pg_bin("pg_dump")
    cmd = [
        pg_dump_cmd,
        "-h",
        parsed.hostname,
        "-p",
        str(parsed.port or 5432),
        "-U",
        parsed.username or "postgres",
        "-d",
        db_name,
        "-F",
        "p",  # plain SQL
    ]
    if extra_args:
        cmd.extend(extra_args)
    cmd.extend(["-f", output_sql_path])
    subprocess.run(cmd, check=True, env=env)


def run_psql_restore(db_uri: str, input_sql_path: str) -> None:
    parsed = urlparse(db_uri)
    if not parsed.hostname or not parsed.path:
        raise RuntimeError("PostgreSQL URI parse edilemedi.")

    db_name = parsed.path.lstrip("/").split("?")[0]
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password

    psql_cmd = _pg_bin("psql")
    cmd = [
        psql_cmd,
        "-h",
        parsed.hostname,
        "-p",
        str(parsed.port or 5432),
        "-U",
        parsed.username or "postgres",
        "-d",
        db_name,
        "-f",
        input_sql_path,
    ]
    subprocess.run(cmd, check=True, env=env)


# --- Dogrulama fonksiyonlari ---

def _run_psql_query(db_uri: str, query: str) -> tuple[bool, str]:
    """Tek bir SQL sorgusu calistir, (basarili, cikti) dondur."""
    parsed = urlparse(db_uri)
    db_name = parsed.path.lstrip("/").split("?")[0]
    env = os.environ.copy()
    if parsed.password:
        env["PGPASSWORD"] = parsed.password
    psql_cmd = _pg_bin("psql")
    cmd = [
        psql_cmd, "-h", parsed.hostname or "localhost",
        "-p", str(parsed.port or 5432),
        "-U", parsed.username or "postgres",
        "-d", db_name, "-t", "-A", "-c", query,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, env=env, timeout=10)
        return r.returncode == 0, (r.stdout or "").strip()
    except Exception as e:
        return False, str(e)


def verify_db_connection(db_uri: str) -> list[str]:
    """PostgreSQL baglantisini dogrula. Hata listesi dondur (bos = OK)."""
    errs = []
    ok, out = _run_psql_query(db_uri, "SELECT 1")
    if not ok:
        errs.append("PostgreSQL baglantisi basarisiz.")
    return errs


def verify_backup_zip(zip_path: str, expect_pg_dump: bool = True) -> list[str]:
    """
    Yedek zip icerigini dogrula. Hata listesi dondur (bos = OK).
    expect_pg_dump: PostgreSQL dump dosyasi bekleniyor mu.
    """
    errs = []
    if not os.path.isfile(zip_path):
        return [f"Yedek dosyasi bulunamadi: {zip_path}"]

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            names = z.namelist()
    except zipfile.BadZipFile:
        return ["Yedek dosyasi gecersiz veya bozuk (zip format hatasi)."]

    if "backup_meta.json" not in names:
        errs.append("backup_meta.json eksik.")

    if expect_pg_dump:
        dump_path = "db_backup/postgres_dump.sql"
        if dump_path not in names:
            errs.append(f"{dump_path} eksik. Bu yedek PostgreSQL dump icermiyor.")
        else:
            with zipfile.ZipFile(zip_path, "r") as z:
                info = z.getinfo(dump_path)
                if info.file_size < 100:
                    errs.append("PostgreSQL dump dosyasi cok kucuk veya bos.")

    # metadata icerigini dogrula
    if "backup_meta.json" in names:
        try:
            with zipfile.ZipFile(zip_path, "r") as z:
                with z.open("backup_meta.json") as f:
                    meta = json.loads(f.read().decode("utf-8"))
            if not isinstance(meta.get("created_at"), str):
                errs.append("backup_meta.json gecersiz (created_at eksik).")
        except Exception as e:
            errs.append(f"backup_meta.json okunamadi: {e}")

    return errs


def verify_restored_db(db_uri: str) -> list[str]:
    """
    Restore sonrasi veritabanini dogrula.
    Kritik tablolarin varligi ve minimum veri kontrolu.
    """
    errs = []
    critical_tables = ["tenants", "users", "roles"]
    for tbl in critical_tables:
        ok, out = _run_psql_query(
            db_uri,
            f"SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name='{tbl}'",
        )
        if not ok:
            errs.append(f"Tablo kontrolu yapilamadi: {tbl}")
            continue
        if (out or "").strip() != "1":
            errs.append(f"Kritik tablo eksik: {tbl}")

    # En az bir tenant ve user olmali (anlamli restore)
    ok, cnt = _run_psql_query(db_uri, "SELECT COUNT(*) FROM tenants")
    if ok and cnt and int(cnt) < 1:
        errs.append("tenants tablosu bos; restore eksik veya basarisiz olabilir.")

    ok, cnt = _run_psql_query(db_uri, "SELECT COUNT(*) FROM users")
    if ok and cnt and int(cnt) < 1:
        errs.append("users tablosu bos; restore eksik veya basarisiz olabilir.")

    return errs


def add_project_files_to_zip(zipf: zipfile.ZipFile, base_dir: str, zip_filename: str) -> int:
    file_count = 0
    for root, dirs, files in os.walk(base_dir):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file_name in files:
            if file_name == zip_filename:
                continue
            _, ext = os.path.splitext(file_name)
            if ext.lower() in EXCLUDE_EXTENSIONS:
                continue
            full_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(full_path, base_dir)
            try:
                zipf.write(full_path, rel_path)
                file_count += 1
            except Exception as exc:
                print(f"Hata - Dosya eklenemedi: {rel_path} ({exc})")
    return file_count


def create_backup(skip_postgres_dump: bool = False) -> str:
    base_dir = os.getcwd()
    backup_dir = make_backup_dirs(base_dir)

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    zip_filename = f"Kokpitim_Tam_Yedek_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)

    db_uri = resolve_db_uri()
    using_postgres = is_postgres_uri(db_uri) and not skip_postgres_dump

    print(f"Yedekleme baslatiliyor... Hedef: {zip_path}")
    if skip_postgres_dump and is_postgres_uri(db_uri):
        print("Uyari: --skip-postgres-dump: pg_dump calistirilmayacak (yalnizca dosya yedegi).")
    print(f"Veritabani turu: {'PostgreSQL (dump dahil)' if using_postgres else 'SQLite/Other veya DB dumpsuz'}")

    with tempfile.TemporaryDirectory() as temp_dir:
        db_dump_rel = None
        metadata = {
            "created_at": timestamp,
            "db_uri_scheme": db_uri.split("://", 1)[0] if "://" in db_uri else "unknown",
            "db_backup_file": None,
            "skip_postgres_dump": bool(skip_postgres_dump),
        }

        if using_postgres:
            db_dump_rel = "db_backup/postgres_dump.sql"
            db_dump_abs = os.path.join(temp_dir, "postgres_dump.sql")
            try:
                run_pg_dump(db_uri, db_dump_abs)
                metadata["db_backup_file"] = db_dump_rel
                print("PostgreSQL dump alindi (pg_dump).")
            except FileNotFoundError:
                raise RuntimeError(
                    "pg_dump bulunamadi. PostgreSQL client kurulu olmali; "
                    "PATH'e bin ekleyin veya PG_BIN ortam degiskeni ile bin klasorunu gosterin "
                    "(ornek: PG_BIN=C:\\Program Files\\PostgreSQL\\16\\bin). "
                    "Sadece kod yedegi icin: python yedekleyici.py backup --skip-postgres-dump"
                )

        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            file_count = add_project_files_to_zip(zipf, base_dir, zip_filename)

            if using_postgres and db_dump_rel:
                zipf.write(db_dump_abs, db_dump_rel)

            metadata_path = os.path.join(temp_dir, "backup_meta.json")
            with open(metadata_path, "w", encoding="utf-8") as meta_f:
                json.dump(metadata, meta_f, ensure_ascii=False, indent=2)
            zipf.write(metadata_path, "backup_meta.json")

    size_mb = os.path.getsize(zip_path) / (1024 * 1024)
    print("-" * 50)
    print(f"Yedekleme basariyla tamamlandi: {zip_filename}")
    print(f"Toplam Dosya Sayisi: {file_count}")
    print(f"Toplam Yedek Boyutu: {size_mb:.2f} MB")
    if using_postgres:
        print("PostgreSQL SQL dump yedege eklendi.")

    # Dogrulama
    check_errors = verify_backup_zip(zip_path, expect_pg_dump=using_postgres)
    if check_errors:
        for e in check_errors:
            print(f"  UYARI: {e}")
        raise RuntimeError("Yedek dogrulama basarisiz.")
    print("Dogrulama: Yedek icerigi OK.")
    print("-" * 50)
    return zip_path


def restore_backup(zip_path: str, dry_run: bool = False, skip_post_verify: bool = False) -> None:
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"Yedek dosyasi bulunamadi: {zip_path}")

    db_uri = resolve_db_uri()
    if not is_postgres_uri(db_uri):
        raise RuntimeError("Geri yukleme icin SQLALCHEMY_DATABASE_URI PostgreSQL olmalidir.")

    # On dogrulama: yedek zip
    print("On dogrulama: Yedek dosyasi kontrol ediliyor...")
    zip_errs = verify_backup_zip(zip_path, expect_pg_dump=True)
    if zip_errs:
        for e in zip_errs:
            print(f"  HATA: {e}")
        raise RuntimeError("Yedek dogrulamasi basarisiz. Geri yukleme iptal edildi.")

    # On dogrulama: hedef baglanti
    print("On dogrulama: PostgreSQL baglantisi kontrol ediliyor...")
    conn_errs = verify_db_connection(db_uri)
    if conn_errs:
        for e in conn_errs:
            print(f"  HATA: {e}")
        raise RuntimeError("Hedef veritabani baglantisi basarisiz.")

    print("On dogrulama: OK.")

    if dry_run:
        print("--dry-run: Gercek geri yukleme atlandi. Tum on kontroller basarili.")
        return

    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(zip_path, "r") as zipf:
            zipf.extractall(temp_dir)

        sql_dump = os.path.join(temp_dir, "db_backup", "postgres_dump.sql")
        if not os.path.isfile(sql_dump):
            raise RuntimeError("Yedek icinde postgres_dump.sql yok. Bu yedek PostgreSQL dump icermiyor.")

        print("UYARI: Mevcut PostgreSQL verisi uzerine geri yukleme yapilacak.")
        print("Geri yukleme baslatiliyor (psql)...")
        try:
            run_psql_restore(db_uri, sql_dump)
        except FileNotFoundError:
            raise RuntimeError(
                "psql bulunamadi. PostgreSQL client kurulu olmali; PATH veya PG_BIN kullanin."
            )

    # Sonra dogrulama
    if not skip_post_verify:
        print("Sonra dogrulama: Restore edilmis veritabani kontrol ediliyor...")
        post_errs = verify_restored_db(db_uri)
        if post_errs:
            for e in post_errs:
                print(f"  UYARI: {e}")
            raise RuntimeError("Restore sonrasi dogrulama basarisiz. Veritabani tutarsiz olabilir.")
        print("Sonra dogrulama: OK.")

    print("Geri yukleme tamamlandi.")


def verify_command(zip_path: str) -> None:
    """Yedek zip icerigini dogrula (restore yapmadan)."""
    if not os.path.isfile(zip_path):
        raise FileNotFoundError(f"Yedek dosyasi bulunamadi: {zip_path}")

    print(f"Dogrulaniyor: {zip_path}")
    expect_dump = True
    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            if "backup_meta.json" in z.namelist():
                with z.open("backup_meta.json") as f:
                    meta0 = json.loads(f.read().decode("utf-8"))
                if meta0.get("skip_postgres_dump"):
                    expect_dump = False
    except Exception:
        pass

    errs = verify_backup_zip(zip_path, expect_pg_dump=expect_dump)
    if errs:
        for e in errs:
            print(f"  HATA: {e}")
        raise RuntimeError("Yedek dogrulamasi basarisiz.")

    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open("backup_meta.json") as f:
            meta = json.loads(f.read().decode("utf-8"))
        print("  backup_meta.json:", json.dumps(meta, ensure_ascii=False, indent=2))
        dump_name = "db_backup/postgres_dump.sql"
        if dump_name in z.namelist():
            info = z.getinfo(dump_name)
            print(f"  postgres_dump.sql: {info.file_size:,} byte")
        else:
            print("  postgres_dump.sql: (yok, dump atlanmis yedek)")
    print("Dogrulama: OK. Yedek guvenilir.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Kokpitim yedekleyici (PostgreSQL destekli, dogrulamali)."
    )
    sub = parser.add_subparsers(dest="command")

    backup_p = sub.add_parser("backup", help="Tam yedek al (kod + db dump), sonra dogrula")
    backup_p.add_argument(
        "--skip-postgres-dump",
        action="store_true",
        help="pg_dump atla (istemci kurulu degilse veya yalnizca kod/instance yedegi).",
    )

    restore_p = sub.add_parser("restore", help="Yedekten PostgreSQL'e geri yukle")
    restore_p.add_argument("--zip", required=True, help="Yedek zip dosya yolu")
    restore_p.add_argument("--dry-run", action="store_true", help="Sadece on kontrolleri yap, geri yukleme yapma")
    restore_p.add_argument("--skip-post-verify", action="store_true", help="Restore sonrasi dogrulamayi atla")

    verify_p = sub.add_parser("verify", help="Yedek zip icerigini dogrula (restore yapmadan)")
    verify_p.add_argument("--zip", required=True, help="Yedek zip dosya yolu")

    return parser


if __name__ == "__main__":
    cli = build_parser()
    args = cli.parse_args()

    try:
        if args.command in (None, "backup"):
            create_backup(skip_postgres_dump=getattr(args, "skip_postgres_dump", False))
        elif args.command == "restore":
            restore_backup(
                args.zip,
                dry_run=getattr(args, "dry_run", False),
                skip_post_verify=getattr(args, "skip_post_verify", False),
            )
        elif args.command == "verify":
            verify_command(args.zip)
        else:
            cli.print_help()
            sys.exit(1)
    except Exception as err:
        print(f"HATA: {err}")
        sys.exit(1)
