import sqlite3
import os

new_lessons = [
    # ENGLISH LESSONS
    {
        "title": "Daily Greeting Expressions",
        "category": "speaking",
        "language": "English",
        "content": "Learn how to greet people professionally in English: 'Good morning', 'How can I help you today?', 'It is a pleasure to meet you'. Practice saying these expressions.",
        "difficulty": "Basic"
    },
    {
        "title": "Digital Devices Vocabulary",
        "category": "vocabulary",
        "language": "English",
        "content": "Learn common words for technology: Computer, Keyboard, Screen, Internet, Website, Password, Email. Match the word with the device you use every day.",
        "difficulty": "Basic"
    },
    {
        "title": "Active Verbs at Work",
        "category": "grammar",
        "language": "English",
        "content": "Verbs are action words. In an office, you: 'write' reports, 'send' emails, 'call' clients, 'organize' files, and 'attend' meetings. Example: I write reports every Monday.",
        "difficulty": "Intermediate"
    },
    {
        "title": "Reading a Simple Transit Map",
        "category": "reading",
        "language": "English",
        "content": "Reading signs is crucial. Learn words like: Platform, Ticket Counter, Exit, Entrance, Delayed, On Time. Example: The train departs from Platform 3.",
        "difficulty": "Intermediate"
    },
    {
        "title": "Writing a Professional Email",
        "category": "writing",
        "language": "English",
        "content": "A professional email starts with a formal salutation: 'Dear Mr. Smith,'. It ends with a professional closing: 'Sincerely,' or 'Best regards,'. Write a short request for leave.",
        "difficulty": "Advanced"
    },
    {
        "title": "Job Interview Introduction",
        "category": "speaking",
        "language": "English",
        "content": "Practice introducing yourself in a job interview: 'Hello, my name is Ravi. I have three years of experience in sales. I am excited about this opportunity.' Pronounce these words clearly.",
        "difficulty": "Advanced"
    },

    # HINDI LESSONS
    {
        "title": "दैनिक अभिवादन शब्द (Daily Greetings)",
        "category": "speaking",
        "language": "Hindi",
        "content": "लोगों से बातचीत शुरू करने के लिए इन अभिवादन शब्दों का उपयोग करें: 'नमस्ते', 'आप कैसे हैं?', 'आपसे मिलकर बहुत अच्छा लगा'। इन्हें बोलने का अभ्यास करें।",
        "difficulty": "Basic"
    },
    {
        "title": "डिजिटल साक्षरता शब्दावली (Digital Tech Words)",
        "category": "vocabulary",
        "language": "Hindi",
        "content": "तकनीक से संबंधित शब्दों को समझें: कंप्यूटर (Computer), कीबोर्ड (Keyboard), इंटरनेट (Internet), वेबसाइट (Website), पासवर्ड (Password)।",
        "difficulty": "Basic"
    },
    {
        "title": "कार्यालय में उपयोग होने वाली क्रियाएं (Workplace Verbs)",
        "category": "grammar",
        "language": "Hindi",
        "content": "कामकाज में क्रिया शब्दों का सही उपयोग करें: 'लिखना' (write reports), 'भेजना' (send emails), 'आयोजन करना' (organize files)। उदाहरण: मैं रोज़ ईमेल भेजता हूँ।",
        "difficulty": "Intermediate"
    },
    {
        "title": "व्यावसायिक पत्र लेखन (Professional Letter Writing)",
        "category": "writing",
        "language": "Hindi",
        "content": "औपचारिक पत्र लिखते समय आदरणीय शब्दों का प्रयोग करें: 'आदरणीय महोदय', 'सादर प्रणाम'। अंत में 'भवदीय' या 'आपका शुभचिंतक' लिखें।",
        "difficulty": "Advanced"
    },

    # TELUGU LESSONS
    {
        "title": "రోజువారీ శుభాకాంక్షలు (Daily Greetings)",
        "category": "speaking",
        "language": "Telugu",
        "content": "ఇతరులతో సంభాషణ ప్రారంభించడానికి ఈ పదాలు ఉపయోగించండి: 'నమస్కారం', 'మీరు ఎలా ఉన్నారు?', 'మిమ్మల్ని కలవడం చాలా సంతోషంగా ఉంది'.",
        "difficulty": "Basic"
    },
    {
        "title": "కార్యాలయ పదజాలం (Workplace Verbs)",
        "category": "grammar",
        "language": "Telugu",
        "content": "ఆఫీస్ పనులలో ఉపయోగించే క్రియలు: 'రాయడం' (write reports), 'పంపడం' (send emails), 'సమావేశం' (attend meetings).",
        "difficulty": "Intermediate"
    },
    {
        "title": "కార్యాలయ ఉత్తర లేఖనం (Professional Letter Writing)",
        "category": "writing",
        "language": "Telugu",
        "content": "అధికారిక లేఖలు రాసేటప్పుడు గౌరవప్రదమైన పదాలను ఉపయోగించండి: 'గౌరవనీయులైన అధికారి గారికి', 'భవదీయుడు'.",
        "difficulty": "Advanced"
    },

    # TAMIL LESSONS
    {
        "title": "தினசரி வாழ்த்துக்கள் (Daily Greetings)",
        "category": "speaking",
        "language": "Tamil",
        "content": "மரியாதையுடன் பேசுங்கள்: 'வணக்கம்', 'நீங்கள் எப்படி இருக்கிறீர்கள்?', 'உங்களை சந்தித்ததில் மகிழ்ச்சி'.",
        "difficulty": "Basic"
    },
    {
        "title": "அலுவலகச் சொற்கள் (Workplace Verbs)",
        "category": "grammar",
        "language": "Tamil",
        "content": "அலுவலக வேலைகளில் பயன்படுத்தப்படும் சொற்கள்: 'எழுதுதல்' (write), 'அனுப்புதல்' (send), 'கோப்புகளை ஒழுங்கமைத்தல்' (organize).",
        "difficulty": "Intermediate"
    },
    {
        "title": "முறையான கடிதம் எழுதுதல் (Professional Letter Writing)",
        "category": "writing",
        "language": "Tamil",
        "content": "முறையான கடிதங்களில் பயன்படுத்தப்படும் சொற்கள்: 'மதிப்பிற்குரிய ஐயா', 'இట్లు தங்களின் உண்மையுள்ள'.",
        "difficulty": "Advanced"
    },

    # KANNADA LESSONS
    {
        "title": "ದಿನನಿತ್ಯದ ಶುಭಾಶಯಗಳು (Daily Greetings)",
        "category": "speaking",
        "language": "Kannada",
        "content": "ಸಂಭಾಷಣೆಯನ್ನು ಪ್ರಾರಂಭಿಸಲು ಈ ಪದಗಳನ್ನು ಬಳಸಿ: 'ನಮಸ್ಕಾರ', 'ನೀವು ಹೇಗಿದ್ದೀರಾ?', 'ಮಿಮ್ಮನ್ನು ಭೇಟಿಯಾಗಿದ್ದು ಸಂತೋಷ ತಂದಿದೆ'.",
        "difficulty": "Basic"
    },
    {
        "title": "ಕಚೇರಿ ಕ್ರಿಯಾಪದಗಳು (Workplace Verbs)",
        "category": "grammar",
        "language": "Kannada",
        "content": "ಕಚೇರಿಯಲ್ಲಿ ಬಳಸುವ ಕ್ರಿಯಾಪದಗಳು: 'ಬರೆಯುವುದು' (write), 'ಕಳುಹಿಸುವುದು' (send), 'ಸಂಘಟಿಸುವುದು' (organize).",
        "difficulty": "Intermediate"
    },
    {
        "title": "ಔಪಚಾರಿಕ ಪತ್ರ ಲೇಖನ (Professional Letter Writing)",
        "category": "writing",
        "language": "Kannada",
        "content": "ಔಪಚಾರಿಕ ಪತ್ರಗಳನ್ನು ಬರೆಯುವಾಗ ಬಳಸುವ ಗೌರವದ ಪದಗಳು: 'ಗೌರವಾನ್ವಿತ ಅಧಿಕಾರಿಗಳಿಗೆ', 'ತಮ್ಮ ವಿಶ್ವಾಸಿ'.",
        "difficulty": "Advanced"
    },

    # MARATHI LESSONS
    {
        "title": "दैनिक संभाषण व सदिच्छा (Daily Greetings)",
        "category": "speaking",
        "language": "Marathi",
        "content": "लोकांशी संवाद साधण्यासाठी या शब्दांचा वापर करा: 'नमस्कार', 'तुम्ही कसे आहात?', 'तुम्हाला भेटून आनंद झाला'.",
        "difficulty": "Basic"
    },
    {
        "title": "कार्यालयीन क्रियापदे (Workplace Verbs)",
        "category": "grammar",
        "language": "Marathi",
        "content": "कार्यालयात वापरायचे क्रियापद शब्द: 'लिहिणे' (write), 'पाठवणे' (send), 'फायली गोळा करणे' (organize).",
        "difficulty": "Intermediate"
    },
    {
        "title": "औपचारिक पत्र लेखन (Professional Letter Writing)",
        "category": "writing",
        "language": "Marathi",
        "content": "पत्र लेखन करताना वापरायचे शब्द: 'आदरणीय महोदय', 'आपला नम्र'.",
        "difficulty": "Advanced"
    }
]

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(base_dir, "literacy.db")

if os.path.exists(db_path):
    print(f"Connecting to database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    count = 0
    for lesson in new_lessons:
        # Check if the lesson already exists
        cursor.execute("SELECT id FROM lessons WHERE title = ? AND language = ?", (lesson["title"], lesson["language"]))
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO lessons (title, category, language, content, difficulty)
                VALUES (?, ?, ?, ?, ?)
            """, (lesson["title"], lesson["category"], lesson["language"], lesson["content"], lesson["difficulty"]))
            count += 1
            
    conn.commit()
    conn.close()
    print(f"Successfully inserted {count} new high-quality lessons into literacy.db!")
else:
    print("Error: literacy.db not found.")
