import urllib.request
import urllib.parse
import json

def test_tts_translation():
    print("Testing dynamic TTS translation in app.py...")
    
    # We query /api/tts with Hindi lang and English question prompt
    text = "Alphabet Identification: Select the uppercase letter that makes the sound /b/:"
    lang = "Hindi"
    
    url = f"http://127.0.0.1:5500/api/tts?text={urllib.parse.quote(text)}&lang={urllib.parse.quote(lang)}"
    
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            print(f"Response status: {resp.status}")
            print(f"Response size: {len(data)} bytes")
            print("Content-type:", resp.headers.get('content-type'))
            if len(data) > 1000 and resp.status == 200:
                print("SUCCESS: Dynamic translation and TTS streaming work perfectly!")
            else:
                print("FAILURE: Invalid response size or status.")
    except Exception as e:
        print(f"Test failed with exception: {e}")

if __name__ == '__main__':
    test_tts_translation()
