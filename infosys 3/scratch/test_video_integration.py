import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
sys.stdout.reconfigure(encoding='utf-8')

from app import app, get_video_folder_for_age, get_local_videos_for_learner

class TestVideoSystem(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_age_mapping_logic(self):
        self.assertEqual(get_video_folder_for_age(1), "age1")
        self.assertEqual(get_video_folder_for_age(2), "age1")
        self.assertEqual(get_video_folder_for_age(3), "age3")
        self.assertEqual(get_video_folder_for_age(4), "age3")
        self.assertEqual(get_video_folder_for_age(5), "age5")
        print("[TEST PASSED] Age Mapping Logic (1->age1, 2->age1, 3->age3, 4->age3, 5->age5)")

    def test_all_language_and_age_video_files(self):
        languages = ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Marathi"]
        ages = [1, 2, 3, 4, 5]

        for lang in languages:
            for age in ages:
                videos = get_local_videos_for_learner(lang, age)
                folder = get_video_folder_for_age(age)
                self.assertTrue(len(videos) > 0, f"No videos found for {lang} Age {age} in {folder}")
                for v in videos:
                    self.assertTrue(v["video_url"].startswith(f"/static/videos/{lang.lower()}/{folder}/"))
                    self.assertTrue(v["video_url"].endswith(".mp4"))
                    rel_path = v["video_url"].lstrip("/").replace("/", os.sep)
                    abs_path = os.path.join(app.root_path, rel_path)
                    self.assertTrue(os.path.exists(abs_path), f"File does not exist on disk: {abs_path}")
        print("[TEST PASSED] All 6 Languages x 5 Ages physical MP4 files verified on disk.")

    def test_missing_video_error_handling(self):
        videos = get_local_videos_for_learner("NonExistentLang", 1)
        self.assertEqual(videos, [])
        print("[TEST PASSED] Missing video error handling returned empty list without crashing.")

    def test_flask_toddler_api_route(self):
        languages = ["English", "Telugu", "Hindi", "Tamil", "Kannada", "Marathi"]
        with self.app.session_transaction() as sess:
            sess["user_id"] = 1
            sess["email"] = "demo@gmail.com"

        for lang in languages:
            for age in [1, 2, 3, 4, 5]:
                with self.app.session_transaction() as sess:
                    sess["language"] = lang
                    sess["age"] = age

                res = self.app.get("/api/toddler/videos")
                self.assertEqual(res.status_code, 200)
                data = res.get_json()
                self.assertIsInstance(data, list)
                self.assertTrue(len(data) > 0)
                folder = get_video_folder_for_age(age)
                for item in data:
                    self.assertIn(f"/static/videos/{lang.lower()}/{folder}/", item["video_url"])
        print("[TEST PASSED] Flask /api/toddler/videos API endpoints verified.")

    def test_flask_lesson_route(self):
        with self.app.session_transaction() as sess:
            sess["user_id"] = 1
            sess["email"] = "demo@gmail.com"
            sess["language"] = "English"
            sess["age"] = 3

        res = self.app.get("/lesson/9828")
        self.assertEqual(res.status_code, 200)
        html = res.get_data(as_text=True)
        self.assertIn("<video", html)
        self.assertIn("/static/videos/english/age3/", html)
        self.assertNotIn("<iframe", html)
        self.assertNotIn("youtube.com", html)
        print("[TEST PASSED] Lesson route renders HTML5 <video> tag with local MP4 and zero YouTube embeds.")

if __name__ == "__main__":
    unittest.main()
