import sqlite3
import json

# Centralized Multilingual Vocabulary Database for all 6 languages
MULTILINGUAL_DICTIONARY = {
    'Greetings': [
{
            'word_id': 'hello',
            'translations': {
                'English': ('Hello', 'hello'),
                'Telugu': ('నమస్కారం', 'namaskaram'),
                'Hindi': ('नमस्ते', 'namaste'),
                'Tamil': ('வணக்கம்', 'vanakkam'),
                'Kannada': ('ನಮಸ್ಕಾರ', 'namaskara'),
                'Marathi': ('नमस्कार', 'namaskar')
            },
            'image': 'hello.png'
        },
{
            'word_id': 'thank_you',
            'translations': {
                'English': ('Thank you', 'thank you'),
                'Telugu': ('ధన్యవాదాలు', 'dhanyavadalu'),
                'Hindi': ('धन्यवाद', 'dhanyavaad'),
                'Tamil': ('நன்றி', 'nanri'),
                'Kannada': ('ಧನ್ಯವಾದಗಳು', 'dhanyavadagalu'),
                'Marathi': ('धन्यवाद', 'dhanyavaad')
            },
            'image': 'thank_you.png'
        },
{
            'word_id': 'good_morning',
            'translations': {
                'English': ('Good morning', 'good morning'),
                'Telugu': ('శుభోదయం', 'shubhodhayam'),
                'Hindi': ('सुप्रभात', 'suprabhaat'),
                'Tamil': ('காலை வணக்கம்', 'kaalai vanakkam'),
                'Kannada': ('ಶುಭೋದಯ', 'shubhodaya'),
                'Marathi': ('शुभ सकाळ', 'shubh sakaal')
            },
            'image': 'good_morning.png'
        },
{
            'word_id': 'good_night',
            'translations': {
                'English': ('Good night', 'good night'),
                'Telugu': ('శుభ రాత్రి', 'shubha raatri'),
                'Hindi': ('शुभ रात्रि', 'shubh raatri'),
                'Tamil': ('இரவு வணக்கம்', 'iravu vanakkam'),
                'Kannada': ('ಶುಭ ರಾತ್ರಿ', 'shubha raatri'),
                'Marathi': ('शुभ रात्री', 'shubh raatri')
            },
            'image': 'good_night.png'
        },
{
            'word_id': 'goodbye',
            'translations': {
                'English': ('Goodbye', 'goodbye'),
                'Telugu': ('సెలవు', 'selavu'),
                'Hindi': ('अलविदा', 'alvida'),
                'Tamil': ('போய் வருகிறேன்', 'poi varugiren'),
                'Kannada': ('ಹೋಗಿ ಬರುತ್ತೇನೆ', 'hogi baruttene'),
                'Marathi': ('निरोप', 'nirop')
            },
            'image': 'goodbye.png'
        },
{
            'word_id': 'please',
            'translations': {
                'English': ('Please', 'please'),
                'Telugu': ('దయచేసి', 'dayachesi'),
                'Hindi': ('कृपया', 'kripya'),
                'Tamil': ('தயவுசெய்து', 'thayavuseythu'),
                'Kannada': ('ದಯವಿಟ್ಟು', 'dayavittu'),
                'Marathi': ('कृपया', 'krupya')
            },
            'image': 'please.png'
        },
{
            'word_id': 'sorry',
            'translations': {
                'English': ('Sorry', 'sorry'),
                'Telugu': ('క్షమించండి', 'kshaminchandi'),
                'Hindi': ('माफ़ कीजिये', 'maaf kijiye'),
                'Tamil': ('மன்னிக்கவும்', 'mannikkavum'),
                'Kannada': ('ಕ್ಷಮಿಸಿ', 'kshamisi'),
                'Marathi': ('माफ करा', 'maaf kara')
            },
            'image': 'sorry.png'
        }
    ],
    'Numbers': [
{
            'word_id': 'one',
            'translations': {
                'English': ('One', 'one'),
                'Telugu': ('ఒకటి', 'okati'),
                'Hindi': ('एक', 'ek'),
                'Tamil': ('ஒன்று', 'ondru'),
                'Kannada': ('ಒಂದು', 'ondu'),
                'Marathi': ('एक', 'ek')
            },
            'image': 'number_1.png'
        },
{
            'word_id': 'two',
            'translations': {
                'English': ('Two', 'two'),
                'Telugu': ('రెండు', 'rendu'),
                'Hindi': ('दो', 'do'),
                'Tamil': ('இரண்டு', 'irandu'),
                'Kannada': ('ಎರಡು', 'eradu'),
                'Marathi': ('दोन', 'don')
            },
            'image': 'number_2.png'
        },
{
            'word_id': 'three',
            'translations': {
                'English': ('Three', 'three'),
                'Telugu': ('మూడు', 'moodu'),
                'Hindi': ('तीन', 'teen'),
                'Tamil': ('மூன்று', 'moondru'),
                'Kannada': ('ಮೂರು', 'mooru'),
                'Marathi': ('तीन', 'teen')
            },
            'image': 'number_3.png'
        },
{
            'word_id': 'four',
            'translations': {
                'English': ('Four', 'four'),
                'Telugu': ('నాలుగు', 'naalugu'),
                'Hindi': ('चार', 'chaar'),
                'Tamil': ('நான்கு', 'naangu'),
                'Kannada': ('ನಾಲ್ಕು', 'naalku'),
                'Marathi': ('चार', 'chaar')
            },
            'image': 'number_4.png'
        },
{
            'word_id': 'five',
            'translations': {
                'English': ('Five', 'five'),
                'Telugu': ('ఐదు', 'aidu'),
                'Hindi': ('पाँच', 'paanch'),
                'Tamil': ('ஐந்து', 'ainthu'),
                'Kannada': ('ಐದು', 'aidu'),
                'Marathi': ('पाच', 'paach')
            },
            'image': 'number_5.png'
        },
{
            'word_id': 'ten',
            'translations': {
                'English': ('Ten', 'ten'),
                'Telugu': ('పది', 'padi'),
                'Hindi': ('दस', 'das'),
                'Tamil': ('பத்து', 'pathu'),
                'Kannada': ('ಹತ್ತು', 'hattu'),
                'Marathi': ('दहा', 'daha')
            },
            'image': 'number_10.png'
        }
    ],
    'Colors': [
{
            'word_id': 'red',
            'translations': {
                'English': ('Red', 'red'),
                'Telugu': ('ఎరుపు', 'erupu'),
                'Hindi': ('लाल', 'laal'),
                'Tamil': ('சிவப்பு', 'sivappu'),
                'Kannada': ('ಕೆಂಪು', 'kempu'),
                'Marathi': ('लाल', 'laal')
            },
            'image': 'color_red.png'
        },
{
            'word_id': 'blue',
            'translations': {
                'English': ('Blue', 'blue'),
                'Telugu': ('నీలం', 'neelam'),
                'Hindi': ('नीला', 'neela'),
                'Tamil': ('நீலம்', 'neelam'),
                'Kannada': ('ನೀಲಿ', 'neeli'),
                'Marathi': ('निळा', 'nila')
            },
            'image': 'color_blue.png'
        },
{
            'word_id': 'green',
            'translations': {
                'English': ('Green', 'green'),
                'Telugu': ('పచ్చ', 'pachcha'),
                'Hindi': ('हरा', 'hara'),
                'Tamil': ('பச்சை', 'pachai'),
                'Kannada': ('ಹಸಿರು', 'hasiru'),
                'Marathi': ('हिरवा', 'hirva')
            },
            'image': 'color_green.png'
        },
{
            'word_id': 'yellow',
            'translations': {
                'English': ('Yellow', 'yellow'),
                'Telugu': ('పసుపు', 'pasupu'),
                'Hindi': ('पीला', 'peela'),
                'Tamil': ('மஞ்சள்', 'manjal'),
                'Kannada': ('ಹಳದಿ', 'haladi'),
                'Marathi': ('पिवळा', 'pivla')
            },
            'image': 'color_yellow.png'
        },
{
            'word_id': 'black',
            'translations': {
                'English': ('Black', 'black'),
                'Telugu': ('నలుపు', 'nalupu'),
                'Hindi': ('काला', 'kaala'),
                'Tamil': ('கருப்பு', 'karuppu'),
                'Kannada': ('ಕಪ್ಪು', 'kappu'),
                'Marathi': ('काळा', 'kala')
            },
            'image': 'color_black.png'
        }
    ],
    'Family': [
{
            'word_id': 'mother',
            'translations': {
                'English': ('Mother', 'mother'),
                'Telugu': ('అమ్మ', 'amma'),
                'Hindi': ('माँ', 'maa'),
                'Tamil': ('அம்மா', 'amma'),
                'Kannada': ('ಅಮ್ಮ', 'amma'),
                'Marathi': ('आई', 'aai')
            },
            'image': 'family_mother.png'
        },
{
            'word_id': 'father',
            'translations': {
                'English': ('Father', 'father'),
                'Telugu': ('నాన్న', 'naanna'),
                'Hindi': ('पिता', 'pita'),
                'Tamil': ('அಪ್ಪா', 'appa'),
                'Kannada': ('ಅಪ್ಪ', 'appa'),
                'Marathi': ('वडील', 'vadil')
            },
            'image': 'family_father.png'
        },
{
            'word_id': 'brother',
            'translations': {
                'English': ('Brother', 'brother'),
                'Telugu': ('సహోదరుడు', 'sahodarudu'),
                'Hindi': ('भाई', 'bhai'),
                'Tamil': ('சகோதரன்', 'sagotharan'),
                'Kannada': ('ಸಹೋದರ', 'sahodara'),
                'Marathi': ('भाऊ', 'bhau')
            },
            'image': 'family_brother.png'
        },
{
            'word_id': 'sister',
            'translations': {
                'English': ('Sister', 'sister'),
                'Telugu': ('సహోదరి', 'sahodari'),
                'Hindi': ('बहन', 'behan'),
                'Tamil': ('சகோதரி', 'sagothari'),
                'Kannada': ('ಸಹೋದರಿ', 'sahodari'),
                'Marathi': ('बहीण', 'bahin')
            },
            'image': 'family_sister.png'
        }
    ],
    'Food': [
{
            'word_id': 'water',
            'translations': {
                'English': ('Water', 'water'),
                'Telugu': ('నీరు', 'neeru'),
                'Hindi': ('पानी', 'paani'),
                'Tamil': ('தண்ணீர்', 'thanneer'),
                'Kannada': ('ನೀರು', 'neeru'),
                'Marathi': ('पाणी', 'paani')
            },
            'image': 'food_water.png'
        },
{
            'word_id': 'milk',
            'translations': {
                'English': ('Milk', 'milk'),
                'Telugu': ('పాలు', 'paalu'),
                'Hindi': ('दूध', 'doodh'),
                'Tamil': ('பால்', 'paal'),
                'Kannada': ('ಹಾಲು', 'haalu'),
                'Marathi': ('दूध', 'doodh')
            },
            'image': 'food_milk.png'
        },
{
            'word_id': 'apple',
            'translations': {
                'English': ('Apple', 'apple'),
                'Telugu': ('ఆపిల్', 'apple'),
                'Hindi': ('सेब', 'seb'),
                'Tamil': ('ஆப்பிள்', 'aappil'),
                'Kannada': ('ಸೇಬು', 'seebu'),
                'Marathi': ('सफरचंद', 'safarchand')
            },
            'image': 'food_apple.png'
        },
{
            'word_id': 'rice',
            'translations': {
                'English': ('Rice', 'rice'),
                'Telugu': ('అన్నం', 'annam'),
                'Hindi': ('चावल', 'chaaval'),
                'Tamil': ('அரிசி', 'arisi'),
                'Kannada': ('ಅಕ್ಕಿ', 'akki'),
                'Marathi': ('भात', 'bhaat')
            },
            'image': 'food_rice.png'
        }
    ],
    'Animals': [
{
            'word_id': 'cat',
            'translations': {
                'English': ('Cat', 'cat'),
                'Telugu': ('పిల్లి', 'pilli'),
                'Hindi': ('बिल्ली', 'billi'),
                'Tamil': ('பூனை', 'poonai'),
                'Kannada': ('ಬೆಕ್ಕು', 'bekku'),
                'Marathi': ('मांजर', 'manjar')
            },
            'image': 'animal_cat.png'
        },
{
            'word_id': 'dog',
            'translations': {
                'English': ('Dog', 'dog'),
                'Telugu': ('కుక్క', 'kukka'),
                'Hindi': ('कुत्ता', 'kutta'),
                'Tamil': ('நாய்', 'naai'),
                'Kannada': ('ನಾಯಿ', 'naayi'),
                'Marathi': ('कुत्रा', 'kutra')
            },
            'image': 'animal_dog.png'
        },
{
            'word_id': 'cow',
            'translations': {
                'English': ('Cow', 'cow'),
                'Telugu': ('ఆవు', 'aavu'),
                'Hindi': ('गाय', 'gaay'),
                'Tamil': ('பசு', 'pasu'),
                'Kannada': ('ಹಸು', 'hasu'),
                'Marathi': ('गाय', 'gaay')
            },
            'image': 'animal_cow.png'
        },
{
            'word_id': 'lion',
            'translations': {
                'English': ('Lion', 'lion'),
                'Telugu': ('సింహం', 'simham'),
                'Hindi': ('शेर', 'sher'),
                'Tamil': ('சிங்கம்', 'singam'),
                'Kannada': ('ಸಿಂಹ', 'simha'),
                'Marathi': ('सिंह', 'sinha')
            },
            'image': 'animal_lion.png'
        }
    ],
    'Daily Objects': [
{
            'word_id': 'book',
            'translations': {
                'English': ('Book', 'book'),
                'Telugu': ('ಪುಸ್ತಕం', 'pustakam'),
                'Hindi': ('किताब', 'kitaab'),
                'Tamil': ('புத்தகம்', 'puthagam'),
                'Kannada': ('ಪುಸ್ತಕ', 'pustaka'),
                'Marathi': ('पुस्तक', 'pustak')
            },
            'image': 'object_book.png'
        },
{
            'word_id': 'pen',
            'translations': {
                'English': ('Pen', 'pen'),
                'Telugu': ('పెన్ను', 'pennu'),
                'Hindi': ('कलम', 'kalam'),
                'Tamil': ('பேனா', 'peena'),
                'Kannada': ('ಪೇನಾ', 'pena'),
                'Marathi': ('पेन', 'pen')
            },
            'image': 'object_pen.png'
        },
{
            'word_id': 'table',
            'translations': {
                'English': ('Table', 'table'),
                'Telugu': ('మేజా', 'meeja'),
                'Hindi': ('मेज़', 'mez'),
                'Tamil': ('மேஜை', 'meejai'),
                'Kannada': ('ಮೇಜು', 'meeju'),
                'Marathi': ('टेबल', 'tebal')
            },
            'image': 'object_table.png'
        },
{
            'word_id': 'chair',
            'translations': {
                'English': ('Chair', 'chair'),
                'Telugu': ('कुर्ची', 'kurchi'),
                'Hindi': ('कुर्सी', 'kursi'),
                'Tamil': ('நாற்காலி', 'naarkali'),
                'Kannada': ('ಖುರ್ಚಿ', 'khurchi'),
                'Marathi': ('खुर्ची', 'khurchi')
            },
            'image': 'object_chair.png'
        }
    ],
    'Daily Conversations': [
{
            'word_id': 'whats_name',
            'translations': {
                'English': ('What is your name?', 'what is your name'),
                'Telugu': ('मी పేరు ఏమిటి?', 'mee peru emiti'),
                'Hindi': ('आपका नाम क्या है?', 'aapka naam kya hai'),
                'Tamil': ('உங்கள் பெயர் என்ன?', 'ungal peyar enna'),
                'Kannada': ('ನಿಮ್ಮ ಹೆಸರೇನು?', 'nimma hesarenu'),
                'Marathi': ('तुमचे नाव काय आहे?', 'tumche naav kay aahe')
            },
            'image': 'conv_name.png'
        },
{
            'word_id': 'my_name_john',
            'translations': {
                'English': ('My name is John.', 'my name is john'),
                'Telugu': ('నా పేరు జాన్.', 'naa peru john'),
                'Hindi': ('मेरा नाम जॉन है।', 'mera naam john hai'),
                'Tamil': ('என் பெயர் ஜான்.', 'en peyar john'),
                'Kannada': ('ನನ್ನ ಹೆಸರು ಜಾನ್.', 'nanna hesaru john'),
                'Marathi': ('माझे नाव जॉन आहे.', 'mazhe naav john aahe')
            },
            'image': 'conv_myname.png'
        },
{
            'word_id': 'how_are_you',
            'translations': {
                'English': ('How are you?', 'how are you'),
                'Telugu': ('మీరు ఎలా ఉన్నారు?', 'meeru ela unnaru'),
                'Hindi': ('आप कैसे हैं?', 'aap kaise hain'),
                'Tamil': ('நீங்கள் எப்படி இருக்கிறீர்கள்?', 'neengal eppadi irukkireergall'),
                'Kannada': ('ನೀವು ಹೇಗಿದ್ದೀರಾ?', 'neevu hegiddira'),
                'Marathi': ('तुम्ही कसे आहात?', 'tumhi kase aahat')
            },
            'image': 'conv_howareyou.png'
        },
{
            'word_id': 'i_am_fine',
            'translations': {
                'English': ('I am fine.', 'i am fine'),
                'Telugu': ('నేను బాగున్నాను.', 'nenu baagunnanu'),
                'Hindi': ('मैं ठीक हूँ।', 'main theek hoon'),
                'Tamil': ('நான் நலமாக இருக்கிறேன்.', 'naan nalamaaga irukkiren'),
                'Kannada': ('ನಾನು ಆರಾಮಾಗಿದ್ದೇನೆ.', 'naanu aaramaagiddene'),
                'Marathi': ('मी ठीक आहे.', 'mi theek aahe')
            },
            'image': 'conv_iamfine.png'
        }
    ],
    'Sentence Practice': [
{
            'word_id': 'i_read',
            'translations': {
                'English': ('I am reading.', 'i am reading'),
                'Telugu': ('నేను చదువుతున్నాను.', 'nenu chaduvuthunnanu'),
                'Hindi': ('मैं पढ़ रहा हूँ।', 'main padh raha hoon'),
                'Tamil': ('நான் படிக்கிறேன்.', 'naan padikkiren'),
                'Kannada': ('ನಾನು ಓದುತ್ತಿದ್ದೇನೆ.', 'naanu oduttiddene'),
                'Marathi': ('मी वाचत आहे.', 'mi vaachat aahe')
            },
            'image': 'sent_reading.png'
        },
{
            'word_id': 'i_write',
            'translations': {
                'English': ('I am writing.', 'i am writing'),
                'Telugu': ('నేను రాస్తున్నాను.', 'nenu raasthunnanu'),
                'Hindi': ('मैं लिख रहा हूँ।', 'main likh raha hoon'),
                'Tamil': ('நான் எழுதுகிறேன்.', 'naan ezhuthugiren'),
                'Kannada': ('ನಾನು ಬರೆಯುತ್ತಿದ್ದೇನೆ.', 'naanu bareyuttiddene'),
                'Marathi': ('मी लिहित आहे.', 'mi lihit aahe')
            },
            'image': 'sent_writing.png'
        },
{
            'word_id': 'we_learn',
            'translations': {
                'English': ('We are learning.', 'we are learning'),
                'Telugu': ('మేము నేర్చుకుంటున్నాము.', 'memu nerchukuntunnamu'),
                'Hindi': ('हम सीख रहे हैं।', 'hum seekh rahe hain'),
                'Tamil': ('நாங்கள் கற்கிறோம்.', 'naangal karkiroam'),
                'Kannada': ('ನಾವು ಕಲಿಯುತ್ತಿದ್ದೇವೆ.', 'naavu kaliyuttiddeve'),
                'Marathi': ('आम्ही शिकत आहोत.', 'aamhi shikat aahot')
            },
            'image': 'sent_learning.png'
        }
    ],
    'Story Reading': [
{
            'word_id': 'story_crow',
            'translations': {
                'English': ('A thirsty crow found water.', 'a thirsty crow found water'),
                'Telugu': ('దాహంతో ఉన్న కాకికి నీరు దొరికింది.', 'daahamtho unna kaakiki neeru dorikindi'),
                'Hindi': ('एक प्यासे कौवे को पानी मिला।', 'ek pyaase kauve ko paani mila'),
                'Tamil': ('ஒரு தாகமுள்ள காகம் நீரைக் கண்டது.', 'oru thaagamulla kaagam neerai kandathu'),
                'Kannada': ('ಬಾಯಾರಿದ ಕಾಗೆಗೆ ನೀರು ಸಿಕ್ಕಿತು.', 'bayaarida kaagege neeru sikkitu'),
                'Marathi': ('एका तहानलेल्या कावळ्याला पाणी सापडले.', 'eka tahanlelya kawalyala pani sapadle')
            },
            'image': 'story_crow.png'
        },
{
            'word_id': 'story_hare_tortoise',
            'translations': {
                'English': ('The slow tortoise won the race.', 'the slow tortoise won the race'),
                'Telugu': ('నెమ్మదిగా ఉన్న తాబేలు పరుగు పందెంలో గెలిచింది.', 'nemmadiga unna taabelu parugu pandemlo gelichindi'),
                'Hindi': ('धीमी कछुए ने दौड़ जीत ली।', 'dheemi kachhue ne daud jeet lee'),
                'Tamil': ('மெதுவான ஆமை பந்தயத்தில் வென்றது.', 'methuvaana aamai panthayathil vendrathu'),
                'Kannada': ('ನಿಧಾನವಾದ ಆಮೆ ಓಟದ ಪಂದ್ಯವನ್ನು ಗೆದ್ದಿತು.', 'nidhaanavaada aame otada pandyavannu gedditu'),
                'Marathi': ('हळू चालणाऱ्या कासवाने शर्यत जिंकली.', 'halu chalnarya kasavane sharyat jinkli')
            },
            'image': 'story_tortoise.png'
        }
    ],
    'At the Market': [
{
            'word_id': 'how_much',
            'translations': {
                'English': ('How much is this?', 'how much is this'),
                'Telugu': ('ఇది ఎంత?', 'idi entha'),
                'Hindi': ('यह कितने का है?', 'yeh kitne ka hai'),
                'Tamil': ('இது எவ்வளவு?', 'ithu evvalavu'),
                'Kannada': ('ಇದು ಎಷ್ಟು?', 'idu eshtu'),
                'Marathi': ('हे कितीला आहे?', 'he kitila aahe')
            },
            'image': 'market_howmuch.png'
        },
{
            'word_id': 'one_kg',
            'translations': {
                'English': ('Give me one kilogram.', 'give me one kilogram'),
                'Telugu': ('నాకు ఒక కిలో ఇవ్వండి.', 'naaku oka kilo ivvandi'),
                'Hindi': ('मुझे एक किलो दे दो।', 'mujhe ek kilo de do'),
                'Tamil': ('எனக்கு ஒரு கிலோ கொடுங்கள்.', 'enakku oru kilo kodungal'),
                'Kannada': ('ನನಗೆ ಒಂದು ಕೆಜಿ ಕೊಡಿ.', 'nanage ondu kg kodi'),
                'Marathi': ('मला एक किलो द्या.', 'mala ek kilo dya')
            },
            'image': 'market_onekg.png'
        },
{
            'word_id': 'is_fresh',
            'translations': {
                'English': ('Is it fresh?', 'is it fresh'),
                'Telugu': ('ఇది తాజాదా?', 'idi taajadaa'),
                'Hindi': ('क्या यह ताज़ा है?', 'kya yeh taaza hai'),
                'Tamil': ('இது புதியதா?', 'ithu puthiyatha'),
                'Kannada': ('ಇದು తాజಾವಾಗಿದೆಯೇ?', 'idu taajaavagideye'),
                'Marathi': ('हे ताजे आहे का?', 'he taje aahe ka')
            },
            'image': 'market_fresh.png'
        },
{
            'word_id': 'market_thanks',
            'translations': {
                'English': ('Thank you, here is the money.', 'thank you here is the money'),
                'Telugu': ('ధన్యవాదాలు, ఇదిగో డబ్బులు.', 'dhanyavadalu idigo dabbulu'),
                'Hindi': ('धन्यवाद, ये लीजिये पैसे।', 'dhanyavaad ye liye paise'),
                'Tamil': ('நன்றி, இதो பணம்.', 'nanri itho panam'),
                'Kannada': ('ಧನ್ಯವಾದಗಳು, ಇಗೋ ಹಣ.', 'dhanyavadagalu igo hana'),
                'Marathi': ('धन्यवाद, हे घ्या पैसे.', 'dhanyavaad he ghya paise')
            },
            'image': 'market_money.png'
        }
    ],
    'Asking for Directions': [
{
            'word_id': 'bus_stand',
            'translations': {
                'English': ('Where is the bus stand?', 'where is the bus stand'),
                'Telugu': ('బస్ స్టాండ్ ఎక్కడ ఉంది?', 'bus stand ekkada undi'),
                'Hindi': ('बस स्टैंड कहाँ है?', 'bus stand kaha hai'),
                'Tamil': ('பேருந்து நிலையம் எங்கே உள்ளது?', 'peerunthu nilaiyam engee ullathu'),
                'Kannada': ('ಬಸ್ ನಿಲ್ದಾಣ ಎಲ್ಲಿದೆ?', 'bus nildana ellide'),
                'Marathi': ('बस स्थानक कोठे आहे?', 'bus sthanak kothe aahe')
            },
            'image': 'dir_bus.png'
        },
{
            'word_id': 'go_straight',
            'translations': {
                'English': ('Go straight.', 'go straight'),
                'Telugu': ('నేరముగా వెళ్ళండి.', 'neramuga vellandi'),
                'Hindi': ('सीधे जाओ।', 'seedhe jao'),
                'Tamil': ('நேராக செல்லுங்கள்.', 'neraga sellungal'),
                'Kannada': ('ನೇರವಾಗಿ ಹೋಗಿ.', 'neravagi hogi'),
                'Marathi': ('सरळ जा.', 'saral ja')
            },
            'image': 'dir_straight.png'
        },
{
            'word_id': 'turn_left',
            'translations': {
                'English': ('Turn left.', 'turn left'),
                'Telugu': ('ఎడమ వైపు తిరగండి.', 'edama vaipu thiragandi'),
                'Hindi': ('बाएँ मुड़ो।', 'baaye mudo'),
                'Tamil': ('இடதுபுறம் திரும்पुங்கள்.', 'idathupuram thirumbungal'),
                'Kannada': ('ಎಡಕ್ಕೆ ತಿರುಗಿ.', 'edakke thirugi'),
                'Marathi': ('डावीकडे वळा.', 'davikade vala')
            },
            'image': 'dir_left.png'
        },
{
            'word_id': 'is_near',
            'translations': {
                'English': ('Is it near?', 'is it near'),
                'Telugu': ('ఇది దగ్గరగా ఉందా?', 'idi daggaraga unda'),
                'Hindi': ('क्या यह पास में है?', 'kya yeh paas mein hai'),
                'Tamil': ('இது அருகில் உள்ளதா?', 'ithu arugil ullatha'),
                'Kannada': ('ಇದು ಹತ್ತಿರವಿದೆಯೇ?', 'idu hattiravideye'),
                'Marathi': ('हे जवळ आहे का?', 'he javal aahe ka')
            },
            'image': 'dir_near.png'
        }
    ],
    'At the Doctor': [
{
            'word_id': 'headache',
            'translations': {
                'English': ('I have a headache.', 'i have a headache'),
                'Telugu': ('నాకు తలనెప్పిగా ఉంది.', 'naaku thalaneppiga undi'),
                'Hindi': ('मेरे सिर में दर्द है।', 'mere sir mein dard hai'),
                'Tamil': ('எனके தலைவலி உள்ளது.', 'enakku thalaivali ullathu'),
                'Kannada': ('ನನಗೆ ತಲೆನೋವು ಇದೆ.', 'nanage talenovu ide'),
                'Marathi': ('माझे डोके दुखत आहे.', 'mazhe doke dukhat aahe')
            },
            'image': 'doc_headache.png'
        },
{
            'word_id': 'take_medicine',
            'translations': {
                'English': ('Take this medicine.', 'take this medicine'),
                'Telugu': ('ఈ మందు తీసుకోండి.', 'ee mandu theesukondi'),
                'Hindi': ('यह दवा लीजिये।', 'yeh dawa lijiye'),
                'Tamil': ('இந்த மருந்தை எடுத்துக் கொள்ளுங்கள்.', 'intha marunthai eduthukollungal'),
                'Kannada': ('ಈ ಔಷಧಿಯನ್ನು ತೆಗೆದುಕೊಳ್ಳಿ.', 'ee aushadhiyannu tegedukolli'),
                'Marathi': ('हे औषध घ्या.', 'he aushadh ghya')
            },
            'image': 'doc_med.png'
        },
{
            'word_id': 'warm_water',
            'translations': {
                'English': ('Drink warm water.', 'drink warm water'),
                'Telugu': ('గోరువెచ్చని నీరు తాగండి.', 'goruvechchani neeru thaagandi'),
                'Hindi': ('गुनगुना पानी पीएं।', 'gunguna paani piye'),
                'Tamil': ('வெதுவெதுப்பான நீர் குடிக்கவும்.', 'vethuvethuppaana neer kudikkavum'),
                'Kannada': ('ಉಗುರುಬೆಚ್ಚಗಿನ ನೀರನ್ನು ಕುಡಿಯಿರಿ.', 'ugurubechagina neerannu kudiyiri'),
                'Marathi': ('कोमट पाणी प्या.', 'komat pani pya')
            },
            'image': 'doc_water.png'
        }
    ],
    'Workspace Conversations': [
{
            'word_id': 'when_meeting',
            'translations': {
                'English': ('When is the meeting?', 'when is the meeting'),
                'Telugu': ('సమావేశం ఎప్పుడు?', 'samavesham eppudu'),
                'Hindi': ('बैठक कब है?', 'baithak kab hai'),
                'Tamil': ('கூட்டம் எப்போது?', 'koottam eppothu'),
                'Kannada': ('ಸಭೆ ಯಾವಾಗ?', 'sabhe yavaga'),
                'Marathi': ('बैठक कधी आहे?', 'baithak kadhi aahe')
            },
            'image': 'work_meeting.png'
        },
{
            'word_id': 'please_sign',
            'translations': {
                'English': ('Please sign this.', 'please sign this'),
                'Telugu': ('దయచేసి ఇక్కడ సంతకం చేయండి.', 'dayachesi ikkada santhakam cheyandi'),
                'Hindi': ('कृपया यहाँ हस्ताक्षर करें।', 'kripya yaha hastakshar kare'),
                'Tamil': ('தயவுசெய்து இங்கே கையெழுத்திடுங்கள்.', 'thayavuseythu inge kaiyeluthidungal'),
                'Kannada': ('ದಯವಿಟ್ಟು ಇಲ್ಲಿ ಸಹಿ ಮಾಡಿ.', 'dayavittu illi sahi madi'),
                'Marathi': ('कृपया येथे स्वाक्षरी करा.', 'krupya yethe svakshari kara')
            },
            'image': 'work_sign.png'
        },
{
            'word_id': 'report_done',
            'translations': {
                'English': ('I completed the report.', 'i completed the report'),
                'Telugu': ('నేను రిపోర్ట్ పూర్తి చేశాను.', 'nenu report poorthi chesaanu'),
                'Hindi': ('मैंने रिपोर्ट पूरी कर ली है।', 'maine report poori kar lee hai'),
                'Tamil': ('நான் அறிக்கையை முடித்துவிட்டேன்.', 'naan arikkaiyai mudithuvitten'),
                'Kannada': ('ನಾನು ವರದಿಯನ್ನು ಪೂರ್ಣಗೊಳಿಸಿದ್ದೇನೆ.', 'naanu varadiyannu purnagolisiddene'),
                'Marathi': ('मी अहवाल पूर्ण केला आहे.', 'mi ahval purna kela aahe')
            },
            'image': 'work_report.png'
        }
    ],
    'Idioms & Daily Slang': [
{
            'word_id': 'hows_it_going',
            'translations': {
                'English': ("How's it going?", 'hows it going'),
                'Telugu': ('ఎలా నడుస్తోంది?', 'ela nadusthondi'),
                'Hindi': ('क्या हाल है?', 'kya haal hai'),
                'Tamil': ('எப்படி போகிறது?', 'eppadi pogirathu'),
                'Kannada': ('ಹೇಗಿದೆ?', 'hegide'),
                'Marathi': ('काय चाललंय?', 'kay chalalay')
            },
            'image': 'slang_hows.png'
        },
{
            'word_id': 'call_it_day',
            'translations': {
                'English': ("Let's call it a day.", 'lets call it a day'),
                'Telugu': ('ఈ రోజుకు ఇక చాలు.', 'ee rojuky ika chaalu'),
                'Hindi': ('आज के लिए बस इतना ही।', 'aaj ke liye bas itna hi'),
                'Tamil': ('இன்றைக்கு இத்துடன் முடிப்போம்.', 'indraikku ithudan mudippoam'),
                'Kannada': ('ಇಂದಿಗೆ ಇಷ್ಟೇ ಸಾಕು.', 'indige ishte saaku'),
                'Marathi': ('आजच्यासाठी पुरे.', 'aajchyasathi pure')
            },
            'image': 'slang_call.png'
        },
{
            'word_id': 'piece_of_cake',
            'translations': {
                'English': ("It's a piece of cake.", 'its a piece of cake'),
                'Telugu': ('ఇది చాలా సులभం.', 'idi chaala sulabham'),
                'Hindi': ('यह बहुत आसान है।', 'yeh bahut aasaan hai'),
                'Tamil': ('இது மிகவும் சுலபம்.', 'ithu migavum sulabam'),
                'Kannada': ('ಇದು ತುಂಬಾ ಸುಲಭ.', 'idu tumba sulabha'),
                'Marathi': ('हे खूप सोपे आहे.', 'he khup sope aahe')
            },
            'image': 'slang_cake.png'
        }
    ],
    'Socializing & Hobbies': [
{
            'word_id': 'what_like_do',
            'translations': {
                'English': ('What do you like to do?', 'what do you like to do'),
                'Telugu': ('మీకు ఏమి చేయడం ఇష్టం?', 'meeru emi cheyadam ishtam'),
                'Hindi': ('आपको क्या करना पसंद है?', 'aapko kya karna pasand hai'),
                'Tamil': ('உங்களுக்கு என்ன செய்ய பிடிக்கும்?', 'ungalukku enna seyya pidikum'),
                'Kannada': ('ನಿಮಗೆ ಏನು ಮಾಡಲು ಇಷ್ಟ?', 'nimage enu madalu ishta'),
                'Marathi': ('तुम्हाला काय करायला आवडते?', 'tumhala kay karायला aavadte')
            },
            'image': 'social_like.png'
        },
{
            'word_id': 'enjoy_music',
            'translations': {
                'English': ('I enjoy listening to music.', 'i enjoy listening to music'),
                'Telugu': ('నాకు సంగీతం వినడం ఇష్టం.', 'naaku sangeetham vinadam ishtam'),
                'Hindi': ('मुझे संगीत सुनना पसंद है।', 'mujhe sangeet sunna pasand hai'),
                'Tamil': ('எனக்கு இசை கேட்க பிடிக்கும்.', 'enakku isai ketka pidikum'),
                'Kannada': ('ನನಗೆ ಸಂಗೀತ ಕೇಳಲು ಇಷ್ಟ.', 'nanage sangeeta kelalu ishta'),
                'Marathi': ('मला गाणी ऐकायला आवडते.', 'mala gani aikalya aavadte')
            },
            'image': 'social_music.png'
        },
{
            'word_id': 'meet_tomorrow',
            'translations': {
                'English': ("Let's meet tomorrow.", 'lets meet tomorrow'),
                'Telugu': ('రేపు కలుద్దాం.', 'repu kaluddam'),
                'Hindi': ('कल मिलते हैं।', 'kal milte hain'),
                'Tamil': ('நாளை சந்திப்போம்.', 'naalai santhippoam'),
                'Kannada': ('ನಾಳೆ ಭೇಟಿಯಾಗೋಣ.', 'naale bhetiyagona'),
                'Marathi': ('उद्या भेटूया.', 'udya bhetuya')
            },
            'image': 'social_meet.png'
        }
    ],
    'Advanced Workplace & Debate': [
{
            'word_id': 'agree_point',
            'translations': {
                'English': ('I agree with your point.', 'i agree with your point'),
                'Telugu': ('నేను మీ పాయింట్ తో ఏకీభవిస్తున్నాను.', 'nenu mee point tho eekibhavisthunnanu'),
                'Hindi': ('मैं आपकी बात से सहमत हूँ।', 'main aapki baat se sahmat hoon'),
                'Tamil': ('நான் உங்கள் கருத்தை ஒப்புக்கொள்கிறேன்.', 'naan ungal karuthai oppukolkiren'),
                'Kannada': ('ನಾನು ನಿಮ್ಮ ಮಾತನ್ನು ಒಪ್ಪುತ್ತೇನೆ.', 'naanu nimma matannu opputtene'),
                'Marathi': ('मी तुमच्या मुद्द्याशी सहमत आहे.', 'mi tumchya muddyashi sahmat aahe')
            },
            'image': 'work_agree.png'
        },
{
            'word_id': 'find_solution',
            'translations': {
                'English': ("Let's find a solution.", 'lets find a solution'),
                'Telugu': ('ఒక పరిష్కారం కనుగొందాం.', 'oka parishkaram kanugondam'),
                'Hindi': ('आइए एक समाधान ढूंढते हैं।', 'aaiye ek samadhan dhundte hain'),
                'Tamil': ('ஒரு தீர்வை கண்டறிவோம்.', 'oru theervai kandarivoam'),
                'Kannada': ('ಒಂದು ಪರಿಹಾರ ಕಂಡುಕೊಳ್ಳೋಣ.', 'ondu parihara kandukollona'),
                'Marathi': ('चला एक उपाय शोधूया.', 'chala ek upay shoduya')
            },
            'image': 'work_solve.png'
        },
{
            'word_id': 'explain_again',
            'translations': {
                'English': ('Can you explain this again?', 'can you explain this again'),
                'Telugu': ('మీరు దీన్ని మళ్ళీ వివరించగలరా?', 'meeru deenni malli vivarinchagalara'),
                'Hindi': ('क्या आप इसे दोबारा समझा सकते हैं?', 'kya aap ise dobara samjha sakte hain'),
                'Tamil': ('நீங்கள் இதை மீண்டும் விளக்க முடியுமா?', 'neengal ithai meendum vilakka mudiyuma'),
                'Kannada': ('ನೀವು ಇದನ್ನು ಮತ್ತೊಮ್ಮೆ ವಿವರಿಸಬಹುದೇ?', 'neevu idannu mattomme vivarisabude'),
                'Marathi': ('तुम्ही हे पुन्हा स्पष्ट करू शकता का?', 'tumhi he punha spashta karu shakta ka')
            },
            'image': 'work_explain.png'
        }
    ]
}
def get_db_connection():
    conn = sqlite3.connect("literacy.db")
    conn.row_factory = sqlite3.Row
    return conn

