with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# 1. Strip the added helpers block
# It starts at index 1076 (def classify_score_to_proficiency) and ends at index 1280 (generate_personalized_learning_path end)
# We find WEEK_MODULE_CONTENT index
week_module_idx = -1
for idx, line in enumerate(lines):
    if "WEEK_MODULE_CONTENT = {" in line:
        week_module_idx = idx
        break

print(f"WEEK_MODULE_CONTENT found at index: {week_module_idx}")

# Strip lines from 1076 up to week_module_idx
clean_lines = lines[:1076] + lines[week_module_idx:]

# 2. Strip the added api block
# In the updated clean_lines list, let's find:
# - start of added api block: @app.route("/api/learning-path") (the first one)
# - end of added api block: def create_database():
first_api_idx = -1
create_db_idx = -1

for idx, line in enumerate(clean_lines):
    if '@app.route("/api/learning-path")' in line and first_api_idx == -1:
        first_api_idx = idx
    if "def create_database():" in line:
        create_db_idx = idx
        break

print(f"First api found at clean index: {first_api_idx}, def create_database found at clean index: {create_db_idx}")

# Let's adjust first_api_idx to include the comment block 4 lines above it if present
if first_api_idx > 4 and "# API Endpoints" in clean_lines[first_api_idx - 2]:
    first_api_idx = first_api_idx - 4

# Strip the muddled API block
final_lines = clean_lines[:first_api_idx] + clean_lines[create_db_idx:]

# 3. Add the unique helpers and unique api endpoints right before create_database
# Find create_database again in final_lines
db_idx = -1
for idx, line in enumerate(final_lines):
    if "def create_database():" in line:
        db_idx = idx
        break

print(f"create_database found at final index: {db_idx}")

new_code = '''
# -------------------------------
# Cognitive Profiling & Assessment Analysis (Milestone 2)
# -------------------------------
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
    cursor.execute("""
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
    """, (reading_score, writing_score, vocabulary_score, grammar_score, listening_score, speaking_score, weak_skills, strong_skills, user_id))
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


# -------------------------------
# Unique REST API Endpoints (Milestone 2)
# -------------------------------

@app.route("/api/next-lesson")
@login_required
def api_next_lesson():
    user_id = session.get("user_id")
    recs = get_content_recommendations(user_id)
    next_l = recs[0] if recs else {"title": "Alphabet Practice", "id": 1}
    return jsonify({"status": "success", "next_lesson": next_l})

@app.route("/api/profile/generate", methods=["POST"])
@login_required
def api_profile_generate():
    user_id = session.get("user_id")
    profile = generate_cognitive_profile(user_id)
    return jsonify({"status": "success", "profile": profile})

@app.route("/api/proficiency/predict", methods=["POST"])
@login_required
def api_proficiency_predict():
    user_id = session.get("user_id")
    # use the original prediction method
    pred_prof = predict_user_proficiency(user_id, update_db=True)
    return jsonify({"status": "success", "predicted_proficiency": pred_prof["current_proficiency"]})

@app.route("/api/profile/update", methods=["POST"])
@login_required
def api_profile_update_endpoint():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users SET
            fullname = ?,
            dob = ?,
            gender = ?,
            avatar = ?,
            current_mascot_dress = ?,
            preferred_language = ?,
            learning_language = ?
        WHERE id = ?
    """, (
        data.get("fullname"),
        data.get("dob"),
        data.get("gender"),
        data.get("avatar"),
        data.get("current_mascot_dress"),
        data.get("preferred_language"),
        data.get("learning_language"),
        user_id
    ))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Profile updated successfully"})

@app.route("/api/profile/retrieve")
@login_required
def api_profile_retrieve():
    user_id = session.get("user_id")
    profile = generate_cognitive_profile(user_id)
    return jsonify({"status": "success", "profile": profile})

@app.route("/api/skills/weak")
@login_required
def api_skills_weak():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT weak_skills FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    weak = [s.strip() for s in row["weak_skills"].split(",") if s.strip()] if (row and row["weak_skills"]) else []
    return jsonify({"status": "success", "weak_skills": weak})

@app.route("/api/skills/strong")
@login_required
def api_skills_strong():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT strong_skills FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    strong = [s.strip() for s in row["strong_skills"].split(",") if s.strip()] if (row and row["strong_skills"]) else []
    return jsonify({"status": "success", "strong_skills": strong})

@app.route("/api/assessment/update-analysis", methods=["POST"])
@login_required
def api_assessment_update_analysis():
    user_id = session.get("user_id")
    profile = generate_cognitive_profile(user_id)
    return jsonify({"status": "success", "message": "Assessment analysis updated", "profile": profile})

@app.route("/api/profile/refresh-predictions", methods=["POST"])
@login_required
def api_profile_refresh_predictions():
    user_id = session.get("user_id")
    profile = generate_cognitive_profile(user_id)
    return jsonify({"status": "success", "message": "Predictions refreshed", "profile": profile})

'''

output_lines = final_lines[:db_idx] + [new_code] + final_lines[db_idx:]

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print("Duplicates cleaned and original structures restored successfully!")
