import os
import sqlite3

# Define the new expanded dictionary string
expanded_dict_str = """MULTILINGUAL_DICTIONARY = {
    "Greetings": [
        {
            "word_id": "hello",
            "translations": {
                "English": ("Hello", "hello"),
                "Telugu": ("నమస్కారం", "namaskaram"),
                "Hindi": ("नमस्ते", "namaste"),
                "Tamil": ("வணக்கம்", "vanakkam"),
                "Kannada": ("ನಮಸ್ಕಾರ", "namaskara"),
                "Marathi": ("नमस्कार", "namaskar")
            },
            "image": "hello.png"
        },
        {
            "word_id": "thank_you",
            "translations": {
                "English": ("Thank you", "thank you"),
                "Telugu": ("ధన్యవాదాలు", "dhanyavadalu"),
                "Hindi": ("धन्यवाद", "dhanyavaad"),
                "Tamil": ("நன்றி", "nanri"),
                "Kannada": ("ಧನ್ಯವಾದಗಳು", "dhanyavadagalu"),
                "Marathi": ("धन्यवाद", "dhanyavaad")
            },
            "image": "thank_you.png"
        },
        {
            "word_id": "good_morning",
            "translations": {
                "English": ("Good morning", "good morning"),
                "Telugu": ("శుభోదయం", "shubhodhayam"),
                "Hindi": ("सुप्रभात", "suprabhaat"),
                "Tamil": ("காலை வணக்கம்", "kaalai vanakkam"),
                "Kannada": ("ಶುಭೋದಯ", "shubhodaya"),
                "Marathi": ("शुभ सकाळ", "shubh sakaal")
            },
            "image": "good_morning.png"
        },
        {
            "word_id": "good_night",
            "translations": {
                "English": ("Good night", "good night"),
                "Telugu": ("శుభ రాత్రి", "shubha raatri"),
                "Hindi": ("शुभ रात्रि", "shubh raatri"),
                "Tamil": ("இரவு வணக்கம்", "iravu vanakkam"),
                "Kannada": ("ಶುಭ ರಾತ್ರಿ", "shubha raatri"),
                "Marathi": ("शुभ रात्री", "shubh raatri")
            },
            "image": "good_night.png"
        },
        {
            "word_id": "goodbye",
            "translations": {
                "English": ("Goodbye", "goodbye"),
                "Telugu": ("సెలవు", "selavu"),
                "Hindi": ("अलविदा", "alvida"),
                "Tamil": ("போய் வருகிறேன்", "poi varugiren"),
                "Kannada": ("ಹೋಗಿ ಬರುತ್ತೇನೆ", "hogi baruttene"),
                "Marathi": ("निरोप", "nirop")
            },
            "image": "goodbye.png"
        },
        {
            "word_id": "please",
            "translations": {
                "English": ("Please", "please"),
                "Telugu": ("దయచేసి", "dayachesi"),
                "Hindi": ("कृपया", "kripya"),
                "Tamil": ("தயவுசெய்து", "thayavuseythu"),
                "Kannada": ("ದಯವಿಟ್ಟು", "dayavittu"),
                "Marathi": ("कृपया", "krupya")
            },
            "image": "please.png"
        },
        {
            "word_id": "sorry",
            "translations": {
                "English": ("Sorry", "sorry"),
                "Telugu": ("క్షమించండి", "kshaminchandi"),
                "Hindi": ("माफ़ कीजिये", "maaf kijiye"),
                "Tamil": ("மன்னிக்கவும்", "mannikkavum"),
                "Kannada": ("ಕ್ಷಮಿಸಿ", "kshamisi"),
                "Marathi": ("माफ करा", "maaf kara")
            },
            "image": "sorry.png"
        }
    ],
    "Numbers": [
        {
            "word_id": "one",
            "translations": {
                "English": ("One", "one"),
                "Telugu": ("ఒకటి", "okati"),
                "Hindi": ("एक", "ek"),
                "Tamil": ("ஒன்று", "ondru"),
                "Kannada": ("ಒಂದು", "ondu"),
                "Marathi": ("एक", "ek")
            },
            "image": "number_1.png"
        },
        {
            "word_id": "two",
            "translations": {
                "English": ("Two", "two"),
                "Telugu": ("రెండు", "rendu"),
                "Hindi": ("दो", "do"),
                "Tamil": ("இரண்டு", "irandu"),
                "Kannada": ("ಎರಡು", "eradu"),
                "Marathi": ("दोन", "don")
            },
            "image": "number_2.png"
        },
        {
            "word_id": "three",
            "translations": {
                "English": ("Three", "three"),
                "Telugu": ("మూడు", "moodu"),
                "Hindi": ("तीन", "teen"),
                "Tamil": ("மூன்று", "moondru"),
                "Kannada": ("ಮೂರು", "mooru"),
                "Marathi": ("तीन", "teen")
            },
            "image": "number_3.png"
        },
        {
            "word_id": "four",
            "translations": {
                "English": ("Four", "four"),
                "Telugu": ("నాలుగు", "naalugu"),
                "Hindi": ("चार", "chaar"),
                "Tamil": ("நான்கு", "naangu"),
                "Kannada": ("ನಾಲ್ಕು", "naalku"),
                "Marathi": ("चार", "chaar")
            },
            "image": "number_4.png"
        },
        {
            "word_id": "five",
            "translations": {
                "English": ("Five", "five"),
                "Telugu": ("ఐదు", "aidu"),
                "Hindi": ("पाँच", "paanch"),
                "Tamil": ("ஐந்து", "ainthu"),
                "Kannada": ("ಐದು", "aidu"),
                "Marathi": ("पाच", "paach")
            },
            "image": "number_5.png"
        },
        {
            "word_id": "ten",
            "translations": {
                "English": ("Ten", "ten"),
                "Telugu": ("పది", "padi"),
                "Hindi": ("दस", "das"),
                "Tamil": ("பத்து", "pathu"),
                "Kannada": ("ಹತ್ತು", "hattu"),
                "Marathi": ("दहा", "daha")
            },
            "image": "number_10.png"
        }
    ],
    "Colors": [
        {
            "word_id": "red",
            "translations": {
                "English": ("Red", "red"),
                "Telugu": ("ఎరుపు", "erupu"),
                "Hindi": ("लाल", "laal"),
                "Tamil": ("சிவப்பு", "sivappu"),
                "Kannada": ("ಕೆಂಪು", "kempu"),
                "Marathi": ("लाल", "laal")
            },
            "image": "color_red.png"
        },
        {
            "word_id": "blue",
            "translations": {
                "English": ("Blue", "blue"),
                "Telugu": ("నీలం", "neelam"),
                "Hindi": ("नीला", "neela"),
                "Tamil": ("நீலம்", "neelam"),
                "Kannada": ("ನೀಲಿ", "neeli"),
                "Marathi": ("निळा", "nila")
            },
            "image": "color_blue.png"
        },
        {
            "word_id": "green",
            "translations": {
                "English": ("Green", "green"),
                "Telugu": ("పచ్చ", "pachcha"),
                "Hindi": ("हरा", "hara"),
                "Tamil": ("பச்சை", "pachai"),
                "Kannada": ("ಹಸಿರು", "hasiru"),
                "Marathi": ("हिरवा", "hirva")
            },
            "image": "color_green.png"
        },
        {
            "word_id": "yellow",
            "translations": {
                "English": ("Yellow", "yellow"),
                "Telugu": ("పసుపు", "pasupu"),
                "Hindi": ("पीला", "peela"),
                "Tamil": ("மஞ்சள்", "manjal"),
                "Kannada": ("ಹಳದಿ", "haladi"),
                "Marathi": ("पिवळा", "pivla")
            },
            "image": "color_yellow.png"
        },
        {
            "word_id": "black",
            "translations": {
                "English": ("Black", "black"),
                "Telugu": ("నలుపు", "nalupu"),
                "Hindi": ("काला", "kaala"),
                "Tamil": ("கருப்பு", "karuppu"),
                "Kannada": ("ಕಪ್ಪು", "kappu"),
                "Marathi": ("काळा", "kala")
            },
            "image": "color_black.png"
        }
    ],
    "Family": [
        {
            "word_id": "mother",
            "translations": {
                "English": ("Mother", "mother"),
                "Telugu": ("అమ్మ", "amma"),
                "Hindi": ("माँ", "maa"),
                "Tamil": ("அம்மா", "amma"),
                "Kannada": ("ಅಮ್ಮ", "amma"),
                "Marathi": ("आई", "aai")
            },
            "image": "family_mother.png"
        },
        {
            "word_id": "father",
            "translations": {
                "English": ("Father", "father"),
                "Telugu": ("నాన్న", "naanna"),
                "Hindi": ("पिता", "pita"),
                "Tamil": ("அಪ್ಪா", "appa"),
                "Kannada": ("ಅಪ್ಪ", "appa"),
                "Marathi": ("वडील", "vadil")
            },
            "image": "family_father.png"
        },
        {
            "word_id": "brother",
            "translations": {
                "English": ("Brother", "brother"),
                "Telugu": ("సహోదరుడు", "sahodarudu"),
                "Hindi": ("भाई", "bhai"),
                "Tamil": ("சகோதரன்", "sagotharan"),
                "Kannada": ("ಸಹೋದರ", "sahodara"),
                "Marathi": ("भाऊ", "bhau")
            },
            "image": "family_brother.png"
        },
        {
            "word_id": "sister",
            "translations": {
                "English": ("Sister", "sister"),
                "Telugu": ("సహోదరి", "sahodari"),
                "Hindi": ("बहन", "behan"),
                "Tamil": ("சகோதரி", "sagothari"),
                "Kannada": ("ಸಹೋದರಿ", "sahodari"),
                "Marathi": ("बहीण", "bahin")
            },
            "image": "family_sister.png"
        }
    ],
    "Food": [
        {
            "word_id": "water",
            "translations": {
                "English": ("Water", "water"),
                "Telugu": ("నీరు", "neeru"),
                "Hindi": ("पानी", "paani"),
                "Tamil": ("தண்ணீர்", "thanneer"),
                "Kannada": ("ನೀರು", "neeru"),
                "Marathi": ("पाणी", "paani")
            },
            "image": "food_water.png"
        },
        {
            "word_id": "milk",
            "translations": {
                "English": ("Milk", "milk"),
                "Telugu": ("పాలు", "paalu"),
                "Hindi": ("दूध", "doodh"),
                "Tamil": ("பால்", "paal"),
                "Kannada": ("ಹಾಲು", "haalu"),
                "Marathi": ("दूध", "doodh")
            },
            "image": "food_milk.png"
        },
        {
            "word_id": "apple",
            "translations": {
                "English": ("Apple", "apple"),
                "Telugu": ("ఆపిల్", "apple"),
                "Hindi": ("सेब", "seb"),
                "Tamil": ("ஆப்பிள்", "aappil"),
                "Kannada": ("ಸೇಬು", "seebu"),
                "Marathi": ("सफरचंद", "safarchand")
            },
            "image": "food_apple.png"
        },
        {
            "word_id": "rice",
            "translations": {
                "English": ("Rice", "rice"),
                "Telugu": ("అన్నం", "annam"),
                "Hindi": ("चावल", "chaaval"),
                "Tamil": ("அரிசி", "arisi"),
                "Kannada": ("ಅಕ್ಕಿ", "akki"),
                "Marathi": ("भात", "bhaat")
            },
            "image": "food_rice.png"
        }
    ],
    "Animals": [
        {
            "word_id": "cat",
            "translations": {
                "English": ("Cat", "cat"),
                "Telugu": ("పిల్లి", "pilli"),
                "Hindi": ("बिल्ली", "billi"),
                "Tamil": ("பூனை", "poonai"),
                "Kannada": ("ಬೆಕ್ಕು", "bekku"),
                "Marathi": ("मांजर", "manjar")
            },
            "image": "animal_cat.png"
        },
        {
            "word_id": "dog",
            "translations": {
                "English": ("Dog", "dog"),
                "Telugu": ("కుక్క", "kukka"),
                "Hindi": ("कुत्ता", "kutta"),
                "Tamil": ("நாய்", "naai"),
                "Kannada": ("ನಾಯಿ", "naayi"),
                "Marathi": ("कुत्रा", "kutra")
            },
            "image": "animal_dog.png"
        },
        {
            "word_id": "cow",
            "translations": {
                "English": ("Cow", "cow"),
                "Telugu": ("ఆవు", "aavu"),
                "Hindi": ("गाय", "gaay"),
                "Tamil": ("பசு", "pasu"),
                "Kannada": ("ಹಸು", "hasu"),
                "Marathi": ("गाय", "gaay")
            },
            "image": "animal_cow.png"
        },
        {
            "word_id": "lion",
            "translations": {
                "English": ("Lion", "lion"),
                "Telugu": ("సింహం", "simham"),
                "Hindi": ("शेर", "sher"),
                "Tamil": ("சிங்கம்", "singam"),
                "Kannada": ("ಸಿಂಹ", "simha"),
                "Marathi": ("सिंह", "sinha")
            },
            "image": "animal_lion.png"
        }
    ],
    "Daily Objects": [
        {
            "word_id": "book",
            "translations": {
                "English": ("Book", "book"),
                "Telugu": ("ಪುಸ್ತಕం", "pustakam"),
                "Hindi": ("किताब", "kitaab"),
                "Tamil": ("புத்தகம்", "puthagam"),
                "Kannada": ("ಪುಸ್ತಕ", "pustaka"),
                "Marathi": ("पुस्तक", "pustak")
            },
            "image": "object_book.png"
        },
        {
            "word_id": "pen",
            "translations": {
                "English": ("Pen", "pen"),
                "Telugu": ("పెన్ను", "pennu"),
                "Hindi": ("कलम", "kalam"),
                "Tamil": ("பேனா", "peena"),
                "Kannada": ("ಪೇನಾ", "pena"),
                "Marathi": ("पेन", "pen")
            },
            "image": "object_pen.png"
        },
        {
            "word_id": "table",
            "translations": {
                "English": ("Table", "table"),
                "Telugu": ("మేజా", "meeja"),
                "Hindi": ("मेज़", "mez"),
                "Tamil": ("மேஜை", "meejai"),
                "Kannada": ("ಮೇಜು", "meeju"),
                "Marathi": ("टेबल", "tebal")
            },
            "image": "object_table.png"
        },
        {
            "word_id": "chair",
            "translations": {
                "English": ("Chair", "chair"),
                "Telugu": ("कुर्ची", "kurchi"),
                "Hindi": ("कुर्सी", "kursi"),
                "Tamil": ("நாற்காலி", "naarkali"),
                "Kannada": ("ಖುರ್ಚಿ", "khurchi"),
                "Marathi": ("खुर्ची", "khurchi")
            },
            "image": "object_chair.png"
        }
    ],
    "Daily Conversations": [
        {
            "word_id": "whats_name",
            "translations": {
                "English": ("What is your name?", "what is your name"),
                "Telugu": ("मी పేరు ఏమిటి?", "mee peru emiti"),
                "Hindi": ("आपका नाम क्या है?", "aapka naam kya hai"),
                "Tamil": ("உங்கள் பெயர் என்ன?", "ungal peyar enna"),
                "Kannada": ("ನಿಮ್ಮ ಹೆಸರೇನು?", "nimma hesarenu"),
                "Marathi": ("तुमचे नाव काय आहे?", "tumche naav kay aahe")
            },
            "image": "conv_name.png"
        },
        {
            "word_id": "my_name_john",
            "translations": {
                "English": ("My name is John.", "my name is john"),
                "Telugu": ("నా పేరు జాన్.", "naa peru john"),
                "Hindi": ("मेरा नाम जॉन है।", "mera naam john hai"),
                "Tamil": ("என் பெயர் ஜான்.", "en peyar john"),
                "Kannada": ("ನನ್ನ ಹೆಸರು ಜಾನ್.", "nanna hesaru john"),
                "Marathi": ("माझे नाव जॉन आहे.", "mazhe naav john aahe")
            },
            "image": "conv_myname.png"
        },
        {
            "word_id": "how_are_you",
            "translations": {
                "English": ("How are you?", "how are you"),
                "Telugu": ("మీరు ఎలా ఉన్నారు?", "meeru ela unnaru"),
                "Hindi": ("आप कैसे हैं?", "aap kaise hain"),
                "Tamil": ("நீங்கள் எப்படி இருக்கிறீர்கள்?", "neengal eppadi irukkireergall"),
                "Kannada": ("ನೀವು ಹೇಗಿದ್ದೀರಾ?", "neevu hegiddira"),
                "Marathi": ("तुम्ही कसे आहात?", "tumhi kase aahat")
            },
            "image": "conv_howareyou.png"
        },
        {
            "word_id": "i_am_fine",
            "translations": {
                "English": ("I am fine.", "i am fine"),
                "Telugu": ("నేను బాగున్నాను.", "nenu baagunnanu"),
                "Hindi": ("मैं ठीक हूँ।", "main theek hoon"),
                "Tamil": ("நான் நலமாக இருக்கிறேன்.", "naan nalamaaga irukkiren"),
                "Kannada": ("ನಾನು ಆರಾಮಾಗಿದ್ದೇನೆ.", "naanu aaramaagiddene"),
                "Marathi": ("मी ठीक आहे.", "mi theek aahe")
            },
            "image": "conv_iamfine.png"
        }
    ],
    "Sentence Practice": [
        {
            "word_id": "i_read",
            "translations": {
                "English": ("I am reading.", "i am reading"),
                "Telugu": ("నేను చదువుతున్నాను.", "nenu chaduvuthunnanu"),
                "Hindi": ("मैं पढ़ रहा हूँ।", "main padh raha hoon"),
                "Tamil": ("நான் படிக்கிறேன்.", "naan padikkiren"),
                "Kannada": ("ನಾನು ಓದುತ್ತಿದ್ದೇನೆ.", "naanu oduttiddene"),
                "Marathi": ("मी वाचत आहे.", "mi vaachat aahe")
            },
            "image": "sent_reading.png"
        },
        {
            "word_id": "i_write",
            "translations": {
                "English": ("I am writing.", "i am writing"),
                "Telugu": ("నేను రాస్తున్నాను.", "nenu raasthunnanu"),
                "Hindi": ("मैं लिख रहा हूँ।", "main likh raha hoon"),
                "Tamil": ("நான் எழுதுகிறேன்.", "naan ezhuthugiren"),
                "Kannada": ("ನಾನು ಬರೆಯುತ್ತಿದ್ದೇನೆ.", "naanu bareyuttiddene"),
                "Marathi": ("मी लिहित आहे.", "mi lihit aahe")
            },
            "image": "sent_writing.png"
        },
        {
            "word_id": "we_learn",
            "translations": {
                "English": ("We are learning.", "we are learning"),
                "Telugu": ("మేము నేర్చుకుంటున్నాము.", "memu nerchukuntunnamu"),
                "Hindi": ("हम सीख रहे हैं।", "hum seekh rahe hain"),
                "Tamil": ("நாங்கள் கற்கிறோம்.", "naangal karkiroam"),
                "Kannada": ("ನಾವು ಕಲಿಯುತ್ತಿದ್ದೇವೆ.", "naavu kaliyuttiddeve"),
                "Marathi": ("आम्ही शिकत आहोत.", "aamhi shikat aahot")
            },
            "image": "sent_learning.png"
        }
    ],
    "Story Reading": [
        {
            "word_id": "story_crow",
            "translations": {
                "English": ("A thirsty crow found water.", "a thirsty crow found water"),
                "Telugu": ("దాహంతో ఉన్న కాకికి నీరు దొరికింది.", "daahamtho unna kaakiki neeru dorikindi"),
                "Hindi": ("एक प्यासे कौवे को पानी मिला।", "ek pyaase kauve ko paani mila"),
                "Tamil": ("ஒரு தாகமுள்ள காகம் நீரைக் கண்டது.", "oru thaagamulla kaagam neerai kandathu"),
                "Kannada": ("ಬಾಯಾರಿದ ಕಾಗೆಗೆ ನೀರು ಸಿಕ್ಕಿತು.", "bayaarida kaagege neeru sikkitu"),
                "Marathi": ("एका तहानलेल्या कावळ्याला पाणी सापडले.", "eka tahanlelya kawalyala pani sapadle")
            },
            "image": "story_crow.png"
        },
        {
            "word_id": "story_hare_tortoise",
            "translations": {
                "English": ("The slow tortoise won the race.", "the slow tortoise won the race"),
                "Telugu": ("నెమ్మదిగా ఉన్న తాబేలు పరుగు పందెంలో గెలిచింది.", "nemmadiga unna taabelu parugu pandemlo gelichindi"),
                "Hindi": ("धीमी कछुए ने दौड़ जीत ली।", "dheemi kachhue ne daud jeet lee"),
                "Tamil": ("மெதுவான ஆமை பந்தயத்தில் வென்றது.", "methuvaana aamai panthayathil vendrathu"),
                "Kannada": ("ನಿಧಾನವಾದ ಆಮೆ ಓಟದ ಪಂದ್ಯವನ್ನು ಗೆದ್ದಿತು.", "nidhaanavaada aame otada pandyavannu gedditu"),
                "Marathi": ("हळू चालणाऱ्या कासवाने शर्यत जिंकली.", "halu chalnarya kasavane sharyat jinkli")
            },
            "image": "story_tortoise.png"
        }
    ]
}"""

