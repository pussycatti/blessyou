import requests, random, string, json, time, csv
from bless_config import *
from mailslurp_client import Configuration, ApiClient, InboxControllerApi
from two_captcha import TwoCaptcha

def random_password(length=10):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def solve_captcha(sitekey, url):
    solver = TwoCaptcha(CAPTCHA_API_KEY)
    result = solver.hcaptcha(sitekey=sitekey, url=url)
    return result['code']

def create_temp_email():
    config = Configuration(api_key={"x-api-key": MAILSLURP_API_KEY})
    with ApiClient(config) as api_client:
        inbox_controller = InboxControllerApi(api_client)
        inbox = inbox_controller.create_inbox()
        return inbox.id, inbox.email_address

def get_verification_code(inbox_id):
    config = Configuration(api_key={"x-api-key": MAILSLURP_API_KEY})
    with ApiClient(config) as api_client:
        inbox_controller = InboxControllerApi(api_client)
        for _ in range(30):
            time.sleep(5)
            emails = inbox_controller.get_emails(inbox_id, min_count=1)
            if emails:
                body = inbox_controller.get_email(emails[0].id).body
                code = next((line for line in body.split() if line.isdigit() and len(line) == 6), None)
                return code
        return None

def register_account(email, password, captcha_token):
    payload = {
        "email": email,
        "password": password,
        "referralCode": REFERRAL_CODE,
        "hCaptchaToken": captcha_token
    }
    resp = requests.post("https://api.blessnet.work/api/auth/signup", json=payload)
    return resp.ok

def verify_account(email, code):
    payload = {"email": email, "code": code}
    r = requests.post("https://api.blessnet.work/api/auth/verify", json=payload)
    return r.ok

def login_and_get_token(email, password):
    r = requests.post("https://api.blessnet.work/api/auth/login", json={"email": email, "password": password})
    return r.json().get("token")

def load_proxies():
    try:
        with open("proxies.txt") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def main():
    count = int(input("How many accounts to create (1–1000)? "))
    proxies = load_proxies() if USE_PROXIES else []
    results = []

    for i in range(count):
        print(f"\n[*] Creating account #{i+1}")
        inbox_id, email = create_temp_email()
        password = random_password()

        captcha_token = solve_captcha("cc7cfc7e-97ad-4b08-8dfc-cacddd4cfc10", "https://app.blessnet.work/register")

        success = register_account(email, password, captcha_token)
        if not success:
            print(f"[!] Failed registration for {email}")
            continue

        code = get_verification_code(inbox_id)
        if not code:
            print(f"[!] Failed to get VC for {email}")
            continue

        if not verify_account(email, code):
            print(f"[!] Verification failed for {email}")
            continue

        token = login_and_get_token(email, password)
        if not token:
            print(f"[!] Login failed for {email}")
            continue

        print(f"[+] Success! {email}")
        results.append({
            "email": email,
            "password": password,
            "token": token,
            "nodes_activated": 0
        })

    with open("bless_accounts.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()
  
