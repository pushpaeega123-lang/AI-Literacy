import urllib.request
import urllib.parse
import json

def test_telugu_tts():
    text = "నమస్కారం! ప్రాంతీయ అక్షరాస్యత కోచ్‌కు స్వాగతం. నేను లూమి, మీ వ్యక్తిగత AI ట్యూటర్. ఈ ప్లాట్‌ఫారమ్ పిల్లలు మరియు పెద్దలకు ప్రాథమిక అక్షరాస్యతను సులభంగా నేర్చుకోవడానికి సహాయపడుతుంది. మీరు ఇంటరాక్టివ్ పాఠాలు చదవవచ్చు, వ్రాయవచ్చు మరియు ఆటలు ఆడవచ్చు. నేర్చుకోవడం ప్రారంభించడానికి, దయచేసి కింద లాంగ్వేజ్ ఎంచుకుని గెట్ స్టార్టెడ్ క్లిక్ చేయండి."
    lang = "Telugu"
    
    url = f"http://127.0.0.1:5500/api/tts?text={urllib.parse.quote(text)}&lang={urllib.parse.quote(lang)}"
    
    try:
        # Start server locally first to process the request
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read()
            print("Response Status:", resp.status)
            print("Response Length:", len(data))
            if resp.status == 200 and len(data) > 10000:
                print("SUCCESS: Telugu TTS with 'AI' processed and generated successfully!")
            else:
                print("FAILURE: Invalid size or response status.")
    except Exception as e:
        print("Error during request:", e)

if __name__ == '__main__':
    # Start app server temporarily
    import subprocess
    import time
    p = subprocess.Popen(["python", "app.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    time.sleep(2)
    try:
        test_telugu_tts()
    finally:
        p.terminate()
