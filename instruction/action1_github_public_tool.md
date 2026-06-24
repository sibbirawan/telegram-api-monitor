# Action 1: Build & Publish a Generic Public Tool on GitHub
**Goal:** Turn your existing TelegramBotApi project into a public, generic, working tool that acts as your portfolio proof — replacing the need for client reviews.
**Time required:** 3–5 hours total (spread over 2 days)
**Impact:** Clients find working code → trust is built before first conversation

---

## Why This Works
A zero-review freelancer saying "I can build this" is ignored.
A zero-review freelancer with a public GitHub repo showing a working tool gets hired.
You already have 90% of the code in TelegramBotApi. This is mostly renaming and cleaning.

---

## Step 1: Create Your GitHub Account (15 min)

### Full Process
1. Go to https://github.com
2. Click **Sign up**
3. Use a professional username — ideally your name: `sibbir-awan` or `awan-automation`
4. Verify email
5. Go to **Settings → Profile**
   - Add a profile photo (same as your Fiverr photo)
   - Bio: `Python automation engineer | Telegram bots | REST API | Excel pipelines | Bangladesh`
   - Add your location: `Dhaka, Bangladesh`
   - Add your website (Fiverr link once created)

### Shortcut
Skip all the optional GitHub tour steps. Go directly to profile settings after email verification.

---

## Step 2: Choose Which Generic Tool to Build (10 min)

Pick ONE. Do not build all three.

| Option | What it does | Who buys it |
|---|---|---|
| **A (Recommended)** | Monitors any REST API on schedule → sends Telegram alert when value crosses threshold | Small businesses, developers, ops teams |
| B | Reads Google Sheet → sends daily Telegram summary | Business owners, team leads |
| C | Monitors website price → sends Telegram alert | E-commerce sellers, buyers |

**Recommendation: Option A.** Your TelegramBotApi already does exactly this for telecom alarms. You just replace alarm-specific logic with generic threshold logic.

---

## Step 3: Prepare Your Local Environment (20 min)

```powershell
# Create a new project folder (do NOT copy your work project — start clean)
mkdir C:\Projects\telegram-api-monitor
cd C:\Projects\telegram-api-monitor

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install requests pandas pyyaml schedule
```

---

## Step 4: Write the Generic Tool (2–3 hours)

### File structure to create:
```
telegram-api-monitor/
├── monitor.py          # main script
├── config.yaml         # all settings here, no hardcoding
├── requirements.txt    # dependencies
└── README.md           # critical — this is what clients read
```

### config.yaml
```yaml
# All configuration here. Never hardcode credentials in monitor.py

TELEGRAM:
  bot_token: "YOUR_BOT_TOKEN_HERE"      # get from @BotFather on Telegram
  chat_id: "YOUR_CHAT_ID_HERE"          # your group or personal chat ID

API:
  url: "https://api.example.com/data"   # replace with your target API
  method: "GET"                          # GET or POST
  headers:
    Content-Type: "application/json"
  auth:
    type: "basic"                        # basic / bearer / none
    username: "YOUR_USERNAME"
    password: "YOUR_PASSWORD"
  response_field: "value"               # which field in the JSON response to monitor

MONITOR:
  check_interval_minutes: 30            # how often to check
  alert_threshold: 100                  # send alert if value exceeds this
  alert_on_change: true                 # also alert when value changes from last check
```

