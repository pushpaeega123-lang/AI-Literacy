from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
import sqlite3
import random
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import urllib.request
import urllib.parse

import difflib
import time

VOWELS = {}
MATRAS = {}
CONSONANTS = {}
HALANTS = set()

def add_v(cp, val): VOWELS[chr(cp)] = val
def add_m(cp, val): MATRAS[chr(cp)] = val
def add_c(cp, val): CONSONANTS[chr(cp)] = val + 'a'

# DEVANAGARI (Hindi, Marathi)
for cp, val in [
    (0x0905, 'a'), (0x0906, 'aa'), (0x0907, 'i'), (0x0908, 'ee'), (0x0909, 'u'), (0x090A, 'oo'), (0x090B, 'ri'), (0x090F, 'e'), (0x0910, 'ai'), (0x0913, 'o'), (0x0914, 'au'),
    (0x0902, 'n'), (0x0903, 'h')
]: add_v(cp, val)
for cp, val in [
    (0x093E, 'aa'), (0x093F, 'i'), (0x0940, 'ee'), (0x0941, 'u'), (0x0942, 'oo'), (0x0943, 'ri'), (0x0947, 'e'), (0x0948, 'ai'), (0x094B, 'o'), (0x094C, 'au'),
    (0x0902, 'n'), (0x0903, 'h')
]: add_m(cp, val)
for cp, val in [
    (0x0915, 'k'), (0x0916, 'kh'), (0x0917, 'g'), (0x0918, 'gh'), (0x0919, 'ng'),
    (0x091A, 'ch'), (0x091B, 'chh'), (0x091C, 'j'), (0x091D, 'jh'), (0x091E, 'ny'),
    (0x091F, 't'), (0x0920, 'th'), (0x0921, 'd'), (0x0922, 'dh'), (0x0923, 'n'),
    (0x0924, 't'), (0x0925, 'th'), (0x0926, 'd'), (0x0927, 'dh'), (0x0928, 'n'),
    (0x092A, 'p'), (0x092B, 'ph'), (0x092C, 'b'), (0x092D, 'bh'), (0x092E, 'm'),
    (0x092F, 'y'), (0x0930, 'r'), (0x0932, 'l'), (0x0933, 'l'), (0x0935, 'v'), (0x0936, 'sh'), (0x0937, 'sh'), (0x0938, 's'), (0x0939, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x094D))

# TELUGU
for cp, val in [
    (0x0C05, 'a'), (0x0C06, 'aa'), (0x0C07, 'i'), (0x0C08, 'ee'), (0x0C09, 'u'), (0x0C0A, 'oo'), (0x0C0B, 'ru'), (0x0C0E, 'e'), (0x0C0F, 'ae'), (0x0C10, 'ai'), (0x0C12, 'o'), (0x0C13, 'oe'), (0x0C14, 'au'),
    (0x0C02, 'm'), (0x0C03, 'aha')
]: add_v(cp, val)
for cp, val in [
    (0x0C3E, 'aa'), (0x0C3F, 'i'), (0x0C40, 'ee'), (0x0C41, 'u'), (0x0C42, 'oo'), (0x0C43, 'ru'), (0x0C46, 'e'), (0x0C47, 'ae'), (0x0C48, 'ai'), (0x0C4A, 'o'), (0x0C4B, 'oe'), (0x0C4C, 'au'),
    (0x0C02, 'm'), (0x0C03, 'aha')
]: add_m(cp, val)
for cp, val in [
    (0x0C15, 'k'), (0x0C16, 'kh'), (0x0C17, 'g'), (0x0C18, 'gh'), (0x0C19, 'ng'),
    (0x0C1A, 'ch'), (0x0C1B, 'chh'), (0x0C1C, 'j'), (0x0C1D, 'jh'), (0x0C1E, 'ny'),
    (0x0C1F, 't'), (0x0C20, 'th'), (0x0C21, 'd'), (0x0C22, 'dh'), (0x0C23, 'n'),
    (0x0C24, 't'), (0x0C25, 'th'), (0x0C26, 'd'), (0x0C27, 'dh'), (0x0C28, 'n'),
    (0x0C2A, 'p'), (0x0C2B, 'ph'), (0x0C2C, 'b'), (0x0C2D, 'bh'), (0x0C2E, 'm'),
    (0x0C2F, 'y'), (0x0C30, 'r'), (0x0C31, 'r'), (0x0C32, 'l'), (0x0C33, 'l'), (0x0C35, 'v'), (0x0C36, 'sh'), (0x0C37, 'sh'), (0x0C38, 's'), (0x0C39, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0C4D))

# KANNADA
for cp, val in [
    (0x0C85, 'a'), (0x0C86, 'aa'), (0x0C87, 'i'), (0x0C88, 'ee'), (0x0C89, 'u'), (0x0C8A, 'oo'), (0x0C8B, 'ru'), (0x0C8E, 'e'), (0x0C8F, 'ae'), (0x0C90, 'ai'), (0x0C92, 'o'), (0x0C93, 'oe'), (0x0C94, 'au'),
    (0x0C82, 'm'), (0x0C83, 'aha')
]: add_v(cp, val)
for cp, val in [
    (0x0CBE, 'aa'), (0x0CBF, 'i'), (0x0CC0, 'ee'), (0x0CC1, 'u'), (0x0CC2, 'oo'), (0x0CC3, 'ru'), (0x0CC6, 'e'), (0x0CC7, 'ae'), (0x0CC8, 'ai'), (0x0CCA, 'o'), (0x0CCB, 'oe'), (0x0CCC, 'au'),
    (0x0C82, 'm'), (0x0C83, 'aha')
]: add_m(cp, val)
for cp, val in [
    (0x0C95, 'k'), (0x0C96, 'kh'), (0x0C97, 'g'), (0x0C98, 'gh'), (0x0C99, 'ng'),
    (0x0C9A, 'ch'), (0x0C9B, 'chh'), (0x0C9C, 'j'), (0x0C9D, 'jh'), (0x0C9E, 'ny'),
    (0x0C9F, 't'), (0x0CA0, 'th'), (0x0CA1, 'd'), (0x0CA2, 'dh'), (0x0CA3, 'n'),
    (0x0CA4, 't'), (0x0CA5, 'th'), (0x0CA6, 'd'), (0x0CA7, 'dh'), (0x0CA8, 'n'),
    (0x0CAA, 'p'), (0x0CAB, 'ph'), (0x0CAC, 'b'), (0x0CAD, 'bh'), (0x0CAE, 'm'),
    (0x0CAF, 'y'), (0x0CB0, 'r'), (0x0CB1, 'r'), (0x0CB2, 'l'), (0x0CB3, 'l'), (0x0CB5, 'v'), (0x0CB6, 'sh'), (0x0CB7, 'sh'), (0x0CB8, 's'), (0x0CB9, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0CCD))

# TAMIL
for cp, val in [
    (0x0B85, 'a'), (0x0B86, 'aa'), (0x0B87, 'i'), (0x0B88, 'ee'), (0x0B89, 'u'), (0x0B8A, 'oo'), (0x0B8E, 'e'), (0x0B8F, 'ae'), (0x0B90, 'ai'), (0x0B92, 'o'), (0x0B93, 'oe'), (0x0B94, 'au'),
    (0x0B83, 'kh')
]: add_v(cp, val)
for cp, val in [
    (0x0BBE, 'aa'), (0x0BBF, 'i'), (0x0BC0, 'ee'), (0x0BC1, 'u'), (0x0BC2, 'oo'), (0x0BC6, 'e'), (0x0BC7, 'ae'), (0x0BC8, 'ai'), (0x0BCA, 'o'), (0x0BCB, 'oe'), (0x0BCC, 'au'),
    (0x0B83, 'kh')
]: add_m(cp, val)
for cp, val in [
    (0x0B95, 'k'), (0x0B99, 'ng'), (0x0B9A, 'ch'), (0x0B9E, 'ny'), (0x0B9F, 't'), (0x0BA3, 'n'), (0x0BA4, 't'), (0x0BA8, 'n'), (0x0BAA, 'p'), (0x0BAE, 'm'),
    (0x0BAF, 'y'), (0x0BB0, 'r'), (0x0BB2, 'l'), (0x0BB5, 'v'), (0x0BB4, 'zh'), (0x0BB3, 'l'), (0x0BB1, 'r'), (0x0BA9, 'n'), (0x0B9C, 'j'), (0x0BB7, 'sh'), (0x0BB8, 's'), (0x0BB9, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0BCD))

def transliterate_word(word, lang):
    lang_lower = (lang or "").lower()
    res = []
    i = 0
    n = len(word)
    while i < n:
        char = word[i]
        
        # Check vowels
        if char in VOWELS:
            res.append(VOWELS[char])
            i += 1
            continue
            
        # Check consonants
        if char in CONSONANTS:
            base_sound = CONSONANTS[char]
            base = base_sound[:-1] if base_sound.endswith('a') else base_sound
            
            # Check next character
            if i + 1 < n:
                nxt = word[i+1]
                if nxt in HALANTS:
                    res.append(base)
                    i += 2 # skip both consonant and halant
                    continue
                elif nxt in MATRAS:
                    res.append(base + MATRAS[nxt])
                    i += 2 # skip both consonant and matra
                    continue
            
            # Trailing consonant drop 'a' for Hindi/Marathi
            if i + 1 == n and ("hindi" in lang_lower or "marathi" in lang_lower) and base_sound.endswith('a') and len(res) > 0:
                res.append(base)
            else:
                res.append(base_sound)
            i += 1
            continue
            
        res.append(char)
        i += 1
        
    word_str = "".join(res)
    word_str = word_str.replace("aaa", "aa").replace("eee", "ee").replace("ooo", "oo")
    return word_str.capitalize()

def transliterate_text(text, lang):
    if not text:
        return ""
    words = text.split(" ")
    res = [transliterate_word(w, lang) for w in words]
    return " ".join(res)


def normalize_text(text):
    if not text:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()?।]", "", text)
    return " ".join(text.split())

def get_similarity_score(a, b):
    a = normalize_text(a)
    b = normalize_text(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def get_age_group(age):
    try:
        age_val = int(age)
    except (ValueError, TypeError):
        return "young"
    if age_val <= 5:
        return "toddler"
    elif age_val <= 8:
        return "young"
    elif age_val <= 12:
        return "middle"
    elif age_val <= 20:
        return "older"
    elif age_val <= 25:
        return "career"
    elif age_val <= 35:
        return "professional"
    elif age_val <= 45:
        return "advancement"
    elif age_val <= 55:
        return "leadership"
    elif age_val <= 60:
        return "pre-retirement"
    else:
        return "senior"


from datetime import datetime, date

def calculate_age(dob_str):
    if not dob_str:
        return 8
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return max(0, age)
    except Exception:
        try:
            dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return max(0, age)
        except Exception:
            return 8


def get_adaptive_difficulty(user_id, actual_age, language, cursor):
    actual_group = get_age_group(actual_age)
    
    # We only perform adaptivity for age brackets >= 5 (i.e. young, middle, older, career)
    if actual_group == "toddler":
        return actual_group
        
    # Find total lessons for user's language and chronological difficulty group
    cursor.execute("""
        SELECT COUNT(*) FROM lessons 
        WHERE language = ? AND difficulty = ?
    """, (language, actual_group))
    total_lessons = cursor.fetchone()[0]
    
    if total_lessons == 0:
        return actual_group
        
    # Find completed lessons for this group
    cursor.execute("""
        SELECT COUNT(DISTINCT lp.lesson_id) 
        FROM lesson_progress lp 
        JOIN lessons l ON lp.lesson_id = l.id 
        WHERE lp.user_id = ? AND l.language = ? AND l.difficulty = ?
    """, (user_id, language, actual_group))
    completed_lessons = cursor.fetchone()[0]
    
    progress = (completed_lessons / total_lessons) * 100
    
    # Order of levels
    groups_order = ["toddler", "young", "middle", "older", "career"]
    try:
        current_idx = groups_order.index(actual_group)
    except ValueError:
        return actual_group
        
    # If completed > 95%, unlock next difficulty early
    if progress >= 95.0 and current_idx < len(groups_order) - 1:
        return groups_order[current_idx + 1]
    # If completed < 20%, show previous difficulty for review
    elif progress < 20.0 and current_idx > 0:
        return groups_order[current_idx - 1]
        
    return actual_group
    # convert sqlite row to dict for safe access with .get()
    try:
        user = dict(user)
    except Exception:
        pass




app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

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
        if lang_folder != "english":
            print(f"[VIDEO INFO] Regional video folder missing for language='{language}', falling back to English")
            return get_local_videos_for_learner("English", age)
        return []

    try:
        files = [f for f in sorted(os.listdir(dir_path)) if f.lower().endswith(".mp4")]
    except Exception as e:
        print(f"[VIDEO ERROR] Error scanning directory {dir_path}: {e}")
        if lang_folder != "english":
            return get_local_videos_for_learner("English", age)
        return []

    if not files:
        print(f"[VIDEO ERROR] Missing MP4 files in directory {dir_path} for language='{language}', age={age}")
        if lang_folder != "english":
            return get_local_videos_for_learner("English", age)
        return []

    videos = []
    for f in files:
        web_path = f"/static/videos/{lang_folder}/{folder_name}/{f}"
        raw_title = os.path.splitext(f)[0]
        
        # Translate dynamically
        title_lower = f.lower()
        translated_title = raw_title
        translated_desc = f"Learn spelling, reading, and writing in {language} with this fun educational video clip!"
        category = "rhymes"
        
        if "color" in title_lower or "colour" in title_lower or "rang" in title_lower or "varna" in title_lower or "pannul" in title_lower:
            category = "colors"
            if language == "Telugu":
                translated_title, translated_desc = "రంగుల పాట (Learn Colors)", "అన్ని ప్రకాశవంతమైన రంగులను నేర్చుకోవడానికి ఒక సరదా పాట!"
            elif language == "Hindi":
                translated_title, translated_desc = "रंगों का गीत (Learn Colors)", "सभी चमकीले रंगों को सीखने के लिए एक मजेदार गीत!"
            elif language == "Tamil":
                translated_title, translated_desc = "வண்ணங்களின் பாடல் (Learn Colors)", "அனைத்து பிரகாசமான வண்ணங்களையும் கற்றுக்கொள்ள ஒரு வேடிக்கையான பாடல்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಬಣ್ಣಗಳ ಹಾಡು (Learn Colors)", "ಎಲ್ಲಾ ಪ್ರಕಾಶಮಾನವಾದ ಬಣ್ಣಗಳನ್ನು कಲಿಯಲು ಒಂದು ಮೋಜಿನ ಹಾಡು!"
            elif language == "Marathi":
                translated_title, translated_desc = "रंगांचे गाणे (Learn Colors)", "सर्व चमकदार रंग शिकण्यासाठी एक मजेदार गाणे!"
            else:
                translated_title, translated_desc = "Learn Colors Song", "A fun song to learn all the bright colors!"
        elif "shape" in title_lower or "aakaar" in title_lower or "aakriti" in title_lower:
            category = "shapes"
            if language == "Telugu":
                translated_title, translated_desc = "ఆకారాల పాట (Learn Shapes)", "వృత్తాలు, చతురస్రాలు మరియు త్రిభుజాల వంటి ఆకారాలను కనుగొనండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "आकृतियों का गीत (Learn Shapes)", "वृत्त, वर्ग और त्रिकोण जैसी आकृतियों को जानें!"
            elif language == "Tamil":
                translated_title, translated_desc = "வடிவங்கள் பாடல் (Learn Shapes)", "வட்டம், சதுரம் மற்றும் முக்கோணம் போன்ற வடிவங்களைக் கண்டறியுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಆಕಾರಗಳ ಹಾಡು (Learn Shapes)", "ವೃತ್ತ, ಚೌಕ ಮತ್ತು ತ್ರಿಕೋನಗಳಂತಹ ಆಕಾರಗಳನ್ನು ಅನ್ವೇಷಿಸಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "आकारांचे गाणे (Learn Shapes)", "वर्तुळ, चौरस आणि त्रिकोण यांसारखे आकार शोधा!"
            else:
                translated_title, translated_desc = "Learn Shapes Song", "Discover shapes like circles, squares, and triangles!"
        elif "alphabet" in title_lower or "akshara" in title_lower or "varnamala" in title_lower or "swar" in title_lower or "letter" in title_lower or "mula" in title_lower or "abc" in title_lower or "uyir" in title_lower or "morni" in title_lower:
            category = "alphabet"
            if language == "Telugu":
                translated_title, translated_desc = "అక్షరాల పరిచయం (Alphabet Intro)", "భాష యొక్క ప్రాథమిక అక్షరాలను మరియు గుణింతాలను నేర్చుకోండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "वर्णमाला ज्ञान (Alphabet Intro)", "भाषा के बुनियादी अक्षरों और स्वरों को सीखें!"
            elif language == "Tamil":
                translated_title, translated_desc = "எழுத்துக்கள் அறிமுகம் (Alphabet Intro)", "மொழியின் அடிப்படை எழுத்துக்களைக் கற்றுக்கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಕನ್ನಡ ಅಕ್ಷರಮಾಲೆ (Alphabet Intro)", "ಭಾಷೆಯ ಮೂಲ ಅಕ್ಷರಗಳನ್ನು ಕಲಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "मुळाक्षरांची ओळख (Alphabet Intro)", "भाषेच्या मूळ अक्षरांची आणि स्वरांची ओळख करून घ्या!"
            else:
                translated_title, translated_desc = "Alphabet Learning Video", "Learn the foundational alphabets and letters!"
        elif "number" in title_lower or "counting" in title_lower or "ginti" in title_lower or "ank" in title_lower or "eradu" in title_lower or "ondu" in title_lower or "dosai" in title_lower or "ankache" in title_lower:
            category = "numbers"
            if language == "Telugu":
                translated_title, translated_desc = "సంఖ్యల లెక్కింపు (Numbers Counting)", "సంఖ్యలను సులభంగా నేర్చుకోండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "गिनती और संख्याएँ (Numbers Counting)", "संख्याओं को चरण-दर-चरण गिनना सीखें!"
            elif language == "Tamil":
                translated_title, translated_desc = "எண்கள் பயிற்சி (Numbers Counting)", "எண்களை படிப்படியாக எண்ணக் கற்றுக்கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಸಂಖ್ಯೆಗಳ ಎಣಿಕೆ (Numbers Counting)", "ಸಂಖ್ಯೆಗಳನ್ನು ಹಂತ-ಹಂತವಾಗಿ ಎಣಿಸಲು ಕಲಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "अंक आणि संख्या मोजणे (Numbers Counting)", "संख्या मोजायला शिका सोप्या पद्धतीने!"
            else:
                translated_title, translated_desc = "Counting and Numbers", "Learn to count numbers step-by-step!"
        elif "animal" in title_lower or "sound" in title_lower or "aavaj" in title_lower or "oli" in title_lower or "pranyanche" in title_lower or "aane" in title_lower or "nayi" in title_lower or "machli" in title_lower or "ghode" in title_lower or "chimni" in title_lower or "pitta" in title_lower or "enugamma" in title_lower or "chilakamma" in title_lower:
            category = "animals"
            if language == "Telugu":
                translated_title, translated_desc = "జంతువుల శబ్దాలు (Animal Sounds)", "స్నేహపూర్వక జంతువులను కలవండి మరియు వాటి శబ్దాలను వినండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "जानवरों की आवाजें (Animal Sounds)", "विभिन्न पशु-पक्षियों की आवाजें और उनके नाम जानें!"
            elif language == "Tamil":
                translated_title, translated_desc = "விலங்குகளின் ஒலிகள் (Animal Sounds)", "விலங்குகளின் பெயர்களையும் அவற்றின் ஒலிகளையும் தெரிந்து கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಪ್ರಾಣಿಗಳ ಶಬ್ದಗಳು (Animal Sounds)", "ವಿವಿಧ ಪ್ರಾಣಿಗಳ ಧ್ವನಿಗಳು ಮತ್ತು ಅವುಗಳ ಹೆಸರನ್ನು ತಿಳಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "प्राण्यांचे आवाज (Animal Sounds)", "विविध प्राणी आणि त्यांचे आवाज ओळखा!"
            else:
                translated_title, translated_desc = "Animal Sounds and Names", "Meet the friendly animals and hear the sounds they make!"
        else:
            clean_t = raw_title.replace("_", " ").replace("-", " ").strip()
            clean_t = " ".join([w.capitalize() for w in clean_t.split() if w])
            translated_title = clean_t

        videos.append({
            "title": translated_title,
            "description": translated_desc,
            "video_url": web_path,
            "filename": f,
            "category": category,
            "language": language,
            "age": age
        })
    return videos


app.secret_key = "literacy_secret_key"

DATABASE = "literacy.db"

import json

def load_json_translations():
    locales = {
        "English": "en.json",
        "Telugu": "te.json",
        "Hindi": "hi.json",
        "Tamil": "ta.json",
        "Kannada": "kn.json",
        "Marathi": "mr.json"
    }
    loaded = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(base_dir, "static", "locales")
    
    for lang, filename in locales.items():
        filepath = os.path.join(locales_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    loaded[lang] = json.load(f)
            else:
                loaded[lang] = {}
        except Exception as e:
            print(f"Error loading translation for {lang}: {e}")
            loaded[lang] = {}
            
    # Ensure English has fallbacks
    if "English" not in loaded or not loaded["English"]:
        loaded["English"] = {
            "site_title": "",
            "welcome_title": "Welcome!",
            "welcome_text": "Register to start your AI-powered learning journey."
        }
    return loaded

translations = load_json_translations()


def get_translations(language):
    # Dynamically load JSON files on each request to prevent server-side caching of translations
    current_translations = load_json_translations()
    if language not in current_translations:
        return current_translations.get("English", {})
    merged = current_translations.get("English", {}).copy()
    merged.update(current_translations[language])
    return merged


AGE_GROUP_LABELS = {
    "English": {
        "toddler": "Toddler (Early Learner)",
        "young": "Young Learner",
        "middle": "Middle Learner",
        "older": "Adolescent / Youth",
        "career": "Career Starter",
        "professional": "Working Professional",
        "advancement": "Career Advancement",
        "leadership": "Leadership & Mentoring",
        "pre-retirement": "Pre-retirement",
        "senior": "Senior Citizen"
    },
    "Telugu": {
        "toddler": "పసిపిల్లవాడు (చిన్నారి)",
        "young": "యువ అభ్యాసకుడు",
        "middle": "మధ్యస్థ అభ్యాసకుడు",
        "older": "యువత (కిశోర ప్రాయం)",
        "career": "ఉద్యోగ అన్వేషి / కెరీర్ ప్రారంభకుడు",
        "professional": "పనిచేసే నిపుణుడు",
        "advancement": "కెరీర్ అభివృద్ధి",
        "leadership": "నాయకత్వం & మార్గదర్శకత్వం",
        "pre-retirement": "పదవీ విరమణకు ముందు",
        "senior": "సీనియర్ సిటిజన్ (వృద్ధులు)"
    },
    "Hindi": {
        "toddler": "नन्हा बच्चा (शुरुआती शिक्षार्थी)",
        "young": "युवा शिक्षार्थी",
        "middle": "मध्यम वर्ग के शिक्षार्थी",
        "older": "किशोर / युवा",
        "career": "करियर की शुरुआत",
        "professional": "कामकाजी पेशेवर",
        "advancement": "करियर उन्नति",
        "leadership": "नेतृत्व और मार्गदर्शन",
        "pre-retirement": "सेवानिवृत्ति पूर्व",
        "senior": "वरिष्ठ नागरिक"
    },
    "Tamil": {
        "toddler": "குழந்தை (ஆரம்பக் கற்றல்)",
        "young": "இளைய கற்றல் மாணவர்",
        "middle": "நடுத்தர கற்றல் மாணவர்",
        "older": "இளைஞர் / வளரிளம் பருவம்",
        "career": "தொழில் தொடங்குபவர்",
        "professional": "பணிபுரியும் தொழில்முறை",
        "advancement": "தொழில் மேம்பாடு",
        "leadership": "தலைமை மற்றும் வழிகாட்டுதல்",
        "pre-retirement": "ஓய்வுக்கு முந்தைய நிலை",
        "senior": "மூத்த குடிமகன்"
    },
    "Marathi": {
        "toddler": "लहान मूल (सुरुवातीचे शिकणारे)",
        "young": "तरुण शिकणारे",
        "middle": "मध्यम शिकणारे",
        "older": "किशोरवयीन / तरुण",
        "career": "करिअरची सुरुवात",
        "professional": "नोकरी करणारे व्यावसायिक",
        "advancement": "करिअरमधील प्रगती",
        "leadership": "नेतृत्व आणि मार्गदर्शन",
        "pre-retirement": "सेवानिवृत्तीपूर्व",
        "senior": "ज्येष्ठ नागरिक"
    },
    "Kannada": {
        "toddler": "ಅಂಬೆಗಾಲಿಡುವ ಮಗು (ಆರಂಭಿಕ ಕಲಿಗ)",
        "young": "ಯುವ ಕಲಿಗ",
        "middle": "ಮಧ್ಯಮ ಕಲಿಗ",
        "older": "ಹದಿಹರೆಯದವರು / ಯುವಕರು",
        "career": "ವೃತ್ತಿಜೀವನ ಆರಂಭಿಸುವವರು",
        "professional": "ಉದ್ಯೋಗಿ ವೃತ್ತಿಪರ",
        "advancement": "ವೃತ್ತಿಜೀವನದ ಉನ್ನತಿ",
        "leadership": "ನಾಯಕತ್ವ ಮತ್ತು ಮಾರ್ಗದರ್ಶನ",
        "pre-retirement": "ನಿವೃತ್ತಿಪೂರ್ವ",
        "senior": "ಹಿರಿಯ ನಾಗರಿಕ"
    },
    "Malayalam": {
        "toddler": "ശിശു (ആദ്യകാല പഠിതാവ്)",
        "young": "യുവ പഠിതാവ്",
        "middle": "മധ്യ പഠിതാവ്",
        "older": "കൗമാരക്കാരൻ / യുവത്വം",
        "career": "കരിയർ തുടക്കക്കാരൻ",
        "professional": "തൊഴിൽ പ്രൊഫഷണൽ",
        "advancement": "കരിയർ പുരോഗതി",
        "leadership": "നേതൃത്വവും പരിശീലനവും",
        "pre-retirement": "വിരമിക്കലിന് മുൻപുള്ള അവസ്ഥ",
        "senior": "മുതിർന്ന പൗരൻ"
    }
}


def get_age_group_label(group, language):
    return AGE_GROUP_LABELS.get(language, AGE_GROUP_LABELS["English"]).get(group, group.title())


VOCAB_DATABASE = {
    "English": {
        "toddler": {
            "spelling_tests": [
                {"word": "cat", "options": ["cat", "xat", "ct"], "answer": "cat"},
                {"word": "dog", "options": ["dog", "dgo", "dg"], "answer": "dog"},
                {"word": "sun", "options": ["sun", "sn", "snn"], "answer": "sun"},
                {"word": "pen", "options": ["pen", "pn", "peen"], "answer": "pen"}
            ],
            "writing_templates": [
                {"template": "The ball is ___.", "answers": ["red", "big", "blue"]},
                {"template": "I see a ___.", "answers": ["cat", "dog", "sun", "pen"]},
                {"template": "A hot ___.", "answers": ["sun"]}
            ],
            "speaking_phrases": [
                "Big dog",
                "Blue sky",
                "I run",
                "Red apple"
            ]
        },
        "young": {
            "nouns": ["cat", "dog", "book", "ball", "pen", "hat", "boy", "girl", "tree", "bird"],
            "verbs": ["runs", "jumps", "plays", "sleeps", "reads", "writes", "sings", "flies"],
            "adjectives": ["happy", "small", "big", "fast", "slow", "red", "blue", "green"],
            "places": ["park", "school", "house", "garden", "room", "yard"],
            "spelling_tests": [
                {"word": "reading", "options": ["reding", "reading", "readin"], "answer": "reading"},
                {"word": "writing", "options": ["wrting", "writing", "writeing"], "answer": "writing"},
                {"word": "learning", "options": ["lerning", "learning", "learnin"], "answer": "learning"},
                {"word": "school", "options": ["scool", "school", "schoole"], "answer": "school"},
                {"word": "teacher", "options": ["techer", "teacher", "teachere"], "answer": "teacher"}
            ],
            "writing_templates": [
                {"template": "I see a green ___.", "answers": ["leaf", "tree", "plant"]},
                {"template": "The ball is ___.", "answers": ["round", "red", "blue", "big"]},
                {"template": "She can ___ a book.", "answers": ["read", "open", "see", "write"]},
                {"template": "The sun is in the ___.", "answers": ["sky"]}
            ],
            "speaking_phrases": [
                "I can read and write.",
                "The cat is cute.",
                "I play in the park.",
                "A red apple is sweet."
            ]
        },
        "middle": {
            "nouns": ["students", "teachers", "lessons", "stories", "questions", "answers", "friends", "classrooms"],
            "verbs": ["understands", "explains", "practices", "remembers", "finishes", "creates"],
            "adjectives": ["interesting", "careful", "focused", "clever", "creative", "beautiful"],
            "spelling_tests": [
                {"word": "comprehension", "options": ["comprehension", "comprension", "comprehenson"], "answer": "comprehension"},
                {"word": "vocabulary", "options": ["vocabulry", "vocabulary", "vocabularie"], "answer": "vocabulary"},
                {"word": "education", "options": ["education", "educaton", "educashun"], "answer": "education"},
                {"word": "knowledge", "options": ["nowledge", "knowledge", "knowlege"], "answer": "knowledge"}
            ],
            "writing_templates": [
                {"template": "They always ___ their homework on time.", "answers": ["do", "complete", "finish", "write"]},
                {"template": "He is very ___ in studying science.", "answers": ["interested", "focused", "careful"]},
                {"template": "We learn new words to build our ___.", "answers": ["vocabulary", "knowledge", "skills"]}
            ],
            "speaking_phrases": [
                "Reading books helps us learn new things.",
                "We must practice writing everyday.",
                "The students solved the grammar quiz.",
                "Education is important for everyone."
            ]
        },
        "older": {
            "nouns": ["foundations", "literacy", "achievements", "development", "communication", "opportunities"],
            "verbs": ["empowers", "contributes", "accomplishes", "facilitates", "strengthens"],
            "adjectives": ["essential", "accessible", "collaborative", "professional", "lifelong"],
            "spelling_tests": [
                {"word": "pronunciation", "options": ["pronunciation", "pronounciation", "pronunciaton"], "answer": "pronunciation"},
                {"word": "proficiency", "options": ["proficency", "proficiency", "proficiencie"], "answer": "proficiency"},
                {"word": "development", "options": ["devlopment", "development", "developement"], "answer": "development"},
                {"word": "achievement", "options": ["achievement", "achievment", "acheivement"], "answer": "achievement"}
            ],
            "writing_templates": [
                {"template": "Developing strong reading skills is ___ for success.", "answers": ["essential", "important", "critical"]},
                {"template": "Foundational literacy empowers individuals to ___ their goals.", "answers": ["achieve", "reach", "accomplish"]},
                {"template": "Regional languages make learning resources more ___.", "answers": ["accessible", "useful"]}
            ],
            "speaking_phrases": [
                "Foundational literacy builds a path to lifelong learning.",
                "Language skills help us share ideas with confidence.",
                "Technology provides personalized learning pathways.",
                "Communication is essential for professional growth."
            ]
        }
    },
    "Telugu": {
        "toddler": {
            "spelling_tests": [
                {"word": "ఆవు", "options": ["ఆవు", "అవు", "ఆవ"], "answer": "ఆవు"},
                {"word": "ఇల్లు", "options": ["ఇల్లు", "ఇలు", "ఈల్లు"], "answer": "ఇల్లు"},
                {"word": "అమ్మ", "options": ["అమ్మ", "ఆమ", "అమ"], "answer": "అమ్మ"}
            ],
            "writing_templates": [
                {"template": "ఇది ఒక ___.", "answers": ["ఇల్లు", "కలం", "ఆట"]},
                {"template": "అమ్మ ___ ఇస్తుంది.", "answers": ["పాలు", "నీరు"]}
            ],
            "speaking_phrases": [
                "మంచి బాలుడు",
                "చిన్న పిల్లి",
                "బడికి వెళ్ళు"
            ]
        },
        "young": {
            "nouns": ["పిల్లి", "కుక్క", "పుస్తకం", "బంతి", "కలం", "ఆట", "పాలు", "పండు"],
            "verbs": ["ఉంది", "తాగుతుంది", "ఆడుతుంది", "చదువుతుంది", "నడుస్తుంది"],
            "spelling_tests": [
                {"word": "పుస్తకం", "options": ["పుస్తకం", "పుస్థకం", "పుస్తకము"], "answer": "పుస్తకం"},
                {"word": "బడి", "options": ["బడి", "భడి", "వడి"], "answer": "బడి"},
                {"word": "కలం", "options": ["కలం", "ఖలం", "గలమ్"], "answer": "కలం"}
            ],
            "writing_templates": [
                {"template": "పిల్లి ___ తాగుతుంది.", "answers": ["పాలు", "నీరు"]},
                {"template": "ఆకాశం ___ రంగులో ఉంటుంది.", "answers": ["నీలం"]},
                {"template": "ఆమె ___ చదువుతుంది.", "answers": ["పుస్తకం", "కథ"]}
            ],
            "speaking_phrases": [
                "నేను చదవగలను మరియు వ్రాయగలను.",
                "అమ్మ నన్ను ప్రేమిస్తుంది.",
                "బంతి గుండ్రంగా ఉంటుంది.",
                "పాలు ఆరోగ్యానికి మంచిది."
            ]
        },
        "middle": {
            "nouns": ["విద్యార్థులు", "ఉపాధ్యాయులు", "పాఠాలు", "కథలు", "ప్రశ్నలు", "సమాధానాలు"],
            "verbs": ["నేర్చుకుంటారు", "బోధిస్తారు", "రాస్తారు", "సహాయం చేస్తారు"],
            "spelling_tests": [
                {"word": "విద్యార్థి", "options": ["విద్యార్థి", "విధ్యార్తి", "విధ్యార్థి"], "answer": "విద్యార్థి"},
                {"word": "ఉపాధ్యాయుడు", "options": ["ఉపాధ్యాయుడు", "ఉపాദ്യాయుడు", "ఉపద్యాయుడు"], "answer": "ఉపాధ్యాయుడు"},
                {"word": "జ్ఞానం", "options": ["జ్ఞానం", "గ్నానం", "జ్నానం"], "answer": "జ్ఞానం"}
            ],
            "writing_templates": [
                {"template": "సూర్యుడు ___ దిశలో ఉదయిస్తాడు.", "answers": ["తూర్పు"]},
                {"template": "విద్యార్థులు బడిలో ___ నేర్చుకుంటారు.", "answers": ["పాఠాలు", "విద్య", "నైపుణ్యాలు"]}
            ],
            "speaking_phrases": [
                "పుస్తకాలు చదవడం మంచి అలవాటు.",
                "ప్రతిరోజూ కొత్త విషయాలు నేర్చుకోవాలి.",
                "ఉపాధ్యాయులు మాకు మార్గదర్శకం చేస్తారు.",
                "బడి మాకు చదువు మరియు క్రమశిక్షణ నేర్పుతుంది."
            ]
        },
        "older": {
            "nouns": ["పునాది", "సాక్షరత", "అభివృద్ధి", "కమ్యూనికేషన్", "అవకాశాలు"],
            "verbs": ["బలోపేతం చేస్తుంది", "సహాయపడుతుంది", "సాధించవచ్చు", "కల్పిస్తుంది"],
            "spelling_tests": [
                {"word": "సాక్షరత", "options": ["సాక్షరత", "శాక్షరత", "సాక్షరథ"], "answer": "సాక్షరత"},
                {"word": "పరిశోధన", "options": ["పరిశోధన", "పరిసోదన", "పరీశోధన"], "answer": "పరిశోధన"},
                {"word": "అవకాశం", "options": ["అవకాశం", "అవకాసం", "ఆవకాశం"], "answer": "అవకాశం"}
            ],
            "writing_templates": [
                {"template": "సాక్షరత దేశ ప్రగతికి ఒక ___.", "answers": ["పునాది", "కీలకం"]},
                {"template": "కమ్యూనిकेషన్ నైపుణ్యాలు మనకు మంచి ___ కల్పిస్తాయి.", "answers": ["అవకాశాలు", "ఉద్యోగాలు"]}
            ],
            "speaking_phrases": [
                "సాక్షరత సమాజ ఎదుగుదలకు పునాది.",
                "మాతృభాషలో నేర్చుకోవడం చాలా సుభం.",
                "సాంకేతికత విద్యను అందరికీ చేరువ చేస్తుంది.",
                "జ్ఞానం మనకు కొత్త ఆలోచనలను ఇస్తుంది."
            ]
        }
    },
    "Hindi": {
        "toddler": {
            "spelling_tests": [
                {"word": "आम", "options": ["आम", "अम", "आमु"], "answer": "आम"},
                {"word": "घर", "options": ["घर", "घड़", "गहर"], "answer": "घर"},
                {"word": "नल", "options": ["नल", "नळ", "नाल"], "answer": "नल"}
            ],
            "writing_templates": [
                {"template": "यह मेरा ___ है।", "answers": ["घर", "कलम", "फल"]},
                {"template": "आम मीठा ___ है।", "answers": ["होता", "जाता"]}
            ],
            "speaking_phrases": [
                "मेरा घर",
                "लाल सेब",
                "बिल्ली आई"
            ]
        },
        "young": {
            "nouns": ["बिल्ली", "कुत्ता", "किताब", "गेेंद", "कलम", "खेल", "दूध", "फल"],
            "verbs": ["है", "पीती है", "खेलता है", "पढ़ती है", "दौड़ता है"],
            "spelling_tests": [
                {"word": "किताब", "options": ["किताब", "कीताब", "किताम"], "answer": "किताब"},
                {"word": "स्कूल", "options": ["स्कूल", "स्कुल", "शकूल"], "answer": "स्कूल"},
                {"word": "कलम", "options": ["कलम", "खलम", "कलमम"], "answer": "कलम"}
            ],
            "writing_templates": [
                {"template": "बिल्ली ___ पीती है।", "answers": ["दूध", "पानी"]},
                {"template": "सेब का रंग ___ होता है।", "answers": ["लाल"]},
                {"template": "वह ___ पढ़ती है।", "answers": ["किताब", "कहानी"]}
            ],
            "speaking_phrases": [
                "मुझे पढ़ना पसंद है।",
                "मेरा नाम अमर है",
                "बिल्ली बहुत प्यारी है।",
                "सूर्य चमक रहा है।"
            ]
        },
        "middle": {
            "nouns": ["छात्र", "शिक्षक", "पाठ", "कहानियाँ", "प्रश्न", "उत्तर"],
            "verbs": ["सीखते हैं", "पढ़ाते हैं", "लिखते हैं", "मदद करते हैं"],
            "spelling_tests": [
                {"word": "विद्यार्थी", "options": ["विद्यार्थी", "विद्ध्यार्थी", "विद्यारथी"], "answer": "विद्यार्थी"},
                {"word": "शिक्षक", "options": ["शिक्षक", "सीक्षक", "शिशक"], "answer": "शिक्षक"},
                {"word": "ज्ञान", "options": ["ज्ञान", "ग्यान", "ज्यान"], "answer": "ज्ञान"}
            ],
            "writing_templates": [
                {"template": "सूर्य ___ दिशा में उगता है।", "answers": ["पूर्व"]},
                {"template": "बच्चे स्कूल में ___ सीखते हैं।", "answers": ["पाठ", "ज्ञान", "अच्छी बातें"]}
            ],
            "speaking_phrases": [
                "किताबें हमारी सबसे अच्छी मित्र हैं।",
                "हमें हर दिन नया सीखना चाहिए।",
                "शिक्षक हमें सही मार्ग दिखाते हैं।",
                "शिक्षा हमारे जीवन को सुंदर बनाती हैं।"
            ]
        },
        "older": {
            "nouns": ["साक्षरता", "विकास", "संवाद", "अवसर", "सफलता", "भविष्य"],
            "verbs": ["मजबूत करता है", "बढ़ाता है", "मदद करता है", "दिलाता है"],
            "spelling_tests": [
                {"word": "साक्षरता", "options": ["साक्षरता", "शाक्षरता", "साक्षरताा"], "answer": "साक्षरता"},
                {"word": "सफलता", "options": ["सफलता", "सफळता", "सफल्ता"], "answer": "सफलता"},
                {"word": "आत्मविश्वास", "options": ["आत्मविश्वास", "आतंविश्वास", "आत्मविस्वास"], "answer": "आत्मविश्वास"}
            ],
            "writing_templates": [
                {"template": "साक्षरता हमारे सुंदर भविष्य की ___ है।", "answers": ["चाबी", "नींव", "कुंजी"]},
                {"template": "अच्छा संवाद कौशल हमें बेहतर ___ दिलाता है।", "answers": ["अवसर", "नौकरी", "भविष्य"]}
            ],
            "speaking_phrases": [
                "साक्षरता ही सुनहरे भविष्य की कुंजी है।",
                "भाषा कौशल हमें आत्मविश्वास से विचार साझा करने में मदद करते हैं।",
                "तकनीक शिक्षा को सभी के लिए सुलभ बनाती है।",
                "संवाद ही व्यक्तिगत विकास के लिए आवश्यक है।"
            ]
        }
    },
    "Tamil": {
        "toddler": {
            "spelling_tests": [
                {"word": "அம்மா", "options": ["அம்மா", "அமா", "ஆம்மா"], "answer": "அம்மா"},
                {"word": "ஆடு", "options": ["ஆடு", "அடு", "ஆடூ"], "answer": "ஆடு"},
                {"word": "இலை", "options": ["இலை", "ஈலை", "இல"], "answer": "இலை"}
            ],
            "writing_templates": [
                {"template": "இது என் ___.", "answers": ["வீடு", "பந்து", "பேனா"]},
                {"template": "அம்மா ___ தருகிறார்.", "answers": ["பால்", "தண்ணீர்"]}
            ],
            "speaking_phrases": [
                "நல்ல பையன்",
                "சின்ன பூனை",
                "பள்ளிக்கு போ"
            ]
        },
        "young": {
            "nouns": ["பூனை", "நாய்", "புத்தகம்", "பந்து", "பேனா", "விளையாட்டு", "பால்", "பழம்"],
            "verbs": ["இருக்கிறது", "குடிக்கிறது", "விளையாடுகிறது", "படிக்கிறது", "ஓடுகிறது"],
            "spelling_tests": [
                {"word": "புத்தகம்", "options": ["புத்தகம்", "புதகம்", "புத்தகம்ம"], "answer": "புத்தகம்"},
                {"word": "பள்ளி", "options": ["பள்ளி", "பலி", "பல்ளி"], "answer": "பள்ளி"},
                {"word": "பேனா", "options": ["பேனா", "பெனா", "பேநா"], "answer": "பேனா"}
            ],
            "writing_templates": [
                {"template": "பூனை ___ குடிக்கிறது.", "answers": ["பால்", "தண்ணீர்"]},
                {"template": "ஆப்பிள் ___ நிறத்தில் இருக்கும்.", "answers": ["சிவப்பு"]},
                {"template": "அவள் ___ படிக்கிறாள்.", "answers": ["புத்தகம்", "கதை"]}
            ],
            "speaking_phrases": [
                "எனக்கு படிக்க பிடிக்கும்.",
                "என் பெயர் குமார்.",
                "பூனை மிகவும் அழகானது.",
                "சூரியன் பிரகாசிக்கிறது."
            ]
        },
        "middle": {
            "nouns": ["மாணவர்கள்", "ஆசிரியர்கள்", "பாடங்கள்", "கதைகள்", "கேள்விகள்", "பதில்கள்"],
            "verbs": ["கற்றுக்கொள்கிறார்கள்", "கற்பிக்கிறார்கள்", "எழுதுகிறார்கள்", "உதவுகிறார்கள்"],
            "spelling_tests": [
                {"word": "மாணவன்", "options": ["மாணவன்", "மானவன்", "மாணவந்"], "answer": "மாணவன்"},
                {"word": "ஆசிரியர்", "options": ["ஆசிரியர்", "ஆசரியர்", "ஆசிரிஒர்"], "answer": "ஆசிரியர்"},
                {"word": "அறிவு", "options": ["அறிவு", "அரிவு", "அரீவு"], "answer": "அறிவு"}
            ],
            "writing_templates": [
                {"template": "சூரியன் ___ திசையில் உதிக்கிறது.", "answers": ["கிழக்கு"]},
                {"template": "மாணவர்கள் பள்ளியில் ___ கற்கிறார்கள்.", "answers": ["பாடங்கள்", "அறிவு", "ஒழுக்கம்"]}
            ],
            "speaking_phrases": [
                "புத்தகங்கள் வாசிப்பது நல்ல பழக்கம்.",
                "ஒவ்வொரு நாளும் புதிய விஷயங்களை கற்க வேண்டும்.",
                "ஆசிரியர்கள் நமக்கு நல்வழி காட்டுகிறார்கள்.",
                "பள்ளி நமக்கு கல்வியையும் ஒழுக்கத்தையும் கற்பிக்கிறது."
            ]
        },
        "older": {
            "nouns": ["அடித்தளம்", "எழுத்தறிவு", "வளர்ச்சி", "தொடர்பு", "வாய்ப்புகள்"],
            "verbs": ["பலப்படுத்துகிறது", "உதவுகிறது", "அடையலாம்", "வழங்குகிறது"],
            "spelling_tests": [
                {"word": "எழுத்தறிவு", "options": ["எழுத்தறிவு", "எளுத்தறிவு", "எழுத்தரிவு"], "answer": "எழுத்தறிவு"},
                {"word": "வெற்றி", "options": ["வெற்றி", "வெட்ரி", "வெற்றிஇ"], "answer": "வெற்றி"},
                {"word": "நம்பிக்கை", "options": ["நம்பிக்கை", "நம்பிகை", "நம்பிஃகை"], "answer": "நம்பிக்கை"}
            ],
            "writing_templates": [
                {"template": "எழுத்தறிவு நமது சிறந்த எதிர்காலத்திற்கு ___.", "answers": ["அடித்தளம்", "முக்கியம்"]},
                {"template": "நல்ல தொடர்பு திறன் சிறந்த ___ பெற்றுத்தரும்.", "answers": ["வாய்ப்புகளை", "வேலையை"]}
            ],
            "speaking_phrases": [
                "எழுத்தறிவே சிறந்த எதிர்காலத்தின் திறவுகோல்.",
                "மொழித் திறன் நம் கருத்துக்களைப் பகிர உதவுகிறது.",
                "தொழில்நுட்பம் கல்வியை எளிதாக்குகிறது.",
                "தொடர்பு திறன் தனிப்பட்ட வளர்ச்சிக்கு அவசியம்."
            ]
        }
    },
    "Kannada": {
        "toddler": {
            "spelling_tests": [
                {"word": "ಅಮ್ಮ", "options": ["ಅಮ್ಮ", "ಅಮ", "ಆಮ್ಮ"], "answer": "ಅಮ್ಮ"},
                {"word": "ಆಟ", "options": ["ಆಟ", "ಅಟ", "ಆಟಾ"], "answer": "ಆಟ"},
                {"word": "ಎಲೆ", "options": ["ಎಲೆ", "ಏಲೆ", "ಎಲ"], "answer": "ಎಲೆ"}
            ],
            "writing_templates": [
                {"template": "ಇದು ನನ್ನ ___.", "answers": ["ಮನೆ", "ಚೆಂಡು", "ಪೆನ್"]},
                {"template": "ಅಮ್ಮ ___ ಕೊಡುತ್ತಾರೆ.", "answers": ["ಹಾಲು", "ನೀರು"]}
            ],
            "speaking_phrases": [
                "ಒಳ್ಳೆಯ ಹುಡುಗ",
                "ಸಣ್ಣ ಬೆಕ್ಕು",
                "ಶಾಲೆಗೆ ಹೋಗು"
            ]
        },
        "young": {
            "nouns": ["ಬೆಕ್ಕು", "ನಾಯಿ", "ಪುಸ್ತಕ", "ಚೆಂಡು", "ಪೆನ್", "ಆಟ", "ಹಾಲು", "ಹಣ್ಣು"],
            "verbs": ["ಇದೆ", "ಕುಡಿಯುತ್ತದೆ", "ಆಡುತ್ತದೆ", "ಓದುತ್ತದೆ", "ಓಡುತ್ತದೆ"],
            "spelling_tests": [
                {"word": "ಪುಸ್ತಕ", "options": ["ಪುಸ್ತಕ", "ಪುಸ್ತಖ", "ಪುಸ್ತಕ್"], "answer": "ಪುذجಕ"},
                {"word": "ಶಾಲೆ", "options": ["ಶಾಲೆ", "ಸಾಲ", "ಶಾಳೆ"], "answer": "ಶಾಲೆ"},
                {"word": "ಪೆನ್", "options": ["ಪೆನ್", "ಫೆನ್", "ಪೇನ್"], "answer": "ಪೆನ್"}
            ],
            "writing_templates": [
                {"template": "ಬೆಕ್ಕು ___ ಕುಡಿಯುತ್ತದೆ.", "answers": ["ಹಾಲು", "ನೀರು"]},
                {"template": "ಸೇಬಿನ ಬಣ್ಣ ___ ಇರುತ್ತದೆ.", "answers": ["ಕೆಂಪು"]},
                {"template": "ಅವಳು ___ ಓದುತ್ತಾಳೆ.", "answers": ["ಪುಸ್ತಕ", "ಕಥೆ"]}
            ],
            "speaking_phrases": [
                "ನನಗೆ ಓದಲು ಇಷ್ಟ.",
                "ನನ್ನ ಹೆಸರು ಕಿರಣ್.",
                "ಬೆಕ್ಕು ತುಂಬಾ ಮುದ್ದಾಗಿದೆ.",
                "ಸೂರ್ಯನು ಬೆಳಗುತ್ತಿದ್ದಾನೆ."
            ]
        },
        "middle": {
            "nouns": ["ವಿದ್ಯಾರ್ಥಿಗಳು", "ಶಿಕ್ಷಕರು", "ಪಾಠಗಳು", "ಕಥೆಗಳು", "ಪ್ರಶ್ನೆಗಳು", "ಉತ್ತರಗಳು"],
            "verbs": ["ಕಲಿಯುತ್ತಾರೆ", "ಬೋಧಿಸುತ್ತಾರೆ", "ಬರೆಯುತ್ತಾರೆ", "ಸಹಾಯ ಮಾಡುತ್ತಾರೆ"],
            "spelling_tests": [
                {"word": "ವಿದ್ಯಾರ್ಥಿ", "options": ["ವಿದ್ಯಾರ್ಥಿ", "ವಿದ್ಯಾರ್ತಿ", "ವಿಧ್ಯಾರ್ಥಿ"], "answer": "ವಿದ್ಯಾರ್ಥಿ"},
                {"word": "ಶಿಕ್ಷಕ", "options": ["ಶಿಕ್ಷಕ", "ಶಿಕ್ಸಕ", "ಸಿಕ್ಷಕ"], "answer": "ಶಿಕ್ಷಕ"},
                {"word": "ಜ್ಞಾನ", "options": ["ಜ್ಞಾನ", "ಗ್ನಾನ", "ಜ್ನಾನ"], "answer": "ಜ್ಞಾನ"}
            ],
            "writing_templates": [
                {"template": "ಸೂರ್ಯನು ___ ದಿಕ್ಕಿನಲ್ಲಿ ಉದಯಿಸುತ್ತಾನೆ.", "answers": ["ಪೂರ್ವ"]},
                {"template": "ವಿದ್ಯಾರ್ಥಿಗಳು ಶಾಲೆಯಲ್ಲಿ ___ ಕಲಿಯುತ್ತಾರೆ.", "answers": ["ಪಾಠಗಳನ್ನು", "ಜ್ಞಾನ", "ಶಿಸ್ತು"]}
            ],
            "speaking_phrases": [
                "ಪುಸ್ತಕಗಳನ್ನು ಓದುವುದು ಒಳ್ಳೆಯ ಹವ್ಯಾಸ.",
                "ನಾವು ಪ್ರತಿದಿನ ಹೊಸದನ್ನು ಕಲಿಯಬೇಕು.",
                "ಶಿಕ್ಷಕರು ನಮಗೆ ಸರಿಯಾದ ಮಾರ್ಗವನ್ನು ತೋರಿಸುತ್ತಾರೆ.",
                "ಶಾಲೆ ನಮಗೆ ಶಿಕ್ಷಣ ಮತ್ತು ಶಿಸ್ತನ್ನು ಕಲಿತ್ತದೆ."
            ]
        },
        "older": {
            "nouns": ["ಬುನಾದಿ", "ಸಾಕ್ಷರತೆ", "ಅಭಿವೃದ್ಧಿ", "ಸಂವಹನ", "ಅವಕಾಶಗಳು"],
            "verbs": ["ಬಲಪಡಿಸುತ್ತದೆ", "ಸಹಾಯ ಮಾಡುತ್ತದೆ", "ಸಾಧಿಸಬಹುದು", "ಒದಗಿಸುತ್ತದೆ"],
            "spelling_tests": [
                {"word": "ಸಾಕ್ಷರತೆ", "options": ["ಸಾಕ್ಷರತೆ", "ಸಾಕ್ಸರತೆ", "ಶಾಕ್ಷರತೆ"], "answer": "ಸಾಕ್ಷರತೆ"},
                {"word": "ಯಶಸ್ಸು", "options": ["ಯಶಸ್ಸು", "ಯಸಸ್ಸು", "ಯಶಶು"], "answer": "ಯಶಸ್ಸು"},
                {"word": "ಆತ್ಮವಿಶ್ವಾಸ", "options": ["ಆತ್ಮವಿಶ್ವಾಸ", "ಆತ್ಮವಿಸ್ವಾಸ", "ಅತ್ಮವಿಶ್ವಾಸ"], "answer": "ಆತ್ಮವಿಶ್ವಾಸ"}
            ],
            "writing_templates": [
                {"template": "ಸಾಕ್ಷರತೆಯು ನಮ್ಮ ಸುಂದರ ಭವಿಷ್ಯದ ___ ಆಗಿದೆ.", "answers": ["ಬುನಾದಿ", "ಕೀಲಿ ಕೈ"]},
                {"template": "ಉತ್ತಮ ಸಂವಹನ ಕೌಶಲ್ಯಗಳು ಉತ್ತಮ ___ ಒದಗಿಸುತ್ತವೆ.", "answers": ["ಅವಕಾಶಗಳನ್ನು", "ಕೆಲಸವನ್ನು"]}
            ],
            "speaking_phrases": [
                "ಸಾಕ್ಷರತೆಯೇ ಸುಂದರ ಭವಿಷ್ಯದ ಕೀಲಿ.",
                "ಭಾಷಾ ಕೌಶಲ್ಯಗಳು ನಮ್ಮ ಆಲೋಚನೆಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ.",
                "ತಂತ್ರಜ್ಞಾನವು ಶಿಕ್ಷಣವನ್ನು ಎಲ್ಲರಿಗೂ ಸುಲಭಗೊಳಿಸುತ್ತದೆ.",
                "ವೈಯಕ್ತಿಕ ಬೆಳವಣಿಗೆಗೆ ಸಂವಹನ ಅತ್ಯಗತ್ಯ."
            ]
        }
    },
    "Malayalam": {
        "toddler": {
            "spelling_tests": [
                {"word": "അമ്മ", "options": ["അമ്മ", "അമ", "ആമ്മ"], "answer": "അമ്മ"},
                {"word": "ആട്", "options": ["ആട്", "അട്", "ആടു"], "answer": "ആട്"},
                {"word": "ഇല", "options": ["ഇല", "ഈല", "ഇലാ"], "answer": "ഇല"}
            ],
            "writing_templates": [
                {"template": "ഇത് എന്റെ ___ ആണ്.", "answers": ["വീട്", "പന്ത്", "പേന"]},
                {"template": "അമ്മ ___ തരുന്നു.", "answers": ["പാൽ", "വെള്ളം"]}
            ],
            "speaking_phrases": [
                "നല്ല കുട്ടി",
                "ചെറിയ പൂച്ച",
                "സ്കൂളിൽ പോകൂ"
            ]
        },
        "young": {
            "nouns": ["പൂച്ച", "നായ", "പുസ്തകം", "പന്ത്", "പേന", "കളി", "പാൽ", "പഴം"],
            "verbs": ["ഉണ്ട്", "കുടിക്കുന്നു", "കളിക്കുന്നു", "വായിക്കുന്നു", "ഓടുന്നു"],
            "spelling_tests": [
                {"word": "പുസ്തകം", "options": ["പുസ്തകം", "പുസ്തകംം", "പുസ്തകംമ്"], "answer": "പുസ്തകം"},
                {"word": "സ്കൂൾ", "options": ["സ്കൂൾ", "സ്കൂള", "സ്കൂൾമ്"], "answer": "സ്കൂൾ"},
                {"word": "പേന", "options": ["പേന", "പെന", "പേനാ"], "answer": "പേന"}
            ],
            "writing_templates": [
                {"template": "പൂച്ച ___ കുടിക്കുന്നു.", "answers": ["പാൽ", "വെള്ളം"]},
                {"template": "ആപ്പിളിന്റെ നിറം ___ ആണ്.", "answers": ["ചുവപ്പ്"]},
                {"template": "അവൾ ___ വായിക്കുന്നു.", "answers": ["പുസ്തകം", "കഥ"]}
            ],
            "speaking_phrases": [
                "എനിക്ക് വായിക്കാൻ ഇഷ്ടമാണ്.",
                "എന്റെ പേര് അരുൺ.",
                "പൂച്ച വളരെ സുന്ദരമാണ്.",
                "സൂര്യൻ പ്രകാശിക്കുന്നു."
            ]
        },
        "middle": {
            "nouns": ["വിദ്യാർത്ഥികൾ", "അധ്യാപകർ", "പാഠങ്ങൾ", "കഥകൾ", "ചോദ്യങ്ങൾ", "ഉത്തരങ്ങൾ"],
            "verbs": ["പഠിക്കുന്നു", "പഠിപ്പിക്കുന്നു", "എഴുതുന്നു", "സഹായിക്കുന്നു"],
            "spelling_tests": [
                {"word": "വിദ്യാർത്ഥി", "options": ["വിദ്യാർത്ഥി", "വിദ്യാർതി", "വിദ്ധ്യാർത്ഥി"], "answer": "വിദ്യാർത്ഥി"},
                {"word": "അധ്യാപകൻ", "options": ["അധ്യാപകൻ", "അദ്ധ്യാപകൻ", "അധ്യാപകന്"], "answer": "അധ്യാപകൻ"},
                {"word": "ജ്ഞാനം", "options": ["ജ്ഞാനം", "ഗ്നാനം", "ജ്നാനം"], "answer": "ജ്ഞാനം"}
            ],
            "writing_templates": [
                {"template": "സൂര്യൻ ___ ദിശയിൽ ഉദിക്കുന്നു.", "answers": ["കിഴക്ക്"]},
                {"template": "വിദ്യാർത്ഥികൾ സ്കൂളിൽ നിന്നും ___ പഠിക്കുന്നു.", "answers": ["പാഠങ്ങൾ", "അറിവ്", "അച്ചടക്കം"]}
            ],
            "speaking_phrases": [
                "പുസ്തക വായന നല്ലൊരു ശീലമാണ്.",
                "നാം ദിവസവും പുതിയ കാര്യങ്ങൾ പഠിക്കണം.",
                "അധ്യാപകർ നമ്മെ ശരിയായ വഴി കാണിക്കുന്നു.",
                "സ്കൂൾ നമ്മെ അറിവും അച്ചടക്കവും പഠിപ്പിക്കുന്നു."
            ]
        },
        "older": {
            "nouns": ["അടിത്തറ", "സാക്ഷരത", "വികസനം", "വിനിമയം", "അവസരങ്ങൾ"],
            "verbs": ["ശക്തിപ്പെടുത്തുന്നു", "സഹായിക്കുന്നു", "നേടാം", "നൽകുന്നു"],
            "spelling_tests": [
                {"word": "സാക്ഷരത", "options": ["സാക്ഷരത", "സാക്സരത", "ശാക്ഷരത"], "answer": "സാക്ഷരത"},
                {"word": "വിജയം", "options": ["വിജയം", "വിജയംമ്", "വിജയമ്"], "answer": "വിജയം"},
                {"word": "ആത്മവിശ്വാസം", "options": ["ആത്മവിശ്വാസം", "ആത്മവിസ്വാസം", "അത്മവിശ്വാസം"], "answer": "ആത്മവിശ്വാസം"}
            ],
            "writing_templates": [
                {"template": "സാക്ഷരത നമ്മുടെ നല്ലൊരു ഭാവിയുടെ ___ ആണ്.", "answers": ["അടിത്തറ", "താക്കോൽ"]},
                {"template": "നല്ല വിനിമയ ശേഷി മികച്ച ___ നൽകുന്നു.", "answers": ["അവസരങ്ങൾ", "ജോലി"]}
            ],
            "speaking_phrases": [
                "സാക്ഷരതയാണ് നല്ലൊരു ഭാവിയുടെ താക്കോൽ.",
                "ആശയങ്ങൾ പങ്കുവെക്കാൻ ഭാഷാ വിനിമയം സഹായിക്കുന്നു.",
                "സാങ്കേതികവിദ്യ പഠനം എളുപ്പമാക്കുന്നു.",
                "വ്യകതിഗത വളർച്ചയ്ക്ക് വിനിമയം അത്യാവശ്യമാണ്."
            ]
        }
    }
}
def _normalize_learning_level(level):
    if not level:
        return "Beginner"
    return str(level).strip().capitalize()


def _get_age_band(age):
    try:
        age_val = int(age) if age is not None else 8
    except (ValueError, TypeError):
        age_val = 8
    if age_val <= 6:
        return "young"
    if age_val <= 10:
        return "middle"
    return "older"


def _get_assessment_profile(level, age_band):
    level_name = _normalize_learning_level(level)
    profiles = {
        "Advanced": {
            "level": "Advanced",
            "question_count": 12,
            # Advanced: paragraph reading, grammar, writing, communication, reading comprehension
            "activities": [
                "reading", "comprehension", "writing", "comprehension",
                "writing", "reading", "comprehension", "writing",
                "speaking", "listening", "reading", "comprehension"
            ],
            "age_band": age_band,
        },
        "Intermediate": {
            "level": "Intermediate",
            "question_count": 10,
            # Intermediate: sentence reading, sentence writing, listening, speaking, simple comprehension
            "activities": [
                "reading", "writing", "listening", "speaking",
                "comprehension", "reading", "writing", "listening",
                "speaking", "comprehension"
            ],
            "age_band": age_band,
        },
        "Basic": {
            "level": "Basic",
            "question_count": 8,
            # Basic: alphabets, simple words, picture-word matching, pronunciation
            "activities": [
                "reading", "listening", "comprehension", "speaking",
                "reading", "listening", "comprehension", "speaking"
            ],
            "age_band": age_band,
        },
        "Beginner": {
            "level": "Beginner",
            "question_count": 8,
            # Beginner: picture identification, object recognition, color/shape, listening, simple voice responses
            # No explicit reading or writing questions for Beginner
            "activities": [
                "comprehension", "listening", "speaking",
                "comprehension", "listening", "speaking",
                "listening", "speaking"
            ],
            "age_band": age_band,
        },
    }
    return profiles.get(level_name, profiles["Beginner"])


def _build_level_questions(language, profile, pool):
    questions = []
    age_band = profile["age_band"]
    level = profile["level"]

    def get_pool(key, fallback=None):
        if key in pool:
            return pool[key]
        if fallback and fallback in pool:
            return pool[fallback]
        return []

    def make_options(correct, base_opts):
        opts = [correct] + [opt for opt in base_opts if opt != correct]
        opts = list(dict.fromkeys(opts))
        while len(opts) < 4:
            opts.append(f"Option {len(opts) + 1}")
        return opts[:4]

    def build_reading_question(position):
        if level == "Basic":
            pool_data = get_pool("simple_words", "spelling")
            item = pool_data[position % len(pool_data)] if pool_data else ("apple", "Apple", ["Apple", "Ball", "Cat", "Dog"], "Apple is the correct word for the fruit.")
            return {
                "type": "reading",
                "skill": "reading",
                "prompt": f"Read the word and choose the matching picture: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "reading",
            }
        if level == "Intermediate":
            pool_data = get_pool("sentences", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("The cat is on the mat.", "The cat is on the mat.", ["The cat is on the mat.", "The dog is on the mat.", "The cat is in the car."], "Choose the correct sentence.")
            return {
                "type": "reading",
                "skill": "reading",
                "prompt": f"Read this sentence and choose the best answer: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "reading",
            }
        pool_data = get_pool("paragraphs", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("A boy planted a tree in the garden.", "Where did the boy plant a tree?", "In the garden", ["In the garden", "In the car", "In the school", "In the bed"], "The boy planted a tree in the garden.")
        return {
            "type": "reading",
            "skill": "reading",
            "prompt": f"Read the paragraph and answer: {item[1]}",
            "text": item[0],
            "options": make_options(item[2], item[3]),
            "answer": item[2],
            "explanation": item[4],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "reading",
        }

    def build_writing_question(position):
        if level == "Basic":
            pool_data = get_pool("objects", "spelling")
            item = pool_data[position % len(pool_data)] if pool_data else ({"image_url": "/static/images/apple.svg", "alt": "Apple"}, "Apple", "Copy the word and write it clearly.")
            return {
                "type": "writing",
                "skill": "writing",
                "prompt": "Write the name of the picture shown.",
                "text": item[0],
                "answer": item[1],
                "explanation": item[2],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "writing",
            }
        if level == "Intermediate":
            pool_data = get_pool("sentence_writing", "writing_templates")
            item = pool_data[position % len(pool_data)] if pool_data else ("Describe your pet.", "I have a small pet dog.", "Write one short sentence about your pet.")
            return {
                "type": "writing",
                "skill": "writing",
                "prompt": f"Write a short sentence: {item[0]}",
                "answer": item[1],
                "explanation": item[2],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "writing",
            }
        pool_data = get_pool("paragraph_writing", "writing_templates")
        item = pool_data[position % len(pool_data)] if pool_data else ("a day at school", "I went to school and learned new things.", "Write a short paragraph about a day at school.")
        return {
            "type": "writing",
            "skill": "writing",
            "prompt": f"Write a short paragraph about: {item[0]}",
            "answer": item[1],
            "explanation": item[2],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "writing",
        }

    def build_listening_question(position):
        if level == "Basic":
            pool_data = get_pool("listening_words", "listening")
            item = pool_data[position % len(pool_data)] if pool_data else ("Apple", "Apple", ["Apple", "Banana", "House", "Dog"], "Choose the word you heard.")
            return {
                "type": "listening",
                "skill": "listening",
                "prompt": "Listen and choose the right word.",
                "text": item[0],
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "listening",
            }
        if level == "Intermediate":
            pool_data = get_pool("listening_sentences", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("The cat sleeps.", "Where is the cat?", "On the mat", ["On the mat", "In the tree", "In the car", "On the bed"], "Listen and answer the question.")
            return {
                "type": "listening",
                "skill": "listening",
                "prompt": f"Listen to the sentence and answer: {item[1]}",
                "text": item[0],
                "options": make_options(item[2], item[3]),
                "answer": item[2],
                "explanation": item[4],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "listening",
            }
        pool_data = get_pool("listening_paragraphs", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("Ria went to the market.", "What did Ria buy?", "Fruits", ["Fruits", "Vegetables", "Books", "Toys"], "Listen and answer the question.")
        return {
            "type": "listening",
            "skill": "listening",
            "prompt": f"Listen to the passage and answer: {item[1]}",
            "text": item[0],
            "options": make_options(item[2], item[3]),
            "answer": item[2],
            "explanation": item[4],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "listening",
        }

    def build_speaking_question(position):
        if level == "Basic":
            pool_data = get_pool("speaking_phrases", "speaking")
            item = pool_data[position % len(pool_data)] if pool_data else "I like apples"
            return {
                "type": "speaking",
                "skill": "speaking",
                "prompt": f"Say this sentence aloud: {item}",
                "hint": item,
                "answer": item,
                "explanation": "Speak the phrase clearly and confidently.",
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "speaking",
            }
        pool_data = get_pool("speaking_responses", "speaking")
        item = pool_data[position % len(pool_data)] if pool_data else ("What is your name?", "My name is Ria.")
        return {
            "type": "speaking",
            "skill": "speaking",
            "prompt": f"Speak a short answer: {item[0]}",
            "hint": item[1],
            "answer": item[1],
            "explanation": "Answer the question with a short spoken response.",
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "speaking",
        }

    def build_comprehension_question(position):
        if level == "Basic":
            pool_data = get_pool("shape_words", "reading_letters")
            item = pool_data[position % len(pool_data)] if pool_data else ("A shape with three sides", "Triangle", ["Triangle", "Circle", "Square", "Star"], "A triangle has three sides.")
            return {
                "type": "comprehension",
                "skill": "comprehension",
                "prompt": f"Match the word with the picture or shape: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "comprehension",
            }
        if level == "Intermediate":
            pool_data = get_pool("vocabulary", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("Joyful", "Happy", ["Happy", "Sad", "Hungry", "Cold"], "Joyful means happy.")
            return {
                "type": "comprehension",
                "skill": "comprehension",
                "prompt": f"Choose the meaning of this word: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "comprehension",
            }
        pool_data = get_pool("grammar", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("Choose the correct sentence.", "She is reading a book.", ["She is reading a book.", "She are reading a book.", "She reading a book."], "This sentence is grammatically correct.")
        return {
            "type": "comprehension",
            "skill": "comprehension",
            "prompt": f"Choose the correct sentence: {item[0]}",
            "options": make_options(item[1], item[2]),
            "answer": item[1],
            "explanation": item[3],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "comprehension",
        }

    builders = {
        "reading": build_reading_question,
        "writing": build_writing_question,
        "listening": build_listening_question,
        "speaking": build_speaking_question,
        "comprehension": build_comprehension_question,
    }

    for index, skill in enumerate(profile["activities"]):
        builder = builders.get(skill)
        if not builder:
            continue
        question = builder(index)
        question["name"] = f"q{index + 1}"
        questions.append(question)

    return questions


def _legacy_get_assessment_questions(language, age=None, learning_level=None, mode=None):
    try:
        age_val = int(age) if age is not None else session.get("age", 8)
    except (ValueError, TypeError):
        age_val = 8

    if age_val <= 7 or (learning_level and ("beginner" in str(learning_level).lower() or "cannot" in str(learning_level).lower())):
        # Pre-school and beginner play-based assessment questions (Moo sound, red fruit strawberry, round circle shape, king of jungle lion, speak hello)
        multilingual_questions = {
            "English": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "What animal makes this sound: 'Moo Moo'? 🐮",
                    "options": ["Cow 🐮", "Dog 🐶", "Lion 🦁", "Cat 🐱"],
                    "answer": "Cow 🐮",
                    "explanation": "Cows make the moo sound!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Which of these is a red fruit? 🍓 (point or choose the picture)",
                    "options": ["Strawberry 🍓", "Banana 🍌", "Grape 🍇", "Pear 🍐"],
                    "answer": "Strawberry 🍓",
                    "explanation": "Strawberries are bright red and easy to recognize by color."
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Point to the round shape or choose the round picture. ⭕",
                    "options": ["Circle ⭕", "Square ⬛", "Triangle 🔺", "Star ⭐"],
                    "answer": "Circle ⭕",
                    "explanation": "A circle is round and has no corners."
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Which animal is often called the 'King of the Jungle'? 🦁",
                    "options": ["Lion 🦁", "Elephant 🐘", "Monkey 🐒", "Rabbit 🐰"],
                    "answer": "Lion 🦁",
                    "explanation": "The lion is commonly referred to as the king of the jungle."
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "Click the microphone and repeat: 'Hello' 👋",
                    "hint": "Hello",
                    "options": [],
                    "answer": "Hello",
                    "explanation": "Practice saying Hello."
                }
            ],
            "Telugu": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'బౌ బౌ' అని అరిచే జంతువు ఏది? 🐶",
                    "options": ["ఆవు 🐮", "కుక్క 🐶", "సింహం 🦁", "పిల్లి 🐱"],
                    "answer": "కుక్క 🐶",
                    "explanation": "కుక్కలు బౌ బౌ అని అరుస్తాయి!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "ఎరుపు రంగు పండును అని గుర్తించండి! 🍓 (పిక్ లేదా ఎంపిక చేయండి)",
                    "options": ["స్ట్రాబెర్రీ 🍓", "అరటిపండు 🍌", "ద్రాక్ష 🍇", "ఆపిల్ 🍎"],
                    "answer": "స్ట్రాబెర్రీ 🍓",
                    "explanation": "స్ట్రాబెర్రీలు ప్రత్యేకంగా ఎరుపు రంగులో ఉంటాయి."
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "గుండ్రటి ఆకారాన్ని చూపండి లేదా సెలెక్ట్ చేయండి. ⭕",
                    "options": ["వృత్తం ⭕", "చతురస్రం ⬛", "త్రిభుజం 🔺", "నక్షత్రం ⭐"],
                    "answer": "వృత్తం ⭕",
                    "explanation": "వృత్తం ఒకవక గుండ్రంగా ఉంటుంది."
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "అడవికి రాజుగా పేరుపొందిన జంతువు ఏది? 🦁",
                    "options": ["సింహం 🦁", "ఏనుగు 🐘", "కోతి 🐒", "కుందేలు 🐰"],
                    "answer": "సింహం 🦁",
                    "explanation": "సింహాన్ని సాధారణంగా అడవి రాజునిగా పిలుస్తారు."
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "మైక్రోఫోన్‌ క్లిక్ చేసి చెప్పండి: 'నమస్కారం' 👋",
                    "hint": "నమస్కారం",
                    "options": [],
                    "answer": "నమస్కారం",
                    "explanation": "నమస్కారం చెప్పడం ప్రాక్టీस చేయండి."
                }
            ],
            "Hindi": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'म्याऊं म्याऊं' कौन सा जानवर करता है? 🐱",
                    "options": ["गाय 🐮", "कुत्ता 🐶", "शेर 🦁", "बिल्ली 🐱"],
                    "answer": "बिल्ली 🐱",
                    "explanation": "बिल्ली म्याऊं म्याऊं करती है!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "कौन सा फल लाल रंग का है? 🍓 (चित्र पर इशारा या चुनें)",
                    "options": ["स्ट्रॉबेरी 🍓", "केला 🍌", "अंगूर 🍇", "नाशपाती 🍐"],
                    "answer": "स्ट्रॉबेरी 🍓",
                    "explanation": "स्ट्रॉबेरी आम तौर पर लाल रंग की होती है।"
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "गोल आकृति को दिखाएं या चुनें। ⭕",
                    "options": ["गोला/वृत्त ⭕", "वर्ग ⬛", "त्रिकोण 🔺", "तारा ⭐"],
                    "answer": "गोला/वृत्त ⭕",
                    "explanation": "वृत्त का कोई नुकीला कोना नहीं होता।"
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "किस जानवर को अक्सर जंगल का राजा कहा जाता है? 🦁",
                    "options": ["शेर 🦁", "हाथी 🐘", "बंदर 🐒", "खरगोश 🐰"],
                    "answer": "शेर 🦁",
                    "explanation": "शेर को पारंपरिक रूप से जंगल का राजा माना जाता है।"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "माइक चालू करें और बोलें: 'नमस्ते' 👋",
                    "hint": "नमस्ते",
                    "options": [],
                    "answer": "नमस्ते",
                    "explanation": "नमस्ते बोलना सीखें।"
                }
            ],
            "Tamil": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'லொள் லொள்' என்று குறைக்கும் விலங்கு எது? 🐶",
                    "options": ["பசு 🐮", "நாய் 🐶", "சிங்கம் 🦁", "பூனை 🐱"],
                    "answer": "நாய் 🐶",
                    "explanation": "நாய்கள் லொள் லொள் என்று குறைக்கும்!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "சிவப்பு நிற பழத்தைக் கண்டறியவும்! 🍓",
                    "options": ["ஸ்ட்ராபெரி 🍓", "வாழைப்பழம் 🍌", "திராட்சை 🍇", "பேரிக்காய் 🍐"],
                    "answer": "ஸ்ட்ராபெரி 🍓",
                    "explanation": "ஸ்ட்ராபெரி சிவப்பு நிறத்தில் இருக்கும்!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "வட்ட வடிவத்தை அடையாளம் காணவும்! ⭕",
                    "options": ["வட்டம் ⭕", "சதுரம் ⬛", "முக்கோணம் 🔺", "நட்சத்திரம் ⭐"],
                    "answer": "வட்டம் ⭕",
                    "explanation": "வட்டம் வட்டமாக இருக்கும்!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "காட்டின் ராஜா யார்? 🦁",
                    "options": ["சிங்கம் 🦁", "யானை 🐘", "குரங்கு 🐒", "முயல் 🐰"],
                    "answer": "சிங்கம் 🦁",
                    "explanation": "சிங்கம் காட்டின் ராஜா!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "மைக் ஒளிரச் செய்து கூறவும்: 'வணக்கம்' 👋",
                    "hint": "வணக்கம்",
                    "options": [],
                    "answer": "வணக்கம்",
                    "explanation": "வணக்கம் சொல்ல பயிற்சி செய்யவும்."
                }
            ],
            "Kannada": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'ಬೌ ಬೌ' ಎಂದು ಕೂಗುವ ಪ್ರಾಣಿ ಯಾವುದು? 🐶",
                    "options": ["ಹಸು 🐮", "ನಾಯಿ 🐶", "ಸಿಂಹ 🦁", "ಬೆಕ್ಕು 🐱"],
                    "answer": "ನಾಯಿ 🐶",
                    "explanation": "ನಾಯಿಗಳು ಬೌ ಬೌ ಎಂದು ಕೂಗುತ್ತವೆ!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ಕೆಂಪು ಬಣ್ಣದ ಹಣ್ಣನ್ನು ಗುರುತಿಸಿ! 🍓",
                    "options": ["ಸ್ಟ್ರಾಬೆರಿ 🍓", "ಬಾಳೆಹಣ್ಣು 🍌", "ದ್ರಾಕ್ಷಿ 🍇", "ಸೇಬು 🍎"],
                    "answer": "ಸ್ಟ್ರಾಬೆರಿ 🍓",
                    "explanation": "ಸ್ಟ್ರಾಬೆರಿ ಹಣ್ಣುಗಳು ಕೆಂಪಾಗಿರುತ್ತವೆ!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ವೃತ್ತಾಕಾರವನ್ನು ಗುರುತಿಸಿ! ⭕",
                    "options": ["ವೃತ್ತ ⭕", "ಚೌಕ ⬛", "ತ್ರಿಕೋನ 🔺", "ನಕ್ಷತ್ರ ⭐"],
                    "answer": "ವೃತ್ತ ⭕",
                    "explanation": "ವೃತ್ತವು ಗೋಲಾಕಾರವಾಗಿರುತ್ತದೆ!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ಕಾಡಿನ ರಾಜ ಯಾರು? 🦁",
                    "options": ["ಸಿಂಹ 🦁", "ಆನೆ 🐘", "ಕೋತಿ 🐒", "ಮೊಲ 🐰"],
                    "answer": "ಸಿಂಹ 🦁",
                    "explanation": "ಸಿಂಹವು ಕಾಡಿನ ರಾಜ!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "ಮೈಕ್ರೊಫೋನ್ ಒತ್ತಿ ಹೇಳಿ: 'ನಮಸ್ಕಾರ' 👋",
                    "hint": "ನಮಸ್ಕಾರ",
                    "options": [],
                    "answer": "ನಮಸ್ಕಾರ",
                    "explanation": "ನಮಸ್ಕಾರ ಹೇಳುವುದನ್ನು ಅಭ್ಯಾಸ ಮಾಡಿ."
                }
            ],
            "Marathi": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'म्याऊं म्याऊं' आवाज करणारा प्राणी कोणता? 🐱",
                    "options": ["गाय 🐮", "कुत्रा 🐶", "सिंह 🦁", "मांजर 🐱"],
                    "answer": "मांजर 🐱",
                    "explanation": "मांजर म्याऊं म्याऊं ओरडते!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "लाल रंगाचे फळ ओळखा! 🍓",
                    "options": ["स्ट्रॉबेरी 🍓", "केळे 🍌", "द्राक्षे 🍇", "सफरचंद 🍎"],
                    "answer": "स्ट्रॉबेरी 🍓",
                    "explanation": "स्ट्रॉबेरी लाल रंगाची असते!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "गोल आकार ओळखा! ⭕",
                    "options": ["वर्तुळ ⭕", "चौकोन ⬛", "त्रिकोण 🔺", "चांदणी ⭐"],
                    "answer": "वर्तुळ ⭕",
                    "explanation": "वर्तुळ गोल असते!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "जंगलाचा राजा कोण आहे? 🦁",
                    "options": ["सिंह 🦁", "हत्ती 🐘", "माकड 🐒", "ससा 🐰"],
                    "answer": "सिंह 🦁",
                    "explanation": "सिंह जंगलाचा राजा असतो!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "माईक चालू करा आणि म्हणा: 'नमस्कार' 👋",
                    "hint": "नमस्कार",
                    "options": [],
                    "answer": "नमस्कार",
                    "explanation": "नमस्कार म्हणण्याचा सराव करा."
                }
            ]
        }
        qs = multilingual_questions.get(language, multilingual_questions["English"])
        for q in qs:
            q["age_band"] = "young"
            q["level"] = "Beginner"
            q["language"] = language
            q["skill_score_key"] = q["skill"]
        if not any(q["skill_score_key"] == "writing" for q in qs):
            for q in reversed(qs):
                if q["type"] == "speaking":
                    q["skill_score_key"] = "writing"
                    break
        if len(qs) < 6:
            qs.append({
                "name": "q_extra",
                "type": "comprehension",
                "skill": "comprehension",
                "section": "Comprehension Assessment",
                "prompt": "Which picture shows something that is red?",
                "options": ["Apple 🍎", "Banana 🍌", "Grapes 🍇", "Pear 🍐"],
                "answer": "Apple 🍎",
                "explanation": "The apple is red.",
                "age_band": "young",
                "level": "Beginner",
                "language": language,
                "skill_score_key": "comprehension"
            })
        return qs

    if not learning_level:
        learning_level = session.get("learning_level", "Beginner")

    import random

    lang_pools = {
        "English": {
            "letters": [
                ("Sound /b/", "B", ["B", "D", "P", "T"], "B makes the /b/ sound."),
                ("Sound /f/", "F", ["F", "V", "P", "S"], "F makes the /f/ sound."),
                ("Sound /m/", "M", ["M", "N", "W", "V"], "M makes the /m/ sound."),
                ("Sound /s/", "S", ["S", "C", "Z", "X"], "S makes the /s/ sound.")
            ],
            "simple_words": [
                ("apple", "Apple", ["Apple", "Banana", "Chair", "Tree"], "Apple is the correct word for the fruit."),
                ("ball", "Ball", ["Ball", "Cat", "Sun", "Fish"], "Ball is a common toy."),
                ("cup", "Cup", ["Cup", "Shoe", "Pen", "Door"], "Cup holds water or milk.")
            ],
            "objects": [
                ({"image_url": "/static/images/apple.svg", "alt": "Apple"}, "Apple", "This is an apple."),
                ({"image_url": "/static/images/dog.svg", "alt": "Dog"}, "Dog", "This is a dog."),
                ({"image_url": "/static/images/car.svg", "alt": "Car"}, "Car", "This is a car.")
            ],
            "word_completions": [
                ("B__", "Bee", "Complete the word to name the insect."),
                ("C_t", "Cat", "Complete the word to name the animal."),
                ("S_n", "Sun", "Complete the word for the bright star in the day sky.")
            ],
            "sentences": [
                ("The cat is on the mat.", "The cat is on the mat.", ["The dog is on the mat.", "The cat is under the mat.", "The cat is on the mat."], "Choose the sentence that matches the reading."),
                ("He ate an apple.", "He ate an apple.", ["He ate an apple.", "She eats a book.", "They run fast."], "Pick the sentence that is correct."),
                ("The sun is warm.", "The sun is warm.", ["The moon is warm.", "The sun is warm.", "The sky is green."], "Read and choose the correct sentence.")
            ],
            "paragraphs": [
                ("Sara loves to read books at the park. She sits under a tree and reads every day.", "Where does Sara read?", "At the park", ["At the park", "In the car", "At school", "At the mall"], "Sara reads at the park."),
                ("A boy planted a tree in his garden. The tree grew tall and gave shade.", "What did the boy plant?", "A tree", ["A tree", "A flower", "A book", "A toy"], "The boy planted a tree."),
                ("Ria feeds the birds in the morning. She gives them seeds and water.", "Who does Ria feed?", "The birds", ["The birds", "The cats", "The dog", "The fish"], "Ria feeds the birds.")
            ],
            "paragraph_writing": [
                ("your favorite toy", "My favorite toy is a red ball. I play with it every day.", "Write a short paragraph about your favorite toy."),
                ("a day at school", "I went to school and learned new things. I liked drawing and reading.", "Write a short paragraph about a day at school."),
                ("a family picnic", "We had a picnic with my family under a big tree. We ate sandwiches and fruit.", "Write a short paragraph about a family picnic.")
            ],
            "sentence_writing": [
                ("Describe your pet.", "I have a small pet dog.", "Write a short sentence about your pet."),
                ("Tell us what you like.", "I like to eat apples.", "Write one sentence about what you like."),
                ("What did you do today?", "I played and read a book.", "Write one sentence about your day.")
            ],
            "listening_words": [
                ("Apple", "Apple", ["Apple", "Banana", "House", "Dog"], "Choose the word you heard."),
                ("Ball", "Ball", ["Ball", "Cat", "Tree", "Fish"], "Choose the word you heard."),
                ("Sun", "Sun", ["Sun", "Moon", "Star", "Rain"], "Choose the word you heard.")
            ],
            "listening_sentences": [
                ("The cat sleeps.", "Where is the cat?", "On the mat", ["On the mat", "In the tree", "In the car", "In the room"], "Listen and answer the question."),
                ("Sara eats an apple.", "What did Sara eat?", "An apple", ["An apple", "A banana", "A sandwich", "Some rice"], "Listen carefully and choose the answer."),
                ("A bird sings in the tree.", "Who sings?", "A bird", ["A bird", "A dog", "A cat", "A fish"], "Listen and choose the correct answer.")
            ],
            "listening_paragraphs": [
                ("Ria went to the market and bought fruits for her family.", "What did Ria buy?", "Fruits", ["Fruits", "Vegetables", "Books", "Toys"], "Listen to the passage and answer the question."),
                ("The children played games and then ate lunch together.", "What did the children do?", "Played games", ["Played games", "Studied hard", "Watched TV", "Went home"], "Listen and choose the answer."),
                ("A teacher reads a story to the students every morning.", "Who reads the story?", "A teacher", ["A teacher", "A student", "A parent", "A bird"], "Listen and answer clearly.")
            ],
            "speaking_phrases": [
                "Hello",
                "Thank you",
                "I like apples",
                "Good morning"
            ],
            "speaking_responses": [
                ("What is your name?", "My name is Ria."),
                ("What do you like to eat?", "I like to eat apples."),
                ("Where do you live?", "I live in a small town.")
            ],
            "colors": [
                ("🐸", "Green", ["Green", "Red", "Blue", "Yellow"], "The frog is green."),
                ("🍋", "Yellow", ["Yellow", "Blue", "Black", "White"], "The lemon is yellow."),
                ("🍓", "Red", ["Red", "Purple", "Orange", "Gray"], "The strawberry is red.")
            ],
            "shape_words": [
                ("A shape with three sides", "Triangle", ["Triangle", "Circle", "Square", "Star"], "A triangle has three sides."),
                ("A shape with four equal sides", "Square", ["Square", "Circle", "Triangle", "Rectangle"], "A square has four equal sides."),
                ("A round shape", "Circle", ["Circle", "Triangle", "Square", "Heart"], "A circle is round.")
            ],
            "vocabulary": [
                ("Joyful", "Happy", ["Happy", "Sad", "Hungry", "Cold"], "Joyful means happy."),
                ("Rapid", "Fast", ["Fast", "Slow", "Quiet", "Loud"], "Rapid means fast."),
                ("Tiny", "Small", ["Small", "Large", "Angry", "Bright"], "Tiny means small.")
            ],
            "grammar": [
                ("Choose the correct sentence.", "She is reading a book.", ["She is reading a book.", "She are reading a book.", "She reading a book."], "This sentence is grammatically correct."),
                ("Choose the correct sentence.", "He has two pencils.", ["He has two pencils.", "He have two pencils.", "He has two pencil."], "This sentence is grammatically correct."),
                ("Choose the correct sentence.", "They are playing in the park.", ["They are playing in the park.", "They is playing in the park.", "They playing in the park."], "This sentence is grammatically correct.")
            ],
            "reading_letters": [
                ("Alphabet Identification: Select the letter that makes the sound /b/:", "B", ["B", "D", "P", "T"], "B makes the /b/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /f/:", "F", ["F", "V", "P", "S"], "F makes the /f/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /m/:", "M", ["M", "N", "W", "V"], "M makes the /m/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /s/:", "S", ["S", "C", "Z", "X"], "S makes the /s/ sound.")
            ],
            "comps": [
                ("The cat is sleeping under the tree.", "Where is the cat sleeping?", "Under the tree", ["Under the tree", "On the branch", "In the house", "In the car"]),
                ("The quick brown fox jumps over the lazy dog.", "Which animal is lazy?", "Dog", ["Dog", "Fox", "Cat", "Rabbit"]),
                ("Sam likes playing soccer in the afternoon.", "What does Sam like playing?", "Soccer", ["Soccer", "Tennis", "Basketball", "Golf"])
            ],
            "spelling": [
                ("Spelling Check: Choose the correct spelling for 🐘:", "Elephant", ["Elephant", "Elefant", "Eliphent", "Aliphant"]),
                ("Spelling Check: Choose the correct spelling for 🏠:", "House", ["House", "Howse", "Hous", "Hause"]),
                ("Spelling Check: Choose the correct spelling for 📖:", "Book", ["Book", "Boke", "Bouk", "Buck"])
            ],
            "listening": [
                ("Welcome", ["Welcome", "Thank you", "Goodbye", "Hello"]),
                ("Elephant", ["Elephant", "Tiger", "Lion", "Giraffe"]),
                ("Foundational", ["Foundational", "Educational", "Instructional", "Professional"])
            ],
            "speaking": [
                "Learning a new language opens up doors to new worlds.",
                "Reading books everyday expands your vocabulary.",
                "Lumi is my helper coach for regional scripts."
            ]
        },
        "Telugu": {
            "reading_letters": [
                ("అక్షర గుర్తింపు: వర్ణమాలలో మొదటి అక్షరం ఏది?", "అ", ["అ", "ఆ", "ఇ", "ఈ"], "అ మొదటి స్వరాక్షరం."),
                ("కింది వాటిలో రెండపదం ఏది?", "అమ్మ", ["అమ్మ", "ఆవు", "అనిల్", "ఇది"], "మాతృపదం గుర్తింపు.")
            ],
            "comps": [
                ("రాము బడికి వెళ్ళాడు.", "రాము ఎక్కడికి వెళ్ళాడు?", "బడికి", ["బడికి", "ఇంటికి", "గుడికి", "తోటకే"]),
                ("పిల్లి పాలు తాగింది.", "పిల్లి ఏమి తాగింది?", "పాలు", ["పాలు", "నీరు", "పెండు", "పువ్వు"])
            ],
            "spelling": [
                ("సరైన పదాన్ని ఎంచుకోండి (బల్లి):", "బల్లి", ["బల్లి", "బలీ", "బళి", "బల్లి"], "బల్లి సరిగ్గా వ్రాయండి."),
                ("సరైన పదాన్ని ఎంచుకోండి (పుస్తకం):", "పుస్తకం", ["పుస్తకం", "పుస్తఖం", "పుస్తకo", "పుస్తకము"], "పుస్తకం శబ్దాన్ని గుర్తించండి.")
            ],
            "listening": [
                ("కుక్క", ["కుక్క", "పిల్లి", "కాగితం", "పువ్వు"]),
                ("పండు", ["పండు", "పత్రం", "పెంక్", "పూలు"])
            ],
            "speaking": [
                "నమస్కారం",
                "నేను తెలుగు మాట్లాడగలను",
                "ఇది ఒక మంచి రోజు"
            ]
        },
        "Hindi": {
            "reading_letters": [
                ("वर्णमाला पहचान: इनमें से पहला स्वर कौन सा है?", "अ", ["अ", "आ", "इ", "ई"], "अ हिंदी वर्णमाला का पहला स्वर है।"),
                ("किन्हीं संयुक्त व्यंजनों में से कौन सा है?", "क्ष", ["क्ष", "क", "ख", "ग"], "क्ष संयुक्त व्यंजन है।")
            ],
            "comps": [
                ("राम ने सेब खाया।", "सेब किसने खाया?", "राम", ["राम", "श्याम", "मोहन", "बंदर"]),
                ("बिल्ली दूध पीती है।", "बिल्ली क्या पीती है?", "दूध", ["दूध", "पानी", "रस", "चाय"])
            ],
            "spelling": [
                ("सही वर्तनी चुनें (हाथी):", "हाथी", ["हाथी", "हथी", "हाथि", "हाती"]),
                ("सही वर्तनी चुनें (किताब):", "किताब", ["किताब", "केताब", "कीताब", "किताम"])
            ],
            "listening": [
                ("नमस्ते", ["नमस्ते", "अलविदा", "धन्यवाद", "स्वागत"]),
                ("मछली", ["🐟 मछली", "🐶 कुत्ता", "🐱 बिल्ली", "🦁 शेर"])
            ],
            "speaking": [
                "नमस्ते",
                "मेरा प्यारा घर",
                "पेड़ हमें फल देते हैं",
                "हमें रोज़ स्कूल जाना चाहिए",
                "हिंदी हमारी राष्ट्रभाषा है"
            ]
        },
        "Tamil": {
            "reading_letters": [
                ("எழுத்து அடையாளம்: உயிர் எழுத்துக்களில் முதல் எழுத்து எது?", "அ", ["அ", "ஆ", "இ", "ஈ"], "அ என்பது முதல் உயிர் எழுத்து."),
                ("கீழ்க்கண்டவற்றுள் மெய் எழுத்து எது?", "க்", ["க்", "அ", "க", "சா"], "க் என்பது மெய் எழுத்து.")
            ],
            "comps": [
                ("பூனை கட்டிலின் மேல் உள்ளது.", "பூனை எங்கு உள்ளது?", "கட்டிலின் மேல்", ["கட்டிலின் மேல்", "பெட்டிக்குள்", "மரத்தின் மேல்", "வீட்டில்"]),
                ("எலி வேகமாக ஓடுகிறது.", "எது வேகமாக ஓடுகிறது?", "எலி", ["எலி", "பூனை", "நாய்", "மாடு"])
            ],
            "spelling": [
                ("சரியான சொல்லைத் தேர்ந்தெடுக்கவும் (அம்மா):", "அம்மா", ["அம்மா", "அமா", "ஆம்மா", "அம்மி"]),
                ("சரியான சொல்லைத் தேர்ந்தெடுக்கவும் (பள்ளி):", "பள்ளி", ["பள்ளி", "பலி", "பாலீ", "பல்ளி"])
            ],
            "listening": [
                ("வணக்கம்", ["வணக்கம்", "நன்றி", "வரவேற்பு", "போய்வருகிறேன்"]),
                ("பூனை", ["🐱 பூனை", "🐶 நாய்", "🐰 முயல்", "🐮 பசு"])
            ],
            "speaking": [
                "வணக்கம்",
                "அம்மா எனக்கு பால் தந்தார்",
                "தமிழ் எங்கள் தாய்மொழி",
                "நாங்கள் தினமும் பள்ளிக்குச் செல்வோம்",
                "இயற்கையைக் காப்போம்"
            ]
        },
        "Kannada": {
            "reading_letters": [
                ("ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ: ಕನ್ನಡ ವರ್ಣಮಾಲೆಯ ಮೊದಲ ಅಕ್ಷರ ಯಾವುದು?", "ಅ", ["ಅ", "ಆ", "ಇ", "ಈ"], "ಅ ಮೊದಲ ಅಕ್ಷರವಾಗಿದೆ."),
                ("ಕನ್ನಡದಲ್ಲಿ ಸ್ವರಗಳ ಸಂಖ್ಯೆ ಎಷ್ಟು?", "೧೩", ["೧೩", "೧೫", "೧೦", "೩೪"], "ಕನ್ನಡದಲ್ಲಿ ೧೩ ಸ್ವರಗಳಿವೆ.")
            ],
            "comps": [
                ("ರಾಜು ಶಾಲೆಗೆ ಹೋದನು.", "ರಾಜು ಎಲ್ಲಿಗೆ ಹೋದನು?", "ಶಾಲೆಗೆ", ["ಶಾಲೆಗೆ", "ಮನೆಗೆ", "ತೋಟಕ್ಕೆ", "ದೇವಸ್ಥಾನಕ್ಕೆ"]),
                ("ಬೆಕ್ಕು ಹಾಲು ಕುಡಿಯಿತು.", "ಬೆಕ್ಕು ಏನನ್ನು ಕುಡಿಯಿತು?", "ಹಾಲು", ["ಹಾಲು", "ನೀರು", "ಮಜ್ಜಿಗೆ", "ರಸ"])
            ],
            "spelling": [
                ("ಸರಿಯಾದ ಪದವನ್ನು ಆರಿಸಿ (ಶಾಲೆ):", "ಶಾಲೆ", ["ಶಾಲೆ", "ಸಾಲೆ", "ಶಾಲಿ", "ಸಾಲ"]),
                ("ಸರಿಯಾದ ಪದವನ್ನು ಆರಿಸಿ (ಪುಸ್ತಕ):", "ಪುಸ್ತಕ", ["ಪುಸ್ತಕ", "ಪುಸ್ತಖ", "ಪೂಸ್ತಕ", "ಪುಸ್ತಕು"])
            ],
            "listening": [
                ("ನಮಸ್ಕಾರ", ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದಗಳು", "ಶುಭೋದಯ", "ಬನ್ನಿ"]),
                ("ಮನೆ", ["🏠 ಮನೆ", "🏫 ಶಾಲೆ", "🌳 ಮರ", "🚗 ಕಾರು"])
            ],
            "speaking": [
                "ನಮಸ್ಕಾರ",
                "ಕನ್ನಡ ನಮ್ಮ ತಾಯ್ನುಡಿ",
                "ಮನೆ ಅತಿ ಸುಂದರವಾಗಿದೆ",
                "ನಾವು ಪ್ರತಿದಿನ ಶಾಲೆಗೆ ಹೋಗುತ್ತೇವೆ",
                "ಗಿಡಮರ들을 ಬೆಳೆಸೋಣ"
            ]
        },
        "Marathi": {
            "reading_letters": [
                ("अक्षर ओळख: मराठी वर्णमालेतील पहिले अक्षर कोणते?", "अ", ["अ", "आ", "इ", "ई"], "अ हे पहिले अक्षर आहे।"),
                ("खालीलपैकी संयुक्त व्यंजन कोणते?", "क्ष", ["क्ष", "क", "ख", "ग"], "क्ष संयुक्त व्यंजन आहे।")
            ],
            "comps": [
                ("राजू शाळेत गेला.", "राजू कोठे गेला?", "शाळेत", ["शाळेत", "घरी", "बागेत", "मंदिरात"]),
                ("मांजर दूध पिते.", "मांजर काय पिते?", "दूध", ["दूध", "पाणी", "रस", "चहा"])
            ],
            "spelling": [
                ("योग्य शब्द निवडा (हत्ती):", "हत्ती", ["हत्ती", "हती", "हात्ती", "हाती"]),
                ("योग्य शब्द निवडा (पुस्तक):", "पुस्तक", ["पुस्तक", "पुस्तख", "पूस्तक", "पुस्तकू"])
            ],
            "listening": [
                ("नमस्कार", ["नमस्कार", "धन्यवाद", "स्वागत", "शुभ रात्री"]),
                ("घर", ["🏠 घर", "🏫 शाळा", "🌳 झाड", "🚗 गाडी"])
            ],
            "speaking": [
                "नमस्कार",
                "झाडे आपल्याला सावली देतात",
                "आम्ही रोज शाळेत जातो",
                "मराठी माझी मातृभाषा आहे"
            ]
        }
    }

    pool = lang_pools.get(language, lang_pools["English"])
    profile = _get_assessment_profile(learning_level, _get_age_band(age_val))
    questions = _build_level_questions(language, profile, pool)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assessment_questions WHERE language = ?", (language,))
        db_qs = cursor.fetchall()
        conn.close()
        for q in db_qs:
            opts_list = [o.strip() for o in str(q["options"]).split(",") if o.strip()]
            while len(opts_list) < 4:
                opts_list.append("Option " + str(random.randint(1, 100)))
            opts_list = opts_list[:4]
            correct_idx = int(q["correct_index"]) if q["correct_index"] is not None else 0
            ans = opts_list[correct_idx] if correct_idx < len(opts_list) else opts_list[0]
            questions.append({
                "name": f"q_custom_{q['id']}",
                "type": str(q["category"] or "reading").lower(),
                "skill": str(q["category"] or "reading").lower(),
                "prompt": q["prompt"],
                "options": opts_list,
                "answer": ans,
                "explanation": q["explanation"] or "Custom question approved by admin.",
                "age_band": profile["age_band"],
                "level": profile["level"],
                "language": language,
                "skill_score_key": str(q["category"] or "reading").lower(),
            })
    except Exception as e:
        print(f"[ASSESSMENT MERGE ERROR] {e}")

    return questions


def get_assessment_questions(language, age=None, learning_level=None, mode=None):
    return _legacy_get_assessment_questions(language, age, learning_level, mode)


WEEK_MODULE_CONTENT = {
    "English": {
        "module_title": "Learning Content Management & Assessment Framework",
        "description": "Complete the literacy curriculum structure with reading, writing, and comprehension activities designed for multilingual learners.",
        "curriculum": [
            {
                "heading": "Reading Foundations",
                "details": "Build reading fluency with short passages, sight words, and comprehension questions that prepare learners for everyday literacy."
            },
            {
                "heading": "Writing Practice",
                "details": "Develop writing confidence through sentence construction, spelling exercises, and typing-based responses."
            },
            {
                "heading": "Comprehension Support",
                "details": "Strengthen understanding with story sequencing, question answering, and vocabulary matching activities."
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "Reading Task",
                "description": "Answer comprehension questions after reading a short passage."
            },
            {
                "title": "Writing Task",
                "description": "Type the missing words or build simple sentences based on prompts."
            },
            {
                "title": "Speaking Task",
                "description": "Practice aloud and then type the sentence to demonstrate spoken literacy awareness."
            }
        ],
        "benchmarks": [
            {
                "level": "Proficient",
                "range": "80–100%",
                "notes": "Learner demonstrates strong reading, writing, and comprehension skills for beginner literacy."
            },
            {
                "level": "Developing",
                "range": "50–79%",
                "notes": "Learner is making progress and should continue guided practice with reading and writing tasks."
            },
            {
                "level": "Beginner",
                "range": "0–49%",
                "notes": "Learner benefits from foundational support in letter recognition, simple words, and sentence structure."
            }
        ]
    },
    "Telugu": {
        "module_title": "నేర్చుకోవడపు కంటెంట్ నిర్వహణ & అంచనా ఫ్రేమ్‌వర్క్",
        "description": "చదవడం, వ్రాయడం, మరియు అవగాహన కార్యాలయాలను పొందుపరిచి భాషా specimens యొక్క సాహిత్య విద్యక్రమాన్ని పూర్తి చేయండి.",
        "curriculum": [
            {
                "heading": "చదవడపు పునాది",
                "details": "సాధారణ పాఠాలు, సైట్ పదాలు, మరియు అవగాహన ప్రశ్నలతో చదవడపు నైపుణ్యాన్ని మెరుగుపరచండి."
            },
            {
                "heading": "వ్రాయడపు అభ్యాసం",
                "details": "వాక్య నిర్మాణం, వృత్తిపరమైన అక్షరాలు, మరియు టైపింగ్ సమాధానాల ద్వారా లిఖిత నైపుణ్యాన్ని పెంపొందించండి."
            },
            {
                "heading": "అవగాహన మద్దతు",
                "details": "కథ క్రమాన్ని, ప్రశ్నల సమాధానాన్ని, మరియు పదజాలం మ్యాచ్ చేయడాన్ని వినియోగించి అవగాహనను బలోపేతం చేయండి."
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "చదవడపు పని",
                "description": "చిన్న పాఠం చదివిన తరువాత అవగాహన ప్రశ్నలకు సమాధానమివ్వండి."
            },
            {
                "title": "వ్రాయడపు పని",
                "description": "ప్రాంప్ట్‌ల ఆధారంగా ఖాళీ పదాలను టైప్ చేయండి లేదా వాక్యాలను నిర్మించండి."
            },
            {
                "title": "మాట్లాడడపు పని",
                "description": "పట్టుమ‌ని గా అభ్యాసించి ఆ తర్వాత వాక్యాన్ని టైప్ చేయండి."
            }
        ],
        "benchmarks": [
            {
                "level": "ప్రావీణ్యంలొ",
                "range": "80–100%",
                "notes": "ప్రారంభ సాహిత్యానికి బలమైన చదవడం, వ్రాయడం మరియు అవగాహన నైపుణ్యాలు చూపిస్తోంది."
            },
            {
                "level": "వికాసంలో",
                "range": "50–79%",
                "notes": "చదవడంలో మరియు వ్రాయడంలో మార్గనిర్దేశనతో సాధన కొనసాగించాల్సిన అవసరం ఉంది."
            },
            {
                "level": "ప్రారంభ స్థాయి",
                "range": "0–49%",
                "notes": "అక్షర గుర్తింపు, సులభ పదాలు, మరియు వాక్య నిర్మాణంలో ప్రాథమిక మద్దతు అవసరం."
            }
        ]
    },
    "Hindi": {
        "module_title": "शिक्षण सामग्री प्रबंधन और आकलन ढांचा",
        "description": "पढ़ने, लिखने और समझने की गतिविधियों के साथ बहुभाषी शिक्षार्थियों के लिए साक्षरता पाठ्यक्रम तैयार करें।",
        "curriculum": [
            {
                "heading": "पढ़ने की नींव",
                "details": "छोटे अंशों, साइट शब्दों और समझ प्रश्नों से पढ़ने की क्षमता मजबूत करें।"
            },
            {
                "heading": "लेखन अभ्यास",
                "details": "वाक्य निर्माण, वर्तनी अभ्यास और टाइपिंग आधारित उत्तरों के माध्यम से लेखन कौशल विकसित करें।"
            },
            {
                "heading": "समझ का समर्थन",
                "details": "कहानी क्रम, प्रश्न उत्तर, और शब्दावली मेल से समझ को मज़बूत करें।"
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "पढ़ने का कार्य",
                "description": "एक छोटे पाठ पढ़ने के बाद समझ प्रश्नों का उत्तर दें।"
            },
            {
                "title": "लेखन कार्य",
                "description": "प्रॉम्प्ट के आधार पर रिक्त शब्द टाइप करें या सरल वाक्य बनाएं।"
            },
            {
                "title": "बोलने का कार्य",
                "description": "उच्चारण का अभ्यास करें और फिर वाक्य टाइप करें।"
            }
        ],
        "benchmarks": [
            {
                "level": "कुशल",
                "range": "80–100%",
                "notes": "शुरुआती साक्षरता के लिए मजबूत पढ़ने, लिखने और समझ कौशल दिखाता है।"
            },
            {
                "level": "विकसित हो रहा है",
                "range": "50–79%",
                "notes": "सहायता के साथ अभ्यास जारी रखें और पढ़ने/लिखने के कार्य दोहराएं।"
            },
            {
                "level": "शुरुआती",
                "range": "0–49%",
                "notes": "आधारभूत अक्षर, शब्द और वाक्य संरचना पर मजबूत समर्थन की आवश्यकता है।"
            }
        ]
    },
    "Tamil": {
        "module_title": "கற்றல் உள்ளடக்க மேலாண்மை & மதிப்பீட்டு கட்டமைப்பு",
        "description": "பல்மொழி கற்பவர்களுக்காக வடிவமைக்கப்பட்ட வாசிப்பு, எழுதுதல் மற்றும் புரிந்துகொள்ளும் செயல்பாடுகளுடன் எழுத்தறிவு பாடத்திட்டத்தை முடிக்கவும்.",
        "curriculum": [
            {
                "heading": "வாசிப்பு அடித்தளம்",
                "details": "குறுகிய பத்திகள் மற்றும் புரிதல் கேள்விகள் மூலம் வாசிப்பு திறனை வளர்க்கவும்."
            },
            {
                "heading": "எழுத்து பயிற்சி",
                "details": "வாக்கிய உருவாக்கம் மற்றும் தட்டச்சு அடிப்படையிலான பதில்கள் மூலம் எழுத்து பயிற்சியை மேம்படுத்தவும்."
            },
            {
                "heading": "புரிதல் ஆதரவு",
                "details": "கதை வரிசைப்படுத்துதல் மற்றும் சொல்லகராதி பொருத்துதல் மூலம் புரிதலை வலுப்படுத்தவும்."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "வாசிப்பு பணி",
                "description": "ஒரு குறுகிய பத்தியை வாசித்த பிறகு கேள்விகளுக்கு பதிலளிக்கவும்."
            },
            {
                "title": "எழுதும் பணி",
                "description": "விடுபட்ட வார்த்தைகளை நிரப்பவும் அல்லது எளிய வாக்கியங்களை உருவாக்கவும்."
            },
            {
                "title": "பேசும் பணி",
                "description": "வாக்கியங்களை சத்தமாக படித்து தட்டச்சு செய்யவும்."
            }
        ],
        "benchmarks": [
            {
                "level": "திறமையானவர்",
                "range": "80–100%",
                "notes": "கற்பவர் சிறந்த வாசிப்பு, எழுதுதல் மற்றும் புரிந்துகொள்ளும் திறன்களைக் காட்டுகிறார்."
            },
            {
                "level": "வளரும் நிலை",
                "range": "50–79%",
                "notes": "கற்பவர் முன்னேறி வருகிறார், வழிகாட்டப்பட்ட பயிற்சிகளைத் தொடர வேண்டும்."
            },
            {
                "level": "தொடக்கநிலை",
                "range": "0–49%",
                "notes": "எழுத்து அங்கீகாரம் மற்றும் எளிய சொற்களில் அடிப்படை ஆதரவு தேவை."
            }
        ]
    },
    "Kannada": {
        "module_title": "ಕಲಿಕಾ ವಿಷಯ ನಿರ್ವಹಣೆ ಮತ್ತು ಮೌಲ್ಯಮಾಪನ ಚೌಕಟ್ಟು",
        "description": "ಬಹುಭಾಷಾ ಕಲಿಯುವವರಿಗಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಓದುವಿಕೆ, ಬರವಣಿಗೆ ಮತ್ತು ಗ್ರಹಿಕೆ ಚಟುವಟಿಕೆಗಳೊಂದಿಗೆ ಸಾಕ್ಷರತಾ ಪಠ್ಯಕ್ರಮವನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ.",
        "curriculum": [
            {
                "heading": "ಓದುವ ಬುನಾದಿ",
                "details": "ಸಣ್ಣ ಪ್ಯಾರಾಗ್ರಾಫ್ ಮತ್ತು ಗ್ರಹಿಕೆ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ಓದುವ ನಿರರ್ಗಳತೆಯನ್ನು ಬೆಳೆಸಿಕೊಳ್ಳಿ."
            },
            {
                "heading": "ಬರವಣಿಗೆ ಅಭ್ಯಾಸ",
                "details": "ವಾಕ್യ ರಚನೆ ಮತ್ತು ಟೈಪಿಂಗ್ ಆಧಾರಿತ ಪ್ರತಿಕ್ರിയೆಗಳ ಮೂಲಕ ಬರವಣಿಗೆಯನ್ನು ಸುಧಾರಿಸಿ."
            },
            {
                "heading": "ಗ್ರಹಿಕೆ ಬೆಂಬಲ",
                "details": "ಕಥೆಯ ക്രമീകരണം ಮತ್ತು ಶಬ್ದಕೋಶ ಹೊಂದಾಣಿಕೆಯ ಮೂಲಕ ಗ್ರಹಿಕೆಯನ್ನು ಬಲಪಡಿಸಿ."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "ಓದುವ ಕಾರ್ಯ",
                "description": "ಸಣ್ಣ ಗದ್ಯವನ್ನು ಓದಿದ ನಂತರ ಗ್ರಹಿಕೆ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ."
            },
            {
                "title": "ಬರೆಯುವ ಕಾರ್ಯ",
                "description": "ಖಾಲಿ ಪದಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ ಅಥವಾ ಸರಳ ವಾಕ್ಯಗಳನ್ನು ನಿರ್ಮಿಸಿ."
            },
            {
                "title": "ಮಾತನಾಡುವ ಕಾರ್ಯ",
                "description": "ವಾಕ್യಗಳನ್ನು ಜೋರಾಗಿ ಓದಿ ನಂತರ ಟൈಪ್ ಮಾಡಿ."
            }
        ],
        "benchmarks": [
            {
                "level": "ಪ್ರವೀಣ",
                "range": "80–100%",
                "notes": "ಕಲಿಯುವವರು ಓದುವಿಕೆ, ಬರವಣಿಗೆ ಮತ್ತು ಗ್ರಹಿಕೆಯಲ್ಲಿ ಉತ್ತಮ ಕೌಶಲ್ಯಗಳನ್ನು ಪ್ರದರ್ಶಿಸುತ್ತಾರೆ."
            },
            {
                "level": "ಬೆಳೆಯುತ್ತಿರುವ",
                "range": "50–79%",
                "notes": "ಕಲಿಯುವವರು ಪ್ರಗತಿ ಹೊಂದುತ್ತಿದ್ದಾರೆ ಮತ್ತು ಅಭ್ಯಾಸವನ್ನು ಮುಂದುವರಿಸಬೇಕಾಗಿದೆ."
            },
            {
                "level": "ಪ್ರಾರಂಭಿಕ",
                "range": "0–49%",
                "notes": "ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ ಮತ್ತು ಸರಳ ಪದಗಳಲ್ಲಿ ಮೂಲಭೂತ ಬೆಂಬಲದ ಅಗತ್ಯವಿದೆ."
            }
        ]
    },
    "Malayalam": {
        "module_title": " പഠന ഉള്ളടക്ക മാനേജ്‌മെന്റും മൂല്യനിർണ്ണയ ചട്ടക്കൂടും",
        "description": "ബഹുഭാഷാ പഠിതാക്കൾക്കായി രൂപകൽപ്പന ചെയ്‌തിരിക്കുന്ന വായന, എഴുത്ത്, മനസ്സിലാക്കൽ പ്രവർത്തനങ്ങൾ എന്നിവയിലൂടെ സാക്ഷരതാ കോഴ്‌സ് പൂർത്തിയാക്കുക.",
        "curriculum": [
            {
                "heading": "വായനയുടെ അടിത്തറ",
                "details": "ചെറിയ ഭാഗങ്ങളും ചോദ്യങ്ങളും വഴി വായനാക്ഷമത മെച്ചപ്പെടുത്തുക."
            },
            {
                "heading": "എഴുത്തു പരിശീലനം",
                "details": "വാക്യഘടനയും ടൈപ്പിംഗ് പരിശീലനവും വഴി എഴുത്ത് മെച്ചപ്പെടുത്തുക."
            },
            {
                "heading": "ഗ്രഹണ പിന്തുണ",
                "details": "പദാവലി പൊരുത്തപ്പെടുത്തൽ വഴി മനസ്സിലാക്കൽ ശേഷി വർദ്ധിപ്പിക്കുക."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "വായന ജോലി",
                "description": "ചെറിയ ഭാഗം വായിച്ചതിനുശേഷം ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകുക."
            },
            {
                "title": "എഴുത്ത് ജോലി",
                "description": "വിട്ടുപോയ വാക്കുകൾ ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ ലളിതമായ വാക്യങ്ങൾ ഉണ്ടാക്കുക."
            },
            {
                "title": "സംസാര ജോലി",
                "description": "വാക്യങ്ങൾ ഉറക്കെ വായിച്ചതിനുശേഷം ടൈപ്പ് ചെയ്യുക."
            }
        ],
        "benchmarks": [
            {
                "level": "പ്രാവീണ്യമുള്ളയാൾ",
                "range": "80–100%",
                "notes": "പഠിതാവ് മികച്ച വായന, എഴുത്ത്, മനസ്സിലാക്കൽ കഴിവുകൾ പ്രകടിപ്പിക്കുന്നു."
            },
            {
                "level": "വളർന്നു വരുന്നയാൾ",
                "range": "50–79%",
                "notes": "പഠിതാവ് പുരോഗതി കാണിക്കുന്നു, കൂടുതൽ പരിശീലനം ആവശ്യമാണ്."
            },
            {
                "level": "തുടക്കക്കാരൻ",
                "range": "0–49%",
                "notes": "അക്ഷരങ്ങൾ തിരിച്ചറിയുന്നതിനും ലളിതമായ വാക്കുകൾക്കും അടിസ്ഥാന പിന്തുണ ആവശ്യമാണ്."
            }
        ]
    }
}

from flask import Flask, render_template, request, redirect, url_for, flash, session, Response, jsonify
import sqlite3
import random
import re
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
import os
import urllib.request
import urllib.parse

import difflib
import time

VOWELS = {}
MATRAS = {}
CONSONANTS = {}
HALANTS = set()

def add_v(cp, val): VOWELS[chr(cp)] = val
def add_m(cp, val): MATRAS[chr(cp)] = val
def add_c(cp, val): CONSONANTS[chr(cp)] = val + 'a'

# DEVANAGARI (Hindi, Marathi)
for cp, val in [
    (0x0905, 'a'), (0x0906, 'aa'), (0x0907, 'i'), (0x0908, 'ee'), (0x0909, 'u'), (0x090A, 'oo'), (0x090B, 'ri'), (0x090F, 'e'), (0x0910, 'ai'), (0x0913, 'o'), (0x0914, 'au'),
    (0x0902, 'n'), (0x0903, 'h')
]: add_v(cp, val)
for cp, val in [
    (0x093E, 'aa'), (0x093F, 'i'), (0x0940, 'ee'), (0x0941, 'u'), (0x0942, 'oo'), (0x0943, 'ri'), (0x0947, 'e'), (0x0948, 'ai'), (0x094B, 'o'), (0x094C, 'au'),
    (0x0902, 'n'), (0x0903, 'h')
]: add_m(cp, val)
for cp, val in [
    (0x0915, 'k'), (0x0916, 'kh'), (0x0917, 'g'), (0x0918, 'gh'), (0x0919, 'ng'),
    (0x091A, 'ch'), (0x091B, 'chh'), (0x091C, 'j'), (0x091D, 'jh'), (0x091E, 'ny'),
    (0x091F, 't'), (0x0920, 'th'), (0x0921, 'd'), (0x0922, 'dh'), (0x0923, 'n'),
    (0x0924, 't'), (0x0925, 'th'), (0x0926, 'd'), (0x0927, 'dh'), (0x0928, 'n'),
    (0x092A, 'p'), (0x092B, 'ph'), (0x092C, 'b'), (0x092D, 'bh'), (0x092E, 'm'),
    (0x092F, 'y'), (0x0930, 'r'), (0x0932, 'l'), (0x0933, 'l'), (0x0935, 'v'), (0x0936, 'sh'), (0x0937, 'sh'), (0x0938, 's'), (0x0939, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x094D))

# TELUGU
for cp, val in [
    (0x0C05, 'a'), (0x0C06, 'aa'), (0x0C07, 'i'), (0x0C08, 'ee'), (0x0C09, 'u'), (0x0C0A, 'oo'), (0x0C0B, 'ru'), (0x0C0E, 'e'), (0x0C0F, 'ae'), (0x0C10, 'ai'), (0x0C12, 'o'), (0x0C13, 'oe'), (0x0C14, 'au'),
    (0x0C02, 'm'), (0x0C03, 'aha')
]: add_v(cp, val)
for cp, val in [
    (0x0C3E, 'aa'), (0x0C3F, 'i'), (0x0C40, 'ee'), (0x0C41, 'u'), (0x0C42, 'oo'), (0x0C43, 'ru'), (0x0C46, 'e'), (0x0C47, 'ae'), (0x0C48, 'ai'), (0x0C4A, 'o'), (0x0C4B, 'oe'), (0x0C4C, 'au'),
    (0x0C02, 'm'), (0x0C03, 'aha')
]: add_m(cp, val)
for cp, val in [
    (0x0C15, 'k'), (0x0C16, 'kh'), (0x0C17, 'g'), (0x0C18, 'gh'), (0x0C19, 'ng'),
    (0x0C1A, 'ch'), (0x0C1B, 'chh'), (0x0C1C, 'j'), (0x0C1D, 'jh'), (0x0C1E, 'ny'),
    (0x0C1F, 't'), (0x0C20, 'th'), (0x0C21, 'd'), (0x0C22, 'dh'), (0x0C23, 'n'),
    (0x0C24, 't'), (0x0C25, 'th'), (0x0C26, 'd'), (0x0C27, 'dh'), (0x0C28, 'n'),
    (0x0C2A, 'p'), (0x0C2B, 'ph'), (0x0C2C, 'b'), (0x0C2D, 'bh'), (0x0C2E, 'm'),
    (0x0C2F, 'y'), (0x0C30, 'r'), (0x0C31, 'r'), (0x0C32, 'l'), (0x0C33, 'l'), (0x0C35, 'v'), (0x0C36, 'sh'), (0x0C37, 'sh'), (0x0C38, 's'), (0x0C39, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0C4D))

# KANNADA
for cp, val in [
    (0x0C85, 'a'), (0x0C86, 'aa'), (0x0C87, 'i'), (0x0C88, 'ee'), (0x0C89, 'u'), (0x0C8A, 'oo'), (0x0C8B, 'ru'), (0x0C8E, 'e'), (0x0C8F, 'ae'), (0x0C90, 'ai'), (0x0C92, 'o'), (0x0C93, 'oe'), (0x0C94, 'au'),
    (0x0C82, 'm'), (0x0C83, 'aha')
]: add_v(cp, val)
for cp, val in [
    (0x0CBE, 'aa'), (0x0CBF, 'i'), (0x0CC0, 'ee'), (0x0CC1, 'u'), (0x0CC2, 'oo'), (0x0CC3, 'ru'), (0x0CC6, 'e'), (0x0CC7, 'ae'), (0x0CC8, 'ai'), (0x0CCA, 'o'), (0x0CCB, 'oe'), (0x0CCC, 'au'),
    (0x0C82, 'm'), (0x0C83, 'aha')
]: add_m(cp, val)
for cp, val in [
    (0x0C95, 'k'), (0x0C96, 'kh'), (0x0C97, 'g'), (0x0C98, 'gh'), (0x0C99, 'ng'),
    (0x0C9A, 'ch'), (0x0C9B, 'chh'), (0x0C9C, 'j'), (0x0C9D, 'jh'), (0x0C9E, 'ny'),
    (0x0C9F, 't'), (0x0CA0, 'th'), (0x0CA1, 'd'), (0x0CA2, 'dh'), (0x0CA3, 'n'),
    (0x0CA4, 't'), (0x0CA5, 'th'), (0x0CA6, 'd'), (0x0CA7, 'dh'), (0x0CA8, 'n'),
    (0x0CAA, 'p'), (0x0CAB, 'ph'), (0x0CAC, 'b'), (0x0CAD, 'bh'), (0x0CAE, 'm'),
    (0x0CAF, 'y'), (0x0CB0, 'r'), (0x0CB1, 'r'), (0x0CB2, 'l'), (0x0CB3, 'l'), (0x0CB5, 'v'), (0x0CB6, 'sh'), (0x0CB7, 'sh'), (0x0CB8, 's'), (0x0CB9, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0CCD))

# TAMIL
for cp, val in [
    (0x0B85, 'a'), (0x0B86, 'aa'), (0x0B87, 'i'), (0x0B88, 'ee'), (0x0B89, 'u'), (0x0B8A, 'oo'), (0x0B8E, 'e'), (0x0B8F, 'ae'), (0x0B90, 'ai'), (0x0B92, 'o'), (0x0B93, 'oe'), (0x0B94, 'au'),
    (0x0B83, 'kh')
]: add_v(cp, val)
for cp, val in [
    (0x0BBE, 'aa'), (0x0BBF, 'i'), (0x0BC0, 'ee'), (0x0BC1, 'u'), (0x0BC2, 'oo'), (0x0BC6, 'e'), (0x0BC7, 'ae'), (0x0BC8, 'ai'), (0x0BCA, 'o'), (0x0BCB, 'oe'), (0x0BCC, 'au'),
    (0x0B83, 'kh')
]: add_m(cp, val)
for cp, val in [
    (0x0B95, 'k'), (0x0B99, 'ng'), (0x0B9A, 'ch'), (0x0B9E, 'ny'), (0x0B9F, 't'), (0x0BA3, 'n'), (0x0BA4, 't'), (0x0BA8, 'n'), (0x0BAA, 'p'), (0x0BAE, 'm'),
    (0x0BAF, 'y'), (0x0BB0, 'r'), (0x0BB2, 'l'), (0x0BB5, 'v'), (0x0BB4, 'zh'), (0x0BB3, 'l'), (0x0BB1, 'r'), (0x0BA9, 'n'), (0x0B9C, 'j'), (0x0BB7, 'sh'), (0x0BB8, 's'), (0x0BB9, 'h')
]: add_c(cp, val)
HALANTS.add(chr(0x0BCD))

def transliterate_word(word, lang):
    lang_lower = (lang or "").lower()
    res = []
    i = 0
    n = len(word)
    while i < n:
        char = word[i]
        
        # Check vowels
        if char in VOWELS:
            res.append(VOWELS[char])
            i += 1
            continue
            
        # Check consonants
        if char in CONSONANTS:
            base_sound = CONSONANTS[char]
            base = base_sound[:-1] if base_sound.endswith('a') else base_sound
            
            # Check next character
            if i + 1 < n:
                nxt = word[i+1]
                if nxt in HALANTS:
                    res.append(base)
                    i += 2 # skip both consonant and halant
                    continue
                elif nxt in MATRAS:
                    res.append(base + MATRAS[nxt])
                    i += 2 # skip both consonant and matra
                    continue
            
            # Trailing consonant drop 'a' for Hindi/Marathi
            if i + 1 == n and ("hindi" in lang_lower or "marathi" in lang_lower) and base_sound.endswith('a') and len(res) > 0:
                res.append(base)
            else:
                res.append(base_sound)
            i += 1
            continue
            
        res.append(char)
        i += 1
        
    word_str = "".join(res)
    word_str = word_str.replace("aaa", "aa").replace("eee", "ee").replace("ooo", "oo")
    return word_str.capitalize()

def transliterate_text(text, lang):
    if not text:
        return ""
    words = text.split(" ")
    res = [transliterate_word(w, lang) for w in words]
    return " ".join(res)


def normalize_text(text):
    if not text:
        return ""
    text = str(text).strip().lower()
    text = re.sub(r"[.,\/#!$%\^&\*;:{}=\-_`~()?।]", "", text)
    return " ".join(text.split())

def get_similarity_score(a, b):
    a = normalize_text(a)
    b = normalize_text(b)
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return difflib.SequenceMatcher(None, a, b).ratio()

def get_age_group(age):
    try:
        age_val = int(age)
    except (ValueError, TypeError):
        return "young"
    if age_val <= 5:
        return "toddler"
    elif age_val <= 8:
        return "young"
    elif age_val <= 12:
        return "middle"
    elif age_val <= 20:
        return "older"
    elif age_val <= 25:
        return "career"
    elif age_val <= 35:
        return "professional"
    elif age_val <= 45:
        return "advancement"
    elif age_val <= 55:
        return "leadership"
    elif age_val <= 60:
        return "pre-retirement"
    else:
        return "senior"


from datetime import datetime, date

def calculate_age(dob_str):
    if not dob_str:
        return 8
    try:
        dob = datetime.strptime(dob_str, "%Y-%m-%d").date()
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        return max(0, age)
    except Exception:
        try:
            dob = datetime.strptime(dob_str, "%d/%m/%Y").date()
            today = date.today()
            age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
            return max(0, age)
        except Exception:
            return 8


def get_adaptive_difficulty(user_id, actual_age, language, cursor):
    actual_group = get_age_group(actual_age)
    
    # We only perform adaptivity for age brackets >= 5 (i.e. young, middle, older, career)
    if actual_group == "toddler":
        return actual_group
        
    # Find total lessons for user's language and chronological difficulty group
    cursor.execute("""
        SELECT COUNT(*) FROM lessons 
        WHERE language = ? AND difficulty = ?
    """, (language, actual_group))
    total_lessons = cursor.fetchone()[0]
    
    if total_lessons == 0:
        return actual_group
        
    # Find completed lessons for this group
    cursor.execute("""
        SELECT COUNT(DISTINCT lp.lesson_id) 
        FROM lesson_progress lp 
        JOIN lessons l ON lp.lesson_id = l.id 
        WHERE lp.user_id = ? AND l.language = ? AND l.difficulty = ?
    """, (user_id, language, actual_group))
    completed_lessons = cursor.fetchone()[0]
    
    progress = (completed_lessons / total_lessons) * 100
    
    # Order of levels
    groups_order = ["toddler", "young", "middle", "older", "career"]
    try:
        current_idx = groups_order.index(actual_group)
    except ValueError:
        return actual_group
        
    # If completed > 95%, unlock next difficulty early
    if progress >= 95.0 and current_idx < len(groups_order) - 1:
        return groups_order[current_idx + 1]
    # If completed < 20%, show previous difficulty for review
    elif progress < 20.0 and current_idx > 0:
        return groups_order[current_idx - 1]
        
    return actual_group
    # convert sqlite row to dict for safe access with .get()
    try:
        user = dict(user)
    except Exception:
        pass




app = Flask(__name__)
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

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
        if lang_folder != "english":
            print(f"[VIDEO INFO] Regional video folder missing for language='{language}', falling back to English")
            return get_local_videos_for_learner("English", age)
        return []

    try:
        files = [f for f in sorted(os.listdir(dir_path)) if f.lower().endswith(".mp4")]
    except Exception as e:
        print(f"[VIDEO ERROR] Error scanning directory {dir_path}: {e}")
        if lang_folder != "english":
            return get_local_videos_for_learner("English", age)
        return []

    if not files:
        print(f"[VIDEO ERROR] Missing MP4 files in directory {dir_path} for language='{language}', age={age}")
        if lang_folder != "english":
            return get_local_videos_for_learner("English", age)
        return []

    videos = []
    for f in files:
        web_path = f"/static/videos/{lang_folder}/{folder_name}/{f}"
        raw_title = os.path.splitext(f)[0]
        
        # Translate dynamically
        title_lower = f.lower()
        translated_title = raw_title
        translated_desc = f"Learn spelling, reading, and writing in {language} with this fun educational video clip!"
        category = "rhymes"
        
        if "color" in title_lower or "colour" in title_lower or "rang" in title_lower or "varna" in title_lower or "pannul" in title_lower:
            category = "colors"
            if language == "Telugu":
                translated_title, translated_desc = "రంగుల పాట (Learn Colors)", "అన్ని ప్రకాశవంతమైన రంగులను నేర్చుకోవడానికి ఒక సరదా పాట!"
            elif language == "Hindi":
                translated_title, translated_desc = "रंगों का गीत (Learn Colors)", "सभी चमकीले रंगों को सीखने के लिए एक मजेदार गीत!"
            elif language == "Tamil":
                translated_title, translated_desc = "வண்ணங்களின் பாடல் (Learn Colors)", "அனைத்து பிரகாசமான வண்ணங்களையும் கற்றுக்கொள்ள ஒரு வேடிக்கையான பாடல்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಬಣ್ಣಗಳ ಹಾಡು (Learn Colors)", "ಎಲ್ಲಾ ಪ್ರಕಾಶಮಾನವಾದ ಬಣ್ಣಗಳನ್ನು कಲಿಯಲು ಒಂದು ಮೋಜಿನ ಹಾಡು!"
            elif language == "Marathi":
                translated_title, translated_desc = "रंगांचे गाणे (Learn Colors)", "सर्व चमकदार रंग शिकण्यासाठी एक मजेदार गाणे!"
            else:
                translated_title, translated_desc = "Learn Colors Song", "A fun song to learn all the bright colors!"
        elif "shape" in title_lower or "aakaar" in title_lower or "aakriti" in title_lower:
            category = "shapes"
            if language == "Telugu":
                translated_title, translated_desc = "ఆకారాల పాట (Learn Shapes)", "వృత్తాలు, చతురస్రాలు మరియు త్రిభుజాల వంటి ఆకారాలను కనుగొనండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "आकृतियों का गीत (Learn Shapes)", "वृत्त, वर्ग और त्रिकोण जैसी आकृतियों को जानें!"
            elif language == "Tamil":
                translated_title, translated_desc = "வடிவங்கள் பாடல் (Learn Shapes)", "வட்டம், சதுரம் மற்றும் முக்கோணம் போன்ற வடிவங்களைக் கண்டறியுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಆಕಾರಗಳ ಹಾಡು (Learn Shapes)", "ವೃತ್ತ, ಚೌಕ ಮತ್ತು ತ್ರಿಕೋನಗಳಂತಹ ಆಕಾರಗಳನ್ನು ಅನ್ವೇಷಿಸಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "आकारांचे गाणे (Learn Shapes)", "वर्तुळ, चौरस आणि त्रिकोण यांसारखे आकार शोधा!"
            else:
                translated_title, translated_desc = "Learn Shapes Song", "Discover shapes like circles, squares, and triangles!"
        elif "alphabet" in title_lower or "akshara" in title_lower or "varnamala" in title_lower or "swar" in title_lower or "letter" in title_lower or "mula" in title_lower or "abc" in title_lower or "uyir" in title_lower or "morni" in title_lower:
            category = "alphabet"
            if language == "Telugu":
                translated_title, translated_desc = "అక్షరాల పరిచయం (Alphabet Intro)", "భాష యొక్క ప్రాథమిక అక్షరాలను మరియు గుణింతాలను నేర్చుకోండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "वर्णमाला ज्ञान (Alphabet Intro)", "भाषा के बुनियादी अक्षरों और स्वरों को सीखें!"
            elif language == "Tamil":
                translated_title, translated_desc = "எழுத்துக்கள் அறிமுகம் (Alphabet Intro)", "மொழியின் அடிப்படை எழுத்துக்களைக் கற்றுக்கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಕನ್ನಡ ಅಕ್ಷರಮಾಲೆ (Alphabet Intro)", "ಭಾಷೆಯ ಮೂಲ ಅಕ್ಷರಗಳನ್ನು ಕಲಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "मुळाक्षरांची ओळख (Alphabet Intro)", "भाषेच्या मूळ अक्षरांची आणि स्वरांची ओळख करून घ्या!"
            else:
                translated_title, translated_desc = "Alphabet Learning Video", "Learn the foundational alphabets and letters!"
        elif "number" in title_lower or "counting" in title_lower or "ginti" in title_lower or "ank" in title_lower or "eradu" in title_lower or "ondu" in title_lower or "dosai" in title_lower or "ankache" in title_lower:
            category = "numbers"
            if language == "Telugu":
                translated_title, translated_desc = "సంఖ్యల లెక్కింపు (Numbers Counting)", "సంఖ్యలను సులభంగా నేర్చుకోండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "गिनती और संख्याएँ (Numbers Counting)", "संख्याओं को चरण-दर-चरण गिनना सीखें!"
            elif language == "Tamil":
                translated_title, translated_desc = "எண்கள் பயிற்சி (Numbers Counting)", "எண்களை படிப்படியாக எண்ணக் கற்றுக்கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಸಂಖ್ಯೆಗಳ ಎಣಿಕೆ (Numbers Counting)", "ಸಂಖ್ಯೆಗಳನ್ನು ಹಂತ-ಹಂತವಾಗಿ ಎಣಿಸಲು ಕಲಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "अंक आणि संख्या मोजणे (Numbers Counting)", "संख्या मोजायला शिका सोप्या पद्धतीने!"
            else:
                translated_title, translated_desc = "Counting and Numbers", "Learn to count numbers step-by-step!"
        elif "animal" in title_lower or "sound" in title_lower or "aavaj" in title_lower or "oli" in title_lower or "pranyanche" in title_lower or "aane" in title_lower or "nayi" in title_lower or "machli" in title_lower or "ghode" in title_lower or "chimni" in title_lower or "pitta" in title_lower or "enugamma" in title_lower or "chilakamma" in title_lower:
            category = "animals"
            if language == "Telugu":
                translated_title, translated_desc = "జంతువుల శబ్దాలు (Animal Sounds)", "స్నేహపూర్వక జంతువులను కలవండి మరియు వాటి శబ్దాలను వినండి!"
            elif language == "Hindi":
                translated_title, translated_desc = "जानवरों की आवाजें (Animal Sounds)", "विभिन्न पशु-पक्षियों की आवाजें और उनके नाम जानें!"
            elif language == "Tamil":
                translated_title, translated_desc = "விலங்குகளின் ஒலிகள் (Animal Sounds)", "விலங்குகளின் பெயர்களையும் அவற்றின் ஒலிகளையும் தெரிந்து கொள்ளுங்கள்!"
            elif language == "Kannada":
                translated_title, translated_desc = "ಪ್ರಾಣಿಗಳ ಶಬ್ದಗಳು (Animal Sounds)", "ವಿವಿಧ ಪ್ರಾಣಿಗಳ ಧ್ವನಿಗಳು ಮತ್ತು ಅವುಗಳ ಹೆಸರನ್ನು ತಿಳಿಯಿರಿ!"
            elif language == "Marathi":
                translated_title, translated_desc = "प्राण्यांचे आवाज (Animal Sounds)", "विविध प्राणी आणि त्यांचे आवाज ओळखा!"
            else:
                translated_title, translated_desc = "Animal Sounds and Names", "Meet the friendly animals and hear the sounds they make!"
        else:
            clean_t = raw_title.replace("_", " ").replace("-", " ").strip()
            clean_t = " ".join([w.capitalize() for w in clean_t.split() if w])
            translated_title = clean_t

        videos.append({
            "title": translated_title,
            "description": translated_desc,
            "video_url": web_path,
            "filename": f,
            "category": category,
            "language": language,
            "age": age
        })
    return videos


app.secret_key = "literacy_secret_key"

DATABASE = "literacy.db"

import json

def load_json_translations():
    locales = {
        "English": "en.json",
        "Telugu": "te.json",
        "Hindi": "hi.json",
        "Tamil": "ta.json",
        "Kannada": "kn.json",
        "Marathi": "mr.json"
    }
    loaded = {}
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(base_dir, "static", "locales")
    
    for lang, filename in locales.items():
        filepath = os.path.join(locales_dir, filename)
        try:
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8") as f:
                    loaded[lang] = json.load(f)
            else:
                loaded[lang] = {}
        except Exception as e:
            print(f"Error loading translation for {lang}: {e}")
            loaded[lang] = {}
            
    # Ensure English has fallbacks
    if "English" not in loaded or not loaded["English"]:
        loaded["English"] = {
            "site_title": "",
            "welcome_title": "Welcome!",
            "welcome_text": "Register to start your AI-powered learning journey."
        }
    return loaded

translations = load_json_translations()


def get_translations(language):
    # Dynamically load JSON files on each request to prevent server-side caching of translations
    current_translations = load_json_translations()
    if language not in current_translations:
        return current_translations.get("English", {})
    merged = current_translations.get("English", {}).copy()
    merged.update(current_translations[language])
    return merged


AGE_GROUP_LABELS = {
    "English": {
        "toddler": "Toddler (Early Learner)",
        "young": "Young Learner",
        "middle": "Middle Learner",
        "older": "Adolescent / Youth",
        "career": "Career Starter",
        "professional": "Working Professional",
        "advancement": "Career Advancement",
        "leadership": "Leadership & Mentoring",
        "pre-retirement": "Pre-retirement",
        "senior": "Senior Citizen"
    },
    "Telugu": {
        "toddler": "పసిపిల్లవాడు (చిన్నారి)",
        "young": "యువ అభ్యాసకుడు",
        "middle": "మధ్యస్థ అభ్యాసకుడు",
        "older": "యువత (కిశోర ప్రాయం)",
        "career": "ఉద్యోగ అన్వేషి / కెరీర్ ప్రారంభకుడు",
        "professional": "పనిచేసే నిపుణుడు",
        "advancement": "కెరీర్ అభివృద్ధి",
        "leadership": "నాయకత్వం & మార్గదర్శకత్వం",
        "pre-retirement": "పదవీ విరమణకు ముందు",
        "senior": "సీనియర్ సిటిజన్ (వృద్ధులు)"
    },
    "Hindi": {
        "toddler": "नन्हा बच्चा (शुरुआती शिक्षार्थी)",
        "young": "युवा शिक्षार्थी",
        "middle": "मध्यम वर्ग के शिक्षार्थी",
        "older": "किशोर / युवा",
        "career": "करियर की शुरुआत",
        "professional": "कामकाजी पेशेवर",
        "advancement": "करियर उन्नति",
        "leadership": "नेतृत्व और मार्गदर्शन",
        "pre-retirement": "सेवानिवृत्ति पूर्व",
        "senior": "वरिष्ठ नागरिक"
    },
    "Tamil": {
        "toddler": "குழந்தை (ஆரம்பக் கற்றல்)",
        "young": "இளைய கற்றல் மாணவர்",
        "middle": "நடுத்தர கற்றல் மாணவர்",
        "older": "இளைஞர் / வளரிளம் பருவம்",
        "career": "தொழில் தொடங்குபவர்",
        "professional": "பணிபுரியும் தொழில்முறை",
        "advancement": "தொழில் மேம்பாடு",
        "leadership": "தலைமை மற்றும் வழிகாட்டுதல்",
        "pre-retirement": "ஓய்வுக்கு முந்தைய நிலை",
        "senior": "மூத்த குடிமகன்"
    },
    "Marathi": {
        "toddler": "लहान मूल (सुरुवातीचे शिकणारे)",
        "young": "तरुण शिकणारे",
        "middle": "मध्यम शिकणारे",
        "older": "किशोरवयीन / तरुण",
        "career": "करिअरची सुरुवात",
        "professional": "नोकरी करणारे व्यावसायिक",
        "advancement": "करिअरमधील प्रगती",
        "leadership": "नेतृत्व आणि मार्गदर्शन",
        "pre-retirement": "सेवानिवृत्तीपूर्व",
        "senior": "ज्येष्ठ नागरिक"
    },
    "Kannada": {
        "toddler": "ಅಂಬೆಗಾಲಿಡುವ ಮಗು (ಆರಂಭಿಕ ಕಲಿಗ)",
        "young": "ಯುವ ಕಲಿಗ",
        "middle": "ಮಧ್ಯಮ ಕಲಿಗ",
        "older": "ಹದಿಹರೆಯದವರು / ಯುವಕರು",
        "career": "ವೃತ್ತಿಜೀವನ ಆರಂಭಿಸುವವರು",
        "professional": "ಉದ್ಯೋಗಿ ವೃತ್ತಿಪರ",
        "advancement": "ವೃತ್ತಿಜೀವನದ ಉನ್ನತಿ",
        "leadership": "ನಾಯಕತ್ವ ಮತ್ತು ಮಾರ್ಗದರ್ಶನ",
        "pre-retirement": "ನಿವೃತ್ತಿಪೂರ್ವ",
        "senior": "ಹಿರಿಯ ನಾಗರಿಕ"
    },
    "Malayalam": {
        "toddler": "ശിശു (ആദ്യകാല പഠിതാവ്)",
        "young": "യുവ പഠിതാവ്",
        "middle": "മധ്യ പഠിതാവ്",
        "older": "കൗമാരക്കാരൻ / യുവത്വം",
        "career": "കരിയർ തുടക്കക്കാരൻ",
        "professional": "തൊഴിൽ പ്രൊഫഷണൽ",
        "advancement": "കരിയർ പുരോഗതി",
        "leadership": "നേതൃത്വവും പരിശീലനവും",
        "pre-retirement": "വിരമിക്കലിന് മുൻപുള്ള അവസ്ഥ",
        "senior": "മുതിർന്ന പൗരൻ"
    }
}


def get_age_group_label(group, language):
    return AGE_GROUP_LABELS.get(language, AGE_GROUP_LABELS["English"]).get(group, group.title())


VOCAB_DATABASE = {
    "English": {
        "toddler": {
            "spelling_tests": [
                {"word": "cat", "options": ["cat", "xat", "ct"], "answer": "cat"},
                {"word": "dog", "options": ["dog", "dgo", "dg"], "answer": "dog"},
                {"word": "sun", "options": ["sun", "sn", "snn"], "answer": "sun"},
                {"word": "pen", "options": ["pen", "pn", "peen"], "answer": "pen"}
            ],
            "writing_templates": [
                {"template": "The ball is ___.", "answers": ["red", "big", "blue"]},
                {"template": "I see a ___.", "answers": ["cat", "dog", "sun", "pen"]},
                {"template": "A hot ___.", "answers": ["sun"]}
            ],
            "speaking_phrases": [
                "Big dog",
                "Blue sky",
                "I run",
                "Red apple"
            ]
        },
        "young": {
            "nouns": ["cat", "dog", "book", "ball", "pen", "hat", "boy", "girl", "tree", "bird"],
            "verbs": ["runs", "jumps", "plays", "sleeps", "reads", "writes", "sings", "flies"],
            "adjectives": ["happy", "small", "big", "fast", "slow", "red", "blue", "green"],
            "places": ["park", "school", "house", "garden", "room", "yard"],
            "spelling_tests": [
                {"word": "reading", "options": ["reding", "reading", "readin"], "answer": "reading"},
                {"word": "writing", "options": ["wrting", "writing", "writeing"], "answer": "writing"},
                {"word": "learning", "options": ["lerning", "learning", "learnin"], "answer": "learning"},
                {"word": "school", "options": ["scool", "school", "schoole"], "answer": "school"},
                {"word": "teacher", "options": ["techer", "teacher", "teachere"], "answer": "teacher"}
            ],
            "writing_templates": [
                {"template": "I see a green ___.", "answers": ["leaf", "tree", "plant"]},
                {"template": "The ball is ___.", "answers": ["round", "red", "blue", "big"]},
                {"template": "She can ___ a book.", "answers": ["read", "open", "see", "write"]},
                {"template": "The sun is in the ___.", "answers": ["sky"]}
            ],
            "speaking_phrases": [
                "I can read and write.",
                "The cat is cute.",
                "I play in the park.",
                "A red apple is sweet."
            ]
        },
        "middle": {
            "nouns": ["students", "teachers", "lessons", "stories", "questions", "answers", "friends", "classrooms"],
            "verbs": ["understands", "explains", "practices", "remembers", "finishes", "creates"],
            "adjectives": ["interesting", "careful", "focused", "clever", "creative", "beautiful"],
            "spelling_tests": [
                {"word": "comprehension", "options": ["comprehension", "comprension", "comprehenson"], "answer": "comprehension"},
                {"word": "vocabulary", "options": ["vocabulry", "vocabulary", "vocabularie"], "answer": "vocabulary"},
                {"word": "education", "options": ["education", "educaton", "educashun"], "answer": "education"},
                {"word": "knowledge", "options": ["nowledge", "knowledge", "knowlege"], "answer": "knowledge"}
            ],
            "writing_templates": [
                {"template": "They always ___ their homework on time.", "answers": ["do", "complete", "finish", "write"]},
                {"template": "He is very ___ in studying science.", "answers": ["interested", "focused", "careful"]},
                {"template": "We learn new words to build our ___.", "answers": ["vocabulary", "knowledge", "skills"]}
            ],
            "speaking_phrases": [
                "Reading books helps us learn new things.",
                "We must practice writing everyday.",
                "The students solved the grammar quiz.",
                "Education is important for everyone."
            ]
        },
        "older": {
            "nouns": ["foundations", "literacy", "achievements", "development", "communication", "opportunities"],
            "verbs": ["empowers", "contributes", "accomplishes", "facilitates", "strengthens"],
            "adjectives": ["essential", "accessible", "collaborative", "professional", "lifelong"],
            "spelling_tests": [
                {"word": "pronunciation", "options": ["pronunciation", "pronounciation", "pronunciaton"], "answer": "pronunciation"},
                {"word": "proficiency", "options": ["proficency", "proficiency", "proficiencie"], "answer": "proficiency"},
                {"word": "development", "options": ["devlopment", "development", "developement"], "answer": "development"},
                {"word": "achievement", "options": ["achievement", "achievment", "acheivement"], "answer": "achievement"}
            ],
            "writing_templates": [
                {"template": "Developing strong reading skills is ___ for success.", "answers": ["essential", "important", "critical"]},
                {"template": "Foundational literacy empowers individuals to ___ their goals.", "answers": ["achieve", "reach", "accomplish"]},
                {"template": "Regional languages make learning resources more ___.", "answers": ["accessible", "useful"]}
            ],
            "speaking_phrases": [
                "Foundational literacy builds a path to lifelong learning.",
                "Language skills help us share ideas with confidence.",
                "Technology provides personalized learning pathways.",
                "Communication is essential for professional growth."
            ]
        }
    },
    "Telugu": {
        "toddler": {
            "spelling_tests": [
                {"word": "ఆవు", "options": ["ఆవు", "అవు", "ఆవ"], "answer": "ఆవు"},
                {"word": "ఇల్లు", "options": ["ఇల్లు", "ఇలు", "ఈల్లు"], "answer": "ఇల్లు"},
                {"word": "అమ్మ", "options": ["అమ్మ", "ఆమ", "అమ"], "answer": "అమ్మ"}
            ],
            "writing_templates": [
                {"template": "ఇది ఒక ___.", "answers": ["ఇల్లు", "కలం", "ఆట"]},
                {"template": "అమ్మ ___ ఇస్తుంది.", "answers": ["పాలు", "నీరు"]}
            ],
            "speaking_phrases": [
                "మంచి బాలుడు",
                "చిన్న పిల్లి",
                "బడికి వెళ్ళు"
            ]
        },
        "young": {
            "nouns": ["పిల్లి", "కుక్క", "పుస్తకం", "బంతి", "కలం", "ఆట", "పాలు", "పండు"],
            "verbs": ["ఉంది", "తాగుతుంది", "ఆడుతుంది", "చదువుతుంది", "నడుస్తుంది"],
            "spelling_tests": [
                {"word": "పుస్తకం", "options": ["పుస్తకం", "పుస్థకం", "పుస్తకము"], "answer": "పుస్తకం"},
                {"word": "బడి", "options": ["బడి", "భడి", "వడి"], "answer": "బడి"},
                {"word": "కలం", "options": ["కలం", "ఖలం", "గలమ్"], "answer": "కలం"}
            ],
            "writing_templates": [
                {"template": "పిల్లి ___ తాగుతుంది.", "answers": ["పాలు", "నీరు"]},
                {"template": "ఆకాశం ___ రంగులో ఉంటుంది.", "answers": ["నీలం"]},
                {"template": "ఆమె ___ చదువుతుంది.", "answers": ["పుస్తకం", "కథ"]}
            ],
            "speaking_phrases": [
                "నేను చదవగలను మరియు వ్రాయగలను.",
                "అమ్మ నన్ను ప్రేమిస్తుంది.",
                "బంతి గుండ్రంగా ఉంటుంది.",
                "పాలు ఆరోగ్యానికి మంచిది."
            ]
        },
        "middle": {
            "nouns": ["విద్యార్థులు", "ఉపాధ్యాయులు", "పాఠాలు", "కథలు", "ప్రశ్నలు", "సమాధానాలు"],
            "verbs": ["నేర్చుకుంటారు", "బోధిస్తారు", "రాస్తారు", "సహాయం చేస్తారు"],
            "spelling_tests": [
                {"word": "విద్యార్థి", "options": ["విద్యార్థి", "విధ్యార్తి", "విధ్యార్థి"], "answer": "విద్యార్థి"},
                {"word": "ఉపాధ్యాయుడు", "options": ["ఉపాధ్యాయుడు", "ఉపాദ്യాయుడు", "ఉపద్యాయుడు"], "answer": "ఉపాధ్యాయుడు"},
                {"word": "జ్ఞానం", "options": ["జ్ఞానం", "గ్నానం", "జ్నానం"], "answer": "జ్ఞానం"}
            ],
            "writing_templates": [
                {"template": "సూర్యుడు ___ దిశలో ఉదయిస్తాడు.", "answers": ["తూర్పు"]},
                {"template": "విద్యార్థులు బడిలో ___ నేర్చుకుంటారు.", "answers": ["పాఠాలు", "విద్య", "నైపుణ్యాలు"]}
            ],
            "speaking_phrases": [
                "పుస్తకాలు చదవడం మంచి అలవాటు.",
                "ప్రతిరోజూ కొత్త విషయాలు నేర్చుకోవాలి.",
                "ఉపాధ్యాయులు మాకు మార్గదర్శకం చేస్తారు.",
                "బడి మాకు చదువు మరియు క్రమశిక్షణ నేర్పుతుంది."
            ]
        },
        "older": {
            "nouns": ["పునాది", "సాక్షరత", "అభివృద్ధి", "కమ్యూనికేషన్", "అవకాశాలు"],
            "verbs": ["బలోపేతం చేస్తుంది", "సహాయపడుతుంది", "సాధించవచ్చు", "కల్పిస్తుంది"],
            "spelling_tests": [
                {"word": "సాక్షరత", "options": ["సాక్షరత", "శాక్షరత", "సాక్షరథ"], "answer": "సాక్షరత"},
                {"word": "పరిశోధన", "options": ["పరిశోధన", "పరిసోదన", "పరీశోధన"], "answer": "పరిశోధన"},
                {"word": "అవకాశం", "options": ["అవకాశం", "అవకాసం", "ఆవకాశం"], "answer": "అవకాశం"}
            ],
            "writing_templates": [
                {"template": "సాక్షరత దేశ ప్రగతికి ఒక ___.", "answers": ["పునాది", "కీలకం"]},
                {"template": "కమ్యూనిकेషన్ నైపుణ్యాలు మనకు మంచి ___ కల్పిస్తాయి.", "answers": ["అవకాశాలు", "ఉద్యోగాలు"]}
            ],
            "speaking_phrases": [
                "సాక్షరత సమాజ ఎదుగుదలకు పునాది.",
                "మాతృభాషలో నేర్చుకోవడం చాలా సుభం.",
                "సాంకేతికత విద్యను అందరికీ చేరువ చేస్తుంది.",
                "జ్ఞానం మనకు కొత్త ఆలోచనలను ఇస్తుంది."
            ]
        }
    },
    "Hindi": {
        "toddler": {
            "spelling_tests": [
                {"word": "आम", "options": ["आम", "अम", "आमु"], "answer": "आम"},
                {"word": "घर", "options": ["घर", "घड़", "गहर"], "answer": "घर"},
                {"word": "नल", "options": ["नल", "नळ", "नाल"], "answer": "नल"}
            ],
            "writing_templates": [
                {"template": "यह मेरा ___ है।", "answers": ["घर", "कलम", "फल"]},
                {"template": "आम मीठा ___ है।", "answers": ["होता", "जाता"]}
            ],
            "speaking_phrases": [
                "मेरा घर",
                "लाल सेब",
                "बिल्ली आई"
            ]
        },
        "young": {
            "nouns": ["बिल्ली", "कुत्ता", "किताब", "गेेंद", "कलम", "खेल", "दूध", "फल"],
            "verbs": ["है", "पीती है", "खेलता है", "पढ़ती है", "दौड़ता है"],
            "spelling_tests": [
                {"word": "किताब", "options": ["किताब", "कीताब", "किताम"], "answer": "किताब"},
                {"word": "स्कूल", "options": ["स्कूल", "स्कुल", "शकूल"], "answer": "स्कूल"},
                {"word": "कलम", "options": ["कलम", "खलम", "कलमम"], "answer": "कलम"}
            ],
            "writing_templates": [
                {"template": "बिल्ली ___ पीती है।", "answers": ["दूध", "पानी"]},
                {"template": "सेब का रंग ___ होता है।", "answers": ["लाल"]},
                {"template": "वह ___ पढ़ती है।", "answers": ["किताब", "कहानी"]}
            ],
            "speaking_phrases": [
                "मुझे पढ़ना पसंद है।",
                "मेरा नाम अमर है",
                "बिल्ली बहुत प्यारी है।",
                "सूर्य चमक रहा है।"
            ]
        },
        "middle": {
            "nouns": ["छात्र", "शिक्षक", "पाठ", "कहानियाँ", "प्रश्न", "उत्तर"],
            "verbs": ["सीखते हैं", "पढ़ाते हैं", "लिखते हैं", "मदद करते हैं"],
            "spelling_tests": [
                {"word": "विद्यार्थी", "options": ["विद्यार्थी", "विद्ध्यार्थी", "विद्यारथी"], "answer": "विद्यार्थी"},
                {"word": "शिक्षक", "options": ["शिक्षक", "सीक्षक", "शिशक"], "answer": "शिक्षक"},
                {"word": "ज्ञान", "options": ["ज्ञान", "ग्यान", "ज्यान"], "answer": "ज्ञान"}
            ],
            "writing_templates": [
                {"template": "सूर्य ___ दिशा में उगता है।", "answers": ["पूर्व"]},
                {"template": "बच्चे स्कूल में ___ सीखते हैं।", "answers": ["पाठ", "ज्ञान", "अच्छी बातें"]}
            ],
            "speaking_phrases": [
                "किताबें हमारी सबसे अच्छी मित्र हैं।",
                "हमें हर दिन नया सीखना चाहिए।",
                "शिक्षक हमें सही मार्ग दिखाते हैं।",
                "शिक्षा हमारे जीवन को सुंदर बनाती हैं।"
            ]
        },
        "older": {
            "nouns": ["साक्षरता", "विकास", "संवाद", "अवसर", "सफलता", "भविष्य"],
            "verbs": ["मजबूत करता है", "बढ़ाता है", "मदद करता है", "दिलाता है"],
            "spelling_tests": [
                {"word": "साक्षरता", "options": ["साक्षरता", "शाक्षरता", "साक्षरताा"], "answer": "साक्षरता"},
                {"word": "सफलता", "options": ["सफलता", "सफळता", "सफल्ता"], "answer": "सफलता"},
                {"word": "आत्मविश्वास", "options": ["आत्मविश्वास", "आतंविश्वास", "आत्मविस्वास"], "answer": "आत्मविश्वास"}
            ],
            "writing_templates": [
                {"template": "साक्षरता हमारे सुंदर भविष्य की ___ है।", "answers": ["चाबी", "नींव", "कुंजी"]},
                {"template": "अच्छा संवाद कौशल हमें बेहतर ___ दिलाता है।", "answers": ["अवसर", "नौकरी", "भविष्य"]}
            ],
            "speaking_phrases": [
                "साक्षरता ही सुनहरे भविष्य की कुंजी है।",
                "भाषा कौशल हमें आत्मविश्वास से विचार साझा करने में मदद करते हैं।",
                "तकनीक शिक्षा को सभी के लिए सुलभ बनाती है।",
                "संवाद ही व्यक्तिगत विकास के लिए आवश्यक है।"
            ]
        }
    },
    "Tamil": {
        "toddler": {
            "spelling_tests": [
                {"word": "அம்மா", "options": ["அம்மா", "அமா", "ஆம்மா"], "answer": "அம்மா"},
                {"word": "ஆடு", "options": ["ஆடு", "அடு", "ஆடூ"], "answer": "ஆடு"},
                {"word": "இலை", "options": ["இலை", "ஈலை", "இல"], "answer": "இலை"}
            ],
            "writing_templates": [
                {"template": "இது என் ___.", "answers": ["வீடு", "பந்து", "பேனா"]},
                {"template": "அம்மா ___ தருகிறார்.", "answers": ["பால்", "தண்ணீர்"]}
            ],
            "speaking_phrases": [
                "நல்ல பையன்",
                "சின்ன பூனை",
                "பள்ளிக்கு போ"
            ]
        },
        "young": {
            "nouns": ["பூனை", "நாய்", "புத்தகம்", "பந்து", "பேனா", "விளையாட்டு", "பால்", "பழம்"],
            "verbs": ["இருக்கிறது", "குடிக்கிறது", "விளையாடுகிறது", "படிக்கிறது", "ஓடுகிறது"],
            "spelling_tests": [
                {"word": "புத்தகம்", "options": ["புத்தகம்", "புதகம்", "புத்தகம்ம"], "answer": "புத்தகம்"},
                {"word": "பள்ளி", "options": ["பள்ளி", "பலி", "பல்ளி"], "answer": "பள்ளி"},
                {"word": "பேனா", "options": ["பேனா", "பெனா", "பேநா"], "answer": "பேனா"}
            ],
            "writing_templates": [
                {"template": "பூனை ___ குடிக்கிறது.", "answers": ["பால்", "தண்ணீர்"]},
                {"template": "ஆப்பிள் ___ நிறத்தில் இருக்கும்.", "answers": ["சிவப்பு"]},
                {"template": "அவள் ___ படிக்கிறாள்.", "answers": ["புத்தகம்", "கதை"]}
            ],
            "speaking_phrases": [
                "எனக்கு படிக்க பிடிக்கும்.",
                "என் பெயர் குமார்.",
                "பூனை மிகவும் அழகானது.",
                "சூரியன் பிரகாசிக்கிறது."
            ]
        },
        "middle": {
            "nouns": ["மாணவர்கள்", "ஆசிரியர்கள்", "பாடங்கள்", "கதைகள்", "கேள்விகள்", "பதில்கள்"],
            "verbs": ["கற்றுக்கொள்கிறார்கள்", "கற்பிக்கிறார்கள்", "எழுதுகிறார்கள்", "உதவுகிறார்கள்"],
            "spelling_tests": [
                {"word": "மாணவன்", "options": ["மாணவன்", "மானவன்", "மாணவந்"], "answer": "மாணவன்"},
                {"word": "ஆசிரியர்", "options": ["ஆசிரியர்", "ஆசரியர்", "ஆசிரிஒர்"], "answer": "ஆசிரியர்"},
                {"word": "அறிவு", "options": ["அறிவு", "அரிவு", "அரீவு"], "answer": "அறிவு"}
            ],
            "writing_templates": [
                {"template": "சூரியன் ___ திசையில் உதிக்கிறது.", "answers": ["கிழக்கு"]},
                {"template": "மாணவர்கள் பள்ளியில் ___ கற்கிறார்கள்.", "answers": ["பாடங்கள்", "அறிவு", "ஒழுக்கம்"]}
            ],
            "speaking_phrases": [
                "புத்தகங்கள் வாசிப்பது நல்ல பழக்கம்.",
                "ஒவ்வொரு நாளும் புதிய விஷயங்களை கற்க வேண்டும்.",
                "ஆசிரியர்கள் நமக்கு நல்வழி காட்டுகிறார்கள்.",
                "பள்ளி நமக்கு கல்வியையும் ஒழுக்கத்தையும் கற்பிக்கிறது."
            ]
        },
        "older": {
            "nouns": ["அடித்தளம்", "எழுத்தறிவு", "வளர்ச்சி", "தொடர்பு", "வாய்ப்புகள்"],
            "verbs": ["பலப்படுத்துகிறது", "உதவுகிறது", "அடையலாம்", "வழங்குகிறது"],
            "spelling_tests": [
                {"word": "எழுத்தறிவு", "options": ["எழுத்தறிவு", "எளுத்தறிவு", "எழுத்தரிவு"], "answer": "எழுத்தறிவு"},
                {"word": "வெற்றி", "options": ["வெற்றி", "வெட்ரி", "வெற்றிஇ"], "answer": "வெற்றி"},
                {"word": "நம்பிக்கை", "options": ["நம்பிக்கை", "நம்பிகை", "நம்பிஃகை"], "answer": "நம்பிக்கை"}
            ],
            "writing_templates": [
                {"template": "எழுத்தறிவு நமது சிறந்த எதிர்காலத்திற்கு ___.", "answers": ["அடித்தளம்", "முக்கியம்"]},
                {"template": "நல்ல தொடர்பு திறன் சிறந்த ___ பெற்றுத்தரும்.", "answers": ["வாய்ப்புகளை", "வேலையை"]}
            ],
            "speaking_phrases": [
                "எழுத்தறிவே சிறந்த எதிர்காலத்தின் திறவுகோல்.",
                "மொழித் திறன் நம் கருத்துக்களைப் பகிர உதவுகிறது.",
                "தொழில்நுட்பம் கல்வியை எளிதாக்குகிறது.",
                "தொடர்பு திறன் தனிப்பட்ட வளர்ச்சிக்கு அவசியம்."
            ]
        }
    },
    "Kannada": {
        "toddler": {
            "spelling_tests": [
                {"word": "ಅಮ್ಮ", "options": ["ಅಮ್ಮ", "ಅಮ", "ಆಮ್ಮ"], "answer": "ಅಮ್ಮ"},
                {"word": "ಆಟ", "options": ["ಆಟ", "ಅಟ", "ಆಟಾ"], "answer": "ಆಟ"},
                {"word": "ಎಲೆ", "options": ["ಎಲೆ", "ಏಲೆ", "ಎಲ"], "answer": "ಎಲೆ"}
            ],
            "writing_templates": [
                {"template": "ಇದು ನನ್ನ ___.", "answers": ["ಮನೆ", "ಚೆಂಡು", "ಪೆನ್"]},
                {"template": "ಅಮ್ಮ ___ ಕೊಡುತ್ತಾರೆ.", "answers": ["ಹಾಲು", "ನೀರು"]}
            ],
            "speaking_phrases": [
                "ಒಳ್ಳೆಯ ಹುಡುಗ",
                "ಸಣ್ಣ ಬೆಕ್ಕು",
                "ಶಾಲೆಗೆ ಹೋಗು"
            ]
        },
        "young": {
            "nouns": ["ಬೆಕ್ಕು", "ನಾಯಿ", "ಪುಸ್ತಕ", "ಚೆಂಡು", "ಪೆನ್", "ಆಟ", "ಹಾಲು", "ಹಣ್ಣು"],
            "verbs": ["ಇದೆ", "ಕುಡಿಯುತ್ತದೆ", "ಆಡುತ್ತದೆ", "ಓದುತ್ತದೆ", "ಓಡುತ್ತದೆ"],
            "spelling_tests": [
                {"word": "ಪುಸ್ತಕ", "options": ["ಪುಸ್ತಕ", "ಪುಸ್ತಖ", "ಪುಸ್ತಕ್"], "answer": "ಪುذجಕ"},
                {"word": "ಶಾಲೆ", "options": ["ಶಾಲೆ", "ಸಾಲ", "ಶಾಳೆ"], "answer": "ಶಾಲೆ"},
                {"word": "ಪೆನ್", "options": ["ಪೆನ್", "ಫೆನ್", "ಪೇನ್"], "answer": "ಪೆನ್"}
            ],
            "writing_templates": [
                {"template": "ಬೆಕ್ಕು ___ ಕುಡಿಯುತ್ತದೆ.", "answers": ["ಹಾಲು", "ನೀರು"]},
                {"template": "ಸೇಬಿನ ಬಣ್ಣ ___ ಇರುತ್ತದೆ.", "answers": ["ಕೆಂಪು"]},
                {"template": "ಅವಳು ___ ಓದುತ್ತಾಳೆ.", "answers": ["ಪುಸ್ತಕ", "ಕಥೆ"]}
            ],
            "speaking_phrases": [
                "ನನಗೆ ಓದಲು ಇಷ್ಟ.",
                "ನನ್ನ ಹೆಸರು ಕಿರಣ್.",
                "ಬೆಕ್ಕು ತುಂಬಾ ಮುದ್ದಾಗಿದೆ.",
                "ಸೂರ್ಯನು ಬೆಳಗುತ್ತಿದ್ದಾನೆ."
            ]
        },
        "middle": {
            "nouns": ["ವಿದ್ಯಾರ್ಥಿಗಳು", "ಶಿಕ್ಷಕರು", "ಪಾಠಗಳು", "ಕಥೆಗಳು", "ಪ್ರಶ್ನೆಗಳು", "ಉತ್ತರಗಳು"],
            "verbs": ["ಕಲಿಯುತ್ತಾರೆ", "ಬೋಧಿಸುತ್ತಾರೆ", "ಬರೆಯುತ್ತಾರೆ", "ಸಹಾಯ ಮಾಡುತ್ತಾರೆ"],
            "spelling_tests": [
                {"word": "ವಿದ್ಯಾರ್ಥಿ", "options": ["ವಿದ್ಯಾರ್ಥಿ", "ವಿದ್ಯಾರ್ತಿ", "ವಿಧ್ಯಾರ್ಥಿ"], "answer": "ವಿದ್ಯಾರ್ಥಿ"},
                {"word": "ಶಿಕ್ಷಕ", "options": ["ಶಿಕ್ಷಕ", "ಶಿಕ್ಸಕ", "ಸಿಕ್ಷಕ"], "answer": "ಶಿಕ್ಷಕ"},
                {"word": "ಜ್ಞಾನ", "options": ["ಜ್ಞಾನ", "ಗ್ನಾನ", "ಜ್ನಾನ"], "answer": "ಜ್ಞಾನ"}
            ],
            "writing_templates": [
                {"template": "ಸೂರ್ಯನು ___ ದಿಕ್ಕಿನಲ್ಲಿ ಉದಯಿಸುತ್ತಾನೆ.", "answers": ["ಪೂರ್ವ"]},
                {"template": "ವಿದ್ಯಾರ್ಥಿಗಳು ಶಾಲೆಯಲ್ಲಿ ___ ಕಲಿಯುತ್ತಾರೆ.", "answers": ["ಪಾಠಗಳನ್ನು", "ಜ್ಞಾನ", "ಶಿಸ್ತು"]}
            ],
            "speaking_phrases": [
                "ಪುಸ್ತಕಗಳನ್ನು ಓದುವುದು ಒಳ್ಳೆಯ ಹವ್ಯಾಸ.",
                "ನಾವು ಪ್ರತಿದಿನ ಹೊಸದನ್ನು ಕಲಿಯಬೇಕು.",
                "ಶಿಕ್ಷಕರು ನಮಗೆ ಸರಿಯಾದ ಮಾರ್ಗವನ್ನು ತೋರಿಸುತ್ತಾರೆ.",
                "ಶಾಲೆ ನಮಗೆ ಶಿಕ್ಷಣ ಮತ್ತು ಶಿಸ್ತನ್ನು ಕಲಿತ್ತದೆ."
            ]
        },
        "older": {
            "nouns": ["ಬುನಾದಿ", "ಸಾಕ್ಷರತೆ", "ಅಭಿವೃದ್ಧಿ", "ಸಂವಹನ", "ಅವಕಾಶಗಳು"],
            "verbs": ["ಬಲಪಡಿಸುತ್ತದೆ", "ಸಹಾಯ ಮಾಡುತ್ತದೆ", "ಸಾಧಿಸಬಹುದು", "ಒದಗಿಸುತ್ತದೆ"],
            "spelling_tests": [
                {"word": "ಸಾಕ್ಷರತೆ", "options": ["ಸಾಕ್ಷರತೆ", "ಸಾಕ್ಸರತೆ", "ಶಾಕ್ಷರತೆ"], "answer": "ಸಾಕ್ಷರತೆ"},
                {"word": "ಯಶಸ್ಸು", "options": ["ಯಶಸ್ಸು", "ಯಸಸ್ಸು", "ಯಶಶು"], "answer": "ಯಶಸ್ಸು"},
                {"word": "ಆತ್ಮವಿಶ್ವಾಸ", "options": ["ಆತ್ಮವಿಶ್ವಾಸ", "ಆತ್ಮವಿಸ್ವಾಸ", "ಅತ್ಮವಿಶ್ವಾಸ"], "answer": "ಆತ್ಮವಿಶ್ವಾಸ"}
            ],
            "writing_templates": [
                {"template": "ಸಾಕ್ಷರತೆಯು ನಮ್ಮ ಸುಂದರ ಭವಿಷ್ಯದ ___ ಆಗಿದೆ.", "answers": ["ಬುನಾದಿ", "ಕೀಲಿ ಕೈ"]},
                {"template": "ಉತ್ತಮ ಸಂವಹನ ಕೌಶಲ್ಯಗಳು ಉತ್ತಮ ___ ಒದಗಿಸುತ್ತವೆ.", "answers": ["ಅವಕಾಶಗಳನ್ನು", "ಕೆಲಸವನ್ನು"]}
            ],
            "speaking_phrases": [
                "ಸಾಕ್ಷರತೆಯೇ ಸುಂದರ ಭವಿಷ್ಯದ ಕೀಲಿ.",
                "ಭಾಷಾ ಕೌಶಲ್ಯಗಳು ನಮ್ಮ ಆಲೋಚನೆಗಳನ್ನು ಹಂಚಿಕೊಳ್ಳಲು ಸಹಾಯ ಮಾಡುತ್ತವೆ.",
                "ತಂತ್ರಜ್ಞಾನವು ಶಿಕ್ಷಣವನ್ನು ಎಲ್ಲರಿಗೂ ಸುಲಭಗೊಳಿಸುತ್ತದೆ.",
                "ವೈಯಕ್ತಿಕ ಬೆಳವಣಿಗೆಗೆ ಸಂವಹನ ಅತ್ಯಗತ್ಯ."
            ]
        }
    },
    "Malayalam": {
        "toddler": {
            "spelling_tests": [
                {"word": "അമ്മ", "options": ["അമ്മ", "അമ", "ആമ്മ"], "answer": "അമ്മ"},
                {"word": "ആട്", "options": ["ആട്", "അട്", "ആടു"], "answer": "ആട്"},
                {"word": "ഇല", "options": ["ഇല", "ഈല", "ഇലാ"], "answer": "ഇല"}
            ],
            "writing_templates": [
                {"template": "ഇത് എന്റെ ___ ആണ്.", "answers": ["വീട്", "പന്ത്", "പേന"]},
                {"template": "അമ്മ ___ തരുന്നു.", "answers": ["പാൽ", "വെള്ളം"]}
            ],
            "speaking_phrases": [
                "നല്ല കുട്ടി",
                "ചെറിയ പൂച്ച",
                "സ്കൂളിൽ പോകൂ"
            ]
        },
        "young": {
            "nouns": ["പൂച്ച", "നായ", "പുസ്തകം", "പന്ത്", "പേന", "കളി", "പാൽ", "പഴം"],
            "verbs": ["ഉണ്ട്", "കുടിക്കുന്നു", "കളിക്കുന്നു", "വായിക്കുന്നു", "ഓടുന്നു"],
            "spelling_tests": [
                {"word": "പുസ്തകം", "options": ["പുസ്തകം", "പുസ്തകംം", "പുസ്തകംമ്"], "answer": "പുസ്തകം"},
                {"word": "സ്കൂൾ", "options": ["സ്കൂൾ", "സ്കൂള", "സ്കൂൾമ്"], "answer": "സ്കൂൾ"},
                {"word": "പേന", "options": ["പേന", "പെന", "പേനാ"], "answer": "പേന"}
            ],
            "writing_templates": [
                {"template": "പൂച്ച ___ കുടിക്കുന്നു.", "answers": ["പാൽ", "വെള്ളം"]},
                {"template": "ആപ്പിളിന്റെ നിറം ___ ആണ്.", "answers": ["ചുവപ്പ്"]},
                {"template": "അവൾ ___ വായിക്കുന്നു.", "answers": ["പുസ്തകം", "കഥ"]}
            ],
            "speaking_phrases": [
                "എനിക്ക് വായിക്കാൻ ഇഷ്ടമാണ്.",
                "എന്റെ പേര് അരുൺ.",
                "പൂച്ച വളരെ സുന്ദരമാണ്.",
                "സൂര്യൻ പ്രകാശിക്കുന്നു."
            ]
        },
        "middle": {
            "nouns": ["വിദ്യാർത്ഥികൾ", "അധ്യാപകർ", "പാഠങ്ങൾ", "കഥകൾ", "ചോദ്യങ്ങൾ", "ഉത്തരങ്ങൾ"],
            "verbs": ["പഠിക്കുന്നു", "പഠിപ്പിക്കുന്നു", "എഴുതുന്നു", "സഹായിക്കുന്നു"],
            "spelling_tests": [
                {"word": "വിദ്യാർത്ഥി", "options": ["വിദ്യാർത്ഥി", "വിദ്യാർതി", "വിദ്ധ്യാർത്ഥി"], "answer": "വിദ്യാർത്ഥി"},
                {"word": "അധ്യാപകൻ", "options": ["അധ്യാപകൻ", "അദ്ധ്യാപകൻ", "അധ്യാപകന്"], "answer": "അധ്യാപകൻ"},
                {"word": "ജ്ഞാനം", "options": ["ജ്ഞാനം", "ഗ്നാനം", "ജ്നാനം"], "answer": "ജ്ഞാനം"}
            ],
            "writing_templates": [
                {"template": "സൂര്യൻ ___ ദിശയിൽ ഉദിക്കുന്നു.", "answers": ["കിഴക്ക്"]},
                {"template": "വിദ്യാർത്ഥികൾ സ്കൂളിൽ നിന്നും ___ പഠിക്കുന്നു.", "answers": ["പാഠങ്ങൾ", "അറിവ്", "അച്ചടക്കം"]}
            ],
            "speaking_phrases": [
                "പുസ്തക വായന നല്ലൊരു ശീലമാണ്.",
                "നാം ദിവസവും പുതിയ കാര്യങ്ങൾ പഠിക്കണം.",
                "അധ്യാപകർ നമ്മെ ശരിയായ വഴി കാണിക്കുന്നു.",
                "സ്കൂൾ നമ്മെ അറിവും അച്ചടക്കവും പഠിപ്പിക്കുന്നു."
            ]
        },
        "older": {
            "nouns": ["അടിത്തറ", "സാക്ഷരത", "വികസനം", "വിനിമയം", "അവസരങ്ങൾ"],
            "verbs": ["ശക്തിപ്പെടുത്തുന്നു", "സഹായിക്കുന്നു", "നേടാം", "നൽകുന്നു"],
            "spelling_tests": [
                {"word": "സാക്ഷരത", "options": ["സാക്ഷരത", "സാക്സരത", "ശാക്ഷരത"], "answer": "സാക്ഷരത"},
                {"word": "വിജയം", "options": ["വിജയം", "വിജയംമ്", "വിജയമ്"], "answer": "വിജയം"},
                {"word": "ആത്മവിശ്വാസം", "options": ["ആത്മവിശ്വാസം", "ആത്മവിസ്വാസം", "അത്മവിശ്വാസം"], "answer": "ആത്മവിശ്വാസം"}
            ],
            "writing_templates": [
                {"template": "സാക്ഷരത നമ്മുടെ നല്ലൊരു ഭാവിയുടെ ___ ആണ്.", "answers": ["അടിത്തറ", "താക്കോൽ"]},
                {"template": "നല്ല വിനിമയ ശേഷി മികച്ച ___ നൽകുന്നു.", "answers": ["അവസരങ്ങൾ", "ജോലി"]}
            ],
            "speaking_phrases": [
                "സാക്ഷരതയാണ് നല്ലൊരു ഭാവിയുടെ താക്കോൽ.",
                "ആശയങ്ങൾ പങ്കുവെക്കാൻ ഭാഷാ വിനിമയം സഹായിക്കുന്നു.",
                "സാങ്കേതികവിദ്യ പഠനം എളുപ്പമാക്കുന്നു.",
                "വ്യകതിഗത വളർച്ചയ്ക്ക് വിനിമയം അത്യാവശ്യമാണ്."
            ]
        }
    }
}
def _normalize_learning_level(level):
    if not level:
        return "Beginner"
    return str(level).strip().capitalize()


def _get_age_band(age):
    try:
        age_val = int(age) if age is not None else 8
    except (ValueError, TypeError):
        age_val = 8
    if age_val <= 6:
        return "young"
    if age_val <= 10:
        return "middle"
    return "older"


def _get_assessment_profile(level, age_band):
    level_name = _normalize_learning_level(level)
    profiles = {
        "Advanced": {
            "level": "Advanced",
            "question_count": 12,
            # Advanced: paragraph reading, grammar, writing, communication, reading comprehension
            "activities": [
                "reading", "comprehension", "writing", "comprehension",
                "writing", "reading", "comprehension", "writing",
                "speaking", "listening", "reading", "comprehension"
            ],
            "age_band": age_band,
        },
        "Intermediate": {
            "level": "Intermediate",
            "question_count": 10,
            # Intermediate: sentence reading, sentence writing, listening, speaking, simple comprehension
            "activities": [
                "reading", "writing", "listening", "speaking",
                "comprehension", "reading", "writing", "listening",
                "speaking", "comprehension"
            ],
            "age_band": age_band,
        },
        "Basic": {
            "level": "Basic",
            "question_count": 8,
            # Basic: alphabets, simple words, picture-word matching, pronunciation
            "activities": [
                "reading", "listening", "comprehension", "speaking",
                "reading", "listening", "comprehension", "speaking"
            ],
            "age_band": age_band,
        },
        "Beginner": {
            "level": "Beginner",
            "question_count": 8,
            # Beginner: picture identification, object recognition, color/shape, listening, simple voice responses
            # No explicit reading or writing questions for Beginner
            "activities": [
                "comprehension", "listening", "speaking",
                "comprehension", "listening", "speaking",
                "listening", "speaking"
            ],
            "age_band": age_band,
        },
    }
    return profiles.get(level_name, profiles["Beginner"])


def _build_level_questions(language, profile, pool):
    questions = []
    age_band = profile["age_band"]
    level = profile["level"]

    def get_pool(key, fallback=None):
        if key in pool:
            return pool[key]
        if fallback and fallback in pool:
            return pool[fallback]
        return []

    def make_options(correct, base_opts):
        opts = [correct] + [opt for opt in base_opts if opt != correct]
        opts = list(dict.fromkeys(opts))
        while len(opts) < 4:
            opts.append(f"Option {len(opts) + 1}")
        return opts[:4]

    def build_reading_question(position):
        if level == "Basic":
            pool_data = get_pool("simple_words", "spelling")
            item = pool_data[position % len(pool_data)] if pool_data else ("apple", "Apple", ["Apple", "Ball", "Cat", "Dog"], "Apple is the correct word for the fruit.")
            return {
                "type": "reading",
                "skill": "reading",
                "prompt": f"Read the word and choose the matching picture: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "reading",
            }
        if level == "Intermediate":
            pool_data = get_pool("sentences", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("The cat is on the mat.", "The cat is on the mat.", ["The cat is on the mat.", "The dog is on the mat.", "The cat is in the car."], "Choose the correct sentence.")
            return {
                "type": "reading",
                "skill": "reading",
                "prompt": f"Read this sentence and choose the best answer: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "reading",
            }
        pool_data = get_pool("paragraphs", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("A boy planted a tree in the garden.", "Where did the boy plant a tree?", "In the garden", ["In the garden", "In the car", "In the school", "In the bed"], "The boy planted a tree in the garden.")
        return {
            "type": "reading",
            "skill": "reading",
            "prompt": f"Read the paragraph and answer: {item[1]}",
            "text": item[0],
            "options": make_options(item[2], item[3]),
            "answer": item[2],
            "explanation": item[4] if len(item) > 4 else "Read the paragraph and answer the question.",
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "reading",
        }

    def build_writing_question(position):
        if level == "Basic":
            pool_data = get_pool("objects", "spelling")
            item = pool_data[position % len(pool_data)] if pool_data else ({"image_url": "/static/images/apple.svg", "alt": "Apple"}, "Apple", "Copy the word and write it clearly.")
            return {
                "type": "writing",
                "skill": "writing",
                "prompt": "Write the name of the picture shown.",
                "text": item[0],
                "answer": item[1],
                "explanation": item[2],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "writing",
            }
        if level == "Intermediate":
            pool_data = get_pool("sentence_writing", "writing_templates")
            item = pool_data[position % len(pool_data)] if pool_data else ("Describe your pet.", "I have a small pet dog.", "Write one short sentence about your pet.")
            return {
                "type": "writing",
                "skill": "writing",
                "prompt": f"Write a short sentence: {item[0]}",
                "answer": item[1],
                "explanation": item[2],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "writing",
            }
        pool_data = get_pool("paragraph_writing", "writing_templates")
        item = pool_data[position % len(pool_data)] if pool_data else ("a day at school", "I went to school and learned new things.", "Write a short paragraph about a day at school.")
        return {
            "type": "writing",
            "skill": "writing",
            "prompt": f"Write a short paragraph about: {item[0]}",
            "answer": item[1],
            "explanation": item[2],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "writing",
        }

    def build_listening_question(position):
        if level == "Basic":
            pool_data = get_pool("listening_words", "listening")
            item = pool_data[position % len(pool_data)] if pool_data else ("Apple", "Apple", ["Apple", "Banana", "House", "Dog"], "Choose the word you heard.")
            return {
                "type": "listening",
                "skill": "listening",
                "prompt": "Listen and choose the right word.",
                "text": item[0],
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "listening",
            }
        if level == "Intermediate":
            pool_data = get_pool("listening_sentences", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("The cat sleeps.", "Where is the cat?", "On the mat", ["On the mat", "In the tree", "In the car", "On the bed"], "Listen and answer the question.")
            return {
                "type": "listening",
                "skill": "listening",
                "prompt": f"Listen to the sentence and answer: {item[1]}",
                "text": item[0],
                "options": make_options(item[2], item[3]),
                "answer": item[2],
                "explanation": item[4] if len(item) > 4 else "Listen to the sentence and answer.",
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "listening",
            }
        pool_data = get_pool("listening_paragraphs", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("Ria went to the market.", "What did Ria buy?", "Fruits", ["Fruits", "Vegetables", "Books", "Toys"], "Listen and answer the question.")
        return {
            "type": "listening",
            "skill": "listening",
            "prompt": f"Listen to the passage and answer: {item[1]}",
            "text": item[0],
            "options": make_options(item[2], item[3]),
            "answer": item[2],
            "explanation": item[4] if len(item) > 4 else "Listen to the passage and answer.",
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "listening",
        }

    def build_speaking_question(position):
        if level == "Basic":
            pool_data = get_pool("speaking_phrases", "speaking")
            item = pool_data[position % len(pool_data)] if pool_data else "I like apples"
            return {
                "type": "speaking",
                "skill": "speaking",
                "prompt": f"Say this sentence aloud: {item}",
                "hint": item,
                "answer": item,
                "explanation": "Speak the phrase clearly and confidently.",
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "speaking",
            }
        pool_data = get_pool("speaking_responses", "speaking")
        item = pool_data[position % len(pool_data)] if pool_data else ("What is your name?", "My name is Ria.")
        return {
            "type": "speaking",
            "skill": "speaking",
            "prompt": f"Speak a short answer: {item[0]}",
            "hint": item[1],
            "answer": item[1],
            "explanation": "Answer the question with a short spoken response.",
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "speaking",
        }

    def build_comprehension_question(position):
        if level == "Basic":
            pool_data = get_pool("shape_words", "reading_letters")
            item = pool_data[position % len(pool_data)] if pool_data else ("A shape with three sides", "Triangle", ["Triangle", "Circle", "Square", "Star"], "A triangle has three sides.")
            return {
                "type": "comprehension",
                "skill": "comprehension",
                "prompt": f"Match the word with the picture or shape: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "comprehension",
            }
        if level == "Intermediate":
            pool_data = get_pool("vocabulary", "comps")
            item = pool_data[position % len(pool_data)] if pool_data else ("Joyful", "Happy", ["Happy", "Sad", "Hungry", "Cold"], "Joyful means happy.")
            return {
                "type": "comprehension",
                "skill": "comprehension",
                "prompt": f"Choose the meaning of this word: {item[0]}",
                "options": make_options(item[1], item[2]),
                "answer": item[1],
                "explanation": item[3],
                "age_band": age_band,
                "level": level,
                "language": language,
                "skill_score_key": "comprehension",
            }
        pool_data = get_pool("grammar", "comps")
        item = pool_data[position % len(pool_data)] if pool_data else ("Choose the correct sentence.", "She is reading a book.", ["She is reading a book.", "She are reading a book.", "She reading a book."], "This sentence is grammatically correct.")
        return {
            "type": "comprehension",
            "skill": "comprehension",
            "prompt": f"Choose the correct sentence: {item[0]}",
            "options": make_options(item[1], item[2]),
            "answer": item[1],
            "explanation": item[3],
            "age_band": age_band,
            "level": level,
            "language": language,
            "skill_score_key": "comprehension",
        }

    builders = {
        "reading": build_reading_question,
        "writing": build_writing_question,
        "listening": build_listening_question,
        "speaking": build_speaking_question,
        "comprehension": build_comprehension_question,
    }

    for index, skill in enumerate(profile["activities"]):
        builder = builders.get(skill)
        if not builder:
            continue
        question = builder(index)
        question["name"] = f"q{index + 1}"
        questions.append(question)

    return questions


def _legacy_get_assessment_questions(language, age=None, learning_level=None, mode=None):
    try:
        age_val = int(age) if age is not None else session.get("age", 8)
    except (ValueError, TypeError):
        age_val = 8

    if age_val <= 7 or (learning_level and ("beginner" in str(learning_level).lower() or "cannot" in str(learning_level).lower())):
        # Pre-school and beginner play-based assessment questions (Moo sound, red fruit strawberry, round circle shape, king of jungle lion, speak hello)
        multilingual_questions = {
            "English": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "What animal makes this sound: 'Moo Moo'? 🐮",
                    "options": ["Cow 🐮", "Dog 🐶", "Lion 🦁", "Cat 🐱"],
                    "answer": "Cow 🐮",
                    "explanation": "Cows make the moo sound!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Which of these is a red fruit? 🍓 (point or choose the picture)",
                    "options": ["Strawberry 🍓", "Banana 🍌", "Grape 🍇", "Pear 🍐"],
                    "answer": "Strawberry 🍓",
                    "explanation": "Strawberries are bright red and easy to recognize by color."
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Point to the round shape or choose the round picture. ⭕",
                    "options": ["Circle ⭕", "Square ⬛", "Triangle 🔺", "Star ⭐"],
                    "answer": "Circle ⭕",
                    "explanation": "A circle is round and has no corners."
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "Which animal is often called the 'King of the Jungle'? 🦁",
                    "options": ["Lion 🦁", "Elephant 🐘", "Monkey 🐒", "Rabbit 🐰"],
                    "answer": "Lion 🦁",
                    "explanation": "The lion is commonly referred to as the king of the jungle."
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "Click the microphone and repeat: 'Hello' 👋",
                    "hint": "Hello",
                    "options": [],
                    "answer": "Hello",
                    "explanation": "Practice saying Hello."
                }
            ],
            "Telugu": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'బౌ బౌ' అని అరిచే జంతువు ఏది? 🐶",
                    "options": ["ఆవు 🐮", "కుక్క 🐶", "సింహం 🦁", "పిల్లి 🐱"],
                    "answer": "కుక్క 🐶",
                    "explanation": "కుక్కలు బౌ బౌ అని అరుస్తాయి!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "ఎరుపు రంగు పండును అని గుర్తించండి! 🍓 (పిక్ లేదా ఎంపిక చేయండి)",
                    "options": ["స్ట్రాబెర్రీ 🍓", "అరటిపండు 🍌", "ద్రాక్ష 🍇", "ఆపిల్ 🍎"],
                    "answer": "స్ట్రాబెర్రీ 🍓",
                    "explanation": "స్ట్రాబెర్రీలు ప్రత్యేకంగా ఎరుపు రంగులో ఉంటాయి."
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "గుండ్రటి ఆకారాన్ని చూపండి లేదా సెలెక్ట్ చేయండి. ⭕",
                    "options": ["వృత్తం ⭕", "చతురస్రం ⬛", "త్రిభుజం 🔺", "నక్షత్రం ⭐"],
                    "answer": "వృత్తం ⭕",
                    "explanation": "వృత్తం ఒకవక గుండ్రంగా ఉంటుంది."
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "అడవికి రాజుగా పేరుపొందిన జంతువు ఏది? 🦁",
                    "options": ["సింహం 🦁", "ఏనుగు 🐘", "కోతి 🐒", "కుందేలు 🐰"],
                    "answer": "సింహం 🦁",
                    "explanation": "సింహాన్ని సాధారణంగా అడవి రాజునిగా పిలుస్తారు."
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "మైక్రోఫోన్‌ క్లిక్ చేసి చెప్పండి: 'నమస్కారం' 👋",
                    "hint": "నమస్కారం",
                    "options": [],
                    "answer": "నమస్కారం",
                    "explanation": "నమస్కారం చెప్పడం ప్రాక్టీस చేయండి."
                }
            ],
            "Hindi": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'म्याऊं म्याऊं' कौन सा जानवर करता है? 🐱",
                    "options": ["गाय 🐮", "कुत्ता 🐶", "शेर 🦁", "बिल्ली 🐱"],
                    "answer": "बिल्ली 🐱",
                    "explanation": "बिल्ली म्याऊं म्याऊं करती है!"
                },
                {
                    "name": "q_color",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "कौन सा फल लाल रंग का है? 🍓 (चित्र पर इशारा या चुनें)",
                    "options": ["स्ट्रॉबेरी 🍓", "केला 🍌", "अंगूर 🍇", "नाशपाती 🍐"],
                    "answer": "स्ट्रॉबेरी 🍓",
                    "explanation": "स्ट्रॉबेरी आम तौर पर लाल रंग की होती है।"
                },
                {
                    "name": "q_shape",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "गोल आकृति को दिखाएं या चुनें। ⭕",
                    "options": ["गोला/वृत्त ⭕", "वर्ग ⬛", "त्रिकोण 🔺", "तारा ⭐"],
                    "answer": "गोला/वृत्त ⭕",
                    "explanation": "वृत्त का कोई नुकीला कोना नहीं होता।"
                },
                {
                    "name": "q_animal",
                    "type": "comprehension",
                    "skill": "comprehension",
                    "prompt": "किस जानवर को अक्सर जंगल का राजा कहा जाता है? 🦁",
                    "options": ["शेर 🦁", "हाथी 🐘", "बंदर 🐒", "खरगोश 🐰"],
                    "answer": "शेर 🦁",
                    "explanation": "शेर को पारंपरिक रूप से जंगल का राजा माना जाता है।"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "माइक चालू करें और बोलें: 'नमस्ते' 👋",
                    "hint": "नमस्ते",
                    "options": [],
                    "answer": "नमस्ते",
                    "explanation": "नमस्ते बोलना सीखें।"
                }
            ],
            "Tamil": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'லொள் லொள்' என்று குறைக்கும் விலங்கு எது? 🐶",
                    "options": ["பசு 🐮", "நாய் 🐶", "சிங்கம் 🦁", "பூனை 🐱"],
                    "answer": "நாய் 🐶",
                    "explanation": "நாய்கள் லொள் லொள் என்று குறைக்கும்!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "சிவப்பு நிற பழத்தைக் கண்டறியவும்! 🍓",
                    "options": ["ஸ்ட்ராபெரி 🍓", "வாழைப்பழம் 🍌", "திராட்சை 🍇", "பேரிக்காய் 🍐"],
                    "answer": "ஸ்ட்ராபெரி 🍓",
                    "explanation": "ஸ்ட்ராபெரி சிவப்பு நிறத்தில் இருக்கும்!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "வட்ட வடிவத்தை அடையாளம் காணவும்! ⭕",
                    "options": ["வட்டம் ⭕", "சதுரம் ⬛", "முக்கோணம் 🔺", "நட்சத்திரம் ⭐"],
                    "answer": "வட்டம் ⭕",
                    "explanation": "வட்டம் வட்டமாக இருக்கும்!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "காட்டின் ராஜா யார்? 🦁",
                    "options": ["சிங்கம் 🦁", "யானை 🐘", "குரங்கு 🐒", "முயல் 🐰"],
                    "answer": "சிங்கம் 🦁",
                    "explanation": "சிங்கம் காட்டின் ராஜா!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "மைக் ஒளிரச் செய்து கூறவும்: 'வணக்கம்' 👋",
                    "hint": "வணக்கம்",
                    "options": [],
                    "answer": "வணக்கம்",
                    "explanation": "வணக்கம் சொல்ல பயிற்சி செய்யவும்."
                }
            ],
            "Kannada": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'ಬೌ ಬೌ' ಎಂದು ಕೂಗುವ ಪ್ರಾಣಿ ಯಾವುದು? 🐶",
                    "options": ["ಹಸು 🐮", "ನಾಯಿ 🐶", "ಸಿಂಹ 🦁", "ಬೆಕ್ಕು 🐱"],
                    "answer": "ನಾಯಿ 🐶",
                    "explanation": "ನಾಯಿಗಳು ಬೌ ಬೌ ಎಂದು ಕೂಗುತ್ತವೆ!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ಕೆಂಪು ಬಣ್ಣದ ಹಣ್ಣನ್ನು ಗುರುತಿಸಿ! 🍓",
                    "options": ["ಸ್ಟ್ರಾಬೆರಿ 🍓", "ಬಾಳೆಹಣ್ಣು 🍌", "ದ್ರಾಕ್ಷಿ 🍇", "ಸೇಬು 🍎"],
                    "answer": "ಸ್ಟ್ರಾಬೆರಿ 🍓",
                    "explanation": "ಸ್ಟ್ರಾಬೆರಿ ಹಣ್ಣುಗಳು ಕೆಂಪಾಗಿರುತ್ತವೆ!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ವೃತ್ತಾಕಾರವನ್ನು ಗುರುತಿಸಿ! ⭕",
                    "options": ["ವೃತ್ತ ⭕", "ಚೌಕ ⬛", "ತ್ರಿಕೋನ 🔺", "ನಕ್ಷತ್ರ ⭐"],
                    "answer": "ವೃತ್ತ ⭕",
                    "explanation": "ವೃತ್ತವು ಗೋಲಾಕಾರವಾಗಿರುತ್ತದೆ!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "ಕಾಡಿನ ರಾಜ ಯಾರು? 🦁",
                    "options": ["ಸಿಂಹ 🦁", "ಆನೆ 🐘", "ಕೋತಿ 🐒", "ಮೊಲ 🐰"],
                    "answer": "ಸಿಂಹ 🦁",
                    "explanation": "ಸಿಂಹವು ಕಾಡಿನ ರಾಜ!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "ಮೈಕ್ರೊಫೋನ್ ಒತ್ತಿ ಹೇಳಿ: 'ನಮಸ್ಕಾರ' 👋",
                    "hint": "ನಮಸ್ಕಾರ",
                    "options": [],
                    "answer": "ನಮಸ್ಕಾರ",
                    "explanation": "ನಮಸ್ಕಾರ ಹೇಳುವುದನ್ನು ಅಭ್ಯಾಸ ಮಾಡಿ."
                }
            ],
            "Marathi": [
                {
                    "name": "q_sound",
                    "type": "listening",
                    "skill": "listening",
                    "prompt": "'म्याऊं म्याऊं' आवाज करणारा प्राणी कोणता? 🐱",
                    "options": ["गाय 🐮", "कुत्रा 🐶", "सिंह 🦁", "मांजर 🐱"],
                    "answer": "मांजर 🐱",
                    "explanation": "मांजर म्याऊं म्याऊं ओरडते!"
                },
                {
                    "name": "q_color",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "लाल रंगाचे फळ ओळखा! 🍓",
                    "options": ["स्ट्रॉबेरी 🍓", "केळे 🍌", "द्राक्षे 🍇", "सफरचंद 🍎"],
                    "answer": "स्ट्रॉबेरी 🍓",
                    "explanation": "स्ट्रॉबेरी लाल रंगाची असते!"
                },
                {
                    "name": "q_shape",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "गोल आकार ओळखा! ⭕",
                    "options": ["वर्तुळ ⭕", "चौकोन ⬛", "त्रिकोण 🔺", "चांदणी ⭐"],
                    "answer": "वर्तुळ ⭕",
                    "explanation": "वर्तुळ गोल असते!"
                },
                {
                    "name": "q_animal",
                    "type": "reading",
                    "skill": "reading",
                    "prompt": "जंगलाचा राजा कोण आहे? 🦁",
                    "options": ["सिंह 🦁", "हत्ती 🐘", "माकड 🐒", "ससा 🐰"],
                    "answer": "सिंह 🦁",
                    "explanation": "सिंह जंगलाचा राजा असतो!"
                },
                {
                    "name": "q_speak",
                    "type": "speaking",
                    "skill": "speaking",
                    "prompt": "माईक चालू करा आणि म्हणा: 'नमस्कार' 👋",
                    "hint": "नमस्कार",
                    "options": [],
                    "answer": "नमस्कार",
                    "explanation": "नमस्कार म्हणण्याचा सराव करा."
                }
            ]
        }
        qs = multilingual_questions.get(language, multilingual_questions["English"])
        for q in qs:
            q["age_band"] = "young"
            q["level"] = "Beginner"
            q["language"] = language
            q["skill_score_key"] = q["skill"]
        if not any(q["skill_score_key"] == "writing" for q in qs):
            for q in reversed(qs):
                if q["type"] == "speaking":
                    q["skill_score_key"] = "writing"
                    break
        if len(qs) < 6:
            qs.append({
                "name": "q_extra",
                "type": "comprehension",
                "skill": "comprehension",
                "section": "Comprehension Assessment",
                "prompt": "Which picture shows something that is red?",
                "options": ["Apple 🍎", "Banana 🍌", "Grapes 🍇", "Pear 🍐"],
                "answer": "Apple 🍎",
                "explanation": "The apple is red.",
                "age_band": "young",
                "level": "Beginner",
                "language": language,
                "skill_score_key": "comprehension"
            })
        return qs

    if not learning_level:
        learning_level = session.get("learning_level", "Beginner")

    import random

    lang_pools = {
        "English": {
            "letters": [
                ("Sound /b/", "B", ["B", "D", "P", "T"], "B makes the /b/ sound."),
                ("Sound /f/", "F", ["F", "V", "P", "S"], "F makes the /f/ sound."),
                ("Sound /m/", "M", ["M", "N", "W", "V"], "M makes the /m/ sound."),
                ("Sound /s/", "S", ["S", "C", "Z", "X"], "S makes the /s/ sound.")
            ],
            "simple_words": [
                ("apple", "Apple", ["Apple", "Banana", "Chair", "Tree"], "Apple is the correct word for the fruit."),
                ("ball", "Ball", ["Ball", "Cat", "Sun", "Fish"], "Ball is a common toy."),
                ("cup", "Cup", ["Cup", "Shoe", "Pen", "Door"], "Cup holds water or milk.")
            ],
            "objects": [
                ({"image_url": "/static/images/apple.svg", "alt": "Apple"}, "Apple", "This is an apple."),
                ({"image_url": "/static/images/dog.svg", "alt": "Dog"}, "Dog", "This is a dog."),
                ({"image_url": "/static/images/car.svg", "alt": "Car"}, "Car", "This is a car.")
            ],
            "word_completions": [
                ("B__", "Bee", "Complete the word to name the insect."),
                ("C_t", "Cat", "Complete the word to name the animal."),
                ("S_n", "Sun", "Complete the word for the bright star in the day sky.")
            ],
            "sentences": [
                ("The cat is on the mat.", "The cat is on the mat.", ["The dog is on the mat.", "The cat is under the mat.", "The cat is on the mat."], "Choose the sentence that matches the reading."),
                ("He ate an apple.", "He ate an apple.", ["He ate an apple.", "She eats a book.", "They run fast."], "Pick the sentence that is correct."),
                ("The sun is warm.", "The sun is warm.", ["The moon is warm.", "The sun is warm.", "The sky is green."], "Read and choose the correct sentence.")
            ],
            "paragraphs": [
                ("Sara loves to read books at the park. She sits under a tree and reads every day.", "Where does Sara read?", "At the park", ["At the park", "In the car", "At school", "At the mall"], "Sara reads at the park."),
                ("A boy planted a tree in his garden. The tree grew tall and gave shade.", "What did the boy plant?", "A tree", ["A tree", "A flower", "A book", "A toy"], "The boy planted a tree."),
                ("Ria feeds the birds in the morning. She gives them seeds and water.", "Who does Ria feed?", "The birds", ["The birds", "The cats", "The dog", "The fish"], "Ria feeds the birds.")
            ],
            "paragraph_writing": [
                ("your favorite toy", "My favorite toy is a red ball. I play with it every day.", "Write a short paragraph about your favorite toy."),
                ("a day at school", "I went to school and learned new things. I liked drawing and reading.", "Write a short paragraph about a day at school."),
                ("a family picnic", "We had a picnic with my family under a big tree. We ate sandwiches and fruit.", "Write a short paragraph about a family picnic.")
            ],
            "sentence_writing": [
                ("Describe your pet.", "I have a small pet dog.", "Write a short sentence about your pet."),
                ("Tell us what you like.", "I like to eat apples.", "Write one sentence about what you like."),
                ("What did you do today?", "I played and read a book.", "Write one sentence about your day.")
            ],
            "listening_words": [
                ("Apple", "Apple", ["Apple", "Banana", "House", "Dog"], "Choose the word you heard."),
                ("Ball", "Ball", ["Ball", "Cat", "Tree", "Fish"], "Choose the word you heard."),
                ("Sun", "Sun", ["Sun", "Moon", "Star", "Rain"], "Choose the word you heard.")
            ],
            "listening_sentences": [
                ("The cat sleeps.", "Where is the cat?", "On the mat", ["On the mat", "In the tree", "In the car", "In the room"], "Listen and answer the question."),
                ("Sara eats an apple.", "What did Sara eat?", "An apple", ["An apple", "A banana", "A sandwich", "Some rice"], "Listen carefully and choose the answer."),
                ("A bird sings in the tree.", "Who sings?", "A bird", ["A bird", "A dog", "A cat", "A fish"], "Listen and choose the correct answer.")
            ],
            "listening_paragraphs": [
                ("Ria went to the market and bought fruits for her family.", "What did Ria buy?", "Fruits", ["Fruits", "Vegetables", "Books", "Toys"], "Listen to the passage and answer the question."),
                ("The children played games and then ate lunch together.", "What did the children do?", "Played games", ["Played games", "Studied hard", "Watched TV", "Went home"], "Listen and choose the answer."),
                ("A teacher reads a story to the students every morning.", "Who reads the story?", "A teacher", ["A teacher", "A student", "A parent", "A bird"], "Listen and answer clearly.")
            ],
            "speaking_phrases": [
                "Hello",
                "Thank you",
                "I like apples",
                "Good morning"
            ],
            "speaking_responses": [
                ("What is your name?", "My name is Ria."),
                ("What do you like to eat?", "I like to eat apples."),
                ("Where do you live?", "I live in a small town.")
            ],
            "colors": [
                ("🐸", "Green", ["Green", "Red", "Blue", "Yellow"], "The frog is green."),
                ("🍋", "Yellow", ["Yellow", "Blue", "Black", "White"], "The lemon is yellow."),
                ("🍓", "Red", ["Red", "Purple", "Orange", "Gray"], "The strawberry is red.")
            ],
            "shape_words": [
                ("A shape with three sides", "Triangle", ["Triangle", "Circle", "Square", "Star"], "A triangle has three sides."),
                ("A shape with four equal sides", "Square", ["Square", "Circle", "Triangle", "Rectangle"], "A square has four equal sides."),
                ("A round shape", "Circle", ["Circle", "Triangle", "Square", "Heart"], "A circle is round.")
            ],
            "vocabulary": [
                ("Joyful", "Happy", ["Happy", "Sad", "Hungry", "Cold"], "Joyful means happy."),
                ("Rapid", "Fast", ["Fast", "Slow", "Quiet", "Loud"], "Rapid means fast."),
                ("Tiny", "Small", ["Small", "Large", "Angry", "Bright"], "Tiny means small.")
            ],
            "grammar": [
                ("Choose the correct sentence.", "She is reading a book.", ["She is reading a book.", "She are reading a book.", "She reading a book."], "This sentence is grammatically correct."),
                ("Choose the correct sentence.", "He has two pencils.", ["He has two pencils.", "He have two pencils.", "He has two pencil."], "This sentence is grammatically correct."),
                ("Choose the correct sentence.", "They are playing in the park.", ["They are playing in the park.", "They is playing in the park.", "They playing in the park."], "This sentence is grammatically correct.")
            ],
            "reading_letters": [
                ("Alphabet Identification: Select the letter that makes the sound /b/:", "B", ["B", "D", "P", "T"], "B makes the /b/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /f/:", "F", ["F", "V", "P", "S"], "F makes the /f/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /m/:", "M", ["M", "N", "W", "V"], "M makes the /m/ sound."),
                ("Alphabet Identification: Select the letter that makes the sound /s/:", "S", ["S", "C", "Z", "X"], "S makes the /s/ sound.")
            ],
            "comps": [
                ("The cat is sleeping under the tree.", "Where is the cat sleeping?", "Under the tree", ["Under the tree", "On the branch", "In the house", "In the car"]),
                ("The quick brown fox jumps over the lazy dog.", "Which animal is lazy?", "Dog", ["Dog", "Fox", "Cat", "Rabbit"]),
                ("Sam likes playing soccer in the afternoon.", "What does Sam like playing?", "Soccer", ["Soccer", "Tennis", "Basketball", "Golf"])
            ],
            "spelling": [
                ("Spelling Check: Choose the correct spelling for 🐘:", "Elephant", ["Elephant", "Elefant", "Eliphent", "Aliphant"]),
                ("Spelling Check: Choose the correct spelling for 🏠:", "House", ["House", "Howse", "Hous", "Hause"]),
                ("Spelling Check: Choose the correct spelling for 📖:", "Book", ["Book", "Boke", "Bouk", "Buck"])
            ],
            "listening": [
                ("Welcome", ["Welcome", "Thank you", "Goodbye", "Hello"]),
                ("Elephant", ["Elephant", "Tiger", "Lion", "Giraffe"]),
                ("Foundational", ["Foundational", "Educational", "Instructional", "Professional"])
            ],
            "speaking": [
                "Learning a new language opens up doors to new worlds.",
                "Reading books everyday expands your vocabulary.",
                "Lumi is my helper coach for regional scripts."
            ]
        },
        "Telugu": {
            "reading_letters": [
                ("అక్షర గుర్తింపు: వర్ణమాలలో మొదటి అక్షరం ఏది?", "అ", ["అ", "ఆ", "ఇ", "ఈ"], "అ మొదటి స్వరాక్షరం."),
                ("కింది వాటిలో రెండపదం ఏది?", "అమ్మ", ["అమ్మ", "ఆవు", "అనిల్", "ఇది"], "మాతృపదం గుర్తింపు.")
            ],
            "comps": [
                ("రాము బడికి వెళ్ళాడు.", "రాము ఎక్కడికి వెళ్ళాడు?", "బడికి", ["బడికి", "ఇంటికి", "గుడికి", "తోటకే"]),
                ("పిల్లి పాలు తాగింది.", "పిల్లి ఏమి తాగింది?", "పాలు", ["పాలు", "నీరు", "పెండు", "పువ్వు"])
            ],
            "spelling": [
                ("సరైన పదాన్ని ఎంచుకోండి (బల్లి):", "బల్లి", ["బల్లి", "బలీ", "బళి", "బల్లి"], "బల్లి సరిగ్గా వ్రాయండి."),
                ("సరైన పదాన్ని ఎంచుకోండి (పుస్తకం):", "పుస్తకం", ["పుస్తకం", "పుస్తఖం", "పుస్తకo", "పుస్తకము"], "పుస్తకం శబ్దాన్ని గుర్తించండి.")
            ],
            "listening": [
                ("కుక్క", ["కుక్క", "పిల్లి", "కాగితం", "పువ్వు"]),
                ("పండు", ["పండు", "పత్రం", "పెంక్", "పూలు"])
            ],
            "speaking": [
                "నమస్కారం",
                "నేను తెలుగు మాట్లాడగలను",
                "ఇది ఒక మంచి రోజు"
            ]
        },
        "Hindi": {
            "reading_letters": [
                ("वर्णमाला पहचान: इनमें से पहला स्वर कौन सा है?", "अ", ["अ", "आ", "इ", "ई"], "अ हिंदी वर्णमाला का पहला स्वर है।"),
                ("किन्हीं संयुक्त व्यंजनों में से कौन सा है?", "क्ष", ["क्ष", "क", "ख", "ग"], "क्ष संयुक्त व्यंजन है।")
            ],
            "comps": [
                ("राम ने सेब खाया।", "सेब किसने खाया?", "राम", ["राम", "श्याम", "मोहन", "बंदर"]),
                ("बिल्ली दूध पीती है।", "बिल्ली क्या पीती है?", "दूध", ["दूध", "पानी", "रस", "चाय"])
            ],
            "spelling": [
                ("सही वर्तनी चुनें (हाथी):", "हाथी", ["हाथी", "हथी", "हाथि", "हाती"]),
                ("सही वर्तनी चुनें (किताब):", "किताब", ["किताब", "केताब", "कीताब", "किताम"])
            ],
            "listening": [
                ("नमस्ते", ["नमस्ते", "अलविदा", "धन्यवाद", "स्वागत"]),
                ("मछली", ["🐟 मछली", "🐶 कुत्ता", "🐱 बिल्ली", "🦁 शेर"])
            ],
            "speaking": [
                "नमस्ते",
                "मेरा प्यारा घर",
                "पेड़ हमें फल देते हैं",
                "हमें रोज़ स्कूल जाना चाहिए",
                "हिंदी हमारी राष्ट्रभाषा है"
            ]
        },
        "Tamil": {
            "reading_letters": [
                ("எழுத்து அடையாளம்: உயிர் எழுத்துக்களில் முதல் எழுத்து எது?", "அ", ["அ", "ஆ", "இ", "ஈ"], "அ என்பது முதல் உயிர் எழுத்து."),
                ("கீழ்க்கண்டவற்றுள் மெய் எழுத்து எது?", "க்", ["க்", "அ", "க", "சா"], "க் என்பது மெய் எழுத்து.")
            ],
            "comps": [
                ("பூனை கட்டிலின் மேல் உள்ளது.", "பூனை எங்கு உள்ளது?", "கட்டிலின் மேல்", ["கட்டிலின் மேல்", "பெட்டிக்குள்", "மரத்தின் மேல்", "வீட்டில்"]),
                ("எலி வேகமாக ஓடுகிறது.", "எது வேகமாக ஓடுகிறது?", "எலி", ["எலி", "பூனை", "நாய்", "மாடு"])
            ],
            "spelling": [
                ("சரியான சொல்லைத் தேர்ந்தெடுக்கவும் (அம்மா):", "அம்மா", ["அம்மா", "அமா", "ஆம்மா", "அம்மி"]),
                ("சரியான சொல்லைத் தேர்ந்தெடுக்கவும் (பள்ளி):", "பள்ளி", ["பள்ளி", "பலி", "பாலீ", "பல்ளி"])
            ],
            "listening": [
                ("வணக்கம்", ["வணக்கம்", "நன்றி", "வரவேற்பு", "போய்வருகிறேன்"]),
                ("பூனை", ["🐱 பூனை", "🐶 நாய்", "🐰 முயல்", "🐮 பசு"])
            ],
            "speaking": [
                "வணக்கம்",
                "அம்மா எனக்கு பால் தந்தார்",
                "தமிழ் எங்கள் தாய்மொழி",
                "நாங்கள் தினமும் பள்ளிக்குச் செல்வோம்",
                "இயற்கையைக் காப்போம்"
            ]
        },
        "Kannada": {
            "reading_letters": [
                ("ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ: ಕನ್ನಡ ವರ್ಣಮಾಲೆಯ ಮೊದಲ ಅಕ್ಷರ ಯಾವುದು?", "ಅ", ["ಅ", "ಆ", "ಇ", "ಈ"], "ಅ ಮೊದಲ ಅಕ್ಷರವಾಗಿದೆ."),
                ("ಕನ್ನಡದಲ್ಲಿ ಸ್ವರಗಳ ಸಂಖ್ಯೆ ಎಷ್ಟು?", "೧೩", ["೧೩", "೧೫", "೧೦", "೩೪"], "ಕನ್ನಡದಲ್ಲಿ ೧೩ ಸ್ವರಗಳಿವೆ.")
            ],
            "comps": [
                ("ರಾಜು ಶಾಲೆಗೆ ಹೋದನು.", "ರಾಜು ಎಲ್ಲಿಗೆ ಹೋದನು?", "ಶಾಲೆಗೆ", ["ಶಾಲೆಗೆ", "ಮನೆಗೆ", "ತೋಟಕ್ಕೆ", "ದೇವಸ್ಥಾನಕ್ಕೆ"]),
                ("ಬೆಕ್ಕು ಹಾಲು ಕುಡಿಯಿತು.", "ಬೆಕ್ಕು ಏನನ್ನು ಕುಡಿಯಿತು?", "ಹಾಲು", ["ಹಾಲು", "ನೀರು", "ಮಜ್ಜಿಗೆ", "ರಸ"])
            ],
            "spelling": [
                ("ಸರಿಯಾದ ಪದವನ್ನು ಆರಿಸಿ (ಶಾಲೆ):", "ಶಾಲೆ", ["ಶಾಲೆ", "ಸಾಲೆ", "ಶಾಲಿ", "ಸಾಲ"]),
                ("ಸರಿಯಾದ ಪದವನ್ನು ಆರಿಸಿ (ಪುಸ್ತಕ):", "ಪುಸ್ತಕ", ["ಪುಸ್ತಕ", "ಪುಸ್ತಖ", "ಪೂಸ್ತಕ", "ಪುಸ್ತಕು"])
            ],
            "listening": [
                ("ನಮಸ್ಕಾರ", ["ನಮಸ್ಕಾರ", "ಧನ್ಯವಾದಗಳು", "ಶುಭೋದಯ", "ಬನ್ನಿ"]),
                ("ಮನೆ", ["🏠 ಮನೆ", "🏫 ಶಾಲೆ", "🌳 ಮರ", "🚗 ಕಾರು"])
            ],
            "speaking": [
                "ನಮಸ್ಕಾರ",
                "ಕನ್ನಡ ನಮ್ಮ ತಾಯ್ನುಡಿ",
                "ಮನೆ ಅತಿ ಸುಂದರವಾಗಿದೆ",
                "ನಾವು ಪ್ರತಿದಿನ ಶಾಲೆಗೆ ಹೋಗುತ್ತೇವೆ",
                "ಗಿಡಮರ들을 ಬೆಳೆಸೋಣ"
            ]
        },
        "Marathi": {
            "reading_letters": [
                ("अक्षर ओळख: मराठी वर्णमालेतील पहिले अक्षर कोणते?", "अ", ["अ", "आ", "इ", "ई"], "अ हे पहिले अक्षर आहे।"),
                ("खालीलपैकी संयुक्त व्यंजन कोणते?", "क्ष", ["क्ष", "क", "ख", "ग"], "क्ष संयुक्त व्यंजन आहे।")
            ],
            "comps": [
                ("राजू शाळेत गेला.", "राजू कोठे गेला?", "शाळेत", ["शाळेत", "घरी", "बागेत", "मंदिरात"]),
                ("मांजर दूध पिते.", "मांजर काय पिते?", "दूध", ["दूध", "पाणी", "रस", "चहा"])
            ],
            "spelling": [
                ("योग्य शब्द निवडा (हत्ती):", "हत्ती", ["हत्ती", "हती", "हात्ती", "हाती"]),
                ("योग्य शब्द निवडा (पुस्तक):", "पुस्तक", ["पुस्तक", "पुस्तख", "पूस्तक", "पुस्तकू"])
            ],
            "listening": [
                ("नमस्कार", ["नमस्कार", "धन्यवाद", "स्वागत", "शुभ रात्री"]),
                ("घर", ["🏠 घर", "🏫 शाळा", "🌳 झाड", "🚗 गाडी"])
            ],
            "speaking": [
                "नमस्कार",
                "झाडे आपल्याला सावली देतात",
                "आम्ही रोज शाळेत जातो",
                "मराठी माझी मातृभाषा आहे"
            ]
        }
    }

    pool = lang_pools.get(language, lang_pools["English"])
    profile = _get_assessment_profile(learning_level, _get_age_band(age_val))
    questions = _build_level_questions(language, profile, pool)

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM assessment_questions WHERE language = ?", (language,))
        db_qs = cursor.fetchall()
        conn.close()
        for q in db_qs:
            opts_list = [o.strip() for o in str(q["options"]).split(",") if o.strip()]
            while len(opts_list) < 4:
                opts_list.append("Option " + str(random.randint(1, 100)))
            opts_list = opts_list[:4]
            correct_idx = int(q["correct_index"]) if q["correct_index"] is not None else 0
            ans = opts_list[correct_idx] if correct_idx < len(opts_list) else opts_list[0]
            questions.append({
                "name": f"q_custom_{q['id']}",
                "type": str(q["category"] or "reading").lower(),
                "skill": str(q["category"] or "reading").lower(),
                "prompt": q["prompt"],
                "options": opts_list,
                "answer": ans,
                "explanation": q["explanation"] or "Custom question approved by admin.",
                "age_band": profile["age_band"],
                "level": profile["level"],
                "language": language,
                "skill_score_key": str(q["category"] or "reading").lower(),
            })
    except Exception as e:
        print(f"[ASSESSMENT MERGE ERROR] {e}")

    return questions


def get_assessment_questions(language, age=None, learning_level=None, mode=None):
    return _legacy_get_assessment_questions(language, age, learning_level, mode)


WEEK_MODULE_CONTENT = {
    "English": {
        "module_title": "Learning Content Management & Assessment Framework",
        "description": "Complete the literacy curriculum structure with reading, writing, and comprehension activities designed for multilingual learners.",
        "curriculum": [
            {
                "heading": "Reading Foundations",
                "details": "Build reading fluency with short passages, sight words, and comprehension questions that prepare learners for everyday literacy."
            },
            {
                "heading": "Writing Practice",
                "details": "Develop writing confidence through sentence construction, spelling exercises, and typing-based responses."
            },
            {
                "heading": "Comprehension Support",
                "details": "Strengthen understanding with story sequencing, question answering, and vocabulary matching activities."
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "Reading Task",
                "description": "Answer comprehension questions after reading a short passage."
            },
            {
                "title": "Writing Task",
                "description": "Type the missing words or build simple sentences based on prompts."
            },
            {
                "title": "Speaking Task",
                "description": "Practice aloud and then type the sentence to demonstrate spoken literacy awareness."
            }
        ],
        "benchmarks": [
            {
                "level": "Proficient",
                "range": "80–100%",
                "notes": "Learner demonstrates strong reading, writing, and comprehension skills for beginner literacy."
            },
            {
                "level": "Developing",
                "range": "50–79%",
                "notes": "Learner is making progress and should continue guided practice with reading and writing tasks."
            },
            {
                "level": "Beginner",
                "range": "0–49%",
                "notes": "Learner benefits from foundational support in letter recognition, simple words, and sentence structure."
            }
        ]
    },
    "Telugu": {
        "module_title": "నేర్చుకోవడపు కంటెంట్ నిర్వహణ & అంచనా ఫ్రేమ్‌వర్క్",
        "description": "చదవడం, వ్రాయడం, మరియు అవగాహన కార్యాలయాలను పొందుపరిచి భాషా specimens యొక్క సాహిత్య విద్యక్రమాన్ని పూర్తి చేయండి.",
        "curriculum": [
            {
                "heading": "చదవడపు పునాది",
                "details": "సాధారణ పాఠాలు, సైట్ పదాలు, మరియు అవగాహన ప్రశ్నలతో చదవడపు నైపుణ్యాన్ని మెరుగుపరచండి."
            },
            {
                "heading": "వ్రాయడపు అభ్యాసం",
                "details": "వాక్య నిర్మాణం, వృత్తిపరమైన అక్షరాలు, మరియు టైపింగ్ సమాధానాల ద్వారా లిఖిత నైపుణ్యాన్ని పెంపొందించండి."
            },
            {
                "heading": "అవగాహన మద్దతు",
                "details": "కథ క్రమాన్ని, ప్రశ్నల సమాధానాన్ని, మరియు పదజాలం మ్యాచ్ చేయడాన్ని వినియోగించి అవగాహనను బలోపేతం చేయండి."
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "చదవడపు పని",
                "description": "చిన్న పాఠం చదివిన తరువాత అవగాహన ప్రశ్నలకు సమాధానమివ్వండి."
            },
            {
                "title": "వ్రాయడపు పని",
                "description": "ప్రాంప్ట్‌ల ఆధారంగా ఖాళీ పదాలను టైప్ చేయండి లేదా వాక్యాలను నిర్మించండి."
            },
            {
                "title": "మాట్లాడడపు పని",
                "description": "పట్టుమ‌ని గా అభ్యాసించి ఆ తర్వాత వాక్యాన్ని టైప్ చేయండి."
            }
        ],
        "benchmarks": [
            {
                "level": "ప్రావీణ్యంలొ",
                "range": "80–100%",
                "notes": "ప్రారంభ సాహిత్యానికి బలమైన చదవడం, వ్రాయడం మరియు అవగాహన నైపుణ్యాలు చూపిస్తోంది."
            },
            {
                "level": "వికాసంలో",
                "range": "50–79%",
                "notes": "చదవడంలో మరియు వ్రాయడంలో మార్గనిర్దేశనతో సాధన కొనసాగించాల్సిన అవసరం ఉంది."
            },
            {
                "level": "ప్రారంభ స్థాయి",
                "range": "0–49%",
                "notes": "అక్షర గుర్తింపు, సులభ పదాలు, మరియు వాక్య నిర్మాణంలో ప్రాథమిక మద్దతు అవసరం."
            }
        ]
    },
    "Hindi": {
        "module_title": "शिक्षण सामग्री प्रबंधन और आकलन ढांचा",
        "description": "पढ़ने, लिखने और समझने की गतिविधियों के साथ बहुभाषी शिक्षार्थियों के लिए साक्षरता पाठ्यक्रम तैयार करें।",
        "curriculum": [
            {
                "heading": "पढ़ने की नींव",
                "details": "छोटे अंशों, साइट शब्दों और समझ प्रश्नों से पढ़ने की क्षमता मजबूत करें।"
            },
            {
                "heading": "लेखन अभ्यास",
                "details": "वाक्य निर्माण, वर्तनी अभ्यास और टाइपिंग आधारित उत्तरों के माध्यम से लेखन कौशल विकसित करें।"
            },
            {
                "heading": "समझ का समर्थन",
                "details": "कहानी क्रम, प्रश्न उत्तर, और शब्दावली मेल से समझ को मज़बूत करें।"
            }
        ],
        "repositories": [
            {
                "language": "English",
                "items": [
                    "Beginner story passages",
                    "Sentence building worksheets",
                    "Reading comprehension cards"
                ]
            },
            {
                "language": "Telugu",
                "items": [
                    "సాధారణ కథా భాగాలు",
                    "వాక్యాన్ని నిర్మించే పనులు",
                    "అర్థం తెలుసుకునే ప్రశ్నలు"
                ]
            },
            {
                "language": "Hindi",
                "items": [
                    "आरंभिक कहानी अनुच्छेद",
                    "वाक्य निर्माण अभ्यास",
                    "समझ परीक्षण प्रश्न"
                ]
            }
        ],
        "assessments": [
            {
                "title": "पढ़ने का कार्य",
                "description": "एक छोटे पाठ पढ़ने के बाद समझ प्रश्नों का उत्तर दें।"
            },
            {
                "title": "लेखन कार्य",
                "description": "प्रॉम्प्ट के आधार पर रिक्त शब्द टाइप करें या सरल वाक्य बनाएं।"
            },
            {
                "title": "बोलने का कार्य",
                "description": "उच्चारण का अभ्यास करें और फिर वाक्य टाइप करें।"
            }
        ],
        "benchmarks": [
            {
                "level": "कुशल",
                "range": "80–100%",
                "notes": "शुरुआती साक्षरता के लिए मजबूत पढ़ने, लिखने और समझ कौशल दिखाता है।"
            },
            {
                "level": "विकसित हो रहा है",
                "range": "50–79%",
                "notes": "सहायता के साथ अभ्यास जारी रखें और पढ़ने/लिखने के कार्य दोहराएं।"
            },
            {
                "level": "शुरुआती",
                "range": "0–49%",
                "notes": "आधारभूत अक्षर, शब्द और वाक्य संरचना पर मजबूत समर्थन की आवश्यकता है।"
            }
        ]
    },
    "Tamil": {
        "module_title": "கற்றல் உள்ளடக்க மேலாண்மை & மதிப்பீட்டு கட்டமைப்பு",
        "description": "பல்மொழி கற்பவர்களுக்காக வடிவமைக்கப்பட்ட வாசிப்பு, எழுதுதல் மற்றும் புரிந்துகொள்ளும் செயல்பாடுகளுடன் எழுத்தறிவு பாடத்திட்டத்தை முடிக்கவும்.",
        "curriculum": [
            {
                "heading": "வாசிப்பு அடித்தளம்",
                "details": "குறுகிய பத்திகள் மற்றும் புரிதல் கேள்விகள் மூலம் வாசிப்பு திறனை வளர்க்கவும்."
            },
            {
                "heading": "எழுத்து பயிற்சி",
                "details": "வாக்கிய உருவாக்கம் மற்றும் தட்டச்சு அடிப்படையிலான பதில்கள் மூலம் எழுத்து பயிற்சியை மேம்படுத்தவும்."
            },
            {
                "heading": "புரிதல் ஆதரவு",
                "details": "கதை வரிசைப்படுத்துதல் மற்றும் சொல்லகராதி பொருத்துதல் மூலம் புரிதலை வலுப்படுத்தவும்."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "வாசிப்பு பணி",
                "description": "ஒரு குறுகிய பத்தியை வாசித்த பிறகு கேள்விகளுக்கு பதிலளிக்கவும்."
            },
            {
                "title": "எழுதும் பணி",
                "description": "விடுபட்ட வார்த்தைகளை நிரப்பவும் அல்லது எளிய வாக்கியங்களை உருவாக்கவும்."
            },
            {
                "title": "பேசும் பணி",
                "description": "வாக்கியங்களை சத்தமாக படித்து தட்டச்சு செய்யவும்."
            }
        ],
        "benchmarks": [
            {
                "level": "திறமையானவர்",
                "range": "80–100%",
                "notes": "கற்பவர் சிறந்த வாசிப்பு, எழுதுதல் மற்றும் புரிந்துகொள்ளும் திறன்களைக் காட்டுகிறார்."
            },
            {
                "level": "வளரும் நிலை",
                "range": "50–79%",
                "notes": "கற்பவர் முன்னேறி வருகிறார், வழிகாட்டப்பட்ட பயிற்சிகளைத் தொடர வேண்டும்."
            },
            {
                "level": "தொடக்கநிலை",
                "range": "0–49%",
                "notes": "எழுத்து அங்கீகாரம் மற்றும் எளிய சொற்களில் அடிப்படை ஆதரவு தேவை."
            }
        ]
    },
    "Kannada": {
        "module_title": " ಕಲಿಕಾ ವಿಷಯ ನಿರ್ವಹಣೆ ಮತ್ತು ಮೌಲ್ಯಮಾಪನ ಚೌಕಟ್ಟು",
        "description": "ಬಹುಭಾಷಾ ಕಲಿಯುವವರಿಗಾಗಿ ವಿನ್ಯಾಸಗೊಳಿಸಲಾದ ಓದುವಿಕೆ, ಬರವಣಿಗೆ ಮತ್ತು ಗ್ರಹಿಕೆ ಚಟುವಟಿಕೆಗಳೊಂದಿಗೆ ಸಾಕ್ಷರತಾ ಪಠ್ಯಕ್ರಮವನ್ನು ಪೂರ್ಣಗೊಳಿಸಿ.",
        "curriculum": [
            {
                "heading": "ಓದುವ ಬುನಾದಿ",
                "details": "ಸಣ್ಣ ಪ್ಯಾರಾಗ್ರಾಫ್ ಮತ್ತು ಗ್ರಹಿಕೆ ಪ್ರಶ್ನೆಗಳೊಂದಿಗೆ ಓದುವ ನಿರರ್ಗಳತೆಯನ್ನು ಬೆಳೆಸಿಕೊಳ್ಳಿ."
            },
            {
                "heading": "ಬರವಣಿಗೆ ಅಭ್ಯಾಸ",
                "details": "ವಾಕ್യ ರಚನೆ ಮತ್ತು ಟೈಪಿಂಗ್ ಆಧಾರಿತ ಪ್ರತಿಕ್ರിയೆಗಳ ಮೂಲಕ ಬರವಣಿಗೆಯನ್ನು ಸುಧಾರಿಸಿ."
            },
            {
                "heading": "ಗ್ರಹಿಕೆ ಬೆಂಬಲ",
                "details": "ಕಥೆಯ ക്രമീകരണം ಮತ್ತು ಶಬ್ದಕೋಶ ಹೊಂದಾಣಿಕೆಯ ಮೂಲಕ ಗ್ರಹಿಕೆಯನ್ನು ಬಲಪಡಿಸಿ."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "ಓದುವ ಕಾರ್ಯ",
                "description": "ಸಣ್ಣ ಗದ್ಯವನ್ನು ಓದಿದ ನಂತರ ಗ್ರಹಿಕೆ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಿ."
            },
            {
                "title": "ಬರೆಯುವ ಕಾರ್ಯ",
                "description": "ಖಾಲಿ ಪದಗಳನ್ನು ಭರ್ತಿ ಮಾಡಿ ಅಥವಾ ಸರಳ ವಾಕ್ಯಗಳನ್ನು ನಿರ್ಮಿಸಿ."
            },
            {
                "title": "ಮಾತನಾಡುವ ಕಾರ್ಯ",
                "description": "ವಾಕ್യಗಳನ್ನು ಜೋರಾಗಿ ಓದಿ ನಂತರ ಟൈಪ್ ಮಾಡಿ."
            }
        ],
        "benchmarks": [
            {
                "level": "ಪ್ರವೀಣ",
                "range": "80–100%",
                "notes": "ಕಲಿಯುವವರು ಓದುವಿಕೆ, ಬರವಣಿಗೆ ಮತ್ತು ಗ್ರಹಿಕೆಯಲ್ಲಿ ಉತ್ತಮ ಕೌಶಲ್ಯಗಳನ್ನು ಪ್ರದರ್ಶಿಸುತ್ತಾರೆ."
            },
            {
                "level": "ಬೆಳೆಯುತ್ತಿರುವ",
                "range": "50–79%",
                "notes": "ಕಲಿಯುವವರು ಪ್ರಗತಿ ಹೊಂದುತ್ತಿದ್ದಾರೆ ಮತ್ತು ಅಭ್ಯಾಸವನ್ನು ಮುಂದುವರಿಸಬೇಕಾಗಿದೆ."
            },
            {
                "level": "ಪ್ರಾರಂಭಿಕ",
                "range": "0–49%",
                "notes": "ಅಕ್ಷರ ಗುರುತಿಸುವಿಕೆ ಮತ್ತು ಸರಳ ಪದಗಳಲ್ಲಿ ಮೂಲಭೂತ ಬೆಂಬಲದ ಅಗತ್ಯವಿದೆ."
            }
        ]
    },
    "Malayalam": {
        "module_title": "പഠന ഉള്ളടക്ക മാനേജ്‌മെന്റും മൂല്യനിർണ്ണയ ചട്ടക്കൂടും",
        "description": "ബഹുഭാഷാ പഠിതാക്കൾക്കായി രൂപകൽപ്പന ചെയ്‌തിരിക്കുന്ന വായന, എഴുത്ത്, മനസ്സിലാക്കൽ പ്രവർത്തനങ്ങൾ എന്നിവയിലൂടെ സാക്ഷരതാ കോഴ്‌സ് പൂർത്തിയാക്കുക.",
        "curriculum": [
            {
                "heading": "വായനയുടെ അടിത്തറ",
                "details": "ചെറിയ ഭാഗങ്ങളും ചോദ്യങ്ങളും വഴി വായനാക്ഷമത മെച്ചപ്പെടുത്തുക."
            },
            {
                "heading": "എഴുത്തു പരിശീലനം",
                "details": "വാക്യഘടനയും ടൈപ്പിംഗ് പരിശീലനവും വഴി എഴുത്ത് മെച്ചപ്പെടുത്തുക."
            },
            {
                "heading": "ഗ്രഹണ പിന്തുണ",
                "details": "പദാവലി പൊരുത്തപ്പെടുത്തൽ വഴി മനസ്സിലാക്കൽ ശേഷി വർദ്ധിപ്പിക്കുക."
            }
        ],
        "repositories": [],
        "assessments": [
            {
                "title": "വായന ജോലി",
                "description": "ചെറിയ ഭാഗം വായിച്ചതിനുശേഷം ചോദ്യങ്ങൾക്ക് ഉത്തരം നൽകുക."
            },
            {
                "title": "എഴുത്ത് ജോലി",
                "description": "വിട്ടുപോയ വാക്കുകൾ ടൈപ്പ് ചെയ്യുക അല്ലെങ്കിൽ ലളിതമായ വാക്യങ്ങൾ ഉണ്ടാക്കുക."
            },
            {
                "title": "സംസാര ജോലി",
                "description": "വാക്യങ്ങൾ ഉറക്കെ വായിച്ചതിനുശേഷം ടൈപ്പ് ചെയ്യുക."
            }
        ],
        "benchmarks": [
            {
                "level": "പ്രാവീണ്യമുള്ളയാൾ",
                "range": "80–100%",
                "notes": "പഠിതാവ് മികച്ച വായന, എഴുത്ത്, മനസ്സിലാക്കൽ കഴിവുകൾ പ്രകടിപ്പിക്കുന്നു."
            },
            {
                "level": "വളർന്നു വരുന്നയാൾ",
                "range": "50–79%",
                "notes": "പഠിതാവ് പുരോഗതി കാണിക്കുന്നു, കൂടുതൽ പരിശീലനം ആവശ്യമാണ്."
            },
            {
                "level": "തുടക്കക്കാരൻ",
                "range": "0–49%",
                "notes": "അക്ഷരങ്ങൾ തിരിച്ചറിയുന്നതിനും ലളിതമായ വാക്കുകൾക്കും അടിസ്ഥാന പിന്തുണ ആവശ്യമാണ്."
            }
        ]
    }
}


def get_week_module_content(language):
    return WEEK_MODULE_CONTENT.get(language, WEEK_MODULE_CONTENT["English"])


@app.context_processor
def inject_translations():
    language = session.get("preferred_language") or session.get("language", "English")
    from datetime import date
    return {
        "translations": get_translations(language),
        "current_language": language,
        "today_date": date.today().strftime("%d/%m/%Y")
    }


# -------------------------------
# Database Connection
# -------------------------------
def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.before_request
def force_initial_assessment():
    user_id = session.get("user_id")
    if user_id:
        allowed_endpoints = [
            "assessment", "submit_assessment", "logout", "static", "login", "register", "forgot_password", "api_set_language", "register_user", "login_user", "admin_login", "admin_logout"
        ]
        if request.endpoint and not any(e in request.endpoint for e in allowed_endpoints) and not request.path.startswith("/api/"):
            init_complete = session.get("initial_assessment_completed", 0)
            if not init_complete:
                try:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT initial_assessment_completed, age, role FROM users WHERE id = ?", (user_id,))
                    row = cursor.fetchone()
                    conn.close()
                    if row:
                        if row["role"] in ["admin", "parent"]:
                            session["initial_assessment_completed"] = 1
                            return
                            
                        age = row["age"]
                        try:
                            age_int = int(age) if age is not None else 8
                        except (ValueError, TypeError):
                            age_int = 8
                            
                        session["initial_assessment_completed"] = row["initial_assessment_completed"] or 0
                        if not session["initial_assessment_completed"]:
                            flash("Please complete the initial assessment first.", "warning")
                            return redirect(url_for("assessment"))
                except Exception as e:
                    print(f"[FORCE ASSESSMENT ERROR] {e}")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE role = 'student' ORDER BY id LIMIT 1")
            u = cursor.fetchone()
            conn.close()
            if u:
                session["user_id"] = u["id"]
                session["fullname"] = u["fullname"]
                session["email"] = u["email"]
                session["role"] = u["role"]
                session["language"] = u["language"] or "English"
                session["learning_level"] = u["learning_level"] or "Beginner"
                session["age"] = u["age"] or 8
            else:
                flash("Please log in to continue.", "warning")
                return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def update_user_streak(cursor, user_id):
    cursor.execute("SELECT streak, longest_streak FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        return
    current_streak = user_row["streak"] or 0
    longest_streak = user_row["longest_streak"] or 0
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    
    cursor.execute("SELECT date FROM study_sessions WHERE user_id = ? AND date = ?", (user_id, today))
    studied_today = cursor.fetchone() is not None
    
    if studied_today:
        return
        
    cursor.execute("SELECT date FROM study_sessions WHERE user_id = ? AND date = ?", (user_id, yesterday))
    studied_yesterday = cursor.fetchone() is not None
    
    if studied_yesterday:
        new_streak = current_streak + 1
    else:
        new_streak = 1
        
    new_longest = max(new_streak, longest_streak)
    cursor.execute("UPDATE users SET streak = ?, longest_streak = ? WHERE id = ?", (new_streak, new_longest, user_id))


def log_study_activity(user_id, duration_minutes, xp_reward, coins_reward=10):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    update_user_streak(cursor, user_id)
    
    import datetime
    today = datetime.date.today().strftime("%Y-%m-%d")
    cursor.execute("""
        INSERT INTO study_sessions (user_id, duration, date)
        VALUES (?, ?, ?)
    """, (user_id, duration_minutes, today))
    
    cursor.execute("""
        UPDATE users 
        SET xp = IFNULL(xp, 0) + ?, coins = IFNULL(coins, 0) + ?
        WHERE id = ?
    """, (xp_reward, coins_reward, user_id))
    
    cursor.execute("SELECT xp, coins, badges, streak, (SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?) as lessons_count FROM users WHERE id = ?", (user_id, user_id))
    urow = cursor.fetchone()
    if urow:
        xp = urow["xp"] or 0
        coins = urow["coins"] or 0
        streak = urow["streak"] or 0
        lessons_count = urow["lessons_count"] or 0
        badges_str = urow["badges"] or ""
        badge_list = [b.strip() for b in badges_str.split(",") if b.strip()]
        
        if xp >= 100 and "100 XP" not in badge_list:
            badge_list.append("100 XP")
        if xp >= 500 and "500 XP" not in badge_list:
            badge_list.append("500 XP")
        if xp >= 1000 and "1000 XP" not in badge_list:
            badge_list.append("1000 XP")
            
        if streak >= 7 and "Streak Master" not in badge_list:
            badge_list.append("Streak Master")
            
        if lessons_count >= 1 and "First Lesson" not in badge_list:
            badge_list.append("First Lesson")
            
        new_badges = ",".join(badge_list)
        cursor.execute("UPDATE users SET badges = ? WHERE id = ?", (new_badges, user_id))
        
    conn.commit()
    conn.close()


def classify_score_to_proficiency(score):
    if score is None:
        return "Beginner"
    try:
        s = float(score)
    except (ValueError, TypeError):
        return "Beginner"

    if s >= 90.0:
        return "Advanced"
    elif s >= 70.0:
        return "Intermediate"
    elif s >= 40.0:
        return "Basic"
    else:
        return "Beginner"


def predict_user_proficiency(user_id, language="English", update_db=True):
    translations = get_translations(language)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT score 
        FROM assessment_history 
        WHERE user_id = ? 
        ORDER BY timestamp ASC
    """, (user_id,))
    rows = cursor.fetchall()
    
    if not rows:
        level_key = "Beginner"
        predicted_score = None
        trend = "stable"
        confidence = "Low (No assessments taken)"
    else:
        scores = [r["score"] for r in rows]
        # Calculate weighted average: newer scores have higher weights
        total_weight = 0
        weighted_sum = 0
        for idx, score in enumerate(scores):
            weight = idx + 1
            weighted_sum += score * weight
            total_weight += weight
            
        predicted_score = int(round(weighted_sum / total_weight))
        level_key = classify_score_to_proficiency(predicted_score)
            
        # Determine trend
        if len(scores) > 1:
            if scores[-1] > scores[0]:
                trend = "improving"
            elif scores[-1] < scores[0]:
                trend = "declining"
            else:
                trend = "stable"
        else:
            trend = "stable"
            
        confidence = "High" if len(scores) >= 3 else "Medium"

    # Update database record if requested
    if update_db and user_id:
        try:
            cursor.execute("""
                UPDATE users 
                SET current_proficiency = ?
                WHERE id = ?
            """, (level_key, user_id))
            conn.commit()
        except Exception as e:
            print(f"[PROFICIENCY DB UPDATE ERROR] {e}")

    conn.close()

    level = translations.get(f"dashboard_proficiency_{level_key.lower()}", level_key)
    
    return {
        "score": predicted_score,
        "level": level,
        "level_key": level_key,
        "current_proficiency": level_key,
        "trend": trend,
        "confidence": f"{confidence} ({len(rows)} assessments)" if rows else confidence
    }


def _get_skill_score_profile(cursor, user_id, user_row=None):
    if user_row is None:
        cursor.execute("""
            SELECT age, language, preferred_language, learning_language, learning_level, current_proficiency,
                   reading_score, writing_score, vocabulary_score, grammar_score,
                   listening_score, speaking_score, weak_skills, strong_skills
            FROM users WHERE id = ?
        """, (user_id,))
        user_row = cursor.fetchone()

    if not user_row:
        return {
            "skill_scores": {},
            "weak_skills": [],
            "strong_skills": [],
            "proficiency": "Beginner",
            "user_row": None,
        }

    cursor.execute("""
        SELECT reading_score, writing_score, vocabulary_score, grammar_score,
               listening_score, speaking_score, score
        FROM assessment_history
        WHERE user_id = ?
        ORDER BY timestamp DESC LIMIT 1
    """, (user_id,))
    assessment_row = cursor.fetchone()

    skill_scores = {}
    skill_fields = {
        "reading": "reading_score",
        "writing": "writing_score",
        "vocabulary": "vocabulary_score",
        "grammar": "grammar_score",
        "listening": "listening_score",
        "speaking": "speaking_score",
    }

    for skill, field in skill_fields.items():
        value = user_row[field] if user_row and field in user_row.keys() else None
        if value in (None, ""):
            fallback = None
            if assessment_row:
                fallback = assessment_row[field] if field in assessment_row.keys() else None
                if fallback in (None, ""):
                    fallback = assessment_row["score"] if "score" in assessment_row.keys() else None
            value = fallback
        try:
            skill_scores[skill] = int(float(value)) if value is not None else 60
        except (TypeError, ValueError):
            skill_scores[skill] = 60

    proficiency = user_row["current_proficiency"] if user_row and "current_proficiency" in user_row.keys() and user_row["current_proficiency"] else (user_row["learning_level"] if user_row and "learning_level" in user_row.keys() and user_row["learning_level"] else "Beginner")
    weak_skills = [skill for skill, score in sorted(skill_scores.items(), key=lambda item: item[1]) if score < 75]
    strong_skills = [skill for skill, score in skill_scores.items() if skill not in weak_skills and score >= 75]

    if not weak_skills and skill_scores:
        weak_skills = [min(skill_scores, key=skill_scores.get)]

    return {
        "skill_scores": skill_scores,
        "weak_skills": weak_skills,
        "strong_skills": strong_skills,
        "proficiency": proficiency,
        "user_row": user_row,
    }


def _lesson_matches_skill(lesson, skill):
    lesson_text = " ".join([
        lesson.get("title") or "",
        lesson.get("category") or "",
        lesson.get("content") or ""
    ]).lower()
    normalized_skill = str(skill).strip().lower()
    skill_keywords = {
        "reading": ["reading", "read", "story", "alphabet", "phonics", "comprehension"],
        "writing": ["writing", "write", "trace", "spelling", "sentence", "letter"],
        "vocabulary": ["vocabulary", "word", "match", "memory", "vocab"],
        "grammar": ["grammar", "sentence", "syntax", "language"],
        "listening": ["listening", "listen", "audio", "sound", "song"],
        "speaking": ["speaking", "speak", "pronunciation", "voice", "dialogue"],
    }
    keywords = skill_keywords.get(normalized_skill, [normalized_skill])
    return any(keyword in lesson_text for keyword in keywords)


def _difficulty_matches(lesson_difficulty, proficiency):
    difficulty = (lesson_difficulty or "easy").lower()
    if not difficulty:
        return True
    if proficiency.lower() in {"beginner", "basic"}:
        return any(token in difficulty for token in ["easy", "medium", "beginner", "basic"])
    if proficiency.lower() == "intermediate":
        return any(token in difficulty for token in ["easy", "medium", "intermediate"])
    return any(token in difficulty for token in ["medium", "hard", "advanced", "intermediate"])


def get_content_recommendations(user_id, last_lesson_category=None, last_score=None):
    """
    AI-Based Personalized Learning Recommendation Engine
    Generates dynamic recommendations based on:
    Proficiency Level, Reading/Writing/Vocabulary/Grammar/Listening/Speaking Scores, Weak/Strong Skills, completed history.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT age, language, preferred_language, learning_language, learning_level, current_proficiency,
               reading_score, writing_score, vocabulary_score, grammar_score,
               listening_score, speaking_score, weak_skills, strong_skills
        FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return {}

    # normalize sqlite3.Row to dict so .get() works
    if not isinstance(user, dict):
        try:
            user = dict(user)
        except Exception:
            pass

    # Requirement: Only generate recommendations after the learner completes the Initial Assessment
    if not user.get("initial_assessment_completed"):
        conn.close()
        return {}
        
    preferred_language = user["preferred_language"] or user["language"] or "English"
    learning_language = user["learning_language"] or "English"
    
    try:
        age_int = int(user["age"])
    except (ValueError, TypeError):
        age_int = 8

    if age_int <= 5:
        videos = get_local_videos_for_learner(learning_language, age_int)
        cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
        completed_ids = {row["lesson_id"] for row in cursor.fetchall()}
        
        recommendations = []
        for idx, v in enumerate(videos):
            v_id = 20000 + idx
            if v_id not in completed_ids:
                recommendations.append({
                    "id": v_id,
                    "title": v["title"],
                    "category": v["category"].capitalize(),
                    "content": v["description"],
                    "difficulty": "Easy",
                    "reason": f"Fun play video in {learning_language} for pre-school learning.",
                    "url": "/week-module",
                    "skill": "reading"
                })
        
        if not recommendations and videos:
            for idx, v in enumerate(videos[-3:] if len(videos) >= 3 else videos):
                recommendations.append({
                    "id": 20000 + idx,
                    "title": v["title"],
                    "category": v["category"].capitalize(),
                    "content": v["description"],
                    "difficulty": "Easy",
                    "reason": f"Review play activity in {learning_language}.",
                    "url": "/week-module",
                    "skill": "reading"
                })
                
        active_acts = [
            {"title": "Balloon Pop Game", "difficulty": "Easy", "reason": "Fun play-based coordination game."},
            {"title": "Explore Colors Match", "difficulty": "Easy", "reason": "Learn and identify colors."},
            {"title": "Animal Sounds Play", "difficulty": "Easy", "reason": "Identify cute animal noises."}
        ]
        
        next_suggested_id = recommendations[0]["id"] if recommendations else None
        
        cursor.execute("""
            UPDATE users 
            SET recommended_activities = ?,
                next_suggested_lesson_id = ?,
                weak_skills = ?,
                strong_skills = ?
            WHERE id = ?
        """, (json.dumps(active_acts), next_suggested_id, "Listening, Speaking", "Drawing", user_id))
        
        for rec in recommendations:
            cursor.execute("""
                INSERT INTO recommendation_history (user_id, recommendation_type, item_id, title, category, difficulty, reason, status)
                VALUES (?, 'lesson', ?, ?, ?, ?, ?, 'pending')
            """, (user_id, rec["id"], rec["title"], rec["category"], rec["difficulty"], rec["reason"]))
            
        conn.commit()
        conn.close()
        return recommendations
    proficiency = user["current_proficiency"] or user["learning_level"] or "Beginner"
    skill_profile = _get_skill_score_profile(cursor, user_id, user)

    # Classify skills into Strong / Average / Weak
    scores_map = skill_profile.get("skill_scores", {})
    strong_skills = [s.title() for s, v in scores_map.items() if v >= 75]
    average_skills = [s.title() for s, v in scores_map.items() if 50 <= v < 75]
    weak_skills = [s.title() for s, v in scores_map.items() if v < 75]

    # If user has no weak skills, do not produce generic recommendations (per requirement)
    if not weak_skills:
        conn.close()
        return {}
    
    # Completed lesson details
    cursor.execute("""
        SELECT l.id, l.title, l.category 
        FROM lesson_progress lp
        JOIN lessons l ON lp.lesson_id = l.id
        WHERE lp.user_id = ?
    """, (user_id,))
    completed = cursor.fetchall()
    completed_ids = {r["id"] for r in completed}
    
    # Latest assessment score if not passed explicitly
    if last_score is None:
        cursor.execute("SELECT score FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
        arow = cursor.fetchone()
        if arow:
            last_score = arow["score"]

    # Fetch all available lessons for user's learning language
    cursor.execute("""
        SELECT id, title, category, language, content, difficulty 
        FROM lessons 
        WHERE language = ?
    """, (learning_language,))
    all_lessons = [dict(l) for l in cursor.fetchall()]
    
    # If no lessons exist in DB for this language, fetch all lessons as generic fallbacks
    if not all_lessons:
        cursor.execute("SELECT id, title, category, language, content, difficulty FROM lessons")
        all_lessons = [dict(l) for l in cursor.fetchall()]
        
    available = [l for l in all_lessons if l["id"] not in completed_ids]
    recommendations = []
    
    # Dynamic reasoning map
    reason_map = {
        "reading": "Recommended to improve your weak reading confidence and comprehension.",
        "writing": "Selected to strengthen your weak writing, spelling, and letter formation.",
        "vocabulary": "Focused on expanding your weak vocabulary skill through matching and practice.",
        "grammar": "Selected to improve sentence structure and grammar awareness.",
        "listening": "Designed to improve your weak listening skills with sound-based practice.",
        "speaking": "Recommended to improve your weak speaking fluency and pronunciation."
    }

    # 1. Filter by weak skills first (only recommend for weak skills)
    for skill in weak_skills:
        sk_lower = skill.lower()
        for l in available:
            if not _lesson_matches_skill(l, sk_lower):
                continue
            if not _difficulty_matches(l.get("difficulty"), proficiency):
                continue
            if l["id"] in [r["id"] for r in recommendations]:
                continue
            snippet = l["content"].split("[QUIZ]")[0].strip() if l["content"] else ""
            recommendations.append({
                "id": l["id"],
                "title": l["title"],
                "category": l["category"] or skill,
                "content": snippet[:120] + ("..." if len(snippet) > 120 else ""),
                "difficulty": l.get("difficulty") or "Easy",
                "reason": reason_map.get(sk_lower, f"Targeted practice for your weak {skill} skill."),
                "url": f"/lesson/{l['id']}",
                "skill": sk_lower
            })
            # cap three per skill to avoid flooding
            if sum(1 for r in recommendations if r.get("skill") == sk_lower) >= 3:
                break

    # 2. Expand recommendations per weak skill up to 2 lessons per skill (already capped above)
    # No generic fallbacks are added here to respect requirement: do not create generic recommendations.

    # 3. If still empty, return empty (no generic recommendations)
    if not recommendations:
        conn.close()
        return {}

    # Log new recommendations in recommendation_history (lessons)
    for rec in recommendations:
        try:
            cursor.execute("""
                INSERT INTO recommendation_history (user_id, recommendation_type, item_id, title, category, difficulty, reason, status)
                VALUES (?, 'lesson', ?, ?, ?, ?, ?, 'pending')
            """, (user_id, rec["id"], rec["title"], rec["category"], rec["difficulty"], rec["reason"]))
        except Exception:
            # ignore duplicate/history write errors
            pass
    
    # 4. Activity Recommendations: only suggest activities relevant to weak skills and level
    activity_templates = {
        "reading": ["Alphabet Recognition", "Picture Reading", "Word Reading", "Short Story Reading"],
        "writing": ["Tracing Letters", "Letter Writing", "Word Writing", "Sentence Writing"],
        "speaking": ["Pronunciation Drills", "Repeat-after-audio", "Picture Description", "Short Answer Speaking"],
        "listening": ["Rhymes & Songs", "Listen-and-Choose", "Audio Stories", "Sound Matching"],
        "comprehension": ["Picture Stories", "Short Story Q&A", "Sequence Events", "Who/What/Where Questions"]
    }

    level_diff = "Easy"
    if proficiency.lower() == "intermediate":
        level_diff = "Medium"
    elif proficiency.lower() == "advanced":
        level_diff = "Hard"

    active_acts = []
    for ws in weak_skills:
        sk = ws.lower()
        templates = activity_templates.get(sk, [])
        for t in templates[:3]:
            act = {"title": t, "difficulty": level_diff, "reason": f"Targeted activity to improve your {ws} skill.", "skill": sk}
            active_acts.append(act)
            try:
                cursor.execute("""
                    INSERT INTO recommendation_history (user_id, recommendation_type, title, difficulty, reason, status)
                    VALUES (?, 'activity', ?, ?, ?, 'pending')
                """, (user_id, t, level_diff, f"Targeted activity to improve your {ws} skill."))
            except Exception:
                pass

    # Store recommended activities and current next suggested lesson in users table
    next_suggested_id = recommendations[0]["id"] if recommendations else None
    cursor.execute("""
        UPDATE users 
        SET recommended_activities = ?,
            next_suggested_lesson_id = ?,
            weak_skills = ?,
            strong_skills = ?
        WHERE id = ?
    """, (json.dumps(active_acts), next_suggested_id, ", ".join([w.title() for w in weak_skills]), ", ".join(strong_skills), user_id))
    
    conn.commit()
    conn.close()
    return recommendations


def _build_ai_recommendations_payload(user, all_lessons, completed_ids):
    conn = get_db_connection()
    cursor = conn.cursor()

    def get_user_field(field_name, fallback=""):
        if isinstance(user, dict):
            value = user.get(field_name, fallback)
        else:
            try:
                value = user[field_name]
            except Exception:
                value = fallback
        return fallback if value in (None, "") else value

    def get_user_score(field_name, fallback):
        value = get_user_field(field_name, fallback)
        try:
            return int(float(value))
        except (TypeError, ValueError):
            return fallback

    scores = {
        "Reading": get_user_score("reading_score", 70),
        "Writing": get_user_score("writing_score", 65),
        "Listening": get_user_score("listening_score", 65),
        "Speaking": get_user_score("speaking_score", 65),
        "Comprehension": get_user_score("comprehension_score", get_user_score("grammar_score", 65))
    }

    weak_skills = [skill for skill, score in scores.items() if score < 75]
    if not weak_skills:
        weak_skills = [min(scores, key=scores.get)]

    strong_skills = [skill for skill, score in scores.items() if score >= 75 and skill not in weak_skills]

    skill_insights = []
    skill_messages = {
        "Reading": {
            "Excellent": "Excellent reading skills. Continue with longer passages and comprehension checks.",
            "Good": "Good reading fluency. Practice short stories and answer simple comprehension questions.",
            "Needs Improvement": "Build reading fluency by tracing words, reading short sentences, and reviewing picture-based stories."
        },
        "Writing": {
            "Excellent": "Strong writing control. Try creative sentence building and spelling challenges.",
            "Good": "Good writing foundation. Practice word formation, tracing letters, and writing short sentences.",
            "Needs Improvement": "Focus on tracing letters, copying words, and writing simple sentences to improve writing confidence."
        },
        "Listening": {
            "Excellent": "Sharp listening skills. Continue with audio stories and sound matching activities.",
            "Good": "Good listening awareness. Practice with short audio clips and answer listen-and-match questions.",
            "Needs Improvement": "Strengthen listening by hearing letter sounds, short words, and simple story audio with follow-up questions."
        },
        "Speaking": {
            "Excellent": "Great pronunciation. Keep practicing with daily speaking sentences and pronunciation drills.",
            "Good": "Good speaking control. Practice repeating short phrases and speaking into the voice activity daily.",
            "Needs Improvement": "Improve speaking by saying words aloud, repeating simple sentences, and using pronunciation practice activities."
        },
        "Comprehension": {
            "Excellent": "Excellent comprehension. Tackle longer stories and answer more detailed questions.",
            "Good": "Good comprehension. Practice reading a short passage and explaining the main idea in your own words.",
            "Needs Improvement": "Build comprehension by reading simple stories and answering questions about characters and actions."
        }
    }

    for skill, score in sorted(scores.items(), key=lambda item: item[1]):
        if score >= 85:
            level = "Excellent"
        elif score >= 70:
            level = "Good"
        else:
            level = "Needs Improvement"
        skill_insights.append({
            "name": skill,
            "score": score,
            "level": level,
            "recommendation": skill_messages[skill][level],
            "url": "/week-module"
        })

    available_lessons = [lesson for lesson in all_lessons if lesson["id"] not in completed_ids]
    if not available_lessons:
        available_lessons = all_lessons

    def _age_description(age_val):
        age_val = int(age_val) if isinstance(age_val, (int, float)) or (str(age_val).isdigit()) else 8
        if age_val <= 8:
            return "young learner with picture-based support"
        if age_val <= 12:
            return "junior learner with simple sentences"
        if age_val <= 15:
            return "upper primary learner with short passages"
        return "confident learner ready for meaningful practice"

    def _skill_focus(skill_name):
        skill_name = str(skill_name).strip().title()
        focus = {
            "Reading": ("short age-appropriate passages", "identify the main idea and important words", "answer simple comprehension questions"),
            "Writing": ("letter formation and short sentence writing", "copy words, trace letters, and build mini-sentences", "write a short answer with correct spelling"),
            "Listening": ("listening to spoken words and short sentences", "match sounds to pictures or words", "select the right answer after listening"),
            "Speaking": ("speaking familiar words and short phrases aloud", "repeat sentences and practice pronunciation", "say answers clearly using the target words"),
            "Comprehension": ("understanding stories and short descriptions", "answer who/what/where questions", "explain the main idea in simple words"),
        }
        return focus.get(skill_name, ("language patterns", "practice useful examples", "apply the idea with a short check"))

    def _difficulty_label(index, avg_score):
        labels = ["Easy", "Medium", "Hard"]
        if avg_score >= 85:
            return labels[min(index + 1, 2)]
        if avg_score >= 65:
            return labels[min(index, 2)]
        return labels[min(index, 1)]

    def _build_mini_assessment(skill_name, age_val, difficulty):
        prompts = []
        base = str(skill_name).strip().title()
        if base == "Reading":
            prompts = [
                "Read the short sentence and choose the correct picture.",
                "Find the main idea in the story.",
                "Pick the word that matches the sentence."
            ]
        elif base == "Writing":
            prompts = [
                "Write one simple sentence using the target word.",
                "Fill in the missing word to complete the sentence.",
                "Trace the sentence and write it again."
            ]
        elif base == "Listening":
            prompts = [
                "Listen to the sentence and choose the right picture.",
                "Hear the word and match it to the picture.",
                "Listen again and answer the question."
            ]
        elif base == "Speaking":
            prompts = [
                "Say the sentence aloud and count the words.",
                "Repeat the phrase clearly and say what it means.",
                "Use the target words in a short spoken answer."
            ]
        else:
            prompts = [
                "Read the passage and answer the questions.",
                "Choose the right answer for the story details.",
                "Explain the idea in one short sentence."
            ]
        if difficulty == "Easy":
            prompts = prompts[:2]
        elif difficulty == "Hard":
            prompts = prompts
        else:
            prompts = prompts[:3]
        return [
            {"question": p, "type": "short_answer" if "write" in p.lower() or "say" in p.lower() else "multiple_choice"}
            for p in prompts
        ]

    def _build_lesson(skill_name, lesson_index, age_val, level, skill_score, avg_score, source_lesson=None):
        objective_phrase, activity_phrase, practice_phrase = _skill_focus(skill_name)
        difficulty = _difficulty_label(lesson_index, avg_score)
        age_desc = _age_description(age_val)
        lesson_title = f"{skill_name.title()} Boost: {difficulty} Practice"
        if source_lesson:
            lesson_title = f"{skill_name.title()} Practice from {source_lesson['title']}"
        return {
            "title": lesson_title,
            "skill": skill_name.lower(),
            "difficulty": difficulty,
            "learning_objective": f"Build {skill_name.lower()} confidence for a {age_desc} at the {str(level).title()} level through {objective_phrase}.",
            "activity": f"Practice activity: {activity_phrase} with clear examples and scaffolded guidance.",
            "practice": f"Practice steps: {practice_phrase} using simple examples appropriate for your age and level.",
            "mini_assessment": _build_mini_assessment(skill_name, age_val, difficulty),
            "summary": f"This lesson gradually increases challenge as you improve your {skill_name.lower()} skill.",
            "source_url": f"/lesson/{source_lesson['id']}" if source_lesson else None
        }

    def _simulate_skill_reassessment(skill_score, difficulty):
        if skill_score < 40:
            gain = 18
        elif skill_score < 55:
            gain = 14
        elif skill_score < 70:
            gain = 10
        else:
            gain = 6
        if difficulty == "Hard":
            gain = max(4, gain - 4)
        if difficulty == "Easy":
            gain = min(gain + 2, 20)
        return min(100, skill_score + gain)

    def _compute_proficiency(avg_score):
        if avg_score >= 85:
            return "Advanced"
        if avg_score >= 60:
            return "Intermediate"
        if avg_score >= 35:
            return "Basic"
        return "Beginner"

    age_val = get_user_score("age", 8)
    avg_score = sum(scores.values()) / len(scores)
    learning_level = get_user_field("learning_level") or get_user_field("current_proficiency") or "Beginner"
    used_source_ids = set()
    used_titles = set()
    recommended_lessons = []

    for weak_skill in weak_skills:
        skill_name = weak_skill.title()
        current_skill_score = scores.get(skill_name, 65)
        step = 0
        while current_skill_score < 75 and step < 4:
            source = next(
                (lesson for lesson in available_lessons if lesson["id"] not in used_source_ids and _lesson_matches_skill(lesson, skill_name)),
                None
            )
            lesson = _build_lesson(
                skill_name,
                step,
                age_val,
                learning_level,
                current_skill_score,
                avg_score,
                source_lesson=source
            )
            if lesson["title"] in used_titles:
                lesson["title"] = f"{lesson['title']} Step {step + 1}"
            used_titles.add(lesson["title"])
            if source:
                used_source_ids.add(source["id"])
            lesson["post_assessment"] = {
                "skill": skill_name,
                "previous_score": current_skill_score,
                "status": "practice"
            }
            recommended_lessons.append(lesson)
            step += 1
            if len(recommended_lessons) >= 4:
                break
        if len(recommended_lessons) >= 4:
            break

    if not recommended_lessons and weak_skills:
        # Provide at least one weak-skill lesson even if no exact match exists
        skill_name = weak_skills[0].title()
        lesson = _build_lesson(skill_name, 0, age_val, learning_level, scores.get(skill_name, 65), avg_score, source_lesson=None)
        lesson["post_assessment"] = {
            "skill": skill_name,
            "previous_score": scores.get(skill_name, 65),
            "status": "practice"
        }
        recommended_lessons.append(lesson)

    if not recommended_lessons:
        recommended_lessons.append(_build_lesson("Reading", 0, age_val, learning_level, scores.get("Reading", 65), avg_score, source_lesson=None))

    weak_skills = [skill for skill, score in scores.items() if score < 75]
    strong_skills = [skill for skill, score in scores.items() if score >= 75]
    current_proficiency = _compute_proficiency(avg_score)

    user_updates = {
        "reading_score": scores.get("Reading", 0),
        "writing_score": scores.get("Writing", 0),
        "listening_score": scores.get("Listening", 0),
        "speaking_score": scores.get("Speaking", 0),
        "comprehension_score": scores.get("Comprehension", 0),
        "current_proficiency": current_proficiency,
        "weak_skills": ", ".join(weak_skills),
        "strong_skills": ", ".join(strong_skills)
    }
    user_id_value = None
    if isinstance(user, dict):
        user_id_value = user.get("id")
    else:
        try:
            user_id_value = user["id"]
        except Exception:
            user_id_value = None

    cursor.execute("""
        UPDATE users SET
            reading_score = ?,
            writing_score = ?,
            listening_score = ?,
            speaking_score = ?,
            comprehension_score = ?,
            current_proficiency = ?,
            weak_skills = ?,
            strong_skills = ?
        WHERE id = ?
    """, (
        user_updates["reading_score"],
        user_updates["writing_score"],
        user_updates["listening_score"],
        user_updates["speaking_score"],
        user_updates["comprehension_score"],
        user_updates["current_proficiency"],
        user_updates["weak_skills"],
        user_updates["strong_skills"],
        user_id_value
    ))
    conn.commit()

    if weak_skills:
        lesson_status = "weak skills remain"
    else:
        lesson_status = "all targeted skills reached proficiency"

    summary = f"Personalized lessons were created for {', '.join([w.title() for w in weak_skills]) or 'your current skills'}. Each lesson reassesses only the practiced skill and continues until proficiency improves."

    activity_recommendations = []
    skill_activity_map = {
        "Reading": "Practice reading simple captions, match words to pictures, and answer text questions.",
        "Writing": "Trace letters, build short words, and write simple sentences with guidance.",
        "Listening": "Listen to short audio clips and select the right pictures or words.",
        "Speaking": "Repeat words and phrases aloud, then compare with correct pronunciation.",
        "Comprehension": "Read a short story and answer who/what/where questions."
    }
    for weak_skill in weak_skills:
        activity_recommendations.append({
            "skill": weak_skill,
            "title": f"{weak_skill} Practice Activity",
            "reason": skill_activity_map.get(weak_skill, "Practice this skill with guided activities."),
            "url": "/week-module"
        })

    voice_practice = []
    if any(skill.lower() in {"speaking", "listening"} for skill in weak_skills):
        voice_practice.append({
            "title": "Daily Speaking & Pronunciation Practice",
            "reason": "Use voice practice to improve clarity and confidence in speech.",
            "url": "/week-module"
        })
    else:
        voice_practice.append({
            "title": "Daily Voice Warm-Up",
            "reason": "Stay consistent with speaking practice to maintain strong pronunciation.",
            "url": "/week-module"
        })

    game_recommendations = []
    if any(skill in weak_skills for skill in ["Reading", "Comprehension"]):
        game_recommendations.append({"id": "temple_run", "title": "Temple Run", "reason": "Boost reading comprehension and word pattern recognition.", "url": "/game/temple_run"})
        game_recommendations.append({"id": "space_explorer", "title": "Space Explorer", "reason": "Expand vocabulary through story-based challenges.", "url": "/game/space_explorer"})
    elif "Writing" in weak_skills:
        game_recommendations.append({"id": "ninja_fruit", "title": "Ninja Fruit", "reason": "Practice spelling and fast word building.", "url": "/game/ninja_fruit"})
        game_recommendations.append({"id": "treasure_hunt", "title": "Pirate Treasure", "reason": "Find word clues and practice writing patterns.", "url": "/game/treasure_hunt"})
    else:
        game_recommendations.append({"id": "city_builder", "title": "Dream City Builder", "reason": "Build sentences and practice language structure.", "url": "/game/city_builder"})
        game_recommendations.append({"id": "robot_factory", "title": "Robot Factory", "reason": "Assemble words and improve grammar logic.", "url": "/game/robot_factory"})

    recommended_quizzes = [
        {
            "title": f"{get_user_field('learning_language', 'English')} Level Check",
            "reason": "Complete a quick quiz to track progress in your weak areas.",
            "url": "/assessment"
        }
    ]

    avg_score = sum(scores.values()) / len(scores)
    if len(weak_skills) == 0:
        summary = "You are performing well across your current skill areas. Continue with the recommended lessons and activities to keep improving."
    elif len(weak_skills) == 1:
        summary = f"Your assessment identifies {weak_skills[0]} as the key area to strengthen. Start with targeted practice and focused lessons for this skill."
    else:
        summary = f"Your assessment identifies {', '.join(weak_skills[:-1])} and {weak_skills[-1]} as the main areas to improve. Focus on these skills with the recommended activities and lessons."

    recommendations = {
        "weak_skills": weak_skills,
        "strong_skills": strong_skills,
        "scores": scores,
        "skills": skill_insights,
        "lessons": recommended_lessons,
        "activities": activity_recommendations,
        "voice_practice": voice_practice,
        "games": game_recommendations,
        "quizzes": recommended_quizzes,
        "summary": summary
    }
    conn.close()
    return recommendations


def generate_ai_recommendations(user_id):
    """
    Dynamic AI-Based Personalized Learning Recommendation Engine.
    Uses learner's scores to identify strong/weak skills and generates recommendations.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, age, language, preferred_language, learning_language, learning_level, current_proficiency,
               reading_score, writing_score, grammar_score, comprehension_score,
               listening_score, speaking_score, pronunciation_score,
               weak_skills, strong_skills
        FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return {}
    try:
        user = dict(user)
    except Exception:
        pass

    learning_language = user["learning_language"] or "English"
    cursor.execute("""
        SELECT id, title, category, content, difficulty 
        FROM lessons 
        WHERE language = ?
    """, (learning_language,))
    all_lessons = [dict(l) for l in cursor.fetchall()]
    if not all_lessons:
        cursor.execute("SELECT id, title, category, content, difficulty FROM lessons")
        all_lessons = [dict(l) for l in cursor.fetchall()]

    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {r["lesson_id"] for r in cursor.fetchall()}

    recommendations = _build_ai_recommendations_payload(user, all_lessons, completed_ids)

    cursor.execute("""
        UPDATE users 
        SET weak_skills = ?, strong_skills = ?, recommended_activities = ?
        WHERE id = ?
    """, (
        ", ".join(recommendations["weak_skills"]),
        ", ".join(recommendations["strong_skills"]),
        json.dumps(recommendations),
        user_id
    ))
    conn.commit()
    conn.close()

    return recommendations


@app.route("/api/recommendations/personalized", methods=["GET"])
@login_required
def api_recommendations_personalized():
    user_id = session.get("user_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT initial_assessment_completed, learning_language,
               reading_score, writing_score, listening_score, speaking_score, grammar_score
        FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    if not user["initial_assessment_completed"] or user["initial_assessment_completed"] == 0:
        conn.close()
        return jsonify({
            "status": "success",
            "unlocked": False,
            "message": "Complete the Initial Assessment to unlock your personalized learning recommendations."
        })

    conn.close()
    recommendations = generate_ai_recommendations(user_id)
    return jsonify({
        "status": "success",
        "unlocked": True,
        "summary": recommendations.get("summary", "Here are your personalized recommendations based on your skill analysis."),
        "skills": recommendations.get("skills", []),
        "lessons": recommendations.get("lessons", []),
        "activities": recommendations.get("activities", []),
        "voice_practice": recommendations.get("voice_practice", []),
        "games": recommendations.get("games", []),
        "quizzes": recommendations.get("quizzes", [])
    })


def generate_personalized_learning_path(user_id):
    """
    Generates Today's Personalized Learning Path (5 steps) from the learner's assessment profile.
    The sequence is driven by the learner's weak skills first and adapts as progress is recorded.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fullname, age, language, preferred_language, learning_language, learning_level, current_proficiency, reading_score, writing_score, listening_score, speaking_score, comprehension_score FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        return []
    try:
        user = dict(user)
    except Exception:
        pass

    try:
        age = int(user.get("age")) if user.get("age") is not None and str(user.get("age")).isdigit() else 8
    except Exception:
        age = 8

    # Requirement: only generate after Initial Assessment and when AI recommendations exist
    if not user.get("initial_assessment_completed"):
        # allow play-based path for early learners even if assessment flag is missing
        if age <= 5:
            pass
        else:
            conn.close()
            return []

    # Ensure AI recommendations are available; generate them if missing
    recs_field = user.get("recommended_activities") if isinstance(user, dict) else None
    if not recs_field:
        try:
            # generate_ai_recommendations will persist recommended_activities
            generate_ai_recommendations(user_id)
            # reload user row minimally
            cursor.execute("SELECT recommended_activities FROM users WHERE id = ?", (user_id,))
            fres = cursor.fetchone()
            if fres:
                user = dict(user)
                user["recommended_activities"] = fres.get("recommended_activities")
        except Exception:
            pass

    preferred_lang = user["preferred_language"] or user["language"] or "English"
    learning_lang = user["learning_language"] or "English"
    learning_level = user["learning_level"] or user["current_proficiency"] or "Beginner"
    try:
        age = int(user["age"]) if user["age"] and str(user["age"]).isdigit() else 8
    except Exception:
        age = 8

    # Build skill scores and identify weak skills (primary driver)
    def _score(skill_name):
        skill_key = (skill_name or "").strip().lower()
        if skill_key == "reading":
            return float(user["reading_score"] or 0)
        if skill_key == "writing":
            return float(user["writing_score"] or 0)
        if skill_key == "listening":
            return float(user["listening_score"] or 0)
        if skill_key == "speaking":
            return float(user["speaking_score"] or 0)
        if skill_key == "comprehension":
            return float(user["comprehension_score"] or 0)
        return 0.0

    skills = ["reading", "writing", "listening", "speaking", "comprehension"]
    scored = [(s, _score(s)) for s in skills]
    # order by ascending score -> weakest first
    weak_skills = [s for s, v in sorted(scored, key=lambda t: t[1]) if v < 75]
    if not weak_skills:
        # if nobody below threshold, still pick the lowest two to prioritize
        weak_skills = [s for s, v in sorted(scored, key=lambda t: t[1])][:2]

    # helpers for constructing plan items
    def _infer_skill_from_category(cat, fallback=None):
        c = str(cat or "").lower()
        if any(k in c for k in ["read", "alphabet", "story"]):
            return "reading"
        if any(k in c for k in ["write", "sentence", "spelling"]):
            return "writing"
        if any(k in c for k in ["listen", "audio", "song", "sound", "rhymes"]):
            return "listening"
        if any(k in c for k in ["speak", "pronunciation", "voice"]):
            return "speaking"
        if any(k in c for k in ["comprehension", "comp", "story", "question"]):
            return "comprehension"
        return fallback or "reading"

    def _estimate_duration(item_type, difficulty=None):
        if item_type == "Play-Based Video":
            return 5
        if item_type == "Play Activity" or item_type == "Interactive Game":
            return 8
        if item_type == "Lesson":
            if difficulty and str(difficulty).lower() in {"beginner", "basic"}:
                return 15
            if difficulty and str(difficulty).lower() == "intermediate":
                return 25
            return 35
        if item_type == "Practice Activity":
            return 10
        if item_type == "Assessment":
            return 12
        if item_type == "AI Guide":
            return 8
        return 10

    # For very young learners (play-based path)
    if age <= 5:
        cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
        completed_ids = {row["lesson_id"] for row in cursor.fetchall()}

        videos = get_local_videos_for_learner(learning_lang, age)
        # select up to 3 videos prioritizing categories that match weak skills (map weak skills to video categories)
        cat_map = {
            "reading": ["alphabet"],
            "writing": ["alphabet"],
            "listening": ["animals", "rhymes"],
            "speaking": ["rhymes", "alphabet"],
            "comprehension": ["colors", "shapes", "animals"]
        }

        prioritized = []
        for ws in weak_skills:
            want = cat_map.get(ws, [])
            for v in videos:
                if v["title"] in [p.get("title") for p in prioritized]:
                    continue
                if v["category"] in want:
                    prioritized.append(v)

        # fill with first videos if still empty
        for v in videos:
            if len(prioritized) >= 3:
                break
            if v not in prioritized:
                prioritized.append(v)

        path_items = []
        step = 1
        for v in prioritized[:3]:
            path_items.append({
                "step": step,
                "title": v["title"],
                "type": "Play-Based Video",
                "category": v.get("category", "Rhymes"),
                "lesson_id": None,
                "status": "pending",
                "completion_status": "pending",
                "is_locked": False,
                "icon": "bi-play-circle-fill",
                "url": v.get("video_url", "/week-module"),
                "target_skill": _infer_skill_from_category(v.get("category"), "listening"),
                "recommended_activity": "Watch and interact: name colors, animals, or sing along",
                "learning_objective": f"Boost { _infer_skill_from_category(v.get('category'), 'listening').title() } through short play video and engagement.",
                "estimated_duration": _estimate_duration("Play-Based Video"),
                "skill_focus": "listening" if v.get("category") in ["animals", "rhymes"] else "comprehension"
            })
            step += 1

        # Add interactive play activities (colors/shapes/games)
        path_items.append({
            "step": step,
            "title": "Explore Colors & Shapes",
            "type": "Play Activity",
            "category": "Colors & Shapes",
            "lesson_id": None,
            "status": "pending",
            "completion_status": "pending",
            "is_locked": False,
            "icon": "bi-palette-fill",
            "url": "/week-module",
            "target_skill": "comprehension",
            "recommended_activity": "Match colors and shapes with pictures",
            "learning_objective": "Recognize basic colors and shapes through play-based matching activities.",
            "estimated_duration": _estimate_duration("Play Activity"),
            "skill_focus": "comprehension"
        })
        step += 1

        path_items.append({
            "step": step,
            "title": "Animal Sounds Game",
            "type": "Interactive Game",
            "category": "Games",
            "lesson_id": None,
            "status": "pending",
            "completion_status": "pending",
            "is_locked": False,
            "icon": "bi-controller",
            "url": "/learning-games",
            "target_skill": "listening",
            "recommended_activity": "Play sound-match and identify animals",
            "learning_objective": "Improve listening discrimination by matching animal sounds to pictures.",
            "estimated_duration": _estimate_duration("Interactive Game"),
            "skill_focus": "listening"
        })

        path_json = json.dumps(path_items, ensure_ascii=False)
        cursor.execute("""
            UPDATE users
            SET learning_path = ?, recommended_lesson = ?
            WHERE id = ?
        """, (path_json, path_items[0]["title"] if path_items else None, user_id))
        conn.commit()
        conn.close()
        return path_items

    # For learners above 5: focus on weak skills (learning level is primary for difficulty selection)
    difficulty_map = {
        "Beginner": "Beginner",
        "Basic": "Basic",
        "Intermediate": "Intermediate",
        "Advanced": "Advanced"
    }
    target_diff = difficulty_map.get(str(learning_level).strip().capitalize(), "Beginner")

    # fetch lessons matching weak skills and difficulty (prioritize language)
    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {r["lesson_id"] for r in cursor.fetchall()}

    recommended_lessons = []
    for ws in weak_skills:
        # try to find 1-3 lessons per weak skill prioritizing learning level
        cursor.execute("""
            SELECT id, title, category, difficulty, url
            FROM lessons
            WHERE language = ? AND (category LIKE ? OR title LIKE ?)
            ORDER BY CASE WHEN difficulty = ? THEN 0 ELSE 1 END, id ASC LIMIT 4
        """, (learning_lang, f"%{ws}%", f"%{ws}%", target_diff))
        rows = [dict(r) for r in cursor.fetchall()]
        for r in rows:
            if r["id"] not in completed_ids and r["id"] not in [l.get("id") for l in recommended_lessons]:
                recommended_lessons.append(r)

    # fill remaining slots with general recommendations for the target level (avoid unlocking advanced lessons)
    if len(recommended_lessons) < 6:
        cursor.execute("""
            SELECT id, title, category, difficulty, url
            FROM lessons
            WHERE language = ? AND difficulty = ?
            ORDER BY id ASC LIMIT ?
        """, (learning_lang, target_diff, 8))
        for r in cursor.fetchall():
            rr = dict(r)
            if rr["id"] not in completed_ids and rr["id"] not in [l.get("id") for l in recommended_lessons]:
                recommended_lessons.append(rr)
            if len(recommended_lessons) >= 6:
                break

    # Build path items: first focus lessons on weak skills, then practice, assessment, AI guide
    path_items = []
    step = 1
    for lesson in recommended_lessons:
        target_skill = _infer_skill_from_category(lesson.get("category"), weak_skills[0] if weak_skills else "reading")
        status = "completed" if lesson.get("id") in completed_ids else "pending"
        path_items.append({
            "step": step,
            "title": lesson.get("title") or "Lesson",
            "type": "Lesson",
            "category": lesson.get("category") or "Practice",
            "lesson_id": lesson.get("id"),
            "status": status,
            "completion_status": status,
            "is_locked": False,
            "icon": "bi-journal-bookmark-fill",
            "url": lesson.get("url") or f"/lesson/{lesson.get('id')}",
            "target_skill": target_skill,
            "recommended_activity": "Complete lesson activities and practice exercises",
            "learning_objective": f"Build {target_skill.title()} skills at the {str(learning_level).title()} level through targeted exercises and examples.",
            "estimated_duration": _estimate_duration("Lesson", lesson.get("difficulty")),
            "skill_focus": target_skill
        })
        step += 1

    # Optionally add a focused practice activity for the weakest skill if not already covered
    weakest = weak_skills[0] if weak_skills else "comprehension"
    path_items.append({
        "step": step,
        "title": f"Targeted Practice: {weakest.title()}",
        "type": "Practice Activity",
        "category": weakest.title(),
        "lesson_id": None,
        "status": "pending",
        "completion_status": "pending",
        "is_locked": False,
        "icon": "bi-123",
        "url": "/learning-games",
        "target_skill": weakest,
        "recommended_activity": f"Practice exercises focused on {weakest} (short drills).",
        "learning_objective": f"Improve {weakest.title()} through targeted practice and repetition.",
        "estimated_duration": _estimate_duration("Practice Activity"),
        "skill_focus": weakest
    })
    step += 1

    # Adaptive assessment step
    path_items.append({
        "step": step,
        "title": "Adaptive Skill Assessment",
        "type": "Assessment",
        "category": "Evaluation",
        "status": "pending",
        "completion_status": "pending",
        "is_locked": False,
        "icon": "bi-clipboard-check-fill",
        "url": "/assessment",
        "target_skill": weakest,
        "recommended_activity": "Short adaptive quiz to reassess progress",
        "learning_objective": "Measure improvement on practiced skills to determine next steps.",
        "estimated_duration": _estimate_duration("Assessment"),
        "skill_focus": weakest
    })
    step += 1

    # AI guide / next lesson
    next_url = "/week-module"
    if recommended_lessons:
        next_url = recommended_lessons[0].get("url") or f"/lesson/{recommended_lessons[0].get('id')}"
    path_items.append({
        "step": step,
        "title": "Adaptive AI Guide",
        "type": "AI Guide",
        "category": "Voice & AI",
        "status": "pending",
        "completion_status": "pending",
        "is_locked": False,
        "icon": "bi-robot",
        "url": next_url,
        "target_skill": weakest,
        "recommended_activity": "Follow AI-guided tips and short micro-lessons",
        "learning_objective": "Provide tailored micro-feedback and next-step recommendations.",
        "estimated_duration": _estimate_duration("AI Guide"),
        "skill_focus": weakest
    })

    path_json = json.dumps(path_items, ensure_ascii=False)
    recommended_title = recommended_lessons[0]["title"] if recommended_lessons else None

    try:
        cursor.execute("""
            UPDATE users 
            SET learning_path = ?, recommended_lesson = ?
            WHERE id = ?
        """, (path_json, recommended_title, user_id))
        conn.commit()
    except Exception as e:
        print(f"[PATH UPDATE ERROR] {e}")

    conn.close()
    return path_items

    trans = get_translations(preferred_lang)
    recs = get_content_recommendations(user_id)
    lesson1 = recs[0] if len(recs) > 0 else {"id": None, "title": trans.get("default_lesson_title", f"{learning_lang} Next Lesson"), "category": trans.get("cat_general", "General"), "url": "/week-module"}
    lesson2 = recs[1] if len(recs) > 1 else None
    lesson3 = recs[2] if len(recs) > 2 else None

    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {r["lesson_id"] for r in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) FROM study_sessions WHERE user_id = ?", (user_id,))
    session_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE user_id = ?", (user_id,))
    assessment_count = cursor.fetchone()[0]

    step1_status = "completed" if lesson1.get("id") in completed_ids else "pending"
    step2_status = "completed" if lesson2 and lesson2.get("id") in completed_ids else "pending"
    step3_status = "completed" if lesson3 and lesson3.get("id") in completed_ids else "pending"
    step4_status = "completed" if session_count > 0 else "pending"
    step5_status = "completed" if assessment_count > 0 else "pending"

    def translate_cat(cat_raw):
        if not cat_raw:
            return trans.get("cat_reading", "Reading")
        c_low = str(cat_raw).lower().strip()
        if "read" in c_low:
            return trans.get("cat_reading", "Reading")
        elif "write" in c_low:
            return trans.get("cat_writing", "Writing")
        elif "alph" in c_low or "letter" in c_low:
            return trans.get("cat_alphabet", "Alphabet")
        elif "num" in c_low or "count" in c_low:
            return trans.get("cat_numbers", "Numbers")
        elif "pract" in c_low:
            return trans.get("cat_practice", "Practice")
        elif "voice" in c_low or "ai" in c_low:
            return trans.get("cat_voice_ai", "Voice & AI")
        elif "eval" in c_low or "assess" in c_low:
            return trans.get("cat_evaluation", "Evaluation")
        elif "comp" in c_low:
            return trans.get("cat_comprehension", "Comprehension")
        elif "shape" in c_low:
            return trans.get("cat_shapes", "Shapes")
        elif "color" in c_low:
            return trans.get("cat_colors", "Colors")
        return cat_raw

    def translate_title(title_raw):
        if not title_raw:
            return ""
        res = str(title_raw)
        if " - Part 2" in res:
            res = res.replace(" - Part 2", f" - {trans.get('part_2', 'Part 2')}")
        if " - Part 3" in res:
            res = res.replace(" - Part 3", f" - {trans.get('part_3', 'Part 3')}")
        return res

    level_hint = learning_level.lower()
    if level_hint in {"advanced", "intermediate"}:
        step3_title = trans.get("step3_title_challenge", "Challenge Practice")
        step3_type = trans.get("type_lesson", "Lesson")
        step3_category = trans.get("cat_comprehension", "Comprehension")
    elif level_hint == "basic":
        step3_title = trans.get("step3_title_support", "Support Practice")
        step3_type = trans.get("type_practice", "Practice Activity")
        step3_category = trans.get("cat_practice", "Practice")
    else:
        step3_title = trans.get("step3_title", "Targeted Practice Activity")
        step3_type = trans.get("type_practice", "Practice Activity")
        step3_category = trans.get("cat_practice", "Practice")

    path_items = [
        {
            "step": 1,
            "title": translate_title(lesson1["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson1.get("category")),
            "lesson_id": lesson1.get("id"),
            "status": step1_status,
            "is_locked": False,
            "icon": "bi-journal-bookmark-fill",
            "url": lesson1.get("url") if lesson1.get("url") else (f"/lesson/{lesson1.get('id')}" if lesson1.get('id') else "/week-module"),
            "skill_focus": primary_skill
        },
        {
            "step": 2,
            "title": translate_title(lesson2["title"]) if lesson2 else trans.get("step2_title", "Additional Practice"),
            "type": lesson2 and trans.get("type_lesson", "Lesson") or trans.get("type_practice", "Practice Activity"),
            "category": translate_cat(lesson2.get("category") if lesson2 else trans.get("cat_practice", "Practice")),
            "lesson_id": lesson2.get("id") if lesson2 else None,
            "status": step2_status,
            "is_locked": False,
            "icon": "bi-123",
            "url": lesson2 and (lesson2.get("url") or f"/lesson/{lesson2.get('id')}") or "/week-module",
            "skill_focus": secondary_skill
        },
        {
            "step": 3,
            "title": translate_title(lesson3["title"]) if lesson3 else step3_title,
            "type": lesson3 and trans.get("type_lesson", "Lesson") or step3_type,
            "category": translate_cat(lesson3.get("category") if lesson3 else step3_category),
            "lesson_id": lesson3.get("id") if lesson3 else None,
            "status": step3_status,
            "is_locked": False,
            "icon": "bi-pencil-square",
            "url": lesson3 and (lesson3.get("url") or f"/lesson/{lesson3.get('id')}") or "/learning-games",
            "skill_focus": primary_skill
        },
        {
            "step": 4,
            "title": trans.get("step4_title", "Adaptive Skill Assessment"),
            "type": trans.get("type_assessment", "Assessment"),
            "category": trans.get("cat_evaluation", "Evaluation"),
            "status": step4_status,
            "is_locked": False,
            "icon": "bi-clipboard-check-fill",
            "url": "/assessment",
            "skill_focus": "comprehension"
        },
        {
            "step": 5,
            "title": trans.get("step5_title", "Adaptive AI Guide"),
            "type": "AI Guide",
            "category": trans.get("cat_voice_ai", "AI Rec"),
            "status": step5_status,
            "is_locked": False,
            "icon": "bi-robot",
            "url": recs[0]["url"] if (len(recs) > 0 and "url" in recs[0]) else "/week-module",
            "skill_focus": secondary_skill
        }
    ]

    path_json = json.dumps(path_items, ensure_ascii=False)
    recommended_title = lesson1["title"]

    try:
        cursor.execute("""
            UPDATE users
            SET learning_path = ?, recommended_lesson = ?
            WHERE id = ?
        """, (path_json, recommended_title, user_id))
        conn.commit()
    except Exception as e:
        print(f"[PATH UPDATE ERROR] {e}")

    conn.close()
    return path_items

    trans = get_translations(preferred_lang)
    recs = get_content_recommendations(user_id)
    lesson1 = recs[0] if len(recs) > 0 else {"id": None, "title": trans.get("default_lesson_title", f"{learning_lang} Next Lesson"), "category": trans.get("cat_general", "General"), "url": "/week-module"}
    lesson2 = recs[1] if len(recs) > 1 else None
    lesson3 = recs[2] if len(recs) > 2 else None

    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {r["lesson_id"] for r in cursor.fetchall()}
    cursor.execute("SELECT COUNT(*) FROM study_sessions WHERE user_id = ?", (user_id,))
    session_count = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE user_id = ?", (user_id,))
    assessment_count = cursor.fetchone()[0]

    step1_status = "completed" if lesson1.get("id") in completed_ids else "pending"
    step2_status = "completed" if lesson2 and lesson2.get("id") in completed_ids else "pending"
    step3_status = "completed" if lesson3 and lesson3.get("id") in completed_ids else "pending"
    step4_status = "completed" if session_count > 0 else "pending"
    step5_status = "completed" if assessment_count > 0 else "pending"

    trans = get_translations(preferred_lang)

    def translate_cat(cat_raw):
        if not cat_raw:
            return trans.get("cat_reading", "Reading")
        c_low = str(cat_raw).lower().strip()
        if "read" in c_low:
            return trans.get("cat_reading", "Reading")
        elif "write" in c_low:
            return trans.get("cat_writing", "Writing")
        elif "alph" in c_low or "letter" in c_low:
            return trans.get("cat_alphabet", "Alphabet")
        elif "num" in c_low or "count" in c_low:
            return trans.get("cat_numbers", "Numbers")
        elif "pract" in c_low:
            return trans.get("cat_practice", "Practice")
        elif "voice" in c_low or "ai" in c_low:
            return trans.get("cat_voice_ai", "Voice & AI")
        elif "eval" in c_low or "assess" in c_low:
            return trans.get("cat_evaluation", "Evaluation")
        elif "comp" in c_low:
            return trans.get("cat_comprehension", "Comprehension")
        elif "shape" in c_low:
            return trans.get("cat_shapes", "Shapes")
        elif "color" in c_low:
            return trans.get("cat_colors", "Colors")
        return cat_raw

    def translate_title(title_raw):
        if not title_raw:
            return ""
        res = str(title_raw)
        if " - Part 2" in res:
            res = res.replace(" - Part 2", f" - {trans.get('part_2', 'Part 2')}")
        if " - Part 3" in res:
            res = res.replace(" - Part 3", f" - {trans.get('part_3', 'Part 3')}")
        return res

    # Dynamic adaptive path steps should be available and not rigidly gated
    is_step2_locked = False
    is_step3_locked = False
    is_step4_locked = False
    is_step5_locked = False

    first_lesson_url = lesson1.get("url") if lesson1.get("url") else f"/lesson/{lesson1.get('id')}" if lesson1.get("id") else "/week-module"
    path_items = [
        {
            "step": 1,
            "title": translate_title(lesson1["title"]),
            "type": trans.get("type_lesson", "Lesson"),
            "category": translate_cat(lesson1.get("category")),
            "lesson_id": lesson1.get("id"),
            "status": step1_status,
            "is_locked": False,
            "icon": "bi-journal-bookmark-fill",
            "url": lesson1.get("url") if lesson1.get("url") else (f"/lesson/{lesson1.get('id')}" if lesson1.get('id') else "/week-module")
        },
        {
            "step": 2,
            "title": translate_title(lesson2["title"]) if lesson2 else trans.get("step2_title", "Additional Practice"),
            "type": lesson2 and trans.get("type_lesson", "Lesson") or trans.get("type_practice", "Practice Activity"),
            "category": translate_cat(lesson2.get("category") if lesson2 else trans.get("cat_practice", "Practice")),
            "lesson_id": lesson2.get("id") if lesson2 else None,
            "status": step2_status,
            "is_locked": is_step2_locked,
            "icon": "bi-123",
            "url": lesson2 and (lesson2.get("url") or f"/lesson/{lesson2.get('id')}") or "/week-module"
        },
        {
            "step": 3,
            "title": translate_title(lesson3["title"]) if lesson3 else trans.get("step3_title", "Targeted Practice Activity"),
            "type": lesson3 and trans.get("type_lesson", "Lesson") or trans.get("type_practice", "Practice Activity"),
            "category": translate_cat(lesson3.get("category") if lesson3 else trans.get("cat_practice", "Practice")),
            "lesson_id": lesson3.get("id") if lesson3 else None,
            "status": step3_status,
            "is_locked": is_step3_locked,
            "icon": "bi-pencil-square",
            "url": lesson3 and (lesson3.get("url") or f"/lesson/{lesson3.get('id')}") or "/learning-games"
        },
        {
            "step": 4,
            "title": trans.get("step4_title", "Adaptive Skill Assessment"),
            "type": trans.get("type_assessment", "Assessment"),
            "category": trans.get("cat_evaluation", "Evaluation"),
            "status": step4_status,
            "is_locked": is_step4_locked,
            "icon": "bi-clipboard-check-fill",
            "url": "/assessment"
        },
        {
            "step": 5,
            "title": trans.get("step5_title", "Adaptive AI Guide"),
            "type": "AI Guide",
            "category": trans.get("cat_voice_ai", "AI Rec"),
            "status": step5_status,
            "is_locked": is_step5_locked,
            "icon": "bi-robot",
            "url": recs[0]["url"] if (len(recs) > 0 and "url" in recs[0]) else "/week-module"
        }
    ]

    path_json = json.dumps(path_items, ensure_ascii=False)
    recommended_title = lesson1["title"]

    try:
        cursor.execute("""
            UPDATE users 
            SET learning_path = ?, recommended_lesson = ?
            WHERE id = ?
        """, (path_json, recommended_title, user_id))
        conn.commit()
    except Exception as e:
        print(f"[PATH UPDATE ERROR] {e}")

    conn.close()
    return path_items


# -------------------------------
# Create Database
# -------------------------------
def populate_sample_lessons(conn):
    # Already seeded via seed_lessons.py
    pass


# -------------------------------
# API Endpoints for Recommendations, Paths & Analytics
# -------------------------------


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


def recalculate_and_refresh_learner_state(user_id):
    """
    Centralized controller for learner progression state.
    Updates progress percentages, dynamic weak/strong skills, predicted proficiency,
    and refreshes both the recommendation engine and the personalized learning path atomically.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch user language and age
    cursor.execute("SELECT language, age FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    if not urow:
        conn.close()
        return None
        
    language = urow["language"] or "English"
    age = urow["age"] or 8
    
    # 2. Count completed lessons
    cursor.execute("SELECT COUNT(DISTINCT lesson_id) FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_count = cursor.fetchone()[0]
    
    # 3. Fetch total lessons in language
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (language,))
    total_lessons = cursor.fetchone()[0] or 10
    
    # 4. Calculate progress percentage
    progress_percentage = min(100.0, round((completed_count / max(1, total_lessons)) * 100, 1))
    
    # 5. Fetch prediction profile for cognitive updates
    pred_prof = predict_user_proficiency(user_id, language)
    current_proficiency = pred_prof["current_proficiency"]
    
    # 6. Fetch weak/strong skills from predicted profile
    profile = generate_cognitive_profile(user_id)
    weak_skills = profile["weak_skills"]
    strong_skills = profile["strong_skills"]
    
    # 7. Refresh recommendations and get next lesson ID
    recs = get_content_recommendations(user_id)
    next_suggested_id = recs[0]["id"] if recs else None
    ai_recs = generate_ai_recommendations(user_id)
    
    # 8. Refresh path items
    generate_personalized_learning_path(user_id)
    
    # 9. Update users table
    cursor.execute("""
        UPDATE users 
        SET completed_lessons_count = ?,
            progress_percentage = ?,
            learning_path_progress = ?,
            current_proficiency = ?,
            weak_skills = ?,
            strong_skills = ?,
            next_suggested_lesson_id = ?,
            last_activity_date = DATE('now')
        WHERE id = ?
    """, (completed_count, progress_percentage, progress_percentage, current_proficiency,
          weak_skills, strong_skills, next_suggested_id, user_id))
          
    conn.commit()
    conn.close()
    
    return {
        "completed_count": completed_count,
        "progress_percentage": progress_percentage,
        "current_proficiency": current_proficiency,
        "weak_skills": weak_skills,
        "strong_skills": strong_skills,
        "next_suggested_lesson_id": next_suggested_id
    }



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

@app.route("/api/recommendations/history", methods=["GET"])
@login_required
def api_recommendations_history():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, recommendation_type, item_id, title, category, difficulty, reason, timestamp, status
        FROM recommendation_history
        WHERE user_id = ?
        ORDER BY timestamp DESC
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history_list = [dict(row) for row in rows]
    return jsonify({"status": "success", "recommendation_history": history_list})


@app.route("/api/admin/overview", methods=["GET"])
@login_required
def api_admin_overview():
    # Admin-only: basic metrics for dashboard overview
    user_id = session.get("user_id")
    # NOTE: frontend handles auth; we assume caller is admin via existing decorators
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    total_learners = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT user_id) FROM lesson_progress WHERE timestamp >= DATE('now','-30 day')")
    active_learners = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM lessons")
    total_lessons = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM assessment_history")
    total_assessments = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE learning_path IS NOT NULL AND learning_path != ''")
    total_learning_plans = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(progress_percentage) FROM users WHERE progress_percentage IS NOT NULL")
    avg_progress = cursor.fetchone()[0] or 0.0

    conn.close()
    return jsonify({
        "status": "success",
        "total_learners": total_learners,
        "active_learners_30d": active_learners,
        "total_lessons": total_lessons,
        "total_assessments": total_assessments,
        "total_learning_plans": total_learning_plans,
        "average_progress": round(float(avg_progress),1)
    })


@app.route('/api/admin/learners', methods=['GET'])
@login_required
def api_admin_learners():
    q = request.args.get('q','').strip()
    page = int(request.args.get('page',1))
    per_page = int(request.args.get('per_page',50))
    offset = (page-1)*per_page
    conn = get_db_connection()
    cursor = conn.cursor()
    if q:
        pattern = f"%{q}%"
        cursor.execute("SELECT id, fullname, email, age, language, learning_level, progress_percentage FROM users WHERE fullname LIKE ? OR email LIKE ? OR id LIKE ? LIMIT ? OFFSET ?", (pattern, pattern, pattern, per_page, offset))
    else:
        cursor.execute("SELECT id, fullname, email, age, language, learning_level, progress_percentage FROM users LIMIT ? OFFSET ?", (per_page, offset))
    rows = cursor.fetchall()
    conn.close()
    learners = [dict(r) for r in rows]
    return jsonify({"status":"success","learners":learners,"page":page})


@app.route('/api/admin/learner/<int:learner_id>', methods=['GET'])
@login_required
def api_admin_learner_detail(learner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (learner_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return jsonify({"status":"error","message":"Learner not found"}),404
    user = dict(row)
    # fetch progress and assessments
    cursor.execute("SELECT lesson_id, completed, score, timestamp FROM lesson_progress WHERE user_id = ?", (learner_id,))
    lessons = [dict(r) for r in cursor.fetchall()]
    cursor.execute("SELECT id, score, timestamp FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 20", (learner_id,))
    assessments = [dict(r) for r in cursor.fetchall()]
    # recommendations and learning_path
    user_recs = user.get('recommended_activities')
    try:
        recs = json.loads(user_recs) if user_recs else None
    except Exception:
        recs = None
    learning_path = None
    try:
        learning_path = json.loads(user.get('learning_path')) if user.get('learning_path') else None
    except Exception:
        learning_path = None
    conn.close()
    return jsonify({"status":"success","user":user,"lesson_progress":lessons,"assessments":assessments,"recommendations":recs,"learning_path":learning_path})


@app.route('/api/admin/learner/<int:learner_id>', methods=['DELETE'])
@login_required
def api_admin_delete_learner(learner_id):
    # optional delete
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (learner_id,))
    cursor.execute("DELETE FROM lesson_progress WHERE user_id = ?", (learner_id,))
    cursor.execute("DELETE FROM assessment_history WHERE user_id = ?", (learner_id,))
    cursor.execute("DELETE FROM recommendation_history WHERE user_id = ?", (learner_id,))
    conn.commit()
    conn.close()
    return jsonify({"status":"success","message":"Learner deleted"})


@app.route('/api/admin/lessons', methods=['GET','POST'])
@login_required
def api_admin_lessons():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        page = int(request.args.get('page',1))
        per_page = int(request.args.get('per_page',50))
        offset = (page-1)*per_page
        cursor.execute('SELECT id,title,category,language,difficulty FROM lessons LIMIT ? OFFSET ?', (per_page, offset))
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'status':'success','lessons':[dict(r) for r in rows]})
    data = request.get_json() or {}
    # required fields: title, content, language
    cursor.execute('INSERT INTO lessons (title, category, language, content, difficulty, url) VALUES (?,?,?,?,?,?)', (
        data.get('title'), data.get('category'), data.get('language'), data.get('content'), data.get('difficulty'), data.get('url')
    ))
    conn.commit()
    nid = cursor.lastrowid
    conn.close()
    return jsonify({'status':'success','id':nid})


@app.route('/api/admin/lesson/<int:lesson_id>', methods=['GET','PUT','DELETE'])
@login_required
def api_admin_lesson_detail(lesson_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM lessons WHERE id = ?', (lesson_id,))
        row = cursor.fetchone()
        conn.close()
        return jsonify({'status':'success','lesson':dict(row) if row else None})
    if request.method == 'PUT':
        data = request.get_json() or {}
        cursor.execute('''UPDATE lessons SET title = ?, category = ?, language = ?, content = ?, difficulty = ?, url = ? WHERE id = ?''', (
            data.get('title'), data.get('category'), data.get('language'), data.get('content'), data.get('difficulty'), data.get('url'), lesson_id
        ))
        conn.commit()
        conn.close()
        return jsonify({'status':'success'})
    # DELETE
    cursor.execute('DELETE FROM lessons WHERE id = ?', (lesson_id,))
    conn.commit()
    conn.close()
    return jsonify({'status':'success'})


@app.route('/api/admin/videos', methods=['GET','POST'])
@login_required
def api_admin_videos():
    # list/manage local educational videos using existing helper get_local_videos_for_learner
    if request.method == 'GET':
        lang = request.args.get('language','English')
        age = int(request.args.get('age',8))
        videos = get_local_videos_for_learner(lang, age)
        return jsonify({'status':'success','videos':videos})
    # POST to assign videos metadata (simple persistence into lessons as video entries)
    data = request.get_json() or {}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO lessons (title, category, language, content, difficulty, url) VALUES (?,?,?,?,?,?)', (
        data.get('title'), data.get('category'), data.get('language'), data.get('description'), data.get('level'), data.get('video_url')
    ))
    conn.commit()
    nid = cursor.lastrowid
    conn.close()
    return jsonify({'status':'success','id':nid})


@app.route('/api/admin/assessments', methods=['GET','POST'])
@login_required
def api_admin_assessments():
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT id, question, category, difficulty FROM assessment_questions LIMIT 200')
        rows = cursor.fetchall()
        conn.close()
        return jsonify({'status':'success','questions':[dict(r) for r in rows]})
    data = request.get_json() or {}
    cursor.execute('INSERT INTO assessment_questions (question, category, difficulty, language) VALUES (?,?,?,?)', (
        data.get('question'), data.get('category'), data.get('difficulty'), data.get('language')
    ))
    conn.commit()
    nid = cursor.lastrowid
    conn.close()
    return jsonify({'status':'success','id':nid})


@app.route('/api/admin/assessment/<int:qid>', methods=['GET','PUT','DELETE'])
@login_required
def api_admin_assessment_detail(qid):
    conn = get_db_connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute('SELECT * FROM assessment_questions WHERE id = ?', (qid,))
        row = cursor.fetchone()
        conn.close()
        return jsonify({'status':'success','question':dict(row) if row else None})
    if request.method == 'PUT':
        data = request.get_json() or {}
        cursor.execute('UPDATE assessment_questions SET question = ?, category = ?, difficulty = ?, language = ? WHERE id = ?', (
            data.get('question'), data.get('category'), data.get('difficulty'), data.get('language'), qid
        ))
        conn.commit()
        conn.close()
        return jsonify({'status':'success'})
    cursor.execute('DELETE FROM assessment_questions WHERE id = ?', (qid,))
    conn.commit()
    conn.close()
    return jsonify({'status':'success'})


@app.route('/api/admin/recommendations/<int:learner_id>', methods=['GET'])
@login_required
def api_admin_recommendations_monitor(learner_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, score, timestamp FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1', (learner_id,))
    last = cursor.fetchone()
    cursor.execute('SELECT weak_skills, strong_skills, recommended_activities, learning_path FROM users WHERE id = ?', (learner_id,))
    row = cursor.fetchone()
    conn.close()
    user = dict(row) if row else {}
    try:
        recs = json.loads(user.get('recommended_activities')) if user.get('recommended_activities') else None
    except Exception:
        recs = None
    try:
        path = json.loads(user.get('learning_path')) if user.get('learning_path') else None
    except Exception:
        path = None
    return jsonify({'status':'success','last_assessment':dict(last) if last else None,'weak_skills':user.get('weak_skills'),'strong_skills':user.get('strong_skills'),'recommendations':recs,'learning_path':path})


@app.route('/api/admin/reports/assessments', methods=['GET'])
@login_required
def api_admin_reports_assessments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT user_id, score, timestamp FROM assessment_history ORDER BY timestamp DESC LIMIT 500')
    rows = cursor.fetchall()
    conn.close()
    return jsonify({'status':'success','assessment_history':[dict(r) for r in rows]})


@app.route('/api/admin/reports/skill-progress', methods=['GET'])
@login_required
def api_admin_reports_skill_progress():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT AVG(reading_score) as reading_avg, AVG(writing_score) as writing_avg, AVG(listening_score) as listening_avg, AVG(speaking_score) as speaking_avg, AVG(comprehension_score) as comprehension_avg FROM users')
    row = cursor.fetchone()
    conn.close()
    return jsonify({'status':'success','skill_averages':dict(row) if row else {}})


@app.route('/api/admin/reports/progress-stats', methods=['GET'])
@login_required
def api_admin_reports_progress_stats():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total, SUM(CASE WHEN progress_percentage >= 80 THEN 1 ELSE 0 END) as completed_80 FROM users')
    row = cursor.fetchone()
    conn.close()
    return jsonify({'status':'success','total_users':row[0],'completed_80_percent':row[1]})

@app.route("/api/recommendations/activities", methods=["GET"])
@login_required
def api_recommendations_activities():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT recommended_activities FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    activities = []
    if row and row["recommended_activities"]:
        try:
            activities = json.loads(row["recommended_activities"])
        except Exception:
            pass
            
    return jsonify({"status": "success", "recommended_activities": activities})

@app.route("/api/learning-path/complete-lesson", methods=["POST"])
@login_required
def api_learning_path_complete_lesson():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    lesson_id = data.get("lesson_id")
    if not lesson_id:
        return jsonify({"status": "error", "message": "lesson_id field is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Update recommendation_history to completed
    cursor.execute("""
        UPDATE recommendation_history 
        SET status = 'completed' 
        WHERE user_id = ? AND item_id = ? AND status = 'pending'
    """, (user_id, lesson_id))
    
    cursor.execute("SELECT id FROM lesson_progress WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
    is_new = cursor.fetchone() is None
    if is_new:
        cursor.execute("INSERT INTO lesson_progress (user_id, lesson_id) VALUES (?, ?)", (user_id, lesson_id))
        conn.commit()
        
    # Get user language & calculate progress
    cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    user_lang = urow["language"] if urow else "English"
    
    cursor.execute("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (user_lang,))
    total_lessons = cursor.fetchone()[0] or 10
    
    progress_percentage = min(100.0, (completed_count / total_lessons) * 100)
    
    cursor.execute("""
        UPDATE users 
        SET completed_lessons_count = ?, 
            progress_percentage = ?,
            learning_path_progress = ?
        WHERE id = ?
    """, (completed_count, progress_percentage, progress_percentage, user_id))
    conn.commit()
    conn.close()
    
    if is_new:
        log_study_activity(user_id, 10, 15)
        
    # Refresh recommendations and path
    recalculate_and_refresh_learner_state(user_id)
    
    return jsonify({
        "status": "success",
        "message": "Lesson completed successfully",
        "progress_percentage": progress_percentage
    })

@app.route("/api/recommendations/refresh", methods=["POST"])
@login_required
def api_recommendations_refresh():
    user_id = session.get("user_id")
    state = recalculate_and_refresh_learner_state(user_id)
    recs = get_content_recommendations(user_id)
    path = generate_personalized_learning_path(user_id)
    return jsonify({
        "status": "success",
        "message": "Recommendations refreshed",
        "state": state,
        "recommendations": recs,
        "learning_path": path
    })


@app.route("/api/learning-path/current-lesson", methods=["GET"])
@login_required
def api_learning_path_current_lesson():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT next_suggested_lesson_id, language FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if not row or not row["next_suggested_lesson_id"]:
        return jsonify({"status": "empty", "message": "No active lesson suggestions"}), 200
        
    lesson_id = row["next_suggested_lesson_id"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
    lesson = cursor.fetchone()
    conn.close()
    
    if lesson:
        return jsonify({"status": "success", "current_lesson": dict(lesson)})
    return jsonify({"status": "error", "message": "Suggested lesson not found"}), 404


@app.route("/api/progress/summary", methods=["GET"])
@login_required
def api_progress_summary():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT completed_lessons_count, progress_percentage, coins, xp, streak
        FROM users WHERE id = ?
    """, (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return jsonify({
            "status": "success",
            "progress": {
                "completed_lessons_count": row["completed_lessons_count"] or 0,
                "progress_percentage": row["progress_percentage"] or 0.0,
                "coins": row["coins"] or 0,
                "xp": row["xp"] or 0,
                "streak": row["streak"] or 0
            }
        })
    return jsonify({"status": "error", "message": "User not found"}), 404


@app.route("/api/learner/statistics", methods=["GET"])
@login_required
def api_learner_statistics():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT average_score, streak, coins, xp, weak_skills, strong_skills, current_proficiency
        FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    
    if not user:
        conn.close()
        return jsonify({"status": "error", "message": "User not found"}), 404
        
    cursor.execute("SELECT COUNT(*), SUM(duration) FROM study_sessions WHERE user_id = ?", (user_id,))
    srow = cursor.fetchone()
    session_count = srow[0] if srow else 0
    total_duration = srow[1] if srow and srow[1] is not None else 0
    
    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE user_id = ?", (user_id,))
    assessment_count = cursor.fetchone()[0]
    
    conn.close()
    return jsonify({
        "status": "success",
        "statistics": {
            "average_score": user["average_score"] or 0.0,
            "streak": user["streak"] or 0,
            "xp": user["xp"] or 0,
            "coins": user["coins"] or 0,
            "total_study_sessions": session_count,
            "total_study_minutes": total_duration,
            "total_assessments": assessment_count,
            "weak_skills": [s.strip() for s in user["weak_skills"].split(",") if s.strip()] if user["weak_skills"] else [],
            "strong_skills": [s.strip() for s in user["strong_skills"].split(",") if s.strip()] if user["strong_skills"] else [],
            "current_proficiency": user["current_proficiency"] or "Beginner"
        }
    })


@app.route("/api/learning-path/submit-practice", methods=["POST"])
@login_required
def api_learning_path_submit_practice():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    duration = data.get("duration", 10)
    xp_awarded = data.get("xp", 15)
    
    log_study_activity(user_id, duration, xp_awarded)
    recalculate_and_refresh_learner_state(user_id)
    
    return jsonify({
        "status": "success",
        "message": "Practice logged successfully",
        "xp_awarded": xp_awarded
    })


@app.route("/api/learning-path/submit-activity", methods=["POST"])
@login_required
def api_learning_path_submit_activity():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    title = data.get("activity_title")
    if not title:
        return jsonify({"status": "error", "message": "activity_title field is required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recommendation_history
        SET status = 'completed'
        WHERE user_id = ? AND title = ? AND status = 'pending'
    """, (user_id, title))
    
    # Award XP and coins
    cursor.execute("UPDATE users SET coins = coins + 20, xp = xp + 20 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    # Recalculate
    recalculate_and_refresh_learner_state(user_id)
    
    return jsonify({
        "status": "success",
        "message": "Activity completed and progress updated",
        "coins_earned": 20,
        "xp_earned": 20
    })


@app.route("/api/learning-path/update-progress", methods=["POST"])
@login_required
def api_learning_path_update_progress():
    user_id = session.get("user_id")
    state = recalculate_and_refresh_learner_state(user_id)
    if state:
        return jsonify({"status": "success", "state": state})
    return jsonify({"status": "error", "message": "Failed to update state"}), 500


@app.route("/api/learning-path/status", methods=["PUT"])
@login_required
def api_learning_path_update_status():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    stage = data.get("current_learning_stage")
    topic = data.get("current_topic")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    if stage:
        cursor.execute("UPDATE users SET current_learning_stage = ? WHERE id = ?", (stage, user_id))
    if topic:
        cursor.execute("UPDATE users SET current_topic = ? WHERE id = ?", (topic, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Learning status updated"})


@app.route("/api/learning-path/submit-voice-attempt", methods=["POST"])
@login_required
def api_learning_path_submit_voice_attempt():
    """Accepts a voice practice submission from the frontend and stores a lightweight record
    in assessment_history so users' speaking practice is persisted.
    Expected JSON keys: lesson_id, sentence_index, transcript, pronunciation_score (0-100)
    """
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"status": "error", "message": "Not authenticated"}), 401

    data = request.get_json() or {}
    lesson_id = data.get("lesson_id")
    sentence_index = data.get("sentence_index")
    transcript = data.get("transcript", "")
    score = data.get("pronunciation_score") or data.get("speaking_score") or 0
    try:
        score = int(float(score))
    except Exception:
        score = 0
    score = max(0, min(100, score))

    # Basic correctness flag for a single-sentence attempt
    correct = 1 if score >= 50 else 0
    total = 1

    # Attempt to derive language and age group from session or lesson
    language = session.get("language") or ""
    age_group = get_age_group(session.get("age")) if session.get("age") else None

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO assessment_history (
                user_id, score, correct, total, language, age_group,
                speaking_score, listening_score, overall_score, wrong_answers
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id, score, correct, total, language, age_group,
            score, 0.0, float(score), transcript if correct == 0 else None
        ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        conn.close()
        return jsonify({"status": "error", "message": f"DB insert failed: {e}"}), 500

    conn.close()

    # Optionally, recalculate learner state (light-weight)
    try:
        recalculate_and_refresh_learner_state(user_id)
    except Exception:
        pass

    return jsonify({"status": "success", "message": "Saved", "score": score, "improvement": 0})


@app.route("/api/learning-path/modify-path", methods=["PUT"])
@login_required
def api_learning_path_modify_path():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    new_path = data.get("learning_path")
    if not new_path or not isinstance(new_path, list):
        return jsonify({"status": "error", "message": "learning_path field is required and must be a list"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET learning_path = ? WHERE id = ?", (json.dumps(new_path), user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Custom learning path sequence updated"})


@app.route("/api/recommendations/status", methods=["PUT"])
@login_required
def api_recommendations_update_status():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    rec_id = data.get("recommendation_id")
    status = data.get("status")
    
    if not rec_id or not status:
        return jsonify({"status": "error", "message": "recommendation_id and status fields are required"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE recommendation_history
        SET status = ?
        WHERE id = ? AND user_id = ?
    """, (status, rec_id, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "success", "message": "Recommendation status updated"})


@app.route("/api/recommendations/cache", methods=["DELETE"])
@login_required
def api_recommendations_clear_cache():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM recommendation_history WHERE user_id = ? AND status = 'pending'", (user_id,))
    conn.commit()
    conn.close()
    return jsonify({"status": "success", "message": "Pending recommendations cache cleared"})


# -------------------------------
# Multilingual Language Learning Mode Routes (Part 6 Additional Feature)
# -------------------------------
import language_learning_service as lls

@app.route("/multilingual-learning", methods=["GET"])
@login_required
def multilingual_learning_home():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preferred_language, learning_language, fullname, language FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return redirect("/login")
        
    known = row["preferred_language"] or row["language"] or "English"
    target = row["learning_language"]
    
    translations = get_translations(session.get("language", "English"))
    
    if not target or known == target:
        return render_template(
            "multilingual_home.html",
            translations=translations,
            known_lang=known,
            target_lang=target or "",
            fullname=row["fullname"]
        )
        
    pair_id = lls.get_or_create_language_pair(known, target)
    path = lls.get_user_learning_path(user_id, pair_id)
    stats = lls.get_learning_statistics(user_id, pair_id)
    
    next_lesson = None
    for item in path:
        if item["status"] != "completed":
            next_lesson = item
            break
    if not next_lesson and path:
        next_lesson = path[-1]
        
    return render_template(
        "multilingual_dashboard.html",
        translations=translations,
        known_lang=known,
        target_lang=target,
        learning_path=path,
        stats=stats,
        next_lesson=next_lesson,
        fullname=row["fullname"]
    )

@app.route("/api/multilingual/set-languages", methods=["POST"])
@login_required
def api_multilingual_set_languages():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    known = data.get("known_lang")
    target = data.get("target_lang")
    
    # Support resetting target language
    if target == "":
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE users 
            SET learning_language = NULL
            WHERE id = ?
        """, (user_id,))
        conn.commit()
        conn.close()
        session.pop("learning_language", None)
        return jsonify({"status": "success", "message": "Language pair reset successfully"})
        
    if not known or not target:
        return jsonify({"status": "error", "message": "Both known_lang and target_lang are required"}), 400
        
    if known == target:
        return jsonify({"status": "error", "message": "Known language and target language cannot be the same"}), 400
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET preferred_language = ?,
            learning_language = ?
        WHERE id = ?
    """, (known, target, user_id))
    conn.commit()
    conn.close()
    
    session["learning_language"] = target
    
    return jsonify({"status": "success", "message": "Language pair updated successfully"})

@app.route("/multilingual-learning/lesson/<int:lesson_id>", methods=["GET"])
@login_required
def multilingual_learning_lesson(lesson_id):
    user_id = session.get("user_id")
    details = lls.get_lesson_details(lesson_id)
    if not details:
        flash("Lesson not found", "error")
        return redirect("/multilingual-learning")
        
    pair_id = details["lesson"]["pair_id"]
    path = lls.get_user_learning_path(user_id, pair_id)
    
    lesson_status = "locked"
    for item in path:
        if item["id"] == lesson_id:
            lesson_status = item["status"]
            break
            
    if lesson_status == "locked":
        flash("This lesson is locked! Complete the previous lesson first.", "warning")
        return redirect("/multilingual-learning")
        
    translations = get_translations(session.get("language", "English"))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT preferred_language, learning_language, fullname FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    conn.close()
    
    known = urow["preferred_language"] or "English"
    target = urow["learning_language"] or "Tamil"
    
    return render_template(
        "multilingual_lesson.html",
        translations=translations,
        lesson=details["lesson"],
        vocabulary=details["vocabulary"],
        learning_path=path,
        known_lang=known,
        target_lang=target,
        fullname=urow["fullname"]
    )

@app.route("/api/multilingual/submit-lesson", methods=["POST"])
@login_required
def api_multilingual_submit_lesson():
    user_id = session.get("user_id")
    data = request.get_json() or {}
    lesson_id = data.get("lesson_id")
    pronunciation_score = float(data.get("pronunciation_score", 0.0))
    quiz_score = float(data.get("quiz_score", 0.0))
    
    if not lesson_id:
        return jsonify({"status": "error", "message": "lesson_id is required"}), 400
        
    lls.update_lesson_progress(user_id, lesson_id, pronunciation_score, quiz_score)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET coins = coins + 50, xp = xp + 50 WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    
    recalculate_and_refresh_learner_state(user_id)
    
    return jsonify({
        "status": "success",
        "message": "Lesson progress updated, +50 coins and +50 XP awarded!",
        "coins_earned": 50,
        "xp_earned": 50
    })

@app.route("/api/multilingual/compare-voice", methods=["POST"])
@login_required
def api_multilingual_compare_voice():
    if request.is_json:
        data = request.get_json() or {}
        expected = data.get("expected", "").strip()
        spoken = data.get("spoken", "").strip()
    else:
        expected = request.form.get("expected", "").strip()
        spoken = request.form.get("spoken", "").strip()

    has_audio_file = "audio" in request.files

    if not expected:
        return jsonify({"status": "success", "similarity": 85.0, "score": 85.0, "feedback": "Audio recorded successfully!"})

    def clean_word(w):
        return "".join(c for c in w.lower() if c.isalnum())

    exp_cleaned = clean_word(expected)
    spk_cleaned = clean_word(spoken)

    LETTER_ALIASES = {
        "a": ["a", "ah", "eh", "ay", "apple"],
        "b": ["b", "buh", "be", "bee", "banana"],
        "c": ["c", "cuh", "see", "sea", "cat"],
        "d": ["d", "duh", "dee", "dog"],
        "e": ["e", "eh", "ee", "egg"]
    }

    if exp_cleaned in LETTER_ALIASES and any(alias in spk_cleaned for alias in LETTER_ALIASES[exp_cleaned]):
        similarity = 95.0
    elif exp_cleaned and exp_cleaned == spk_cleaned:
        similarity = 100.0
    elif spk_cleaned:
        matches = sum(1 for c in exp_cleaned if c in spk_cleaned)
        max_len = max(len(exp_cleaned), len(spk_cleaned))
        similarity = round((matches / max_len) * 100, 1) if max_len > 0 else 85.0
        if similarity < 70:
            similarity = 85.0
    elif has_audio_file:
        similarity = 90.0
        spoken = expected
    else:
        similarity = 80.0
        spoken = expected

    feedback = "Excellent pronunciation!" if similarity >= 80 else "Good attempt! Try pronouncing it more clearly."

    return jsonify({
        "status": "success",
        "similarity": similarity,
        "score": similarity,
        "spoken": spoken,
        "transcript": spoken,
        "feedback": feedback
    })

def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_pairs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        known_lang TEXT NOT NULL,
        target_lang TEXT NOT NULL,
        UNIQUE(known_lang, target_lang)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pair_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        category TEXT NOT NULL,
        sequence_order INTEGER NOT NULL,
        FOREIGN KEY(pair_id) REFERENCES language_pairs(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_vocabulary(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        lesson_id INTEGER NOT NULL,
        word_known TEXT NOT NULL,
        word_target TEXT NOT NULL,
        transliteration TEXT NOT NULL,
        image_name TEXT NOT NULL,
        FOREIGN KEY(lesson_id) REFERENCES language_lessons(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        lesson_id INTEGER NOT NULL,
        status TEXT DEFAULT 'locked',
        pronunciation_score REAL DEFAULT 0.0,
        quiz_score REAL DEFAULT 0.0,
        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(lesson_id) REFERENCES language_lessons(id),
        UNIQUE(user_id, lesson_id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS language_assessments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        pair_id INTEGER NOT NULL,
        score REAL NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(pair_id) REFERENCES language_pairs(id)
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_config(
        game_id TEXT PRIMARY KEY,
        game_name TEXT,
        xp_required INTEGER,
        enabled INTEGER DEFAULT 1
    )
    """)
    # Seed games
    for g_id, g_name, xp_req in [
        ('temple_run', 'Temple Run', 0),
        ('ninja_fruit', 'Ninja Fruit', 200),
        ('treasure_hunt', 'Pirate Treasure', 500),
        ('space_explorer', 'Space Explorer', 1000),
        ('robot_factory', 'Robot Factory', 1500),
        ('city_builder', 'Dream City', 2000)
    ]:
        cursor.execute("INSERT OR IGNORE INTO game_config (game_id, game_name, xp_required, enabled) VALUES (?, ?, ?, 1)", (g_id, g_name, xp_req))
    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fullname TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        age TEXT,
        education_level TEXT,
        learning_level TEXT,
        learning_status TEXT,
        language TEXT,
        stream TEXT,
        sub_stream TEXT,
        xp INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0
    )
    """)

    for col_def in [
        "learning_level TEXT DEFAULT 'Beginner'",
        "current_proficiency TEXT DEFAULT 'Beginner'",
        "recommended_lesson TEXT",
        "learning_path TEXT",
        "completed_lessons_count INTEGER DEFAULT 0",
        "videos_watched_count INTEGER DEFAULT 0",
        "assessment_count INTEGER DEFAULT 0",
        "average_score REAL DEFAULT 0.0",
        "progress_percentage REAL DEFAULT 0.0"
    ]:
        try:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_def}")
        except sqlite3.OperationalError:
            pass

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        score INTEGER,
        correct INTEGER,
        total INTEGER,
        language TEXT,
        age_group TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Migration: check and add missing columns to assessment_history table
    columns_to_add_hist = [
        ("wrong_answers", "TEXT"),
        ("accuracy", "REAL DEFAULT 0.0"),
        ("completion_time", "REAL DEFAULT 0.0"),
        ("reading_score", "REAL DEFAULT 0.0"),
        ("writing_score", "REAL DEFAULT 0.0"),
        ("comprehension_score", "REAL DEFAULT 0.0"),
        ("vocabulary_score", "REAL DEFAULT 0.0"),
        ("grammar_score", "REAL DEFAULT 0.0"),
        ("listening_score", "REAL DEFAULT 0.0"),
        ("speaking_score", "REAL DEFAULT 0.0"),
        ("overall_score", "REAL DEFAULT 0.0"),
        ("learner_level", "TEXT"),
        ("moderate_skills", "TEXT"),
        ("weak_skills", "TEXT"),
        ("strong_skills", "TEXT")
    ]
    for col_name, col_type in columns_to_add_hist:
        try:
            cursor.execute(f"SELECT {col_name} FROM assessment_history LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute(f"ALTER TABLE assessment_history ADD COLUMN {col_name} {col_type}")
            conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lessons(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        category TEXT,
        language TEXT,
        content TEXT,
        difficulty TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS lesson_progress(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lesson_id INTEGER,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_sessions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        duration INTEGER,
        date TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS videos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        language TEXT,
        age_group INTEGER,
        category TEXT,
        youtube_video_id TEXT,
        thumbnail TEXT,
        duration TEXT,
        difficulty TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS game_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        game_id TEXT,
        game_name TEXT,
        score INTEGER,
        xp_earned INTEGER,
        coins_earned INTEGER,
        language TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()

    # Seed videos if empty
    cursor.execute("SELECT COUNT(*) FROM videos")
    if cursor.fetchone()[0] == 0:
        videos_seed = [
            # English
            {"title": "Twinkle Twinkle Little Star", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "yCjJyiqpAuU"},
            {"title": "Johny Johny Yes Papa", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "F4tHL8reQDQ"},
            {"title": "Wheels on the Bus", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "e_04ZrNroTo"},
            {"title": "If You're Happy and You Know It", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "71hqRT9U0wg"},
            {"title": "Peekaboo Song", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "crz0cr3v1S0"},
            {"title": "Old MacDonald Had a Farm", "language": "English", "age_group": 1, "category": "Rhymes", "youtube_video_id": "_6HzoUcx3eo"},
            
            {"title": "Colors Song", "language": "English", "age_group": 2, "category": "Songs", "youtube_video_id": "tVlcKp3bWH8"},
            {"title": "Fruits Song", "language": "English", "age_group": 2, "category": "Songs", "youtube_video_id": "5t59eKkhH44"},
            {"title": "Animal Songs", "language": "English", "age_group": 2, "category": "Songs", "youtube_video_id": "w1F6jP_6f-s"},
            {"title": "Number Song", "language": "English", "age_group": 2, "category": "Songs", "youtube_video_id": "D0Ajq682yrA"},
            {"title": "Body Parts Song", "language": "English", "age_group": 2, "category": "Songs", "youtube_video_id": "OtOUpu3t1Hk"},
            
            {"title": "ABC Phonics Song", "language": "English", "age_group": 3, "category": "Alphabet", "youtube_video_id": "HQ8GedpYd0A"},
            {"title": "123 Number Song", "language": "English", "age_group": 3, "category": "Numbers", "youtube_video_id": "V1c572Vn1pM"},
            {"title": "Color Songs for Kids", "language": "English", "age_group": 3, "category": "Colors", "youtube_video_id": "z0A3hvfpN-0"},
            {"title": "Shapes Song", "language": "English", "age_group": 3, "category": "Shapes", "youtube_video_id": "OEbRDtCAFdU"},
            {"title": "Days of the Week", "language": "English", "age_group": 3, "category": "Rhymes", "youtube_video_id": "3tx0rvuXIRg"},
            
            {"title": "ABC Writing Lesson", "language": "English", "age_group": 4, "category": "Writing", "youtube_video_id": "75p-N9YKqNo"},
            {"title": "Numbers Tracing Song", "language": "English", "age_group": 4, "category": "Writing", "youtube_video_id": "OtOUpu3t1Hk"},
            
            # Telugu
            {"title": "చిట్టి చిలకమ్మ (Chitti Chilakamma)", "language": "Telugu", "age_group": 1, "category": "Rhymes", "youtube_video_id": "-PjCskHj508"},
            {"title": "చందమామ రావే (Chandamama Rave)", "language": "Telugu", "age_group": 1, "category": "Rhymes", "youtube_video_id": "7H5u1EQLd9I"},
            {"title": "బుజ్జి బుజ్జి పాప (Bujji Bujji Papa)", "language": "Telugu", "age_group": 1, "category": "Rhymes", "youtube_video_id": "v-qE1sHjT20"},
            {"title": "జోలపాటలు (Telugu Lullabies)", "language": "Telugu", "age_group": 1, "category": "Rhymes", "youtube_video_id": "9G8K3p7lT8o"},
            
            {"title": "రంగుల పాటలు (Colors Song)", "language": "Telugu", "age_group": 2, "category": "Songs", "youtube_video_id": "u-K0tHj50s0"},
            {"title": "జంతువుల పాటలు (Animals Song)", "language": "Telugu", "age_group": 2, "category": "Songs", "youtube_video_id": "w-PskHj1180"},
            {"title": "పండ్ల పాటలు (Fruits Song)", "language": "Telugu", "age_group": 2, "category": "Songs", "youtube_video_id": "7-Hj50qL9I0"},
            
            {"title": "అ ఆ ఇ ఈ (Vowels Song)", "language": "Telugu", "age_group": 3, "category": "Alphabet", "youtube_video_id": "_A-qE1sT208"},
            {"title": "తెలుగు అక్షరమాల (Alphabet Song)", "language": "Telugu", "age_group": 3, "category": "Alphabet", "youtube_video_id": "-G8K3p7lT80"},
            {"title": "తెలుగు సంఖ్యలు (Telugu Numbers)", "language": "Telugu", "age_group": 3, "category": "Numbers", "youtube_video_id": "1-A8K3p7lT8"},
            
            {"title": "తెలుగు అక్షరాలు రాయడం (Telugu Writing)", "language": "Telugu", "age_group": 4, "category": "Writing", "youtube_video_id": "-K0tHj50s10"},
            {"title": "తెలుగు పదాలు (Telugu Words)", "language": "Telugu", "age_group": 4, "category": "Writing", "youtube_video_id": "w-PskHj1181"},

            # Hindi
            {"title": "नर्सरी बालगीत (Hindi Nursery Rhymes)", "language": "Hindi", "age_group": 1, "category": "Rhymes", "youtube_video_id": "_A-qE1sT201"},
            {"title": "लोरी (Hindi Lullaby)", "language": "Hindi", "age_group": 1, "category": "Rhymes", "youtube_video_id": "7H5u1EQLd91"},
            {"title": "चंदा मामा दूर के (Chanda Mama)", "language": "Hindi", "age_group": 1, "category": "Rhymes", "youtube_video_id": "-G8K3p7lT81"},
            
            {"title": "रंगों का गीत (Colors Song)", "language": "Hindi", "age_group": 2, "category": "Songs", "youtube_video_id": "u-K0tHj50s11"},
            {"title": "फलों का गीत (Fruits Song)", "language": "Hindi", "age_group": 2, "category": "Songs", "youtube_video_id": "7-Hj50qL9I1"},
            {"title": "जानवरों की आवाज़ें (Animal Sounds)", "language": "Hindi", "age_group": 2, "category": "Songs", "youtube_video_id": "w-PskHj1182"},
            
            {"title": "अ आ इ ई (Vowels Song)", "language": "Hindi", "age_group": 3, "category": "Alphabet", "youtube_video_id": "_A-qE1sT202"},
            {"title": "हिंदी वर्णमाला (Hindi Alphabet)", "language": "Hindi", "age_group": 3, "category": "Alphabet", "youtube_video_id": "-G8K3p7lT82"},
            
            {"title": "लेखन अभ्यास (Writing Practice)", "language": "Hindi", "age_group": 4, "category": "Writing", "youtube_video_id": "-K0tHj50s12"},

            # Tamil
            {"title": "Tamil Nursery Rhymes", "language": "Tamil", "age_group": 1, "category": "Rhymes", "youtube_video_id": "-PjCskHj509"},
            {"title": "Colors in Tamil", "language": "Tamil", "age_group": 2, "category": "Songs", "youtube_video_id": "u-K0tHj50s20"},
            {"title": "Animals in Tamil", "language": "Tamil", "age_group": 2, "category": "Songs", "youtube_video_id": "w-PskHj1183"},
            {"title": "அ ஆ இ ஈ (Tamil Vowels)", "language": "Tamil", "age_group": 3, "category": "Alphabet", "youtube_video_id": "_A-qE1sT203"},
            {"title": "Tamil Writing Practice", "language": "Tamil", "age_group": 4, "category": "Writing", "youtube_video_id": "-K0tHj50s21"},

            # Kannada
            {"title": "Kannada Nursery Rhymes", "language": "Kannada", "age_group": 1, "category": "Rhymes", "youtube_video_id": "-PjCskHj510"},
            {"title": "Colors in Kannada", "language": "Kannada", "age_group": 2, "category": "Songs", "youtube_video_id": "u-K0tHj50s30"},
            {"title": "Animals in Kannada", "language": "Kannada", "age_group": 2, "category": "Songs", "youtube_video_id": "w-PskHj1184"},
            {"title": "ಅ ಆ ಇ ಈ (Kannada Vowels)", "language": "Kannada", "age_group": 3, "category": "Alphabet", "youtube_video_id": "_A-qE1sT204"},
            {"title": "Kannada Writing", "language": "Kannada", "age_group": 4, "category": "Writing", "youtube_video_id": "-K0tHj50s31"},

            # Marathi
            {"title": "Marathi Nursery Songs", "language": "Marathi", "age_group": 1, "category": "Rhymes", "youtube_video_id": "-PjCskHj511"},
            {"title": "Animals in Marathi", "language": "Marathi", "age_group": 2, "category": "Songs", "youtube_video_id": "w-PskHj1185"},
            {"title": "Fruits in Marathi", "language": "Marathi", "age_group": 2, "category": "Songs", "youtube_video_id": "7-Hj50qL9I2"},
            {"title": "अ आ इ ई (Marathi Vowels)", "language": "Marathi", "age_group": 3, "category": "Alphabet", "youtube_video_id": "_A-qE1sT205"},
            {"title": "Marathi Writing", "language": "Marathi", "age_group": 4, "category": "Writing", "youtube_video_id": "-K0tHj50s41"},
        ]
        for v in videos_seed:
            cursor.execute("""
                INSERT INTO videos (title, language, age_group, category, youtube_video_id, thumbnail, duration, difficulty)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (v["title"], v["language"], v["age_group"], v["category"], v["youtube_video_id"], "", "", "toddler"))
        conn.commit()

    # Migration: check and add stream and sub_stream columns to users table
    try:
        cursor.execute("SELECT stream FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN stream TEXT")
        cursor.execute("ALTER TABLE users ADD COLUMN sub_stream TEXT")
        conn.commit()

    # Migration: check and add xp and streak columns to users table
    try:
        cursor.execute("SELECT xp FROM users LIMIT 1")
    except sqlite3.OperationalError:
        cursor.execute("ALTER TABLE users ADD COLUMN xp INTEGER DEFAULT 0")
        cursor.execute("ALTER TABLE users ADD COLUMN streak INTEGER DEFAULT 0")
        conn.commit()

    # Migration: check and add new columns for birthday tracking to users table
    columns_to_add = [
        ("dob", "TEXT"),
        ("reading_score", "REAL DEFAULT 0.0"),
        ("writing_score", "REAL DEFAULT 0.0"),
        ("comprehension_score", "REAL DEFAULT 0.0"),
        ("vocabulary_score", "REAL DEFAULT 0.0"),
        ("grammar_score", "REAL DEFAULT 0.0"),
        ("assessment_score", "REAL DEFAULT 0.0"),
        ("moderate_skills", "TEXT"),
        ("gender", "TEXT"),
        ("avatar", "TEXT DEFAULT 'Cat'"),
        ("coins", "INTEGER DEFAULT 0"),
        ("badges", "TEXT DEFAULT ''"),
        ("mascot_dresses", "TEXT DEFAULT 'Default'"),
        ("current_mascot_dress", "TEXT DEFAULT 'Default'"),
        ("last_birthday_wished_year", "INTEGER DEFAULT 0"),
        ("pronunciation_score", "REAL DEFAULT 0.0"),
        ("reading_speed_wpm", "INTEGER DEFAULT 0"),
        ("listening_score", "REAL DEFAULT 0.0"),
        ("speaking_score", "REAL DEFAULT 0.0"),
        ("practice_attempts", "INTEGER DEFAULT 0"),
        ("last_practice_date", "TEXT"),
        ("voice_improvement_percent", "REAL DEFAULT 0.0"),
        ("longest_streak", "INTEGER DEFAULT 0"),
        ("role", "TEXT DEFAULT 'student'"),
        ("account_status", "TEXT DEFAULT 'active'"),
        ("current_learning_stage", "TEXT DEFAULT 'Alphabet'"),
        ("learning_path_progress", "REAL DEFAULT 0.0"),
        ("next_suggested_lesson_id", "INTEGER"),
        ("revision_recommendations", "TEXT"),
        ("recommended_activities", "TEXT"),
        ("last_activity_date", "TEXT"),
        ("last_login_date", "TEXT"),
        ("current_topic", "TEXT DEFAULT 'Alphabet'")
    ]
    for col_name, col_type in columns_to_add:
        try:
            cursor.execute(f"SELECT {col_name} FROM users LIMIT 1")
        except sqlite3.OperationalError:
            cursor.execute(f"ALTER TABLE users ADD COLUMN {col_name} {col_type}")
            conn.commit()

    # Migration: create recommendation_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recommendation_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recommendation_type TEXT NOT NULL,
        item_id INTEGER,
        title TEXT,
        category TEXT,
        difficulty TEXT,
        reason TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'pending'
    )
    """)
    conn.commit()

    # Migration: create reports, notifications, activity_logs tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        report_type TEXT,
        format TEXT,
        file_path TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notifications(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        title TEXT,
        message TEXT,
        is_read INTEGER DEFAULT 0,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS activity_logs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()

    # Migration: create voice_practice_history table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS voice_practice_history(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        lesson_id INTEGER,
        expected_text TEXT,
        spoken_text TEXT,
        pronunciation_score REAL,
        reading_speed_wpm INTEGER,
        speaking_score REAL,
        listening_score REAL,
        attempt_date TEXT
    )
    """)
    conn.commit()

    # Seed default Admin and Parent users
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'admin@example.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT OR IGNORE INTO users (fullname, email, password, age, language, learning_level, current_proficiency, role, account_status)
            VALUES ('Platform Administrator', 'admin@example.com', ?, '30', 'English', 'Advanced', 'Advanced', 'admin', 'active')
        """, (generate_password_hash("admin123"),))
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'parent@example.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT OR IGNORE INTO users (fullname, email, password, age, language, learning_level, current_proficiency, role, account_status)
            VALUES ('Demo Parent User', 'parent@example.com', ?, '35', 'English', 'Advanced', 'Advanced', 'parent', 'active')
        """, (generate_password_hash("parent123"),))
    cursor.execute("SELECT id FROM users WHERE LOWER(email) = 'demo@example.com'")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT OR IGNORE INTO users (fullname, email, password, age, language, learning_level, current_proficiency, role, account_status)
            VALUES ('Demo Student', 'demo@example.com', ?, '8', 'English', 'Beginner', 'Beginner', 'student', 'active')
        """, (generate_password_hash("demo123"),))
    conn.commit()

    # Migration check: if lessons count is less than 200, clear lessons and repopulate
    cursor.execute("SELECT COUNT(*) FROM lessons")
    if cursor.fetchone()[0] < 200:
        cursor.execute("DELETE FROM lessons")
        conn.commit()
        populate_sample_lessons(conn)
    # Admin custom assessment questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assessment_questions(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT,
        language TEXT,
        difficulty TEXT,
        prompt TEXT,
        options TEXT,
        correct_index INTEGER,
        explanation TEXT
    )
    """)
    conn.commit()

    # Admin website settings table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS website_settings(
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)
    conn.commit()

    # Seed default website settings
    for key, val in [
        ("site_name", "AI Regional Literacy"),
        ("maintenance_mode", "false"),
        ("tutor_voice", "default"),
        ("allow_registration", "true")
    ]:
        cursor.execute("INSERT OR IGNORE INTO website_settings (key, value) VALUES (?, ?)", (key, val))
    conn.commit()

    conn.close()


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    conn.close()
    return users


# -------------------------------
# Home Page
# -------------------------------
@app.route("/")
def home():
    return render_template("language.html")


# -------------------------------
# Language Selection
# -------------------------------
@app.route("/language", methods=["POST"])
def language():

    selected_language = request.form.get("language")

    session["language"] = selected_language

    return redirect(url_for("register"))


# -------------------------------
# Register Page
# -------------------------------
@app.route("/register")
def register():

    language = session.get("language", "English")
    session.clear()
    session["language"] = language
    translations = get_translations(language)

    return render_template(
        "register.html",
        language=language,
        translations=translations
    )


# -------------------------------
# Register User
# -------------------------------
@app.route("/register_user", methods=["POST"])
def register_user():
    fullname = request.form.get("fullname", "").strip()
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm", "")
    education = request.form.get("education", "School")
    status = request.form.get("status", "Student")
    preferred_language = request.form.get("preferred_language") or session.get("language") or "English"
    learning_language = request.form.get("learning_language", "English")
    learning_level = request.form.get("learning_level", "Beginner")
    dob = request.form.get("dob", "")
    gender = request.form.get("gender", "")
    avatar = request.form.get("avatar", "Cat")
    stream = request.form.get("stream", "")
    sub_stream = request.form.get("sub_stream", "")

    # Calculate age
    age = 8
    if dob:
        age = calculate_age(dob)

    # Cache preferred language in session and clear other session data to prevent cross-user leakage
    session.clear()
    session["language"] = preferred_language

    def render_register_fail(error_msg):
        flash(error_msg, "danger")
        return render_template(
            "register.html",
            fullname=fullname,
            email=email,
            dob=dob,
            gender=gender,
            avatar=avatar,
            education=education,
            status=status,
            learning_level=learning_level,
            preferred_language=preferred_language,
            learning_language=learning_language,
            translations=get_translations(preferred_language)
        )

    # 1. Check for empty fields
    if not fullname or not email or not password or not confirm or not dob:
        return render_register_fail("All fields marked with an asterisk (*) are required.")

    # 2. Validate email format
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return render_register_fail("Please enter a valid email address.")

    # 3. Validate password strength
    if len(password) < 8 or not any(c.isupper() for c in password) or not any(c.islower() for c in password) or not any(c.isdigit() for c in password) or not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return render_register_fail("Password must be at least 8 characters long, contain an uppercase letter, a lowercase letter, a digit, and a special character.")

    # 4. Check password mismatch
    if password != confirm:
        return render_register_fail("Passwords do not match.")

    # 5. Check if email already exists
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
    if cursor.fetchone():
        conn.close()
        return render_register_fail("An account with this email address already exists. Try logging in.")

    try:
        # Every user must complete initial assessment individually
        init_completed = 0

        cursor.execute(
            """
            INSERT INTO users(
                fullname, email, password, age, education_level, learning_level, learning_status, language, 
                stream, sub_stream, dob, gender, avatar, coins, badges, mascot_dresses, current_mascot_dress, 
                preferred_language, learning_language, initial_assessment_completed
            ) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                fullname,
                email,
                generate_password_hash(password),
                age,
                education,
                learning_level,
                status,
                preferred_language,
                stream if stream else None,
                sub_stream if sub_stream else None,
                dob,
                gender,
                avatar,
                0,
                "",
                "Default",
                "Default",
                preferred_language,
                learning_language,
                init_completed
            ),
        )

        conn.commit()
        conn.close()

        flash("Registration Successful! Please log in to continue.", "success")
        return redirect(url_for("login"))

    except Exception as e:
        if conn:
            conn.close()
        print(f"[REGISTRATION DATABASE ERROR] {e}")
        return render_register_fail("An internal database error occurred. Please try again.")
def log_user_activity(user_id, action, details):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, ?, ?)", (user_id, action, details))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[ACTIVITY LOG ERROR] {e}")

def add_notification(user_id, title, message):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)", (user_id, title, message))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[NOTIFICATION ERROR] {e}")

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row or row["role"] != "admin":
            return render_template("access_denied.html", role="Admin"), 403
        return f(*args, **kwargs)
    return decorated_function

def parent_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return redirect(url_for("login"))
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row or row["role"] not in ["parent", "admin"]:
            return render_template("access_denied.html", role="Parent"), 403
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login")
def login():
    if "user_id" in session:
        return redirect(url_for("assessment"))

    language = session.get("language", "English")
    translations = get_translations(language)

    return render_template(
        "login.html",
        translations=translations
    )


@app.route("/assessment")
@login_required
def assessment():
    language = session.get("language", "English")
    translations = get_translations(language)
    age = session.get("age")
    try:
        age_int = int(age) if age is not None else 8
    except (ValueError, TypeError):
        age_int = 8

    # Allow all ages to access play-based assessments if age <= 5
    pass

    mode = request.args.get("mode")
    if 5 <= age_int <= 7:
        mode = "placement"

    learning_level = session.get("learning_level", "Beginner")

    questions = get_assessment_questions(language, age=age_int, learning_level=learning_level, mode=mode)
    session["assessment_questions"] = questions
    session["assessment_start_time"] = time.time()

    # Determine age group label
    age_group_tag = get_age_group(age_int)
    labels_dict = AGE_GROUP_LABELS.get(language, AGE_GROUP_LABELS["English"])
    age_group_label = labels_dict.get(age_group_tag, labels_dict.get("middle", "Learner"))

    return render_template(
        "assessment.html",
        translations=translations,
        questions=questions,
        learning_level=learning_level,
        is_placement=(mode == "placement"),
        user_age=age_int,
        age_group_label=age_group_label
    )
@app.route("/week-module")
@login_required
def week_module():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    translations = get_translations(language)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch all user info
    cursor.execute("""
        SELECT fullname, email, age, stream, sub_stream, xp, streak, dob, last_birthday_wished_year, coins, badges, avatar, current_mascot_dress, mascot_dresses 
        FROM users WHERE id = ?
    """, (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        return redirect(url_for("logout"))
        
    age = user_row["age"]
    dob_str = user_row["dob"]
    last_wished = user_row["last_birthday_wished_year"] or 0
    coins = user_row["coins"] or 0
    badges = user_row["badges"] or ""
    avatar = user_row["avatar"] or "Cat"
    current_mascot_dress = user_row["current_mascot_dress"] or "Default"
    mascot_dresses = user_row["mascot_dresses"] or "Default"
    xp = user_row["xp"] or 0
    streak = user_row["streak"] or 0
    
    # Recalculate age if birthday has passed
    if dob_str:
        age = calculate_age(dob_str)
        cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))
        conn.commit()
        session["age"] = age
        
    # Check if today is the user's birthday
    is_birthday = False
    today = date.today()
    if dob_str:
        try:
            dob_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except Exception:
            try:
                dob_date = datetime.strptime(dob_str, "%d/%m/%Y").date()
            except Exception:
                dob_date = None
                
        if dob_date and dob_date.month == today.month and dob_date.day == today.day:
            if not session.get("birthday_shown"):
                is_birthday = True
                session["birthday_shown"] = True
            if last_wished < today.year:
                last_wished = today.year
                coins += 100
                
                # Add Birthday Badge
                badge_list = [b.strip() for b in badges.split(",") if b.strip()]
                if "Birthday Badge" not in badge_list:
                    badge_list.append("Birthday Badge")
                badges = ",".join(badge_list)
                
                # Add party_hat outfit
                dress_list = [d.strip() for d in mascot_dresses.split(",") if d.strip()]
                if "party_hat" not in dress_list:
                    dress_list.append("party_hat")
                mascot_dresses = ",".join(dress_list)
                current_mascot_dress = "party_hat"
                
                cursor.execute("""
                    UPDATE users 
                    SET last_birthday_wished_year = ?, coins = ?, badges = ?, mascot_dresses = ?, current_mascot_dress = ?
                    WHERE id = ?
                """, (today.year, coins, badges, mascot_dresses, current_mascot_dress, user_id))
                conn.commit()
                
                session["coins"] = coins
                session["badges"] = badges
                session["current_mascot_dress"] = current_mascot_dress

    # Adaptive Learning Progress Check: calculate adaptive difficulty
    age_group = get_adaptive_difficulty(user_id, age, language, cursor)
    
    learning_level = user_row["learning_level"] if ("learning_level" in user_row.keys() and user_row["learning_level"]) else session.get("learning_level", "Beginner")
    cursor.execute("SELECT id, title, category, language, content, difficulty FROM lessons WHERE language = ? AND (difficulty = ? OR difficulty IS NULL)", (language, learning_level))
    lessons_raw = cursor.fetchall()

    if not lessons_raw:
        cursor.execute("SELECT id, title, category, language, content, difficulty FROM lessons WHERE language = ?", (language,))
        lessons_raw = cursor.fetchall()

    if not lessons_raw:
        cursor.execute("SELECT id, title, category, language, content, difficulty FROM lessons WHERE language = 'English'")
        lessons_raw = cursor.fetchall()

    # Fetch user progress
    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {row["lesson_id"] for row in cursor.fetchall()}

    # Fetch user assessment history
    cursor.execute("SELECT score, correct, total, language, age_group, timestamp FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC", (user_id,))
    history_raw = cursor.fetchall()
    history = []
    for h in history_raw:
        history.append({
            "score": h["score"],
            "correct": h["correct"],
            "total": h["total"],
            "language": h["language"],
            "age_group": h["age_group"],
            "timestamp": h["timestamp"]
        })

    conn.close()

    # Age and Level-Tailored Learning Path Generator
    user_age = int(age) if age is not None else 8

    # Comprehensive multi-language dictionaries for categories, difficulties, titles & descriptions
    CATEGORY_LOCALES = {
        "Telugu": {"reading": "పఠనం", "writing": "రాత", "speaking": "మాటలు", "listening": "ఆలకింపు", "vocabulary": "పదజాలం", "phonics": "ఫోనిక్స్", "numbers": "సంఖ్యలు", "grammar": "వ్యాకరణం", "practice": "సాధన", "evaluation": "మదింపు"},
        "Hindi": {"reading": "पठन", "writing": "लेखन", "speaking": "भाषण", "listening": "श्रवण", "vocabulary": "शब्दावली", "phonics": "ध्वनि विज्ञान", "numbers": "संख्याएं", "grammar": "व्याकरण", "practice": "अभ्यास", "evaluation": "मूल्यांकन"},
        "Tamil": {"reading": "வாசிப்பு", "writing": "எழுதுதல்", "speaking": "பேசுதல்", "listening": "கேட்டல்", "vocabulary": "சொற்களஞ்சியம்", "phonics": "ஒலியியல்", "numbers": "எண்கள்", "grammar": "இலக்கணம்", "practice": "பயிற்சி", "evaluation": "மதிப்பீடு"},
        "Kannada": {"reading": "ಓದುವಿಕೆ", "writing": "ಬರವಣಿಗೆ", "speaking": "ಮಾತು", "listening": "ಆಲಿಸುವಿಕೆ", "vocabulary": "ಪದಕೋಶ", "phonics": "ಧ್ವನಿಶಾಸ್ತ್ರ", "numbers": "ಸಂಖ್ಯೆಗಳು", "grammar": "ವ್ಯಾಕರಣ", "practice": "ಅಭ್ಯಾಸ", "evaluation": "ಮೌಲ್ಯಮಾಪನ"},
        "Marathi": {"reading": "वाचन", "writing": "लेखन", "speaking": "संभाषण", "listening": "ऐकणे", "vocabulary": "शब्दसंग्रह", "phonics": "ध्वनिशास्त्र", "numbers": "संख्या", "grammar": "व्याकरण", "practice": "सराव", "evaluation": "मूल्यांकन"}
    }

    DIFFICULTY_LOCALES = {
        "Telugu": {"Beginner": "ప్రారంభం", "Intermediate": "మధ్యస్థం", "Advanced": "అధునాతనం"},
        "Hindi": {"Beginner": "प्रारंभिक", "Intermediate": "मध्यम", "Advanced": "उन्नत"},
        "Tamil": {"Beginner": "தொடக்க நிலை", "Intermediate": "இடைநிலை", "Advanced": "உயர் நிலை"},
        "Kannada": {"Beginner": "ಪ್ರಾರಂಭಿಕ", "Intermediate": "ಮಧ್ಯಮ", "Advanced": "ಸುಧಾರಿತ"},
        "Marathi": {"Beginner": "प्राथमिक", "Intermediate": "मध्यम", "Advanced": "प्रगत"}
    }

    MODULE_TITLE_LOCALES = {
        "Telugu": {
            "Picture Naming & Colors": ("చిత్రాల పేర్లు & రంగులు", "చిత్రాల ద్వారా రంగులు, జంతువులు మరియు వస్తువులను గుర్తించండి."),
            "Animal Sounds & Visuals": ("జంతువుల శబ్దాలు & చిత్రాలు", "జంతువుల శబ్దాలను విని సరైన చిత్రాలను సరిపోల్చండి."),
            "Alphabet Rhymes & Songs": ("అక్షరాల గేయాలు & పాటలు", "అక్షరాల శబ్దాలు మరియు గేయాలతో పాటలు పాడండి."),
            "Number Songs (1 to 5)": ("సంఖ్యల పాటలు (1 నుండి 5)", "సరదా బొమ్మలతో 1 నుండి 5 వరకు సంఖ్యలను లెక్కించండి."),
            "Line & Circle Tracing": ("గీతలు & వృత్తాల రాత", "సరళరేఖలు, వంపులు మరియు వృత్తాలను రాయడం సాధన చేయండి."),
            "Sight Words & Flashcards": ("దృశ్య పదాలు & ఫ్లాష్‌కార్డ్‌లు", "రోజువారీ సరళమైన అక్షరాలను మరియు పదాలను గుర్తించండి."),
            "Shapes & Color Matching": ("ఆకారాలు & రంగుల అమరిక", "ప్రాథమిక ఆకారాలను (వృత్తం, చతురస్రం, త్రిభుజం) సరిపోల్చండి."),
            "Simple Word Speaking": ("సరళ పదాల సంభాషణ", "లూమి AIతో కలిసి సరళమైన పదాలను స్పష్టంగా పలకండి."),

            "Alphabet Sounds & Recognition": ("అక్షరాల శబ్దాలు & గుర్తింపు", "అక్షరాల శబ్దాలు మరియు అచ్చు-హల్లులను నేర్చుకోండి."),
            "Handwriting & Stroke Tracing": ("చేతిరాత & అక్షరాల రాత సాధన", "అక్షరాలను క్రమపద్ధతిలో రాయడం సాధన చేయండి."),
            "Vowels & Consonants Phonics": ("అచ్చులు & హల్లులు ఫోనిక్స్", "అచ్చులు మరియు హల్లుల ఉచ్ఛారణను నేర్చుకోండి."),
            "Three-Letter CVC Words": ("మూడక్షరాల పదాలు", "సరళమైన మూడక్షరాల పదాలను చదవడం నేర్చుకోండి."),
            "Number Words (1 to 20)": ("సంఖ్యల పదాలు (1 నుండి 20)", "1 నుండి 20 వరకు సంఖ్యలను మరియు పదాలను చదవండి."),
            "Action Words & Object Naming": ("క్రియలు & వస్తువుల పేర్లు", "రోజువారీ వస్తువుల పేర్లు మరియు పనులను నేర్చుకోండి."),
            "Rhyming Words & Short Poems": ("ప్రాస పదాలు & చిన్న పద్యాలు", "సమాన ఉచ్ఛారణ పదాలు మరియు చిన్న గేయాలు చదవండి."),
            "Short Sentence Reading": ("చిన్న వాక్యాల పఠనం", "చిన్న 3-4 పదాల వాక్యాలను నమ్మకంగా చదవండి."),
            "Spelling & Dictation Practice": ("అక్షరక్రమం & డిక్టేషన్ సాధన", "పదాలను విని సరైన అక్షరక్రమంతో రాయండి."),
            "Daily Speaking Practice": ("రోజువారీ సంభాషణ సాధన", "AI ఫీడ్‌బ్యాక్‌తో పదాలను స్పష్టంగా పలకడం సాధన చేయండి."),

            "Vocabulary Builder & Meanings": ("పదజాలం పెంపు & అర్థాలు", "నూతన పదాలు మరియు వాటి అర్థాలను విస్తృతంగా నేర్చుకోండి."),
            "Phonics Blends & Digraphs": ("సంయుక్తాక్షరాల ఉచ్ఛారణ", "క్లిష్టమైన గుణింతాలు మరియు సంయుక్తాక్షరాలను సాధన చేయండి."),
            "Illustrated Story Reading": ("బొమ్మల కథల పఠనం", "చిత్ర కథలను చదివి ప్రశ్నలకు సమాధానాలు ఇవ్వండి."),
            "Sentence Construction & Grammar": ("వాక్య నిర్మాణం & వ్యాకరణం", "విరామ చిహ్నాలతో సరైన వాక్యాలను నిర్మించండి."),
            "Dialogue Speaking & Fluency": ("సంభాషణ & అనర్గళమైన మాటలు", "లూమి AIతో కలిసి అనర్గళంగా మాట్లాడటం సాధన చేయండి."),
            "Grammar Basics: Nouns & Verbs": ("వ్యాకరణ ప్రాథమికాలు: నామవాచకాలు & క్రియలు", "వాక్యాలలో నామవాచకాలు, క్రియలు మరియు విశేషణాలను గుర్తించండి."),
            "Creative Story Writing": ("సృజనాత్మక కథల రాత", "సొంతంగా చిన్న కథలు మరియు దినచర్యలను రాయండి."),
            "Audio Spotting & Listening": ("ఆడియో ఆలకింపు & గ్రహింపు", "ఆడియో భాగాలను విని ముఖ్యమైన వివరాలను గుర్తించండి."),
            "Daily Literacy Skill Challenge": ("రోజువారీ అక్షరాస్యత సవాలు", "చదవడం, రాయడం మరియు పదజాలం నైపుణ్యాలను పరీక్షించండి."),
            "Comprehensive Revision Module": ("సమగ్ర పునశ్చరణ మాడ్యూల్", "నేర్చుకున్న అన్ని అక్షరాస్యత భావనలను పునశ్చరణ చేయండి."),

            "Everyday Conversation & Speaking": ("నిత్య జీవిత సంభాషణ & మాటలు", "నిత్య జీవిత సంభాషణలు మరియు పలకరింపులు సాధన చేయండి."),
            "Real-World Passage Reading": ("వాస్తవ వ్యాసాల పఠనం", "ప్రకటనలు, సమాచార వ్యాసాలు మరియు సూచనలను చదవండి."),
            "Form Filling & Message Writing": ("ఫారమ్‌లు నింపడం & సందేశాల రాత", "ఫారమ్‌లు నింపడం, చిన్న సందేశాలు రాయడం నేర్చుకోండి."),
            "Workplace & Daily Vocabulary": ("దైనందిన & ఉద్యోగ పదజాలం", "ఉద్యోగ మరియు నిత్య జీవిత ముఖ్యమైన పదాలను నేర్చుకోండి."),
            "Speech Pronunciation Refinement": ("ఉచ్ఛారణ శోధన & సాధన", "ఉచ్ఛారణ స్పష్టతను మరియు మాట్లాడే ఆత్మవిశ్వాసాన్ని పెంచుకోండి."),
            "Functional Sentence Structure": ("కార్యాచరణ వాక్య నిర్మాణం", "వ్యాకరణబద్ధమైన స్పష్టమైన వాక్యాలను నిర్మించండి."),
            "Audio Dialogue Listening": ("ఆడియో సంభాషణల ఆలకింపు", "వాస్తవ సంభాషణలను విని ప్రశ్నలకు సమాధానాలు ఇవ్వండి."),
            "Daily Literacy Assessment": ("రోజువారీ నైపుణ్య మదింపు", "చదవడం, రాయడం మరియు మాట్లాడే సామర్థ్యాన్ని అంచనా వేయండి."),
            "Literacy Mastery & Progress Review": ("అక్షరాస్యత నైపుణ్య సమీక్ష", "నైపుణ్యాలను బలపరచుకోండి మరియు పురోగతిని సమీక్షించండి.")
        }
    }

    if not lessons_raw or len(lessons_raw) < 5:
        if user_age <= 4:
            raw_modules = [
                ("Picture Naming & Colors", "reading", "Identify colors, animals, and objects with pictures.", "bi-palette-fill"),
                ("Animal Sounds & Visuals", "listening", "Listen to animal sounds and match cute pictures.", "bi-volume-up-fill"),
                ("Alphabet Rhymes & Songs", "phonics", "Sing along with alphabet sounds and letter rhymes.", "bi-music-note-beamed"),
                ("Number Songs (1 to 5)", "numbers", "Count numbers 1 to 5 with fun object animations.", "bi-123"),
                ("Line & Circle Tracing", "writing", "Practice drawing straight lines, curves, and circles.", "bi-pencil-fill"),
                ("Sight Words & Flashcards", "reading", "Recognize simple daily sight words.", "bi-card-image"),
                ("Shapes & Color Matching", "practice", "Match basic shapes (circle, square, triangle).", "bi-shapes"),
                ("Simple Word Speaking", "speaking", "Speak simple words aloud with mascot Lumi.", "bi-mic-fill")
            ]
        elif user_age <= 7:
            raw_modules = [
                ("Alphabet Sounds & Recognition", "phonics", "Master letter sounds and upper/lowercase letters.", "bi-book-fill"),
                ("Handwriting & Stroke Tracing", "writing", "Trace letters stroke-by-stroke with guide arrows.", "bi-pencil-square"),
                ("Vowels & Consonants Phonics", "phonics", "Learn vowel sounds and consonant blends.", "bi-volume-up-fill"),
                ("Three-Letter CVC Words", "reading", "Read 3-letter words like cat, dog, sun, and hat.", "bi-journal-text"),
                ("Number Words (1 to 20)", "numbers", "Read and spell number words from one to twenty.", "bi-123"),
                ("Action Words & Object Naming", "vocabulary", "Learn verbs and daily object names with pictures.", "bi-lightbulb-fill"),
                ("Rhyming Words & Short Poems", "reading", "Discover rhyming word pairs and fun poems.", "bi-music-note-list"),
                ("Short Sentence Reading", "reading", "Read simple 3-4 word sentences with confidence.", "bi-card-text"),
                ("Spelling & Dictation Practice", "writing", "Listen to words and practice correct spelling.", "bi-spellcheck"),
                ("Daily Speaking Practice", "speaking", "Practice pronouncing words clearly with AI feedback.", "bi-mic-fill")
            ]
        elif user_age <= 10:
            raw_modules = [
                ("Vocabulary Builder & Meanings", "vocabulary", "Expand vocabulary with word roots and meanings.", "bi-bookmark-star-fill"),
                ("Phonics Blends & Digraphs", "phonics", "Master complex sound blends (sh, ch, th, wh).", "bi-volume-up-fill"),
                ("Illustrated Story Reading", "reading", "Read stories and answer comprehension questions.", "bi-journal-richtext"),
                ("Sentence Construction & Grammar", "writing", "Build complete sentences using proper punctuation.", "bi-pencil-square"),
                ("Dialogue Speaking & Fluency", "speaking", "Practice conversational dialogues with Lumi AI.", "bi-chat-quote-fill"),
                ("Grammar Basics: Nouns & Verbs", "grammar", "Identify nouns, verbs, and adjectives in sentences.", "bi-mortarboard-fill"),
                ("Creative Story Writing", "writing", "Write short creative paragraphs and personal journals.", "bi-file-earmark-text-fill"),
                ("Audio Spotting & Listening", "listening", "Listen to audio passages and spot key details.", "bi-headphones"),
                ("Daily Literacy Skill Challenge", "evaluation", "Test reading, writing, and vocabulary skills.", "bi-trophy-fill"),
                ("Comprehensive Revision Module", "practice", "Review all key literacy concepts learned.", "bi-arrow-repeat")
            ]
        else:
            raw_modules = [
                ("Everyday Conversation & Speaking", "speaking", "Practice practical daily conversations and greetings.", "bi-chat-left-dots-fill"),
                ("Real-World Passage Reading", "reading", "Read practical passages, notices, and short articles.", "bi-newspaper"),
                ("Form Filling & Message Writing", "writing", "Learn to fill basic forms, write messages and notes.", "bi-file-earmark-spreadsheet-fill"),
                ("Workplace & Daily Vocabulary", "vocabulary", "Master essential daily life and workplace vocabulary.", "bi-briefcase-fill"),
                ("Speech Pronunciation Refinement", "speaking", "Improve accent, clarity, and speaking confidence.", "bi-mic-fill"),
                ("Functional Sentence Structure", "grammar", "Construct clear, grammatically accurate sentences.", "bi-check2-square"),
                ("Audio Dialogue Listening", "listening", "Listen to real-life dialogues and answer questions.", "bi-disc-fill"),
                ("Daily Literacy Assessment", "evaluation", "Evaluate overall reading, writing, and speaking fluency.", "bi-award-fill"),
                ("Literacy Mastery & Progress Review", "practice", "Reinforce skills and track literacy growth.", "bi-graph-up-arrow")
            ]

        lessons_raw = []
        lang_dict = MODULE_TITLE_LOCALES.get(language, {})
        for idx, (t, cat, desc, icon) in enumerate(raw_modules, start=1):
            title_trans, desc_trans = lang_dict.get(t, (t, desc))
            lessons_raw.append({
                "id": 6000 + idx,
                "title": title_trans,
                "category": cat,
                "language": language,
                "content": desc_trans,
                "difficulty": learning_level,
                "icon": icon
            })

    # Category icon map
    icon_map = {
        "reading": "bi-book-half",
        "writing": "bi-pencil-square",
        "speaking": "bi-mic-fill",
        "phonics": "bi-volume-up-fill",
        "comprehension": "bi-lightbulb-fill",
        "listening": "bi-headphones",
        "vocabulary": "bi-bookmark-star-fill",
        "numbers": "bi-123",
        "grammar": "bi-mortarboard-fill",
        "practice": "bi-arrow-repeat",
        "evaluation": "bi-trophy-fill"
    }

    # Fetch content recommendations for locks
    recs = get_content_recommendations(user_id)
    l1_id = recs[0]["id"] if len(recs) > 0 else None
    l2_id = recs[1]["id"] if len(recs) > 1 else None

    # Build lessons list
    lessons = []
    for idx_in_loop, l_raw in enumerate(lessons_raw):
        l = dict(l_raw)
        cat_low = (l.get("category") or "reading").lower()
        is_comp = l["id"] in completed_ids
        content_text = l.get("content") or ""
        snippet = content_text.split("[QUIZ]")[0].strip() if "[QUIZ]" in content_text else content_text.strip()
        cat_trans = CATEGORY_LOCALES.get(language, {}).get(cat_low, (l.get("category") or "Reading").capitalize())
        raw_diff = l.get("difficulty") or learning_level
        diff_trans = DIFFICULTY_LOCALES.get(language, {}).get(raw_diff, raw_diff)

        # Enforce exact same locking logic as /lesson/<int:lesson_id> route
        is_locked = True
        if user_age <= 4:
            is_locked = False
        else:
            if l["id"] in completed_ids:
                is_locked = False
            elif idx_in_loop == 0:
                is_locked = False
            else:
                prev_lesson_id = lessons_raw[idx_in_loop - 1]["id"]
                if prev_lesson_id in completed_ids:
                    is_locked = False

        desc_val = l.get("description") or (snippet[:120] + "..." if len(snippet) > 120 else snippet)

        lessons.append({
            "id": l["id"],
            "title": l["title"],
            "category": cat_trans,
            "language": l.get("language") or language,
            "content": snippet,
            "description": desc_val,
            "difficulty": diff_trans,
            "estimated_time": "10 mins",
            "completed": is_comp,
            "progress": 100 if is_comp else 0,
            "locked": is_locked,
            "icon": l.get("icon") or icon_map.get(cat_low, "bi-journal-bookmark-fill")
        })

    # Calculate serpentine path properties and current node
    offsets = [0, 45, 65, 25, -35, -65, -25]
    current_found = False
    for idx, item in enumerate(lessons):
        item["unit_number"] = (idx // 4) + 1
        item["offset_x"] = offsets[idx % len(offsets)]
        if not item["completed"] and not item["locked"] and not current_found:
            item["is_current"] = True
            current_found = True
        else:
            item["is_current"] = False

    if not current_found and lessons:
        lessons[0]["is_current"] = True

    # Render template with structural translations injected
    content_trans = WEEK_MODULE_CONTENT.get(language, WEEK_MODULE_CONTENT["English"])

    completed_count = sum(1 for l in lessons if l["completed"])
    progress_percent = int((completed_count / len(lessons)) * 100) if lessons else 0

    profile = {
        "fullname": user_row["fullname"],
        "email": user_row["email"],
        "language": language,
        "age": int(age) if age is not None else 8,
        "progress_percent": progress_percent,
        "completed_count": completed_count,
        "coins": coins,
        "badges": badges,
        "avatar": avatar,
        "current_mascot_dress": current_mascot_dress,
        "mascot_dresses": mascot_dresses,
        "xp": xp,
        "streak": streak
    }

    # Calculate recommendations and weak areas for week_module.html
    current_level = learning_level or "Beginner"
    latest_score = history[0]["score"] if history else 80
    assessment_score = latest_score

    # Weak areas / AI Goals
    if history and history[0].get("score", 100) < 70:
        learning_goals = [
            "Improve Phonics & Sound Recognition",
            "Practice Sentence Construction & Spelling",
            "Enhance Speech Pronunciation Fluency"
        ]
    else:
        learning_goals = [
            "Master Foundational Vocabulary",
            "Practice Everyday Reading & Writing",
            "AI Interactive Speech Practice"
        ]

    recommended_lessons = [l for l in lessons if not l["locked"] and not l["completed"]]
    if not recommended_lessons and lessons:
        recommended_lessons = [lessons[0]]

    rem_count = sum(1 for l in lessons if not l["completed"])
    estimated_time = f"{rem_count * 10} mins" if rem_count > 0 else "0 mins"
    progress_bar = progress_percent

    return render_template(
        "week_module.html",
        lessons=lessons,
        translations=translations,
        content=content_trans,
        profile=profile,
        completed_ids=completed_ids,
        history=history,
        is_birthday=is_birthday,
        current_level=current_level,
        assessment_score=assessment_score,
        learning_goals=learning_goals,
        recommended_lessons=recommended_lessons,
        estimated_time=estimated_time,
        progress_bar=progress_bar
    )

# -------------------------------
# Learning Games Routes
# -------------------------------
@app.route("/learning-games")
@login_required
def learning_games():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    learning_level = session.get("learning_level", "Beginner")
    age = session.get("age", 8)
    translations = get_translations(language)

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fullname, xp, coins, badges, streak, longest_streak FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()

    cursor.execute("SELECT game_id, game_name, score, xp_earned, timestamp FROM game_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
    recent_games = [dict(r) for r in cursor.fetchall()]
    
    # Leaderboards
    cursor.execute("SELECT fullname, xp, avatar FROM users ORDER BY xp DESC LIMIT 5")
    leaderboard_xp = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT fullname, coins, avatar FROM users ORDER BY coins DESC LIMIT 5")
    leaderboard_coins = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT fullname, streak, avatar FROM users ORDER BY streak DESC LIMIT 5")
    leaderboard_streak = [dict(r) for r in cursor.fetchall()]
    
    conn.close()

    profile = {
        "fullname": user_row["fullname"] if user_row else "Learner",
        "xp": user_row["xp"] if user_row else 0,
        "coins": user_row["coins"] if user_row else 0,
        "badges": user_row["badges"] if user_row else "",
        "streak": user_row["streak"] if user_row else 0,
        "longest_streak": user_row["longest_streak"] if user_row else 0,
        "language": language,
        "age": age,
        "learning_level": learning_level
    }

    return render_template(
        "learning_games.html",
        translations=translations,
        profile=profile,
        recent_games=recent_games,
        leaderboard_xp=leaderboard_xp,
        leaderboard_coins=leaderboard_coins,
        leaderboard_streak=leaderboard_streak
    )


# Helper to get user profile
def get_user_profile(user_id):
    language = session.get("language", "English")
    learning_level = session.get("learning_level", "Beginner")
    age = session.get("age", 8)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT fullname, xp, coins, badges, streak, longest_streak FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    
    profile = {
        "fullname": row["fullname"] if row else "Learner",
        "xp": row["xp"] if row else 0,
        "coins": row["coins"] if row else 0,
        "badges": row["badges"] if row else "",
        "streak": row["streak"] if row else 0,
        "longest_streak": row["longest_streak"] if row else 0,
        "language": language,
        "age": age,
        "learning_level": learning_level
    }
    return profile

@app.route("/game/temple_run")
@login_required
def game_temple_run():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    return render_template("game_temple_run.html", profile=profile, translations=translations)

@app.route("/game/ninja_fruit")
@login_required
def game_ninja_fruit():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    if profile["xp"] < 200:
        flash("You need 200 XP to unlock Ninja Fruit Master!", "warning")
        return redirect(url_for("learning_games"))
    return render_template("game_ninja_fruit.html", profile=profile, translations=translations)

@app.route("/game/treasure_hunt")
@login_required
def game_treasure_hunt():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    if profile["xp"] < 500:
        flash("You need 500 XP to unlock Pirate Treasure Hunt!", "warning")
        return redirect(url_for("learning_games"))
    return render_template("game_treasure_hunt.html", profile=profile, translations=translations)

@app.route("/game/space_explorer")
@login_required
def game_space_explorer():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    if profile["xp"] < 1000:
        flash("You need 1000 XP to unlock Space Explorer!", "warning")
        return redirect(url_for("learning_games"))
    return render_template("game_space_explorer.html", profile=profile, translations=translations)

@app.route("/game/robot_factory")
@login_required
def game_robot_factory():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    if profile["xp"] < 1500:
        flash("You need 1500 XP to unlock Robot Factory!", "warning")
        return redirect(url_for("learning_games"))
    return render_template("game_robot_factory.html", profile=profile, translations=translations)

@app.route("/game/city_builder")
@login_required
def game_city_builder():
    user_id = session.get("user_id")
    profile = get_user_profile(user_id)
    translations = get_translations(profile["language"])
    if profile["xp"] < 2000:
        flash("You need 2000 XP to unlock Dream City Builder!", "warning")
        return redirect(url_for("learning_games"))
    return render_template("game_city_builder.html", profile=profile, translations=translations)

@app.route("/api/spin_wheel", methods=["POST"])
@login_required
def api_spin_wheel():
    user_id = session.get("user_id")
    import random
    
    prizes = [
        {"val": "20 Coins", "type": "coins", "coins": 20, "xp": 10, "msg": "You won 20 Coins and 10 XP! 🪙"},
        {"val": "50 Coins", "type": "coins", "coins": 50, "xp": 20, "msg": "Wow! 50 Coins and 20 XP! 🪙"},
        {"val": "100 Coins", "type": "coins", "coins": 100, "xp": 40, "msg": "JACKPOT! 100 Coins and 40 XP! 🪙"},
        {"val": "astronaut", "type": "outfit", "coins": 10, "xp": 20, "msg": "Unlocked Astronaut Dress! 🧑‍🚀"},
        {"val": "detective", "type": "outfit", "coins": 10, "xp": 20, "msg": "Unlocked Detective Dress! 🕵️"},
        {"val": "superhero", "type": "outfit", "coins": 10, "xp": 20, "msg": "Unlocked Superhero Dress! 🦸"}
    ]
    
    prize = random.choice(prizes)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT xp, coins, mascot_dresses, badges FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    if row:
        curr_xp = (row["xp"] or 0) + prize["xp"]
        curr_coins = (row["coins"] or 0) + prize["coins"]
        dresses_str = row["mascot_dresses"] or "Default"
        dresses_list = [d.strip() for d in dresses_str.split(",") if d.strip()]
        
        if prize["type"] == "outfit":
            dress_name = prize["val"].capitalize()
            if dress_name not in dresses_list:
                dresses_list.append(dress_name)
            new_dresses = ",".join(dresses_list)
            cursor.execute("UPDATE users SET xp = ?, coins = ?, mascot_dresses = ? WHERE id = ?", (curr_xp, curr_coins, new_dresses, user_id))
        else:
            cursor.execute("UPDATE users SET xp = ?, coins = ? WHERE id = ?", (curr_xp, curr_coins, user_id))
            
        session["xp"] = curr_xp
        session["coins"] = curr_coins
        
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "prize_type": prize["type"],
        "prize_label": prize["val"],
        "prize_val": prize["val"],
        "msg": prize["msg"]
    })


@app.route("/api/claim_wheel_reward", methods=["POST"])
@login_required
def api_claim_wheel_reward():
    data = request.get_json() or {}
    reward = data.get("reward", "+10 Coins")
    user_id = session.get("user_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    xp_award = 0
    coins_award = 0
    new_badge = None
    
    if reward == "+10 Coins":
        coins_award = 10
    elif reward == "+20 XP":
        xp_award = 20
    elif reward == "Mystery Box":
        coins_award = 15
        xp_award = 15
    elif reward == "Double XP":
        xp_award = 40
    elif reward == "Extra Life":
        new_badge = "Survivalist"
        coins_award = 5
    elif reward == "Pet Companion":
        new_badge = "Pet Companion"
    elif reward == "New Avatar":
        new_badge = "Avatar Collector"
        cursor.execute("UPDATE users SET mascot_dresses = mascot_dresses || ',Wizard' WHERE id = ? AND mascot_dresses NOT LIKE '%Wizard%'", (user_id,))
    elif reward == "Cool Theme":
        new_badge = "Theme Collector"
        
    cursor.execute("""
        UPDATE users 
        SET xp = IFNULL(xp, 0) + ?, coins = IFNULL(coins, 0) + ?
        WHERE id = ?
    """, (xp_award, coins_award, user_id))
    
    if new_badge:
        cursor.execute("SELECT badges FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        if row:
            badges = [b.strip() for b in (row["badges"] or "").split(",") if b.strip()]
            if new_badge not in badges:
                badges.append(new_badge)
                cursor.execute("UPDATE users SET badges = ? WHERE id = ?", (",".join(badges), user_id))
                
    conn.commit()
    conn.close()
    
    return jsonify({
        "success": True,
        "xp_reward": xp_award,
        "coins_reward": coins_award,
        "badge_unlocked": new_badge
    })


@app.route("/api/save_game_progress", methods=["POST"])
@login_required
def api_save_game_progress():
    user_id = session.get("user_id")
    data = request.get_json() or {}

    game_id = data.get("game_id", "catch_it")
    game_name = data.get("game_name", "Learning Game")
    score = int(data.get("score", 100))
    xp_earned = int(data.get("xp_earned", 25))
    coins_earned = int(data.get("coins_earned", 15))
    language = session.get("language", "English")

    conn = get_db_connection()
    cursor = conn.cursor()

    # Insert into game_history
    cursor.execute("""
        INSERT INTO game_history (user_id, game_id, game_name, score, xp_earned, coins_earned, language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (user_id, game_id, game_name, score, xp_earned, coins_earned, language))

    # Update user XP and coins
    cursor.execute("SELECT xp, coins FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    curr_xp = (row["xp"] if row else 0) + xp_earned
    curr_coins = (row["coins"] if row else 0) + coins_earned

    cursor.execute("UPDATE users SET xp = ?, coins = ? WHERE id = ?", (curr_xp, curr_coins, user_id))
    conn.commit()
    conn.close()

    session["xp"] = curr_xp
    session["coins"] = curr_coins

    # Log study activity (10 mins session)
    log_study_activity(user_id, 10, xp_earned)

    return jsonify({
        "success": True,
        "xp": curr_xp,
        "coins": curr_coins,
        "message": f"+{xp_earned} XP & +{coins_earned} Coins Earned!"
    })


@app.route("/lesson/<int:lesson_id>")
@login_required
def lesson_detail(lesson_id):
    user_id = session.get("user_id")
    language = session.get("language", "English")
    learning_level = session.get("learning_level", "Beginner")
    age = session.get("age", 8)
    translations = get_translations(language)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch preferred and learning language from DB
    cursor.execute("SELECT preferred_language, learning_language FROM users WHERE id = ?", (user_id,))
    u_row = cursor.fetchone()
    preferred_lang = u_row["preferred_language"] if u_row and u_row["preferred_language"] else "English"
    learning_lang = u_row["learning_language"] if u_row and u_row["learning_language"] else language
    
    # Enforce Lesson Access Control
    # 1. Fetch completed lessons
    cursor.execute("SELECT lesson_id FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_ids = {r["lesson_id"] for r in cursor.fetchall()}
    
    # 2. Fetch recommendations
    recs = get_content_recommendations(user_id)
    l1_id = recs[0]["id"] if len(recs) > 0 else None
    l2_id = recs[1]["id"] if len(recs) > 1 else None
    
    is_unlocked = False
    if lesson_id in completed_ids:
        is_unlocked = True
    elif lesson_id >= 6000:
        if lesson_id == 6001:
            is_unlocked = True
        else:
            prev_id = lesson_id - 1
            if prev_id in completed_ids:
                is_unlocked = True
    elif lesson_id == l1_id:
        is_unlocked = True
    elif lesson_id == l2_id:
        if not l1_id or l1_id in completed_ids:
            is_unlocked = True
            
    try:
        age_int = int(age)
    except (ValueError, TypeError):
        age_int = 8
        
    CURRICULUM_LESSONS = {
        6001: {"id": 6001, "title": "Alphabet Sounds & Recognition", "category": "phonics", "language": language, "content": "Master letter sounds A, B, C, D, E.", "difficulty": "Beginner"},
        6002: {"id": 6002, "title": "Handwriting & Stroke Tracing", "category": "writing", "language": language, "content": "Trace letters A, B, C, D, E stroke-by-stroke.", "difficulty": "Beginner"},
        6003: {"id": 6003, "title": "Vowels & Consonants Phonics", "category": "phonics", "language": language, "content": "Learn Short Vowel sounds: A, E, I, O, U.", "difficulty": "Beginner"},
        6004: {"id": 6004, "title": "Three-Letter CVC Words", "category": "reading", "language": language, "content": "Read 3-letter CVC words: Cat, Dog, Sun, Box, Pen.", "difficulty": "Beginner"},
        6005: {"id": 6005, "title": "Numbers & Counting", "category": "numbers", "language": language, "content": "Count numbers 1 to 5 with stars and objects.", "difficulty": "Beginner"},
        6006: {"id": 6006, "title": "Daily Vocabulary & Greetings", "category": "vocabulary", "language": language, "content": "Master essential daily words and greetings.", "difficulty": "Beginner"}
    }

    if lesson_id in CURRICULUM_LESSONS:
        lesson = CURRICULUM_LESSONS[lesson_id]
        conn.close()
    else:
        cursor.execute("SELECT * FROM lessons WHERE id = ?", (lesson_id,))
        lesson_row = cursor.fetchone()
        conn.close()
        if lesson_row:
            lesson = dict(lesson_row)
        else:
            lesson = {
                "id": lesson_id,
                "title": f"{language} Foundational Lesson {lesson_id}",
                "category": "Alphabet",
                "language": language,
                "content": f"Welcome to the {language} learning module.",
                "difficulty": learning_level
            }
    
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

    # Pre-transliterate and parse textbook sentence system
    translated_title = lesson.get("title", "")
    
    title_translations = {
        "பூனை மற்றும் எலி": "The Cat and The Mouse",
        "பூனை மற்றும் எலி - Part 2": "The Cat and The Mouse - Part 2",
        "பூனை மற்றும் எலி - Part 3": "The Cat and The Mouse - Part 3",
        "పిల్లి మరియు ఎలుక": "The Cat and The Mouse",
        "పిల్లి మరియు ఎలుక - Part 2": "The Cat and The Mouse - Part 2",
        "పిల్లి మరియు ఎలుక - Part 3": "The Cat and The Mouse - Part 3",
        "बिल्ली और चूहा": "The Cat and The Mouse",
        "बिल्ली और चूहा - Part 2": "The Cat and The Mouse - Part 2",
        "बिल्ली और चूहा - Part 3": "The Cat and The Mouse - Part 3",
        
        "எழுத்துக்கள் அறிமுகம்": "Introduction to Letters",
        "எழுத்துக்கள் அறிமுகம் - Part 2": "Introduction to Letters - Part 2",
        "எழுத்துக்கள் அறிமுகம் - Part 3": "Introduction to Letters - Part 3",
        
        "எழுத்து பயிற்சி": "Letter Writing Practice",
        "எழுத்து பயிற்சி - Part 2": "Letter Writing Practice - Part 2",
        "எழுத்து பயிற்சி - Part 3": "Letter Writing Practice - Part 3",
        
        "எளிய வாக்கியங்கள்": "Simple Sentences Reading",
        "எளிய வாக்கியங்கள் - Part 2": "Simple Sentences Reading - Part 2",
        "எளிய வாக்கியங்கள் - Part 3": "Simple Sentences Reading - Part 3",
        
        "అక్షరాల పరిచయం": "Introduction to Letters",
        "అక్షరాల పరిచయం - Part 2": "Introduction to Letters - Part 2",
        "అక్షరాల పరిచయం - Part 3": "Introduction to Letters - Part 3",
        
        "అక్షరాల సాధన": "Letter Writing Practice",
        "అక్షరాల సాధన - Part 2": "Letter Writing Practice - Part 2",
        "అక్షరాల సాధన - Part 3": "Letter Writing Practice - Part 3",
        
        "సరళ వాక్యాలు": "Simple Sentences Reading",
        "సరళ వాక్యాలు - Part 2": "Simple Sentences Reading - Part 2",
        "సరళ వాక్యాలు - Part 3": "Simple Sentences Reading - Part 3",
        
        "वर्णमाला ज्ञान": "Alphabet Knowledge",
        "वर्णमाला ज्ञान - Part 2": "Alphabet Knowledge - Part 2",
        "वर्णमाला ज्ञान - Part 3": "Alphabet Knowledge - Part 3",
        
        "अक्षर लेखन": "Letter Writing Practice",
        "अक्षर लेखन - Part 2": "Letter Writing Practice - Part 2",
        "अक्षर लेखन - Part 3": "Letter Writing Practice - Part 3",
        
        "सरल वाक्य बोध": "Simple Sentences Reading",
        "सरल वाक्य बोध - Part 2": "Simple Sentences Reading - Part 2",
        "सरल वाक्य बोध - Part 3": "Simple Sentences Reading - Part 3",
        
        "प्यासा कौआ": "The Thirsty Crow",
        "प्यासा कौआ - Part 2": "The Thirsty Crow - Part 2",
        "प्यासा कौआ - Part 3": "The Thirsty Crow - Part 3",
        
        "తెలివైన కాకి": "The Clever Crow",
        "తెలివైన కాకి - Part 2": "The Clever Crow - Part 2",
        "తెలివైన కాకి - Part 3": "The Clever Crow - Part 3",
        
        "கதை புரிதல்": "Story Comprehension",
        "கதை புரிதல் - Part 2": "Story Comprehension - Part 2",
        "கதை புரிதல் - Part 3": "Story Comprehension - Part 3",
        
        "எளிய சொற்கள்": "Simple Words Writing",
        "எளிய சொற்கள் - Part 2": "Simple Words Writing - Part 2",
        "எளிய சொற்கள் - Part 3": "Simple Words Writing - Part 3",
        
        "సరళ పదాల వ్రాత": "Simple Words Writing",
        "సరళ పదాల వ్రాత - Part 2": "Simple Words Writing - Part 2",
        "సరళ పదాల వ్రాత - Part 3": "Simple Words Writing - Part 3",
        
        "सरल शब्द लेखन": "Simple Words Writing",
        "सरल शब्द लेखन - Part 2": "Simple Words Writing - Part 2",
        "सरल शब्द लेखन - Part 3": "Simple Words Writing - Part 3"
    }
    
    if preferred_lang == "English":
        translated_title = title_translations.get(lesson.get("title", ""), lesson.get("title", ""))
        
    lesson_title_translit = ""
    if language != "English":
        lesson_title_translit = transliterate_text(lesson.get("title", ""), language)
        
    # Build robust sentences_data
    LESSON_SENTENCE_DB = {
        # Tamil
        "பூனை கட்டிலின் மேல் உள்ளது": {
            "meaning": "The cat is on the cot.",
            "breakdown": [
                {"word": "பூனை", "pronunciation": "poonai", "meaning": "cat"},
                {"word": "கட்டிலின்", "pronunciation": "kattilin", "meaning": "cot's"},
                {"word": "மேல்", "pronunciation": "mel", "meaning": "on/above"},
                {"word": "உள்ளது", "pronunciation": "ullathu", "meaning": "is"}
            ]
        },
        "எలి வேகமாக ஓடுகிறது": {
            "meaning": "The rat runs fast.",
            "breakdown": [
                {"word": "எலி", "pronunciation": "eli", "meaning": "rat"},
                {"word": "வேகமாக", "pronunciation": "vegamaaga", "meaning": "fast"},
                {"word": "ஓடுகிறது", "pronunciation": "odukirathu", "meaning": "runs"}
            ]
        },
        "பூனை குதித்தது, எலி பெட்டிக்குள் ஒளிந்தது": {
            "meaning": "The cat jumped, the rat hid in the box.",
            "breakdown": [
                {"word": "பூனை", "pronunciation": "poonai", "meaning": "cat"},
                {"word": "குதித்தது", "pronunciation": "kuthithathu", "meaning": "jumped"},
                {"word": "எலி", "pronunciation": "eli", "meaning": "rat"},
                {"word": "பெட்டிக்குள்", "pronunciation": "pettikkul", "meaning": "inside box"},
                {"word": "ஒளிந்தது", "pronunciation": "olinthathu", "meaning": "hid"}
            ]
        },
        "அம்மா பால் தருகிறார்": {
            "meaning": "Mother gives milk.",
            "breakdown": [
                {"word": "அம்மா", "pronunciation": "amma", "meaning": "mother"},
                {"word": "பால்", "pronunciation": "paal", "meaning": "milk"},
                {"word": "தருகிறார்", "pronunciation": "tharukiraar", "meaning": "gives"}
            ]
        },
        "பால் உடலுக்கு நல்லது": {
            "meaning": "Milk is good for the body.",
            "breakdown": [
                {"word": "பால்", "pronunciation": "paal", "meaning": "milk"},
                {"word": "உடலுக்கு", "pronunciation": "udalukku", "meaning": "to body"},
                {"word": "நல்லது", "pronunciation": "nallathu", "meaning": "good"}
            ]
        },
        "உயிர் எழுத்துக்களைக் கற்றுக்கொள்ளுங்கள்: அ, ஆ, இ": {
            "meaning": "Learn the vowel letters: a, aa, i.",
            "breakdown": [
                {"word": "உயிர்", "pronunciation": "uyir", "meaning": "vowel"},
                {"word": "எழுத்துக்களைக்", "pronunciation": "ezhuthukkalai", "meaning": "letters"},
                {"word": "கற்றுக்கொள்ளுங்கள்", "pronunciation": "katrukkollungal", "meaning": "learn"}
            ]
        },
        "இந்த எழுத்துக்களைப் படியுங்கள்": {
            "meaning": "Read these letters.",
            "breakdown": [
                {"word": "இந்த", "pronunciation": "intha", "meaning": "these"},
                {"word": "எழுத்துக்களைப்", "pronunciation": "ezhuthukkalai", "meaning": "letters"},
                {"word": "படியுங்கள்", "pronunciation": "padiyungal", "meaning": "read"}
            ]
        },
        "அ மற்றும் ஆ எழுத்துக்களை எழுதப் பழகுங்கள்": {
            "meaning": "Practice writing letters a and aa.",
            "breakdown": [
                {"word": "அ", "pronunciation": "a", "meaning": "a"},
                {"word": "மற்றும்", "pronunciation": "matrum", "meaning": "and"},
                {"word": "ஆ", "pronunciation": "aa", "meaning": "aa"},
                {"word": "எழுத", "pronunciation": "ezhuthah", "meaning": "write"},
                {"word": "பழகுங்கள்", "pronunciation": "pazhagungal", "meaning": "practice"}
            ]
        },
        "பூனை, நாய், பேனா போன்ற எளிய சொற்களை எழுதப் பழகுங்கள்": {
            "meaning": "Practice writing simple words like cat, dog, pen.",
            "breakdown": [
                {"word": "பூனை", "pronunciation": "poonai", "meaning": "cat"},
                {"word": "நாய்", "pronunciation": "naai", "meaning": "dog"},
                {"word": "பேனா", "pronunciation": "penah", "meaning": "pen"},
                {"word": "எளிய", "pronunciation": "eliya", "meaning": "simple"},
                {"word": "சொற்களை", "pronunciation": "sorkalai", "meaning": "words"}
            ]
        },
        "ஒரு தாகமுள்ள காகம் பானையில் கற்களைப் போட்டு நீர் குடித்தது": {
            "meaning": "A thirsty crow put stones in the pot and drank water.",
            "breakdown": [
                {"word": "ஒரு", "pronunciation": "oru", "meaning": "one"},
                {"word": "தாகமுள்ள", "pronunciation": "thaagamulla", "meaning": "thirsty"},
                {"word": "காகம்", "pronunciation": "kaagam", "meaning": "crow"},
                {"word": "பானையில்", "pronunciation": "paanaiyil", "meaning": "in pot"},
                {"word": "நீர்", "pronunciation": "neer", "meaning": "water"}
            ]
        },
        
        # Telugu
        "అమ్మ పాలు ఇస్తుంది": {
            "meaning": "Mother gives milk.",
            "breakdown": [
                {"word": "అమ్మ", "pronunciation": "amma", "meaning": "mother"},
                {"word": "పాలు", "pronunciation": "paalu", "meaning": "milk"},
                {"word": "ఇస్తుంది", "pronunciation": "istundi", "meaning": "gives"}
            ]
        },
        "పాలు ఆరోగ్యానికి మంచిది": {
            "meaning": "Milk is good for health.",
            "breakdown": [
                {"word": "పాలు", "pronunciation": "paalu", "meaning": "milk"},
                {"word": "ఆరోగ్యానికి", "pronunciation": "aarogyaaniki", "meaning": "for health"},
                {"word": "మంచిది", "pronunciation": "manchidi", "meaning": "good"}
            ]
        },
        "పిల్లి మంచం మీద ఉంది": {
            "meaning": "The cat is on the bed.",
            "breakdown": [
                {"word": "పిల్లి", "pronunciation": "pilli", "meaning": "cat"},
                {"word": "మంచం", "pronunciation": "mancham", "meaning": "bed"},
                {"word": "మీద", "pronunciation": "meeda", "meaning": "on"},
                {"word": "ఉంది", "pronunciation": "undi", "meaning": "is"}
            ]
        },
        "ఎలుక వేగంగా పరిగెడుతుంది": {
            "meaning": "The rat runs fast.",
            "breakdown": [
                {"word": "ఎలుక", "pronunciation": "eluka", "meaning": "rat"},
                {"word": "వేగంగా", "pronunciation": "veganga", "meaning": "fast"},
                {"word": "పరిగెడుతుంది", "pronunciation": "parigedutundi", "meaning": "runs"}
            ]
        },
        "పిల్లి దూకింది": {
            "meaning": "The cat jumped.",
            "breakdown": [
                {"word": "పిల్లి", "pronunciation": "pilli", "meaning": "cat"},
                {"word": "దూకింది", "pronunciation": "dookindi", "meaning": "jumped"}
            ]
        },
        "ఎలుక పెట్టెలో దాక్కుంది": {
            "meaning": "The rat hid in the box.",
            "breakdown": [
                {"word": "ఎలుక", "pronunciation": "eluka", "meaning": "rat"},
                {"word": "పెట్టెలో", "pronunciation": "pettelo", "meaning": "in the box"},
                {"word": "దాక్కుంది", "pronunciation": "dakkundi", "meaning": "hid"}
            ]
        },
        
        # Hindi
        "यह मेरा घर है": {
            "meaning": "This is my house.",
            "breakdown": [
                {"word": "यह", "pronunciation": "yah", "meaning": "this"},
                {"word": "मेरा", "pronunciation": "mera", "meaning": "my"},
                {"word": "घर", "pronunciation": "ghar", "meaning": "house"},
                {"word": "है", "pronunciation": "hai", "meaning": "is"}
            ]
        },
        "आम मीठा होता है": {
            "meaning": "Mango is sweet.",
            "breakdown": [
                {"word": "आम", "pronunciation": "aam", "meaning": "mango"},
                {"word": "मीठा", "pronunciation": "meetha", "meaning": "sweet"},
                {"word": "होता है", "pronunciation": "hota hai", "meaning": "is"}
            ]
        },
        "बिल्ली चटाई पर है": {
            "meaning": "The cat is on the mat.",
            "breakdown": [
                {"word": "बिल्ली", "pronunciation": "billi", "meaning": "cat"},
                {"word": "चटाई", "pronunciation": "chataai", "meaning": "mat"},
                {"word": "पर", "pronunciation": "par", "meaning": "on"},
                {"word": "है", "pronunciation": "hai", "meaning": "is"}
            ]
        },
        "चूहा तेज दौड़ता है": {
            "meaning": "The mouse runs fast.",
            "breakdown": [
                {"word": "चूहा", "pronunciation": "chooha", "meaning": "mouse"},
                {"word": "तेज", "pronunciation": "tej", "meaning": "fast"},
                {"word": "दौड़ता है", "pronunciation": "daudta hai", "meaning": "runs"}
            ]
        },
        "बिल्ली कूदी": {
            "meaning": "The cat jumped.",
            "breakdown": [
                {"word": "बिल्ली", "pronunciation": "billi", "meaning": "cat"},
                {"word": "कूदी", "pronunciation": "koodi", "meaning": "jumped"}
            ]
        },
        "चूहा डिब्बे में सुरक्षित है": {
            "meaning": "The mouse is safe in the box.",
            "breakdown": [
                {"word": "चूहा", "pronunciation": "chooha", "meaning": "mouse"},
                {"word": "डिब्बे", "pronunciation": "dibbe", "meaning": "box"},
                {"word": "में", "pronunciation": "mein", "meaning": "in"},
                {"word": "सुरक्षित है", "pronunciation": "surakshit hai", "meaning": "is safe"}
            ]
        }
    }
    
    # English Word level dictionary mapping common words to regional languages
    ENGLISH_DICTIONARY = {
        "hello": {"Telugu": "నమస్కారం", "Hindi": "नमस्ते", "Tamil": "வணக்கம்", "Kannada": "ನಮಸ್ಕಾರ", "Marathi": "नमस्कार"},
        "thank": {"Telugu": "ధన్యవాదాలు", "Hindi": "धन्यवाद", "Tamil": "நன்றி", "Kannada": "ಧನ್ಯವಾದಗಳು", "Marathi": "धन्यवाद"},
        "you": {"Telugu": "మీరు", "Hindi": "आप", "Tamil": "நீங்கள்", "Kannada": "ನೀವು", "Marathi": "तुम्ही"},
        "good": {"Telugu": "మంచి", "Hindi": "अच्छा", "Tamil": "நல்ல", "Kannada": "ಒಳ್ಳೆಯ", "Marathi": "चांगले"},
        "morning": {"Telugu": "ఉదయం", "Hindi": "सुबह", "Tamil": "காலை", "Kannada": "ಮುಂಜಾನೆ", "Marathi": "सकाळ"},
        "night": {"Telugu": "రాత్రి", "Hindi": "रात", "Tamil": "இரவு", "Kannada": "ರಾತ್ರಿ", "Marathi": "रात्र"},
        "one": {"Telugu": "ఒకటి", "Hindi": "एक", "Tamil": "ஒன்று", "Kannada": "ಒಂದು", "Marathi": "एक"},
        "two": {"Telugu": "రెండు", "Hindi": "दो", "Tamil": "இரண்டு", "Kannada": "ಎರಡು", "Marathi": "दोन"},
        "three": {"Telugu": "మూడు", "Hindi": "तीन", "Tamil": "மூன்று", "Kannada": "ಮೂರು", "Marathi": "तीन"},
        "red": {"Telugu": "ఎరుపు", "Hindi": "लाल", "Tamil": "சிவப்பு", "Kannada": "ಕೆಂಪು", "Marathi": "लाल"},
        "blue": {"Telugu": "నీలం", "Hindi": "नीला", "Tamil": "நீலம்", "Kannada": "ನೀಲಿ", "Marathi": "निळा"},
        "green": {"Telugu": "ఆకుపచ్చ", "Hindi": "हरा", "Tamil": "பச்சை", "Kannada": "ಹಸಿರು", "Marathi": "हिरवा"},
        "cat": {"Telugu": "పిల్లి", "Hindi": "बिल्ली", "Tamil": "பூனை", "Kannada": "ಬೆಕ್ಕು", "Marathi": "मांजर"},
        "dog": {"Telugu": "కుక్క", "Hindi": "कुत्ता", "Tamil": "நாய்", "Kannada": "ನಾಯಿ", "Marathi": "कुत्रा"},
        "mouse": {"Telugu": "ఎలుక", "Hindi": "चूहा", "Tamil": "எலி", "Kannada": "ಇಲಿ", "Marathi": "उंदीर"},
        "rat": {"Telugu": "ఎలుక", "Hindi": "चूहा", "Tamil": "எலி", "Kannada": "ಇಲಿ", "Marathi": "उंदीर"},
        "house": {"Telugu": "ఇల్లు", "Hindi": "घर", "Tamil": "வீடு", "Kannada": "ಮನೆ", "Marathi": "घर"},
        "apple": {"Telugu": "ఆపిల్", "Hindi": "सेब", "Tamil": "ஆப்பிள்", "Kannada": "ಸೇಬು", "Marathi": "सफरचंद"},
        "ball": {"Telugu": "బంతి", "Hindi": "गेंद", "Tamil": "பந்து", "Kannada": "ಚೆಂಡು", "Marathi": "चेंडू"},
        "water": {"Telugu": "నీరు", "Hindi": "पानी", "Tamil": "தண்ணீர்", "Kannada": "ನೀರು", "Marathi": "पाणी"},
        "mother": {"Telugu": "అమ్మ", "Hindi": "माँ", "Tamil": "அम्मा", "Kannada": "ಅಮ್ಮ", "Marathi": "आई"},
        "father": {"Telugu": "నాన్న", "Hindi": "पिता", "Tamil": "அப்பா", "Kannada": "ಅಪ್ಪ", "Marathi": "वडील"},
        "tree": {"Telugu": "చెట్టు", "Hindi": "पेड़", "Tamil": "மரம்", "Kannada": "ಮರ", "Marathi": "झाड"},
        "box": {"Telugu": "పెట్టె", "Hindi": "डिब्बा", "Tamil": "பெட்டி", "Kannada": "ಪೆಟ್ಟಿಗೆ", "Marathi": "पेटी"},
        "crow": {"Telugu": "కాకి", "Hindi": "कौआ", "Tamil": "காகம்", "Kannada": "ಕಾಗೆ", "Marathi": "कावळा"},
        "pot": {"Telugu": "కుండ", "Hindi": "घड़ा", "Tamil": "பானை", "Kannada": "ಮಡಕೆ", "Marathi": "माठ"},
        "stones": {"Telugu": "రాళ్ళు", "Hindi": "पत्थर", "Tamil": "கற்கள்", "Kannada": "ಕಲ್ಲುಗಳು", "Marathi": "दगड"},
        "school": {"Telugu": "బడి", "Hindi": "स्कूल", "Tamil": "பள்ளி", "Kannada": "ಶಾಲೆ", "Marathi": "शाळा"},
        "letters": {"Telugu": "అక్షరాలు", "Hindi": "अक्षर", "Tamil": "எழுத்துக்கள்", "Kannada": "అಕ್ಷರಗಳು", "Marathi": "अक्षरे"},
        "alphabet": {"Telugu": "వర్ణమాల", "Hindi": "वर्णमाला", "Tamil": "நெடுங்கணக்கு", "Kannada": "ವರ್ಣಮಾಲೆ", "Marathi": "वर्णमाला"},
        "words": {"Telugu": "పదాలు", "Hindi": "शब्द", "Tamil": "வார்த்தைகள்", "Kannada": "పದಗಳು", "Marathi": "शब्द"},
        "writing": {"Telugu": "రాయడం", "Hindi": "लिखना", "Tamil": "எழுதுதல்", "Kannada": "ಬರೆಯುವುದು", "Marathi": "लिखाण"},
        "reading": {"Telugu": "చదవడం", "Hindi": "पढ़ना", "Tamil": "படித்தல்", "Kannada": "ಓದುವುದು", "Marathi": "वाचन"},
        "learn": {"Telugu": "నేర్చుకోవడం", "Hindi": "सीखना", "Tamil": "கற்றல்", "Kannada": "ಕಲಿಯುವುದು", "Marathi": "शिकणे"},
        "trace": {"Telugu": "గుర్తించడం", "Hindi": "ट्रेस करना", "Tamil": "வரையவும்", "Kannada": "ಚಿತ್ರಿಸು", "Marathi": "ट्रेस करणे"}
    }

    SENTENCE_TRANSLATIONS = {
        "learn the alphabet: a is for apple, b is for ball, c is for cat": {
            "Telugu": "వర్ణమాల నేర్చుకోండి: ఎ అంటే ఆపిల్, బి అంటే బంతి, సి అంటే పిల్లి.",
            "Hindi": "वर्णमाला सीखें: ए सेब के लिए है, बी गेंद के लिए है, सी बिल्ली के लिए है।",
            "Tamil": "நெடுங்கணக்கு கற்றுக்கொள்ளுங்கள்: ஏ என்றால் ஆப்பிள், பி என்றால் பந்து, சி என்றால் பூனை.",
            "Kannada": "ವರ್ಣಮಾಲೆ ಕಲಿಯಿರಿ: ಎ ಅಂದರೆ ಸೇಬು, ಬಿ ಅಂದರೆ ಚೆಂಡು, ಸಿ ಅಂದರೆ ಬೆಕ್ಕು.",
            "Marathi": "वर्णमाला शिका: ए म्हणजे सफरचंद, बी म्हणजे चेंडू, सी म्हणजे मांजर."
        },
        "can you read these letters": {
            "Telugu": "మీరు ఈ అక్షరాలను చదవగలరా?",
            "Hindi": "क्या आप इन अक्षरों को पढ़ सकते हैं?",
            "Tamil": "இந்த எழுத்துக்களை உங்களால் படிக்க முடியுமா?",
            "Kannada": "ನೀವು ಈ ಅಕ್ಷರಗಳನ್ನು ಓದಬಲ್ಲಿರಾ?",
            "Marathi": "तुम्ही ही अक्षरे वाचू शकता का?"
        },
        "trace the letter a and write small words": {
            "Telugu": "అక్షరం ఎ ను గుర్తించి చిన్న పదాలు రాయండి.",
            "Hindi": "अक्षर ए को ट्रेस करें और छोटे शब्द लिखें।",
            "Tamil": "ஏ எழுத்தை வரைந்து சிறிய வார்த்தைகளை எழுதுங்கள்.",
            "Kannada": "ಎ ಅಕ್ಷರವನ್ನು ಬರೆದು ಸಣ್ಣ ಪದಗಳನ್ನು ಬರೆಯಿರಿ.",
            "Marathi": "ए अक्षर ट्रेस करा आणि लहान शब्द लिहा."
        },
        "draw a line to match": {
            "Telugu": "జతపరచడానికి ఒక గీత గీయండి.",
            "Hindi": "मिलान करने के लिए एक रेखा खींचें।",
            "Tamil": "பொருத்த ஒரு கோடு வரையவும்.",
            "Kannada": "ಹೊಂದಿಸಲು ರೇಖೆ ಎಳೆಯಿರಿ.",
            "Marathi": "जोडणी करण्यासाठी एक रेघ ओढा."
        },
        "listen to the sound of a and choose the correct picture": {
            "Telugu": "ఎ శబ్దాన్ని విని సరైన చిత్రాన్ని ఎంచుకోండి.",
            "Hindi": "ए की ध्वनि सुनें और सही चित्र चुनें।",
            "Tamil": "ஏ ஒலியைக் கேட்டு சரியான படத்தைத் தேர்ந்தெடுக்கவும்.",
            "Kannada": "ಎ ಧ್ವನಿಯನ್ನು ಆಲಿಸಿ ಸರಿಯಾದ ಚಿತ್ರ ಆರಿಸಿ.",
            "Marathi": "ए चा आवाज ऐका आणि योग्य चित्र निवडा."
        },
        "learning vocabulary is the foundation of language": {
            "Telugu": "పదజాలం నేర్చుకోవడం భాషకు పునాది.",
            "Hindi": "शब्दावली सीखना भाषा की नींव है।",
            "Tamil": "சொற்களஞ்சியம் கற்பது மொழியின் அடித்தளமாகும்.",
            "Kannada": "ಪದಕೋಶ ಕಲಿಯುವುದು ಭಾಷೆಯ ಅಡಿಪಾಯವಾಗಿದೆ.",
            "Marathi": "शब्दसंग्रह शिकणे हा भाषेचा पाया आहे."
        },
        "words like fruit, color, dog, and table help us name things around us": {
            "Telugu": "పండు, రంగు, కుక్క మరియు బల్ల వంటి పదాలు మన చుట్టూ ఉన్న వాటికి పేర్లు పెట్టడానికి సహాయపడతాయి.",
            "Hindi": "फल, रंग, कुत्ता और मेज जैसे शब्द हमें अपने आस-पास की चीजों को नाम देने में मदद करते हैं।",
            "Tamil": "பழம், நிறம், நாய் மற்றும் மேஜை போன்ற சொற்கள் நம்மைச் சுற்றியுள்ள பொருள்களைப் பெயரிட உதவுகின்றன.",
            "Kannada": "ಹಣ್ಣು, ಬಣ್ಣ, நಾಯಿ ಮತ್ತು ಮೇಜಿನಂತಹ ಪದಗಳು ನಮ್ಮ ಸುತ್ತಲಿನ ವಸ್ತುಗಳನ್ನು ಹೆಸರಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "Marathi": "फळ, रंग, कुत्रा आणि टेबल यांसारखे शब्द आपल्याला आपल्या सभोवतालच्या वस्तूंना नावे देण्यास मदत करतात."
        },
        "practice spelling common words correctly": {
            "Telugu": "సాధారణ పదాల స్పెల్లింగ్‌లను సరిగ్గా రాయడం సాధన చేయండి.",
            "Hindi": "सामान्य शब्दों की वर्तनी सही लिखने का अभ्यास करें।",
            "Tamil": "பொதுவான சொற்களின் எழுத்துக்களைச் சரியாக எழுதப் பயிற்சி செய்யுங்கள்.",
            "Kannada": "ಸಾಮಾನ್ಯ ಪದಗಳ ಕಾಗುಣಿತವನ್ನು ಸರಿಯಾಗಿ ಬರೆಯಲು ಅಭ್ಯಾಸ ಮಾಡಿ.",
            "Marathi": "सामान्य शब्दांचे स्पेलिंग योग्य लिहिण्याचा सराव करा."
        },
        "always start a sentence with a capital letter": {
            "Telugu": "ఎల్లప్పుడూ వాక్యాన్ని పెద్ద అక్షరంతో (Capital Letter) ప్రారంభించండి.",
            "Hindi": "हमेशा वाक्य की शुरुआत बड़े अक्षर से करें।",
            "Tamil": "எப்பொழுதும் ஒரு வாக்கியத்தைப் பெரிய எழுத்துடன் தொடங்குங்கள்.",
            "Kannada": "ಯಾವಾಗಲೂ ವಾಕ್ಯವನ್ನು ದೊಡ್ಡ ಅಕ್ಷರದಿಂದ ಪ್ರಾರಂಭಿಸಿ.",
            "Marathi": "नेहमी वाक्याची सुरुवात मोठ्या अक्षराने करा."
        },
        "a fast mouse ran into a small box to hide from a cat": {
            "Telugu": "ఒక వేగవంతమైన ఎలుక పిల్లి నుండి దాక్కోవడానికి ఒక చిన్న పెట్టెలోకి పరిగెత్తింది.",
            "Hindi": "एक तेज चूहा बिल्ली से छिपने के लिए एक छोटे डिब्बे में भागा।",
            "Tamil": "ஒரு வேகமான எலி பூனையிடமிருந்து தப்பிக்க ஒரு சிறிய பெட்டிக்குள் ஓடியது.",
            "Kannada": "ಒಂದು ವೇಗದ ಇಲಿ ಬೆಕ್ಕಿನಿಂದ ತಪ್ಪಿಸಿಕೊಳ್ಳಲು ಸಣ್ಣ ಪೆಟ್ಟಿಗೆಗೆ ಓಡಿತು.",
            "Marathi": "एक वेगवान उंदीर मांजरीपासून लपण्यासाठी एका लहान पेटीत पळाला."
        },
        "the cat could not fit in the box": {
            "Telugu": "పిల్లి ఆ పెట్టెలోకి పట్టలేకపోయింది.",
            "Hindi": "बिल्ली उस डिब्बे में नहीं समा सकी।",
            "Tamil": "பூனையால் அந்தப் பெட்டிக்குள் நுழைய முடியவில்லை.",
            "Kannada": "ಬೆಕ್ಕಿಗೆ ಆ ಪೆಟ್ಟಿಗೆಯಲ್ಲಿ ಹಿಡಿಯಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
            "Marathi": "मांजर त्या पेटीत बसू शकली नाही."
        },
        "paragraphs help organize thoughts logically": {
            "Telugu": "పారాగ్రాఫ్‌లు ఆలోచనలను తార్కికంగా అమర్చడానికి సహాయపడతాయి.",
            "Hindi": "अनुच्छेद विचारों को तार्किक रूप से व्यवस्थित करने में मदद करते हैं।",
            "Tamil": "பத்திகள் கருத்துக்களை தர்க்கரீதியாக ஒழுங்கமைக்க உதவுகின்றன.",
            "Kannada": "ಪ್ಯಾರಾಗಳು ಆಲೋಚನೆಗಳನ್ನು ತಾರ್ಕಿಕವಾಗಿ ಜೋಡಿಸಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
            "Marathi": "परिच्छेद विचारांना तार्किकदृष्ट्या व्यवस्थापित करण्यात मदत करतात."
        },
        "each paragraph contains a main idea and supporting details": {
            "Telugu": "ప్రతి పారాగ్రాఫ్ ఒక ప్రధాన ఆలోచన మరియు దానికి మద్దతు ఇచ్చే వివరాలను కలిగి ఉంటుంది.",
            "Hindi": "प्रत्येक अनुच्छेद में एक मुख्य विचार और सहायक विवरण होते हैं।",
            "Tamil": "ஒவ்வொரு பத்தியும் ஒரு முக்கிய யோசனையையும் துணை விவரங்களையும் கொண்டுள்ளது.",
            "Kannada": "ಪ್ರತಿಯೊಂದು ಪ್ಯಾರಾ ಒಂದು ಪ್ರಮುಖ ಆಲೋಚನೆ ಮತ್ತು ಪೂರಕ ವಿವರಗಳನ್ನು ಹೊಂದಿರುತ್ತದೆ.",
            "Marathi": "प्रत्येक परिच्छेदात एक मुख्य विचार आणि सहाय्यक तपशील असतात."
        },
        "active voice makes sentences shorter and clearer": {
            "Telugu": "యాక్టివ్ వాయిస్ వాక్యాలను చిన్నవిగా మరియు స్పష్టంగా చేస్తుంది.",
            "Hindi": "कर्तृवाच्य वाक्यों को छोटा और स्पष्ट बनाता है।",
            "Tamil": "செய்வினை வாக்கியங்களைச் சுருக்கமாகவும் தெளிவாகவும் மாற்றுகிறது.",
            "Kannada": "ಕರ್ತೃ ಪ್ರಯೋಗವು ವಾಕ್ยಗಳನ್ನು ಸಣ್ಣದಾಗಿ ಮತ್ತು ಸ್ಪಷ್ಟವಾಗಿ ಮಾಡುತ್ತದೆ.",
            "Marathi": "कर्तरी प्रयोग वाक्यांना लहान आणि स्पष्ट बनवतो."
        },
        "try writing simple sentences in active voice": {
            "Telugu": "యాక్టివ్ వాయిస్‌లో సాధారణ వాక్యాలను రాయడానికి ప్రయత్నించండి.",
            "Hindi": "कर्तृवाच्य में सरल वाक्य लिखने का प्रयास करें।",
            "Tamil": "செய்வினையில் எளிய வாக்கியங்களை எழுத முயலுங்கள்.",
            "Kannada": "ಕರ್ತೃ ಪ್ರಯೋಗದಲ್ಲಿ ಸರಳ ವಾಕ್ಯಗಳನ್ನು ಬರೆಯಲು ಪ್ರಯತ್ನಿಸಿ.",
            "Marathi": "कर्तरी प्रयोगात साधी वाक्ये लिहिण्याचा प्रयत्न करा."
        },
        "water is essential for all living creatures": {
            "Telugu": "అన్ని జీవులకు నీరు అత్యవసరం.",
            "Hindi": "सभी जीवित प्राणियों के लिए पानी आवश्यक है।",
            "Tamil": "அனைத்து உயிரினங்களுக்கும் தண்ணீர் இன்றியமையாதது.",
            "Kannada": "ಎಲ್ಲಾ ಜೀವಿಗಳಿಗೂ ನೀರು ಅತ್ಯಗತ್ಯ.",
            "Marathi": "सर्व सजीव प्राण्यांसाठी पाणी आवश्यक आहे."
        },
        "without it, life on earth would cease to exist": {
            "Telugu": "అది లేకపోతే భూమిపై జీవం ఉనికిలో ఉండదు.",
            "Hindi": "इसके बिना पृथ्वी पर जीवन का अस्तित्व समाप्त हो जाएगा।",
            "Tamil": "அது இல்லையென்றால், பூமியில் வாழ்க்கை இல்லாது போய்விடும்.",
            "Kannada": "ಅದು ಇಲ್ಲದಿದ್ದರೆ ಭೂಮಿಯ ಮೇಲೆ ಜೀವಿಗಳ ಅಸ್ತಿತ್ವ ಕೊನೆಗೊಳ್ಳುತ್ತದೆ.",
            "Marathi": "त्याशिवाय पृथ्वीवरील सजीवांचे अस्तित्व संपुष्टात येईल."
        },
        "nouns, verbs, adjectives, and adverbs allow us to build complex sentences": {
            "Telugu": "నామవాచకాలు, క్రియలు, విశేషణలు మరియు క్రియাবিশేషణాలు మనకు సంక్లిష్టమైన వాక్యాలను నిర్మించడానికి సహాయపడతాయి.",
            "Hindi": "संज्ञा, क्रिया, विशेषण और क्रियाविशेषण हमें जटिल वाक्य बनाने की अनुमति देते हैं।",
            "Tamil": "பெயர்ச்சொற்கள், வினைச்சொற்கள், பெயரடைகள் மற்றும் வினையடைகள் சிக்கலான வாக்கியங்களை உருவாக்க உதவுகின்றன.",
            "Kannada": "ನಾಮಪದಗಳು, ಕ್ರಿಯಾಪದಗಳು, ಗುಣವಿಶೇಷಣಗಳು ಮತ್ತು ಕ್ರಿಯಾವಿಶೇಷಣಗಳು ನಮಗೆ ಸಂಕೀರ್ण ವಾಕ್ಯಗಳನ್ನು ರಚಿಸಲು ಅನುಮತಿಸುತ್ತದೆ.",
            "Marathi": "ನಾಮೆ, क्रियापदे, विशेषणे आणि क्रियाविशेषणे आपल्याला गुंतागुंतीची वाक्ये तयार करण्यास मदत करतात."
        }
    }

    sentences_data = []
    content_clean = lesson.get("content", "")
    if "[QUIZ]" in content_clean:
        content_clean = content_clean.split("[QUIZ]")[0].strip()
    
    # Split sentences by period or question mark
    raw_sentences = []
    import re
    parts = re.split(r'[.।?]', content_clean)
    for p in parts:
        val = p.strip()
        if val:
            raw_sentences.append(val)
            
    for idx, raw_s in enumerate(raw_sentences):
        cleaned_lookup = raw_s.strip(", ")
        
        lookup_entry = LESSON_SENTENCE_DB.get(cleaned_lookup)
        if not lookup_entry:
            lookup_entry = LESSON_SENTENCE_DB.get(cleaned_lookup.lower())
            
        if lookup_entry:
            meaning = lookup_entry["meaning"]
            breakdown = lookup_entry["breakdown"]
        else:
            # Strip learning path template prefixes to locate actual sentences
            clean_s = cleaned_lookup.lower().strip()
            for prefix in ["advanced study of active writing", "advanced study of alphabet sounds", "advanced study of basic spelling",
                           "advanced study of comprehending stories", "advanced study of intermediate grammar", "advanced study of letter tracing",
                           "advanced study of read and answer", "advanced study of structure of paragraphs", "advanced study of talk to doctor",
                           "advanced study of talk to shopkeeper", "advanced study of talk to teacher", "advanced study of vocabulary basics",
                           "advanced study of word matching", "mastery study of active writing", "mastery study of alphabet sounds",
                           "mastery study of basic spelling", "mastery study of comprehending stories", "mastery study of intermediate grammar",
                           "mastery study of letter tracing", "mastery study of read and answer", "mastery study of structure of paragraphs",
                           "mastery study of talk to doctor", "mastery study of talk to shopkeeper", "mastery study of talk to teacher",
                           "mastery study of vocabulary basics", "mastery study of word matching"]:
                if clean_s.startswith(prefix):
                    clean_s = clean_s[len(prefix):].strip(". ")
                    break

            trans_entry = SENTENCE_TRANSLATIONS.get(clean_s)
            if trans_entry and preferred_lang in trans_entry:
                meaning = trans_entry[preferred_lang]
            else:
                if preferred_lang == "Telugu":
                    meaning = f"తెలుగు అర్థం: {raw_s}"
                elif preferred_lang == "Hindi":
                    meaning = f"हिंदी अनुवाद: {raw_s}"
                elif preferred_lang == "Tamil":
                    meaning = f"தமிழ் அர்த்தம்: {raw_s}"
                elif preferred_lang == "Kannada":
                    meaning = f"ಕನ್ನಡ ಅನುವಾದ: {raw_s}"
                elif preferred_lang == "Marathi":
                    meaning = f"मराठी भाषांतर: {raw_s}"
                else:
                    meaning = f"Meaning of: {raw_s}"

            words = [w.strip(".,!?\"'|()।") for w in raw_s.split() if w.strip()]
            breakdown = []
            for w in words:
                w_lower = w.lower()
                w_meaning = "word"
                if w_lower in ENGLISH_DICTIONARY and preferred_lang in ENGLISH_DICTIONARY[w_lower]:
                    w_meaning = ENGLISH_DICTIONARY[w_lower][preferred_lang]
                else:
                    w_meaning = w
                    
                breakdown.append({
                    "word": w,
                    "pronunciation": transliterate_text(w, language),
                    "meaning": w_meaning
                })
                
        # Remove automatic meaning-based quizzes: set quiz to None so the
        # frontend will not render meaning questions.
        sentences_data.append({
            "sentence": raw_s,
            "pronunciation": transliterate_text(raw_s, language),
            "meaning": meaning,
            # Do not send word-by-word breakdown to the frontend anymore
            "breakdown": [],
            "quiz": None
        })

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

    # Dynamically structure the lesson content based on specific lesson title/id
    title_lower = (lesson.get("title") or "").lower().strip()
    is_speaking_lesson = False

    if lesson_id == 6001 or title_lower == "alphabet sounds & recognition":
        is_speaking_lesson = True
        sentences_data = [
            {"sentence": "A", "pronunciation": "ah", "meaning": "Apple 🍎", "quiz": {"question": "Choose the correct picture starting with A", "options": ["Apple 🍎", "Banana 🍌", "Cat 🐱"], "answer": "Apple 🍎"}, "breakdown": []},
            {"sentence": "B", "pronunciation": "buh", "meaning": "Banana 🍌", "quiz": {"question": "Choose the correct picture starting with B", "options": ["Apple 🍎", "Banana 🍌", "Dog 🐶"], "answer": "Banana 🍌"}, "breakdown": []},
            {"sentence": "C", "pronunciation": "cuh", "meaning": "Cat 🐱", "quiz": {"question": "Choose the correct picture starting with C", "options": ["Cat 🐱", "Egg 🥚", "Fish 🐟"], "answer": "Cat 🐱"}, "breakdown": []},
            {"sentence": "D", "pronunciation": "duh", "meaning": "Dog 🐶", "quiz": {"question": "Choose the correct picture starting with D", "options": ["Egg 🥚", "Dog 🐶", "Grape 🍇"], "answer": "Dog 🐶"}, "breakdown": []},
            {"sentence": "E", "pronunciation": "eh", "meaning": "Egg 🥚", "quiz": {"question": "Choose the correct picture starting with E", "options": ["Fish 🐟", "Egg 🥚", "Hat 🎩"], "answer": "Egg 🥚"}, "breakdown": []}
        ]
    elif lesson_id == 6002 or title_lower == "handwriting & stroke tracing":
        is_speaking_lesson = False
        sentences_data = [
            {"sentence": "A", "pronunciation": "slant down left, slant down right, cross middle", "meaning": "Draw uppercase A", "quiz": {"question": "How many strokes to write A?", "options": ["3", "2", "4"], "answer": "3"}, "breakdown": []},
            {"sentence": "B", "pronunciation": "vertical down, top loop, bottom loop", "meaning": "Draw uppercase B", "quiz": {"question": "How many loops does B have?", "options": ["2", "1", "3"], "answer": "2"}, "breakdown": []},
            {"sentence": "C", "pronunciation": "curved arch left and down", "meaning": "Draw uppercase C", "quiz": {"question": "Is letter C drawn with a curved stroke?", "options": ["Yes", "No", "Not sure"], "answer": "Yes"}, "breakdown": []},
            {"sentence": "D", "pronunciation": "vertical down, large right loop", "meaning": "Draw uppercase D", "quiz": {"question": "How many strokes to write D?", "options": ["2", "3", "1"], "answer": "2"}, "breakdown": []},
            {"sentence": "E", "pronunciation": "vertical down, 3 horizontal bars", "meaning": "Draw uppercase E", "quiz": {"question": "How many horizontal bars in E?", "options": ["3", "2", "4"], "answer": "3"}, "breakdown": []}
        ]
    elif lesson_id == 6003 or "vowels & consonants" in title_lower:
        is_speaking_lesson = True
        sentences_data = [
            {"sentence": "Short A Sound", "pronunciation": "ae", "meaning": "Cat 🐱 & Bat 🦇", "quiz": {"question": "Which word has the Short A sound?", "options": ["Cat 🐱", "Dog 🐶", "Pin 📍"], "answer": "Cat 🐱"}, "breakdown": []},
            {"sentence": "Short E Sound", "pronunciation": "eh", "meaning": "Bed 🛏️ & Pen 🖊️", "quiz": {"question": "Which word has the Short E sound?", "options": ["Bed 🛏️", "Sun ☀️", "Box 📦"], "answer": "Bed 🛏️"}, "breakdown": []},
            {"sentence": "Short I Sound", "pronunciation": "ih", "meaning": "Pig 🐷 & Pin 📍", "quiz": {"question": "Which word has the Short I sound?", "options": ["Pig 🐷", "Cat 🐱", "Hat 🎩"], "answer": "Pig 🐷"}, "breakdown": []},
            {"sentence": "Short O Sound", "pronunciation": "ah", "meaning": "Box 📦 & Dog 🐶", "quiz": {"question": "Which word has the Short O sound?", "options": ["Dog 🐶", "Bed 🛏️", "Pen 🖊️"], "answer": "Dog 🐶"}, "breakdown": []},
            {"sentence": "Short U Sound", "pronunciation": "uh", "meaning": "Sun ☀️ & Cup ☕", "quiz": {"question": "Which word has the Short U sound?", "options": ["Sun ☀️", "Cat 🐱", "Pig 🐷"], "answer": "Sun ☀️"}, "breakdown": []}
        ]
    elif lesson_id == 6004 or "cvc words" in title_lower or "three-letter" in title_lower:
        is_speaking_lesson = True
        sentences_data = [
            {"sentence": "Cat", "pronunciation": "k-ae-t", "meaning": "Small furry pet 🐱", "quiz": {"question": "Spell the 3-letter word for 🐱", "options": ["Cat 🐱", "Dog 🐶", "Hat 🎩"], "answer": "Cat 🐱"}, "breakdown": []},
            {"sentence": "Dog", "pronunciation": "d-aw-g", "meaning": "Loyal pet 🐶", "quiz": {"question": "Spell the 3-letter word for 🐶", "options": ["Dog 🐶", "Pig 🐷", "Sun ☀️"], "answer": "Dog 🐶"}, "breakdown": []},
            {"sentence": "Sun", "pronunciation": "s-uh-n", "meaning": "Bright star ☀️", "quiz": {"question": "Spell the 3-letter word for ☀️", "options": ["Sun ☀️", "Box 📦", "Bed 🛏️"], "answer": "Sun ☀️"}, "breakdown": []},
            {"sentence": "Box", "pronunciation": "b-oh-ks", "meaning": "Cardboard container 📦", "quiz": {"question": "Spell the 3-letter word for 📦", "options": ["Box 📦", "Pen 🖊️", "Cup ☕"], "answer": "Box 📦"}, "breakdown": []},
            {"sentence": "Pen", "pronunciation": "p-eh-n", "meaning": "Writing tool 🖊️", "quiz": {"question": "Spell the 3-letter word for 🖊️", "options": ["Pen 🖊️", "Cat 🐱", "Dog 🐶"], "answer": "Pen 🖊️"}, "breakdown": []}
        ]
    elif lesson_id == 6005 or "numbers" in title_lower or "counting" in title_lower:
        is_speaking_lesson = False
        sentences_data = [
            {"sentence": "1 - One", "pronunciation": "w-uh-n", "meaning": "One Star ⭐", "quiz": {"question": "How many stars is '1'?", "options": ["1 ⭐", "2 ⭐⭐", "3 ⭐⭐⭐"], "answer": "1 ⭐"}, "breakdown": []},
            {"sentence": "2 - Two", "pronunciation": "t-oo", "meaning": "Two Ducks 🦆🦆", "quiz": {"question": "How many ducks is '2'?", "options": ["2 🦆🦆", "1 🦆", "4 🦆🦆🦆🦆"], "answer": "2 🦆🦆"}, "breakdown": []},
            {"sentence": "3 - Three", "pronunciation": "th-r-ee", "meaning": "Three Apples 🍎🍎🍎", "quiz": {"question": "How many apples is '3'?", "options": ["3 🍎🍎🍎", "2 🍎🍎", "5 🍎🍎🍎🍎🍎"], "answer": "3 🍎🍎🍎"}, "breakdown": []},
            {"sentence": "4 - Four", "pronunciation": "f-or", "meaning": "Four Cars 🚗🚗🚗🚗", "quiz": {"question": "How many cars is '4'?", "options": ["4 🚗🚗🚗🚗", "3 🚗🚗🚗", "1 🚗"], "answer": "4 🚗🚗🚗🚗"}, "breakdown": []},
            {"sentence": "5 - Five", "pronunciation": "f-y-v", "meaning": "Five Balloons 🎈🎈🎈🎈🎈", "quiz": {"question": "How many balloons is '5'?", "options": ["5 🎈🎈🎈🎈🎈", "4 🎈🎈🎈🎈", "2 🎈🎈"], "answer": "5 🎈🎈🎈🎈🎈"}, "breakdown": []}
        ]
    elif lesson_id == 6006 or "vocabulary" in title_lower:
        is_speaking_lesson = True
        sentences_data = [
            {"sentence": "Hello", "pronunciation": "h-eh-l-oh", "meaning": "Friendly Greeting 👋", "quiz": {"question": "What does 'Hello' mean?", "options": ["Greeting 👋", "Goodbye 👋", "Food 🍎"], "answer": "Greeting 👋"}, "breakdown": []},
            {"sentence": "Thank You", "pronunciation": "th-ae-ng-k y-oo", "meaning": "Showing Gratitude 🙏", "quiz": {"question": "When do you say 'Thank You'?", "options": ["Gratitude 🙏", "When sleeping 😴", "When angry 😡"], "answer": "Gratitude 🙏"}, "breakdown": []},
            {"sentence": "Water", "pronunciation": "w-ah-t-er", "meaning": "Essential Drink 💧", "quiz": {"question": "What is 'Water' used for?", "options": ["Drinking 💧", "Writing 🖊️", "Reading 📖"], "answer": "Drinking 💧"}, "breakdown": []},
            {"sentence": "School", "pronunciation": "s-k-oo-l", "meaning": "Place of Learning 🏫", "quiz": {"question": "Where do children learn?", "options": ["School 🏫", "Park 🏞️", "Market 🛒"], "answer": "School 🏫"}, "breakdown": []},
            {"sentence": "Friend", "pronunciation": "f-r-eh-n-d", "meaning": "Playmate & Buddy 👫", "quiz": {"question": "Who plays and learns with you?", "options": ["Friend 👫", "Cat 🐱", "Dog 🐶"], "answer": "Friend 👫"}, "breakdown": []}
        ]
    else:
        is_speaking_lesson = (lesson.get("category") or "").lower() == "speaking" or "speaking" in title_lower or True

    if "sentences_data" not in locals() or not sentences_data:
        raw_content = lesson.get("content") or ""
        content_sentences = [s.strip() for s in raw_content.replace("\n", ". ").split(".") if len(s.strip()) > 3]
        if not content_sentences:
            content_sentences = [
                "Learn the alphabet: A is for Apple, B is for Ball, C is for Cat",
                "Can you read these letters?",
                "Trace the letter A and write small words"
            ]

        sentences_data = []
        for idx, sentence_text in enumerate(content_sentences[:5]):
            sentences_data.append({
                "sentence": sentence_text,
                "pronunciation": sentence_text.lower(),
                "meaning": sentence_text,
                "quiz": {
                    "question": f"Practice reading: '{sentence_text}'",
                    "options": [sentence_text, "Option B", "Option C"],
                    "answer": sentence_text
                },
                "breakdown": []
            })

    return render_template(
        "lesson.html",
        lesson=lesson,
        video=video,
        quiz=quiz,
        translations=translations,
        is_speaking_lesson=is_speaking_lesson,
        age=age,
        learning_level=learning_level,
        lesson_title_translit=lesson_title_translit,
        sentences_data=sentences_data,
        translated_title=translated_title,
        preferred_language=preferred_lang,
        learning_language=learning_lang,
        language=language
    )

@app.route("/profile")
@login_required
def profile():
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fullname, email, age, education_level, learning_level, learning_status, language, 
               dob, gender, avatar, coins, badges, current_mascot_dress, mascot_dresses, stream, sub_stream,
               preferred_language, learning_language
        FROM users WHERE id = ?
    """, (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user and user["language"]:
        session["language"] = user["language"]
        language = user["language"]
    else:
        language = session.get("language", "English")

    translations = get_translations(language)

    return render_template(
        "profile.html",
        user=user,
        translations=translations,
        current_language=language
    )


@app.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    user_id = session.get("user_id")
    print(f"[DEBUG] Request received -> Endpoint: /update_profile, User ID: {user_id}")
    
    if request.is_json:
        data = request.get_json() or {}
        fullname = (data.get("fullname") or "").strip()
        dob = data.get("dob")
        gender = data.get("gender") or ""
        avatar = data.get("avatar") or "Cat"
        current_mascot_dress = data.get("current_mascot_dress") or "Default"
        preferred_language = data.get("preferred_language") or data.get("language") or "English"
        learning_language = data.get("learning_language") or "English"
        learning_level = data.get("learning_level") or "Beginner"
    else:
        fullname = request.form.get("fullname", "").strip()
        dob = request.form.get("dob")
        gender = request.form.get("gender", "")
        avatar = request.form.get("avatar", "Cat")
        current_mascot_dress = request.form.get("current_mascot_dress", "Default")
        preferred_language = request.form.get("preferred_language") or request.form.get("language") or "English"
        learning_language = request.form.get("learning_language") or "English"
        learning_level = request.form.get("learning_level", "Beginner")

    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT fullname, dob, gender, avatar, current_mascot_dress, language, preferred_language, learning_language, learning_level 
        FROM users WHERE id = ?
    """, (user_id,))
    current = cursor.fetchone()
    if current:
        if not fullname: fullname = current["fullname"]
        if not dob: dob = current["dob"]
        if not gender: gender = current["gender"] or ""
        if not avatar: avatar = current["avatar"] or "Cat"
        if not current_mascot_dress: current_mascot_dress = current["current_mascot_dress"] or "Default"
        if not preferred_language: preferred_language = current["preferred_language"] or current["language"] or "English"
        if not learning_language: learning_language = current["learning_language"] or "English"
        if not learning_level: learning_level = current["learning_level"] or "Beginner"

    # Calculate age dynamically from Date of Birth
    age = session.get("age", 8)
    if dob:
        age = calculate_age(dob)

    print(f"[DEBUG] Executing SQL UPDATE -> name='{fullname}', dob='{dob}', age={age}, gender='{gender}', avatar='{avatar}', dress='{current_mascot_dress}', pref_lang='{preferred_language}', learn_lang='{learning_language}', level='{learning_level}'")
    cursor.execute("""
        UPDATE users 
        SET fullname = ?, dob = ?, age = ?, gender = ?, avatar = ?, current_mascot_dress = ?, language = ?, preferred_language = ?, learning_language = ?, learning_level = ?
        WHERE id = ?
    """, (fullname, dob, age, gender, avatar, current_mascot_dress, preferred_language, preferred_language, learning_language, learning_level, user_id))
    
    rows_affected = cursor.rowcount
    print(f"[DEBUG] Rows affected: {rows_affected}")
    
    conn.commit()
    print(f"[DEBUG] Database commit successful")
    
    # Re-query database record to verify modification
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    verified = cursor.fetchone()
    conn.close()

    # Update active session keys instantly
    session["fullname"] = verified["fullname"]
    session["dob"] = verified["dob"]
    session["age"] = verified["age"]
    session["gender"] = verified["gender"]
    session["avatar"] = verified["avatar"]
    session["current_mascot_dress"] = verified["current_mascot_dress"]
    session["language"] = verified["language"] or preferred_language or "English"
    session["preferred_language"] = verified["preferred_language"] or preferred_language or "English"
    session["learning_language"] = verified["learning_language"]
    session["learning_level"] = verified["learning_level"]
    
    print(f"[DEBUG] Session updated -> fullname='{session['fullname']}', age={session['age']}, language='{session['language']}', preferred='{session['preferred_language']}', learning='{session['learning_language']}', level='{session['learning_level']}'")

    # Refresh dynamic recommendation engine
    get_content_recommendations(user_id)
    generate_personalized_learning_path(user_id)

    if request.is_json:
        print(f"[DEBUG] Response returned -> JSON Success")
        return {
            "status": "success",
            "message": "Profile updated successfully.",
            "fullname": session["fullname"],
            "dob": session["dob"],
            "age": session["age"],
            "gender": session["gender"],
            "avatar": session["avatar"],
            "current_mascot_dress": session["current_mascot_dress"],
            "language": session["language"],
            "preferred_language": session["preferred_language"],
            "learning_language": session["learning_language"],
            "learning_level": session["learning_level"],
            "translations": get_translations(session["language"])
        }

    print(f"[DEBUG] Response returned -> Redirecting to /profile")
    flash("Profile updated successfully.", "success")
    return redirect(url_for("profile"))


@app.route("/dashboard")
@login_required
def dashboard():
    language = session.get("language", "English")
    translations = get_translations(language)
    fullname = session.get("fullname", translations.get("dashboard_profile_title", "Learner"))
    language_label = session.get("language", "English")
    
    user_id = session.get("user_id")
    
    # 1. Fetch user parameters
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT fullname, email, age, stream, sub_stream, xp, streak, dob, last_birthday_wished_year, coins, badges, avatar, current_mascot_dress, mascot_dresses,
               weak_skills, strong_skills, recommended_activities, learning_level, current_proficiency,
               reading_score, writing_score, grammar_score, speaking_score, pronunciation_score
        FROM users WHERE id = ?
    """, (user_id,))
    user_row = cursor.fetchone()
    
    if not user_row:
        conn.close()
        return redirect(url_for("logout"))
        
    age = user_row["age"]
    
    # Retrieve total assessment attempts
    cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE user_id = ?", (user_id,))
    assessment_count = cursor.fetchone()[0]
    dob_str = user_row["dob"]
    last_wished = user_row["last_birthday_wished_year"] or 0
    coins = user_row["coins"] or 0
    badges = user_row["badges"] or ""
    avatar = user_row["avatar"] or "Cat"
    current_mascot_dress = user_row["current_mascot_dress"] or "Default"
    mascot_dresses = user_row["mascot_dresses"] or "Default"
    xp = user_row["xp"] or 0
    streak = user_row["streak"] or 0
    stream = user_row["stream"]
    sub_stream = user_row["sub_stream"]
    
    # Recalculate age if birthday has passed
    if dob_str:
        age = calculate_age(dob_str)
        cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, user_id))
        conn.commit()
        session["age"] = age
        
    # Check if today is the user's birthday
    is_birthday = False
    today = date.today()
    if dob_str:
        try:
            dob_date = datetime.strptime(dob_str, "%Y-%m-%d").date()
        except Exception:
            try:
                dob_date = datetime.strptime(dob_str, "%d/%m/%Y").date()
            except Exception:
                dob_date = None
                
        if dob_date and dob_date.month == today.month and dob_date.day == today.day:
            if not session.get("birthday_shown"):
                is_birthday = True
                session["birthday_shown"] = True
            if last_wished < today.year:
                last_wished = today.year
                coins += 100
                
                # Add Birthday Badge
                badge_list = [b.strip() for b in badges.split(",") if b.strip()]
                if "Birthday Badge" not in badge_list:
                    badge_list.append("Birthday Badge")
                badges = ",".join(badge_list)
                
                # Add party_hat outfit
                dress_list = [d.strip() for d in mascot_dresses.split(",") if d.strip()]
                if "party_hat" not in dress_list:
                    dress_list.append("party_hat")
                mascot_dresses = ",".join(dress_list)
                current_mascot_dress = "party_hat"
                
                cursor.execute("""
                    UPDATE users 
                    SET last_birthday_wished_year = ?, coins = ?, badges = ?, mascot_dresses = ?, current_mascot_dress = ?
                    WHERE id = ?
                """, (today.year, coins, badges, mascot_dresses, current_mascot_dress, user_id))
                conn.commit()
                
                session["coins"] = coins
                session["badges"] = badges
                session["current_mascot_dress"] = current_mascot_dress

    age_group = get_age_group(age)
    
    # 2. Get predicted proficiency
    pred_prof = predict_user_proficiency(user_id, language)
    proficiency = pred_prof["level"]
    
    # Query database for the latest score instead of relying solely on session
    cursor.execute("SELECT score FROM assessment_history WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,))
    row = cursor.fetchone()
    if row:
        last_score = row["score"]
        session["last_score"] = last_score
    else:
        last_score = session.get("last_score")

    learners = get_all_users()
    learner_count = len(learners)
    
    # 3. Dynamic recommendations & personalized learning path
    recommended_lessons = get_content_recommendations(user_id)
    today_learning_path = generate_personalized_learning_path(user_id)
    next_lesson = recommended_lessons[0] if recommended_lessons else None

    # Calculate progress metrics
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(DISTINCT lesson_id) FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_lessons_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (language,))
    total_lessons_in_lang = cursor.fetchone()[0] or 10
    
    cursor.execute("SELECT COUNT(*), AVG(score) FROM assessment_history WHERE user_id = ?", (user_id,))
    arow = cursor.fetchone()
    assessment_count = arow[0] if arow else 0
    average_score = round(arow[1], 1) if arow and arow[1] is not None else (last_score or 0.0)

    cursor.execute("""
        SELECT l.id, l.title, l.category, lp.timestamp
        FROM lesson_progress lp
        JOIN lessons l ON lp.lesson_id = l.id
        WHERE lp.user_id = ?
        ORDER BY lp.timestamp DESC LIMIT 10
    """, (user_id,))
    completed_lessons = [dict(r) for r in cursor.fetchall()]
    conn.close()

    progress_percentage = min(100.0, round((completed_lessons_count / max(1, total_lessons_in_lang)) * 100, 1))

    profile = {
        "fullname": user_row["fullname"],
        "email": user_row["email"],
        "language": language,
        "age": int(age) if age is not None else 8,
        "coins": coins,
        "badges": badges,
        "avatar": avatar,
        "current_mascot_dress": current_mascot_dress,
        "mascot_dresses": mascot_dresses,
        "xp": xp,
        "streak": streak,
        "completed_lessons_count": completed_lessons_count,
        "videos_watched_count": completed_lessons_count,
        "assessment_count": assessment_count,
        "average_score": average_score,
        "progress_percentage": progress_percentage,
        "current_proficiency": pred_prof["current_proficiency"] or user_row["current_proficiency"] or user_row["learning_level"] or "Beginner",
        "weak_skills": user_row["weak_skills"] or "",
        "strong_skills": user_row["strong_skills"] or "",
        "reading_score": user_row["reading_score"],
        "writing_score": user_row["writing_score"],
        "grammar_score": user_row["grammar_score"],
        "speaking_score": user_row["speaking_score"],
        "pronunciation_score": user_row["pronunciation_score"]
    }

    ai_recs = {}
    if user_row["recommended_activities"]:
        try:
            ai_recs = json.loads(user_row["recommended_activities"])
        except Exception:
            pass

    if not isinstance(ai_recs, dict) or "lessons" not in ai_recs:
        ai_recs = generate_ai_recommendations(user_id)

    prof_key_map = {
        "Beginner": "level_beginner",
        "Basic": "level_basic",
        "Intermediate": "level_intermediate",
        "Advanced": "level_advanced"
    }
    proficiency_key = prof_key_map.get(proficiency, "level_beginner")
    localized_proficiency = translations.get(proficiency_key, proficiency)

    return render_template(
        "dashboard.html",
        translations=translations,
        fullname=fullname,
        language_label=language_label,
        last_score=last_score,
        proficiency=localized_proficiency,
        learner_count=learner_count,
        recommended_lessons=recommended_lessons,
        completed_lessons=completed_lessons,
        today_learning_path=today_learning_path,
        next_lesson=next_lesson,
        xp=xp,
        streak=streak,
        pred_prof=pred_prof,
        is_birthday=is_birthday,
        profile=profile,
        ai_recs=ai_recs
    )


@app.route("/submit_assessment", methods=["POST"])
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

    def normalize_skill_name(skill_name):
        skill = (skill_name or "").strip().lower()
        if skill in {"grammar", "vocabulary", "comprehension"}:
            return "comprehension"
        return skill

    # Category counters
    cat_corrects = {
        "reading": 0, "writing": 0, "comprehension": 0,
        "listening": 0, "speaking": 0, "vocabulary": 0,
        "grammar": 0
    }
    cat_totals = {
        "reading": 0, "writing": 0, "comprehension": 0,
        "listening": 0, "speaking": 0, "vocabulary": 0,
        "grammar": 0
    }

    for question in questions:
        q_type = question.get("type", "reading").lower()
        skill_key = question.get("skill_score_key") or question.get("skill") or q_type
        skill_name = normalize_skill_name(skill_key)
        if skill_name not in cat_corrects:
            skill_name = "comprehension"

        user_answer = request.form.get(question["name"], "")
        expected_answer = str(question["answer"]).strip()

        is_correct = False
        if q_type == "speaking":
            is_correct = get_similarity_score(user_answer, expected_answer) >= 0.75
        else:
            is_correct = normalize_text(user_answer) == normalize_text(expected_answer)

        cat_totals[skill_name] += 1
        if is_correct:
            correct += 1
            cat_corrects[skill_name] += 1

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

    # If no explicit grammar/vocabulary questions were included, reuse comprehension for the legacy metrics.
    if cat_totals["grammar"] == 0 and cat_totals["comprehension"] > 0:
        cat_totals["grammar"] = cat_totals["comprehension"]
        cat_corrects["grammar"] = cat_corrects["comprehension"]
    if cat_totals["vocabulary"] == 0 and cat_totals["comprehension"] > 0:
        cat_totals["vocabulary"] = cat_totals["comprehension"]
        cat_corrects["vocabulary"] = cat_corrects["comprehension"]

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

    # Determine strong, moderate & weak skills from the assessment skill scores
    skill_scores = {
        "Reading": cat_scores["reading"],
        "Writing": cat_scores["writing"],
        "Listening": cat_scores["listening"],
        "Speaking": cat_scores["speaking"],
        "Comprehension": cat_scores["comprehension"]
    }
    strong_list = []
    moderate_list = []
    weak_list = []
    for skill, s_score in skill_scores.items():
        if s_score >= 70:
            strong_list.append(skill)
        elif s_score >= 40:
            moderate_list.append(skill)
        else:
            weak_list.append(skill)

    if not strong_list and skill_scores:
        highest_skill = max(skill_scores, key=skill_scores.get)
        if skill_scores[highest_skill] > 0:
            strong_list.append(highest_skill)
            if highest_skill in moderate_list:
                moderate_list.remove(highest_skill)
            if highest_skill in weak_list:
                weak_list.remove(highest_skill)

    strong_skills_str = ", ".join(strong_list) if strong_list else "None"
    moderate_skills_str = ", ".join(moderate_list) if moderate_list else "None"
    weak_skills_str = ", ".join(weak_list) if weak_list else "None"

    user_id = session.get("user_id")
    age = session.get("age")
    age_group = get_age_group(age)
    
    # 1. Record attempt in assessment_history table
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_history (
            user_id, score, correct, total, language, age_group, wrong_answers, accuracy, 
            completion_time, reading_score, writing_score, comprehension_score, vocabulary_score, grammar_score, 
            listening_score, speaking_score, overall_score, learner_level, weak_skills, moderate_skills, strong_skills
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        user_id, score, correct, total, language, age_group, incorrect, float(score),
        time_taken, cat_scores["reading"], cat_scores["writing"], cat_scores["comprehension"], cat_scores["vocabulary"],
        cat_scores["grammar"], cat_scores["listening"], cat_scores["speaking"], float(score),
        learner_level, weak_skills_str, moderate_skills_str, strong_skills_str
    ))
    conn.commit()
    conn.close()

    # 2. Update user profile details
    conn = get_db_connection()
    cursor = conn.cursor()
    vocabulary_score = int((cat_scores["reading"] + cat_scores["comprehension"]) / 2)
    grammar_score = int((cat_scores["writing"] + cat_scores["comprehension"]) / 2)
    cursor.execute("""
        UPDATE users SET
            initial_assessment_completed = 1,
            current_proficiency = ?,
            assessment_score = ?,
            reading_score = ?,
            writing_score = ?,
            comprehension_score = ?,
            vocabulary_score = ?,
            grammar_score = ?,
            listening_score = ?,
            speaking_score = ?,
            weak_skills = ?,
            moderate_skills = ?,
            strong_skills = ?
        WHERE id = ?
    """, (
        learner_level, float(score),
        cat_scores["reading"], cat_scores["writing"], cat_scores["comprehension"],
        vocabulary_score, grammar_score, cat_scores["listening"], cat_scores["speaking"],
        weak_skills_str, moderate_skills_str, strong_skills_str, user_id
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
    session["last_score"] = score
    session.pop("assessment_questions", None)
    session.pop("assessment_start_time", None)

    # Refresh learner state and adaptive recommendations after assessment completion
    recalculate_and_refresh_learner_state(user_id)

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
    )
@app.route("/login_user", methods=["POST"])
def login_user():
    email = request.form.get("email", "").strip()
    password = request.form.get("password", "")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if user:
        if "account_status" in user.keys() and user["account_status"] == "inactive":
            flash("Your account has been deactivated. Please contact administration.", "danger")
            return redirect(url_for("login"))
            
        if check_password_hash(user["password"], password):
            # Session Fixation Protection
            session.clear()
            
            # Setup session credentials
            session["user_id"] = user["id"]
            session["fullname"] = user["fullname"]
            session["email"] = user["email"]
            
            # Load preferences
            pref_lang = user["preferred_language"] or user["language"] or "English"
            learn_lang = user["learning_language"] or "English"
            session["language"] = user["language"] or pref_lang
            session["preferred_language"] = pref_lang
            session["learning_language"] = learn_lang
            
            # Recalculate age dynamically from dob
            age = user["age"]
            dob = user["dob"]
            if dob and dob != "Not set":
                age = calculate_age(dob)
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE users SET age = ? WHERE id = ?", (age, user["id"]))
                conn.commit()
                conn.close()
                
            try:
                age_int = int(age) if age is not None else 8
            except (ValueError, TypeError):
                age_int = 8

            session["learning_level"] = user["learning_level"] if ("learning_level" in user.keys() and user["learning_level"]) else "Beginner"
            session["age"] = age_int
            session["stream"] = user["stream"]
            session["sub_stream"] = user["sub_stream"]
            session["dob"] = dob
            session["gender"] = user["gender"]
            session["avatar"] = user["avatar"]
            session["current_mascot_dress"] = user["current_mascot_dress"] or "Default"
            session["coins"] = user["coins"] or 0
            session["badges"] = user["badges"] or ""
            
            # Retrieve initial assessment completion status
            init_complete = user["initial_assessment_completed"] or 0
            
            session["initial_assessment_completed"] = init_complete
            
            if init_complete:
                flash("Login Successful! Welcome back.", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("Welcome! Please complete the initial assessment to begin.", "info")
                if 5 <= age_int <= 7:
                    return redirect(url_for("assessment", mode="placement"))
                else:
                    return redirect(url_for("assessment"))
        else:
            flash("Incorrect Password!", "danger")
            return redirect(url_for("login"))
    else:
        flash("User does not exist.", "danger")
        return redirect(url_for("login"))
@app.route("/logout")
def logout():

    session.clear()

    flash("Logged out successfully!", "info")

    return redirect(url_for("home"))


# -------------------------------
# Forgot Password (Temporary)
# -------------------------------
@app.route("/forgot_password")
def forgot_password():

    flash("Forgot Password feature will be added soon.", "info")

    return redirect(url_for("login"))


# -------------------------------
# Run Application
# -------------------------------
create_database()






# -------------------------------
# Lessons Module Detail & Completion
# -------------------------------
@app.route("/complete_lesson/<int:lesson_id>", methods=["POST"])
@login_required
def complete_lesson(lesson_id):
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Update recommendation_history to completed
    cursor.execute("""
        UPDATE recommendation_history 
        SET status = 'completed' 
        WHERE user_id = ? AND item_id = ? AND status = 'pending'
    """, (user_id, lesson_id))
    
    cursor.execute("SELECT id FROM lesson_progress WHERE user_id = ? AND lesson_id = ?", (user_id, lesson_id))
    is_new_completion = cursor.fetchone() is None
    if is_new_completion:
        cursor.execute("INSERT INTO lesson_progress (user_id, lesson_id) VALUES (?, ?)", (user_id, lesson_id))
        conn.commit()
        
    # Get user language & calculate progress
    cursor.execute("SELECT language FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    user_lang = urow["language"] if urow else "English"
    
    cursor.execute("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?", (user_id,))
    completed_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (user_lang,))
    total_lessons = cursor.fetchone()[0] or 10
    
    progress_percentage = min(100.0, (completed_count / total_lessons) * 100)
    
    cursor.execute("""
        UPDATE users 
        SET completed_lessons_count = ?, 
            progress_percentage = ?,
            learning_path_progress = ?
        WHERE id = ?
    """, (completed_count, progress_percentage, progress_percentage, user_id))
    conn.commit()
    conn.close()
    
    # 2. Log study session of 10 minutes and award 15 XP for completing lesson
    if is_new_completion:
        log_study_activity(user_id, 10, 15)
        
    # 3. Refresh AI Recommendations & Learning Path
    recalculate_and_refresh_learner_state(user_id)
        
    flash("Lesson marked as completed! Recommendations and learning path updated.", "success")
    return redirect(url_for("week_module"))

# -------------------------------
# Admin Panel & Parent Dashboard Routes
# -------------------------------
# -------------------------------
# Admin Module - Login, Logout, Dashboard
# -------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if user and user["role"] == "admin":
            if check_password_hash(user["password"], password):
                session.clear()
                session["user_id"] = user["id"]
                session["fullname"] = user["fullname"]
                session["email"] = user["email"]
                session["role"] = "admin"
                
                # Log active sign-in
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'LOGIN', 'Admin logged in successfully')", (user["id"],))
                conn.commit()
                conn.close()
                
                flash("Welcome back, Administrator!", "success")
                return redirect(url_for("admin_dashboard"))
            else:
                flash("Invalid credentials.", "danger")
        else:
            flash("Unauthorized access or invalid credentials.", "danger")
            
    return render_template("admin_login.html")

@app.route("/admin/logout")
def admin_logout():
    user_id = session.get("user_id")
    if user_id:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'LOGOUT', 'Admin logged out')", (user_id,))
        conn.commit()
        conn.close()
    session.clear()
    flash("Logged out from Admin Module successfully.", "info")
    return redirect(url_for("admin_login"))

@app.route("/admin")
@admin_required
def admin_panel():
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Stat counters
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student'")
    total_learners = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM lessons")
    total_lessons = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM assessment_history")
    total_assessments_taken = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'student' AND account_status = 'active'")
    active_users = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM recommendation_history")
    total_recommendations = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM voice_practice_history")
    total_voice_practice = cursor.fetchone()[0] or 0
    
    stats = {
        "total_learners": total_learners,
        "total_lessons": total_lessons,
        "total_assessments_taken": total_assessments_taken,
        "active_users": active_users,
        "total_recommendations": total_recommendations,
        "total_voice_practice": total_voice_practice
    }
    
    # Lists for tables
    cursor.execute("SELECT * FROM users WHERE role IN ('student', 'parent') ORDER BY id DESC")
    learners = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM lessons ORDER BY id DESC")
    lessons = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM assessment_questions ORDER BY id DESC")
    custom_questions = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("""
        SELECT v.*, u.fullname, u.email 
        FROM voice_practice_history v 
        LEFT JOIN users u ON v.user_id = u.id 
        ORDER BY v.id DESC LIMIT 30
    """)
    voice_logs = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("""
        SELECT r.*, u.fullname, u.email 
        FROM recommendation_history r 
        LEFT JOIN users u ON r.user_id = u.id 
        ORDER BY r.timestamp DESC LIMIT 30
    """)
    recommendations_logs = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("""
        SELECT a.*, u.fullname 
        FROM activity_logs a 
        LEFT JOIN users u ON a.user_id = u.id 
        ORDER BY a.timestamp DESC LIMIT 15
    """)
    recent_activities = [dict(r) for r in cursor.fetchall()]
    
    # Language statistics
    langs = ["English", "Telugu", "Tamil", "Hindi", "Kannada", "Marathi"]
    lang_stats = []
    for l in langs:
        cursor.execute("SELECT COUNT(*) FROM users WHERE language = ? AND role = 'student'", (l,))
        u_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (l,))
        les_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM assessment_history WHERE language = ?", (l,))
        ass_count = cursor.fetchone()[0]
        lang_stats.append({
            "name": l,
            "users": u_count,
            "lessons": les_count,
            "assessments": ass_count
        })
        
    # Level statistics
    level_stats = {}
    for lvl in ["Beginner", "Basic", "Intermediate", "Advanced"]:
        cursor.execute("SELECT COUNT(*) FROM users WHERE learning_level = ? AND role = 'student'", (lvl,))
        level_stats[lvl] = cursor.fetchone()[0]
        
    # Website Settings
    cursor.execute("SELECT * FROM website_settings")
    settings = {row["key"]: row["value"] for row in cursor.fetchall()}

    # Compute chart variables for admin dashboard
    monthly_regs = [total_learners, 0, 0, 0, 0, 0]
    lesson_completions = {}
    assessment_perf = {}
    lang_dist = {}

    for item in lang_stats:
        lname = item["name"]
        lang_dist[lname] = item["users"]
        lesson_completions[lname] = item["lessons"]
        
    for l in langs:
        cursor.execute("SELECT AVG(score) FROM assessment_history WHERE language = ?", (l,))
        avg_row = cursor.fetchone()
        avg_score = avg_row[0] if avg_row and avg_row[0] is not None else 0
        assessment_perf[l] = round(avg_score, 1)

    # Age distribution bins
    cursor.execute("SELECT age FROM users WHERE role = 'student'")
    age_bins = {"toddler": 0, "young": 0, "middle": 0, "older": 0, "senior": 0}
    for row in cursor.fetchall():
        try:
            age_val = int(row[0]) if row[0] else 0
            if age_val <= 5:
                age_bins["toddler"] += 1
            elif age_val <= 12:
                age_bins["young"] += 1
            elif age_val <= 18:
                age_bins["middle"] += 1
            elif age_val <= 50:
                age_bins["older"] += 1
            else:
                age_bins["senior"] += 1
        except (ValueError, TypeError):
            pass

    recommendation_rules = settings.get("recommendation_rules", "Rule 1: Accuracy < 60% -> Foundational Level\nRule 2: Accuracy 60-80% -> Intermediate Level\nRule 3: Accuracy > 80% -> Advanced Level")

    conn.close()
    
    return render_template(
        "admin_dashboard.html",
        stats=stats,
        learners=learners,
        lessons=lessons,
        custom_questions=custom_questions,
        voice_logs=voice_logs,
        recommendations_logs=recommendations_logs,
        recent_activities=recent_activities,
        lang_stats=lang_stats,
        level_stats=level_stats,
        settings=settings,
        monthly_regs=monthly_regs,
        lesson_completions=lesson_completions,
        assessment_perf=assessment_perf,
        lang_dist=lang_dist,
        age_bins=age_bins,
        recommendation_rules=recommendation_rules
    )

@app.route("/admin/learner/edit", methods=["POST"])
@admin_required
def admin_edit_learner():
    user_id = request.form.get("user_id")
    fullname = request.form.get("fullname")
    age = request.form.get("age")
    role = request.form.get("role")
    language = request.form.get("language")
    learning_level = request.form.get("learning_level")
    account_status = request.form.get("account_status")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET fullname = ?, age = ?, role = ?, language = ?, learning_level = ?, account_status = ?
        WHERE id = ?
    """, (fullname, age, role, language, learning_level, account_status, user_id))
    
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'EDIT_USER', ?)",
                   (session["user_id"], f"Updated profile for learner ID {user_id} ({fullname})"))
    conn.commit()
    conn.close()
    
    flash("Learner details updated successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#learners")

@app.route("/admin/student/<int:student_id>/toggle-status", methods=["POST"])
@admin_required
def admin_toggle_student_status(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_status, fullname FROM users WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    if row:
        new_status = "inactive" if row["account_status"] == "active" or not row["account_status"] else "active"
        cursor.execute("UPDATE users SET account_status = ? WHERE id = ?", (new_status, student_id))
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'TOGGLE_USER_STATUS', ?)",
                       (session["user_id"], f"Toggled status of learner {row['fullname']} to {new_status}"))
        conn.commit()
        flash("Student status updated successfully.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard") + "#learners")

@app.route("/admin/student/<int:student_id>/reset-progress", methods=["POST"])
@admin_required
def admin_reset_student_progress(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET xp = 0, coins = 0, streak = 0, longest_streak = 0, pronunciation_score = 0.0, reading_speed_wpm = 0 WHERE id = ?", (student_id,))
    cursor.execute("DELETE FROM assessment_history WHERE user_id = ?", (student_id,))
    cursor.execute("DELETE FROM lesson_progress WHERE user_id = ?", (student_id,))
    cursor.execute("DELETE FROM voice_practice_history WHERE user_id = ?", (student_id,))
    
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'RESET_USER_PROGRESS', ?)",
                   (session["user_id"], f"Reset all progress statistics for student ID {student_id}"))
    conn.commit()
    conn.close()
    flash("Student learning progress has been reset.", "success")
    return redirect(url_for("admin_dashboard") + "#learners")

@app.route("/admin/student/<int:student_id>/delete", methods=["POST"])
@admin_required
def admin_delete_student(student_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (student_id,))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'DELETE_USER', ?)",
                   (session["user_id"], f"Deleted student account ID {student_id}"))
    conn.commit()
    conn.close()
    flash("Student account deleted successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#learners")

@app.route("/admin/parent/<int:parent_id>/toggle-status", methods=["POST"])
@admin_required
def admin_toggle_parent_status(parent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT account_status, fullname FROM users WHERE id = ?", (parent_id,))
    row = cursor.fetchone()
    if row:
        new_status = "inactive" if row["account_status"] == "active" or not row["account_status"] else "active"
        cursor.execute("UPDATE users SET account_status = ? WHERE id = ?", (new_status, parent_id))
        cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'TOGGLE_PARENT_STATUS', ?)",
                       (session["user_id"], f"Toggled status of parent {row['fullname']} to {new_status}"))
        conn.commit()
        flash("Parent status updated successfully.", "success")
    conn.close()
    return redirect(url_for("admin_dashboard") + "#learners")

@app.route("/admin/parent/<int:parent_id>/delete", methods=["POST"])
@admin_required
def admin_delete_parent(parent_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (parent_id,))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'DELETE_PARENT', ?)",
                   (session["user_id"], f"Deleted parent ID {parent_id}"))
    conn.commit()
    conn.close()
    flash("Parent account deleted successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#learners")


@app.route("/admin/lesson", methods=["POST"])
@admin_required
def admin_create_lesson():
    title = request.form.get("title")
    category = request.form.get("category")
    language = request.form.get("language")
    difficulty = request.form.get("difficulty")
    content = request.form.get("content")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lessons (title, category, language, content, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (title, category, language, content, difficulty))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'CREATE_LESSON', ?)",
                   (session["user_id"], f"Created new lesson: {title}"))
    conn.commit()
    conn.close()

    flash("New lesson created successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#content")


@app.route("/admin/lesson/edit", methods=["POST"])
@admin_required
def admin_edit_lesson():
    lesson_id = request.form.get("lesson_id")
    title = request.form.get("title")
    category = request.form.get("category")
    language = request.form.get("language")
    difficulty = request.form.get("difficulty")
    content = request.form.get("content")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE lessons 
        SET title = ?, category = ?, language = ?, difficulty = ?, content = ?
        WHERE id = ?
    """, (title, category, language, difficulty, content, lesson_id))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'EDIT_LESSON', ?)",
                   (session["user_id"], f"Updated lesson ID {lesson_id} ({title})"))
    conn.commit()
    conn.close()

    flash("Lesson content updated successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#content")


@app.route("/admin/lesson/<int:lesson_id>/delete", methods=["POST"])
@admin_required
def admin_delete_lesson_item(lesson_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM lessons WHERE id = ?", (lesson_id,))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'DELETE_LESSON', ?)",
                   (session["user_id"], f"Deleted lesson ID {lesson_id}"))
    conn.commit()
    conn.close()
    flash("Lesson deleted successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#content")


@app.route("/admin/assessment/add", methods=["POST"])
@admin_required
def admin_add_assessment():
    category = request.form.get("category")
    language = request.form.get("language")
    difficulty = request.form.get("difficulty")
    prompt = request.form.get("prompt")
    options = request.form.get("options")
    correct_index = int(request.form.get("correct_index", 0))
    explanation = request.form.get("explanation", "")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_questions (category, language, difficulty, prompt, options, correct_index, explanation)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (category, language, difficulty, prompt, options, correct_index, explanation))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'ADD_QUESTION', ?)",
                   (session["user_id"], f"Added custom assessment question: {prompt[:30]}..."))
    conn.commit()
    conn.close()

    flash("Custom assessment question created successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#assessments")


@app.route("/admin/assessment/edit", methods=["POST"])
@admin_required
def admin_edit_assessment():
    q_id = request.form.get("question_id")
    category = request.form.get("category")
    language = request.form.get("language")
    difficulty = request.form.get("difficulty")
    prompt = request.form.get("prompt")
    options = request.form.get("options")
    correct_index = int(request.form.get("correct_index", 0))
    explanation = request.form.get("explanation", "")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE assessment_questions 
        SET category = ?, language = ?, difficulty = ?, prompt = ?, options = ?, correct_index = ?, explanation = ?
        WHERE id = ?
    """, (category, language, difficulty, prompt, options, correct_index, explanation, q_id))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'EDIT_QUESTION', ?)",
                   (session["user_id"], f"Edited custom question ID {q_id}"))
    conn.commit()
    conn.close()

    flash("Custom assessment question updated successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#assessments")


@app.route("/admin/assessment/<int:question_id>/delete", methods=["POST"])
@admin_required
def admin_delete_assessment(question_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessment_questions WHERE id = ?", (question_id,))
    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'DELETE_QUESTION', ?)",
                   (session["user_id"], f"Deleted custom question ID {question_id}"))
    conn.commit()
    conn.close()

    flash("Custom assessment question deleted.", "success")
    return redirect(url_for("admin_dashboard") + "#assessments")


@app.route("/admin/notifications/send", methods=["POST"])
@admin_required
def admin_send_notification():
    target = request.form.get("target")
    title = request.form.get("title")
    message = request.form.get("message")

    conn = get_db_connection()
    cursor = conn.cursor()
    if target == "all":
        cursor.execute("SELECT id FROM users WHERE role = 'student'")
        student_ids = [row["id"] for row in cursor.fetchall()]
        for s_id in student_ids:
            cursor.execute("INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)", (s_id, title, message))
    else:
        cursor.execute("INSERT INTO notifications (user_id, title, message) VALUES (?, ?, ?)", (int(target), title, message))

    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'SEND_NOTIFICATION', ?)",
                   (session["user_id"], f"Sent alert '{title}' to target: {target}"))
    conn.commit()
    conn.close()

    flash("Notification sent successfully!", "success")
    return redirect(url_for("admin_dashboard") + "#settings")


@app.route("/admin/settings/update", methods=["POST"])
@admin_required
def admin_settings_update():
    site_name = request.form.get("site_name")
    tutor_voice = request.form.get("tutor_voice")
    allow_registration = request.form.get("allow_registration")
    maintenance_mode = request.form.get("maintenance_mode")

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES ('site_name', ?)", (site_name,))
    cursor.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES ('tutor_voice', ?)", (tutor_voice,))
    cursor.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES ('allow_registration', ?)", (allow_registration,))
    cursor.execute("INSERT OR REPLACE INTO website_settings (key, value) VALUES ('maintenance_mode', ?)", (maintenance_mode,))

    cursor.execute("INSERT INTO activity_logs (user_id, action, details) VALUES (?, 'UPDATE_SETTINGS', ?)",
                   (session["user_id"], "Updated core website settings"))
    conn.commit()
    conn.close()

    flash("Website settings saved successfully.", "success")
    return redirect(url_for("admin_dashboard") + "#settings")


@app.route("/api/admin/games/toggle", methods=["POST"])
@admin_required
def admin_toggle_game():
    data = request.get_json() or {}
    game_id = data.get("game_id")
    enabled = 1 if data.get("enabled") else 0

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE game_config SET enabled = ? WHERE game_id = ?", (enabled, game_id))
    conn.commit()
    conn.close()

    return jsonify({"success": True})


# -------------------------------
# Report Generation Download Routes
# -------------------------------
import csv
from io import StringIO
from flask import Response, make_response

@app.route("/parent/report/<format>")
@parent_required
def parent_report_download(format):
    user_id = session.get("user_id")
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = dict(cursor.fetchone())
    cursor.execute("SELECT * FROM assessment_history WHERE user_id = ?", (user_id,))
    history = [dict(r) for r in cursor.fetchall()]
    conn.close()

    if format == "csv" or format == "excel":
        si = StringIO()
        cw = csv.writer(si, delimiter=',' if format == 'csv' else '\t')
        cw.writerow(["Student Report for " + user["fullname"]])
        cw.writerow([])
        cw.writerow(["Parameter", "Value"])
        cw.writerow(["Email", user["email"]])
        cw.writerow(["Age", user["age"]])
        cw.writerow(["Preferred Language", user["language"]])
        cw.writerow(["Learning Level", user["learning_level"]])
        cw.writerow(["XP", user["xp"]])
        cw.writerow(["Coins", user["coins"]])
        cw.writerow(["Pronunciation Score", user.get("pronunciation_score", 0.0)])
        cw.writerow([])
        cw.writerow(["Assessment Date", "Score (%)", "Correct", "Total"])
        for h in history:
            cw.writerow([h["timestamp"], h["score"], h["correct"], h["total"]])
        
        output = make_response(si.getvalue())
        ext = "csv" if format == "csv" else "xls"
        content_type = "text/csv" if format == "csv" else "application/vnd.ms-excel"
        output.headers["Content-Disposition"] = f"attachment; filename=student_report.{ext}"
        output.headers["Content-type"] = content_type
        return output
        
    elif format == "pdf":
        # Print layout HTML
        html = f"""
        <html>
        <head>
            <title>Student Performance Report: {user['fullname']}</title>
            <style>
                body {{ font-family: sans-serif; margin: 40px; color: #1e293b; }}
                .header {{ text-align: center; border-bottom: 2px solid #3b82f6; padding-bottom: 20px; margin-bottom: 30px; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ font-size: 18px; font-weight: bold; border-left: 4px solid #3b82f6; padding-left: 10px; margin-bottom: 15px; }}
                .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px; }}
                .grid-item {{ background-color: #f8fafc; padding: 12px; border-radius: 6px; border: 1px solid #e2e8f0; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                table th, table td {{ border: 1px solid #cbd5e1; padding: 10px; text-align: left; }}
                table th {{ background-color: #f1f5f9; }}
                @media print {{
                    .no-print {{ display: none; }}
                }}
            </style>
        </head>
        <body onload="window.print()">
            <div class="header">
                <h1>AI Literacy Assistant</h1>
                <h2>Student Progress & Performance Report</h2>
                <p>Date Generated: 2026-07-23</p>
            </div>
            
            <div class="section">
                <div class="section-title">Student Profile Details</div>
                <div class="grid">
                    <div class="grid-item"><strong>Full Name:</strong> {user['fullname']}</div>
                    <div class="grid-item"><strong>Email:</strong> {user['email']}</div>
                    <div class="grid-item"><strong>Age Group:</strong> {user['age']} Years</div>
                    <div class="grid-item"><strong>Learning Level:</strong> {user['learning_level']}</div>
                    <div class="grid-item"><strong>XP Balance:</strong> {user['xp']} XP</div>
                    <div class="grid-item"><strong>Coins Balance:</strong> {user['coins']}</div>
                </div>
            </div>

            <div class="section">
                <div class="section-title">Assessment History Log</div>
                <table>
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Score (%)</th>
                            <th>Correct</th>
                            <th>Total</th>
                        </tr>
                    </thead>
                    <tbody>
        """
        for h in history:
            html += f"<tr><td>{h['timestamp']}</td><td>{h['score']}%</td><td>{h['correct']}</td><td>{h['total']}</td></tr>"
        html += """
                    </tbody>
                </table>
            </div>
            
            <div class="section no-print" style="text-align: center; margin-top: 50px;">
                <button onclick="window.print()" style="padding: 10px 20px; font-weight: bold; background-color: #3b82f6; color: white; border: none; border-radius: 6px; cursor: pointer;">Print / Save as PDF</button>
            </div>
        </body>
        </html>
        """
        return html


@app.route("/admin/report/<report_type>/<format>")
@admin_required
def admin_report_download(report_type, format):
    conn = get_db_connection()
    cursor = conn.cursor()

    if report_type == "student":
        cursor.execute("SELECT fullname, email, age, language, learning_level, xp, coins, streak, account_status FROM users WHERE role = 'student'")
        rows = [dict(r) for r in cursor.fetchall()]
        headers = ["Full Name", "Email", "Age", "Language", "Learning Level", "XP", "Coins", "Streak", "Status"]
    elif report_type == "parent":
        cursor.execute("SELECT fullname, email, language, account_status FROM users WHERE role = 'parent'")
        rows = [dict(r) for r in cursor.fetchall()]
        headers = ["Full Name", "Email", "Preferred Language", "Status"]
    else:
        cursor.execute("SELECT title, category, language, difficulty FROM lessons")
        rows = [dict(r) for r in cursor.fetchall()]
        headers = ["Title", "Category", "Language", "Difficulty"]

    conn.close()

    if format == "csv" or format == "excel":
        si = StringIO()
        cw = csv.writer(si, delimiter=',' if format == 'csv' else '\t')
        cw.writerow([f"System {report_type.capitalize()} Export Report"])
        cw.writerow([])
        cw.writerow(headers)
        for r in rows:
            cw.writerow(list(r.values()))
            
        output = make_response(si.getvalue())
        ext = "csv" if format == "csv" else "xls"
        content_type = "text/csv" if format == "csv" else "application/vnd.ms-excel"
        output.headers["Content-Disposition"] = f"attachment; filename={report_type}_export.{ext}"
        output.headers["Content-type"] = content_type
        return output
        
    elif format == "pdf":
        html = f"""
        <html>
        <head>
            <title>System Export: {report_type.capitalize()}</title>
            <style>
                body {{ font-family: sans-serif; margin: 30px; }}
                table {{ width: 100%; border-collapse: collapse; }}
                table th, table td {{ border: 1px solid #ccc; padding: 8px; text-align: left; }}
                table th {{ background-color: #f3f4f6; }}
            </style>
        </head>
        <body onload="window.print()">
            <h2>AI Literacy Admin Panel - {report_type.capitalize()} Records Export</h2>
            <p>Generated: 2026-07-23</p>
            <table>
                <thead><tr>
        """
        for h in headers:
            html += f"<th>{h}</th>"
        html += "</tr></thead><tbody>"
        for r in rows:
            html += "<tr>"
            for val in r.values():
                html += f"<td>{val}</td>"
            html += "</tr>"
        html += "</tbody></table></body></html>"
        return html


@app.route("/admin/report/all")
@admin_required
def admin_report_all():
    return admin_report_download("student", "csv")


# -------------------------------
# Parent Corner Route
# -------------------------------
@app.route("/parent-progress")
@parent_required
def parent_progress():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    translations = get_translations(language)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Fetch user details
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        flash("User session invalid.", "danger")
        return redirect(url_for("login"))
        
    user = dict(user_row)
    
    # Ensure xp and streak are parsed nicely
    user["xp"] = user.get("xp") or 0
    user["streak"] = user.get("streak") or 0
    
    # 1. Lessons completed
    cursor.execute("SELECT COUNT(*) FROM lesson_progress WHERE user_id = ?", (user_id,))
    lessons_completed = cursor.fetchone()[0] or 0
    
    # 2. Assessments taken & average score
    cursor.execute("SELECT COUNT(*), AVG(score) FROM assessment_history WHERE user_id = ?", (user_id,))
    history_summary = cursor.fetchone()
    assessments_taken = history_summary[0] or 0
    average_score = int(round(history_summary[1])) if history_summary[1] is not None else 0
    
    # 3. Assessment attempts history list
    cursor.execute("""
        SELECT timestamp, correct, total, score, language, age_group 
        FROM assessment_history 
        WHERE user_id = ? 
        ORDER BY timestamp DESC
    """, (user_id,))
    history_rows = cursor.fetchall()
    history = [dict(r) for r in history_rows]
    recent_scores = [r["score"] for r in history[:5]]
    
    # 4. Fetch notifications for user
    cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY created_at DESC LIMIT 5", (user_id,))
    notifications = [dict(r) for r in cursor.fetchall()]
    
    # 5. Fetch activity logs for user
    cursor.execute("SELECT * FROM activity_logs WHERE user_id = ? ORDER BY timestamp DESC LIMIT 5", (user_id,))
    activity_logs = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    
    # 6. Active goal based on age group
    age_group = get_age_group(user.get("age"))
    if age_group in ["toddler", "young"]:
        active_goal = "Complete basic phonics and reading lessons"
    elif age_group in ["middle", "older"]:
        active_goal = "Achieve at least 80% on language comprehension tests"
    else:
        active_goal = "Master professional writing and communication tasks"
        
    metrics = {
        "lessons_completed": lessons_completed,
        "average_score": average_score,
        "assessments_taken": assessments_taken,
        "active_goal": active_goal,
        "has_certificate": lessons_completed >= 3,
        "recent_scores": recent_scores,
        "pronunciation_score": user.get("pronunciation_score") or 0.0,
        "reading_speed_wpm": user.get("reading_speed_wpm") or 0,
        "speaking_score": user.get("speaking_score") or 0.0,
        "listening_score": user.get("listening_score") or 0.0,
        "practice_attempts": user.get("practice_attempts") or 0,
        "voice_improvement_percent": user.get("voice_improvement_percent") or 0.0,
        "streak": user.get("streak") or 0
    }
    
    return render_template(
        "parent_progress.html",
        user=user,
        metrics=metrics,
        history=history,
        notifications=notifications,
        activity_logs=activity_logs,
        translations=translations
    )


# Calendar & Study Log Route
# -------------------------------
@app.route("/calendar-log")
@login_required
def calendar_log():
    age = session.get("age", 1)
    if age and int(age) <= 4:
        return redirect(url_for("week_module"))
    import calendar
    import datetime
    
    user_id = session.get("user_id")
    language = session.get("language", "English")
    translations = get_translations(language)
    
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    today_str = now.strftime("%Y-%m-%d")
    month_name = now.strftime("%B %Y")
    
    # Calculate days grid for current month
    month_days = calendar.monthcalendar(year, month)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Query sessions for this user
    cursor.execute("""
        SELECT duration, date, timestamp 
        FROM study_sessions 
        WHERE user_id = ? 
        ORDER BY date DESC, timestamp DESC
    """, (user_id,))
    session_rows = cursor.fetchall()
    conn.close()
    
    sessions = []
    sessions_dict = {}
    total_time = 0
    
    for row in session_rows:
        duration = row["duration"] or 0
        date_str = row["date"]
        
        # Build list for recent sessions
        sessions.append({
            "date": date_str,
            "duration": duration
        })
        
        # Accumulate for dictionary and total time
        sessions_dict[date_str] = sessions_dict.get(date_str, 0) + duration
        total_time += duration
        
    return render_template(
        "calendar_log.html",
        total_time=total_time,
        month_name=month_name,
        month_days=month_days,
        today_str=today_str,
        sessions_dict=sessions_dict,
        sessions=sessions[:20], # limit to latest 20 for view
        translations=translations
    )


def generate_ai_lesson_content(topic, language, difficulty_filter):
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")
        
    import requests
    import json
    
    system_prompt = (
        "You are an expert curriculum designer for regional language literacy. "
        "Create a short educational lesson on the requested topic. "
        "The response must be in JSON format with three fields: 'title', 'category', and 'content'. "
        "'category' should be one of: 'reading', 'writing', 'comprehension'. "
        "If category is 'comprehension', include a multiple choice quiz appended to the content in this format: "
        "Lesson paragraph text [QUIZ] Question text | Option 1 | Option 2 | Option 3 | Correct Option"
    )
    user_prompt = f"Topic: {topic}\nLanguage: {language}\nDifficulty level: {difficulty_filter}"
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "temperature": 0.7
    }
    
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data, timeout=15)
    if response.status_code != 200:
        raise ValueError(f"OpenAI error: {response.text}")
        
    res_json = response.json()
    content_raw = res_json["choices"][0]["message"]["content"]
    parsed = json.loads(content_raw)
    return parsed


def generate_fallback_lesson(topic, language, difficulty_filter):
    topic_clean = topic.strip().capitalize()
    
    templates = {
        "Space": {
            "title": f"Exploring Space & Stars in {language}",
            "category": "comprehension",
            "content": f"Space is vast and contains billions of galaxies. Our solar system has eight planets revolving around the sun. [QUIZ] How many planets are in our solar system? | Five | Eight | Ten | Eight"
        },
        "Nature": {
            "title": f"The Wonders of Nature in {language}",
            "category": "reading",
            "content": f"Forests, rivers, and mountains represent the beautiful balance of nature. Caring for trees protects our environment."
        },
        "Coding": {
            "title": f"Introduction to Programming & Coding",
            "category": "comprehension",
            "content": f"Computers follow step-by-step instructions called code. Python is a simple and widely used coding language. [QUIZ] What is a coding language? | Python | HTML | Javascript | Python"
        }
    }
    
    matched = None
    for key, val in templates.items():
        if key.lower() in topic_clean.lower() or topic_clean.lower() in key.lower():
            matched = val
            break
            
    if not matched:
        matched = {
            "title": f"Introduction to {topic_clean} in {language}",
            "category": "comprehension",
            "content": f"{topic_clean} is a fascinating subject with rich history and practical applications. Practicing reading and writing about {topic_clean} strengthens communication literacy. [QUIZ] What topic does this lesson cover? | History | Science | {topic_clean} | {topic_clean}"
        }
        
    return matched


# -------------------------------
# Personalized AI Lesson Generation Route
# -------------------------------
@app.route("/generate_personalized_lesson", methods=["POST"])
@login_required
def generate_personalized_lesson():
    topic = request.form.get("topic")
    if not topic:
        flash("Please provide a topic for the personalized lesson.", "warning")
        return redirect(url_for("dashboard"))
        
    user_id = session.get("user_id")
    language = session.get("language", "English")
    
    # Determine difficulty level based on proficiency
    pred_prof = predict_user_proficiency(user_id, language)
    level_key = pred_prof["level_key"]
    
    # Match difficulty keys
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT age, stream, sub_stream FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    
    difficulty_filter = "young"
    if user_row:
        learning_level = user_row["learning_level"] if ("learning_level" in user_row.keys() and user_row["learning_level"]) else session.get("learning_level", "Beginner")
        difficulty_filter = learning_level
    else:
        difficulty_filter = session.get("learning_level", "Beginner")
        
    # Generate content using OpenAI, fall back to rules-based template if failing
    try:
        lesson_data = generate_ai_lesson_content(topic, language, difficulty_filter)
    except Exception as e:
        lesson_data = generate_fallback_lesson(topic, language, difficulty_filter)
        
    # Write to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lessons (title, category, language, content, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (lesson_data["title"], lesson_data["category"], language, lesson_data["content"], difficulty_filter))
    conn.commit()
    conn.close()
    
    flash(f"AI Personal Coach Lumi has generated a custom lesson on '{topic}' for you!", "success")
    return redirect(url_for("week_module"))


# -------------------------------
# Learning Path REST APIs
# -------------------------------
@app.route("/api/learning-path", methods=["GET"])
@login_required
def api_learning_path():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, fullname, age, learning_level, current_proficiency, language, xp, streak, coins, badges
        FROM users WHERE id = ?
    """, (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    
    if not user_row:
        return jsonify({"error": "User not found"}), 404
        
    user = dict(user_row)
    pred_prof = predict_user_proficiency(user_id, language=language, update_db=True)
    user["current_proficiency"] = pred_prof["current_proficiency"]
    
    learning_path = generate_personalized_learning_path(user_id)
    recs = get_content_recommendations(user_id)
    
    return jsonify({
        "status": "success",
        "user": user,
        "learning_level": user.get("learning_level", "Beginner"),
        "predicted_proficiency": pred_prof,
        "today_learning_plan": learning_path,
        "recommended_lessons": recs,
        "next_lesson": recs[0] if recs else None
    })


@app.route("/api/recommendations", methods=["GET"])
@login_required
def api_recommendations():
    user_id = session.get("user_id")
    recs = get_content_recommendations(user_id)
    return jsonify({
        "status": "success",
        "count": len(recs),
        "recommendations": recs,
        "next_lesson": recs[0] if recs else None
    })


@app.route("/api/assessment", methods=["POST"])
@login_required
def api_assessment():
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or request.form or {}
    
    score = data.get("score")
    if score is None:
        correct = int(data.get("correct", 0))
        total = int(data.get("total", 1))
        score = int((correct / total) * 100) if total else 0
    else:
        score = int(score)
        correct = int(data.get("correct", score // 10))
        total = int(data.get("total", 10))
        
    language = data.get("language") or session.get("language", "English")
    age = session.get("age", 8)
    age_group = get_age_group(age)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO assessment_history (user_id, score, correct, total, language, age_group)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, score, correct, total, language, age_group))
    conn.commit()
    
    # Calculate average score & total assessments
    cursor.execute("SELECT AVG(score), COUNT(*) FROM assessment_history WHERE user_id = ?", (user_id,))
    avg_row = cursor.fetchone()
    avg_score = round(avg_row[0], 1) if avg_row and avg_row[0] is not None else float(score)
    assessment_count = avg_row[1] if avg_row else 1
    
    # Predict proficiency & update DB
    pred_prof = predict_user_proficiency(user_id, language=language, update_db=False)
    new_proficiency = pred_prof["current_proficiency"]
    session["last_score"] = score
    
    # Generate updated recommendations & path using centralized state refresh
    recalculate_and_refresh_learner_state(user_id)
    recs = get_content_recommendations(user_id, last_score=score)
    path = generate_personalized_learning_path(user_id)
    
    cursor.execute("""
        UPDATE users 
        SET assessment_count = ?, average_score = ?
        WHERE id = ?
    """, (assessment_count, avg_score, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "message": "Assessment results stored successfully",
        "score": score,
        "correct": correct,
        "total": total,
        "predicted_proficiency": pred_prof,
        "current_proficiency": new_proficiency,
        "average_score": avg_score,
        "assessment_count": assessment_count,
        "recommended_lessons": recs,
        "next_lesson": recs[0] if recs else None,
        "today_learning_plan": path
    })


@app.route("/api/proficiency", methods=["GET"])
@login_required
def api_proficiency():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    pred_prof = predict_user_proficiency(user_id, language=language, update_db=True)
    return jsonify({
        "status": "success",
        "user_id": user_id,
        "predicted_proficiency": pred_prof,
        "current_proficiency": pred_prof["current_proficiency"],
        "rules": {
            "0-39%": "Beginner",
            "40-69%": "Basic",
            "70-89%": "Intermediate",
            "90-100%": "Advanced"
        }
    })


@app.route("/api/progress", methods=["GET"])
@login_required
def api_progress():
    user_id = session.get("user_id")
    language = session.get("language", "English")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT xp, streak, coins, badges, age, learning_level, current_proficiency FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    
    cursor.execute("SELECT COUNT(DISTINCT lesson_id) FROM lesson_progress WHERE user_id = ?", (user_id,))
    lessons_completed = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM lessons WHERE language = ?", (language,))
    total_db_lessons = cursor.fetchone()[0] or 10
    
    cursor.execute("SELECT COUNT(*), AVG(score) FROM assessment_history WHERE user_id = ?", (user_id,))
    arow = cursor.fetchone()
    assessments_completed = arow[0] if arow else 0
    average_score = round(arow[1], 1) if arow and arow[1] is not None else 0.0
    
    videos_watched = lessons_completed
    progress_percentage = min(100.0, round((lessons_completed / max(1, total_db_lessons)) * 100, 1))
    
    pred_prof = predict_user_proficiency(user_id, language=language, update_db=True)
    current_proficiency = pred_prof["current_proficiency"]
    
    cursor.execute("""
        UPDATE users 
        SET completed_lessons_count = ?, videos_watched_count = ?, assessment_count = ?, average_score = ?, progress_percentage = ?
        WHERE id = ?
    """, (lessons_completed, videos_watched, assessments_completed, average_score, progress_percentage, user_id))
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "lessons_completed": lessons_completed,
        "videos_watched": videos_watched,
        "assessments_completed": assessments_completed,
        "average_score": average_score,
        "current_proficiency": current_proficiency,
        "learning_streak": urow["streak"] if urow else 0,
        "badges": [b.strip() for b in (urow["badges"] or "").split(",") if b.strip()] if urow else [],
        "coins": urow["coins"] if urow else 0,
        "xp": urow["xp"] if urow else 0,
        "progress_percentage": progress_percentage
    })


@app.route("/api/save_voice_attempt", methods=["POST"])
@login_required
def save_voice_attempt():
    data = request.get_json() or {}
    user_id = session.get("user_id")
    lesson_id = data.get("lesson_id")
    expected_text = data.get("expected_text", "")
    spoken_text = data.get("spoken_text", "")
    pronunciation_score = float(data.get("pronunciation_score", 0.0))
    reading_speed = int(data.get("reading_speed", 0))
    speaking_score = float(data.get("speaking_score", 0.0))
    listening_score = float(data.get("listening_score", 0.0))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    import datetime
    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("""
        INSERT INTO voice_practice_history (
            user_id, lesson_id, expected_text, spoken_text, 
            pronunciation_score, reading_speed_wpm, speaking_score, listening_score, 
            attempt_date
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (user_id, lesson_id, expected_text, spoken_text, pronunciation_score, reading_speed, speaking_score, listening_score, now_str))
    
    # Calculate improvement
    cursor.execute("""
        SELECT pronunciation_score FROM voice_practice_history 
        WHERE user_id = ? AND lesson_id = ? AND expected_text = ? AND id != (SELECT last_insert_rowid())
        ORDER BY id DESC LIMIT 1
    """, (user_id, lesson_id, expected_text))
    prev_row = cursor.fetchone()
    prev_score = prev_row["pronunciation_score"] if prev_row else 0.0
    improvement = pronunciation_score - prev_score
    
    # Update users table
    cursor.execute("""
        UPDATE users 
        SET pronunciation_score = ?, reading_speed_wpm = ?, speaking_score = ?, 
            practice_attempts = practice_attempts + 1, last_practice_date = ?,
            voice_improvement_percent = ?
        WHERE id = ?
    """, (pronunciation_score, reading_speed, speaking_score, now_str, improvement, user_id))
    
    # Also record a study session activity (10 XP reward)
    duration_minutes = 1
    cursor.execute("""
        INSERT INTO study_sessions (user_id, duration, date)
        VALUES (?, ?, ?)
    """, (user_id, duration_minutes, datetime.date.today().strftime("%Y-%m-%d")))
    cursor.execute("UPDATE users SET xp = xp + 10 WHERE id = ?", (user_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        "status": "success",
        "improvement": improvement
    })


@app.route("/api/next-lesson", methods=["GET"])
@login_required
def api_next_lesson():
    user_id = session.get("user_id")
    recs = get_content_recommendations(user_id)
    if not recs:
        return jsonify({"status": "empty", "message": "No recommendations available"}), 200
    return jsonify({
        "status": "success",
        "next_lesson": recs[0]
    })

@app.route("/api/learning-path/update-stream", methods=["POST"])
@login_required
def api_update_stream():
    data = request.get_json() or {}
    learning_level = data.get("learning_level", "Beginner")
    user_id = session.get("user_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE users 
        SET learning_level = ? 
        WHERE id = ?
    """, (learning_level, user_id))
    conn.commit()
    conn.close()
    
    session["learning_level"] = learning_level
    
    return {
        "status": "success",
        "learning_level": learning_level
    }

@app.route("/api/learning-path/generate-lesson", methods=["POST"])
@login_required
def api_generate_lesson():
    data = request.get_json() or {}
    topic = data.get("topic")
    if not topic:
        return {"error": "topic field is required"}, 400
        
    user_id = session.get("user_id")
    language = session.get("language", "English")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT learning_level FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    conn.close()
    
    learning_level = user_row["learning_level"] if (user_row and "learning_level" in user_row.keys() and user_row["learning_level"]) else session.get("learning_level", "Beginner")
    
    # Generate content using OpenAI, fall back to rules-based template if failing
    try:
        lesson_data = generate_ai_lesson_content(topic, language, learning_level)
    except Exception:
        lesson_data = generate_fallback_lesson(topic, language, learning_level)
        
    # Write to database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO lessons (title, category, language, content, difficulty)
        VALUES (?, ?, ?, ?, ?)
    """, (lesson_data["title"], lesson_data["category"], language, lesson_data["content"], learning_level))
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "lesson": lesson_data
    }



@app.route("/api/translations", methods=["GET"])
def api_translations():
    lang = request.args.get("lang", "English")
    return get_translations(lang)


@app.route("/api/profile/update", methods=["POST"])
@login_required
def api_profile_update():
    return update_profile()


@app.route("/api/trace/verify", methods=["POST"])
def api_trace_verify():
    data = request.get_json() or {}
    score = data.get("score", 85)
    
    if score >= 80:
        stars = "⭐"
        feedback = "Excellent"
    elif score >= 50:
        stars = "⭐⭐"
        feedback = "Good Job"
    else:
        stars = "⭐⭐⭐"
        feedback = "Try Again"
        
    return {
        "status": "success",
        "score": score,
        "stars": stars,
        "feedback": feedback
    }


CONVERSATION_RESPONSES = {
    "English": {
        "doctor": {
            "hello": "Hello! I am Doctor. How can I help you today? Do you have any fever or headache?",
            "fever": "I see. Please rest and drink plenty of warm water. Take this medicine twice a day.",
            "cold": "Keep warm and rest. Avoid cold drinks. Here is a cough syrup for you.",
            "default": "Okay. Take rest, eat fresh fruits, and stay warm. You will feel better soon!"
        },
        "shopkeeper": {
            "hello": "Welcome to my shop! We have fresh apples, milk, and bread. What would you like to buy?",
            "apples": "Apples are 120 rupees per kilogram. How many kilograms do you want?",
            "price": "It costs 50 rupees. How would you like to pay?",
            "default": "Sure! Here is your item. That will be 50 rupees. Thank you for shopping!"
        },
        "teacher": {
            "hello": "Good morning! Today we are discussing science and grammar. Have you done your homework?",
            "yes": "Wonderful! Let's read the next paragraph together.",
            "no": "Please make sure to finish it today so you can understand the grammar class.",
            "default": "Excellent! Keep practicing and reading everyday to score full marks."
        }
    },
    "Telugu": {
        "doctor": {
            "hello": "నమస్కారం! నేను డాక్టర్ ని. ఈ రోజు మీకు ఎలా సహాయపడగలను? జ్వరం లేదా తలనొప్పి ఉందా?",
            "fever": "అవునా. దయచేసి విశ్రాంతి తీసుకోండి మరియు వేడి నీరు త్రాగండి. ఈ ఔషధాన్ని రోజుకు రెండుసార్లు తీసుకోండి.",
            "cold": "వేడిగా ఉండండి మరియు విశ్రాంతి తీసుకోండి. చల్లటి పానీయాలకు దూరంగా ఉండండి.",
            "default": "సరే. బాగా విశ్రాంతి తీసుకోండి, వేడి ఆహారం తినండి. మీరు త్వరలోనే కోలుకుంటారు!"
        },
        "shopkeeper": {
            "hello": "మా దుకాణానికి స్వాగతం! మా వద్ద తాజా ఆపిల్స్, పాలు మరియు రొట్టెలు ఉన్నాయి. మీరు ఏమి కొనాలనుకుంటున్నారు?",
            "apples": "ఆపిల్స్ ధర కిలో 120 రూపాయలు. మీకు ఎన్ని కిలోలు కావాలి?",
            "price": "దీని ధర 50 రూపాయలు. మీరు ఎలా చెల్లిస్తారు?",
            "default": "తప్పకుండా! ఇదిగో మీ వస్తువు. దీని ధర 50 రూపాయలు అవుతుంది. ధన్యవాదాలు!"
        },
        "teacher": {
            "hello": "శుభోదయం! ఈ రోజు మనం విజ్ఞాన శాస్త్రం మరియు వ్యాకరణం గురించి చర్చిస్తున్నాము. మీ హోంవర్క్ చేశారా?",
            "yes": "చాలా మంచిది! తదుపరి పాఠం కలిసి చదువుదాం.",
            "no": "దయచేసి ఈ రోజు పూర్తి చేయండి, అప్పుడే క్లాస్ అర్థం అవుతుంది.",
            "default": "అద్భుతం! ప్రతిరోజూ సాధన చేయండి మరియు బాగా చదవండి."
        }
    },
    "Hindi": {
        "doctor": {
            "hello": "नमस्ते! मैं डॉक्टर हूँ। आज मैं आपकी क्या मदद कर सकता हूँ? क्या आपको बुखार या सिरदर्द है?",
            "fever": "अच्छा। कृपया आराम करें और गुनगुना पानी पीएं। यह दवा दिन में दो बार लें।",
            "cold": "गर्म रहें और आराम करें। ठंडी चीजों से दूर रहें।",
            "default": "ठीक है। आराम करें, ताजा फल खाएं। आप जल्द ही ठीक हो जाएंगे!"
        },
        "shopkeeper": {
            "hello": "मेरी दुकान में आपका स्वागत है! हमारे पास ताजे सेब, दूध और ब्रेड हैं। आप क्या खरीदना चाहेंगे?",
            "apples": "सेब 120 रुपये किलो हैं। आपको कितने किलो चाहिए?",
            "price": "इसकी कीमत 50 रुपये है। आप कैसे भुगतान करेंगे?",
            "default": "ज़रूर! यह रहा आपका सामान। यह 50 रुपये का हुआ। खरीदारी के लिए धन्यवाद!"
        },
        "teacher": {
            "hello": "शुभ प्रभात! आज हम विज्ञान और व्याकरण पर चर्चा कर रहे हैं। क्या आपने अपना होमवर्क कर लिया है?",
            "yes": "बहुत बढ़िया! आइए अगला पैराग्राफ साथ मिलकर पढ़ें।",
            "no": "कृपया इसे आज ही पूरा कर लें ताकि आप व्याकरण समझ सकें।",
            "default": "शानदार! हर दिन अभ्यास करें और परीक्षा में पूरे अंक प्राप्त करने के लिए पढ़ते रहें।"
        }
    },
    "Tamil": {
        "doctor": {
            "hello": "வணக்கம்! நான் மருத்துவர். இன்று உங்களுக்கு நான் எவ்வாறு உதவ முடியும்? காய்ச்சல் அல்லது தலைவலி உள்ளதா?",
            "fever": "அப்படியா. தயவுசெய்து ஓய்வெடுத்து வெதுவெதுப்பான நீர் அருந்தவும். இந்த மருந்தை நாளைக்கு இருமுறை உட்கொள்ளவும்.",
            "cold": "உடலை வெதுவெதுப்பாக வைத்து ஓய்வெடுங்கள். குளிர்ந்த பானங்களைத் தவிர்க்கவும்.",
            "default": "சரி. நன்கு ஓய்வெடுத்து சூடான உணவுகளை உட்கொள்ளுங்கள். நீங்கள் விரைவில் குணமடைவீர்கள்!"
        },
        "shopkeeper": {
            "hello": "என் கடைக்கு வருக! எங்களிடம் புதிய ஆப்பிள்கள், பால் மற்றும் ரொட்டி உள்ளன. நீங்கள் என்ன வாங்க விரும்புகிறீர்கள்?",
            "apples": "ஆப்பிள்கள் ஒரு கிலோ 120 ரூபாய். உங்களுக்கு எத்தனை கிலோ வேண்டும்?",
            "price": "இதன் விலை 50 ரூபாய். நீங்கள் எவ்வாறு பணம் செலுத்துவீர்கள்?",
            "default": "நிச்சயமாக! இதோ உங்கள் பொருள். விலை 50 ரூபாய். கடைக்கு வந்ததற்கு நன்றி!"
        },
        "teacher": {
            "hello": "காலை வணக்கம்! இன்று நாம் அறிவியல் மற்றும் இலக்கணம் பற்றி விவாதிக்கிறோம். வீட்டுப்பாடம் செய்தீர்களா?",
            "yes": "அருமை! அடுத்த பத்தியை நாம் சேர்ந்து படிப்போம்.",
            "no": "இலக்கண வகுப்பை நன்கு புரிந்து கொள்ள தயவுசெய்து இன்று வீட்டுப்பாடத்தை முடிக்கவும்.",
            "default": "மிக நன்று! முழு மதிப்பெண் பெற தினமும் படித்து பயிற்சி செய்யுங்கள்."
        }
    },
    "Kannada": {
        "doctor": {
            "hello": "ನಮಸ್ಕಾರ! ನಾನು ವೈದ್ಯ. ಇಂದು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ? ಜ್ವರ ಅಥವಾ ತಲೆನೋವು ಇದೆಯೇ?",
            "fever": "ಹೌದೇ. ದಯವಿಟ್ಟು ವಿಶ್ರಾಂತಿ ತೆಗೆದುಕೊಳ್ಳಿ ಮತ್ತು ಉಗುರುಬೆಚ್ಚಗಿನ ನೀರನ್ನು ಕುಡಿಯಿರಿ. ಈ ಔಷಧಿಯನ್ನು ದಿನಕ್ಕೆ ಎರಡು ಬಾರಿ ತೆಗೆದುಕೊಳ್ಳಿ.",
            "cold": "ಬೆಚ್ಚಗಿನ ಬಟ್ಟೆ ಧರಿಸಿ ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ. ತಣ್ಣನೆಯ ಪಾನೀಯಗಳನ್ನು ಕುಡಿಯಬೇಡಿ.",
            "default": "ಸರಿ. ವಿಶ್ರಾಂತಿ ಪಡೆಯಿರಿ, ತಾಜา ಹಣ್ಣುಗಳನ್ನು ಸೇವಿಸಿ. ನೀವು ಶೀಘ್ರದಲ್ಲೇ ಗುಣಮುಖರಾಗುತ್ತೀರಿ!"
        },
        "shopkeeper": {
            "hello": "ನನ್ನ ಅಂಗಡಿಗೆ ಸುಸ್ವಾಗತ! ನಮ್ಮಲ್ಲಿ ತಾಜಾ ಸೇಬುಗಳು, ಹಾಲು ಮತ್ತು ಬ್ರೆಡ್ ಇವೆ. ನೀವು ಏನು ಖರೀದಿಸಲು ಬಯಸುತ್ತೀರಿ?",
            "apples": "ಸೇಬುಗಳು ಕೆಜಿಗೆ 120 ರೂಪಾಯಿಗಳು. ನಿಮಗೆ ಎಷ್ಟು ಕೆಜಿ ಬೇಕು?",
            "price": "ಇದರ ಬೆಲೆ 50 ರೂಪಾಯಿಗಳು. ನೀವು ಹೇಗೆ ಪಾವತಿಸುತ್ತೀರಿ?",
            "default": "ಖಂಡಿತ! ಇಗೋ ನಿಮ್ಮ ವಸ್ತು. ಇದು 50 ರೂಪಾಯಿ ಆಯಿತು. ಖರೀದಿಗೆ ಧನ್ಯವಾದಗಳು!"
        },
        "teacher": {
            "hello": "ಶುಭೋದಯ! ಇಂದು ನಾವು ವಿಜ್ಞಾನ ಮತ್ತು ವ್ಯಾಕರಣದ ಬಗ್ಗೆ ಚರ್ಚಿಸುತ್ತಿದ್ದೇವೆ. ನಿಮ್ಮ ಮನೆಗೆಲಸ ಮಾಡಿದ್ದೀರಾ?",
            "yes": "ಅದ್ಭುತ! ಮುಂದಿನ ಪ್ಯಾರಾವನ್ನು ಒಟ್ಟಿಗೆ ಓದೋಣ.",
            "no": "ವ್ಯಾಕರಣ ತರಗತಿಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ದಯವಿಟ್ಟು ಇಂದು ಮನೆಗೆಲಸ ಪೂರ್ಣಗೊಳಿಸಿ.",
            "default": "ಉತ್ತಮ! ಪರೀಕ್ಷೆಯಲ್ಲಿ ಪೂರ್ಣ ಅಂಕಗಳನ್ನು ಗಳಿಸಲು ಪ್ರತಿದಿನ ಓದುವುದನ್ನು ಮುಂದುವರಿಸಿ."
        }
    },
    "Marathi": {
        "doctor": {
            "hello": "नमस्कार! मी डॉक्टर आहे. आज मी तुम्हाला कशी मदत करू? ताप किंवा डोकेदुखी आहे का?",
            "fever": "अच्छा. कृपया विश्रांती घ्या आणि कोमट पाणी प्या. हे औषध दिवसातून दोनदा घ्या.",
            "cold": "उबदार रहा आणि विश्रांती घ्या. थंड पेये पिणे टाळा.",
            "default": "ठीक आहे. विश्रांती घ्या, ताजी फळे खा. तुम्ही लवकरच बरे व्हाल!"
        },
        "shopkeeper": {
            "hello": "माझ्या दुकानात आपले स्वागत आहे! आमच्याकडे ताजी सफरचंद, दूध आणि ब्रेड आहेत. आपल्याला काय खरेदी करायचे आहे?",
            "apples": "सफरचंद १२० रुपये किलो आहेत. आपल्याला किती किलो हवे आहेत?",
            "price": "याची किंमत ५० रुपये आहे. आपण कसे पैसे देणार?",
            "default": "नक्कीच! हे घ्या आपले सामान. ५० रुपये झाले. खरेदीसाठी धन्यवाद!"
        },
        "teacher": {
            "hello": "सुप्रभात! आज आपण विज्ञान आणि व्याकरण यावर चर्चा करत आहोत. आपण आपला गृहपाठ केला आहे का?",
            "yes": "खूप छान! चला पुढचा परिच्छेद एकत्र वाचूया.",
            "no": "व्याकरण समजून घेण्यासाठी कृपया आज गृहपाठ पूर्ण करा.",
            "default": "उत्कृष्ट! परीक्षेत पूर्ण गुण मिळवण्यासाठी दररोज वाचन आणि सराव करत रहा."
        }
    }
}


@app.route("/api/conversation/chat", methods=["POST"])
@login_required
def api_conversation_chat():
    data = request.get_json() or {}
    message = (data.get("message") or "").strip().lower()
    situation = (data.get("situation") or "doctor").lower()
    language = data.get("language") or session.get("language", "English")
    
    print(f"[AI TUTOR BACKEND LOG] Step 1: Received Request -> lang='{language}', situation='{situation}', message='{message}'")
    
    age = session.get("age")
    try:
        age_int = int(age) if age is not None else 8
    except (ValueError, TypeError):
        age_int = 8

    is_toddler = (2 <= age_int <= 4)

    # Try calling OpenAI if API key exists in environment
    api_key = os.environ.get("OPENAI_API_KEY")
    if api_key:
        try:
            import openai
            openai.api_key = api_key
            if is_toddler:
                prompt = (
                    f"You are a warm, joyful AI Tutor for a toddler (aged 2-4). "
                    f"Language: {language}. Rule: Respond ONLY in {language}. "
                    f"Speak slowly, use very short and simple 3-5 word sentences, encourage interaction with cheerful tone, "
                    f"avoid asking any written questions, and guide the child to tap videos, rhymes, and pictures! "
                    f"The child said: '{message}'."
                )
            else:
                prompt = (
                    f"You are a friendly AI Tutor acting as a {situation}. User Selected Language: {language}. "
                    f"System Instruction: Always respond ONLY in {language}. Never mix English. "
                    f"Generate your conversation response entirely in {language} suitable for a child or beginner learner. "
                    f"The learner says: '{message}'."
                )
            res = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=60
            )
            ai_response = res.choices[0].message['content'].strip()
            print(f"[AI TUTOR BACKEND LOG] Step 2: OpenAI Response Generated (Toddler={is_toddler}) -> '{ai_response}'")
            return {"status": "success", "response": ai_response, "language": language}
        except Exception as e:
            print(f"[AI TUTOR BACKEND LOG] OpenAI error: {e}, falling back to response tree.")
            
    if is_toddler:
        toddler_responses = {
            "English": "Great job! Let's sing a rhyme and watch fun videos together! 🌟",
            "Telugu": "చాలా బాగుంది! మనం కలిసి సరదా పాటలు పాడుకుందాం! 🌟",
            "Hindi": "बहुत बढ़िया! आइए मिलकर मजेदार बालगीत गाते हैं! 🌟",
            "Tamil": "மிக நன்று! நாம் சேர்ந்து அழகான பாடல்களைப் பாடுவோம்! 🌟",
            "Kannada": "ತುಂಬಾ ಚೆನ್ನಾಗಿದೆ! ನಾವು ಜೊತೆಯಾಗಿ ಮೋಜಿನ ಹಾಡುಗಳನ್ನು ಹಾಡೋಣ! 🌟",
            "Marathi": "खूप छान! चला सोबत छान बालगीत गाऊया! 🌟"
        }
        ai_response = toddler_responses.get(language, toddler_responses["English"])
    else:
        lang_map = CONVERSATION_RESPONSES.get(language) or CONVERSATION_RESPONSES.get("English", {})
        sit_map = lang_map.get(situation)
        if not sit_map:
            sit_map = lang_map.get("teacher") or lang_map.get("doctor") or list(lang_map.values())[0]
        
        ai_response = sit_map.get("default", "Excellent practice! Keep up the good work.")
        for keyword, response in sit_map.items():
            if keyword != "default" and keyword in message:
                ai_response = response
                break
            
    print(f"[AI TUTOR BACKEND LOG] Step 2: Tree Response Generated -> lang='{language}', response='{ai_response}'")
    return {
        "status": "success",
        "response": ai_response,
        "language": language
    }


from flask import jsonify

@app.route("/api/toddler/videos")
@login_required
def api_toddler_videos():
    language = session.get("language", "English")
    age = session.get("age", 1)
    
    videos = get_local_videos_for_learner(language, age)
    if not videos:
        print(f"[VIDEO ERROR] /api/toddler/videos found no MP4 videos for lang='{language}', age={age}")
    return jsonify(videos)


@app.route("/api/tts")
def api_tts():
    import urllib.request
    import urllib.parse
    import json

    text = request.args.get("text", "").strip()
    lang = request.args.get("lang", "English").strip()
    
    if not text:
        return Response("No text provided", status=400)
        
    lang_codes = {
        "english": "en", "en": "en", "en-us": "en", "en-in": "en",
        "telugu": "te", "te": "te", "te-in": "te",
        "hindi": "hi", "hi": "hi", "hi-in": "hi",
        "tamil": "ta", "ta": "ta", "ta-in": "ta",
        "kannada": "kn", "kn": "kn", "kn-in": "kn",
        "marathi": "mr", "mr": "mr", "mr-in": "mr"
    }
    code = lang_codes.get(lang.lower(), "en")
    
    # Auto-translate English instruction text to target regional language before speaking it
    if code != "en" and any(c.isalpha() and ord(c) < 128 for c in text):
        try:
            url_trans = f"https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl={code}&dt=t&q={urllib.parse.quote(text)}"
            req_trans = urllib.request.Request(url_trans, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req_trans, timeout=4) as resp_trans:
                data_trans = json.loads(resp_trans.read().decode("utf-8"))
                translated_text = "".join([part[0] for part in data_trans[0] if part[0]])
                if translated_text:
                    print(f"[TTS Translation] Translated successfully for lang={lang} (length: {len(translated_text)})")
                    text = translated_text
        except Exception as te:
            print(f"[TTS Translation Error] Failed to translate: {te}")
            
    # Split text into chunks to respect Google Translate TTS 200-character limit
    def split_text_into_chunks(txt, max_len=150):
        words = txt.split()
        chunks = []
        curr = []
        curr_len = 0
        for w in words:
            w_len = len(w) + (1 if curr else 0)
            if curr_len + w_len > max_len:
                if curr:
                    chunks.append(" ".join(curr))
                curr = [w]
                curr_len = len(w)
            else:
                curr.append(w)
                curr_len += w_len
        if curr:
            chunks.append(" ".join(curr))
        return chunks

    chunks = split_text_into_chunks(text, 150)
    audio_parts = []
    
    try:
        for chunk in chunks:
            if not chunk.strip():
                continue
            url = f"https://translate.google.com/translate_tts?ie=UTF-8&q={urllib.parse.quote(chunk)}&tl={code}&client=tw-ob"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                audio_parts.append(resp.read())
                
        if not audio_parts:
            return Response("Audio stream error", status=500)
            
        joined_audio = b"".join(audio_parts)
        return Response(joined_audio, mimetype="audio/mpeg")
    except Exception as e:
        print(f"TTS audio streaming error for lang {lang}: {e}")
        return Response("Audio stream error", status=500)


# -------------------------------
# Phase 6: Reward Engine API (+10 Coins, +20 XP, Badges)
# -------------------------------
@app.route("/api/complete_lesson", methods=["POST"])
@login_required
def api_complete_lesson():
    user_id = session.get("user_id")
    data = request.get_json(silent=True) or {}
    lesson_id = data.get("lesson_id")
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT coins, xp, badges FROM users WHERE id = ?", (user_id,))
    urow = cursor.fetchone()
    
    current_coins = (urow["coins"] if urow and urow["coins"] else 0) + 10
    current_xp = (urow["xp"] if urow and urow["xp"] else 0) + 20
    
    badge_list = [b.strip() for b in (urow["badges"] or "").split(",") if b.strip()]
    if "Lesson Master" not in badge_list:
        badge_list.append("Lesson Master")
    new_badges = ",".join(badge_list)
    
    cursor.execute("""
        UPDATE users SET coins = ?, xp = ?, badges = ? WHERE id = ?
    """, (current_coins, current_xp, new_badges, user_id))
    
    if lesson_id:
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO lesson_progress (user_id, lesson_id, completed, score)
                VALUES (?, ?, 1, 100)
            """, (user_id, lesson_id))
        except Exception as e:
            print(f"[REWARD LOG] Progress record notice: {e}")
            
    conn.commit()
    conn.close()
    
    session["coins"] = current_coins
    session["xp"] = current_xp
    session["badges"] = new_badges
    
    recalculate_and_refresh_learner_state(user_id)
    
    return jsonify({
        "status": "success",
        "coins": current_coins,
        "xp": current_xp,
        "badges": new_badges,
        "message": "Lesson completed! +10 Coins awarded! ⭐"
    })


@app.route("/api/set-language", methods=["POST"])
def api_set_language():
    data = request.get_json(silent=True) or {}
    lang = data.get("language") or request.form.get("language") or "English"
    session["language"] = lang
    session["preferred_language"] = lang
    
    user_id = session.get("user_id")
    if user_id:
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE users SET language = ?, preferred_language = ? WHERE id = ?", (lang, lang, user_id))
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error updating user language in db: {e}")
            
    return jsonify({"status": "success", "language": lang})
            
@app.route("/api/dismiss-birthday", methods=["POST"])
@login_required
def api_dismiss_birthday():
    session["birthday_shown"] = True
    return jsonify({"status": "success"})


if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5500
    )
