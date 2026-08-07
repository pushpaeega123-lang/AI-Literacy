import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("literacy.db")
cursor = conn.cursor()

# Remove existing testuser if any
cursor.execute("DELETE FROM users WHERE email = 'testuser@example.com'")

hashed_pw = generate_password_hash("Password@123")
cursor.execute("""
    INSERT INTO users (
        fullname, email, password, age, education_level, learning_status,
        language, preferred_language, learning_language, initial_assessment_completed,
        learning_level, current_proficiency, xp, coins
    ) VALUES (
        'Test User', 'testuser@example.com', ?, '10', 'School', 'Student',
        'English', 'Hindi', 'English', 1,
        'Beginner', 'Beginner', 100, 100
    )
""", (hashed_pw,))

conn.commit()
conn.close()
print("Test user created successfully!")
