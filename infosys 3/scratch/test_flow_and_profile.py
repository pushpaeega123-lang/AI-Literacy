import sqlite3
from datetime import date, datetime
import app

def calculate_age_test(dob_str):
    return app.calculate_age(dob_str)

def run_tests():
    print("=========================================")
    print("RUNNING VERIFICATION TESTS")
    print("=========================================\n")

    # 1. Test Age Calculation from DOB
    print("--- 1. Testing Age Calculation ---")
    today = date.today()
    
    # DOB for Age 2 (approx 2 years ago)
    dob_2 = f"{today.year - 2}-{today.month:02d}-{today.day:02d}"
    age_2 = calculate_age_test(dob_2)
    print(f"DOB '{dob_2}' -> Calculated Age: {age_2} (Expected: 2)")
    assert age_2 == 2, f"Expected 2, got {age_2}"

    # DOB for Age 4
    dob_4 = f"{today.year - 4}-{today.month:02d}-{today.day:02d}"
    age_4 = calculate_age_test(dob_4)
    print(f"DOB '{dob_4}' -> Calculated Age: {age_4} (Expected: 4)")
    assert age_4 == 4, f"Expected 4, got {age_4}"

    # DOB for Age 5
    dob_5 = f"{today.year - 5}-{today.month:02d}-{today.day:02d}"
    age_5 = calculate_age_test(dob_5)
    print(f"DOB '{dob_5}' -> Calculated Age: {age_5} (Expected: 5)")
    assert age_5 == 5, f"Expected 5, got {age_5}"

    # DOB for Age 7
    dob_7 = f"{today.year - 7}-{today.month:02d}-{today.day:02d}"
    age_7 = calculate_age_test(dob_7)
    print(f"DOB '{dob_7}' -> Calculated Age: {age_7} (Expected: 7)")
    assert age_7 == 7, f"Expected 7, got {age_7}"

    # DOB for Age 8
    dob_8 = f"{today.year - 8}-{today.month:02d}-{today.day:02d}"
    age_8 = calculate_age_test(dob_8)
    print(f"DOB '{dob_8}' -> Calculated Age: {age_8} (Expected: 8)")
    assert age_8 == 8, f"Expected 8, got {age_8}"

    print("Age Calculation Test: PASSED!\n")

    # 2. Test Placement & Assessment Questions by Age
    print("--- 2. Testing Assessment Questions & Flow by Age ---")
    
    # Age 5-7 -> Placement Activity
    qs_5 = app.get_assessment_questions("English", age=5, learning_level="Beginner", mode="placement")
    print(f"Age 5 Placement Questions Count: {len(qs_5)}")
    print(f"First Question Prompt: {qs_5[0]['prompt']}")
    assert len(qs_5) > 0

    # Age 8+ -> Formal Assessment
    qs_8 = app.get_assessment_questions("English", age=8, learning_level="Beginner")
    print(f"Age 8 Assessment Questions Count: {len(qs_8)}")
    assert len(qs_8) > 0
    print("Assessment Questions Test: PASSED!\n")

    # 3. Test Profile Update via App Client
    print("--- 3. Testing Profile Update Logic & Database Persistence ---")
    app.app.config['TESTING'] = True
    app.app.config['SECRET_KEY'] = 'testsecret'
    
    with app.app.test_client() as client:
        # Create test user in DB
        conn = app.get_db_connection()
        cursor = conn.cursor()
        test_email = "testuser_profile@example.com"
        cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
        cursor.execute("""
            INSERT INTO users (fullname, email, password, dob, age, gender, avatar, current_mascot_dress, language, learning_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("Old Name", test_email, "hash", "2018-01-01", 8, "Female", "Cat", "Default", "English", "Beginner"))
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        with client.session_transaction() as sess:
            sess["user_id"] = user_id
            sess["fullname"] = "Old Name"
            sess["email"] = test_email
            sess["language"] = "English"
            sess["learning_level"] = "Beginner"
            sess["age"] = 8

        # Perform JSON profile update request
        new_dob = f"{today.year - 6}-05-15" # Age 6
        update_payload = {
            "fullname": "Updated Super Learner",
            "dob": new_dob,
            "gender": "Male",
            "avatar": "Panda",
            "current_mascot_dress": "crown",
            "language": "Telugu",
            "learning_level": "Intermediate"
        }
        
        response = client.post("/update_profile", json=update_payload)
        data = response.get_json()
        print("Response JSON status:", data.get("status"))
        print("Response message:", data.get("message"))
        assert data.get("status") == "success"
        assert data.get("message") == "Profile updated successfully."

        # Verify DB content
        conn = app.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT fullname, dob, age, gender, avatar, current_mascot_dress, language, learning_level FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        print("DB Verified Values:", dict(row))
        assert row["fullname"] == "Updated Super Learner"
        assert row["dob"] == new_dob
        assert int(row["age"]) == 6 # Calculated dynamically from DOB!
        assert row["gender"] == "Male"
        assert row["avatar"] == "Panda"
        assert row["current_mascot_dress"] == "crown"
        assert row["language"] == "Telugu"
        assert row["learning_level"] == "Intermediate"

        print("Profile Update & Database Persistence Test: PASSED!\n")

    print("=========================================")
    print("ALL VERIFICATION TESTS PASSED SUCCESSFULLY!")
    print("=========================================")

if __name__ == "__main__":
    run_tests()
