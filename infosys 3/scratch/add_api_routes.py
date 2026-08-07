with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

api_routes = '''
# -------------------------------
# API Endpoints for Recommendations, Paths & Analytics
# -------------------------------

@app.route("/api/learning-path")
@login_required
def api_learning_path():
    user_id = session.get("user_id")
    path = generate_personalized_learning_path(user_id)
    return jsonify({"status": "success", "today_learning_plan": path})

@app.route("/api/recommendations")
@login_required
def api_recommendations():
    user_id = session.get("user_id")
    recs = get_content_recommendations(user_id)
    return jsonify({"status": "success", "recommendations": recs})

@app.route("/api/assessment", methods=["POST"])
@login_required
def api_assessment_post():
    data = request.get_json() or {}
    score = data.get("score", 0)
    correct = data.get("correct", 0)
    total = data.get("total", 0)
    language = data.get("language", "English")
    user_id = session.get("user_id")
    age = session.get("age", 8)
    age_group = get_age_group(age)
    
    prof = classify_score_to_proficiency(score)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_history (user_id, score, correct, total, language, age_group, overall_score)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, score, correct, total, language, age_group, float(score)))
    
    cursor.execute("""
        UPDATE users SET
            current_proficiency = ?,
            learning_level = ?,
            assessment_score = ?
        WHERE id = ?
    """, (prof, prof, float(score), user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "current_proficiency": prof})

@app.route("/api/proficiency")
@login_required
def api_proficiency():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT current_proficiency FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    prof = row["current_proficiency"] if row else "Beginner"
    return jsonify({"current_proficiency": prof})

@app.route("/api/progress")
@login_required
def api_progress():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM assessment_history WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    count = row["count"] if row else 0
    return jsonify({"status": "success", "assessments_completed": count})

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
    prof = predict_user_proficiency(user_id)
    return jsonify({"status": "success", "predicted_proficiency": prof})

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

modified = content.replace("create_database()", api_routes + "create_database()", 1)

with open("app.py", "w", encoding="utf-8") as f:
    f.write(modified)
print("API routes addition complete!")
