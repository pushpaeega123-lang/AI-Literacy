import os
import json
import random
import requests

def get_gemini_api_key():
    """
    Retrieves the Gemini API key from environment variables or local .env files.
    """
    # 1. Check environment variables
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key

    # 2. Check local .env file
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        env_paths = [
            os.path.join(current_dir, ".env"),
            os.path.join(current_dir, "..", ".env"),
            os.path.join(os.getcwd(), ".env")
        ]
        for env_path in env_paths:
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.strip().startswith("GEMINI_API_KEY="):
                            parsed_key = line.split("=", 1)[1].strip()
                            return parsed_key.strip('"').strip("'")
    except Exception:
        pass

    return None

def get_fallback_questions(language, age, learning_level):
    """
    Queries the legacy assessment question database or pool to return exactly 10 questions.
    Acts as a failsafe when the LLM service is unavailable or key is missing.
    """
    print(f"[Gemini Service] Falling back to offline question generator for {language}, age {age}, level {learning_level}")
    try:
        from app import _legacy_get_assessment_questions
        # Request questions from local pool
        legacy_qs = _legacy_get_assessment_questions(language, age, learning_level)
        
        # Ensure we return exactly 10 questions
        if not legacy_qs:
            raise ValueError("No legacy questions found")
            
        result = []
        # Copy and rename questions to ensure name uniqueness
        for i in range(10):
            source_q = legacy_qs[i % len(legacy_qs)]
            q_copy = source_q.copy()
            q_copy["name"] = f"q{i+1}"
            if "skill" not in q_copy:
                q_copy["skill"] = q_copy.get("type", "comprehension")
            result.append(q_copy)
            
        return result
    except Exception as e:
        print(f"[Gemini Service] Fallback question generation failed: {e}")
        print(f"[WARNING] Missing translation or fallback questions for language: {language}")
        # Return hardcoded static list of 10 generic questions
        fallback_list = []
        categories = ["vocabulary", "grammar", "comprehension", "reading", "writing", "listening", "speaking"]
        for i in range(10):
            cat = categories[i % len(categories)]
            if cat == "speaking":
                fallback_list.append({
                    "name": f"q{i+1}",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": f"Click the microphone and say: Hello! 👋 [Fallback: Translated content not available in {language}]",
                    "options": [],
                    "answer": "Hello",
                    "explanation": f"Practice saying Hello. (Fallback question for {language})",
                    "hint": "Hello"
                })
            elif cat == "writing":
                fallback_list.append({
                    "name": f"q{i+1}",
                    "type": "writing",
                    "skill": "writing",
                    "prompt": f"Complete the word: 'p_ncil' [Fallback: Translated content not available in {language}]",
                    "options": [],
                    "answer": "pencil",
                    "explanation": f"The missing letters form 'pencil'. (Fallback question for {language})",
                    "hint": "pencil"
                })
            else:
                fallback_list.append({
                    "name": f"q{i+1}",
                    "type": cat,
                    "skill": cat,
                    "prompt": f"Practice question for category {cat}. Select the correct option. [Fallback: Translated content not available in {language}]",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "answer": "Option A",
                    "explanation": f"This is a fallback practice question for category {cat} in {language}.",
                    "hint": "Option A"
                })
        return fallback_list

def generate_adaptive_assessment(language, age, learning_level, prev_score=None, prev_weak=None):
    """
    Calls Google Gemini API to generate 10 unique, age-appropriate, and qualification-appropriate
    language assessment questions in the target language. Falls back to local generation if LLM fails.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        print("[Gemini Service] No GEMINI_API_KEY configured. Loading fallback questions.")
        return get_fallback_questions(language, age, learning_level)

    # 1. Randomize theme/topics to ensure every set of generated questions is unique
    themes = [
        "nature, birds, flowers, environment",
        "family, school life, friendship, helpers",
        "animals, wildlife, pets, safari",
        "food, fruits, vegetables, cooking",
        "travel, transport, vehicles, destinations",
        "hobbies, reading, music, art",
        "sports, games, fitness, outdoors",
        "time, seasons, calendar, daily routine",
        "computers, science, wonders of space, technology",
        "shopping, market, festivals, culture"
    ]
    selected_theme = random.choice(themes)

    # 2. Build structured prompt
    user_prompt = f"""
