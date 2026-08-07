with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find duplicate occurrences of helper functions
helper_starts = []
for idx, line in enumerate(lines):
    if "def classify_score_to_proficiency(" in line:
        helper_starts.append(idx)

print(f"helper_starts: {helper_starts}")

# Find occurrences of create_database
db_funcs = []
for idx, line in enumerate(lines):
    if "def create_database():" in line:
        db_funcs.append(idx)

print(f"db_funcs: {db_funcs}")
