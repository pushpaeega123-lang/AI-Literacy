import unittest
from app import app, get_db_connection

class AdminDashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        
        # Verify default test admin exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email='admin@example.com' AND role='admin'")
        self.admin_row = cursor.fetchone()
        
        cursor.execute("SELECT id FROM users WHERE role='student' LIMIT 1")
        self.student_row = cursor.fetchone()
        conn.close()

    def test_admin_flow(self):
        print("\n--- Running Programmatic Integration Test ---")
        
        # 1. Admin Login Redirection
        print("Testing Admin Login with admin@example.com...")
        response = self.app.post('/admin/login', data={
            'email': 'admin@example.com',
            'password': 'AdminPassword123!'
        }, follow_redirects=False)
        
        self.assertEqual(response.status_code, 302)
        redirect_target = response.headers.get("Location")
        print(f"Login redirected successfully to: {redirect_target}")
        self.assertTrue("admin/dashboard" in redirect_target or "admin" in redirect_target)
        
        # Create persistent session
        with self.app.session_transaction() as sess:
            sess['user_id'] = self.admin_row['id']
            sess['fullname'] = 'Platform Administrator'
            sess['email'] = 'admin@example.com'
            sess['role'] = 'admin'
            sess['language'] = 'English'

        # 2. Get Admin Dashboard
        print("Testing access to Admin Dashboard...")
        dashboard_response = self.app.get('/admin/dashboard')
        self.assertEqual(dashboard_response.status_code, 200)
        html = dashboard_response.data.decode('utf-8')
        
        # Verify sidebar components
        self.assertIn("User Management", html)
        self.assertIn("Lesson Content Management", html)
        self.assertIn("Configure AI Rules Engine", html)
        self.assertIn("Supported Languages", html)
        self.assertIn("completionsChart", html)
        print("Admin Dashboard HTML loaded successfully containing charts, sidebar, and stats.")

        # 3. Access Guard on Learner Features
        print("Testing access control guard: Admin accessing student /assessment...")
        assessment_response = self.app.get('/assessment', follow_redirects=False)
        self.assertEqual(assessment_response.status_code, 302)
        self.assertTrue("admin/dashboard" in assessment_response.headers.get("Location"))
        print("Access guard successfully redirected admin away from student assessment page.")

        # 4. Learner Progress JSON API
        if self.student_row:
            student_id = self.student_row['id']
            print(f"Testing Learner Progress API for student ID {student_id}...")
            api_response = self.app.get(f'/admin/learner/{student_id}/progress')
            self.assertEqual(api_response.status_code, 200)
            data = api_response.get_json()
            self.assertTrue(data['success'])
            self.assertIn('user', data)
            self.assertIn('lessons', data)
            self.assertIn('assessments', data)
            self.assertIn('voice_practice', data)
            print("Learner Progress JSON API returned successfully.")
        else:
            print("No students in DB to test API.")
            
        print("--- Integration Test Completed Successfully ---")

if __name__ == "__main__":
    unittest.main()
