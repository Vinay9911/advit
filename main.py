import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright

# Configuration
CSV_FILE = 'contacts.csv'
SCREENSHOT_DIR = 'screenshots'
HEADLESS_MODE = False 

def ensure_directories():
    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

def send_whatsapp_message(page, number, image_path, caption):
    print(f"   -> Opening chat for {number}...")
    
    # 1. Open direct chat link
    page.goto(f"https://web.whatsapp.com/send?phone={number}")

    # 2. Wait for the chat to load (look for the message input box)
    try:
        # Increased timeout to 60s for slow loads
        page.wait_for_selector('div[contenteditable="true"]', timeout=60000)
    except:
        print(f"   [Error] Could not load chat for {number}. Number might be invalid.")
        return

    print("   -> Chat loaded. Uploading image...")

    # 3. Handle Image Upload (FIXED METHOD)
    try:
        # A. Click the "Attach" (Plus) icon to activate the DOM elements
        # We try multiple common selectors for the Attach button
        attach_btn = page.locator('div[title="Attach"]').or_(page.locator('span[data-icon="plus"]'))
        attach_btn.first.click()
        
        # B. Directly inject the file into the hidden input
        # We look for the input that accepts images
        file_input = page.locator('input[accept*="image"]')
        file_input.set_input_files(image_path)
        
    except Exception as e:
        print(f"   [!] Upload failed: {e}")
        return

    # 4. Handle Caption
    if caption:
        print("   -> Adding caption...")
        # Wait for the image preview window (caption bar)
        page.wait_for_selector('div[contenteditable="true"]', timeout=15000)
        page.keyboard.type(caption)
        time.sleep(1) 

    # 5. Click Send
    print("   -> Sending...")
    page.keyboard.press("Enter")
    
    # Wait for message to send
    time.sleep(5) 

def main():
    ensure_directories()
    
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print("Error: contacts.csv not found!")
        return

    with sync_playwright() as p:
        # Launch Browser
        browser = p.chromium.launch(headless=HEADLESS_MODE)
        context = browser.new_context()
        page = context.new_page()

        # --- STEP 1: Login ---
        print("=== STEP 1: WhatsApp Login ===")
        page.goto("https://web.whatsapp.com")
        print("PLEASE SCAN THE QR CODE ON THE BROWSER NOW.")
        
        # Wait until the search bar appears
        try:
            page.wait_for_selector("div[contenteditable='true']", timeout=60000)
        except:
            print("Login timeout. Please run again and scan faster.")
            browser.close()
            return
            
        print("Login detected! Starting automation...")

        # --- STEP 2: Iterate through Contacts ---
        for index, row in df.iterrows():
            name = row['name']
            number = str(row['whatsapp_number'])
            url = row['url']
            caption = row['caption'] if pd.notna(row['caption']) else ""

            print(f"\nProcessing {name} ({index + 1}/{len(df)})...")

            try:
                # A. Open URL and Screenshot
                print(f"   -> navigating to {url}")
                page.goto(url, timeout=30000)
                
                screenshot_filename = f"{SCREENSHOT_DIR}/{name.replace(' ', '_')}.png"
                page.screenshot(path=screenshot_filename, full_page=True)
                print(f"   -> Screenshot saved: {screenshot_filename}")

                # B. Send via WhatsApp
                send_whatsapp_message(page, number, screenshot_filename, caption)
                print("   -> Done!")

            except Exception as e:
                print(f"   [!] Error processing {name}: {e}")

        print("\n=== All tasks completed. Closing browser in 5 seconds. ===")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()