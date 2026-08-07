import sqlite3

conn = sqlite3.connect(r"c:\Users\user\Downloads\infosys40\infosys 3\literacy.db")
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Check table info
try:
    cursor.execute("PRAGMA table_info(assessment_questions)")
    print("Columns in assessment_questions:")
    for r in cursor.fetchall():
        print(dict(r))
except Exception as e:
    print(f"Error checking columns: {e}")

# Check first 20 rows
try:
    cursor.execute("SELECT * FROM assessment_questions LIMIT 50")
    rows = cursor.fetchall()
    print("\nRows in assessment_questions:")
    for r in rows:
        print(dict(r))
except Exception as e:
    print(f"Error checking rows: {e}")

conn.close()