You are an expert curriculum designer and language evaluator specializing in literacy development.
Create a personalized language assessment for a user with the following profile:
- Target Language: {language}
- Age: {age}
- Qualification / Proficiency Level: {learning_level}
- Previous Assessment Score: {f"{prev_score}%" if prev_score is not None else "Not Available (First assessment)"}
- Previous Weak Skills / Topics: {prev_weak if prev_weak else "None"}
- Selection Theme: Incorporate ideas and words related to "{selected_theme}" to keep questions diverse.

Instructions & Rules:
1. Generate exactly 10 questions customized for this learner's level ({learning_level}) and age ({age}).
2. The assessment must be completely in {language}. All user-facing content (prompt, options, answer, explanation, hint) must be written in {language}.
3. Generate a different set of questions for every learner by making them unique and focusing on different vocabulary and contexts.
4. Distribute question types across: "reading", "writing", "comprehension", "listening", "speaking", "vocabulary", "grammar". 
   Ensure there is a balanced mix. Include speaking (repeating/pronouncing), listening, and comprehension tasks.
5. The output MUST be a valid JSON array of exactly 10 question objects. Do not include markdown code blocks like ```json ... ```, return the raw JSON text.
6. The question object structure must be EXACTLY:
   - "name": Uniquely named "q1", "q2", ..., up to "q10".
   - "type": One of: "reading", "writing", "comprehension", "listening", "speaking", "vocabulary", "grammar".
   - "skill": Map to the category name, such as: "reading", "writing", "comprehension", "listening", "speaking", "vocabulary", "grammar".
   - "prompt": The actual question text or instructions (written in {language}). For speaking tasks, ask the user to read or repeat a sentence. For listening tasks, specify the spoken text or prompt.
   - "options": An array of 4 string options (written in {language}) if type is reading, comprehension, listening, grammar, or vocabulary. For speaking and writing tasks, options must be an empty array [].
   - "answer": The correct answer. For multiple choice, it must exactly match one of the options. For speaking, it must match the expected text/sentence. For writing, it must be the correct target text.
   - "explanation": An explanation (written in {language}) of why the answer is correct.
   - "hint": For speaking questions, this MUST be the exact target word or sentence in {language} that the learner is prompted to say (as the speech recognition matches this). For other tasks, a helpful hint in {language}.

