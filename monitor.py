import time
import requests
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from dotenv import load_dotenv
import os

load_dotenv() # This loads the variables from your .env file

# --- CONFIGURATION (SECURE FOR GITHUB) ---
WEBKIOSK_URL = "https://webkiosk.thapar.edu" 
USER_ID = os.environ.get("USER_ID")      
PASSWORD = os.environ.get("PASSWORD")    
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID = os.environ.get("CHAT_ID")

def send_telegram_alert(message):
    if not BOT_TOKEN: return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try: requests.post(url, data=data)
    except: pass

def check_grades():
    # HEADLESS MODE (Mandatory for Cloud)
    options = webdriver.ChromeOptions()
    options.add_argument("--headless") 
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        print("🔄 Opening Webkiosk...")
        driver.get(WEBKIOSK_URL)
        
        # --- LOGIN ---
        wait = WebDriverWait(driver, 10)
        try: driver.find_element(By.NAME, "Userid").send_keys(USER_ID)
        except: driver.find_element(By.XPATH, '/html/body/table/tbody/tr[4]/td[2]/table/tbody/tr/td/input[3]').send_keys(USER_ID)
        
        driver.find_element(By.XPATH, '/html/body/table/tbody/tr[4]/td[2]/table/tbody/tr/td/input[5]').send_keys(PASSWORD)
        driver.find_element(By.XPATH, '//*[@id="BTNSubmit"]').click()
        time.sleep(5) 

        # --- ROBUST NAVIGATION ---
        print("🔍 Searching for Exam Info menu...")
        driver.switch_to.default_content()
        all_frames = driver.find_elements(By.TAG_NAME, "frame")
        
        # 1. Open the Exam Info folder
        for i in range(len(all_frames)):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(i)
                # Look for the dropdown heading
                exam_folder = driver.find_elements(By.XPATH, "//*[contains(text(), 'Exam. Info')]")
                if exam_folder:
                    exam_folder[0].click()
                    print(f"✅ Opened Exam Info folder in frame {i}")
                    break
            except: continue

        time.sleep(2)

        # 2. Click specifically on 'Exam Marks'
        print("📊 Clicking 'Exam Marks' link...")
        marks_clicked = False
        for i in range(len(all_frames)):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(i)
                # We target the specific text seen in your screenshot
                marks_link = driver.find_elements(By.PARTIAL_LINK_TEXT, "Exam Marks")
                if marks_link:
                    marks_link[0].click()
                    marks_clicked = True
                    print(f"✅ Success: Clicked 'Exam Marks' in frame {i}")
                    break
            except: continue

        if not marks_clicked:
            print("❌ Error: Could not find 'Exam Marks' link in the menu.")
            driver.save_screenshot("menu_fail.png")
            return

        # 3. Handle the 'Show' button page
        time.sleep(2)
        print("🔘 Clicking 'Show' button...")
        driver.switch_to.default_content()
        
        show_found = False
        # Get frames again to ensure fresh reference
        all_frames = driver.find_elements(By.TAG_NAME, "frame")
        
        for i in range(len(all_frames)):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(i)
                # Try finding button by various attributes
                show_button = driver.find_elements(By.XPATH, "//input[@value='Show' or @name='btnShow' or @type='submit']")
                if show_button:
                    show_button[0].click()
                    show_found = True
                    print(f"✅ Clicked 'Show' button in frame {i}")
                    break
            except:
                continue

        if not show_found:
            print("⚠️ Show button not found in frames. Attempting direct click...")
            try:
                driver.switch_to.default_content()
                driver.find_element(By.XPATH, "//input[@value='Show']").click()
                show_found = True
            except:
                print("❌ Failed to click Show button.")

        time.sleep(5) # CRITICAL: Wait for table to render after click

        # --- DATA EXTRACTION ---
        print("📥 Looking for table-1...")
        current_text = ""
        driver.switch_to.default_content()
        
        # We must check EVERY frame again because clicking 'Show' 
        # often refreshes the data into a specific frame.
        data_frames = driver.find_elements(By.TAG_NAME, "frame")
        for i in range(len(data_frames)):
            try:
                driver.switch_to.default_content()
                driver.switch_to.frame(i)
                table_element = driver.find_elements(By.ID, "table-1")
                if table_element:
                    current_text = table_element[0].text
                    print(f"✅ Marks Table found in frame {i}!")
                    break
            except:
                continue

        if not current_text:
            print("❌ Error: Could not find the marks table 'table-1' in any frame.")
            # Let's take a screenshot for debugging if it fails
            driver.save_screenshot("debug_error.png")
            return

        # --- SCRAPE & DATA EXTRACTION ---
        current_lines = [line.strip() for line in current_text.split('\n') if line.strip()]

        def get_unique_key(line):
            parts = line.split()
            if len(parts) < 6: return None 
            # Reverse indexing for safety against variable subject name lengths
            event = parts[-4]
            subject = " ".join(parts[2:-4])
            return f"{subject.lower().replace(' ', '_')}_{event.lower()}"

        # 1. Map Current Session
        current_data_map = {}
        for line in current_lines:
            if any(x in line for x in ["Sr. No.", "Exam Code", "Subject"]): continue
            key = get_unique_key(line)
            if key: current_data_map[key] = line

        # 2. Load Memory
        old_keys = set()
        if os.path.exists("grades_data.txt"):
            with open("grades_data.txt", "r", encoding="utf-8") as f:
                for old_line in f:
                    old_key = get_unique_key(old_line.strip())
                    if old_key: old_keys.add(old_key)

        # 3. Compare & Alert
        new_updates_found = False
        for key, full_line in current_data_map.items():
            if key not in old_keys:
                new_updates_found = True
                parts = full_line.split()
                
                # --- NEW ROBUST PARSING LOGIC ---
                # 1. Find the index where the Subject Code (with brackets) exists
                code_index = -1
                for idx, p in enumerate(parts):
                    if "(" in p and ")" in p:
                        code_index = idx
                        break
                
                if code_index != -1 and len(parts) > code_index + 1:
                    # Subject is everything from index 2 up to the code
                    subject_name = " ".join(parts[2 : code_index + 1])
                    # Event is ALWAYS the very next word after the code
                    event = parts[code_index + 1]
                else:
                    # Fallback if code logic fails
                    event = parts[-4]
                    subject_name = " ".join(parts[2:-4])
                
                print(f"{subject_name} ({event})")
                msg = f"New Marks Alert ! Marks of {subject_name} - {event} have been uploaded. Check WebKiosk now!"
                send_telegram_alert(msg)

        # 4. Save Memory
        if new_updates_found or not os.path.exists("grades_data.txt"):
            with open("grades_data.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(current_lines))
            print("💾 Memory file updated successfully.")
        else:
            print("😴 No new unique subject-event entries found.")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    check_grades()