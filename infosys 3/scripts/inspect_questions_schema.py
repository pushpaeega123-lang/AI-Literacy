import sqlite3, json

def inspect_table(db='literacy.db', table='assessment_questions'):
    conn = sqlite3.connect(db)
    cur = conn.cursor()
    try:
        cur.execute(f"PRAGMA table_info('{table}')")
        cols = cur.fetchall()
        schema = [{"cid": c[0], "name": c[1], "type": c[2], "notnull": c[3], "dflt_value": c[4], "pk": c[5]} for c in cols]
        cur.execute(f"SELECT * FROM {table} LIMIT 1")
        row = cur.fetchone()
        if row:
            colnames = [d[0] for d in cur.description]
            sample = {colnames[i]: row[i] for i in range(len(colnames))}
        else:
            sample = None
        print(json.dumps({"table": table, "schema": schema, "sample": sample}, indent=2, ensure_ascii=False))
    except Exception as e:
        print(json.dumps({"error": str(e)}))
    finally:
        conn.close()

if __name__ == '__main__':
    inspect_table()
