# AutoSnap: Automated Webpage Screenshot to WhatsApp Sender

## Overview
This tool is an automated solution designed to streamline the process of capturing webpage information and sharing it via WhatsApp. It reads a list of contacts and URLs from a CSV file, visits each URL to capture a full-page screenshot, and automatically sends the image (with an optional caption) to the designated WhatsApp contact.

The solution uses a **"Clipboard Injection" method** (copy-paste) to ensure high reliability when interacting with WhatsApp Web, bypassing common issues with file upload buttons and hidden inputs.

## Tools Used

* **Python 3.10+**: Core programming language.
* **Playwright**: For robust browser automation (navigating URLs, handling WhatsApp Web). preferred over Selenium for speed and stability.
* **Pandas**: For efficient reading and parsing of the CSV data.
* **PyWin32 & Pillow (PIL)**: For interacting with the Windows Clipboard to perform "Ctrl+V" paste operations, simulating natural user behavior.

## Prerequisites

* Windows OS (Required for `pywin32` clipboard functionality).
* Python 3.8 or higher installed.
* An active WhatsApp account on your mobile phone (for scanning the QR code).

## Installation

1.  **Clone or Download** this project folder.
2.  **Install Python Dependencies**:
    Open your terminal/command prompt in the project folder and run:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: This installs `playwright`, `pandas`, `pillow`, and `pywin32`)*

3.  **Install Browser Binaries**:
    Run the following command to download the necessary browsers for Playwright:
    ```bash
    playwright install
    ```

## Configuration

1.  Open the `contacts.csv` file.
2.  Add your contacts in the following format:
    * **name**: The name of the person (for file naming).
    * **whatsapp_number**: Phone number with country code (e.g., `919999999999`). **Do not use `+` or spaces.**
    * **url**: The full webpage link (e.g., `https://www.google.com`).
    * **caption**: (Optional) Text to send along with the image.

    **Example `contacts.csv`:**
    ```csv
    name,whatsapp_number,url,caption
    Test User,919876543210,[https://www.wikipedia.org](https://www.wikipedia.org),Here is the info you requested
    ```

## How to Run the Script

1.  **Start the Automation**:
    Run the main script from your terminal:
    ```bash
    python main.py
    ```

2.  **Login to WhatsApp**:
    * A Chromium browser window will open and load WhatsApp Web.
    * **Action Required**: Use your phone to scan the QR code displayed on the screen.
    * The script waits up to 60 seconds for you to log in.

3.  **Watch it Work**:
    * Once logged in, the script will automatically take over.
    * It will navigate to the URLs, save screenshots to the `screenshots/` folder, and send them one by one.
    * **Important**: Do not minimize the browser window or use the clipboard (Copy/Paste) while the script is running, as it relies on the active clipboard.

## Troubleshooting

* **"Login Timeout"**: If you don't scan the QR code within 60 seconds, the script will stop. Just run `python main.py` again.
* **Image not sending**: Ensure your phone has an active internet connection so WhatsApp Web can sync.
* **Invalid Number**: If a number is not on WhatsApp, the script will log an error and move to the next contact.