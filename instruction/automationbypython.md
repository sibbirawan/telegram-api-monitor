# Python Automation Portfolio — Project Reference Document
**Purpose:** This document is for an AI agent to read and brainstorm strategies to help the owner land 1 paid online freelancing job within 30 days.

**Owner background:** Telecom NOC professional in Bangladesh. Full-time job, low salary. Wants side income via Fiverr/Upwork. No prior freelancing history. All projects below are real, production-grade, and currently running or were run in a professional environment.

---

## Project 1: TelegramBotApi

### What it does
Full end-to-end telecom alarm notification system. Fetches live alarm data from a REST API (AUTIN FM system), processes and classifies 21,000+ alarm records, then delivers formatted summary messages to Telegram groups every 30 minutes automatically.

### Workflow
1. `main.py` / `main_simplified.py` / `main_cached.py` — entry points with different risk levels
2. `process_notif.py` — calls AUTIN REST API, downloads paginated alarm data, converts UTC to BD timezone, enriches with reference Excel files (region, towerco, KPI status, fault category)
3. `single_click_msg.py` — formats messages: region-wise, towerco-wise (ABHT/KTBL/STL), VIP sites, KPI/Non-KPI, power failure, root-cause breakdown
4. `_runlib.py` — sends regional aging reports, POP site updates, GP share site reports
5. `auto_bot.py` — template-driven auto notifications using Excel/CSV config files
6. `rcwise.py` — root-cause-wise breakdown (Active/Non-Active/Non-Identified), uploads CSV files to Telegram
7. Runs on Windows Task Scheduler every 30 minutes

### Tech stack
Python, requests, pandas, telepot, PyYAML, openpyxl, numpy, scikit-learn, geopy, arrow, sqlalchemy

### Advantages
- Production-tested on live telecom data (21,000+ records per run)
- Modular architecture: cached fallback, simplified mode, full mode
- Auto-splits long messages (>3700 chars) into multiple Telegram messages
- Configurable via YAML — no code change needed for credentials or chat IDs
- Handles API pagination, timezone conversion, deduplication, missing data

### Sellable as
- Telegram bot that sends scheduled alerts from any API or database
- REST API data fetch + automated notification system
- Custom Telegram notification bot for any business

---

## Project 2: FTT.reset

### What it does
Trouble ticket and network fault reset automation. Fetches live alarm rows from the AUTIN API, filters resource activation tickets, selects correct Rilink values, and prepares batch import Excel files for operational handoff. Also contains AMOS and ENM reset automation sub-modules.

### Workflow
1. `fetching.py` — reads latest `Incident Ticket_*.xlsx`, extracts site codes, fetches matching alarm rows from live API
2. `query_resource_activation.py` — filters resource activation tickets, picks `chosen_rilink`, writes `filtered_resource_activation.xlsx` and updates `batch_transfer_trouble_ticket_import.xlsx`
3. `update_batch_transfer.py` — appends new batch rows using incident ticket file + raw alarms Excel
4. `NGS fix/` — AMOS login and fix automation scripts for Ericsson network elements
5. `HW reset/` — ENM reset automation modules for Huawei equipment

### Tech stack
Python, pandas, openpyxl, PyYAML, requests, urllib3, paramiko (for SSH in sub-modules)

### Advantages
- Converts messy incident ticket data into clean, ready-to-import Excel output
- Eliminates duplicate ticket rows automatically
- Supports both live API fetch and Excel-based raw input
- End-to-end: from alarm fetch → ticket filter → batch import file → network reset

### Sellable as
- Excel/CSV automation pipeline from API data
- Incident ticket processing automation
- Python script to clean and process Excel data automatically

---

## Project 3: pg bot (Power Generator Verification Bot)

### What it does
Telegram-based Power Generator (PG/DG) verification bot. Automates initial package installation, patches script paths dynamically so the bot runs from any folder, and runs the PG verification workflow on demand via a Windows batch launcher.

### Workflow
1. `setup.py` — installs all dependencies, patches hardcoded paths in `pg_bot.py` and `exfunc/` modules to match the current machine
2. `pg_bot.py` — main bot runner, reads config from `docs/confreno.yml`, executes PG verification logic
3. `run_pg_bot.bat` — one-click Windows launcher
4. `observability.py` — monitoring and diagnostics for bot health

### Tech stack
Python, requests, PyYAML, pandas, numpy, openpyxl, telepot

### Advantages
- Self-configuring: setup.py handles path patching automatically, no manual config edits
- One-click launch via .bat file — non-technical users can run it
- Centralized config in YAML
- Portable: works from any folder on any Windows machine after setup

