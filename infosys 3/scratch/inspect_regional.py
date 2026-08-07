import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect("literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT title, content, language FROM lessons WHERE language != 'English' LIMIT 30")
rows = cursor.fetchall()
for r in rows:
    print(r["language"], "|", r["title"], "==>", r["content"])
conn.close()
