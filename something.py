import requests
import random
import string
import time

BASE_URL_PREFIX = (
    "https://auth.roblox.com/v1/usernames/validate"
    "?birthday=1992-12-31T23:00:00.000Z&context=Signup&username="
)

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
    return True

def check_username(username: str) -> bool:
    url = BASE_URL_PREFIX + username
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=5)
        if r.status_code != 200:
            return False
        data = r.json()
        code = data.get("code")
        return code == "UsernameOK" or code == 0 or data.get("message","").lower() == "username is valid"
    except Exception:
        return False

def generate_candidate(mode, binary_base, number_base):
    if random.random() < 0.01:
        return generate_full_random(20), binary_base, number_base
    if mode == "repeater":
        return generate_repeater(), binary_base, number_base
    elif mode == "binary-growth":
        binary_base = generate_binary_growth(binary_base)
        return binary_base, binary_base, number_base
    elif mode == "number-growth":
        number_base = generate_number_growth(number_base)
        return str(number_base), binary_base, number_base
    else:
        return generate_full_random(), binary_base, number_base

def main():
    print("[*] Starting 50 username checks...")
    mode = random.choice(["repeater", "binary-growth", "number-growth"])
    binary_base = ''.join(random.choices("01", k=6))
    number_base = random.randint(100000, 999999)
    found_usernames = []
    count = 0
    while count < 50:
        username, binary_base, number_base = generate_candidate(mode, binary_base, number_base)
        if should_skip(username):
            continue
        if 3 <= len(username) <= 20:
            count += 1
            is_available = check_username(username)
            status = "AVAILABLE" if is_available else "taken/invalid"
            print(f"[{count:02d}] {username} → {status}")
            if is_available:
                found_usernames.append(username)
        time.sleep(0.1)
    print("\n[+] Found available usernames:")
    for u in found_usernames:
        print(u)

if __name__ == "__main__":
    main()
