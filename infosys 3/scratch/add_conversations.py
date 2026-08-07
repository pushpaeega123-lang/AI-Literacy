import os
import sqlite3

MULTILINGUAL_DICTIONARY = {}

# Define the new categories dictionaries as text
new_categories_str = """
    "At the Market": [
        {
            "word_id": "how_much",
            "translations": {
                "English": ("How much is this?", "how much is this"),
                "Telugu": ("ఇది ఎంత?", "idi entha"),
                "Hindi": ("यह कितने का है?", "yeh kitne ka hai"),
                "Tamil": ("இது எவ்வளவு?", "ithu evvalavu"),
                "Kannada": ("ಇದು ಎಷ್ಟು?", "idu eshtu"),
                "Marathi": ("हे कितीला आहे?", "he kitila aahe")
            },
            "image": "market_howmuch.png"
        },
        {
            "word_id": "one_kg",
            "translations": {
                "English": ("Give me one kilogram.", "give me one kilogram"),
                "Telugu": ("నాకు ఒక కిలో ఇవ్వండి.", "naaku oka kilo ivvandi"),
                "Hindi": ("मुझे एक किलो दे दो।", "mujhe ek kilo de do"),
                "Tamil": ("எனக்கு ஒரு கிலோ கொடுங்கள்.", "enakku oru kilo kodungal"),
                "Kannada": ("ನನಗೆ ಒಂದು ಕೆಜಿ ಕೊಡಿ.", "nanage ondu kg kodi"),
                "Marathi": ("मला एक किलो द्या.", "mala ek kilo dya")
            },
            "image": "market_onekg.png"
        },
        {
            "word_id": "is_fresh",
            "translations": {
                "English": ("Is it fresh?", "is it fresh"),
                "Telugu": ("ఇది తాజాదా?", "idi taajadaa"),
                "Hindi": ("क्या यह ताज़ा है?", "kya yeh taaza hai"),
                "Tamil": ("இது புதியதா?", "ithu puthiyatha"),
                "Kannada": ("ಇದು తాజಾವಾಗಿದೆಯೇ?", "idu taajaavagideye"),
                "Marathi": ("हे ताजे आहे का?", "he taje aahe ka")
            },
            "image": "market_fresh.png"
        },
        {
            "word_id": "market_thanks",
            "translations": {
                "English": ("Thank you, here is the money.", "thank you here is the money"),
                "Telugu": ("ధన్యవాదాలు, ఇదిగో డబ్బులు.", "dhanyavadalu idigo dabbulu"),
                "Hindi": ("धन्यवाद, ये लीजिये पैसे।", "dhanyavaad ye liye paise"),
                "Tamil": ("நன்றி, இதो பணம்.", "nanri itho panam"),
                "Kannada": ("ಧನ್ಯವಾದಗಳು, ಇಗೋ ಹಣ.", "dhanyavadagalu igo hana"),
                "Marathi": ("धन्यवाद, हे घ्या पैसे.", "dhanyavaad he ghya paise")
            },
            "image": "market_money.png"
        }
    ],
    "Asking for Directions": [
        {
            "word_id": "bus_stand",
            "translations": {
                "English": ("Where is the bus stand?", "where is the bus stand"),
                "Telugu": ("బస్ స్టాండ్ ఎక్కడ ఉంది?", "bus stand ekkada undi"),
                "Hindi": ("बस स्टैंड कहाँ है?", "bus stand kaha hai"),
                "Tamil": ("பேருந்து நிலையம் எங்கே உள்ளது?", "peerunthu nilaiyam engee ullathu"),
                "Kannada": ("ಬಸ್ ನಿಲ್ದಾಣ ಎಲ್ಲಿದೆ?", "bus nildana ellide"),
                "Marathi": ("बस स्थानक कोठे आहे?", "bus sthanak kothe aahe")
            },
            "image": "dir_bus.png"
        },
        {
            "word_id": "go_straight",
            "translations": {
                "English": ("Go straight.", "go straight"),
                "Telugu": ("నేరముగా వెళ్ళండి.", "neramuga vellandi"),
                "Hindi": ("सीधे जाओ।", "seedhe jao"),
                "Tamil": ("நேராக செல்லுங்கள்.", "neraga sellungal"),
                "Kannada": ("ನೇರವಾಗಿ ಹೋಗಿ.", "neravagi hogi"),
                "Marathi": ("सरळ जा.", "saral ja")
            },
            "image": "dir_straight.png"
        },
        {
            "word_id": "turn_left",
            "translations": {
                "English": ("Turn left.", "turn left"),
                "Telugu": ("ఎడమ వైపు తిరగండి.", "edama vaipu thiragandi"),
                "Hindi": ("बाएँ मुड़ो।", "baaye mudo"),
                "Tamil": ("இடதுபுறம் திரும்पुங்கள்.", "idathupuram thirumbungal"),
                "Kannada": ("ಎಡಕ್ಕೆ ತಿರುಗಿ.", "edakke thirugi"),
                "Marathi": ("डावीकडे वळा.", "davikade vala")
            },
            "image": "dir_left.png"
        },
        {
            "word_id": "is_near",
            "translations": {
                "English": ("Is it near?", "is it near"),
                "Telugu": ("ఇది దగ్గరగా ఉందా?", "idi daggaraga unda"),
                "Hindi": ("क्या यह पास में है?", "kya yeh paas mein hai"),
                "Tamil": ("இது அருகில் உள்ளதா?", "ithu arugil ullatha"),
                "Kannada": ("ಇದು ಹತ್ತಿರವಿದೆಯೇ?", "idu hattiravideye"),
                "Marathi": ("हे जवळ आहे का?", "he javal aahe ka")
            },
            "image": "dir_near.png"
        }
    ],
    "At the Doctor": [
        {
            "word_id": "headache",
            "translations": {
                "English": ("I have a headache.", "i have a headache"),
                "Telugu": ("నాకు తలనెప్పిగా ఉంది.", "naaku thalaneppiga undi"),
                "Hindi": ("मेरे सिर में दर्द है।", "mere sir mein dard hai"),
                "Tamil": ("எனके தலைவலி உள்ளது.", "enakku thalaivali ullathu"),
                "Kannada": ("ನನಗೆ ತಲೆನೋವು ಇದೆ.", "nanage talenovu ide"),
                "Marathi": ("माझे डोके दुखत आहे.", "mazhe doke dukhat aahe")
            },
            "image": "doc_headache.png"
        },
        {
            "word_id": "take_medicine",
            "translations": {
                "English": ("Take this medicine.", "take this medicine"),
                "Telugu": ("ఈ మందు తీసుకోండి.", "ee mandu theesukondi"),
                "Hindi": ("यह दवा लीजिये।", "yeh dawa lijiye"),
                "Tamil": ("இந்த மருந்தை எடுத்துக் கொள்ளுங்கள்.", "intha marunthai eduthukollungal"),
                "Kannada": ("ಈ ಔಷಧಿಯನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.", "ee aushadhiyannu tegedukolli"),
                "Marathi": ("हे औषध घ्या.", "he aushadh ghya")
            },
            "image": "doc_med.png"
        },
        {
            "word_id": "warm_water",
            "translations": {
                "English": ("Drink warm water.", "drink warm water"),
                "Telugu": ("గోరువెచ్చని నీరు తాగండి.", "goruvechchani neeru thaagandi"),
                "Hindi": ("गुनगुना पानी पीएं।", "gunguna paani piye"),
                "Tamil": ("வெதுவெதுப்பான நீர் குடிக்கவும்.", "vethuvethuppaana neer kudikkavum"),
                "Kannada": ("ಉಗುರುಬೆಚ್ಚಗಿನ ನೀರನ್ನು ಕುಡಿಯಿರಿ.", "ugurubechagina neerannu kudiyiri"),
                "Marathi": ("कोमट पाणी प्या.", "komat pani pya")
            },
            "image": "doc_water.png"
        }
    ],
    "Workspace Conversations": [
        {
            "word_id": "when_meeting",
            "translations": {
                "English": ("When is the meeting?", "when is the meeting"),
                "Telugu": ("సమావేశం ఎప్పుడు?", "samavesham eppudu"),
                "Hindi": ("बैठक कब है?", "baithak kab hai"),
                "Tamil": ("கூட்டம் எப்போது?", "koottam eppothu"),
                "Kannada": ("ಸಭೆ ಯಾವಾಗ?", "sabhe yavaga"),
                "Marathi": ("बैठक कधी आहे?", "baithak kadhi aahe")
            },
            "image": "work_meeting.png"
        },
        {
            "word_id": "please_sign",
            "translations": {
                "English": ("Please sign this.", "please sign this"),
                "Telugu": ("దయచేసి ఇక్కడ సంతకం చేయండి.", "dayachesi ikkada santhakam cheyandi"),
                "Hindi": ("कृपया यहाँ हस्ताक्षर करें।", "kripya yaha hastakshar kare"),
                "Tamil": ("தயவுசெய்து இங்கே கையெழுத்திடுங்கள்.", "thayavuseythu inge kaiyeluthidungal"),
                "Kannada": ("ದಯವಿಟ್ಟು ಇಲ್ಲಿ ಸಹಿ ಮಾಡಿ.", "dayavittu illi sahi madi"),
                "Marathi": ("कृपया येथे स्वाक्षरी करा.", "krupya yethe svakshari kara")
            },
            "image": "work_sign.png"
        },
        {
            "word_id": "report_done",
            "translations": {
                "English": ("I completed the report.", "i completed the report"),
                "Telugu": ("నేను రిపోర్ట్ పూర్తి చేశాను.", "nenu report poorthi chesaanu"),
                "Hindi": ("मैंने रिपोर्ट पूरी कर ली है।", "maine report poori kar lee hai"),
                "Tamil": ("நான் அறிக்கையை முடித்துவிட்டேன்.", "naan arikkaiyai mudithuvitten"),
                "Kannada": ("ನಾನು ವರದಿಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿದ್ದೇನೆ.", "naanu varadiyannu purnagolisiddene"),
                "Marathi": ("मी अहवाल पूर्ण केला आहे.", "mi ahval purna kela aahe")
            },
            "image": "work_report.png"
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
    # Since we updated the dictionary in the last turn, let's locate the last key "Story Reading"
    # and insert our new categories after it.
    story_reading_str = '"Story Reading": ['
    story_reading_idx = content.find(story_reading_str)
    
    if story_reading_idx != -1:
        # Find the closing bracket of Story Reading: which is the bracket right before the end of the dictionary
        # Let's locate the ']' of Story Reading
        next_bracket = content.find(']', story_reading_idx)
        # The closing dictionary brace is right after that (with some formatting)
        closing_brace_idx = content.find('}', next_bracket)
        
        # We replace the closing brace of the dictionary with our new entries and the closing brace
        replacement = ",\n" + new_categories_str + "\n}"
        new_content = content[:closing_brace_idx] + replacement + content[closing_brace_idx+1:]
        
        # Also, let's update the `categories` list inside `get_or_create_language_pair`!
        # Search for categories list
        old_cat_list = 'categories = [\n            "Greetings", "Numbers", "Colors", "Family", "Food", \n            "Animals", "Daily Objects", "Daily Conversations", \n            "Sentence Practice", "Story Reading"\n        ]'
        new_cat_list = 'categories = [\n            "Greetings", "Numbers", "Colors", "Family", "Food", \n            "Animals", "Daily Objects", "Daily Conversations", \n            "Sentence Practice", "Story Reading",\n            "At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations"\n        ]'
        if old_cat_list in new_content:
            new_content = new_content.replace(old_cat_list, new_cat_list)
        else:
            # Try a slightly different format
            new_content = new_content.replace('"Story Reading"', '"Story Reading", "At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations"')
            
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully expanded MULTILINGUAL_DICTIONARY and categories list in language_learning_service.py!")
    else:
        print("Error: Could not locate 'Story Reading' key inside dictionary.")
else:
    print("Error: service path not found.")


# Step 2: Database Migration to insert the 4 new conversational lessons and their vocabulary
db_path = os.path.join(base_dir, "literacy.db")
if os.path.exists(db_path):
    print("Connecting to literacy.db for conversational migration...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Define local dictionary for execution
    exec("MULTILINGUAL_DICTIONARY = {" + new_categories_str + "}", globals())
    
    cursor.execute("SELECT id, known_lang, target_lang FROM language_pairs")
    pairs = cursor.fetchall()
    
    lessons_added = 0
    words_added = 0
    for p in pairs:
        pair_id = p["id"]
        known = p["known_lang"]
        target = p["target_lang"]
        print(f"Syncing conversations for language pair {known} -> {target}...")
        
        categories = ["At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations"]
        for idx, cat in enumerate(categories, 11):
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
    print(f"Migration completed. Created {lessons_added} new speaking lessons and synced {words_added} conversations!")
else:
    print("Error: database path not found.")
