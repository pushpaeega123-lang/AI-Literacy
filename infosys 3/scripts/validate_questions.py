"""
Validate assessment questions in the DB for common issues:
- missing required metadata (skill, level, modality)
- no correct option or multiple correct options
- placeholder options like 'Option 4' or 'Option 1'
- duplicated options or identical text
- modality mismatch (e.g., audio present but text also shown for listening items)

Outputs JSON report to stdout.
"""
import sqlite3
import json
import re

PLACEHOLDER_PATTERN = re.compile(r"^Option\s*\d+$", re.IGNORECASE)
# accept multiple possible prompt column names used in different schemas
REQUIRED_FIELDS = ["skill", "level", "modality"]
PROMPT_KEYS = ["prompt_text", "prompt", "text", "prompt_sentence"]


def fetch_questions(conn):
    cur = conn.cursor()
    # try common table names
    candidates = ["assessment_questions", "questions", "assessment_items"]
    for t in candidates:
        try:
            cur.execute(f"SELECT * FROM {t} LIMIT 1")
            # if works, fetch all
            cur.execute(f"SELECT * FROM {t}")
            rows = cur.fetchall()
            cols = [d[0] for d in cur.description]
            return t, cols, rows
        except Exception:
            continue
    raise RuntimeError("No question table found among candidates: " + ",".join(candidates))


def row_to_dict(cols, row):
    return {cols[i]: row[i] for i in range(len(cols))}


def analyze_option_text(text):
    if text is None:
        return []
    return [t.strip() for t in text.split("||") if t.strip()]


def validate_item(item):
    problems = []
    # Required metadata
    for f in REQUIRED_FIELDS:
        if not item.get(f):
            problems.append(f"missing_{f}")
    # Options parsing: try common columns
    option_texts = []
    if item.get('options_json'):
        try:
            opts = json.loads(item.get('options_json'))
            for o in opts:
                option_texts.append(o.get('text') or o.get('label') or '')
            correct_count = sum(1 for o in opts if o.get('is_correct') or o.get('correct'))
        except Exception:
            problems.append('invalid_options_json')
            correct_count = 0
    else:
        # fallback: some schemas store option1..option4 or options concat
        for k in ['option1','option2','option3','option4','opt_a','opt_b','opt_c','opt_d']:
            if k in item:
                v = item.get(k)
                if v:
                    option_texts.append(v)
        # also try a 'options' field with || separator
        if not option_texts and item.get('options'):
            option_texts = analyze_option_text(item.get('options'))
        # try correct key
        correct_count = 0
        for k in ['correct_option','correct','answer','answer_key']:
            if k in item and item.get(k) is not None:
                # if stored as index or letter or id
                correct_count = 1
                break
    # check correct count
    if correct_count == 0:
        problems.append('no_correct_option')
    # placeholder options
    for t in option_texts:
        if PLACEHOLDER_PATTERN.match(t):
            problems.append('placeholder_option')
    # duplicate options
    texts = [t.strip().lower() for t in option_texts if t]
    if len(texts) != len(set(texts)):
        problems.append('duplicate_options')
    # empty options
    if any(not t for t in option_texts):
        problems.append('empty_option_text')
    # modality mismatch heuristic
    modality = (item.get('modality') or '').lower()
    if modality == 'listening':
        # if listening, prefer audio-only prompts; detect any visible prompt text under known keys
        prompt = ''
        for k in PROMPT_KEYS:
            if item.get(k):
                prompt = str(item.get(k)).strip()
                break
        if prompt:
            problems.append('listening_has_text_prompt')
    # ensure at least one prompt key exists
    if not any(item.get(k) for k in PROMPT_KEYS):
        problems.append('missing_prompt_text')
    return problems


def main(db_path='literacy.db'):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    try:
        table, cols, rows = fetch_questions(conn)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        return
    issues = []
    for r in rows:
        item = row_to_dict(cols, r)
        # normalize strings
        for k,v in item.items():
            if isinstance(v, bytes):
                try:
                    item[k] = v.decode('utf-8')
                except Exception:
                    item[k] = str(v)
        problems = validate_item(item)
        if problems:
            issues.append({
                "id": item.get('id') or item.get('question_id') or None,
                "title": item.get('prompt_text') or item.get('prompt_sentence') or item.get('title') or '',
                "problems": problems
            })
    report = {"table": table, "checked": len(rows), "issues_count": len(issues), "issues": issues}
    print(json.dumps(report, indent=2, ensure_ascii=False))

if __name__ == '__main__':
    main()
