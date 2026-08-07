import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

# Define the new get_assessment_questions function
new_function = """def get_assessment_questions(language, age=None, learning_level=None, mode=None):
    try:
        age_val = int(age) if age is not None else session.get("age", 8)
    except (ValueError, TypeError):
        age_val = 8

    if not learning_level:
        learning_level = session.get("learning_level", "Beginner")
    lvl = str(learning_level).capitalize()

    def build_15_questions(lang, age_num, level_str):
        questions = []
        if lang == "Telugu":
            # 6 skills structured questions for Telugu (exactly 15)
            # Reading Skills
            questions.append({"name": "q1", "type": "reading", "prompt": "అక్షర గుర్తింపు: వర్ణమాలలో మొదటి అక్షరం ఏది?", "options": ["అ", "ఆ", "ఇ", "ఈ"], "answer": "అ", "explanation": "అ అనేది వర్ణమాలలో మొదటి అక్షరం."})
            questions.append({"name": "q2", "type": "reading", "prompt": "పద పఠనం: ఈ చిత్రం దేనికి సంబంధించినది? 🍎", "options": ["ఆపిల్", "పిల్లి", "కుక్క", "ఆవు"], "answer": "ఆపిల్", "explanation": "ఇ定ఆపిల్ పండు."})
            questions.append({"name": "q3", "type": "reading", "prompt": "రీడింగ్ కాంప్రహెన్షన్: 'పిల్లి పాలు తాగింది' - ఇందులో ఎవరు పాలు తాగారు?", "options": ["పిల్లి", "పాలు", "కుక్క", "ఎలుక"], "answer": "పిల్లి", "explanation": "పిల్లి పాలు తాగింది అని వాక్యం చెబుతోంది."})
            # Writing Skills
            questions.append({"name": "q4", "type": "writing", "prompt": "ఖాళీలను నింపండి: అ _ మ (తల్లి)", "options": ["మ్మ", "క్క", "ల్ల", "య్య"], "answer": "మ్మ", "explanation": "అమ్మ అనేది సరైన పదం."})
            questions.append({"name": "q5", "type": "writing", "prompt": "పదాల అమరిక: సరైన అక్షరాన్ని నింపండి: ఆ ప _ లు", "options": ["లి", "కి", "మి", "రి"], "answer": "లి", "explanation": "ఆపిలు."})
            questions.append({"name": "q6", "type": "writing", "prompt": "వాక్య ముగింపు: 'మేము బడికి _________.'", "options": ["వెళ్తాము", "వెళ్లి", "వెళ్లాడు", "వెళ్లారు"], "answer": "వెళ్తాము", "explanation": "మేము బడికి వెళ్తాము అనేది సరైన క్రియా రూపం."})
            # Vocabulary Skills
            questions.append({"name": "q7", "type": "vocabulary", "prompt": "పర్యాయపదం: 'సూర్యుడు' అంటే ఏమిటి?", "options": ["రవి", "చంద్రుడు", "నక్షత్రం", "భూమి"], "answer": "రవి", "explanation": "సూర్యుడికి మరో పేరు రవి."})
            questions.append({"name": "q8", "type": "vocabulary", "prompt": "వ్యతిరేక పదం: మంచి x ___", "options": ["చెడు", "గొప్ప", "అందం", "ధైర్యం"], "answer": "చెడు", "explanation": "మంచికి వ్యతిరేక పదం చెడు."})
            questions.append({"name": "q9", "type": "vocabulary", "prompt": "చిత్ర పదం: ఈ బొమ్మ ఏమిటి? 🔺", "options": ["త్రిభుజం", "చతురస్రం", "వృత్తం", "దీర్ఘచతురస్రం"], "answer": "త్రిభుజం", "explanation": "మూడు మూలలు ఉన్నది త్రిభుజం."})
            # Grammar Skills
            questions.append({"name": "q10", "type": "grammar", "prompt": "సరైన వాక్యం: కింది వాటిలో సరైన వాక్యం ఏది?", "options": ["రాముడు బడికి వెళ్ళాడు.", "రాముడు బడికి వెళ్ళారు.", "రాముడు బడికి వెళ్ళిపోయావు.", "రాముడు బడికి వెళ్ళింది."], "answer": "రాముడు బడికి వెళ్ళాడు.", "explanation": "ఏకవచన నామవాచకానికి సరైన క్రియా రూపం 'వెళ్ళాడు'."})
            questions.append({"name": "q11", "type": "grammar", "prompt": "లోపించిన పదం: 'వారు రేపు ఊరికి _________.'", "options": ["వెళతారు", "వెళ్ళాడు", "వెళ్ళింది", "వెళ్ళావు"], "answer": "వెళతారు", "explanation": "రేపు భవిష్యత్ కాలాన్ని సూచిస్తుంది, కాబట్టి వెళతారు సరైనది."})
            questions.append({"name": "q12", "type": "grammar", "prompt": "వ్యాకరణం: నామవాచకాన్ని గుర్తించండి: 'కృష్ణ పండు తిన్నాడు'", "options": ["కృష్ణ", "పండు", "తిన్నాడు", "తిన్నాను"], "answer": "కృష్ణ", "explanation": "వ్యక్తి పేరు కాబట్టి కృష్ణ నామవాచకం."})
            # Listening Skills
            questions.append({"name": "q13", "type": "listening", "prompt": "వినండి మరియు సరైన చిత్రాన్ని ఎంచుకోండి:", "text": "కుక్క", "options": ["🐶 కుక్క", "🐱 పిల్లి", "🐰 కుందేలు", "🐮 ఆవు"], "answer": "🐶 కుక్క", "explanation": "కుక్క అని వినబడింది."})
            # Speaking Skills
            questions.append({"name": "q14", "type": "speaking", "prompt": "ఈ వాక్యాన్ని గట్టిగా చదవండి: నేను రోజూ క్రమశిక్షణతో చదువుకుంటాను.", "hint": "నేను రోజూ క్రమశిక్షణతో చదువుకుంటాను", "answer": "నేను రోజూ క్రమశిక్షణతో చదువుకుంటాను", "explanation": "ఉచ్చారణ పరీక్ష."})
            questions.append({"name": "q15", "type": "speaking", "prompt": "ఈ పదాన్ని స్పష్టంగా పలకండి: నమస్కారం", "hint": "నమస్కారం", "answer": "నమస్కారం", "explanation": "పలకడం పరీక్ష."})
        else:
            # 6 skills structured questions for English & Fallbacks
            # Reading Skills
            questions.append({"name": "q1", "type": "reading", "prompt": "Alphabet Identification: Select the uppercase letter that makes the sound /b/:", "options": ["B", "D", "P", "T"], "answer": "B", "explanation": "B makes the /b/ sound."})
            questions.append({"name": "q2", "type": "reading", "prompt": "Word Reading: Which word matches the picture of 🍎?", "options": ["Apple", "Banana", "Orange", "Grape"], "answer": "Apple", "explanation": "The image is an Apple."})
            questions.append({"name": "q3", "type": "reading", "prompt": "Reading Comprehension: 'The quick brown fox jumps over the lazy dog.' Which animal is lazy?", "options": ["Dog", "Fox", "Cat", "Rabbit"], "answer": "Dog", "explanation": "The text calls the dog lazy."})
            # Writing Skills
            questions.append({"name": "q4", "type": "writing", "prompt": "Spelling Check: Choose the correct spelling for 🐘:", "options": ["Elephant", "Elefant", "Eliphent", "Aliphant"], "answer": "Elephant", "explanation": "Elephant is the correct spelling."})
            questions.append({"name": "q5", "type": "writing", "prompt": "Sentence Completion: Complete the sentence: 'The children are ________ in the school playground.'", "options": ["playing", "play", "played", "plays"], "answer": "playing", "explanation": "Present continuous tense 'are playing' is required."})
            questions.append({"name": "q6", "type": "writing", "prompt": "Word Completion: Fill in the blank to name 🐱: C _ T", "options": ["A", "E", "O", "I"], "answer": "A", "explanation": "CAT is the correct animal word."})
            # Vocabulary Skills
            questions.append({"name": "q7", "type": "vocabulary", "prompt": "Synonyms: Choose the word that means the same as 'Happy':", "options": ["Glad", "Sad", "Angry", "Tired"], "answer": "Glad", "explanation": "Glad is a synonym of Happy."})
            questions.append({"name": "q8", "type": "vocabulary", "prompt": "Antonyms: Choose the opposite of 'Cold':", "options": ["Hot", "Warm", "Freeze", "Cool"], "answer": "Hot", "explanation": "Hot is the opposite of Cold."})
            questions.append({"name": "q9", "type": "vocabulary", "prompt": "Picture Vocabulary: What is shown in the image? 🚗", "options": ["Car", "Bicycle", "Train", "Airplane"], "answer": "Car", "explanation": "It's a Car."})
            # Grammar Skills
            questions.append({"name": "q10", "type": "grammar", "prompt": "Correct Sentence: Select the grammatically correct sentence:", "options": ["She goes to school every day.", "She go to school every day.", "She going to school every day.", "She gone to school every day."], "answer": "She goes to school every day.", "explanation": "Third person singular requires verb + s (goes)."})
            questions.append({"name": "q11", "type": "grammar", "prompt": "Missing Word: Identify the missing word: 'They ___ planning a picnic for tomorrow.'", "options": ["are", "is", "am", "was"], "answer": "are", "explanation": "They is a plural pronoun, so 'are' is used."})
            questions.append({"name": "q12", "type": "grammar", "prompt": "Missing Letter: Which letter completes the word 're_d' (meaning to look at written words)?", "options": ["a", "e", "i", "o"], "answer": "a", "explanation": "READ."})
            # Listening Skills
            questions.append({"name": "q13", "type": "listening", "prompt": "Listen and select the word you hear:", "text": "Welcome", "options": ["Welcome", "Thank you", "Goodbye", "Hello"], "answer": "Welcome", "explanation": "Welcome was spoken."})
            # Speaking Skills
            questions.append({"name": "q14", "type": "speaking", "prompt": "Read this sentence aloud: 'Learning a new language opens up doors to new worlds.'", "hint": "Learning a new language opens up doors to new worlds", "answer": "Learning a new language opens up doors to new worlds", "explanation": "Pronounce all words clearly."})
            questions.append({"name": "q15", "type": "speaking", "prompt": "Pronounce this word clearly: 'Foundational'", "hint": "Foundational", "answer": "Foundational", "explanation": "Foundational."})

        return questions

    return build_15_questions(language, age_val, lvl)"""

# Locate the get_assessment_questions definition
pattern = r"def get_assessment_questions\(language, age=None, learning_level=None, mode=None\):.*?return build_15_questions\(language, age_val, lvl\)"
modified, count = re.subn(pattern, new_function, content, flags=re.DOTALL)

if count > 0:
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(modified)
    print("Replacement success! Modified", count, "occurrence(s).")
else:
    print("Replacement failed! Target pattern not matched.")
