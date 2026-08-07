import sqlite3
import json

conn = sqlite3.connect(r"c:\Users\user\Downloads\infosys40\infosys 3\literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Find all records with apple or image
cursor.execute("SELECT * FROM assessment_questions WHERE prompt LIKE '%apple%' OR options LIKE '%apple%' OR text LIKE '%apple%' OR prompt LIKE '%image%'")
rows = cursor.fetchall()
conn.close()

output = []
for r in rows:
    output.append(f"Q ID {r['id']}: {dict(r)}\n")

with open(r"c:\Users\user\Downloads\infosys40\infosys 3\scratch\apple_questions.txt", "w", encoding="utf-8") as f:
    f.writelines(output)

print(f"Done. Found {len(rows)} matching rows.")
