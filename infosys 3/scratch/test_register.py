import sqlite3
from werkzeug.security import generate_password_hash

DATABASE = "literacy.db"

def test_insert():
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        
        fullname = "Test User"
        email = "test@example.com"
        password = "Password123!"
        age = 8
        education = "School"
        learning_level = "Beginner"
        status = "Student"
        preferred_language = "English"
        learning_language = "English"
        init_completed = 0
        dob = "2018-01-01"
        gender = "Male"
        avatar = "Cat"
        stream = ""
        sub_stream = ""
        
        cursor.execute(
            """
            INSERT INTO users(
                fullname, email, password, age, education_level, learning_level, learning_status, language, 
                stream, sub_stream, dob, gender, avatar, coins, badges, mascot_dresses, current_mascot_dress, 
                preferred_language, learning_language, initial_assessment_completed
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fullname,
                email,
                generate_password_hash(password),
                age,
                education,
                learning_level,
                status,
                preferred_language,
                stream if stream else None,
                sub_stream if sub_stream else None,
                dob,
                gender,
                avatar,
                0,
                "",
                "Default",
                "Default",
                preferred_language,
                learning_language,
                init_completed
            ),
        )
        
        conn.commit()
        print("Insert successful!")
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    test_insert()
