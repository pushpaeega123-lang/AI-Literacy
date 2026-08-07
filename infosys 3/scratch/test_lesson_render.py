import sqlite3
import sys
sys.path.append('.')
sys.stdout.reconfigure(encoding='utf-8')
from app import app

# Create a test client
client = app.test_client()

# Enable session tracking
with client.session_transaction() as sess:
    sess['user_id'] = 10028
    sess['email'] = 'testuser@example.com'
    sess['fullname'] = 'Test User'
    sess['preferred_language'] = 'Hindi'
    sess['learning_language'] = 'English'
    sess['age'] = '3'

# Send mock request
print("Sending mock request to /lesson/1...")
response = client.get('/lesson/1')
html = response.data.decode('utf-8')

print(f"Response status: {response.status_code}")
if response.status_code == 302:
    print(f"Redirect Location: {response.headers.get('Location')}")
assert response.status_code == 200, "Failed to load lesson 1"

# Check if sentence translation matches Hindi SENTENCE_TRANSLATIONS dictionary
print("Checking sentence translations...")
expected_trans = "वर्णमाला सीखें: ए सेब के लिए है, बी गेंद के लिए है"
if expected_trans in html:
    print("SUCCESS: Found Hindi sentence translation in rendered HTML!")
else:
    print("FAILED: Hindi sentence translation not found!")

# Check if word-by-word breakdown has correct Hindi dictionary translation
print("Checking word breakdowns...")
expected_word = "सेब" # for apple
if expected_word in html:
    print("SUCCESS: Found Hindi word mapping 'सेब' in breakdown chips!")
else:
    print("FAILED: Hindi word mapping 'सेब' not found!")

# Check if voice assessment modal is present
print("Checking Voice Assessment modal layout...")
if "voicePracticeModal" in html:
    print("SUCCESS: Voice Assessment modal is present in HTML!")
else:
    print("FAILED: Voice Assessment modal is missing!")

if "Voice Assessment" in html:
    print("SUCCESS: Voice Assessment title is present in modal header!")
else:
    print("FAILED: Voice Assessment title is missing!")

if "accuracy-stars" in html:
    print("SUCCESS: Accuracy stars container is present in modal body!")
else:
    print("FAILED: Accuracy stars container is missing!")
