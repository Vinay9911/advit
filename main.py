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
    page.goto(f"https://web.whatsapp.com/send?phone={number}")

    # --- FIX: BETTER LOADING CHECK ---
    # We wait specifically for the 'footer' element (where the type bar is).
    # If this times out, it means the chat didn't open (or number is invalid).
    try:
        page.wait_for_selector('footer', timeout=20000)
        print("   -> Chat verified (Footer loaded).")
    except:
        print(f"   [!] Error: Chat footer did not load for {number}. Number might be invalid or popup blocked it.")
        return

    # --- FIX: ROBUST UPLOAD ---
    print("   -> Uploading image...")
    try:
        # 1. Click the "+" (Attach) button. 
        # We look for the button explicitly inside the footer to be safe.
        # Common selectors: title="Attach" or data-icon="plus"
        attach_button = page.locator('div[title="Attach"]').or_(page.locator('span[data-icon="plus"]'))
        attach_button.first.click()
        
        # 2. Upload the file to the hidden input
        # Once the menu is open, the input[type='file'] becomes available/active
        page.locator('input[type="file"]').set_input_files(image_path)
        
    except Exception as e:
        print(f"   [!] Upload failed: {e}")
        return

    # Handle Caption
    if caption:
        print("   -> Adding caption...")
        # Wait for the caption input box (it appears after file selection)
        try:
            page.wait_for_selector('div[aria-label="Add a caption"]', timeout=10000)
            page.locator('div[aria-label="Add a caption"]').type(caption)
        except:
            # Fallback if aria-label changes
            page.keyboard.type(caption)
            
        time.sleep(1) 

    # Click Send
    print("   -> Sending...")
    page.keyboard.press("Enter")
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

        # --- STEP 1: Login ---
        print("=== STEP 1: WhatsApp Login ===")
        page.goto("https://web.whatsapp.com")
        print("PLEASE SCAN THE QR CODE ON THE BROWSER NOW.")
        
        # Wait for the sidebar to load (indicates login success)
        try:
            page.wait_for_selector("#pane-side", timeout=60000)
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
                # Screenshot
                print(f"   -> navigating to {url}")
                page.goto(url, timeout=45000)
                screenshot_filename = f"{SCREENSHOT_DIR}/{name.replace(' ', '_')}.png"
                page.screenshot(path=screenshot_filename, full_page=True)
                print(f"   -> Screenshot saved")

                # Send
                send_whatsapp_message(page, number, screenshot_filename, caption)
                print("   -> Done!")

            except Exception as e:
                print(f"   [!] Error processing {name}: {e}")

        print("\n=== All tasks completed. Closing browser in 5 seconds. ===")
        time.sleep(5)
        browser.close()

if __name__ == "__main__":
    main()