# telegram-api-monitor

A lightweight Python tool that polls any REST API on a schedule and sends
alerts to Telegram when a value crosses a threshold or changes.

No server needed — runs on any Windows/Linux/Mac machine or a $5/month VPS.

---

## What it does

- Fetches data from any REST API (GET or POST, Basic Auth or Bearer token)
- Checks a specific field in the JSON response
- Sends a Telegram message if the value exceeds your threshold
- Also alerts when the value changes (optional)
- Runs every N minutes automatically — fully hands-free

---

## Real use cases

| Use case | API source | Alert when |
|---|---|---|
| Monitor server CPU via API | Your monitoring API | CPU > 80% |
| Track daily sales count | Your CRM API | Sales drop below target |
| Watch stock or crypto price | Public finance API | Price crosses target |
| Alert on new support tickets | Helpdesk API | Ticket count increases |
| Network alarm count spike | Any network FM API | Alarm count > threshold |

---

## Setup (5 minutes)

Requirements: Python 3.10+

```
git clone https://github.com/sibbirawan/telegram-api-monitor
cd telegram-api-monitor
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

---

## Configure

1. Copy config.example.yaml to config.yaml
2. Fill in your values (Telegram token, chat ID, API URL, threshold)
3. Get a Telegram bot token from @BotFather on Telegram
4. Get your chat ID from @userinfobot on Telegram

---

## Run

```
python monitor.py
```

## Test (no API or Telegram token needed)

```
python monitor.py --test
```

---

## Run automatically on Windows (Task Scheduler)

1. Open Task Scheduler and create a Basic Task
2. Trigger: At startup or daily at a fixed time
3. Action: python C:\Projects\telegram-api-monitor\monitor.py
4. Done — runs automatically without manual intervention

---

## Project structure

```
telegram-api-monitor/
├── monitor.py            # Main script
├── config.example.yaml   # Template config (copy to config.yaml)
├── requirements.txt      # Dependencies
├── tests/                # Self-tests
└── instruction/          # Setup guides
```

---

## Need a custom version?

I build custom Python automation tools — API integrations, Telegram bots,
Excel report pipelines, SSH automation.

GitHub: https://github.com/sibbirawan

---

## License

MIT
---
