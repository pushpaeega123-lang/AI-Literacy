import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import unittest
import sqlite3
import json
from app import app, get_db_connection
import language_learning_service as lls

class TestMultilingualLearningMode(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "testing-secret-key"
        
        # Insert test user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = 'test_multi@example.com'")
        cursor.execute("""
            INSERT INTO users (id, fullname, email, password, age, language, learning_level, current_proficiency,
                               initial_assessment_completed, preferred_language, learning_language)
            VALUES (6666, 'Multi Learner', 'test_multi@example.com', 'pwd', 8, 'English', 'Beginner', 'Beginner',
                    1, 'English', '')
        """)
        
        # Clean progress database for user
        cursor.execute("DELETE FROM language_progress WHERE user_id = 6666")
        
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = 6666")
        cursor.execute("DELETE FROM language_progress WHERE user_id = 6666")
        conn.commit()
        conn.close()

    def test_1_identical_languages_validation(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 6666
            sess["fullname"] = "Multi Learner"
            sess["language"] = "English"

        # POST setting known and target identical should fail
        res = self.client.post("/api/multilingual/set-languages", json={
            "known_lang": "English",
            "target_lang": "English"
        })
        self.assertEqual(res.status_code, 400)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "error")
        self.assertIn("cannot be the same", data["message"])

    def test_2_curriculum_seeding_and_unlock_flow(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 6666
            sess["fullname"] = "Multi Learner"
            sess["language"] = "English"

        # 1. Select English -> Tamil
        res = self.client.post("/api/multilingual/set-languages", json={
            "known_lang": "English",
            "target_lang": "Tamil"
        })
        self.assertEqual(res.status_code, 200)

        # 2. Get database details and ensure vocabulary populated
        pair_id = lls.get_or_create_language_pair("English", "Tamil")
        self.assertTrue(pair_id > 0)
        
        path = lls.get_user_learning_path(6666, pair_id)
        self.assertEqual(len(path), 17) # 17 curriculum lessons
        
        # Step 1 should be unlocked, Step 2 should be locked
        self.assertEqual(path[0]["status"], "unlocked")
        self.assertEqual(path[1]["status"], "locked")
        
        lesson1_id = path[0]["id"]
        lesson2_id = path[1]["id"]

        # 3. Access locked lesson 2 directly -> should redirect
        res_lock = self.client.get(f"/multilingual-learning/lesson/{lesson2_id}")
        self.assertEqual(res_lock.status_code, 302)

        # 4. Access unlocked lesson 1 -> should succeed (200)
        res_ok = self.client.get(f"/multilingual-learning/lesson/{lesson1_id}")
        self.assertEqual(res_ok.status_code, 200)

        # 5. Submit lesson 1 completion
        res_sub = self.client.post("/api/multilingual/submit-lesson", json={
            "lesson_id": lesson1_id,
            "pronunciation_score": 85.0,
            "quiz_score": 100.0
        })
        self.assertEqual(res_sub.status_code, 200)

        # 6. Re-evaluate path: lesson 2 should now be unlocked!
        new_path = lls.get_user_learning_path(6666, pair_id)
        self.assertEqual(new_path[0]["status"], "completed")
        self.assertEqual(new_path[1]["status"], "unlocked")

    def test_3_pronunciation_similarity(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 6666
            
        # Exact match
        res_exact = self.client.post("/api/multilingual/compare-voice", json={
            "expected": "வணக்கம்",
            "spoken": "வணக்கம்"
        })
        data_exact = json.loads(res_exact.data)
        self.assertEqual(data_exact["similarity"], 100.0)

        # Mismatch
        res_mismatch = self.client.post("/api/multilingual/compare-voice", json={
            "expected": "வணக்கம்",
            "spoken": "நன்றி"
        })
        data_mismatch = json.loads(res_mismatch.data)
        self.assertTrue(data_mismatch["similarity"] < 100.0)

if __name__ == "__main__":
    unittest.main()
