import os
import time
import pandas as pd
from io import BytesIO
from PIL import Image
import win32clipboard 
from playwright.sync_api import sync_playwright

# Configuration
CSV_FILE = 'contacts.csv'
SCREENSHOT_DIR = 'screenshots'
HEADLESS_MODE = False 

def ensure_directories():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

def copy_to_clipboard(image_path):
    image = Image.open(image_path)
    output = BytesIO()
    image.convert("RGB").save(output, "BMP")
    data = output.getvalue()[14:]
    output.close()
    
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()

def send_whatsapp_message(page, number, image_path, caption):
    print(f"   -> Opening chat for {number}...")
    page.goto(f"https://web.whatsapp.com/send?phone={number}")

    # 1. Wait for Chat
    try:
        # Wait for the main chat input box
        page.wait_for_selector('footer div[contenteditable="true"]', timeout=30000)
        page.click('footer div[contenteditable="true"]')
        print("   -> Chat focused.")
    except:
        print(f"   [!] Error: Chat not found for {number}")
        return

    # 2. PASTE (Ctrl+V)
    try:
        copy_to_clipboard(image_path)
        print("   -> Pasting image...")
        page.keyboard.press("Control+V")
        
        # --- FIX: BLIND WAIT ---
        # Instead of waiting for a specific selector that might fail,
        # we just wait 3 seconds for the image preview to load visually.
        time.sleep(3) 
        
    except Exception as e:
        print(f"   [!] Paste failed: {e}")
        return

    # 3. TYPE CAPTION & SEND
    if caption:
        print("   -> Typing caption...")
        page.keyboard.type(caption)
        time.sleep(1)

    print("   -> Sending (Enter)...")
    page.keyboard.press("Enter")
    
    # Wait for upload to finish
    time.sleep(5) 

def main():
    ensure_directories()
    
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("Error: contacts.csv not found!")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context()
        page = context.new_page()

        print("=== STEP 1: WhatsApp Login ===")
        page.goto("https://web.whatsapp.com")
        print("PLEASE SCAN QR CODE NOW.")
        
        try:
            page.wait_for_selector("#pane-side", timeout=60000)
            print("Login success!")
        except:
            print("Login timeout.")
            return

        for index, row in df.iterrows():
            name = row['name']
            number = str(row['whatsapp_number'])
            url = row['url']
            caption = row['caption'] if pd.notna(row['caption']) else ""

            print(f"\nProcessing {name}...")
            
            try:
                # Screenshot
                page.goto(url, timeout=60000)
                path = f"{SCREENSHOT_DIR}/{name.replace(' ', '_')}.png"
                page.screenshot(path=path, full_page=True)
                
                # Send
                send_whatsapp_message(page, number, path, caption)
                print("   -> Done!")
                
            except Exception as e:
                print(f"   [!] Error: {e}")

        print("\n=== Closing in 5s ===")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()