Return ONLY the raw JSON array.
"""

    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": user_prompt}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.8
        }
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=20)
        if response.status_code != 200:
            print(f"[Gemini Service] API Error (Status {response.status_code}): {response.text}")
            return get_fallback_questions(language, age, learning_level)

        res_json = response.json()
        raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Parse output JSON
        questions = json.loads(raw_text)
        
        # Verify it is a valid list of exactly 10 questions
        if isinstance(questions, list) and len(questions) == 10:
            # Post-process and normalize keys/values
            for i, q in enumerate(questions):
                q["name"] = f"q{i+1}"
                # Normalize types and skills
                q["type"] = q.get("type", "comprehension").lower()
                if "skill" not in q or not q["skill"]:
                    q["skill"] = q.get("type", "comprehension")
                q["skill"] = q["skill"].lower()
                
                # Verify options array
                if q["type"] in ["speaking", "writing"]:
                    q["options"] = []
                elif "options" not in q or not isinstance(q["options"], list):
                    q["options"] = []
                    
                # Fix up any missing keys
                if "answer" not in q:
                    q["answer"] = q["options"][0] if q["options"] else "Answer"
                if "explanation" not in q:
                    q["explanation"] = "Practice is key to language mastery."
                if "hint" not in q:
                    q["hint"] = q["answer"]
                    
            print(f"[Gemini Service] Successfully generated 10 adaptive questions for theme '{selected_theme}'")
            return questions
        else:
            print(f"[Gemini Service] Invalid data structure or length: {type(questions)}")
            return get_fallback_questions(language, age, learning_level)
            
    except Exception as e:
        print(f"[Gemini Service] Exception calling Gemini API: {e}")
        return get_fallback_questions(language, age, learning_level)

def gemini_generate_lesson_content(topic, language, difficulty_filter):
    """
    Calls Google Gemini API to generate lesson content.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        raise ValueError("GEMINI_API_KEY not configured")
        
    import sqlite3
    
    # Set default values for prompt inputs
    age = 20
    qualification = "High School"
    preferred_language = language
    learning_language = language
    learning_level = difficulty_filter
    skill_level = "Beginner"
    module_name = topic
    lesson_title = topic
    lesson_description = f"A comprehensive lesson focusing on {topic}."
    
    # Try to look up the logged-in user profile details to populate inputs
    try:
        from flask import session
        user_id = session.get("user_id")
        if user_id:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(current_dir, "literacy.db")
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT age, education_level, preferred_language, learning_language, learning_level, current_proficiency 
                FROM users WHERE id = ?
            """, (user_id,))
            row = cursor.fetchone()
            conn.close()
            if row:
                if row["age"]:
                    age = row["age"]
                if row["education_level"]:
                    qualification = row["education_level"]
                if row["preferred_language"]:
                    preferred_language = row["preferred_language"]
                if row["learning_language"]:
                    learning_language = row["learning_language"]
                if row["learning_level"]:
                    learning_level = row["learning_level"]
                if row["current_proficiency"]:
                    skill_level = row["current_proficiency"]
    except Exception as e:
        print(f"[Gemini Service] User DB lookup failed: {e}")

    system_prompt = (
        "You are an Expert AI Educational Curriculum Designer and Adaptive Learning Assistant for the project "
        "\"AI-Powered Learning Support Assistant for Foundational Literacy Development.\"\n"
        "Your responsibility is to generate HIGH-QUALITY, PERSONALIZED, AGE-APPROPRIATE, MULTILINGUAL, and CURRICULUM-ALIGNED learning content for learners aged 6 to 60 years.\n\n"
        "The response must be returned as a JSON object with exactly three fields:\n"
        "1. 'title': The Lesson Title (string).\n"
        "2. 'category': One of 'reading', 'writing', or 'comprehension' (string).\n"
        "3. 'content': The complete generated lesson text formatted in Markdown, following the 20-section structure below (string).\n\n"
        f"Ensure all lesson contents inside the 'content' field are generated in the target Learning Language ({learning_language})."
    )
    
    user_prompt = f"""
# MASTER PROMPT – AI-Powered Learning Support Assistant for Foundational Literacy Development

---

## PROJECT OBJECTIVE

Develop personalized literacy lessons that improve:
* Reading
* Writing
* Speaking
* Listening
* Vocabulary
* Pronunciation
* Communication
* Comprehension

The generated lesson must support adaptive learning based on the learner's ability.

---

## INPUT PARAMETERS

Age:
{age}

Qualification:
{qualification}

Preferred Language:
{preferred_language}

Learning Language:
{learning_language}

Assessment Level:
{learning_level}

Current Skill Level:
{skill_level}

Curriculum Module:
{module_name}

Lesson Title:
{lesson_title}

Lesson Description:
{lesson_description}

---

# MOST IMPORTANT RULE

The **Lesson Title is the ONLY source of truth.**

Everything generated must belong ONLY to the given Lesson Title.

Never generate content from another lesson.
Never mix topics.

---

# CURRICULUM ALIGNMENT

Before generating content, identify the lesson title.
Understand its learning objective.
Generate ONLY concepts that belong to that lesson.
Every heading must match the lesson.
Every explanation must match the lesson.
Every example must match the lesson.
Every activity must match the lesson.
Every exercise must match the lesson.
Every quiz must match the lesson.
Every assessment must match the lesson.
If anything is unrelated, remove it.

---

# AGE ADAPTATION

