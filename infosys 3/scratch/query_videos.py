import sqlite3
import sys

sys.stdout.reconfigure(encoding='utf-8')
conn = sqlite3.connect("literacy.db")
c = conn.cursor()
c.execute("SELECT id, title, language, age_group, category, youtube_video_id FROM videos")
for row in c.fetchall():
    print(f"ID: {row[0]}, Title: {row[1]}, Lang: {row[2]}, Age: {row[3]}, Cat: {row[4]}, YT: {row[5]}")
conn.close()
