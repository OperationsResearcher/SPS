"""Tomofil çalışan fotoğraflarını sisteme yükle.

`docs/tomofil/fotos/İsim Soyisim.jpg` → User.profile_picture
- Pillow ile 512×512 JPEG q=85'e resize
- static/uploads/profiles/tomofil_<user_id>.jpg olarak kaydet
- DB'de User.profile_picture = '/static/uploads/profiles/tomofil_<id>.jpg'

Kullanım:
    python scripts/tomofil_photo_upload.py            # dry-run
    python scripts/tomofil_photo_upload.py --apply    # uygula
"""
from __future__ import annotations

import io
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

PHOTOS_DIR = ROOT / "docs" / "tomofil" / "fotos"
TENANT_ID = 27


def main():
    apply_mode = "--apply" in sys.argv

    from app import create_app
    from app.extensions import db
    from app.models.core import User
    from PIL import Image, ImageOps

    app = create_app()
    with app.app_context():
        users = User.query.filter_by(tenant_id=TENANT_ID).all()
        upload_dir = Path(app.static_folder) / "uploads" / "profiles"
        upload_dir.mkdir(parents=True, exist_ok=True)

        matched = []
        missing = []
        for u in users:
            if not u.first_name or u.first_name.lower() == "tomofil":
                continue
            expected = PHOTOS_DIR / f"{u.first_name} {u.last_name}.jpg"
            if expected.exists():
                matched.append((u, expected))
            else:
                missing.append(u)

        print(f"\n=== Tomofil profil foto yükleme ===")
        print(f"Toplam Tomofil kullanıcı (admin hariç): {len(matched)+len(missing)}")
        print(f"Foto bulunan: {len(matched)}")
        print(f"Foto bulunamayan: {len(missing)}")
        if missing:
            for u in missing:
                print(f"  ! {u.first_name} {u.last_name}")

        if not apply_mode:
            print("\n--- Önizleme (ilk 5) ---")
            for u, src in matched[:5]:
                out = f"tomofil_{u.id}.jpg"
                print(f"  {src.name}  →  {out}  (user_id={u.id})")
            print(f"\n--apply ile yükle")
            return

        success = 0
        errors = []
        for u, src in matched:
            try:
                out_name = f"tomofil_{u.id}.jpg"
                out_path = upload_dir / out_name
                with src.open("rb") as f:
                    blob = f.read()
                img = Image.open(io.BytesIO(blob))
                img = ImageOps.exif_transpose(img)
                if img.mode in ("RGBA", "LA", "P"):
                    bg = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode in ("RGBA", "LA"):
                        bg.paste(img, mask=img.split()[-1])
                    else:
                        bg.paste(img.convert("RGBA"), mask=img.convert("RGBA").split()[-1])
                    img = bg
                elif img.mode != "RGB":
                    img = img.convert("RGB")
                img.thumbnail((512, 512), Image.LANCZOS)
                img.save(out_path, "JPEG", quality=85, optimize=True, progressive=True)
                u.profile_picture = f"/static/uploads/profiles/{out_name}"
                success += 1
                if success % 10 == 0:
                    db.session.commit()
                    print(f"  ... {success}/{len(matched)} yüklendi")
            except Exception as e:
                errors.append((u, str(e)))
        db.session.commit()
        print(f"\n✓ {success} foto yüklendi, DB güncellendi.")
        if errors:
            print(f"! {len(errors)} hata:")
            for u, msg in errors[:5]:
                print(f"  {u.first_name} {u.last_name}: {msg}")


if __name__ == "__main__":
    main()
