with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

new_recs_function = """def get_content_recommendations(user_id, last_lesson_category=None, last_score=None):
    \"\"\"
    AI-Based Personalized Learning Recommendation Engine
    Generates dynamic recommendations based on:
    Proficiency Level, Reading/Writing/Vocabulary/Grammar/Listening/Speaking Scores, Weak/Strong Skills, completed history.
    \"\"\"
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        SELECT age, language, learning_level, current_proficiency,
               reading_score, writing_score, vocabulary_score, grammar_score,
               listening_score, speaking_score, weak_skills, strong_skills
        FROM users WHERE id = ?
    \"\"\", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return []
        
    language = user["language"] or "English"
    proficiency = user["current_proficiency"] or user["learning_level"] or "Beginner"
    
    # Parse weak skills
    weak_str = user["weak_skills"] or ""
    weak_skills = [s.strip().lower() for s in weak_str.split(",") if s.strip()]
    
    # Completed lesson details
    cursor.execute(\"\"\"
        SELECT l.id, l.title, l.category 
        FROM lesson_progress lp
        JOIN lessons l ON lp.lesson_id = l.id
        WHERE lp.user_id = ?
    \"\"\", (user_id,))
    completed = cursor.fetchall()
    completed_ids = {r["id"] for r in completed}
    
    # Latest assessment score if not passed explicitly
    if last_score is None:
        cursor.execute("SELECT score FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        arow = cursor.fetchone()
        if arow:
            last_score = arow["score"]

    # Fetch all available lessons for user language
    cursor.execute(\"\"\"
        SELECT id, title, category, language, content, difficulty 
        FROM lessons 
        WHERE language = ?
    \"\"\", (language,))
    all_lessons = [dict(l) for l in cursor.fetchall()]
    
    # If no lessons exist in DB for this language, fetch all lessons as generic fallbacks
    if not all_lessons:
        cursor.execute("SELECT id, title, category, language, content, difficulty FROM lessons")
        all_lessons = [dict(l) for l in cursor.fetchall()]
        
    available = [l for l in all_lessons if l["id"] not in completed_ids]
    recommendations = []
    
    # Dynamic reasoning map
    reason_map = {
        "reading": "Recommended to build reading fluency and text comprehension.",
        "writing": "Selected to improve writing form, tracing, and sentence spelling.",
        "vocabulary": "Focused on expanding vocabulary and matching word forms.",
        "grammar": "Selected to strengthen sentence syntax and grammar principles.",
        "listening": "Designed to practice phonetic listening and audio feedback.",
        "speaking": "Recommended to practice oral speech recognition and pronunciation."
    }

    # Match difficulty level
    pref_diffs = ["easy"]
    if proficiency.lower() == "intermediate":
        pref_diffs = ["medium", "easy"]
    elif proficiency.lower() == "advanced":
        pref_diffs = ["hard", "medium"]

    # 1. Filter by weak skills first
    for skill in weak_skills:
        for l in available:
            l_cat = (l["category"] or "").lower()
            l_title = (l["title"] or "").lower()
            l_diff = (l["difficulty"] or "easy").lower()
            
            # Check if lesson matches category and user difficulty preference
            if (skill in l_cat or skill in l_title) and l_diff in pref_diffs:
                if l["id"] not in [r["id"] for r in recommendations]:
                    snippet = l["content"].split("[QUIZ]")[0].strip() if l["content"] else ""
                    recommendations.append({
                        "id": l["id"],
                        "title": l["title"],
                        "category": l["category"] or skill.capitalize(),
                        "content": snippet[:90] + "...",
                        "difficulty": l["difficulty"] or "Easy",
                        "reason": reason_map.get(skill, f"Recommended to support your {skill.capitalize()} skills."),
                        "url": f"/lesson/{l['id']}"
                    })
                    if len(recommendations) >= 3:
                        break
        if len(recommendations) >= 3:
            break

    # 2. Progression-based filling: if not enough recommendations, fill with remaining matching difficulty
    for l in available:
        if len(recommendations) >= 5:
            break
        if l["id"] not in [r["id"] for r in recommendations]:
            l_diff = (l["difficulty"] or "easy").lower()
            if l_diff in pref_diffs:
                snippet = l["content"].split("[QUIZ]")[0].strip() if l["content"] else ""
                recommendations.append({
                    "id": l["id"],
                    "title": l["title"],
                    "category": l["category"] or "General",
                    "content": snippet[:90] + "...",
                    "difficulty": l["difficulty"] or "Easy",
                    "reason": f"Recommended lesson for your {proficiency} level.",
                    "url": f"/lesson/{l['id']}"
                })

    # 3. Fallback recommendations if list still empty
    if not recommendations:
        for l in available[:3]:
            snippet = l["content"].split("[QUIZ]")[0].strip() if l["content"] else ""
            recommendations.append({
                "id": l["id"],
                "title": l["title"],
                "category": l["category"] or "General",
                "content": snippet[:90] + "...",
                "difficulty": l["difficulty"] or "Easy",
                "reason": "Suggested starting step for your learning path.",
                "url": f"/lesson/{l['id']}"
            })

    # Log new recommendations in recommendation_history
    for rec in recommendations:
        cursor.execute(\"\"\"
            INSERT INTO recommendation_history (user_id, recommendation_type, item_id, title, category, difficulty, reason, status)
            VALUES (?, 'lesson', ?, ?, ?, ?, ?, 'pending')
        \"\"\", (user_id, rec["id"], rec["title"], rec["category"], rec["difficulty"], rec["reason"]))
    
    # 4. Activity Recommendations
    activity_pool = {
        "easy": ["Tracing Practice", "Fill in the Blanks", "Picture Identification", "Label the Picture"],
        "medium": ["Word Matching", "Sentence Arrangement", "Vocabulary Practice", "Memory Game"],
        "hard": ["Grammar Basics", "Revision Quiz", "Match the Following", "Puzzle Activity"]
    }
    
    level_diff = "easy"
    if proficiency.lower() == "intermediate":
        level_diff = "medium"
    elif proficiency.lower() == "advanced":
        level_diff = "hard"
        
    active_acts = []
    for act_title in activity_pool[level_diff]:
        active_acts.append({
            "title": act_title,
            "difficulty": level_diff.capitalize(),
            "reason": f"Reinforces key {proficiency} skills through interactive practice."
        })
        # log in history
        cursor.execute(\"\"\"
            INSERT INTO recommendation_history (user_id, recommendation_type, title, difficulty, reason, status)
            VALUES (?, 'activity', ?, ?, ?, 'pending')
        \"\"\", (user_id, act_title, level_diff.capitalize(), f"Reinforces key {proficiency} skills through interactive practice."))

    # Store recommended activities and current next suggested lesson in users table
    next_suggested_id = recommendations[0]["id"] if recommendations else None
    cursor.execute(\"\"\"
        UPDATE users 
        SET recommended_activities = ?,
            next_suggested_lesson_id = ?
        WHERE id = ?
    \"\"\", (json.dumps(active_acts), next_suggested_id, user_id))
    
    conn.commit()
    conn.close()
    return recommendations"""

# Locate original get_content_recommendations signature and end
import re
pattern = r"def get_content_recommendations\(user_id, last_lesson_category=None, last_score=None\):.*?return recommendations\s*[\n]*"
modified, count = re.subn(pattern, new_recs_function, content, flags=re.DOTALL)

if count > 0:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(modified)
    print("get_content_recommendations replacement success!")
else:
    print("get_content_recommendations replacement failed!")