Age 6–10
* Very simple vocabulary
* Short sentences
* Interactive learning
* Image-friendly explanations
* Simple examples
* Easy activities
* Fun quizzes

Age 11–15
* Moderate explanations
* Practical examples
* Reading passages
* Writing exercises
* Skill-building activities

Age 16–25
* Concept-based learning
* Communication skills
* Academic examples
* Workplace preparation
* Problem-solving activities

Age 26–60
* Practical literacy
* Daily-life communication
* Workplace literacy
* Functional reading
* Functional writing
* Real-world applications

---

# LESSON STRUCTURE

Generate the lesson content inside the JSON 'content' field in the following order:

1. Lesson Title

2. Learning Objectives

3. Introduction

4. Main Lesson Explanation

5. Key Concepts

6. Examples

7. Vocabulary

8. Reading Practice

9. Writing Practice

10. Speaking Practice

11. Listening Activity

12. Pronunciation Practice

13. Interactive Activity

14. Real-life Application

15. Practice Questions

16. Quiz (5 Questions)

17. Voice Assessment Task

18. Summary

19. Key Takeaways

20. Learning Outcome

---

# MULTILINGUAL SUPPORT

Generate the lesson in the selected Learning Language ({learning_language}).
If Preferred Language ({preferred_language}) differs from Learning Language ({learning_language}), use Preferred Language only for brief guidance where necessary.
Do not mix multiple languages throughout the lesson unless specifically requested.

---

# PERSONALIZATION

Adapt the lesson using:
* learner age ({age})
* qualification ({qualification})
* learning level ({learning_level})
* skill level ({skill_level})

---

# AI VALIDATION

Before returning the lesson, perform these validation checks.
✓ Lesson Title matches lesson content.
✓ Every heading belongs to the lesson.
✓ Every paragraph belongs to the lesson.
✓ Every example belongs to the lesson.
✓ Every activity belongs to the lesson.
✓ Every assessment belongs to the lesson.
✓ Every quiz belongs to the lesson.
✓ Every pronunciation task belongs to the lesson.
✓ Every vocabulary item belongs to the lesson.
✓ Content matches learner age.
✓ Content matches qualification.
✓ Content matches learning level.
✓ Content matches selected language ({learning_language}).
✓ No unrelated topic exists.

If any validation fails, regenerate internally until every validation passes.

---

# FINAL RESPONSE

Return ONLY a JSON object with 'title', 'category', and 'content' fields.
The 'content' field must contain the final validated lesson in {learning_language}.
Never generate content from any other lesson.
Never ignore the Lesson Title.
The Lesson Title must control the entire lesson generation process.
The final lesson must have a 100% semantic match with the selected Lesson Title and curriculum.
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    res = requests.post(url, headers=headers, json=payload, timeout=15)
    if res.status_code != 200:
        raise ValueError(f"Gemini API error: {res.text}")
        
    res_json = res.json()
    raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
    return json.loads(raw_text)

def gemini_generate_recommendations(user_profile, available_lessons):
    """
    Calls Gemini API to generate personalized recommendations based on the user's scores.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    # Construct prompt with user stats
    system_prompt = """
You are an expert AI tutor and language learning recommender system.
Analyze the user's profile and initial assessment scores, and generate a personalized recommendations JSON payload.
All user-facing text fields (like summary, recommendation, description) MUST be written in the user's selected language.

