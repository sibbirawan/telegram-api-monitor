import os
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import yaml

from monitor import Monitor, fetch_api_value, load_config, send_telegram


class TestFetchApiValue(unittest.TestCase):
    def _make_cfg(self, field: str, response_json: dict) -> dict:
        return {
            "API": {
                "url": "http://fake",
                "method": "GET",
                "headers": {},
                "auth": {"type": "none"},
                "response_field": field,
            }
        }

    @patch("monitor.requests.get")
    def test_simple_field(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"value": 42}
        mock_get.return_value = mock_resp

        cfg = self._make_cfg("value", {"value": 42})
        result = fetch_api_value(cfg)

        self.assertEqual(result, 42.0)

    @patch("monitor.requests.get")
    def test_nested_field_path(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"data": {"count": 7}}
        mock_get.return_value = mock_resp

        cfg = self._make_cfg("data.count", {"data": {"count": 7}})
        result = fetch_api_value(cfg)

        self.assertEqual(result, 7.0)

    @patch("monitor.requests.get")
    def test_missing_field_returns_none(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_resp.json.return_value = {"other": 1}
        mock_get.return_value = mock_resp

        cfg = self._make_cfg("value", {"other": 1})
        result = fetch_api_value(cfg)

        self.assertIsNone(result)

    def test_missing_url_returns_none(self):
        cfg = {
            "API": {
                "url": "",
                "method": "GET",
                "headers": {},
                "auth": {"type": "none"},
                "response_field": "value",
            }
        }

        result = fetch_api_value(cfg)
        self.assertIsNone(result)


class TestMonitorCooldown(unittest.TestCase):
    def _make_monitor(self) -> Monitor:
        cfg = {
            "API": {"url": "http://fake", "method": "GET", "headers": {}, "auth": {"type": "none"}, "response_field": "id"},
            "MONITOR": {"alert_threshold": 0, "alert_on_change": False, "alert_cooldown_minutes": 30},
            "TELEGRAM": {"bot_token": "tok", "chat_id": "123"},
            "USER": {"initials": "AS"},
        }
        return Monitor(cfg)

    def test_first_alert_always_passes(self):
        monitor = self._make_monitor()
        self.assertTrue(monitor._cooldown_passed(datetime.now(), 30))

    def test_cooldown_blocks_rapid_repeat(self):
        monitor = self._make_monitor()
        monitor.last_alert_time = datetime.now()
        self.assertFalse(monitor._cooldown_passed(datetime.now(), 30))

    def test_cooldown_allows_after_interval(self):
        monitor = self._make_monitor()
        monitor.last_alert_time = datetime.now() - timedelta(minutes=31)
        self.assertTrue(monitor._cooldown_passed(datetime.now(), 30))


class TestLoadConfig(unittest.TestCase):
    def test_raises_for_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_config("nonexistent_xyz.yaml")

    def test_loads_valid_yaml(self):
        data = {"TELEGRAM": {"bot_token": "tok", "chat_id": "123"}}
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            yaml.dump(data, f)
            path = f.name

        try:
            cfg = load_config(path)
            self.assertEqual(cfg["TELEGRAM"]["bot_token"], "tok")
        finally:
            os.unlink(path)


class TestSendTelegram(unittest.TestCase):
    def test_returns_false_when_token_missing(self):
        self.assertFalse(send_telegram("", "123", "message"))

    @patch("monitor.requests.post")
    def test_returns_true_on_success(self, mock_post):
        mock_resp = MagicMock()
        mock_resp.raise_for_status = MagicMock()
        mock_post.return_value = mock_resp

        result = send_telegram("valid_token", "123", "hello")
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
