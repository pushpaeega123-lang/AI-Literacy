import sqlite3, json

def list_admins(db_path='literacy.db'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    try:
        c.execute("SELECT id, fullname, email, role FROM users WHERE role = 'admin'")
        rows = c.fetchall()
        print(json.dumps([dict(r) for r in rows], ensure_ascii=False))
    except Exception as e:
        print('ERROR:', e)
    finally:
        conn.close()

if __name__ == '__main__':
    list_admins()
