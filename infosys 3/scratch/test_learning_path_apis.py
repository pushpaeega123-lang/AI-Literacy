import unittest
import sqlite3
import json
from app import app, get_db_connection

class TestLearningPathManagementAPIs(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "testing-secret-key"
        
        # Setup clean test user
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE email = 'test_path_apis@example.com'")
        cursor.execute("DELETE FROM study_sessions WHERE user_id = 7777")
        cursor.execute("DELETE FROM recommendation_history WHERE user_id = 7777")
        
        cursor.execute("""
            INSERT INTO users (id, fullname, email, password, age, language, learning_level, current_proficiency,
                               weak_skills, strong_skills, initial_assessment_completed, coins, xp, streak,
                               current_learning_stage, learning_path_progress)
            VALUES (7777, 'Path API Learner', 'test_path_apis@example.com', 'hashedpwd', 8, 'English', 'Beginner', 'Beginner',
                    'reading,writing', 'vocabulary', 1, 100, 200, 3, 'Alphabet', 10.0)
        """)
        
        # Insert test recommendations
        cursor.execute("""
            INSERT INTO recommendation_history (user_id, recommendation_type, item_id, title, category, difficulty, reason, status)
            VALUES (7777, 'lesson', 9801, 'Alphabet Tracing A-Z', 'Alphabet', 'Easy', 'Prerequisite', 'pending')
        """)
        
        conn.commit()
        conn.close()

    def tearDown(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = 7777")
        cursor.execute("DELETE FROM study_sessions WHERE user_id = 7777")
        cursor.execute("DELETE FROM recommendation_history WHERE user_id = 7777")
        conn.commit()
        conn.close()

    def test_1_route_protection_unauthenticated(self):
        # Expect redirects or auth failures when not logged in
        res = self.client.get("/api/progress/summary")
        self.assertEqual(res.status_code, 302)

    def test_2_get_apis_success(self):
        # Mock login session
        with self.client.session_transaction() as sess:
            sess["user_id"] = 7777
            sess["fullname"] = "Path API Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1

        # GET /api/progress/summary
        res1 = self.client.get("/api/progress/summary")
        self.assertEqual(res1.status_code, 200)
        data1 = json.loads(res1.data)
        self.assertEqual(data1["status"], "success")
        self.assertEqual(data1["progress"]["streak"], 3)
        self.assertEqual(data1["progress"]["xp"], 200)

        # GET /api/learner/statistics
        res2 = self.client.get("/api/learner/statistics")
        self.assertEqual(res2.status_code, 200)
        data2 = json.loads(res2.data)
        self.assertEqual(data2["status"], "success")
        self.assertEqual(data2["statistics"]["current_proficiency"], "Beginner")

    def test_3_post_apis_progress_updates(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 7777
            sess["fullname"] = "Path API Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1

        # 1. POST /api/learning-path/submit-practice
        res1 = self.client.post("/api/learning-path/submit-practice", json={"duration": 15, "xp": 25})
        self.assertEqual(res1.status_code, 200)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(duration) FROM study_sessions WHERE user_id = 7777")
        duration = cursor.fetchone()[0]
        self.assertEqual(duration, 15)
        conn.close()

        # 2. POST /api/learning-path/submit-activity
        res2 = self.client.post("/api/learning-path/submit-activity", json={"activity_title": "Interactive Tracing"})
        self.assertEqual(res2.status_code, 200)
        
        # 3. POST /api/learning-path/update-progress
        res3 = self.client.post("/api/learning-path/update-progress")
        self.assertEqual(res3.status_code, 200)

    def test_4_put_delete_apis(self):
        with self.client.session_transaction() as sess:
            sess["user_id"] = 7777
            sess["fullname"] = "Path API Learner"
            sess["language"] = "English"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"
            sess["initial_assessment_completed"] = 1

        # 1. PUT /api/learning-path/status
        res1 = self.client.put("/api/learning-path/status", json={"current_learning_stage": "Words", "current_topic": "Phonics"})
        self.assertEqual(res1.status_code, 200)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT current_learning_stage, current_topic FROM users WHERE id = 7777")
        row = cursor.fetchone()
        self.assertEqual(row["current_learning_stage"], "Words")
        self.assertEqual(row["current_topic"], "Phonics")
        
        # Get dynamic rec ID
        cursor.execute("SELECT id FROM recommendation_history WHERE user_id = 7777 AND status = 'pending' LIMIT 1")
        rec_id = cursor.fetchone()[0]
        conn.close()

        # 2. PUT /api/recommendations/status
        res2 = self.client.put("/api/recommendations/status", json={"recommendation_id": rec_id, "status": "completed"})
        self.assertEqual(res2.status_code, 200)

        # 3. DELETE /api/recommendations/cache
        res3 = self.client.delete("/api/recommendations/cache")
        self.assertEqual(res3.status_code, 200)

if __name__ == "__main__":
    unittest.main()
