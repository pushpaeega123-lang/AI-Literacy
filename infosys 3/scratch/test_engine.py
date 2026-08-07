import unittest
import json
import sqlite3
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import (
    app, get_db_connection, create_database,
    classify_score_to_proficiency, predict_user_proficiency,
    get_content_recommendations, generate_personalized_learning_path
)

class TestPersonalizedLearningEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_database()
        cls.client = app.test_client()
        cls.client.testing = True

    def setUp(self):
        # Create a test user in SQLite database
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = 9999")
        cursor.execute("DELETE FROM assessment_history WHERE user_id = 9999")
        cursor.execute("DELETE FROM lesson_progress WHERE user_id = 9999")
        cursor.execute("""
            INSERT INTO users (id, fullname, email, password, age, language, learning_level, current_proficiency, initial_assessment_completed)
            VALUES (9999, 'Test Learner', 'engine_test@example.com', 'pass', 8, 'Telugu', 'Beginner', 'Beginner', 1)
        """)
        conn.commit()
        conn.close()

    def test_1_proficiency_prediction_rules(self):
        """Test exact score boundaries for learner proficiency prediction"""
        self.assertEqual(classify_score_to_proficiency(0), "Beginner")
        self.assertEqual(classify_score_to_proficiency(35), "Beginner")
        self.assertEqual(classify_score_to_proficiency(40), "Basic")
        self.assertEqual(classify_score_to_proficiency(65), "Basic")
        self.assertEqual(classify_score_to_proficiency(70), "Intermediate")
        self.assertEqual(classify_score_to_proficiency(85), "Intermediate")
        self.assertEqual(classify_score_to_proficiency(90), "Advanced")
        self.assertEqual(classify_score_to_proficiency(100), "Advanced")
        print("[OK] Proficiency classification boundary rules passed!")

    def test_2_adaptive_recommendation_model(self):
        """Test recommendation changes based on assessment score"""
        # Low score (45%) test
        recs_low = get_content_recommendations(9999, last_score=45)
        self.assertTrue(len(recs_low) > 0)
        self.assertIn("reason", recs_low[0])
        top_title = recs_low[0]['title'].encode('ascii', 'replace').decode('ascii')
        print(f"[OK] Low score (45%) recommendations count: {len(recs_low)}, Top recommendation: {top_title}")

        # High score (95%) test
        recs_high = get_content_recommendations(9999, last_score=95)
        self.assertTrue(len(recs_high) > 0)
        top_high_title = recs_high[0]['title'].encode('ascii', 'replace').decode('ascii')
        print(f"[OK] High score (95%) recommendations count: {len(recs_high)}, Top recommendation: {top_high_title}")

    def test_3_learning_path_generation(self):
        """Test 5-step daily personalized learning path generation"""
        path = generate_personalized_learning_path(9999)
        self.assertEqual(len(path), 5)
        self.assertEqual(path[0]["step"], 1)
        self.assertIn("assessment", path[3]["url"])
        self.assertEqual(path[4]["type"], "AI Guide")
        print("[OK] 5-Step Learning Path generated successfully!")

    def test_4_api_endpoints_integration(self):
        """Test Flask REST APIs with active session"""
        with self.client.session_transaction() as sess:
            sess["user_id"] = 9999
            sess["fullname"] = "Test Learner"
            sess["language"] = "Telugu"
            sess["age"] = 8
            sess["learning_level"] = "Beginner"

        # 1. GET /api/learning-path
        res_path = self.client.get("/api/learning-path")
        self.assertEqual(res_path.status_code, 200)
        data_path = res_path.get_json()
        self.assertEqual(data_path["status"], "success")
        self.assertEqual(len(data_path["today_learning_plan"]), 5)
        print("[OK] API GET /api/learning-path verified!")

        # 2. GET /api/recommendations
        res_recs = self.client.get("/api/recommendations")
        self.assertEqual(res_recs.status_code, 200)
        data_recs = res_recs.get_json()
        self.assertEqual(data_recs["status"], "success")
        print("[OK] API GET /api/recommendations verified!")

        # 3. POST /api/assessment
        res_assess = self.client.post("/api/assessment", json={"score": 85, "correct": 8, "total": 10, "language": "Telugu"})
        self.assertEqual(res_assess.status_code, 200)
        data_assess = res_assess.get_json()
        self.assertEqual(data_assess["status"], "success")
        self.assertEqual(data_assess["current_proficiency"], "Intermediate")
        print(f"[OK] API POST /api/assessment verified! Updated proficiency: {data_assess['current_proficiency']}")

        # 4. GET /api/proficiency
        res_prof = self.client.get("/api/proficiency")
        self.assertEqual(res_prof.status_code, 200)
        data_prof = res_prof.get_json()
        self.assertEqual(data_prof["current_proficiency"], "Intermediate")
        print("[OK] API GET /api/proficiency verified!")

        # 5. GET /api/progress
        res_prog = self.client.get("/api/progress")
        self.assertEqual(res_prog.status_code, 200)
        data_prog = res_prog.get_json()
        self.assertEqual(data_prog["status"], "success")
        self.assertEqual(data_prog["assessments_completed"], 1)
        print("[OK] API GET /api/progress verified!")

        # 6. GET /api/next-lesson
        res_next = self.client.get("/api/next-lesson")
        self.assertEqual(res_next.status_code, 200)
        data_next = res_next.get_json()
        self.assertEqual(data_next["status"], "success")
        self.assertIn("title", data_next["next_lesson"])
        next_title = data_next['next_lesson']['title'].encode('ascii', 'replace').decode('ascii')
        print(f"[OK] API GET /api/next-lesson verified! Next lesson: {next_title}")

if __name__ == "__main__":
    unittest.main()
