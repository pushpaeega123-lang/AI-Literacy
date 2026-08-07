import sqlite3
DATABASE = "literacy.db"

def migrate():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # Columns to add to assessment_history
    columns_hist = [
        "writing_score REAL DEFAULT 0.0",
        "vocabulary_score REAL DEFAULT 0.0",
        "grammar_score REAL DEFAULT 0.0",
        "learner_level TEXT",
        "weak_skills TEXT",
        "strong_skills TEXT"
    ]

    for col in columns_hist:
        try:
            cursor.execute(f"ALTER TABLE assessment_history ADD COLUMN {col}")
            print("[assessment_history] Added column:", col)
        except sqlite3.OperationalError:
            print("[assessment_history] Column already exists:", col)

    # Columns to add to users
    columns_users = [
        "writing_score REAL DEFAULT 0.0",
        "vocabulary_score REAL DEFAULT 0.0",
        "grammar_score REAL DEFAULT 0.0",
        "weak_skills TEXT",
        "strong_skills TEXT"
    ]

    for col in columns_users:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col}")
            print("[users] Added column:", col)
        except sqlite3.OperationalError:
            print("[users] Column already exists:", col)

    conn.commit()
    conn.close()
    print("Migration finished!")

if __name__ == "__main__":
    migrate()
