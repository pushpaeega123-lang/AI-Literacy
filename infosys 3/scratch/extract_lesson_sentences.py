import sqlite3
conn = sqlite3.connect("literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
cursor.execute("SELECT DISTINCT content FROM lessons")
contents = [r["content"] for r in cursor.fetchall() if r["content"]]
print(f"Unique contents: {len(contents)}")
sentences = set()
for c in contents:
    # Clean quiz parts
    if "[QUIZ]" in c:
        c = c.split("[QUIZ]")[0].strip()
    import re
    parts = re.split(r'[.।?]', c)
    for p in parts:
        val = p.strip()
        if val:
            sentences.add(val)

print(f"Unique sentences: {len(sentences)}")
for s in sorted(list(sentences))[:40]:
    print(s)
conn.close()
