import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import sqlite3
import json
from app import app, get_db_connection, get_content_recommendations, generate_personalized_learning_path, generate_ai_recommendations, get_assessment_questions

class TestPersonalizedLearningRecommendationEngine(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "testing-secret-key"
        
        # Setup clean test user in SQLite
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete test records if any exist
        cursor.execute("DELETE FROM users WHERE email = 'test_recs@example.com'")
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = 8888")
        cursor.execute("DELETE FROM recommendation_history WHERE user_id = 8888")
        
        # Insert clean test user profile
        cursor.execute("""
            INSERT INTO users (id, fullname, email, password, age, language, learning_level, current_proficiency,
                               weak_skills, strong_skills, initial_assessment_completed, completed_lessons_count, progress_percentage)
            VALUES (8888, 'Recommendation Learner', 'test_recs@example.com', 'hashedpassword', 8, 'English', 'Beginner', 'Beginner',
                    'reading,grammar', 'vocabulary', 1, 0, 0.0)
        """)
        
        # Ensure we have at least a few sample lessons for the English language
        cursor.execute("DELETE FROM lessons WHERE language = 'English' AND id IN (9801, 9802, 9803, 9804)")
        cursor.execute("""
            INSERT INTO lessons (id, title, category, language, content, difficulty)
            VALUES 
            (9801, 'Alphabet Tracing A-Z', 'Alphabet', 'English', 'Trace alphabet letters...', 'easy'),
            (9802, 'Word Match Game', 'Vocabulary', 'English', 'Match words with objects...', 'easy'),
            (9803, 'Reading Sentences', 'Reading', 'English', 'Practice reading complete sentences...', 'easy'),
            (9804, 'Grammar Basics', 'Grammar', 'English', 'Learn nouns, verbs, and punctuation...', 'medium')
        """)
        
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = 8888")
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = 8888")
        cursor.execute("DELETE FROM recommendation_history WHERE user_id = 8888")
        cursor.execute("DELETE FROM lessons WHERE id IN (9801, 9802, 9803, 9804)")
        conn.commit()
        conn.close()

    def test_1_dynamic_weak_skills_recommendations(self):
        # The user has weak_skills='reading,grammar'
        # get_content_recommendations should recommend lessons matching reading or grammar (e.g. 9803 or 9804)
        recs = get_content_recommendations(8888)
        self.assertTrue(len(recs) > 0)
        
        rec_ids = [r["id"] for r in recs]
        self.assertIn(9803, rec_ids) # Reading lesson should be present
        
        # Verify reason explains why it was generated
        reading_rec = next(r for r in recs if r["id"] == 9803)
        self.assertEqual(reading_rec["reason"], "Recommended to build reading fluency and text comprehension.")

    def test_2_recommendation_history_preservation(self):
        # Clear existing logs
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM recommendation_history WHERE user_id = 8888")
        conn.commit()
        
        # Trigger recommendations
        recs = get_content_recommendations(8888)
        
        # Verify recommendation_history holds pending recommendations
        cursor.execute("SELECT COUNT(*) FROM recommendation_history WHERE user_id = 8888 AND status = 'pending'")
        pending_count = cursor.fetchone()[0]
        self.assertTrue(pending_count > 0)
        conn.close()

    def test_3_lesson_completion_refresh_flow(self):
        # Login mock session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 8888
            sess["fullname"] = "Recommendation Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1

        # Retrieve recommendations first to seed history
        get_content_recommendations(8888)
        
        # Post to complete lesson 9803 (Reading Sentences)
        res = self.client.post("/api/learning-path/complete-lesson", json={"lesson_id": 9803})
        self.assertEqual(res.status_code, 200)
        
        # Check that recommendation history status updated to 'completed'
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM recommendation_history WHERE user_id = 8888 AND item_id = 9803")
        status = cursor.fetchone()[0]
        self.assertEqual(status, "completed")
        
        # Check that progress_percentage has updated in users table
        cursor.execute("SELECT progress_percentage, learning_path_progress FROM users WHERE id = 8888")
        row = cursor.fetchone()
        self.assertTrue(row["progress_percentage"] > 0)
        self.assertTrue(row["learning_path_progress"] > 0)
        conn.close()

    def test_4_lesson_access_locking(self):
        # Setup session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 8888
            sess["fullname"] = "Recommendation Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1
            
        # Get path items
        path = generate_personalized_learning_path(8888)
        
        # Step 1 is lesson 9801 (Alphabet Tracing A-Z)
        # Step 2 is lesson 9802 (Word Match Game) -> locked since Step 1 is not completed
        step2_item = next(step for step in path if step["step"] == 2)
        step2_lesson_id = step2_item["lesson_id"]
        
        # Verify access to Step 2 redirects because it is locked
        res = self.client.get(f"/lesson/{step2_lesson_id}")
        self.assertEqual(res.status_code, 302) # Should redirect back to dashboard
        
        # Now mark Step 1 (9801) completed
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lesson_progress (user_id, lesson_id) VALUES (8888, 9801)", ())
        conn.commit()
        conn.close()
        
        # Accessing Step 2 (9802) should now be allowed (returns 200 status code)
        res_after = self.client.get(f"/lesson/{step2_lesson_id}")
        self.assertEqual(res_after.status_code, 200)

    def test_5_endpoints_integration(self):
        # Setup session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 8888
            sess["fullname"] = "Recommendation Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1
            
        # 1. GET /api/recommendations/history
        res_hist = self.client.get("/api/recommendations/history")
        self.assertEqual(res_hist.status_code, 200)
        data_hist = json.loads(res_hist.data)
        self.assertEqual(data_hist["status"], "success")
        
        # 2. GET /api/recommendations/activities
        res_act = self.client.get("/api/recommendations/activities")
        self.assertEqual(res_act.status_code, 200)
        data_act = json.loads(res_act.data)
        self.assertEqual(data_act["status"], "success")
        
        # 3. POST /api/recommendations/refresh
        res_ref = self.client.post("/api/recommendations/refresh")
        self.assertEqual(res_ref.status_code, 200)
        data_ref = json.loads(res_ref.data)
        self.assertEqual(data_ref["status"], "success")

    def test_6_skill_specific_recommendations_update_after_lesson_completion(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET reading_score = 30, writing_score = 80, listening_score = 60, speaking_score = 40 WHERE id = 8888")
        conn.commit()
        conn.close()

        recs = get_content_recommendations(8888)
        skill_titles = [r["title"] for r in recs]
        self.assertTrue(any("Reading" in title or "Sentence" in title for title in skill_titles))

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO lesson_progress (user_id, lesson_id) VALUES (8888, 9803)")
        conn.commit()
        conn.close()

        updated_recs = get_content_recommendations(8888)
        self.assertTrue(len(updated_recs) >= len(recs))

    def test_7_ai_recommendations_generate_skill_specific_lessons_and_lock_path_until_improved(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET reading_score = 35, writing_score = 80, listening_score = 55, speaking_score = 40, weak_skills = 'reading,listening,speaking', strong_skills = 'writing' WHERE id = 8888")
        conn.commit()
        conn.close()

        ai_recs = generate_ai_recommendations(8888)
        self.assertTrue(ai_recs.get("lessons"))
        self.assertTrue(any(lesson.get("skill") in {"reading", "listening", "speaking"} for lesson in ai_recs.get("lessons", [])))

        path = generate_personalized_learning_path(8888)
        step2 = next(step for step in path if step["step"] == 2)
        self.assertTrue(step2["is_locked"])

    def test_8_assessment_questions_are_age_level_and_comprehension_aware(self):
        beginner_questions = get_assessment_questions("English", age=8, learning_level="Beginner")
        self.assertTrue(len(beginner_questions) >= 10)
        self.assertTrue(any(q.get("skill") == "comprehension" for q in beginner_questions))

        advanced_questions = get_assessment_questions("English", age=14, learning_level="Advanced")
        self.assertTrue(len(advanced_questions) >= 12)
        self.assertTrue(any(q.get("skill") == "comprehension" for q in advanced_questions))

if __name__ == "__main__":
    unittest.main()
