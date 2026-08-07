import os
import sqlite3
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import app as app_module


class AssessmentAndPathBackendTests(unittest.TestCase):
    def test_assessment_questions_cover_all_core_skills_for_intermediate_level(self):
        questions = app_module.get_assessment_questions("English", age=12, learning_level="Intermediate")

        self.assertGreaterEqual(len(questions), 8)
        skill_keys = {q.get("skill_score_key") for q in questions}
        self.assertTrue({"reading", "writing", "listening", "speaking", "comprehension"} <= skill_keys)

    def test_beginner_assessment_uses_play_based_prompts_without_text_questions(self):
        questions = app_module.get_assessment_questions("English", age=4, learning_level="Beginner")

        self.assertGreaterEqual(len(questions), 6)
        self.assertTrue(all(q.get("type") not in {"reading", "writing"} for q in questions))
        self.assertTrue(any(q.get("skill_score_key") == "writing" for q in questions))

    def test_personalized_path_uses_play_based_steps_for_early_learners(self):
        conn = sqlite3.connect(":memory:")
        conn.row_factory = sqlite3.Row
        conn.execute("CREATE TABLE users (id INTEGER PRIMARY KEY, fullname TEXT, age INTEGER, language TEXT, preferred_language TEXT, learning_language TEXT, learning_level TEXT, current_proficiency TEXT, reading_score REAL, writing_score REAL, comprehension_score REAL, listening_score REAL, speaking_score REAL, weak_skills TEXT, strong_skills TEXT, learning_path TEXT, recommended_lesson TEXT, initial_assessment_completed INTEGER DEFAULT 0, assessment_completed INTEGER DEFAULT 0)")
        conn.execute("CREATE TABLE lesson_progress (user_id INTEGER, lesson_id INTEGER)")
        conn.execute("CREATE TABLE study_sessions (user_id INTEGER, date TEXT, duration INTEGER)")
        conn.execute("CREATE TABLE assessment_history (user_id INTEGER)")
        conn.execute("INSERT INTO users (id, fullname, age, language, preferred_language, learning_language, learning_level, current_proficiency, reading_score, writing_score, comprehension_score, listening_score, speaking_score, weak_skills, strong_skills) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (1, "Asha", 4, "English", "English", "English", "Beginner", "Beginner", 30, 25, 40, 35, 20, "Listening, Speaking", "None"))
        conn.commit()
        original_get_db_connection = app_module.get_db_connection
        app_module.get_db_connection = lambda: conn
        try:
            path = app_module.generate_personalized_learning_path(1)
        finally:
            app_module.get_db_connection = original_get_db_connection

        self.assertTrue(path)
        self.assertTrue(any(item.get("type") == "Play-Based Video" for item in path))
        self.assertTrue(any(item.get("type") == "Play Activity" for item in path))
        self.assertTrue(any(item.get("skill_focus") == "listening" for item in path))


if __name__ == "__main__":
    unittest.main()