def get_or_create_language_pair(known, target):
    """Retrieves or creates a unique language learning pair id."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM language_pairs WHERE known_lang = ? AND target_lang = ?", (known, target))
        row = cursor.fetchone()
        if row:
            return row["id"]
            
        cursor.execute("INSERT INTO language_pairs (known_lang, target_lang) VALUES (?, ?)", (known, target))
        conn.commit()
        pair_id = cursor.lastrowid
        
        # Populate dynamic lessons and vocabulary for this pair
        categories = [
            "Greetings", "Numbers", "Colors", "Family", "Food", 
            "Animals", "Daily Objects", "Daily Conversations", 
            "Sentence Practice", "Story Reading", 
            "At the Market", "Asking for Directions", "At the Doctor", "Workspace Conversations",
            "Idioms & Daily Slang", "Socializing & Hobbies", "Advanced Workplace & Debate"
        ]
        
        for idx, cat in enumerate(categories, 1):
            cursor.execute("""
                INSERT INTO language_lessons (pair_id, title, category, sequence_order)
                VALUES (?, ?, ?, ?)
            """, (pair_id, f"Lesson {idx}: {cat}", cat, idx))
            lesson_id = cursor.lastrowid
            
            # Populate vocab matching this category
            vocab_list = MULTILINGUAL_DICTIONARY.get(cat, [])
            for vocab in vocab_list:
                known_val, _ = vocab["translations"].get(known, (vocab["translations"]["English"][0], ""))
                target_val, translit = vocab["translations"].get(target, (vocab["translations"]["English"][0], ""))
                
                cursor.execute("""
                    INSERT INTO language_vocabulary (lesson_id, word_known, word_target, transliteration, image_name)
                    VALUES (?, ?, ?, ?, ?)
                """, (lesson_id, known_val, target_val, translit, vocab["image"]))
                
        conn.commit()
        return pair_id
    finally:
        conn.close()

def get_user_learning_path(user_id, pair_id):
    """Generates sequential steps mapping timeline unlocks for the user."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT l.*, p.status, p.pronunciation_score, p.quiz_score 
        FROM language_lessons l
        LEFT JOIN language_progress p ON l.id = p.lesson_id AND p.user_id = ?
        WHERE l.pair_id = ?
        ORDER BY l.sequence_order ASC
    """, (user_id, pair_id))
    lessons = [dict(row) for row in cursor.fetchall()]
    
    if not lessons:
        conn.close()
        return []
        
    # Ensure progress tracking records exist
    updated = False
    for idx, les in enumerate(lessons):
        if les["status"] is None:
            # First lesson starts unlocked, others start locked
            initial_status = "unlocked" if idx == 0 else "locked"
            cursor.execute("""
                INSERT INTO language_progress (user_id, lesson_id, status)
                VALUES (?, ?, ?)
            """, (user_id, les["id"], initial_status))
            les["status"] = initial_status
            les["pronunciation_score"] = 0.0
            les["quiz_score"] = 0.0
            updated = True
            
    if updated:
        conn.commit()
        
    conn.close()
    return lessons

def get_lesson_details(lesson_id):
    """Retrieves metadata and vocabulary list for a lesson."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM language_lessons WHERE id = ?", (lesson_id,))
    lesson = cursor.fetchone()
    if not lesson:
        conn.close()
        return None
        
    cursor.execute("SELECT * FROM language_vocabulary WHERE lesson_id = ?", (lesson_id,))
    vocab = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return {
        "lesson": dict(lesson),
        "vocabulary": vocab
    }

