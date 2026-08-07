import sqlite3

print("Listing all users from literacy.db:")
try:
    conn = sqlite3.connect(r"c:\Users\user\Downloads\infosys40\infosys 3\literacy.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, fullname, email, role FROM users")
    rows = cursor.fetchall()
    for r in rows:
        print(dict(r))
    conn.close()
except Exception as e:
    print(f"Error querying db: {e}")
