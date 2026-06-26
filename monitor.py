"""
telegram-api-monitor
====================
Polls any REST API on a schedule and sends Telegram alerts when a value
crosses a threshold or changes.

Author: Awan Sibbir
License: MIT
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
import time
from datetime import datetime
from typing import Optional

import requests
import schedule
import yaml
from dotenv import load_dotenv

# Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()],
)
log = logging.getLogger(__name__)


def _env_override(cfg: dict, dotted_key: str, env_var: str) -> None:
    """Write env_var value into cfg at the dotted path if the var is set."""
    value = os.environ.get(env_var)
    if value is None:
        return

    keys = dotted_key.split(".")
    node = cfg
    for key in keys[:-1]:
        node = node.setdefault(key, {})
    node[keys[-1]] = value


def load_config(path: str = "config.yaml") -> dict:
    """Load YAML config, then overlay any env vars from .env or the environment."""
    load_dotenv()

    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        cfg = yaml.safe_load(f) or {}

    _env_override(cfg, "TELEGRAM.bot_token", "TELEGRAM_BOT_TOKEN")
    _env_override(cfg, "TELEGRAM.chat_id", "TELEGRAM_CHAT_ID")
    _env_override(cfg, "API.auth.token", "API_BEARER_TOKEN")

    return cfg


def send_telegram(token: str, chat_id: str, message: str) -> bool:
    if not token or not chat_id:
        log.error("Telegram token or chat_id is missing.")
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}

    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        log.info("Telegram message sent successfully.")
        return True
    except requests.exceptions.RequestException as exc:
        log.error(f"Telegram send failed: {exc}")
        return False


def _build_auth(api_cfg: dict) -> tuple[Optional[tuple], dict]:
    """Return requests auth tuple and headers for basic/bearer/none auth."""
    auth_cfg = api_cfg.get("auth", {}) or {}
    auth_type = auth_cfg.get("type", "none").lower()
    headers = dict(api_cfg.get("headers", {}) or {})

    if auth_type == "basic":
        return (auth_cfg.get("username", ""), auth_cfg.get("password", "")), headers

    if auth_type == "bearer":
        token = auth_cfg.get("token", "")
        if not token:
            log.warning("Bearer auth selected but token is empty.")
        headers["Authorization"] = f"Bearer {token}"
        return None, headers

    return None, headers


def fetch_api_value(cfg: dict) -> Optional[float]:
    api = cfg.get("API", {})
    url = api.get("url")
    method = api.get("method", "GET").upper()
    field = api.get("response_field", "value")

    if not url:
        log.error("API URL is missing in config.")
        return None

    auth, headers = _build_auth(api)

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

        for key in field.split("."):
            if isinstance(data, dict):
                data = data.get(key)
            else:
                log.error(f"Cannot navigate response field path '{field}'")
                return None

        if data is None:
            log.warning(f"Field '{field}' resolved to None.")
            return None
        return float(data)

    except (ValueError, TypeError) as exc:
        log.error(f"Could not convert API response to float: {exc}")
    except requests.exceptions.RequestException as exc:
        log.error(f"API request failed: {exc}")
    return None


class Monitor:
    """Encapsulates polling state and alert cooldown behavior."""

    def __init__(self, cfg: dict) -> None:
        self.cfg = cfg
        self.last_value: Optional[float] = None
        self.last_alert_time: Optional[datetime] = None

    def run_check(self) -> None:
        monitor_cfg = self.cfg.get("MONITOR", {}) or {}
        threshold = monitor_cfg.get("alert_threshold")
        alert_on_change = monitor_cfg.get("alert_on_change", False)
        cooldown_minutes = monitor_cfg.get("alert_cooldown_minutes", 30)

        tg = self.cfg.get("TELEGRAM", {}) or {}
        token = tg.get("bot_token")
        chat_id = tg.get("chat_id")

        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M")

        log.info(f"Running check at {now_str}...")
        value = fetch_api_value(self.cfg)

        if value is None:
            log.warning("Skipping this cycle — API fetch returned no value.")
            return

        log.info(f"Current value: {value} | Threshold: {threshold} | Last: {self.last_value}")

        reasons: list[str] = []
        if threshold is not None and value > threshold:
            reasons.append(f"Value <b>{value}</b> exceeded threshold <b>{threshold}</b>")
        if alert_on_change and self.last_value is not None and value != self.last_value:
            reasons.append(f"Value changed from <b>{self.last_value}</b> → <b>{value}</b>")

        if reasons and self._cooldown_passed(now, cooldown_minutes):
            user_initials = self.cfg.get("USER", {}).get("initials", "User")
            reason_text = "\n".join(reasons)
            message = (
                f"🚀 <b>LIVE DATA EVENT DETECTED</b> 🚀\n\n"
                f"👤 <b>Operator:</b> <code>{user_initials}</code>\n"
                f"📈 <b>Current Value:</b> <code>{value}</code>\n"
                f"⛔ <b>Alert Threshold:</b> <code>{threshold}</code>\n"
                f"🔔 <b>Trigger Reason:</b> {reason_text}\n\n"
                f"📅 <b>System Timestamp:</b> <i>{now_str}</i>\n"
                f"🤖 <i>Automated by your Python Monitor Tool</i>"
            )
            if send_telegram(token, chat_id, message):
                self.last_alert_time = now

        self.last_value = value

    def _cooldown_passed(self, now: datetime, cooldown_minutes: int) -> bool:
        if self.last_alert_time is None:
            return True
        elapsed = (now - self.last_alert_time).total_seconds() / 60
        if elapsed < cooldown_minutes:
            remaining = cooldown_minutes - elapsed
            log.info(f"Cooldown active — {remaining:.1f} min remaining.")
            return False
        return True


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Monitor any REST API and send Telegram alerts."
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to YAML config file (default: config.yaml)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run self-tests and exit",
    )
    return parser.parse_args()


def run_self_tests() -> None:
    print("Running self-tests...")

    try:
        load_config("__nonexistent__.yaml")
        raise AssertionError("Expected FileNotFoundError")
    except FileNotFoundError:
        print("[PASS] load_config raises FileNotFoundError for missing file")

    assert send_telegram("", "123", "test") is False
    print("[PASS] send_telegram returns False on missing token")

    cfg = {
        "API": {"url": "http://fake", "method": "GET", "response_field": "id", "auth": {"type": "none"}},
        "MONITOR": {"alert_threshold": 0, "alert_on_change": False, "alert_cooldown_minutes": 30},
        "TELEGRAM": {"bot_token": "tok", "chat_id": "123"},
        "USER": {"initials": "AS"},
    }
    monitor = Monitor(cfg)
    assert monitor._cooldown_passed(datetime.now(), 30) is True
    monitor.last_alert_time = datetime.now()
    assert monitor._cooldown_passed(datetime.now(), 30) is False
    print("[PASS] alert cooldown logic works")

    print("All tests passed.")


def main() -> None:
    args = parse_args()

    if args.test:
        run_self_tests()
        sys.exit(0)

    try:
        cfg = load_config(args.config)
    except FileNotFoundError as exc:
        log.error(str(exc))
        log.error("Copy config.example.yaml to config.yaml and fill in your values.")
        sys.exit(1)

    interval = cfg.get("MONITOR", {}).get("check_interval_minutes", 30)
    log.info(f"Monitor started. Checking every {interval} minutes. Config: {args.config}")

    monitor = Monitor(cfg)
    monitor.run_check()
    schedule.every(interval).minutes.do(monitor.run_check)

    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
