with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

old_path_block = """    path_items = [
        {
            "step": 1,
            "title": translate_title(lesson1["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson1.get("category")),
            "lesson_id": lesson1.get("id"),
            "status": step1_status,
            "icon": "bi-journal-bookmark-fill",
            "url": f"/lesson/{lesson1.get('id')}" if lesson1.get('id') else "/week-module"
        },
        {
            "step": 2,
            "title": translate_title(lesson2["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson2.get("category")),
            "lesson_id": lesson2.get("id"),
            "status": step2_status,
            "icon": "bi-123",
            "url": f"/lesson/{lesson2.get('id')}" if lesson2.get('id') else "/week-module"
        },
        {
            "step": 3,
            "title": trans.get("step3_title", "Tracing & Counting Practice"),
            "type": trans.get("type_practice", "Practice Activity"),
            "category": trans.get("cat_practice", "Practice"),
            "status": step3_status,
            "icon": "bi-pencil-square",
            "url": "/learning-games"
        },
        {
            "step": 4,
            "title": trans.get("step5_title", "Daily Skill Assessment"),
            "type": trans.get("type_assessment", "Assessment"),
            "category": trans.get("cat_evaluation", "Evaluation"),
            "status": step4_status,
            "icon": "bi-clipboard-check-fill",
            "url": "/assessment"
        },
        {
            "step": 5,
            "title": "AI Recommendation",
            "type": "AI Guide",
            "category": "AI Rec",
            "status": step5_status,
            "icon": "bi-robot",
            "url": recs[0]["url"] if (len(recs) > 0 and "url" in recs[0]) else "/week-module"
        }
    ]"""

new_path_block = """    # Calculate dynamic sequential lock statuses
    is_step2_locked = (step1_status != "completed")
    is_step3_locked = (step2_status != "completed") or is_step2_locked
    is_step4_locked = (step3_status != "completed") or is_step3_locked
    is_step5_locked = (step4_status != "completed") or is_step4_locked

    path_items = [
        {
            "step": 1,
            "title": translate_title(lesson1["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson1.get("category")),
            "lesson_id": lesson1.get("id"),
            "status": step1_status,
            "is_locked": False,
            "icon": "bi-journal-bookmark-fill",
            "url": f"/lesson/{lesson1.get('id')}" if lesson1.get('id') else "/week-module"
        },
        {
            "step": 2,
            "title": translate_title(lesson2["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson2.get("category")),
            "lesson_id": lesson2.get("id"),
            "status": step2_status,
            "is_locked": is_step2_locked,
            "icon": "bi-123",
            "url": f"/lesson/{lesson2.get('id')}" if lesson2.get('id') else "/week-module"
        },
        {
            "step": 3,
            "title": trans.get("step3_title", "Tracing & Counting Practice"),
            "type": trans.get("type_practice", "Practice Activity"),
            "category": trans.get("cat_practice", "Practice"),
            "status": step3_status,
            "is_locked": is_step3_locked,
            "icon": "bi-pencil-square",
            "url": "/learning-games"
        },
        {
            "step": 4,
            "title": trans.get("step5_title", "Daily Skill Assessment"),
            "type": trans.get("type_assessment", "Assessment"),
            "category": trans.get("cat_evaluation", "Evaluation"),
            "status": step4_status,
            "is_locked": is_step4_locked,
            "icon": "bi-clipboard-check-fill",
            "url": "/assessment"
        },
        {
            "step": 5,
            "title": "AI Recommendation",
            "type": "AI Guide",
            "category": "AI Rec",
            "status": step5_status,
            "is_locked": is_step5_locked,
            "icon": "bi-robot",
            "url": recs[0]["url"] if (len(recs) > 0 and "url" in recs[0]) else "/week-module"
        }
    ]"""

if old_path_block in content:
    content = content.replace(old_path_block, new_path_block)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Learning path steps updated with lock indicators!")
else:
    # Try with raw split normalized to verify
    print("Learning path block not found precisely. Let's do a regex replacement.")
    import re
    # We can search for the block using regex
    pattern = re.compile(r"path_items\s*=\s*\[.*?\}\s*\]", re.DOTALL)
    modified, count = re.subn(pattern, new_path_block, content)
    if count > 0:
        with open("app.py", "w", encoding="utf-8") as f:
            f.write(modified)
        print("Learning path steps updated with lock indicators via regex!")
    else:
        print("Regex update failed!")
