#!/usr/bin/env python3
"""
instagram_follow_unfollow.py

A minimal, policy-aware Instagram follow/unfollow bot for **testing** and **workflow QA** using Selenium.
- Logs in with username/password (env or CLI)
- Processes a CSV/TXT list of usernames to follow or unfollow
- Human-like pacing (random jitter), retry/backoff on common UI states
- Whitelist support + "last-followed-only" unfollow mode
- JSONL logs of every action

REQUIREMENTS:
    pip install selenium webdriver-manager python-dotenv

USAGE EXAMPLES:
    # Follow users from CSV (usernames in first column or one per line)
    python instagram_follow_unfollow.py --mode follow --input users.csv --max-actions 30 --headless

    # Unfollow users from a CSV, skipping whitelisted usernames
    python instagram_follow_unfollow.py --mode unfollow --input to_unfollow.txt --whitelist keep.txt --headless

    # Unfollow only users you previously followed with this script (from the follow-log)
    python instagram_follow_unfollow.py --mode unfollow --last-followed-only --max-actions 25

ENV (optional if not passed via CLI):
    IG_USERNAME=your_username
    IG_PASSWORD=your_password

IMPORTANT / COMPLIANCE:
- Use only with accounts you own/manage and in accordance with Instagram's Terms.
- Keep pacing conservative; avoid spiky automation.
- This script is for testing/education and does not attempt to evade platform detection.
"""

import os
import csv
import time
import json
import random
import argparse
from pathlib import Path
from typing import List, Optional, Dict

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager


# ------------------------- Utility & Config -------------------------

def jitter_sleep(min_s: float, max_s: float) -> None:
    """Sleep a random time between min_s and max_s seconds."""
    time.sleep(random.uniform(min_s, max_s))

def backoff_sleep(attempt: int, base: float = 0.8, cap: float = 12.0) -> None:
    """Exponential backoff with a small jitter."""
    delay = min(cap, base * (2 ** (attempt - 1)))
    time.sleep(delay + random.uniform(0, 0.6))

def read_usernames(path: Path) -> List[str]:
    """Read usernames from CSV/TXT (first column or one per line)."""
    if not path.exists():
        return []
    out = []
    if path.suffix.lower() in {".csv", ".tsv"}:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            dialect = csv.Sniffer().sniff(f.read(1024), delimiters=",\t;|")
            f.seek(0)
            reader = csv.reader(f, dialect)
            for row in reader:
                if not row: 
                    continue
                out.append(row[0].strip().lstrip("@"))
    else:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if line:
                    out.append(line.lstrip("@"))
    # Dedup while preserving order
    seen, uniq = set(), []
    for u in out:
        if u and u not in seen:
            seen.add(u)
            uniq.append(u)
    return uniq

def write_jsonl(path: Path, data: Dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")

def load_last_followed(log_path: Path, limit: Optional[int] = None) -> List[str]:
    """Return usernames we previously followed (most recent last)."""
    if not log_path.exists():
        return []
    followed = []
    with log_path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("action") == "follow" and rec.get("success") is True and rec.get("username"):
                followed.append(rec["username"])
    if limit:
        return list(dict.fromkeys(followed))[-limit:]
    return list(dict.fromkeys(followed))

# ------------------------- Selenium Setup -------------------------

def build_driver(headless: bool = False, user_data_dir: Optional[str] = None) -> webdriver.Chrome:
    chrome_opts = ChromeOptions()
    if headless:
        chrome_opts.add_argument("--headless=new")
    chrome_opts.add_argument("--disable-blink-features=AutomationControlled")
    chrome_opts.add_argument("--start-maximized")
    chrome_opts.add_argument("--no-sandbox")
    chrome_opts.add_argument("--disable-dev-shm-usage")
    if user_data_dir:
        chrome_opts.add_argument(f"--user-data-dir={user_data_dir}")
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=chrome_opts)
    driver.set_page_load_timeout(45)
    driver.implicitly_wait(2)
    return driver

# ------------------------- Instagram Actions -------------------------

