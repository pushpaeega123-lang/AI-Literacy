import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "literacy.db"


def create_database():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age INTEGER,
        education_level TEXT,
        learning_level TEXT,
        learning_status TEXT,
        language TEXT
    )
    """)

    for col_def in [
        "learning_level TEXT DEFAULT 'Beginner'",
        "current_proficiency TEXT DEFAULT 'Beginner'",
        "recommended_lesson TEXT",
        "learning_path TEXT",
        "completed_lessons_count INTEGER DEFAULT 0",
        "videos_watched_count INTEGER DEFAULT 0",
        "assessment_count INTEGER DEFAULT 0",
        "average_score REAL DEFAULT 0.0",
        "progress_percentage REAL DEFAULT 0.0",
        "notifications_enabled INTEGER DEFAULT 1",
        "push_subscription TEXT"
    ]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass

    conn.commit()
    conn.close()

    print("Database created successfully!")


def insert_sample_user():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    password = generate_password_hash("123456")

    try:

        cursor.execute("""

        INSERT INTO users
        (fullname,email,password,age,education_level,learning_status,language)

        VALUES(?,?,?,?,?,?,?)

        """,

        (

            "Demo User",
            "demo@gmail.com",
            password,
            20,
            "Intermediate",
            "Student",
            "English"

        )

        )

        conn.commit()

        print("Sample user inserted.")

    except sqlite3.IntegrityError:

        print("Sample user already exists.")

    conn.close()


def view_users():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    conn.close()

    return users


def delete_all_users():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM users")

    conn.commit()
    conn.close()

    print("All users deleted.")


if __name__ == "__main__":

    create_database()

    insert_sample_user()

    users = view_users()

    print("\nRegistered Users\n")

    for user in users:
        try:
            print(user)
        except Exception:
            print(str(user).encode('utf-8'))