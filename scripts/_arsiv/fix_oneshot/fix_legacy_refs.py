import re

with open('models/user.py', 'r', encoding='utf-8') as f:
    content = f.read()

# String relationship referanslarini LegacyUser'a guncelle
content = re.sub(r"relationship\('User'", "relationship('LegacyUser'", content)
content = content.replace(
    "# users = db.relationship('User', backref='kurum', lazy=True)  # User modelinde backref var",
    "# users = db.relationship('LegacyUser', backref='kurum', lazy=True)  # LegacyUser modelinde backref var"
)

with open('models/user.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('models/user.py guncellendi')
