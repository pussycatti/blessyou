import json, time
import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from bless_config import EXTENSION_PATH

def load_accounts():
    with open("bless_accounts.json") as f:
        return json.load(f)

def launch_browser_with_extension(account, index):
    options = uc.ChromeOptions()
    options.add_argument(f"--load-extension={EXTENSION_PATH}")
    options.add_argument(f"--user-data-dir=chrome_profiles/profile_{index}")
    driver = uc.Chrome(options=options)

    try:
        driver.get("chrome-extension://<EXT_ID>/popup.html")  # Replace <EXT_ID> with actual ID
        time.sleep(2)
        # Simulate login with token or manual UI if needed
        print(f"[+] Chrome node launched for {account['email']}")
    except Exception as e:
        print(f"[!] Error launching node for {account['email']}: {e}")
    return driver

def main():
    accounts = load_accounts()
    for i, acc in enumerate(accounts):
        print(f"\n[*] Launching 5 nodes for {acc['email']}")
        for j in range(5):
            launch_browser_with_extension(acc, i*5 + j)
            time.sleep(2)

if __name__ == "__main__":
    main()
