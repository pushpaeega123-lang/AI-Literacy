import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

conn = sqlite3.connect(r"c:\Users\user\Downloads\infosys40\infosys 3\literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT email, password FROM users WHERE role = 'admin'")
admins = cursor.fetchall()
conn.close()

passwords_to_try = ["123456", "admin", "admin123", "password", "admin_test", "admin@123"]

for admin in admins:
    email = admin["email"]
    p_hash = admin["password"]
    print(f"Checking email: {email}")
    matched = False
    for p in passwords_to_try:
        if check_password_hash(p_hash, p):
            print(f"  FOUND PASSWORD: {p}")
            matched = True
            break
    if not matched:
        print("  Did not match standard list.")