# Step 1: Update the dictionary inside language_learning_service.py
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
service_path = os.path.join(base_dir, "language_learning_service.py")

if os.path.exists(service_path):
    print("Reading language_learning_service.py...")
    with open(service_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    start_idx = None
    end_idx = None
    
    for idx, line in enumerate(lines):
        if "MULTILINGUAL_DICTIONARY = {" in line:
            start_idx = idx
            break
            
    if start_idx is not None:
        brace_count = 1
        for idx in range(start_idx + 1, len(lines)):
            line = lines[idx]
            brace_count += line.count("{") - line.count("}")
            if brace_count == 0:
                end_idx = idx
                break
                
    if start_idx is not None and end_idx is not None:
        print(f"Found dictionary from line {start_idx + 1} to {end_idx + 1}. Replacing...")
        new_content = "".join(lines[:start_idx]) + expanded_dict_str + "".join(lines[end_idx + 1:])
        with open(service_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        print("Successfully updated MULTILINGUAL_DICTIONARY definition in language_learning_service.py!")
    else:
        print("Error: Could not locate MULTILINGUAL_DICTIONARY block.")
else:
    print("Error: language_learning_service.py not found.")


# Step 2: Database Migration to sync existing language pairs
db_path = os.path.join(base_dir, "literacy.db")
if os.path.exists(db_path):
    print("Connecting to literacy.db for migration...")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Let's import the newly updated dictionary
    # Since we modified the file, we can parse our local expanded dictionary directly
    # or evaluate the MULTILINGUAL_DICTIONARY variable
    exec(expanded_dict_str, globals())
    
    cursor.execute("SELECT id, known_lang, target_lang FROM language_pairs")
    pairs = cursor.fetchall()
    
    words_added = 0
    for p in pairs:
        pair_id = p["id"]
        known = p["known_lang"]
        target = p["target_lang"]
        print(f"Syncing language pair {known} -> {target}...")
        
        # Check all categories
        for cat_name, vocab_list in MULTILINGUAL_DICTIONARY.items():
            # Get the lesson_id for this pair and category
            cursor.execute("SELECT id FROM language_lessons WHERE pair_id = ? AND category = ?", (pair_id, cat_name))
            lesson_row = cursor.fetchone()
            if not lesson_row:
                continue
            lesson_id = lesson_row["id"]
            
            # Sync vocabulary words under this lesson
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
    print(f"Migration finished. Added {words_added} new vocabulary translations to active user database profiles!")
else:
    print("Error: literacy.db not found for migration.")
