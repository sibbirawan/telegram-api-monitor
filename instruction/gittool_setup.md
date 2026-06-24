# Deep Dive: Making Your 5 Projects Publicly Safe on GitHub

This guide goes beyond just building a "generic tool". Since you explicitly asked for a breakdown of **"which Python script needed from each project folder to make GitHub public tool"** and **"how to avoid user sensitive data,"** I will provide a detailed, project-by-project sanitization blueprint.

**The Golden Rule of Open-Sourcing:** 
You must **never** commit real credentials, IP addresses, or live data to a public GitHub repository. If you do, bots will scrape your repo within hours and hack your accounts. 

## 🛡️ Step 0: The Mandatory `.gitignore` File
Before you do anything, you MUST create a `.gitignore` file in the root of every project folder you intend to push to GitHub. This prevents you from accidentally uploading sensitive files.
Create a file named `.gitignore` in your project root and paste this:

```text
# Secrets and Credentials
.env
*.pem
*.ppk
*.key
config*.yaml   # Avoids accidentally uploading your real YAML configs
config*.json
credentials.json

# Data files with real content
*.xlsx
*.xls
*.csv
*.txt        # Be careful with .txt; you might want to allow example.txt but not site.txt

# Python cache
__pycache__/
*.pyc
.venv/
venv/
env/

# IDE clutter
.vscode/
.idea/
```

**The Safe Structure:**
Instead of uploading `config.yaml`, upload `config.example.yaml`. Instead of `data.xlsx`, upload `data_sample.xlsx`. Your README should say: *"Copy `config.example.yaml` to `config.yaml` and fill in your credentials."*

---

## 📂 Project-by-Project: Which Scripts & How to Sanitize Them

Here is the exact breakdown of which Python files to showcase for each of your 5 projects, and exactly what to strip out to make them public-safe.

### 1. TelegramBotApi (The Alarm Bot)
**Which scripts to keep for the tool:**
*   `main_cached.py` (Your entry point)
*   `process_notif.py` (The core API handler)
*   `single_click_msg.py` (The formatter)
*   `_runlib.py` & `rcwise.py` (The reporting engine)
*   `auto_bot.py` (The scheduler template)

**What MUST be removed / replaced:**
*   **API Credentials:** Search for your AUTIN FM REST API URL, your API username, and password. Replace the URL with `https://api.company-example.com/alarms`.
*   **Telegram Secrets:** Search for `bot_token` and `chat_id`. Replace them with `"YOUR_TELEGRAM_BOT_TOKEN"` and `"YOUR_CHAT_ID"`.
*   **Live Excel Files:** Do not upload the actual `.xlsx` reference files containing real site names and regions. Instead, create a dummy `reference_example.xlsx` with 3 rows of placeholder data (e.g., `Site_ID: DUMMY001, Region: DHAKA`).

**How to make it run as a public demo:**
Modify `process_notif.py` to check if `config.yaml` exists. If it doesn't, it prints: *"Please configure your API credentials in config.yaml. See config.example.yaml for format."*

---

### 2. FTT.reset (Ticket & Reset Automation)
**Which scripts to keep for the tool:**
*   `fetching.py`
*   `query_resource_activation.py`
*   `update_batch_transfer.py`
*   The logic from `NGS fix/` and `HW reset/` folders (Paramiko SSH code)

**What MUST be removed / replaced:**
*   **Real Ticket Excel Files:** Do **not** upload `Incident Ticket_*.xlsx` or `batch_transfer_trouble_ticket_import.xlsx` to GitHub.
*   **SSH / Remote Credentials:** Inside `NGS fix/` and `HW reset/`, there will be SSH connection logic. Replace the actual IP addresses (e.g., `10.16.63.29`) with `192.168.1.1` or `YOUR_NETWORK_IP`.
*   **Rilink Values:** The `chosen_rilink` logic is internal. Create a dummy variable or comment out the real filter logic, replacing it with `# Redacted internal logic`.

**How to make it a public tool:**
In your GitHub README, state: *"This script processes Incident Tickets provided in a specific CSV/Excel format. I have included a `sample_incident_template.xlsx` so you can see the required structure. The script outputs a standardized Excel file."* (Create that sample template).

---

### 3. pg bot (Power Generator Verification Bot)
**Which scripts to keep for the tool:**
*   `setup.py` (This is incredibly useful to showcase because clients love "one-click installers").
*   `pg_bot.py`
*   `run_pg_bot.bat`
*   `observability.py`

