import os
import sqlite3

# Define MULTILINGUAL_DICTIONARY statically to prevent linter warnings.
# It will be dynamically populated at runtime using exec().
MULTILINGUAL_DICTIONARY = {}

# Define the new native fluent categories as text
native_categories_str = """
    "Idioms & Daily Slang": [
        {
            "word_id": "hows_it_going",
            "translations": {
                "English": ("How's it going?", "hows it going"),
                "Telugu": ("ఎలా నడుస్తోంది?", "ela nadusthondi"),
                "Hindi": ("क्या हाल है?", "kya haal hai"),
                "Tamil": ("எப்படி போகிறது?", "eppadi pogirathu"),
                "Kannada": ("ಹೇಗಿದೆ?", "hegide"),
                "Marathi": ("काय चाललंय?", "kay chalalay")
            },
            "image": "slang_hows.png"
        },
        {
            "word_id": "call_it_day",
            "translations": {
                "English": ("Let's call it a day.", "lets call it a day"),
                "Telugu": ("ఈ రోజుకు ఇక చాలు.", "ee rojuky ika chaalu"),
                "Hindi": ("आज के लिए बस इतना ही।", "aaj ke liye bas itna hi"),
                "Tamil": ("இன்றைக்கு இத்துடன் முடிப்போம்.", "indraikku ithudan mudippoam"),
                "Kannada": ("ಇಂದಿಗೆ ಇಷ್ಟೇ ಸಾಕು.", "indige ishte saaku"),
                "Marathi": ("आजच्यासाठी पुरे.", "aajchyasathi pure")
            },
            "image": "slang_call.png"
        },
        {
            "word_id": "piece_of_cake",
            "translations": {
                "English": ("It's a piece of cake.", "its a piece of cake"),
                "Telugu": ("ఇది చాలా సులभం.", "idi chaala sulabham"),
                "Hindi": ("यह बहुत आसान है।", "yeh bahut aasaan hai"),
                "Tamil": ("இது மிகவும் சுலபம்.", "ithu migavum sulabam"),
                "Kannada": ("ಇದು ತುಂಬಾ ಸುಲಭ.", "idu tumba sulabha"),
                "Marathi": ("हे खूप सोपे आहे.", "he khup sope aahe")
            },
            "image": "slang_cake.png"
        }
    ],
    "Socializing & Hobbies": [
        {
            "word_id": "what_like_do",
            "translations": {
                "English": ("What do you like to do?", "what do you like to do"),
                "Telugu": ("మీకు ఏమి చేయడం ఇష్టం?", "meeru emi cheyadam ishtam"),
                "Hindi": ("आपको क्या करना पसंद है?", "aapko kya karna pasand hai"),
                "Tamil": ("உங்களுக்கு என்ன செய்ய பிடிக்கும்?", "ungalukku enna seyya pidikum"),
                "Kannada": ("ನಿಮಗೆ ಏನು ಮಾಡಲು ಇಷ್ಟ?", "nimage enu madalu ishta"),
                "Marathi": ("तुम्हाला काय करायला आवडते?", "tumhala kay karायला aavadte")
            },
            "image": "social_like.png"
        },
        {
            "word_id": "enjoy_music",
            "translations": {
                "English": ("I enjoy listening to music.", "i enjoy listening to music"),
                "Telugu": ("నాకు సంగీతం వినడం ఇష్టం.", "naaku sangeetham vinadam ishtam"),
                "Hindi": ("मुझे संगीत सुनना पसंद है।", "mujhe sangeet sunna pasand hai"),
                "Tamil": ("எனக்கு இசை கேட்க பிடிக்கும்.", "enakku isai ketka pidikum"),
                "Kannada": ("ನನಗೆ ಸಂಗೀತ ಕೇಳಲು ಇಷ್ಟ.", "nanage sangeeta kelalu ishta"),
                "Marathi": ("मला गाणी ऐकायला आवडते.", "mala gani aikalya aavadte")
            },
            "image": "social_music.png"
        },
        {
            "word_id": "meet_tomorrow",
            "translations": {
                "English": ("Let's meet tomorrow.", "lets meet tomorrow"),
                "Telugu": ("రేపు కలుద్దాం.", "repu kaluddam"),
                "Hindi": ("कल मिलते हैं।", "kal milte hain"),
                "Tamil": ("நாளை சந்திப்போம்.", "naalai santhippoam"),
                "Kannada": ("ನಾಳೆ ಭೇಟಿಯಾಗೋಣ.", "naale bhetiyagona"),
                "Marathi": ("उद्या भेटूया.", "udya bhetuya")
            },
            "image": "social_meet.png"
        }
    ],
    "Advanced Workplace & Debate": [
        {
            "word_id": "agree_point",
            "translations": {
                "English": ("I agree with your point.", "i agree with your point"),
                "Telugu": ("నేను మీ పాయింట్ తో ఏకీభవిస్తున్నాను.", "nenu mee point tho eekibhavisthunnanu"),
                "Hindi": ("मैं आपकी बात से सहमत हूँ।", "main aapki baat se sahmat hoon"),
                "Tamil": ("நான் உங்கள் கருத்தை ஒப்புக்கொள்கிறேன்.", "naan ungal karuthai oppukolkiren"),
                "Kannada": ("ನಾನು ನಿಮ್ಮ ಮಾತನ್ನು ಒಪ್ಪುತ್ತೇನೆ.", "naanu nimma matannu opputtene"),
                "Marathi": ("मी तुमच्या मुद्द्याशी सहमत आहे.", "mi tumchya muddyashi sahmat aahe")
            },
            "image": "work_agree.png"
        },
        {
            "word_id": "find_solution",
            "translations": {
                "English": ("Let's find a solution.", "lets find a solution"),
                "Telugu": ("ఒక పరిష్కారం కనుగొందాం.", "oka parishkaram kanugondam"),
                "Hindi": ("आइए एक समाधान ढूंढते हैं।", "aaiye ek samadhan dhundte hain"),
                "Tamil": ("ஒரு தீர்வை கண்டறிவோம்.", "oru theervai kandarivoam"),
                "Kannada": ("ಒಂದು ಪರಿಹಾರ ಕಂಡುಕೊಳ್ಳೋಣ.", "ondu parihara kandukollona"),
                "Marathi": ("चला एक उपाय शोधूया.", "chala ek upay shoduya")
            },
            "image": "work_solve.png"
        },
        {
            "word_id": "explain_again",
            "translations": {
                "English": ("Can you explain this again?", "can you explain this again"),
                "Telugu": ("మీరు దీన్ని మళ్ళీ వివరించగలరా?", "meeru deenni malli vivarinchagalara"),
                "Hindi": ("क्या आप इसे दोबारा समझा सकते हैं?", "kya aap ise dobara samjha sakte hain"),
                "Tamil": ("நீங்கள் இதை மீண்டும் விளக்க முடியுமா?", "neengal ithai meendum vilakka mudiyuma"),
                "Kannada": ("ನೀವು ಇದನ್ನು ಮತ್ತೊಮ್ಮೆ ವಿವರಿಸಬಹುದೇ?", "neevu idannu mattomme vivarisabude"),
                "Marathi": ("तुम्ही हे पुन्हा स्पष्ट करू शकता का?", "tumhi he punha spashta karu shakta ka")
            },
            "image": "work_explain.png"
        }
    ]
"""

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
service_path = os.path.join(base_dir, "language_learning_service.py")

