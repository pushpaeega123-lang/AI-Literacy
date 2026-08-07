import sys
import os

sys.path.append(r"c:\Users\user\Downloads\infosys40\infosys 3")

from app import app, get_db_connection, get_content_recommendations, _get_skill_score_profile

conn = get_db_connection()
cursor = conn.cursor()

# Check if test learner already exists
cursor.execute("SELECT id FROM users WHERE email = 'testlearner@example.com'")
row = cursor.fetchone()
if row:
    user_id = row["id"]
    # Update user details
    cursor.execute("""
        UPDATE users
        SET age = 6,
            learning_language = 'English',
            preferred_language = 'English',
            learning_level = 'Beginner',
            initial_assessment_completed = 1,
            reading_score = 30,
            writing_score = 90,
            vocabulary_score = 90,
            grammar_score = 90,
            listening_score = 90,
            speaking_score = 90,
            weak_skills = 'reading',
            strong_skills = 'writing, vocabulary, grammar, listening, speaking'
        WHERE id = ?
    """, (user_id,))
else:
    cursor.execute("""
        INSERT INTO users (fullname, email, password, age, learning_language, preferred_language, learning_level, initial_assessment_completed,
                           reading_score, writing_score, vocabulary_score, grammar_score, listening_score, speaking_score, weak_skills, strong_skills)
        VALUES ('Test Learner', 'testlearner@example.com', 'hashedpassword', 6, 'English', 'English', 'Beginner', 1,
                30, 90, 90, 90, 90, 90, 'reading', 'writing, vocabulary, grammar, listening, speaking')
    """)
    user_id = cursor.lastrowid

conn.commit()

# Clean lesson progress for user
cursor.execute("DELETE FROM lesson_progress WHERE user_id = ?", (user_id,))
conn.commit()

print(f"Test user created/updated with ID: {user_id}")

# Let's inspect the weak skills profile
skill_profile = _get_skill_score_profile(cursor, user_id)
print("\n--- SKILL PROFILE ---")
print("Weak skills:", skill_profile["weak_skills"])
print("Strong skills:", skill_profile["strong_skills"])

# Mock a lesson in the database
cursor.execute("DELETE FROM lessons WHERE title = 'Three-Letter CVC Words' AND language = 'English'")
cursor.execute("""
    INSERT INTO lessons (title, category, language, content, difficulty)
    VALUES ('Three-Letter CVC Words', 'reading', 'English', 'Real generated multi-sentence lesson content with a quiz [QUIZ] question_text | option1 | option2 | option3 | correct_option', 'Beginner')
""")
conn.commit()
conn.close()

with app.test_request_context():
    from flask import session
    session["user_id"] = user_id
    session["language"] = "English"
    session["learning_language"] = "English"
    session["learning_level"] = "Beginner"
    session["age"] = 6
    
    # 1. Test get_content_recommendations
    recs = get_content_recommendations(user_id)
    print("\n--- RECOMMENDATIONS ENGINE (AI LITERACY JOURNEY) ---")
    if recs:
        for r in recs[:3]:
            print(f"ID: {r['id']}, Title: {r['title']}, Category: {r['category']}, Reason: {r['reason']}")
    else:
        print("No recommendations returned.")

    # 2. Test week_module logic
    import app as app_module
    original_render = app_module.render_template
    captured_context = {}
    def mock_render(template_name, **context):
        captured_context.update(context)
        return "Mock Rendered HTML"
    app_module.render_template = mock_render
    
    try:
        app_module.week_module()
        print("\n--- CURRICULUM CENTER GRID (WEEK-MODULE ROUTE) ---")
        lessons = captured_context.get("lessons", [])
        print(f"Total lessons in Curriculum Center: {len(lessons)}")
        for idx, l in enumerate(lessons, start=1):
            print(f"{idx}. ID: {l['id']}, Title: {l['title']}, Category: {l['category']}, Locked: {l['locked']}")
    finally:
        app_module.render_template = original_render

    # 3. Test lesson_detail logic
    captured_lesson = {}
    captured_context.clear()
    def mock_render_lesson(template_name, **context):
        captured_lesson.update(context.get("lesson", {}))
        captured_context.update(context)
        return "Mock Rendered HTML"
    app_module.render_template = mock_render_lesson
    
    try:
        app_module.lesson_detail(6004)
        print("\n--- LESSON DETAIL VIEW ROUTE ---")
        print("Lesson ID:", captured_lesson.get("id"))
        print("Title:", captured_lesson.get("title"))
        print("Category:", captured_lesson.get("category"))
        print("Content:", captured_lesson.get("content"))
        
        sent_data = captured_context.get("sentences_data", [])
        print(f"Sentences count: {len(sent_data)}")
        if sent_data:
            print("Last sentence quiz:", sent_data[-1].get("quiz"))
    finally:
        app_module.render_template = original_render