**What MUST be removed / replaced:**
*   **The Configuration File:** The file `docs/confreno.yml` (or whatever your YAML file is named) holds Telegram tokens and internal API endpoints. You MUST strip this and replace it with a `docs/confreno.example.yml`.
*   **Hardcoded Paths:** Your `setup.py` patches paths dynamically. That is actually safe, but ensure that `setup.py` does not contain any hardcoded internal Windows administrative passwords. Strip those.

**How to make it a public tool:**
Write a README that highlights the "Self-installing" feature. Include a screenshot of the `run_pg_bot.bat` file. This is a killer feature for non-technical business owners.

---

### 4. CELL2RRU (ENM Text Parser)
**Which scripts to keep for the tool:**
*   `cell2rru_builder.py`
*   `reset_cli_builder.py`

**What MUST be removed / replaced:**
*   **Live CLI Exports:** Do **not** upload your actual DHK and CTG region `.txt` export files. Real ENM CLI exports contain the exact physical topology of your employer's network, which is a massive security breach.
*   **The Input data:** Create a `sample_ENM_export.txt` file. Create just 4-5 lines of fake, dummy ENM CLI text that matches the pattern your parser expects. 

**How to make it a public tool:**
This is the **SAFEST** project to open-source because it technically doesn't need credentials—it only parses text files. In your README, state: *"This tool expects a raw text export from ENM. Use the included `sample_ENM_export.txt` to test the parser without exposing your live data."*

---

### 5. CC Raw (AMOS SSH Batch Automation)
**Which scripts to keep for the tool:**
*   `run_amosdhk.py` or `run_amosctg.py`

**What MUST be removed / replaced:**
*   **Server IPs:** Replace `SERVER_IP = "10.16.63.29"` with `SERVER_IP = "YOUR_SERVER_IP"`.
*   **Credentials:** Replace `USERNAME = "sis2732"` and `PASSWORD = "..."` with `USERNAME = "YOUR_USERNAME"` and `PASSWORD = "YOUR_PASSWORD"`.
*   **Site List & Command List:** Do not upload the real `sitelist.txt` and `CC.txt`.
    *   Create `sitelist_example.txt` and put inside: `SITE_DUMMY_01`, `SITE_DUMMY_02`.
    *   Create `CC_example.txt` and put inside: `show version`, `show status`.

**How to make it a public tool:**
Your Paramiko SSH code is highly marketable. State in the README: *"This tool is designed for remote AMOS batch execution. It automatically uploads your local `.txt` files, runs the remote command, downloads the logs, and deletes the remote files. It is currently configured for a placeholder IP. To use it, simply update the constants in `run_amos.py`."*

---

## 🎯 The Ultimate Reality Check: Should you publish ALL 5?

Here is the critical advice: **Cleaning up and managing 5 separate GitHub repositories takes massive time.** 

The previous AI agent's **Action 1** specifically recommended **only building Option A** (a single generic REST API to Telegram monitor) and copying your `process_notif.py` and `requests` logic into it. 

**If I were you, I would do this:**
1.  **Pick Project 4 (CELL2RRU)** or **Project 1 (TelegramBotApi)** to actually build a public repo. Why? Because they are "pure data" scripts with no networking credentials required, making them the easiest to sanitize.
2.  **Do NOT open-source the SSH scripts (Project 5) or the reset scripts (Project 2)** completely. Instead, take **only** the `paramiko` connection class and `sftp` logic, wrap it in a new, clean folder called `ssh_automation_tool`, publish that small snippet. 
3.  **The 80/20 rule:** 80% of clients will hire you based on the fact that you *demonstrate knowledge* of `paramiko` and `pandas`. They don't need your entire `FTT.reset` workflow—they just need to see you know how to handle the libraries. 

---

## 🚀 Actionable Summary Checklist (What to do RIGHT NOW):

1.  **Create a `demo` branch** in your local repos for Projects 1 and 4. Never touch your live `main` branch.
2.  **Run a Credential Scanner:** Install `trufflehog` or `git secrets` on your PC. Run it against your project folders. It will instantly show you where you have hardcoded passwords in your Python files.
3.  **Copy & Paste the `config.example.yaml` pattern:** For every project, find the config file, rename it to `config.example.yaml`, replace all real values with `"PLACEHOLDER"`, and push *only* the `.example` file. 
4.  **Add the `.gitignore`** immediately before you do `git add .`.
5.  **Test your upload:** Before you push to GitHub, run `git add .` and then `git status --ignored`. Look at the list. Make sure your `.xlsx`, `.yaml`, and `.txt` real files are marked as `ignored`.

By following this specific blueprint, you will retain all the impressive code structure of your real projects while safely placing dummy data in the public eye, ensuring you never compromise your day job or expose client secrets.
