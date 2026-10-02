# 🚀 Pico Vault: Autonomous Personal Knowledge & Action OS

Welcome to your **Autonomous Personal Knowledge Management (PKM) and Productivity Operating System**.

Pico Vault is built to be a living digital workshop tailored for machine learning engineering, robotics, DIY builds, side ventures, and athletic life operations. It bridges the gap between passive note-taking and active execution through **automated intake**, **native Obsidian Bases**, **deep repo/literature analyzers**, and a **proactive AI engine**.

---

## 🧭 System Architecture & Vault Topology

The vault is organized according to an action-oriented **Hybrid PARA + Maps of Content (MOC)** architecture:

```
pico-vault/
├── 00_Inbox/                      # Fast capture zone for raw thoughts, links & mobile intake
│   ├── Quick Capture.md           # Instant dropzone for tasks, ideas, research, and inspo
│   └── Mobile Share Guide.md      # iOS Shortcuts & Android webhook setup guide
│
├── 01_Dashboard/                  # Cockpit views and daily intelligence
│   ├── Home.md                    # Primary Command Center
│   └── Daily Briefing.md          # Automated 6:00 AM morning briefing & Serendipity Engine
│
├── 10_Projects/                   # Active initiatives with defined endpoints & milestone tasks
│   ├── Autonomous Vault OS/       # The operating system itself
│   ├── Career & Job Search/       # Applications, interview prep, technical briefs (Akiva, TRL11)
│   ├── Dinner Service Optimizer/  # Restaurant kitchen & table optimization engine
│   ├── DIY ESP32 (mixikid)/       # Hardware build: automated plant telemetry station
│   ├── Body.me App/               # Streamlit health & fitness tracker
│   └── San Diego Relocation/      # Moving logistics, neighborhoods, and lease timelines
│
├── 20_Areas/                      # Ongoing life domains & operations
│   ├── Finance & Leases/          # Taxes, paystubs, Hermes leases, financial planning
│   ├── Health & Fitness/          # 2025 Workouts, functional athletic programming
│   ├── Industry FC/               # Soccer team roster, kits, tactical drills
│   ├── Safe & Records/            # Insurance policies, door codes, secrets, NGROK, TSA
│   └── Personal/                  # Goals, travel itineraries, calendar
│
├── 30_Ideas/                      # The Innovation Incubator
│   ├── Ideas.base                 # Native Obsidian Base (Cards Gallery & Stage Pipeline)
│   ├── Ideas Hub.md               # Map of Content linking all active concepts
│   ├── AI & Tech/                 # Trend Scraper, Local SLM Orchestration, Paper Summarizer
│   ├── Business & Commerce/       # Custom Hotsauce, Fermentation Brand, SoCalCoastal
│   └── Creative & Sports/         # Dynasty Basketball Predictor, Mixes, Red Rising Map
│
├── 40_Tasks/                      # Central Action Repository
│   ├── Tasks.base                 # Native Obsidian Base (Active, Overdue, Priority, Done)
│   └── Tasks Hub.md               # Central action center and sprint tracker
│
├── 50_Knowledge/                  # Deep Technical Reference Library
│   ├── Knowledge Hub.md           # Map of Content indexing all engineering domains
│   ├── Reinforcement Learning/    # UC Berkeley CS 285 course notes, MTDRL, Gymnasium
│   ├── AI & Machine Learning/     # Agents, Neural ODEs, Swin-Transformer, RAG, DPO vs PPO
│   ├── Edge & Cloud Systems/      # Docker, Kubernetes, Helm, Model Serving
│   └── How-To Guides/             # LLC formation, brand creation, prompt playbooks
│
├── 60_Inspiration/                # Curated Media, Repos & DIY Builds (157+ items)
│   ├── Inspiration.base           # Native Obsidian Base (Cards Gallery & Domain Views)
│   ├── Inspiration Hub.md         # Master Map of Content
│   ├── AI & Autonomous Agents/    # Feynman research agent, Claude Code skills, OpenWorker
│   ├── Dev Tools & Repos/         # Scrapling, Ditto site cloner, PageIndex reasoning RAG
│   ├── Robotics & Hardware/       # Microduck RL biped robot, reBot-DevArm 6-axis arm
│   ├── Woodworking & Workshop/    # 90-degree corner clamps, 2x6 Adirondack chair
│   ├── Gardening & Homestead/     # 4-bed companion planting, dragonfly mosquito defense
│   ├── Athletics & Training/      # Soccer isometrics, Japanese ball mastery, running form
│   └── Culture & Lifestyle/       # Japan food/watch guides, San Diego music festivals
│
├── 90_Archive/                    # Historical records and completed files
├── Assets/                        # Centralized attachments (PDF leases, diagrams, screenshots)
├── Templates/                     # Reusable templates (Note, Idea, Task, Project, Research)
└── scripts/                       # Autonomous Python & PowerShell engines
```

---

## 📊 The Native Obsidian Bases

This vault uses **Obsidian Bases** (`.base` files) to provide database views with zero external plugin dependencies:

