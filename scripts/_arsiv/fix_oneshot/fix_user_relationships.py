import re

with open('models/user.py', 'r', encoding='utf-8') as f:
    content = f.read()

original = content

# Geri al: 'models.user.User' -> 'User'
content = re.sub(r"relationship\('models\.user\.User'", "relationship('User'", content)
content = content.replace(
    "# users = db.relationship('models.user.User', backref='kurum', lazy=True)  # User modelinde backref var",
    "# users = db.relationship('User', backref='kurum', lazy=True)  # User modelinde backref var"
)

if content == original:
    print("Degisiklik yok")
else:
    with open('models/user.py', 'w', encoding='utf-8') as f:
        f.write(content)
    print("Geri alindi: relationship('models.user.User') -> relationship('User')")
