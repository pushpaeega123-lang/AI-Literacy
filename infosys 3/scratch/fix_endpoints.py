with open("app.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# We want to replace lines from index 2237 (the line before '# -------------------------------')
# up to index 2340 (the line before 'def create_database():')

start_idx = -1
end_idx = -1

for idx, line in enumerate(lines):
    if "# Unique REST API Endpoints (Milestone 2)" in line:
        start_idx = idx - 1
    if "def create_database():" in line:
        end_idx = idx
        break

print(f"Start index: {start_idx}, End index: {end_idx}")

new_unique_apis = '''
# -------------------------------
# Unique REST API Endpoints (Milestone 2)
# -------------------------------

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
    pred_prof = predict_user_proficiency(user_id, update_db=True)
    return jsonify({"status": "success", "predicted_proficiency": pred_prof["current_proficiency"]})

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

output_lines = lines[:start_idx] + [new_unique_apis] + lines[end_idx:]

with open("app.py", "w", encoding="utf-8") as f:
    f.writelines(output_lines)

print("Duplicate endpoints removed and unique REST APIs optimized!")
