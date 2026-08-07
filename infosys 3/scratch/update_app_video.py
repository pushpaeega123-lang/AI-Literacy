import os
import sys
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

helpers_code = '''
def get_video_folder_for_age(age):
    try:
        age_int = int(age)
    except (ValueError, TypeError):
        age_int = 1

    if age_int == 1 or age_int == 2:
        return "age1"
    elif age_int == 3 or age_int == 4:
        return "age3"
    elif age_int == 5:
        return "age5"
    else:
        return f"age{age_int}"


def get_local_videos_for_learner(language, age):
    lang_folder = (language or "English").lower().strip()
    folder_name = get_video_folder_for_age(age)
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dir_path = os.path.join(base_dir, "static", "videos", lang_folder, folder_name)

    if not os.path.exists(dir_path):
        print(f"[VIDEO ERROR] Missing folder for language='{language}', age={age}: {dir_path}")
        return []

    try:
        files = [f for f in sorted(os.listdir(dir_path)) if f.lower().endswith(".mp4")]
    except Exception as e:
        print(f"[VIDEO ERROR] Error scanning directory {dir_path}: {e}")
        return []

    if not files:
        print(f"[VIDEO ERROR] Missing MP4 files in directory {dir_path} for language='{language}', age={age}")
        return []

    videos = []
    for f in files:
        web_path = f"/static/videos/{lang_folder}/{folder_name}/{f}"
        videos.append({
            "title": os.path.splitext(f)[0],
            "video_url": web_path,
            "filename": f,
            "category": "Local Video",
            "language": language,
            "age": age
        })
    return videos
'''

lesson_detail_code = '''@app.route("/lesson/<int:lesson_id>")
@login_required
def lesson_detail(lesson_id):
    user_id = session.get("user_id")
    language = session.get("language", "English")
    learning_level = session.get("learning_level", "Beginner")
    age = session.get("age", 8)
    translations = get_translations(language)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
    lesson_row = cursor.fetchone()
    conn.close()
    
    if not lesson_row:
        flash("Lesson not found.", "warning")
        return redirect(url_for("week_module"))
        
    lesson = dict(lesson_row)
    
    # Parse quiz from lesson content if present
    quiz = None
    content_text = lesson.get("content", "")
    if "[QUIZ]" in content_text:
        parts = content_text.split("[QUIZ]")
        lesson["content"] = parts[0].strip()
        quiz_str = parts[1].strip()
        quiz_parts = [p.strip() for p in quiz_str.split("|")]
        if len(quiz_parts) >= 2:
            quiz = {
                "question": quiz_parts[0],
                "options": quiz_parts[1:-1],
                "answer": quiz_parts[-1]
            }
    elif lesson.get("category") == "comprehension" or "comprehension" in lesson.get("title", "").lower():
        if language == "Telugu":
            quiz = {
                "question": "పైన ఉన్న పాఠం ఆధారంగా: ప్రధాన నేర్చుకోదగ్గ విషయం ఏమిటి?",
                "options": ["అభ్యాసం చేయడం మరియు కొత్త విషయాలు గ్రహించడం", "ఏమీ చేయకపోవడం", "ఆటలు మాత్రమే ఆడటం"],
                "answer": "అభ్యాసం చేయడం మరియు కొత్త విషయాలు గ్రహించడం"
            }
        elif language == "Hindi":
            quiz = {
                "question": "ऊपर दिए गए पाठ के अनुसार: मुख्य सीख क्या है?",
                "options": ["अभ्यास करना और नई बातें सीखना", "कुछ न करना", "केवल खेल खेलना"],
                "answer": "अभ्यास करना और नई बातें सीखना"
            }
        elif language == "Tamil":
            quiz = {
                "question": "மேலே உள்ள பாடத்தின் அடிப்படையில்: முதன்மை கற்றல் செய்தி என்ன?",
                "options": ["பயிற்சி செய்து புதிய விஷயங்களைக் கற்றுக்கொள்வது", "எதுவும் செய்யாமல் இருப்பது", "விளையாடுவது மட்டுமே"],
                "answer": "பயிற்சி செய்து புதிய விஷயங்களைக் கற்றுக்கொள்வது"
            }
        elif language == "Kannada":
            quiz = {
                "question": "ಮೇಲಿನ ಪಾಠದ ಆಧಾರದ ಮೇಲೆ: ಪ್ರಮುಖ ಕಲಿಕಾ ವಿಷಯ ಯಾವುದು?",
                "options": ["ಅಭ್ಯಾಸ ಮಾಡುವುದು ಮತ್ತು ಹೊಸ ವಿಷಯಗಳನ್ನು ಕಲಿಯುವುದು", "ಏನೂ ಮಾಡದಿರುವುದು", "ಆಟ ಮಾತ್ರ ಆಡುವುದು"],
                "answer": "ಅಭ್ಯಾಸ ಮಾಡುವುದು మరియు కొత్త విషయాలను ಕಲಿಯುವುದು"
            }
        elif language == "Marathi":
            quiz = {
                "question": "वरील पाठाच्या आधारे: मुख्य शिकवण कोणती आहे?",
                "options": ["सराव करणे आणि नवीन गोष्टी शिकणे", "काहीही न करणे", "फक्त खेळणे"],
                "answer": "सराव करणे आणि नवीन गोष्टी शिकणे"
            }
        else:
            quiz = {
                "question": "Based on the lesson content above: What is the key takeaway?",
                "options": ["Practicing consistently and learning new ideas", "Doing nothing", "Only playing games all day"],
                "answer": "Practicing consistently and learning new ideas"
            }

    # Resolve local video for learner age and language
    video = None
    try:
        age_val = int(age)
    except (ValueError, TypeError):
        age_val = 1

    local_vids = get_local_videos_for_learner(language, age_val)
    if local_vids:
        vid_idx = (lesson_id - 1) % len(local_vids)
        video = local_vids[vid_idx]
    else:
        print(f"[VIDEO ERROR] Video file missing for lesson_id={lesson_id}, age={age_val}, language='{language}'")
        video = None

    return render_template(
        "lesson.html",
        lesson=lesson,
        video=video,
        quiz=quiz,
        translations=translations,
        age=age,
        learning_level=learning_level
    )'''

