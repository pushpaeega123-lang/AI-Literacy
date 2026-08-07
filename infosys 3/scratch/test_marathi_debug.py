import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

from app import app

def test_debug():
    with app.test_client() as client:
        resp = client.get("/api/tts?text=%E0%A4%AE%E0%A4%BE%E0%A4%82%E0%A4%9C%E0%A4%B0&lang=Marathi")
        print("Status Code:", resp.status_code)
        print("Data Length:", len(resp.data))
        if resp.status_code != 200:
            print("Error Details:", resp.data.decode('utf-8'))

if __name__ == '__main__':
    try:
        test_debug()
    except Exception as e:
        import traceback
        traceback.print_exc()
