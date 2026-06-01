import re

with open('system_control_asistencia/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace MySQL config with SQLite
old_db = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'control_acceso_asistencia_ia',
        'USER': 'root',
        'PASSWORD' : '',
        'HOST' : 'localhost',
        'PORT' : '3306',
    }
}"""

new_db = """DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}"""

if old_db in content:
    content = content.replace(old_db, new_db)
    print("SUCCESS: MySQL replaced with SQLite")
else:
    print("WARNING: Could not find exact MySQL config block, trying regex...")
    # Try regex approach
    pattern = r"DATABASES\s*=\s*\{[^}]+\{[^}]+\}[^}]*\}"
    match = re.search(pattern, content, re.DOTALL)
    if match:
        print(f"Found block: {match.group()}")
    else:
        print("ERROR: Could not find DATABASES block")

with open('system_control_asistencia/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done!")