### Sellable as
- Self-installing Python bot/tool with one-click launcher
- Telegram bot with automated setup script
- Portable Python automation tool for Windows

---

## Project 4: CELL2RRU

### What it does
Builds the ENM (Ericsson Network Manager) cell-to-RRU mapping and reset CLI database required for automated hardware reset workflows. Converts raw ENM CLI export text files into structured Excel outputs for downstream alarm-to-CLI automation.

### Workflow
1. Place ENM CLI export `.txt` files in the directory (DHK and CTG regions separately)
2. `cell2rru_builder.py` — parses raw text, builds cell-to-RRU mapping table
3. `reset_cli_builder.py` — generates ENM CLI restart commands for all RRUs in bulk
4. Output: `CELL2RRU_Output.xlsx` with two sheets: `cell2rru` (mapping) and `reset cli` (commands)
5. Integrates with Windows Task Scheduler / one-click deployment model (described in `PROJECT_WORKFLOW.txt`)

### Tech stack
Python, pandas, openpyxl

### Advantages
- Turns unstructured CLI export text into a reusable, queryable Excel database
- Separates CTG and DHK processing
- Generates ready-to-run ENM CLI bulk restart commands
- Designed to integrate with alarm-to-CLI automation pipelines

### Sellable as
- Text/log file parser that outputs structured Excel
- Data extraction and transformation script (any raw text → Excel)
- Bulk command generation automation

---

## Project 5: CC Raw (AMOS SSH Batch Automation)

### What it does
Automates AMOS (Ericsson CLI tool) batch command execution on remote telecom servers via SSH/SFTP. Uploads site lists and command files, triggers remote `amosbatch`, downloads output logs, and optionally cleans up the remote folder — fully hands-free.

### Workflow
1. Edit constants in `run_amosdhk.py` / `run_amosctg.py`: SERVER_IP, USERNAME, PASSWORD, site file path, command file path, download dir
2. Script SSH-connects to server, uploads local site list + command file via SFTP
3. Executes remote `amosbatch` command
4. Downloads output logs to local folder
5. Optionally cleans remote output directory

### Tech stack
Python, paramiko (SSH/SFTP), pandas, openpyxl

### Advantages
- Full remote automation: no manual login to server required
- Handles upload → execute → download → cleanup in one run
- Separate scripts for DHK and CTG regions, easy to extend to other regions
- Reusable for any SFTP-based remote command execution workflow

### Sellable as
- SSH/SFTP automation script (upload files, run remote commands, download output)
- Remote server automation via Python
- Paramiko-based file transfer and command execution tool

---

## Cross-Project Skills Summary (for profile/proposal writing)

| Skill | Evidence |
|---|---|
| REST API integration (GET/POST, pagination, auth) | TelegramBotApi, FTT.reset |
| Telegram bot development | TelegramBotApi, pg bot |
| pandas data processing (merge, filter, dedupe, enrich) | All 5 projects |
| Excel/CSV automation (read, write, multi-sheet) | All 5 projects |
| SSH/SFTP automation | CC Raw |
| Scheduled automation (Windows Task Scheduler) | TelegramBotApi, CELL2RRU |
| YAML config management | TelegramBotApi, FTT.reset, pg bot |
| Self-installing/portable Python tools | pg bot |
| Raw text/log parsing → structured output | CELL2RRU, CC Raw |
| Modular, production-grade code structure | TelegramBotApi |

---

## Context for AI Agent Brainstorming

**Goal:** 1 paid job within 30 days on Fiverr or Upwork.

**Constraints:**
- Full-time job — max 1–2 hours/day on weekdays, more on weekends
- No prior freelancing reviews
- Based in Bangladesh (Payoneer/bank transfer works)
- Does NOT want video editing or graphic design work
- Prefers Python automation, bot development, data processing

**Key strengths to exploit:**
- All projects are real and production-tested, not tutorial copies
- Has working Telegram bot code ready to adapt for any client
- Can do API → data → Excel/Telegram pipelines end to end
- Understands SSH, remote server automation (rare for Fiverr freshers)
- telecom domain knowledge is a niche differentiator

**Suggested gig angles for brainstorming:**
- "Telegram bot that alerts you from your API/database on a schedule"
- "Python script to fetch API data and deliver as Excel/CSV report"
- "Automate your repetitive Excel report with Python"
- "SSH/SFTP file automation script using Python paramiko"
- "Self-installing Python automation tool for Windows"
