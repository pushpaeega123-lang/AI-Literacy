with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update columns_to_add in create_database for users table
# Let's locate the list starting with columns_to_add = [
import re

user_cols_pattern = r"(columns_to_add = \[\s*\n\s*\(\"dob\", \"TEXT\"\),)"
user_cols_replacement = r"""\1
        ("reading_score", "REAL DEFAULT 0.0"),
        ("writing_score", "REAL DEFAULT 0.0"),
        ("vocabulary_score", "REAL DEFAULT 0.0"),
        ("grammar_score", "REAL DEFAULT 0.0"),
        ("assessment_score", "REAL DEFAULT 0.0"),"""

content, count = re.subn(user_cols_pattern, user_cols_replacement, content)
print(f"Updated users columns: {count} matches")

# 2. Add assessment_history migrations
hist_table_pattern = r"(CREATE TABLE IF NOT EXISTS assessment_history\(.*?\s*\)\s*\"\"\"\))"
hist_table_replacement = r"""\1
    
    # Migration: check and add missing columns to assessment_history table
    columns_to_add_hist = [
        ("wrong_answers", "TEXT"),
        ("accuracy", "REAL DEFAULT 0.0"),
        ("completion_time", "REAL DEFAULT 0.0"),
        ("reading_score", "REAL DEFAULT 0.0"),
        ("writing_score", "REAL DEFAULT 0.0"),
        ("vocabulary_score", "REAL DEFAULT 0.0"),
        ("grammar_score", "REAL DEFAULT 0.0"),
        ("listening_score", "REAL DEFAULT 0.0"),
        ("speaking_score", "REAL DEFAULT 0.0"),
        ("overall_score", "REAL DEFAULT 0.0"),
        ("learner_level", "TEXT"),
        ("weak_skills", "TEXT"),
        ("strong_skills", "TEXT")
    ]
    for col_name, col_type in columns_to_add_hist:
        try:
            cursor.execute(f"SELECT {col_name} FROM assessment_history LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute(f"ALTER TABLE assessment_history ADD COLUMN {col_name} {col_type}")
            conn.commit()"""

content, count2 = re.subn(hist_table_pattern, hist_table_replacement, content, flags=re.DOTALL)
print(f"Updated assessment_history columns: {count2} matches")

if count > 0 or count2 > 0:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Database migrations fix applied to app.py!")
else:
    print("Failed to apply database migrations fix!")