### monitor.py
```python
"""
telegram-api-monitor
Polls any REST API on a schedule and sends Telegram alerts when a threshold is crossed.
Author: your-github-username
"""

import os
import time
import logging
import requests
import yaml
import schedule
from datetime import datetime

# ── Logging setup ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


# ── Config loader ──────────────────────────────────────────────────────────────
def load_config(path: str = "config.yaml") -> dict:
    """Load YAML config. Raises FileNotFoundError if missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r") as f:
        return yaml.safe_load(f)


# ── Telegram sender ────────────────────────────────────────────────────────────
def send_telegram(token: str, chat_id: str, message: str) -> bool:
    """
    Send a message via Telegram Bot API.
    Returns True on success, False on failure.
    """
    if not token or not chat_id:
        log.error("Telegram token or chat_id is missing in config.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        response = requests.post(url, json=payload, timeout=10)
        response.raise_for_status()
        log.info("Telegram message sent successfully.")
        return True
    except requests.exceptions.Timeout:
        log.error("Telegram send timed out.")
    except requests.exceptions.HTTPError as e:
        log.error(f"Telegram HTTP error: {e.response.status_code} — {e.response.text}")
    except requests.exceptions.RequestException as e:
        log.error(f"Telegram send failed: {e}")
    return False


# ── API fetcher ────────────────────────────────────────────────────────────────
def fetch_api_value(cfg: dict) -> float | None:
    """
    Fetch a numeric value from the configured API.
    Returns float on success, None on any failure.
    """
    api = cfg.get("API", {})
    url = api.get("url")
    method = api.get("method", "GET").upper()
    headers = api.get("headers", {})
    field = api.get("response_field", "value")

    # Build auth
    auth = None
    auth_cfg = api.get("auth", {})
    if auth_cfg.get("type") == "basic":
        auth = (auth_cfg.get("username", ""), auth_cfg.get("password", ""))

    if not url:
        log.error("API URL is missing in config.")
        return None

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, auth=auth, timeout=15, verify=False)
        elif method == "POST":
            payload = api.get("payload", {})
            response = requests.post(url, headers=headers, auth=auth, json=payload, timeout=15, verify=False)
        else:
            log.error(f"Unsupported HTTP method: {method}")
            return None

        response.raise_for_status()
        data = response.json()

        # Support nested field paths like "data.metrics.count"
        for key in field.split("."):
            if isinstance(data, dict):
                data = data.get(key)
            else:
                log.error(f"Cannot navigate response field path '{field}'")
                return None

        return float(data) if data is not None else None

    except requests.exceptions.Timeout:
        log.error("API request timed out.")
    except requests.exceptions.HTTPError as e:
        log.error(f"API HTTP error: {e.response.status_code}")
    except (ValueError, TypeError) as e:
        log.error(f"Could not convert API response to float: {e}")
    except requests.exceptions.RequestException as e:
        log.error(f"API request failed: {e}")
    return None


# ── Main check job ─────────────────────────────────────────────────────────────
last_value: float | None = None  # module-level state between runs

def run_check(cfg: dict) -> None:
    """Fetch API value, compare to threshold, send Telegram alert if needed."""
    global last_value

    monitor = cfg.get("MONITOR", {})
    threshold = monitor.get("alert_threshold")
    alert_on_change = monitor.get("alert_on_change", False)

    tg = cfg.get("TELEGRAM", {})
    token = tg.get("bot_token")
    chat_id = tg.get("chat_id")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    log.info(f"Running check at {now}...")

    value = fetch_api_value(cfg)
    if value is None:
        log.warning("Skipping this cycle — API fetch returned no value.")
        return

    log.info(f"Current value: {value} | Threshold: {threshold} | Last: {last_value}")

    # Alert conditions
    should_alert = False
    reason = ""

    if threshold is not None and value > threshold:
        should_alert = True
        reason = f"⚠️ Value <b>{value}</b> exceeded threshold <b>{threshold}</b>"

    if alert_on_change and last_value is not None and value != last_value:
        should_alert = True
        reason += f"\n📊 Value changed: {last_value} → {value}"

    if should_alert:
        message = f"🤖 <b>API Monitor Alert</b>\n{reason}\n🕐 {now}"
        send_telegram(token, chat_id, message)

    last_value = value


# ── Entry point ────────────────────────────────────────────────────────────────
def main():
    try:
        cfg = load_config("config.yaml")
    except FileNotFoundError:
        log.error("Missing config.yaml. Copy config.example.yaml to config.yaml and fill values.")
        return

    interval = cfg.get("MONITOR", {}).get("check_interval_minutes", 30)

    log.info(f"Monitor started. Checking every {interval} minutes.")

    # Run immediately on start, then on schedule
    run_check(cfg)
    schedule.every(interval).minutes.do(run_check, cfg=cfg)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        print("Running self-tests...")
        # Quick self-tests
        try:
            load_config("nonexistent.yaml")
            assert False, "Should have raised FileNotFoundError"
        except FileNotFoundError:
            print("✓ load_config raises FileNotFoundError for missing file")

        result = send_telegram("invalid_token", "123", "test")
        assert result is False
        print("✓ send_telegram returns False on invalid token")

        print("All tests passed.")
        sys.exit(0)
    main()
```

### requirements.txt
```
requests>=2.31.0
pandas>=2.0.0
pyyaml>=6.0
schedule>=1.2.0
```

---

## Step 5: Write the README.md (45 min — most important file)

(README guidance omitted here for brevity — included in final repo)

---

## Step 6: Push to GitHub (20 min)

(Instructions for initializing git and pushing are provided; do not push without user credentials.)

---

(Full document continues with community posting guidance, demo screenshot advice, and promotion steps.)