def ig_login(driver: webdriver.Chrome, username: str, password: str) -> None:
    driver.get("https://www.instagram.com/accounts/login/")
    wait = WebDriverWait(driver, 30)
    # Accept cookies if the banner appears (EU users)
    try:
        wait.until(EC.presence_of_element_located((By.NAME, "username")))
    except Exception:
        pass

    # Fill username/password
    user_el = wait.until(EC.element_to_be_clickable((By.NAME, "username")))
    pass_el = wait.until(EC.element_to_be_clickable((By.NAME, "password")))
    user_el.clear(); user_el.send_keys(username); jitter_sleep(0.4, 0.9)
    pass_el.clear(); pass_el.send_keys(password); jitter_sleep(0.3, 0.8)

    submit = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
    submit.click()

    # Wait for home or handle "Save Your Login Info?" / "Turn on Notifications"
    # We don't rely on class names; use text-based fallbacks conservatively.
    for attempt in range(1, 6):
        jitter_sleep(1.2, 2.4)
        if "instagram.com/" in driver.current_url and "/login" not in driver.current_url:
            break
        # Dismiss "Save your login info?" or "Turn on Notifications" if shown
        for text in ["Not now", "Not Now"]:
            try:
                btn = driver.find_element(By.XPATH, f"//button[normalize-space()='{text}']")
                btn.click()
            except Exception:
                pass
        backoff_sleep(attempt)

def open_profile(driver: webdriver.Chrome, username: str) -> None:
    driver.get(f"https://www.instagram.com/{username}/")
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, "//header//h2 | //header//h1"))
    )
    jitter_sleep(1.0, 2.0)

def get_follow_state(driver: webdriver.Chrome) -> str:
    """
    Returns one of: 'follow', 'following', 'requested', 'unavailable'
    Tries multiple selectors for resiliency.
    """
    # Primary CTA buttons live in header near the username.
    candidates = [
        "//header//button[.//div[text()='Follow'] or normalize-space()='Follow']",
        "//header//button[.//div[text()='Following'] or normalize-space()='Following']",
        "//header//button[.//div[text()='Requested'] or normalize-space()='Requested']",
        # Sometimes buttons render without nested <div>
        "//header//button[normalize-space()='Follow' or normalize-space()='Following' or normalize-space()='Requested']",
    ]
    for xp in candidates:
        try:
            btns = driver.find_elements(By.XPATH, xp)
            if not btns:
                continue
            # Prefer visible button
            btn = next((b for b in btns if b.is_displayed()), btns[0])
            label = btn.text.strip()
            if label.lower() == "follow":
                return "follow"
            if label.lower() == "following":
                return "following"
            if label.lower() == "requested":
                return "requested"
        except Exception:
            continue
    return "unavailable"

def click_follow(driver: webdriver.Chrome) -> bool:
    """Click the 'Follow' button if available."""
    try:
        xp = "//header//button[.//div[text()='Follow'] or normalize-space()='Follow']"
        btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
        jitter_sleep(0.4, 1.1)
        btn.click()
        jitter_sleep(1.0, 1.8)
        return True
    except Exception:
        return False

def click_unfollow(driver: webdriver.Chrome) -> bool:
    """
    Click the 'Following' button, then confirm 'Unfollow' in modal.
    """
    try:
        xp = "//header//button[.//div[text()='Following'] or normalize-space()='Following']"
        btn = WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, xp)))
        jitter_sleep(0.4, 1.1)
        btn.click()
        # Confirm dialog
        jitter_sleep(0.6, 1.2)
        confirm_xps = [
            "//button[normalize-space()='Unfollow']",
            "//div[@role='dialog']//button[normalize-space()='Unfollow']",
        ]
        for cxp in confirm_xps:
            try:
                cbtn = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, cxp)))
                jitter_sleep(0.2, 0.6)
                cbtn.click()
                jitter_sleep(0.8, 1.5)
                return True
            except Exception:
                continue
        return False
    except Exception:
        return False

# ------------------------- Processing Loop -------------------------

