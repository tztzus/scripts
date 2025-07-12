import threading
import requests
import random
import string
import time
import re

WEBHOOK_URL = ('https://discord.com/api/webhooks/1392815153271275640/dSPbzVx5qptvlXCibjBWgbAyyOVWMnk89anLmA477_IMDAbw9HqlrzqNl0obUtA8n0MW')
BASE_URL_PREFIX = (
    "https://auth.roblox.com/v1/usernames/validate"
    "?birthday=1992-12-31T23:00:00.000Z&context=Signup&username="
)

# ------------ global counters and locks ------------
username_counter = 0
counter_lock = threading.Lock()
webhook_lock = threading.Lock()

# ------------ generators ------------

def generate_repeater() -> str:
    prefix_len = random.randint(2, 4)
    prefix = ''.join(random.choices(string.digits, k=prefix_len))
    repeat_digit = random.choice("0123456789")
    repeat_count = random.randint(10, 15)
    return prefix + repeat_digit * repeat_count

def generate_binary_growth(base: str) -> str:
    return base + random.choice("01")

def generate_number_growth(base: int) -> int:
    return base + 1

def generate_full_random(length: int | None = None) -> str:
    if length is None:
        length = random.randint(3, 19)
    charset = string.ascii_lowercase + string.digits
    return ''.join(random.choices(charset, k=length))

# ------------ filtering ------------

def is_repeating_pattern(username: str) -> bool:
    for size in range(1, 5):
        pattern = username[:size]
        if pattern * (20 // len(pattern)) == username[: len(pattern) * (20 // len(pattern))]:
            return True
    return False

def should_skip(username: str) -> bool:
    if len(username) != 20:
        return False
    if username.isdigit():
        return False
    if all(c in "01" for c in username):
        return False
    if is_repeating_pattern(username):
        return False
    return True  # skip all other 20‑char usernames

# ------------ API check ------------

def check_username(username: str) -> bool:
    url = BASE_URL_PREFIX + username
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code != 200:
            return False
        data = r.json()
        code = data.get("code")
        return code == 0 and data.get("message", "").lower() == "username is valid"
    except Exception:
        return False

# ------------ webhook ------------

def send_to_webhook(username: str, number: int) -> None:
    length = len(username)
    payload = {"content": f"✅ Available Roblox username: **{username}** [#{number}] (length: {length})"}
    with webhook_lock:
        try:
            requests.post(WEBHOOK_URL, json=payload, timeout=5)
            time.sleep(1)  # delay between webhook sends
        except Exception:
            pass

# ------------ worker thread ------------

def worker() -> None:
    mode = random.choice(["repeater", "binary-growth", "number-growth"])
    binary_base = ''.join(random.choices("01", k=6))
    number_base = random.randint(100000, 999999)

    while True:
        if random.random() < 0.00001:
            username = generate_full_random(20)  # 1 % chance full‑random 20 chars
        elif mode == "repeater":
            username = generate_repeater()
        elif mode == "binary-growth":
            binary_base = generate_binary_growth(binary_base)
            username = binary_base
        elif mode == "number-growth":
            number_base = generate_number_growth(number_base)
            username = str(number_base)
        else:
            username = generate_full_random()

        if should_skip(username):
            continue

        if 3 <= len(username) <= 20 and check_username(username):
            with counter_lock:
                global username_counter
                username_counter += 1
                n = username_counter
            length = len(username)
            print(f"[+] {username} [#{n}] (length: {length})")
            send_to_webhook(username, n)

        time.sleep(0.1)

# ------------ main ------------

def main(thread_count: int = 5) -> None:
    print("[!] Starting Roblox Username Scanner with 5 threads...")
    for _ in range(thread_count):
        threading.Thread(target=worker, daemon=True).start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Exiting...")

if __name__ == "__main__":
    main()
