import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def test_landing_voice():
    # Setup Chrome
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Enable console log capture
    options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("Navigating to landing page...")
        driver.get("http://127.0.0.1:5500/")
        time.sleep(3)
        
        # Check console logs
        print("\n--- Initial Console Logs ---")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"[{log['level']}] {log['message']}")
            
        # Find Tamil badge and click it
        print("\nClicking Tamil language badge...")
        tamil_badge = driver.find_element(By.ID, "badge-tamil")
        tamil_badge.click()
        time.sleep(2)
        
        # Check logs again
        print("\n--- Console Logs after clicking Tamil ---")
        logs = driver.get_log('browser')
        for log in logs:
            print(f"[{log['level']}] {log['message']}")
            
    finally:
        driver.quit()

if __name__ == '__main__':
    test_landing_voice()