Return a JSON object with the following structure:
{
    "summary": "A 2-3 sentence friendly, encouraging analysis of the user's current strengths and improvement areas, written in the selected language.",
    "weak_skills": ["list of weak skills from: reading, writing, listening, speaking, comprehension"],
    "strong_skills": ["list of strong skills from: reading, writing, listening, speaking, comprehension"],
    "skills": [
        {
            "name": "Reading (or localized name)",
            "level": "Excellent / Good / Needs Improvement",
            "score": 70,
            "recommendation": "Localized recommendation message advising on what to practice next.",
            "url": "/week-module"
        },
        {
            "name": "Writing (or localized name)",
            "level": "Excellent / Good / Needs Improvement",
            "score": 70,
            "recommendation": "Localized recommendation message advising on what to practice next.",
            "url": "/week-module"
        },
        {
            "name": "Listening (or localized name)",
            "level": "Excellent / Good / Needs Improvement",
            "score": 70,
            "recommendation": "Localized recommendation message advising on what to practice next.",
            "url": "/week-module"
        },
        {
            "name": "Speaking (or localized name)",
            "level": "Excellent / Good / Needs Improvement",
            "score": 70,
            "recommendation": "Localized recommendation message advising on what to practice next.",
            "url": "/week-module"
        },
        {
            "name": "Comprehension (or localized name)",
            "level": "Excellent / Good / Needs Improvement",
            "score": 70,
            "recommendation": "Localized recommendation message advising on what to practice next.",
            "url": "/week-module"
        }
    ],
    "lessons": [
        {
            "title": "Localized Lesson Title",
            "category": "reading / writing / comprehension / speaking / listening",
            "description": "Localized description of what they will learn",
            "url": "/lesson/1"
        }
    ],
    "activities": [
        {
            "title": "Localized Activity Title",
            "category": "Practice",
            "description": "Localized description of practice activity",
            "url": "/learning-games"
        }
    ],
    "voice_practice": [
        {
            "title": "Localized Voice Practice Title",
            "category": "Speaking",
            "description": "Localized speaking drill description",
            "url": "/week-module"
        }
    ],
    "games": [
        {
            "title": "Localized Game Title",
            "category": "Grammar / Spelling / Vocabulary",
            "description": "Localized game recommendation description",
            "url": "/learning-games"
        }
    ],
    "quizzes": [
        {
            "title": "Localized Quiz Title",
            "category": "Assessment",
            "description": "Localized quiz description",
            "url": "/assessment"
        }
    ]
}
"""

    user_prompt = f"""
User Profile:
- Age: {user_profile.get('age', 8)}
- Selected Language: {user_profile.get('language', 'English')}
- Learning Level: {user_profile.get('learning_level', 'Beginner')}
- Reading Score: {user_profile.get('reading_score', 70)}%
- Writing Score: {user_profile.get('writing_score', 70)}%
- Listening Score: {user_profile.get('listening_score', 70)}%
- Speaking Score: {user_profile.get('speaking_score', 70)}%
- Comprehension Score: {user_profile.get('comprehension_score', 70)}%

Available Lessons Metadata:
{[{"id": l["id"], "title": l["title"], "category": l["category"]} for l in available_lessons[:6]]}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            res_json = res.json()
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            parsed = json.loads(raw_text)
            
            # Match lesson URLs dynamically if generated lesson list has entries
            if parsed.get("lessons") and available_lessons:
                for idx, l in enumerate(parsed["lessons"]):
                    db_lesson = available_lessons[idx % len(available_lessons)]
                    l["url"] = f"/lesson/{db_lesson['id']}"
                    
            return parsed
    except Exception as e:
        print(f"[Gemini Recommendations Exception] {e}")
    return None

def gemini_generate_learning_path(user_profile, available_lessons):
    """
    Calls Gemini API to generate a personalized 5-step learning path.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        return None

    system_prompt = """
You are an expert AI tutor specializing in language literacy instruction.
Create a personalized 5-step learning path for the user based on their assessment profile.
The steps must sequence logic from weaker skills first to reinforcement, practice, assessment, and AI guidance.
All user-facing text fields (like title, category, recommended_activity, learning_objective) MUST be in the user's selected language.

Return a JSON array of exactly 5 step objects with this structure:
[
  {
    "step": 1,
    "title": "Localized Title",
    "type": "Lesson",
    "category": "Localized Category Name",
    "lesson_id": null,
    "status": "pending",
    "completion_status": "pending",
    "is_locked": false,
    "icon": "bi-journal-bookmark-fill",
    "url": "/week-module",
    "target_skill": "reading / writing / listening / speaking / comprehension",
    "recommended_activity": "Localized activity instructions",
    "learning_objective": "Localized learning objective",
    "estimated_duration": 10,
    "skill_focus": "reading / writing / listening / speaking / comprehension"
  },
  ...
]
"""

    user_prompt = f"""
