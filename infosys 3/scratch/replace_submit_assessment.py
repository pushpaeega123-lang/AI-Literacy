import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Define the new submit_assessment function
new_submit_route = """@app.route("/submit_assessment", methods=["POST"])
@login_required
def submit_assessment():
    language = session.get("language", "English")
    translations = get_translations(language)
    questions = session.get("assessment_questions")

    if not questions:
        flash("Your assessment session has expired. Please retake the assessment.", "warning")
        return redirect(url_for("assessment"))

    # Calculate time taken
    start_time = session.get("assessment_start_time", time.time())
    time_taken = int(time.time() - start_time)

    correct = 0
    total = len(questions)
    review_items = []

    # Category counters
    cat_corrects = {
        "reading": 0, "writing": 0, "vocabulary": 0,
        "grammar": 0, "listening": 0, "speaking": 0
    }
    cat_totals = {
        "reading": 0, "writing": 0, "vocabulary": 0,
        "grammar": 0, "listening": 0, "speaking": 0
    }

    for question in questions:
        q_type = question.get("type", "reading").lower()
        if q_type not in cat_corrects:
            q_type = "reading"  # fallback
            
        user_answer = request.form.get(question["name"], "")
        expected_answer = str(question["answer"]).strip()
        
        is_correct = False
        if q_type == "speaking":
            is_correct = get_similarity_score(user_answer, expected_answer) >= 0.75
        else:
            is_correct = normalize_text(user_answer) == normalize_text(expected_answer)
            
        cat_totals[q_type] += 1
        if is_correct:
            correct += 1
            cat_corrects[q_type] += 1

        review_items.append({
            "prompt": question.get("hint") if q_type == "speaking" else (question.get("prompt") if question.get("prompt") else "Question"),
            "user_answer": user_answer if user_answer.strip() else "Not Attempted",
            "correct_answer": expected_answer,
            "is_correct": is_correct,
            "explanation": question.get("explanation", "Practice is key to mastering language rules.")
        })

    score = int((correct / total) * 100) if total else 0
    attempted = sum(1 for q in questions if request.form.get(q["name"], "").strip())
    incorrect = total - correct
    pass_status = "Pass" if score >= 50 else "Fail"

    # Calculate category scores
    cat_scores = {}
    for cat in cat_corrects:
        tot = cat_totals[cat]
        cat_scores[cat] = int((cat_corrects[cat] / tot) * 100) if tot > 0 else 0

    # Determine learner proficiency level (based only on performance, not age)
    if score >= 85:
        learner_level = "Advanced"
    elif score >= 60:
        learner_level = "Intermediate"
    elif score >= 35:
        learner_level = "Basic"
    else:
        learner_level = "Beginner"

    # Determine strong & weak skills lists
    strong_list = []
    weak_list = []
    for skill, s_score in cat_scores.items():
        skill_name = skill.capitalize()
        if s_score >= 70:
            strong_list.append(skill_name)
        else:
            weak_list.append(skill_name)

    strong_skills_str = ", ".join(strong_list) if strong_list else "None"
    weak_skills_str = ", ".join(weak_list) if weak_list else "None"

    user_id = session.get("user_id")
    age = session.get("age")
    age_group = get_age_group(age)
    
    # 1. Record attempt in assessment_history table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        INSERT INTO assessment_history (
            user_id, score, correct, total, language, age_group, wrong_answers, accuracy, 
            completion_time, reading_score, writing_score, vocabulary_score, grammar_score, 
            listening_score, speaking_score, overall_score, learner_level, weak_skills, strong_skills
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    \"\"\", (
        user_id, score, correct, total, language, age_group, incorrect, float(score),
        time_taken, cat_scores["reading"], cat_scores["writing"], cat_scores["vocabulary"],
        cat_scores["grammar"], cat_scores["listening"], cat_scores["speaking"], float(score),
        learner_level, weak_skills_str, strong_skills_str
    ))
    conn.commit()
    conn.close()

    # 2. Update user profile details
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(\"\"\"
        UPDATE users SET
            initial_assessment_completed = 1,
            learning_level = ?,
            current_proficiency = ?,
            assessment_score = ?,
            reading_score = ?,
            writing_score = ?,
            vocabulary_score = ?,
            grammar_score = ?,
            listening_score = ?,
            speaking_score = ?,
            weak_skills = ?,
            strong_skills = ?
        WHERE id = ?
    \"\"\", (
        learner_level, learner_level, float(score),
        cat_scores["reading"], cat_scores["writing"], cat_scores["vocabulary"],
        cat_scores["grammar"], cat_scores["listening"], cat_scores["speaking"],
        weak_skills_str, strong_skills_str, user_id
    ))
    conn.commit()
    conn.close()

    # Award custom XP based on category scores
    xp_reward = (cat_corrects["speaking"] * 30) + (cat_corrects["listening"] * 30) + (cat_corrects["reading"] * 20) + (cat_corrects["writing"] * 20) + ((cat_corrects["vocabulary"] + cat_corrects["grammar"]) * 10)
    
    # Award Coins
    coins_reward = 15
    if score >= 50:
        coins_reward += 10
    if score == 100:
        coins_reward += 25
        
    duration_minutes = max(1, time_taken // 60)
    log_study_activity(user_id, duration_minutes, xp_reward, coins_reward)
    
    # Evaluate Perfect Score Badges
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT badges FROM users WHERE id = ?", (user_id,))
    u_badges_row = cursor.fetchone()
    if u_badges_row:
        badges_str = u_badges_row["badges"] or ""
        badge_list = [b.strip() for b in badges_str.split(",") if b.strip()]
        
        if score == 100 and "Perfect Assessment" not in badge_list:
            badge_list.append("Perfect Assessment")
        if cat_scores["speaking"] >= 90 and "Speaking Star" not in badge_list:
            badge_list.append("Speaking Star")
        if cat_scores["listening"] >= 90 and "Listening Hero" not in badge_list:
            badge_list.append("Listening Hero")
        if cat_scores["reading"] >= 90 and "Reading Champion" not in badge_list:
            badge_list.append("Reading Champion")
        if cat_scores["writing"] >= 90 and "Writing Expert" not in badge_list:
            badge_list.append("Writing Expert")
        if cat_scores["vocabulary"] >= 90 and "Vocabulary Master" not in badge_list:
            badge_list.append("Vocabulary Master")
        if cat_scores["grammar"] >= 90 and "Grammar Expert" not in badge_list:
            badge_list.append("Grammar Expert")
            
        cursor.execute("UPDATE users SET badges = ? WHERE id = ?", (",".join(badge_list), user_id))
        conn.commit()
    conn.close()

    # Update session variables
    session["initial_assessment_completed"] = 1
    session["learning_level"] = learner_level
    session["last_score"] = score
    session.pop("assessment_questions", None)
    session.pop("assessment_start_time", None)

    return render_template(
        "assessment_result.html",
        score=score,
        correct=correct,
        incorrect=incorrect,
        total=total,
        attempted=attempted,
        time_taken=time_taken,
        pass_status=pass_status,
        review_items=review_items,
        translations=translations,
        cat_scores=cat_scores,
        learner_level=learner_level,
        strong_skills=strong_skills_str,
        weak_skills=weak_skills_str
    )"""

# Replace submit_assessment route in app.py
pattern = r"@app\.route\(\"/submit_assessment\", methods=\[\"POST\"\]\).*?translations=translations\s*\)"
modified, count = re.subn(pattern, new_submit_route, content, flags=re.DOTALL)

if count > 0:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(modified)
    print("Submit assessment route updated! Modified", count, "occurrence(s).")
else:
    print("Submit assessment replacement failed!")
