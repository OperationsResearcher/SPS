"""DB instance ve model analizi — sadece okuma, degisiklik yok."""
import os, ast, re

def get_db_instances(filepath):
    """SQLAlchemy() instance tanimlarini bul."""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        matches = re.findall(r'(\w+)\s*=\s*SQLAlchemy\(\)', content)
        return matches
    except:
        return []

def get_db_imports(filepath):
    """db import satirlarini bul."""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        lines = []
        for line in content.splitlines():
            if 'import db' in line or ('from' in line and 'db' in line and 'import' in line):
                lines.append(line.strip())
        return lines
    except:
        return []

def get_tablenames(filepath):
    """__tablename__ tanimlarini bul."""
    try:
        with open(filepath, encoding='utf-8') as f:
            content = f.read()
        # class adi ve tablename'i birlikte bul
        results = []
        current_class = None
        for line in content.splitlines():
            cm = re.match(r'^class\s+(\w+)', line)
            if cm:
                current_class = cm.group(1)
            tm = re.match(r"\s+__tablename__\s*=\s*['\"](.+)['\"]", line)
            if tm and current_class:
                results.append((current_class, tm.group(1)))
        return results
    except:
        return []

print("=" * 70)
print("1. SQLAlchemy db INSTANCE TANIMLARI")
print("=" * 70)

instance_files = [
    'extensions.py',
    'app/extensions.py',
    'app/models/__init__.py',
]
for f in instance_files:
    if os.path.exists(f):
        instances = get_db_instances(f)
        if instances:
            print(f"  {f} → db = SQLAlchemy()  [{', '.join(instances)}]")
        else:
            # import mi var?
            imports = get_db_imports(f)
            db_imports = [i for i in imports if 'SQLAlchemy' not in i and 'db' in i]
            if db_imports:
                print(f"  {f} → import: {db_imports[0]}")
            else:
                print(f"  {f} → db instance YOK / import YOK")

print()
print("=" * 70)
print("2. MODEL DOSYALARI — db IMPORT KAYNAKLARI")
print("=" * 70)

print("\n  app/models/*.py:")
for fname in sorted(os.listdir('app/models')):
    if not fname.endswith('.py') or fname == '__init__.py':
        continue
    path = f'app/models/{fname}'
    imports = get_db_imports(path)
    db_line = next((i for i in imports if 'db' in i and 'import' in i), None)
    print(f"    {fname:30s} → {db_line or '(db import bulunamadi)'}")

print("\n  models/*.py:")
for fname in sorted(os.listdir('models')):
    if not fname.endswith('.py') or fname == '__init__.py':
        continue
    path = f'models/{fname}'
    imports = get_db_imports(path)
    db_line = next((i for i in imports if 'db' in i and 'import' in i), None)
    print(f"    {fname:30s} → {db_line or '(db import bulunamadi)'}")

print("\n  app/models/__init__.py:")
imports = get_db_imports('app/models/__init__.py')
for i in imports:
    print(f"    {i}")

print("\n  models/__init__.py:")
imports = get_db_imports('models/__init__.py')
for i in imports:
    print(f"    {i}")

print()
print("=" * 70)
print("3. create_app — init_app CAGRISI")
print("=" * 70)
with open('__init__.py', encoding='utf-8') as f:
    content = f.read()
for line in content.splitlines():
    if 'init_app' in line:
        print(f"  {line.strip()}")

print()
print("=" * 70)
print("4. CAKISAN TABLO ADLARI VE CLASS ADLARI")
print("=" * 70)

all_tables = {}  # tablename -> [(class, file)]
all_classes = {}  # classname -> [file]

search_dirs = [
    ('models', [f for f in os.listdir('models') if f.endswith('.py')]),
    ('app/models', [f for f in os.listdir('app/models') if f.endswith('.py')]),
]

for dirpath, files in search_dirs:
    for fname in files:
        path = f'{dirpath}/{fname}'
        tables = get_tablenames(path)
        for classname, tablename in tables:
            all_tables.setdefault(tablename, []).append((classname, path))
            all_classes.setdefault(classname, []).append(path)

print("\n  Cakisan __tablename__'ler (2+ class ayni tabloyu kullaniyor):")
found_table_conflict = False
for tname, entries in sorted(all_tables.items()):
    if len(entries) > 1:
        found_table_conflict = True
        print(f"  CAKISMA: '{tname}'")
        for cls, fp in entries:
            print(f"    class {cls} in {fp}")

if not found_table_conflict:
    print("  Tablo adi cakismasi YOK")

print("\n  Cakisan class adlari (2+ dosyada ayni isim):")
found_class_conflict = False
for cname, files in sorted(all_classes.items()):
    if len(files) > 1:
        found_class_conflict = True
        print(f"  CAKISMA: class '{cname}'")
        for fp in files:
            print(f"    {fp}")

if not found_class_conflict:
    print("  Class adi cakismasi YOK")

print()
print("=" * 70)
print("5. SONUC")
print("=" * 70)
if found_table_conflict or found_class_conflict:
    print("  SORUN VAR — yukardaki cakismalar giderilmeli")
else:
    print("  Temiz")
