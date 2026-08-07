"""
Safe migration to add `skill`, `level`, `modality` columns to `assessment_questions` and populate by heuristics.
No rows are deleted. Prints a summary of updates.
"""
import sqlite3
import json

TYPE_TO_SKILL = {
    'vocabulary': 'Reading',
    'reading': 'Reading',
    'sentence': 'Reading',
    'grammar': 'Writing',
    'cloze': 'Comprehension',
    'comprehension': 'Comprehension',
    'listening': 'Listening',
    'spoken': 'Speaking',
    'speaking': 'Speaking',
    'writing': 'Writing',
}

AGE_TO_LEVEL = {
    'preschool': 'Beginner',
    'pre-school': 'Beginner',
    'child': 'Beginner',
    'kid': 'Beginner',
    'teen': 'Basic',
    'adult': 'Intermediate',
}


def ensure_column(conn, table, column, coltype='TEXT'):
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info('{table}')")
    cols = [r[1] for r in cur.fetchall()]
    if column not in cols:
        cur.execute(f"ALTER TABLE {table} ADD COLUMN {column} {coltype}")
        conn.commit()
        return True
    return False


def infer_skill(row):
    t = (row.get('type') or '').lower()
    if t:
        for k,v in TYPE_TO_SKILL.items():
            if k in t:
                return v
    # fallback: look at name
    name = (row.get('name') or '').lower()
    for k,v in TYPE_TO_SKILL.items():
        if k in name:
            return v
    return 'Reading'


def infer_level(row):
    ag = (row.get('age_group') or '').lower()
    if ag:
        for k,v in AGE_TO_LEVEL.items():
            if k in ag:
                return v
    # fallback: use name hints
    if 'beginner' in (row.get('name') or '').lower():
        return 'Beginner'
    return 'Basic'


def infer_modality(row):
    # If prompt empty and options present -> likely listening with images, but default to 'text'
    prompt = (row.get('prompt') or '').strip()
    opts = (row.get('options') or '').strip()
    t = (row.get('type') or '').lower()
    if 'listen' in t or 'audio' in t or not prompt and opts:
        return 'listening' if 'audio' in (row.get('name') or '').lower() or 'listen' in t else 'text'
    if 'speak' in t or 'pronoun' in t:
        return 'speaking'
    return 'text'


def migrate(db='literacy.db'):
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    table = 'assessment_questions'
    updated = 0
    added_cols = []
    try:
        if ensure_column(conn, table, 'skill'):
            added_cols.append('skill')
        if ensure_column(conn, table, 'level'):
            added_cols.append('level')
        if ensure_column(conn, table, 'modality'):
            added_cols.append('modality')
        cur = conn.cursor()
        cur.execute(f"SELECT * FROM {table}")
        rows = cur.fetchall()
        for r in rows:
            row = {k: r[k] for k in r.keys()}
            skill = row.get('skill') or infer_skill(row)
            level = row.get('level') or infer_level(row)
            modality = row.get('modality') or infer_modality(row)
            # Update only if blank
            updates = []
            params = []
            if not row.get('skill'):
                updates.append('skill = ?')
                params.append(skill)
            if not row.get('level'):
                updates.append('level = ?')
                params.append(level)
            if not row.get('modality'):
                updates.append('modality = ?')
                params.append(modality)
            if updates:
                params.append(row.get('id'))
                sql = f"UPDATE {table} SET {', '.join(updates)} WHERE id = ?"
                cur.execute(sql, params)
                updated += 1
        conn.commit()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    finally:
        conn.close()
    print(json.dumps({"added_columns": added_cols, "rows_updated": updated}, ensure_ascii=False))

if __name__ == '__main__':
    migrate()
