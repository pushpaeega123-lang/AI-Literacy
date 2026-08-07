import sqlite3
conn = sqlite3.connect('literacy.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    print("Table:", table[0])
    cursor.execute(f"PRAGMA table_info({table[0]})")
    for col in cursor.fetchall():
        print("  ", col)
conn.close()
