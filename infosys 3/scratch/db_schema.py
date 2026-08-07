import sqlite3

def dump_schema():
    conn = sqlite3.connect("literacy.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    for name, sql in tables:
        print(f"Table: {name}")
        print(f"Schema:\n{sql}\n")
        print("-" * 50)
    conn.close()

if __name__ == "__main__":
    dump_schema()