User Profile:
- Age: {user_profile.get('age', 8)}
- Selected Language: {user_profile.get('language', 'English')}
- Learning Level: {user_profile.get('learning_level', 'Beginner')}
- Reading Score: {user_profile.get('reading_score', 70)}%
- Writing Score: {user_profile.get('writing_score', 70)}%
- Listening Score: {user_profile.get('listening_score', 70)}%
- Speaking Score: {user_profile.get('speaking_score', 70)}%
- Comprehension Score: {user_profile.get('comprehension_score', 70)}%

Available Lessons:
{[{"id": l["id"], "title": l["title"], "category": l["category"]} for l in available_lessons[:6]]}
"""

    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": f"{system_prompt}\n\n{user_prompt}"}
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "temperature": 0.7
        }
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=15)
        if res.status_code == 200:
            res_json = res.json()
            raw_text = res_json["candidates"][0]["content"]["parts"][0]["text"].strip()
            parsed = json.loads(raw_text)
            
            # Map dynamic step details
            if isinstance(parsed, list) and len(parsed) == 5:
                for idx, step in enumerate(parsed):
                    if step.get("type") == "Lesson" and available_lessons:
                        db_lesson = available_lessons[idx % len(available_lessons)]
                        step["lesson_id"] = db_lesson["id"]
                        step["url"] = f"/lesson/{db_lesson['id']}"
                return parsed
    except Exception as e:
        print(f"[Gemini Learning Path Exception] {e}")
    return None

def generate_post_lesson_ai_feedback(lesson_title, score, language="English", user_age=8):
    """
    Generates personalized post-lesson AI feedback explaining strengths, weaknesses,
    and recommended next steps.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        if score >= 80:
            return {
                "headline": "Outstanding Mastery! 🌟",
                "strengths": f"You demonstrated strong comprehension in '{lesson_title}'.",
                "weaknesses": "Keep practicing to refine your speed and accent accuracy.",
                "recommendation": "Ready to unlock the next level module!"
            }
        elif score >= 50:
            return {
                "headline": "Good Progress! 👍",
                "strengths": f"You successfully completed core activities for '{lesson_title}'.",
                "weaknesses": "Review key vocabulary and practice speaking aloud.",
                "recommendation": "Replay the voice exercises before moving to the next lesson."
            }
        else:
            return {
                "headline": "Keep Going! 💪",
                "strengths": "Great effort attempting all lesson practice questions.",
                "weaknesses": "Need more practice with foundational phonics and sentence patterns.",
                "recommendation": "We recommend re-reading this lesson to achieve 80%+ mastery."
            }

    system_prompt = f"""
    You are Lumi, a warm, encouraging educational AI mentor.
    Provide constructive, age-appropriate post-lesson feedback in language: {language}.
    Return raw JSON with exactly 4 fields:
    1. 'headline': A short encouraging 3-5 word title with emoji.
    2. 'strengths': 1-2 sentences on what the learner did well.
    3. 'weaknesses': 1-2 sentences on area to improve based on score ({score}%).
    4. 'recommendation': Specific next learning step.
    """
    headers = {"Content-Type": "application/json"}
    payload = {
        "contents": [{"parts": [{"text": f"Lesson: {lesson_title}, Score: {score}%, Age: {user_age}"}]}],
        "generationConfig": {"responseMimeType": "application/json", "temperature": 0.7}
    }
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    try:
        res = requests.post(url, headers=headers, json=payload, timeout=10)
        if res.status_code == 200:
            raw_text = res.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
            return json.loads(raw_text)
    except Exception as e:
        print(f"[Gemini Post-Lesson Feedback Exception] {e}")

    return {
        "headline": "Great Effort! ⭐",
        "strengths": f"You completed {lesson_title}.",
        "weaknesses": "Practice key words daily for maximum retention.",
        "recommendation": "Continue on your learning path!"
    }