### 1. `Tasks.base` (`40_Tasks/Tasks.base`)
- **Active Tasks**: Filtered to `status != "done"`, grouped by priority (`🔴 High`, `🟡 Medium`, `🟢 Low`), sorted by due date.
- **Overdue / Urgent**: Flags tasks where `is_overdue == true` or `priority == "🔴 High"`.
- **Completed**: Historical record of finished tasks.
- **Formulas**:
  - `days_until_due`: `if(due_date, (date(due_date) - today()).days, "")`
  - `is_overdue`: `if(due_date, date(due_date) < today() && status != "done", false)`

### 2. `Ideas.base` (`30_Ideas/Ideas.base`)
- **Idea Gallery**: Visual cards view displaying stage badge, domain, effort, and value.
- **By Stage Pipeline**: Grouped by development stage (`💡 Spark` $\rightarrow$ `🌱 Developing` $\rightarrow$ `🚀 Ready to Build` $\rightarrow$ `⏸️ Backlog`).
- **AI & Tech**: Filtered view for software and machine learning concepts.

### 3. `Inspiration.base` (`60_Inspiration/Inspiration.base`)
- **Inspiration Gallery**: Visual gallery of saved media, GitHub repos, and viral builds.
- **By Category**: Grouped table across all 7 inspiration streams with source authors, likes, and links.
- **Domain Tabs**: Specific views for `AI & Dev Tools`, `Robotics & Hardware`, `Athletics & Training`, and `Gardening & Homestead`.

---

## ⚡ The Automation Suite (`scripts/`)

All scripts are written in local Python and PowerShell with zero cloud dependencies:

| Script | Purpose | Command |
| :--- | :--- | :--- |
| **`setup_daemon.ps1`** | Master daemon & automation manager: start/stop background watcher, status monitor, Task Scheduler install. | `.\scripts\setup_daemon.ps1 status` |
| **`run_silent_watcher.vbs`**| Windowless VBS launcher for `vault_watcher.py` (zero console popup). | `wscript scripts/run_silent_watcher.vbs` |
| **`run_silent_brief.vbs`**  | Windowless VBS launcher for `daily_brief.py` for automated morning briefing runs. | `wscript scripts/run_silent_brief.vbs` |
| **`vault_watcher.py`** | Background daemon that monitors `Quick Capture.md` and triages entries the moment you save. | `python scripts/vault_watcher.py` |
| **`vault_ingest.py`** | Core classification engine: parses tasks, ideas, research, and inspo; injects wikilinks. | `python scripts/vault_ingest.py` |
| **`enrich_repos.py`** | Deep repo/paper analyzer: queries GitHub & arXiv APIs to generate technical briefs. | `python scripts/enrich_repos.py --url <URL>` |
| **`compile_project.py`** | Idea-to-project compiler: generates architecture blueprints, DIY BOMs, and spawns tasks. | `python scripts/compile_project.py --idea <Name>` |
| **`daily_brief.py`** | Daily briefing & Serendipity Engine: compiles morning priorities, idea spotlights, and ML pairings. | `python scripts/daily_brief.py` |
| **`mobile_intake.py`** | Lightweight HTTP webhook server for receiving "Share to Vault" from iOS and Android. | `python scripts/mobile_intake.py` |
| **`vault_cli.ps1`** | PowerShell aliases and functions for terminal power users. | `. .\scripts\vault_cli.ps1` |

---

## 💻 Terminal Power Tools (`vault_cli.ps1`)

In any PowerShell terminal, run `. .\scripts\vault_cli.ps1` to load shortcuts:

```powershell
# 1. Quick inspiration or link capture
inspo "https://github.com/microsoft/autogen Multi-agent conversation framework"

# 2. Quick task logging (supports due date and priority flags)
task "Review Akiva system design questions due:2026-09-18 !high"

# 3. Quick idea capture
idea "Local SLM personal task agent"

# 4. Deep research scaffolding
research "Direct Preference Optimization vs PPO in RLHF"

# 5. Daily Briefing & Watcher Daemon
brief-vault     # Compiles today's morning briefing
watch-vault     # Launches the background watcher daemon
```

---

## 📱 Mobile "Share-to-Vault" Workflow

You can share links, Instagram reels, and tweets directly from your phone into your vault:

1. **Start the Webhook Server**:
   ```powershell
   python scripts/mobile_intake.py
   ```
