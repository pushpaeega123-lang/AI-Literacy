import sqlite3
conn = sqlite3.connect("literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT id, title, category, language, difficulty, SUBSTR(content, 1, 100) as c_preview FROM lessons")
rows = cursor.fetchall()
print(f"Total lessons in DB: {len(rows)}")
for r in rows[:15]:
    print(dict(r))
conn.close()