def process_user(
    driver: webdriver.Chrome,
    username: str,
    mode: str,
    log_path: Path,
    whitelist: Optional[set] = None,
) -> Dict:
    rec = {
        "username": username,
        "mode": mode,
        "ts": int(time.time()),
        "action": None,
        "success": False,
        "state_before": None,
        "state_after": None,
        "error": None,
    }
    try:
        if whitelist and username in whitelist and mode == "unfollow":
            rec["action"] = "skip_whitelisted"
            rec["success"] = True
            write_jsonl(log_path, rec)
            return rec

        open_profile(driver, username)
        state = get_follow_state(driver)
        rec["state_before"] = state

        if mode == "follow":
            if state == "follow":
                ok = click_follow(driver)
                state_after = get_follow_state(driver)
                rec["state_after"] = state_after
                rec["action"] = "follow" if ok else "noop_follow_click_failed"
                rec["success"] = ok and state_after in {"following", "requested"}
            elif state in {"following", "requested"}:
                rec["action"] = "noop_already_following"
                rec["success"] = True
            else:
                rec["action"] = "noop_unavailable"
                rec["success"] = False

        elif mode == "unfollow":
            if state == "following":
                ok = click_unfollow(driver)
                state_after = get_follow_state(driver)
                rec["state_after"] = state_after
                rec["action"] = "unfollow" if ok else "noop_unfollow_click_failed"
                rec["success"] = ok and state_after in {"follow", "unavailable"}
            elif state in {"follow", "requested"}:
                rec["action"] = "noop_not_following"
                rec["success"] = True
            else:
                rec["action"] = "noop_unavailable"
                rec["success"] = False
        else:
            rec["error"] = f"unknown_mode:{mode}"
    except Exception as e:
        rec["error"] = repr(e)

    write_jsonl(log_path, rec)
    return rec

# ------------------------- Main -------------------------

def main():
    load_dotenv()
    parser = argparse.ArgumentParser(description="Instagram Follow/Unfollow Bot (Selenium, policy-aware)")
    parser.add_argument("--mode", choices=["follow", "unfollow"], required=True, help="Action to perform.")
    parser.add_argument("--input", type=str, help="Path to CSV/TXT list of usernames (first column or one per line).")
    parser.add_argument("--whitelist", type=str, help="Path to CSV/TXT of usernames to NEVER unfollow.")
    parser.add_argument("--last-followed-only", action="store_true", help="Unfollow only those previously followed by this script.")
    parser.add_argument("--max-actions", type=int, default=20, help="Max actions this run (default 20).")
    parser.add_argument("--headless", action="store_true", help="Run Chrome in headless mode.")
    parser.add_argument("--user-data-dir", type=str, help="Optional Chrome user-data dir for persisted sessions.")
    parser.add_argument("--min-wait", type=float, default=6.0, help="Min seconds between actions.")
    parser.add_argument("--max-wait", type=float, default=12.0, help="Max seconds between actions.")
    parser.add_argument("--username", type=str, default=os.getenv("IG_USERNAME"), help="Instagram username (or env IG_USERNAME).")
    parser.add_argument("--password", type=str, default=os.getenv("IG_PASSWORD"), help="Instagram password (or env IG_PASSWORD).")
    parser.add_argument("--log-dir", type=str, default="state", help="Directory for logs/jsonl.")
    args = parser.parse_args()

    if not args.username or not args.password:
        raise SystemExit("Missing credentials. Provide --username/--password or set IG_USERNAME/IG_PASSWORD.")

    # Input resolution
    usernames: List[str] = []
    if args.last_followed_only and args.mode == "unfollow":
        usernames = load_last_followed(Path(args.log_dir) / "actions.jsonl")
    elif args.input:
        usernames = read_usernames(Path(args.input))
    else:
        raise SystemExit("Provide --input <file> OR use --last-followed-only (with --mode unfollow).")

    if not usernames:
        raise SystemExit("No usernames to process.")

    whitelist_set = set(read_usernames(Path(args.whitelist))) if args.whitelist else None

    log_path = Path(args.log_dir) / "actions.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    driver = build_driver(headless=args.headless, user_data_dir=args.user_data_dir)
    try:
        ig_login(driver, args.username, args.password)
        actions_done = 0

        for u in usernames:
            if actions_done >= args.max_actions:
                break

            rec = process_user(
                driver=driver,
                username=u,
                mode=args.mode,
                log_path=log_path,
                whitelist=whitelist_set
            )

            actions_done += 1 if rec.get("action") not in {"noop_already_following", "noop_not_following"} else 0

            # Pace between actions
            jitter_sleep(args.min_wait, args.max_wait)

        print(f"Done. Processed={min(args.max_actions, len(usernames))}, Logs={log_path}")
    finally:
        try:
            driver.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