# Step 1: Append new categories inside MULTILINGUAL_DICTIONARY in language_learning_service.py
if os.path.exists(service_path):
    print("Reading language_learning_service.py...")
    with open(service_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # We find the end of MULTILINGUAL_DICTIONARY = { ... }
    # Locate "Workspace Conversations"
    workspace_str = '"Workspace Conversations": ['
    workspace_idx = content.find(workspace_str)
    
    if workspace_idx != -1:
        # Find closing brace of the dictionary
        next_bracket = content.find(']', workspace_idx)
        closing_brace_idx = content.find('}', next_bracket)
        
        replacement = ",\n" + native_categories_str + "\n}"
        new_content = content[:closing_brace_idx] + replacement + content[closing_brace_idx+1:]
        
        # Update categories list in get_or_create_language_pair
        old_cat_list = '"At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations"'
        new_cat_list = '"At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations", "Idioms & Daily Slang", "Socializing & Hobbies", "Advanced Workplace & Debate"'
        new_content = new_content.replace(old_cat_list, new_cat_list)
        
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully expanded MULTILINGUAL_DICTIONARY with native fluent categories!")
    else:
        print("Error: Could not locate 'Workspace Conversations' key inside dictionary.")
else:
    print("Error: service path not found.")


# Step 2: Database Migration to insert the new native fluent lessons and vocabulary
db_path = os.path.join(base_dir, "literacy.db")
if os.path.exists(db_path):
    print("Connecting to literacy.db for native fluent migration...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Define local dictionary for execution
    exec("MULTILINGUAL_DICTIONARY = {" + native_categories_str + "}", globals())
    
    cursor.execute("SELECT id, known_lang, target_lang FROM language_pairs")
    pairs = cursor.fetchall()
    
    lessons_added = 0
    words_added = 0
    for p in pairs:
        pair_id = p["id"]
        known = p["known_lang"]
        target = p["target_lang"]
        print(f"Syncing native speaking for language pair {known} -> {target}...")
        
        categories = ["Idioms & Daily Slang", "Socializing & Hobbies", "Advanced Workplace & Debate"]
        for idx, cat in enumerate(categories, 15):
            # Check if this lesson already exists for this pair
            cursor.execute("SELECT id FROM language_lessons WHERE pair_id = ? AND category = ?", (pair_id, cat))
            lesson_row = cursor.fetchone()
            if not lesson_row:
                cursor.execute("""
                    INSERT INTO language_lessons (pair_id, title, category, sequence_order)
                    VALUES (?, ?, ?, ?)
                """, (pair_id, f"Lesson {idx}: {cat}", cat, idx))
                lesson_id = cursor.lastrowid
                lessons_added += 1
            else:
                lesson_id = lesson_row["id"]
                
            # Populate vocab matching this category
            vocab_list = MULTILINGUAL_DICTIONARY.get(cat, [])
            for vocab in vocab_list:
                known_val, _ = vocab["translations"].get(known, (vocab["translations"]["English"][0], ""))
                target_val, translit = vocab["translations"].get(target, (vocab["translations"]["English"][0], ""))
                
                # Check if this word already exists in language_vocabulary for this lesson
                cursor.execute("""
                    SELECT id FROM language_vocabulary 
                    WHERE lesson_id = ? AND word_known = ? AND word_target = ?
                """, (lesson_id, known_val, target_val))
                
                if not cursor.fetchone():
                    cursor.execute("""
                        INSERT INTO language_vocabulary (lesson_id, word_known, word_target, transliteration, image_name)
                        VALUES (?, ?, ?, ?, ?)
                    """, (lesson_id, known_val, target_val, translit, vocab["image"]))
                    words_added += 1
                    
    conn.commit()
    conn.close()
    print(f"Migration completed. Created {lessons_added} new native speaking lessons and synced {words_added} vocabulary words!")
else:
    print("Error: database path not found.")