2. **iOS Shortcut / Android Setup**:
   - See detailed instructions in [`00_Inbox/Mobile Share Guide.md`](file:///c:/Users/picof/Documents/pico-vault/00_Inbox/Mobile%20Share%20Guide.md).
   - Tap **Share** on any web page or app $\rightarrow$ select **"Send to Pico Vault"**.
   - The link is posted to the webhook, appended to `Quick Capture.md`, and automatically categorized into `60_Inspiration/` with implementation suggestions.

---

## 🛠️ How to Compile Ideas & DIY Builds

To turn any idea from `30_Ideas/` or `60_Inspiration/` into an active project:

```powershell
python scripts/compile_project.py --idea "Name of Note"
```

- **For Software / AI Projects**:
  - Generates Mermaid architecture diagrams, data models, and 4 sequential milestones.
  - Spawns 6 atomic tasks in `40_Tasks/` registered in `Tasks.base`.
  - Registers the project in `Home.md`.
- **For Physical DIY / Maker Builds**:
  - Generates a **Bill of Materials (BOM) Table** with part specs, estimated costs, and acquisition checkboxes.
  - Renders a **Mermaid pinout/wiring schematic** (e.g. ESP32 to sensors).
  - Generates tool lists, cut lists, and physical assembly tasks.

---

## 🤖 Autonomous Background Automation & Windows Startup

You never need to manually trigger ingestion. The vault includes an autonomous daemon manager:

```powershell
# Check background automation health and pending items
.\scripts\setup_daemon.ps1 status

# Start the watcher silently in the background (zero popup window)
.\scripts\setup_daemon.ps1 start

# Stop the watcher daemon
.\scripts\setup_daemon.ps1 stop

# Configure auto-start at Windows logon & 6:00 AM Task Scheduler briefing
.\scripts\setup_daemon.ps1 install
```

- **Silent Operation**: Uses `scripts/run_silent_watcher.vbs` to execute `pythonw` completely detached with zero distracting cmd prompt windows.
- **Logon Persistence**: Copies an automated startup hook into Windows `shell:startup`.
- **Scheduled Briefing**: Runs `scripts/daily_brief.py` every day at 6:00 AM so your morning dashboard is fresh when you open your laptop.

---

## 🏗️ Priority Project Blueprints & Sprint Scaffolds

The vault contains fully compiled, ready-to-execute projects with Mermaid system architectures and atomic sprint tasks:

| Project | Domain | Architecture / Deliverables | Location |
| :--- | :--- | :--- | :--- |
| **Trend Scraper** | AI & Social | Reddit/TikTok/X scraper, NLP clustering, velocity score engine | [`10_Projects/Trend Scraper/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/Trend%20Scraper/Trend%20Scraper.md) |
| **Dynasty Basketball Predictor** | ML & Sports | NBA API scraper, Bi-LSTM career aging curve, Trade Value Engine | [`10_Projects/Dynasty Basketball Predictor/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/Dynasty%20Basketball%20Predictor/Dynasty%20Basketball%20Predictor.md) |
| **Job Recruiter Agent** | Multi-Agent | Resume parser, auto-tailor prompt engine, headless cover letter PDF builder | [`10_Projects/Job Recruiter Agent/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/Job%20Recruiter%20Agent/Job%20Recruiter%20Agent.md) |
| **Custom Hotsauce Business** | Physical & Commerce | HACCP pH log, batch formulation matrix, Shopify inventory & nutrition labels | [`10_Projects/Custom Hotsauce Business/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/Custom%20Hotsauce%20Business/Custom%20Hotsauce%20Business.md) |
| **DIY ESP32 Plant Monitor** | Embedded / IoT | **C++ Arduino Firmware** (`esp32_plant_monitor.ino`) + SSD1306 OLED + ADC calibration + [`WIRING_GUIDE.md`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/DIY%20ESP32%20(mixikid)/WIRING_GUIDE.md) | [`10_Projects/DIY ESP32 (mixikid)/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/DIY%20ESP32%20(mixikid)/) |
| **Dinner Service Optimizer** | Backend & Algorithmic | **FastAPI Simulation Engine** (`models.py`, `optimizer.py`, `app.py`) with kitchen load balancing & VIP seat dispatch | [`10_Projects/Dinner Service Optimizer/src/`](file:///c:/Users/picof/Documents/pico-vault/10_Projects/Dinner%20Service%20Optimizer/src/) |

---

## 🌅 The Daily Workflow

### 1. Morning: Cockpit Review (2 mins)
- Open Obsidian to [`01_Dashboard/Daily Briefing.md`](file:///c:/Users/picof/Documents/pico-vault/01_Dashboard/Daily%20Briefing.md) or [`Home.md`](file:///c:/Users/picof/Documents/pico-vault/Home.md).
- Review your **Top 4 Priority Tasks** for the day.
- Check the **Idea Spotlight** and **Serendipity Pairing** to spark creative connections.

### 2. Daytime: Zero-Friction Capture
- Drop thoughts, tasks, and media into [`00_Inbox/Quick Capture.md`](file:///c:/Users/picof/Documents/pico-vault/00_Inbox/Quick%20Capture.md) or use terminal shortcuts (`inspo`, `task`, `idea`).
- The background daemon (`vault_watcher.py`) auto-triages everything silently.

### 3. Evening: Build & Execution
- Mark completed tasks directly in [`Tasks.base`](file:///c:/Users/picof/Documents/pico-vault/40_Tasks/Tasks.base) or on `Home.md` by clicking the status cell and setting it to `done`.
- Watch completed tasks automatically archive out of active views.