api_toddler_videos_code = '''@app.route("/api/toddler/videos")
@login_required
def api_toddler_videos():
    language = session.get("language", "English")
    age = session.get("age", 1)
    
    videos = get_local_videos_for_learner(language, age)
    if not videos:
        print(f"[VIDEO ERROR] /api/toddler/videos found no MP4 videos for lang='{language}', age={age}")
    return jsonify(videos)'''

# Insert helper functions if not present
if 'def get_video_folder_for_age' not in content:
    target = 'app = Flask(__name__)'
    target_idx = content.find(target)
    if target_idx != -1:
        insert_pos = content.find('\n', target_idx) + 1
        content = content[:insert_pos] + helpers_code + '\n' + content[insert_pos:]

# Replace lesson_detail
lesson_detail_pattern = re.compile(r'@app\.route\("/lesson/<int:lesson_id>"\)\s*@login_required\s*def lesson_detail\(lesson_id\):.*?(?=\n@app\.route)', re.DOTALL)
content, count1 = lesson_detail_pattern.subn(lesson_detail_code + '\n', content, count=1)
print(f"Replaced lesson_detail: {count1}")

# Remove duplicate lesson route (lines 2591-2628)
dup_pattern = re.compile(r'# -\s*# Lessons Module Detail & Completion\s*# -\s*@app\.route\("/lesson/<int:lesson_id>"\)\s*@login_required\s*def lesson\(lesson_id\):.*?(?=\n@app\.route\("/complete_lesson)', re.DOTALL)
content, count2 = dup_pattern.subn('\n', content)
print(f"Removed duplicate lesson route: {count2}")

# Replace api_toddler_videos
api_toddler_pattern = re.compile(r'@app\.route\("/api/toddler/videos"\)\s*@login_required\s*def api_toddler_videos\(\):.*?(?=\n@app\.route\("/api/tts"\))', re.DOTALL)
content, count3 = api_toddler_pattern.subn(api_toddler_videos_code + '\n\n', content)
print(f"Replaced api_toddler_videos: {count3}")

# Remove age <= 4 block in complete_lesson if present
complete_lesson_pattern = re.compile(r'(def complete_lesson\(lesson_id\):\s*)\n\s*age = session\.get\("age", 1\)\s*\n\s*if age and int\(age\) <= 4:\s*\n\s*flash\("Lessons are not available for toddlers\.", "info"\)\s*\n\s*return redirect\(url_for\("week_module"\)\)', re.DOTALL)
content, count4 = complete_lesson_pattern.subn(r'\1', content)
print(f"Updated complete_lesson: {count4}")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated app.py successfully!")
