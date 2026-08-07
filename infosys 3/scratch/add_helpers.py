with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

helpers_code = '''
def classify_score_to_proficiency(score):
    try:
        score_val = float(score)
    except (ValueError, TypeError):
        score_val = 0.0
    if score_val <= 35:
        return "Beginner"
    elif score_val <= 69:
        return "Basic"
    elif score_val <= 89:
        return "Intermediate"
    else:
        return "Advanced"

def predict_user_proficiency(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT score FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 3", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "Beginner"
    avg_score = sum(r["score"] for r in rows) / len(rows)
    return classify_score_to_proficiency(avg_score)

def generate_cognitive_profile(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {}
        
    cursor.execute("SELECT * FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    history = cursor.fetchall()
    conn.close()
    
    total_assessments = len(history)
    last_assessment_date = history[0]["timestamp"] if history else "Never"
    
    reading_score = user["reading_score"] or 0.0
    writing_score = user["writing_score"] or 0.0
    vocabulary_score = user["vocabulary_score"] or 0.0
    grammar_score = user["grammar_score"] or 0.0
    listening_score = user["listening_score"] or 0.0
    speaking_score = user["speaking_score"] or 0.0
    
    if total_assessments > 0 and reading_score == 0 and writing_score == 0:
        last_score = history[0]["score"]
        reading_score = last_score
        writing_score = max(0, last_score - 10)
        vocabulary_score = max(0, last_score - 5)
        grammar_score = max(0, last_score - 15)
        listening_score = last_score
        speaking_score = last_score
        
    overall_score = user["assessment_score"] or (history[0]["score"] if history else 0.0)
    
    confidence_score = 50.0
    if total_assessments > 1:
        scores = [h["score"] for h in history]
        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        std_dev = variance ** 0.5
        confidence_score = max(10.0, min(100.0, 100.0 - std_dev))
    elif total_assessments == 1:
        confidence_score = 75.0 if overall_score >= 50 else 50.0
        
    avg_time = sum(h["completion_time"] for h in history) / total_assessments if total_assessments > 0 else 0
    if avg_time == 0:
        learning_speed = "Normal"
        speed_index = 75
    elif avg_time < 120:
        learning_speed = "Fast Learner"
        speed_index = 90
    elif avg_time < 300:
        learning_speed = "Moderate Pace"
        speed_index = 70
    else:
        learning_speed = "Steady Learner"
        speed_index = 50
        
    weak_list = []
    strong_list = []
    
    skills_map = {
        "Reading": reading_score,
        "Writing": writing_score,
        "Vocabulary": vocabulary_score,
        "Grammar": grammar_score,
        "Listening": listening_score,
        "Speaking": speaking_score
    }
    
    for skill, s_score in skills_map.items():
        if s_score >= 70:
            strong_list.append(skill)
        else:
            weak_list.append(skill)
            
    weak_skills = ", ".join(weak_list) if weak_list else "None"
    strong_skills = ", ".join(strong_list) if strong_list else "None"
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        UPDATE users SET
            reading_score = ?,
            writing_score = ?,
            vocabulary_score = ?,
            grammar_score = ?,
            listening_score = ?,
            speaking_score = ?,
            weak_skills = ?,
            strong_skills = ?
        WHERE id = ?
    \"\"\", (reading_score, writing_score, vocabulary_score, grammar_score, listening_score, speaking_score, weak_skills, strong_skills, user_id))
    conn.commit()
    conn.close()
    
    profile = {
        "overall_level": user["learning_level"] or "Beginner",
        "reading_ability": reading_score,
        "writing_ability": writing_score,
        "vocabulary_level": vocabulary_score,
        "grammar_understanding": grammar_score,
        "listening_readiness": listening_score,
        "speaking_readiness": speaking_score,
        "confidence_level": confidence_score,
        "learning_speed": learning_speed,
        "speed_index": speed_index,
        "accuracy_percentage": overall_score,
        "weak_skills": weak_skills,
        "strong_skills": strong_skills,
        "repeated_mistakes": "Alphabet Confusions, Pronunciation Gaps" if "Speaking" in weak_list or "Reading" in weak_list else "Spelling Inaccuracies",
        "improvement_areas": "Reading Fluency, Vocabulary Expansion",
        "readiness_index": int(overall_score * 0.9 + confidence_score * 0.1),
        "last_assessment_date": last_assessment_date,
        "total_assessments": total_assessments
    }
    return profile

def get_content_recommendations(user_id, last_score=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT language, learning_level, current_proficiency FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return []
    
    lang = user["language"] or "English"
    prof = user["current_proficiency"] or "Beginner"
    
    if last_score is not None:
        prof = classify_score_to_proficiency(last_score)
        
    difficulty = "Easy"
    if prof == "Intermediate":
        difficulty = "Medium"
    elif prof == "Advanced":
        difficulty = "Hard"
        
    cursor.execute("SELECT * FROM lessons WHERE language = ? AND difficulty = ? LIMIT 5", (lang, difficulty))
    lessons = cursor.fetchall()
    
    if not lessons:
        cursor.execute("SELECT * FROM lessons WHERE language = ? LIMIT 5", (lang,))
        lessons = cursor.fetchall()
        
    if not lessons:
        cursor.execute("SELECT * FROM lessons LIMIT 5")
        lessons = cursor.fetchall()
        
    conn.close()
    
    recs = []
    for lesson in lessons:
        recs.append({
            "id": lesson["id"],
            "title": lesson["title"],
            "category": lesson["category"],
            "difficulty": lesson["difficulty"],
            "content": lesson["content"],
            "reason": f"Recommended for your {prof} level based on assessment performance."
        })
    return recs

def generate_personalized_learning_path(user_id):
    recs = get_content_recommendations(user_id)
    lesson_title_1 = recs[0]["title"] if len(recs) > 0 else "Alphabet Practice"
    lesson_title_2 = recs[1]["title"] if len(recs) > 1 else "Word Reading"
    lesson_title_3 = recs[2]["title"] if len(recs) > 2 else "Sentence Practice"
    
    path = [
        {"step": 1, "type": "Lesson", "title": lesson_title_1, "url": "/lesson/1"},
        {"step": 2, "type": "Practice", "title": lesson_title_2, "url": "/practice"},
        {"step": 3, "type": "Game", "title": "Play Word Game", "url": "/learning-games"},
        {"step": 4, "type": "Assessment", "title": "Check Progress", "url": "/assessment"},
        {"step": 5, "type": "AI Guide", "title": "Chat with Lumi", "url": "/chat"}
    ]
    return path

'''

modified = content.replace("WEEK_MODULE_CONTENT = {", helpers_code + "WEEK_MODULE_CONTENT = {", 1)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(modified)
print("Helpers addition complete!")
