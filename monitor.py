"""
telegram-api-monitor
Polls any REST API on a schedule and sends Telegram alerts when a threshold is crossed.
Author: Sibbir Awan (github.com/sibbirawan)
"""

from __future__ import annotations
import os
import time
import logging
from typing import Optional

import requests
import yaml
import schedule
from datetime import datetime

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)
log = logging.getLogger(__name__)


def load_config(path: str = "config.yaml") -> dict:
    """Load YAML config. Raises FileNotFoundError if missing."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id:
        log.error("Telegram token or chat_id is missing in config.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        log.info("Telegram message sent successfully.")
        return True
    except requests.exceptions.RequestException as e:
        log.error(f"Telegram send failed: {e}")
        return False


def fetch_api_value(cfg: dict) -> Optional[float]:
    api = cfg.get("API", {})
    url = api.get("url")
    method = api.get("method", "GET").upper()
    headers = api.get("headers", {}) or {}
    field = api.get("response_field", "value")

    auth = None
    auth_cfg = api.get("auth", {}) or {}
    if auth_cfg.get("type") == "basic":
        auth = (auth_cfg.get("username", ""), auth_cfg.get("password", ""))

    if not url:
        log.error("API URL is missing in config.")
        return None

    try:
        if method == "GET":
            resp = requests.get(url, headers=headers, auth=auth, timeout=15)
        elif method == "POST":
            payload = api.get("payload", {})
            resp = requests.post(url, headers=headers, auth=auth, json=payload, timeout=15)
        else:
            log.error(f"Unsupported HTTP method: {method}")
            return None

        resp.raise_for_status()
        data = resp.json()

        for key in field.split('.'):
            if isinstance(data, dict):
                data = data.get(key)
            else:
                log.error(f"Cannot navigate response field path '{field}'")
                return None

        if data is None:
            return None
        return float(data)

    except (ValueError, TypeError) as e:
        log.error(f"Could not convert API response to float: {e}")
    except requests.exceptions.RequestException as e:
        log.error(f"API request failed: {e}")
    return None


last_value: Optional[float] = None


def run_check(cfg: dict) -> None:
    global last_value
    monitor = cfg.get("MONITOR", {}) or {}
    threshold = monitor.get("alert_threshold")
    alert_on_change = monitor.get("alert_on_change", False)

    tg = cfg.get("TELEGRAM", {}) or {}
    token = tg.get("bot_token")
    chat_id = tg.get("chat_id")

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    log.info(f"Running check at {now}...")

    value = fetch_api_value(cfg)
    if value is None:
        log.warning("Skipping this cycle — API fetch returned no value.")
        return

    log.info(f"Current value: {value} | Threshold: {threshold} | Last: {last_value}")

    should_alert = False
    reasons = []

    if threshold is not None and value > threshold:
        should_alert = True
        reasons.append(f"Value <b>{value}</b> exceeded threshold <b>{threshold}</b>")

    if alert_on_change and last_value is not None and value != last_value:
        should_alert = True
        reasons.append(f"Value changed from <b>{last_value}</b> → <b>{value}</b>")

    if should_alert:
        # Pull the user initials from the config, default to "User" if not found
        user_initials = cfg.get("USER", {}).get("initials", "User")
        
        reason_text = "\n".join(reasons)
        message = (
            f"🚀 <b>LIVE DATA EVENT DETECTED</b> 🚀\n\n"
            f"👤 <b>Operator:</b> <code>{user_initials}</code>\n"
            f"📈 <b>Current Value:</b> <code>{value}</code>\n"
            f"⛔ <b>Alert Threshold:</b> <code>{threshold}</code>\n"
            f"🔔 <b>Trigger Reason:</b> {reason_text}\n\n"
            f"📅 <b>System Timestamp:</b> <i>{now}</i>\n"
            f"🤖 <i>Automated by your Python Monitor Tool</i>"
        )
        send_telegram(token, chat_id, message)

    last_value = value


def main() -> None:
    try:
        cfg = load_config("config.yaml")
    except FileNotFoundError:
        log.error("Missing config.yaml. Copy config.example.yaml to config.yaml and fill values.")
        return

    interval = cfg.get("MONITOR", {}).get("check_interval_minutes", 30)
    log.info(f"Monitor started. Checking every {interval} minutes.")

    run_check(cfg)
    schedule.every(interval).minutes.do(run_check, cfg=cfg)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print('Running self-tests...')
        try:
            load_config('nonexistent.yaml')
            assert False, 'Should have raised FileNotFoundError'
        except FileNotFoundError:
            print('[PASS] load_config raises FileNotFoundError for missing file')

        result = send_telegram('invalid_token', '123', 'test')
        assert result is False
        print('[PASS] send_telegram returns False on invalid token')

        print('All tests passed.')
        sys.exit(0)
    main()
