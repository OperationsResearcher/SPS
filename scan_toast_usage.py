import os

ROOT = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(ROOT, "templates")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def main() -> None:
    suspicious: list[str] = []
    all_showtoast: list[str] = []

    for dirpath, _, files in os.walk(TEMPLATES_DIR):
        for name in files:
            if not name.lower().endswith((".html", ".htm")):
                continue
            path = os.path.join(dirpath, name)
            text = read_text(path)

            if "showToast" not in text:
                continue
            if "showToast(" not in text:
                continue

            rel = os.path.relpath(path, ROOT)
            all_showtoast.append(rel)

            extends_base = '{% extends "base.html" %}' in text or "extends \"base.html\"" in text
            has_local_impl = "function showToast" in text or "showToast wrapper" in text

            if not extends_base and not has_local_impl:
                suspicious.append(rel)

    print(f"templates with showToast(): {len(all_showtoast)}")
    print(f"showToast() but no base/local impl: {len(suspicious)}")
    if suspicious:
        print("\n".join(sorted(suspicious)))


if __name__ == "__main__":
    main()