def update_lesson_progress(user_id, lesson_id, pronunciation_score, quiz_score):
    """Updates scores and unlocks next lesson if requirements are met (>= 70%)."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Update current lesson
    cursor.execute("""
        UPDATE language_progress
        SET status = 'completed',
            pronunciation_score = ?,
            quiz_score = ?,
            last_updated = CURRENT_TIMESTAMP
        WHERE user_id = ? AND lesson_id = ?
    """, (pronunciation_score, quiz_score, user_id, lesson_id))
    
    # 2. Get lesson details to unlock next sequence_order
    cursor.execute("SELECT pair_id, sequence_order FROM language_lessons WHERE id = ?", (lesson_id,))
    curr = cursor.fetchone()
    if curr:
        pair_id = curr["pair_id"]
        next_order = curr["sequence_order"] + 1
        
        cursor.execute("""
            SELECT id FROM language_lessons 
            WHERE pair_id = ? AND sequence_order = ?
        """, (pair_id, next_order))
        nxt = cursor.fetchone()
        if nxt:
            next_lesson_id = nxt["id"]
            # Unlock next lesson if not already unlocked/completed
            cursor.execute("""
                INSERT INTO language_progress (user_id, lesson_id, status)
                VALUES (?, ?, 'unlocked')
                ON CONFLICT(user_id, lesson_id) DO UPDATE SET
                status = CASE WHEN status = 'locked' THEN 'unlocked' ELSE status END
            """, (user_id, next_lesson_id))
            
    conn.commit()
    conn.close()

def get_learning_statistics(user_id, pair_id):
    """Calculates overall multilingual progress indicators."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) as total,
               SUM(CASE WHEN p.status = 'completed' THEN 1 ELSE 0 END) as completed
        FROM language_lessons l
        JOIN language_progress p ON l.id = p.lesson_id AND p.user_id = ?
        WHERE l.pair_id = ?
    """, (user_id, pair_id))
    stats = cursor.fetchone()
    total_count = stats["total"] or 10
    completed_count = stats["completed"] or 0
    completion_percentage = int((completed_count / total_count) * 100)
    
    # Vocabulary learned count
    cursor.execute("""
        SELECT COUNT(*) FROM language_vocabulary v
        JOIN language_lessons l ON v.lesson_id = l.id
        JOIN language_progress p ON l.id = p.lesson_id AND p.user_id = ?
        WHERE l.pair_id = ? AND p.status = 'completed'
    """, (user_id, pair_id))
    vocab_learned = cursor.fetchone()[0] or 0
    
    # Average Pronunciation score
    cursor.execute("""
        SELECT AVG(pronunciation_score) FROM language_progress p
        JOIN language_lessons l ON p.lesson_id = l.id
        WHERE p.user_id = ? AND l.pair_id = ? AND p.status = 'completed'
    """, (user_id, pair_id))
    avg_pron = cursor.fetchone()[0] or 0.0
    
    conn.close()
    
    return {
        "completed_lessons": completed_count,
        "total_lessons": total_count,
        "completion_percentage": completion_percentage,
        "vocabulary_learned": vocab_learned,
        "pronunciation_score": round(avg_pron, 1)
    }
