#!/usr/bin/env python3
"""
Idea-to-Project Compiler & System Blueprint Generator for pico-vault
--------------------------------------------------------------------
Autonomously transforms concepts and ideas into production-ready project blueprints:
1. Complete Project Specification & Architecture/Process Blueprint (Mermaid diagrams)
2. Detailed Phased Milestones (Phase 1 through Phase 4)
3. 6 Atomic Sprint Tasks logged directly to 40_Tasks/ & indexed by Tasks.base
4. Dual registration in Home.md and 01_Dashboard/Home.md Active Projects matrices.

Usage:
    python scripts/compile_project.py --priority-all
    python scripts/compile_project.py --idea "Trend Scraper"
    python scripts/compile_project.py --idea "Dynasty Basketball Predictor"
    python scripts/compile_project.py --idea "Job Recruiter Agent"
    python scripts/compile_project.py --idea "Custom Hotsauce Business"
"""

import os
import sys
import re
import datetime
import argparse

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IDEAS_DIR = os.path.join(VAULT_ROOT, "30_Ideas")
INSP_DIR = os.path.join(VAULT_ROOT, "60_Inspiration")
PROJECTS_DIR = os.path.join(VAULT_ROOT, "10_Projects")
TASKS_DIR = os.path.join(VAULT_ROOT, "40_Tasks")
HOME_FILE = os.path.join(VAULT_ROOT, "Home.md")
DASHBOARD_HOME_FILE = os.path.join(VAULT_ROOT, "01_Dashboard", "Home.md")

os.makedirs(PROJECTS_DIR, exist_ok=True)
os.makedirs(TASKS_DIR, exist_ok=True)

def find_source_note(query):
    query_clean = query.lower().strip()
    for search_dir in [IDEAS_DIR, INSP_DIR]:
        for root, dirs, files in os.walk(search_dir):
            for f in files:
                if f.endswith(".md") and query_clean in f.lower():
                    return os.path.join(root, f)
    return None

def spawn_atomic_task(task_title, priority, due_date, project_title, checklist=None, today=None):
    if today is None:
        today = datetime.date.today()
    clean_filename = re.sub(r'[\\/*?:"<>|\[\]]', "", task_title).strip() + ".md"
    task_path = os.path.join(TASKS_DIR, clean_filename)

    checklist_str = ""
    if checklist:
        checklist_str = "\n".join([f"- [ ] {item}" for item in checklist])
    else:
        checklist_str = "- [ ] Initial scoping and environment setup\n- [ ] Implement and test changes\n- [ ] Commit and sign off milestone progress"

    content = f"""---
title: "{task_title}"
type: task
status: todo
priority: "{priority}"
due_date: "{due_date}"
project: "[[{project_title}]]"
created: "{today.strftime('%Y-%m-%d')}"
completed_date: ""
tags:
  - task
  - project-task
---

# {task_title}

> [!todo] Project Sprint Task
> Part of active milestone for [[{project_title}]].

## Action Checklist
{checklist_str}

## Related
- Project: [[{project_title}]]
- Hub: [[Tasks Hub]]
"""
    with open(task_path, "w", encoding="utf-8") as tf:
        tf.write(content)

def update_home_dashboards(project_title, domain):
    for target_path in [HOME_FILE, DASHBOARD_HOME_FILE]:
        if not os.path.exists(target_path):
            continue
        with open(target_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Check if project already in table
        if f"[[{project_title}]]" in content:
            continue

        table_marker = "| :--- | :--- | :--- | :--- |"
        if table_marker in content:
            new_row = f"\n| **[[{project_title}]]** | {domain} | 🚀 Active | [[Tasks Hub]] • Milestone Sprint |"
            content = content.replace(table_marker, table_marker + new_row)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"📌 Added [[{project_title}]] to {os.path.basename(os.path.dirname(target_path)) or 'Root'}/{os.path.basename(target_path)} Active Projects matrix!")

def compile_trend_scraper(target_dir, today):
    title = "Trend Scraper"
    today_str = today.strftime("%Y-%m-%d")
    target_date = (today + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    project_file = os.path.join(target_dir, f"{title}.md")

    content = f"""---
title: "{title}"
type: project
project_type: software-ai
status: active
priority: "🔴 High"
start_date: "{today_str}"
target_date: "{target_date}"
tags:
  - project
  - software
  - ai-ml
  - scraping
  - market-intelligence
  - automation
---

# 📈 Project: {title}

> [!important] Mission Objective
> Develop an autonomous, multi-platform market intelligence harvester that surfaces breakout cultural, tech, and e-commerce trends across Reddit, X (Twitter), TikTok, and Google Trends before they saturate the mainstream, utilizing NLP clustering, velocity scoring, and automated alerting.

---

## 🏛️ System Architecture Blueprint

```mermaid
graph TD
    subgraph Data Harvesters
        R[Reddit Scraper<br/>PRAW & Subreddit Feeds]
        X[X / Twitter Scraper<br/>Playwright & Query Streams]
        TT[TikTok Trend Scraper<br/>Trending Hashtags & Creative Center]
        GT[Google Trends Ingestion<br/>pytrends & Search Feeds]
        HN[Hacker News & Tech Blogs<br/>Official RSS & Firecrawl]
    end

    subgraph Ingestion & Storage Pipeline
        Worker[Celery / Redis Queue Runner]
        Dedupe[Deduplication & Canonical Normalizer]
        RawDB[(DuckDB / PostgreSQL<br/>Raw Post Time-Series)]
    end

    subgraph Intelligence & Scoring Engine
        Embed[Gemini / BGE Embeddings]
        Cluster[HDBSCAN & BERTopic Clustering]
        Velocity[Trend Velocity Engine<br/>dMentions / dt * Engagement]
        Summarizer[Gemini 2.5 Flash<br/>Insight Synthesis & Tagging]
    end

    subgraph Presentation & Distribution
        API[FastAPI Service]
        UI[Streamlit / Next.js Analytics Portal]
        Alerts[Telegram / Discord Webhook Bot]
        VaultSync[Pico-Vault Sync Daemon<br/>Direct to 30_Ideas & 60_Inspiration]
    end

    R --> Worker
    X --> Worker
    TT --> Worker
    GT --> Worker
    HN --> Worker

    Worker --> Dedupe
    Dedupe --> RawDB
    RawDB --> Embed
    Embed --> Cluster
    Cluster --> Velocity
    Velocity --> Summarizer

    Summarizer --> API
    API --> UI
    API --> Alerts
    API --> VaultSync
```

### Technical Stack & Dependencies
- **Scraping Frameworks**: Playwright (Headless Browser), PRAW (Reddit API), `pytrends`, BeautifulSoup4
- **Orchestration & Storage**: DuckDB / SQLite, Redis Queue, APScheduler / Cron
- **AI & NLP Stack**: Gemini API (`@google/genai` / `google-genai`), BERTopic, `sentence-transformers`, HDBSCAN
- **Backend Service**: FastAPI (Python 3.11+)
- **Frontend & UI**: Streamlit / Next.js with Plotly interactive charts
- **Alerting & Export**: Webhooks (Telegram / Discord), Obsidian Markdown Vault Exporter

---

## 📐 Mathematical Formulation: Trend Velocity & Virality Score

To distinguish between sustained organic breakout trends and noisy single-spike anomalies, each identified topic cluster is scored using the composite velocity metric:

$$V_{{cluster}} = \\left( \\frac{{\\Delta \\text{{Mentions}}}}{{\\Delta t}} \\right) \\times \\log(1 + \\text{{Total Engagement}}) \\times \\mathcal{{B}}_{{platforms}} \\times \\mathcal{{S}}_{{sentiment}}$$

- **Temporal Gradient ($\\frac{{\\Delta \\text{{Mentions}}}}{{\\Delta t}}$)**: Rate of mention acceleration over 6h, 24h, and 72h rolling windows.
- **Engagement Multiplier**: Weighted sum of upvotes, reposts, comments, and video views.
- **Cross-Platform Breadth ($\\mathcal{{B}}_{{platforms}}$)**: Amplification factor ($1.0$ for single source, $1.8$ for 2 sources, $2.5$ for 3+ sources).
- **Sentiment Polarity ($\\mathcal{{S}}_{{sentiment}}$)**: Sentiment classification filter separating high-intent interest from negative PR controversy.

---

## 🎯 Phased Milestones & Build Sprints

### Phase 1: Multi-Platform Ingestion & Resilient Scraping Engine (Days 1–10)
- [ ] Implement robust Reddit scraper using PRAW targeting r/all, r/technology, r/startups, and curated subreddit clusters
- [ ] Build Playwright headless scrapers for TikTok Creative Center trends and X/Twitter search query streams
- [ ] Setup Google Trends automated query runner using `pytrends` for keyword category velocity
- [ ] Establish DuckDB schema with content hashing (SHA-256) to eliminate cross-platform duplicate posts
- [ ] Implement proxy rotation, exponential backoff retries, and strict rate-limiting middleware

### Phase 2: Signal Processing, NLP Clustering & Trend Velocity Modeling (Days 11–22)
- [ ] Build text normalization pipeline (cleaning URLs, hashtags, user mentions, and emoji sentiment)
- [ ] Integrate embedding generation pipeline using lightweight dense vector embeddings
- [ ] Implement unsupervised clustering via HDBSCAN/BERTopic to dynamically aggregate posts into unified concept clusters
- [ ] Implement mathematical trend velocity scoring algorithm with rolling 6h/24h/72h acceleration metrics
- [ ] Connect Gemini 2.5 Flash summarizer to generate concise executive synthesis and market opportunity analyses

### Phase 3: Interactive Visualizer & Real-time Alerting System (Days 23–34)
- [ ] Scaffold FastAPI backend exposing cluster velocity time-series, platform breakdown, and post samples
- [ ] Develop responsive Streamlit web dashboard featuring trending topic leaderboards, velocity heatmaps, and keyword search
- [ ] Implement threshold-based alerting daemon firing notifications to Telegram and Discord when velocity surpasses 3σ
- [ ] Build automated vault sync pipeline logging top-ranked breakout trends directly into `30_Ideas/` as new actionable notes
- [ ] Implement CSV and JSON export pipelines for downstream financial or marketing workflows

### Phase 4: Backtesting, Hardening, Dockerization & Production Deployment (Days 35–45)
- [ ] Backtest algorithm against historical viral breakout events to optimize precision and recall
- [ ] Conduct end-to-end integration testing and stress test scraper resilience against UI DOM changes
- [ ] Package entire application into Docker Compose multi-container setup (worker, database, API, dashboard)
- [ ] Set up automated healthcheck pings, logging rotate, and unhandled exception recovery
- [ ] Sign off v1.0 deployment and integrate telemetry into [[Home Dashboard]]

---

## 📋 Active Sprint Tasks (40_Tasks/)

| Task Name | Priority | Due Date | Status |
| :--- | :--- | :--- | :--- |
| [[Scrape multi-platform feeds Reddit X TikTok for Trend Scraper]] | 🔴 High | `{(today + datetime.timedelta(days=5)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build normalization and deduplication pipeline for Trend Scraper]] | 🔴 High | `{(today + datetime.timedelta(days=11)).strftime('%Y-%m-%d')}` | `todo` |
| [[Implement LLM clustering and trend velocity scoring for Trend Scraper]] | 🔴 High | `{(today + datetime.timedelta(days=18)).strftime('%Y-%m-%d')}` | `todo` |
| [[Develop vector index and semantic search for Trend Scraper]] | 🟡 Medium | `{(today + datetime.timedelta(days=26)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build real-time Streamlit trend dashboard for Trend Scraper]] | 🟡 Medium | `{(today + datetime.timedelta(days=34)).strftime('%Y-%m-%d')}` | `todo` |
| [[Deploy automated alerting and daily digest cron for Trend Scraper]] | 🔴 High | `{(today + datetime.timedelta(days=42)).strftime('%Y-%m-%d')}` | `todo` |

---

## 🔗 Related Vault Notes
- Origin Note: [[Trend Scraper]]
- Strategy & Ideas: [[Ideas Hub]] • [[Ideas.base]]
- Automation & Agents: [[Autonomous Vault OS]] • [[AI Agents]] • [[Simple Edge Serving]]
- Action Engine: [[Tasks Hub]] • [[Tasks.base]]
"""
    with open(project_file, "w", encoding="utf-8") as f:
        f.write(content)

    tasks = [
        ("Scrape multi-platform feeds Reddit X TikTok for Trend Scraper", 5, "🔴 High", [
            "Configure Reddit PRAW API client with rate-limiting and subreddit targets",
            "Build headless Playwright crawler for TikTok trending creative center",
            "Integrate pytrends client to pull daily Google Search velocity feeds",
            "Verify network resilience with automated retries and proxy handling"
        ]),
        ("Build normalization and deduplication pipeline for Trend Scraper", 11, "🔴 High", [
            "Implement URL sanitization, hashtag extraction, and text cleaning",
            "Create SHA-256 content hashing to deduplicate identical cross-platform stories",
            "Initialize DuckDB storage schema with indexed timestamps and engagement metrics",
            "Write automated ingestion unit tests verifying schema integrity"
        ]),
        ("Implement LLM clustering and trend velocity scoring for Trend Scraper", 18, "🔴 High", [
            "Generate dense vector embeddings using sentence-transformers or Gemini",
            "Tune HDBSCAN clustering parameters for dynamic cluster boundary formation",
            "Implement velocity mathematical formula calculating acceleration across 6h/24h/72h",
            "Connect Gemini 2.5 Flash prompt harness to synthesize trend takeaways"
        ]),
        ("Develop vector index and semantic search for Trend Scraper", 26, "🟡 Medium", [
            "Construct ChromaDB / DuckDB vector indexing for clustered topic exploration",
            "Enable cosine similarity queries to cross-reference new articles against historical trends",
            "Add metadata tagging for categorized sectors (Tech, E-Commerce, Creator, Finance)",
            "Benchmark query latency and optimize vector cache hit rates"
        ]),
        ("Build real-time Streamlit trend dashboard for Trend Scraper", 34, "🟡 Medium", [
            "Build interactive Streamlit layout with sidebar date pickers and category filters",
            "Render Plotly velocity acceleration charts and cross-platform mention splits",
            "Add detailed cluster drill-down view showing original social posts and quotes",
            "Implement 1-click export to CSV and markdown format"
        ]),
        ("Deploy automated alerting and daily digest cron for Trend Scraper", 42, "🔴 High", [
            "Implement Telegram Bot and Discord webhook notification handlers",
            "Configure trigger logic for trends exceeding 3-sigma velocity surge threshold",
            "Set up APScheduler / cron job to write top 5 breakout trends into Pico-Vault 30_Ideas/",
            "Verify 24-hour non-blocking daemon execution and logging"
        ]),
    ]
    for task_desc, days, priority, checklist in tasks:
        due = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        spawn_atomic_task(task_desc, priority, due, title, checklist, today)

    print(f"✅ Compiled Blueprint: 10_Projects/{title}/{title}.md & 6 Sprint Tasks")
    return project_file

def compile_dynasty_basketball(target_dir, today):
    title = "Dynasty Basketball Predictor"
    today_str = today.strftime("%Y-%m-%d")
    target_date = (today + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    project_file = os.path.join(target_dir, f"{title}.md")

    content = f"""---
title: "{title}"
type: project
project_type: software-ai
status: active
priority: "🔴 High"
start_date: "{today_str}"
target_date: "{target_date}"
tags:
  - project
  - software
  - sports
  - machine-learning
  - transformers
  - dynasty-fantasy
---

# 🏀 Project: {title}

> [!important] Mission Objective
> Engineer a deep sequential / transformer-based predictive modeling system for dynasty fantasy basketball. The platform ingests multi-year historical player box scores, models non-linear aging curves, and forecasts future Fantasy Points Per Game (FPPG) to uncover breakout stars before ascension and identify optimal sell-high windows for declining veterans.

---

## 🏛️ System Architecture Blueprint

```mermaid
graph TD
    subgraph Data Extraction & Ingestion
        NBA[NBA Official Stats API / hoopR]
        BR[Basketball-Reference Scraper]
        DK[DraftKings / Yahoo / Sleeper Scoring Feeds]
        Hist[Historical Box Scores 2010-2026]
    end

    subgraph Feature Engineering & Scoring Engine
        Ingest[Data Normalization & Cleaning Pipeline]
        DB[(DuckDB Historical Store)]
        GoodsBads[Goods vs Bads Scoring Engine]
        AdvMetrics[Advanced Metrics: USG%, TS%, PER, WS/48, Pace]
        Aging[Actuarial Aging & Mileage Curves]
    end

    subgraph Predictive Model Pipeline
        Embed[Player Archetype & Positional Embeddings]
        SeqModel[Temporal Sequential / Transformer Encoder]
        Attention[Multi-Head Self-Attention over Multi-Year Sequences]
        Heads[Prediction Heads: Next-Year FPPG, 3Y Trajectory, Breakout %, Decline Risk]
    end

    subgraph Dynasty Decision & UI Layer
        MarketADP[Consensus Market Value / ADP Tracker]
        Valuation[Dynasty Surplus Valuation Engine<br/>Buy-Low / Sell-High Arbitrage]
        UI[Interactive Streamlit Dashboard & Trade Analyzer]
        Export[Obsidian Vault Sync & Roster Evaluator]
    end

    NBA --> Ingest
    BR --> Ingest
    DK --> Ingest
    Hist --> Ingest

    Ingest --> DB
    DB --> GoodsBads
    DB --> AdvMetrics
    GoodsBads --> Aging
    AdvMetrics --> Aging

    Aging --> Embed
    Embed --> SeqModel
    SeqModel --> Attention
    Attention --> Heads

    Heads --> Valuation
    MarketADP --> Valuation
    Valuation --> UI
    Valuation --> Export
```

### Fantasy Points Per Game (FPPG) Metric Formulation
The platform evaluates player output across foundational positive contributions ("Goods") and efficiency penalties ("Bads"):

$$\\text{{Fantasy Points}} = \\underbrace{{(1.0 \\times \\text{{PTS}}) + (1.2 \\times \\text{{REB}}) + (1.5 \\times \\text{{AST}}) + (3.0 \\times \\text{{STL}}) + (3.0 \\times \\text{{BLK}})}}_{{\\text{{Goods (Positive Production)}}}} - \\underbrace{{(1.0 \\times (\\text{{FGA}} - \\text{{FG}})) - (1.0 \\times (\\text{{FTA}} - \\text{{FT}})) - (1.0 \\times \\text{{TOV}})}}_{{\\text{{Bads (Inefficiency Penalties)}}}}$$

### Modeling Methodology & Technical Stack
- **Languages & Frameworks**: Python 3.11+, PyTorch, PyTorch Lightning, Polars / Pandas
- **Model Architectures**: Temporal Sequence Transformer (self-attention across game-level and season-level trajectories), Temporal Convolutional Networks (TCN), and baseline Gradient Boosted Decision Trees (XGBoost / LightGBM)
- **Data Stores**: DuckDB for sub-second analytical aggregations across 1M+ individual player box scores
- **Frontend & Visualization**: Streamlit, Plotly, Altair for career aging curve overlays and interactive trade valuation charts

---

## 🎯 Phased Milestones & Build Sprints

### Phase 1: Historical Data Ingestion & Statistical Pipeline (Days 1–10)
- [ ] Ingest comprehensive 15-season NBA box score dataset (game-level, per-minute, and season aggregations)
- [ ] Implement the parameterized "Goods vs Bads" fantasy scoring pipeline in Polars/DuckDB
- [ ] Calculate advanced contextual stats: True Shooting % (TS%), Usage Rate (USG%), Assist-to-Turnover Ratio, Rebound %, and Team Pace
- [ ] Clean and normalize injury records, games missed, and minutes-per-game (MPG) distribution
- [ ] Establish automated unit test suite verifying historical point totals against official fantasy platforms

### Phase 2: Feature Engineering & Actuarial Aging Curves (Days 11–22)
- [ ] Calculate baseline empirical aging curves categorized by position (Point Guards, Wings, Stretch Bigs, Rim Protectors)
- [ ] Formulate athletic mileage indicators: cumulative career minutes, back-to-back performance decay, and post-injury trajectory shifts
- [ ] Construct rolling temporal features (last 10 games, last 30 games, year-over-year deltas, career peak differentials)
- [ ] Train baseline benchmark models (Ridge Regression and XGBoost) to establish benchmark RMSE/MAE for next-year FPPG
- [ ] Document baseline performance metrics and feature importance rankings

### Phase 3: Transformer & Sequence Model Architecture (Days 23–34)
- [ ] Implement PyTorch dataset loader generating padded multi-season time-series sequence tensors per player
- [ ] Build Transformer Encoder architecture with positional encodings and multi-head self-attention across career phases
- [ ] Implement multi-task prediction heads: (1) 1-Year Ahead FPPG, (2) 3-Year Career Arc Vector, (3) Breakout Star Probability, (4) Cliff Decline Probability
- [ ] Train model using masked season evaluation and walk-forward backtesting (train on 2010–2021, validate 2022–2024, test 2025–2026)
- [ ] Generate Monte Carlo simulation bands (10th percentile floor, 50th median, 90th percentile ceiling) for each player

### Phase 4: Dynasty Valuation Engine, Trade Analyzer & Interactive UI (Days 35–45)
- [ ] Ingest consensus dynasty ADP (Average Draft Position) and trade market valuations from Sleeper and DynastyProcess
- [ ] Construct the Arbitrage Valuation Engine: compare model predicted 3-year value against current market perception to tag "Strong Buy", "Hold", "Sell High"
- [ ] Build full-featured Streamlit interactive web application with player career trajectory visualizers and head-to-head comparisons
- [ ] Implement automated trade calculator evaluating multi-player dynasty asset exchanges
- [ ] Export rankings and trade target watchlists directly to [[Dynasty Basketball Predictor]] and vault briefing

---

## 📋 Active Sprint Tasks (40_Tasks/)

| Task Name | Priority | Due Date | Status |
| :--- | :--- | :--- | :--- |
| [[Ingest multi-year NBA player game logs and box scores for Dynasty Basketball Predictor]] | 🔴 High | `{(today + datetime.timedelta(days=5)).strftime('%Y-%m-%d')}` | `todo` |
| [[Implement fantasy scoring metric pipeline Goods vs Bads for Dynasty Basketball Predictor]] | 🔴 High | `{(today + datetime.timedelta(days=11)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build player aging curve and career trajectory baseline for Dynasty Basketball Predictor]] | 🔴 High | `{(today + datetime.timedelta(days=18)).strftime('%Y-%m-%d')}` | `todo` |
| [[Train transformer sequence model for multi-year FPPG projections for Dynasty Basketball Predictor]] | 🔴 High | `{(today + datetime.timedelta(days=26)).strftime('%Y-%m-%d')}` | `todo` |
| [[Develop breakout and sell-high anomaly detection engine for Dynasty Basketball Predictor]] | 🟡 Medium | `{(today + datetime.timedelta(days=34)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build interactive dynasty trade and player valuation UI for Dynasty Basketball Predictor]] | 🟡 Medium | `{(today + datetime.timedelta(days=42)).strftime('%Y-%m-%d')}` | `todo` |

---

## 🔗 Related Vault Notes
- Origin Note: [[Dynasty Basketball Predictor]]
- Technical Theory: [[Knowledge Hub]] • [[CS 285 Intro to RL]] • [[Neural Ordinary Differentiable Equations]]
- Ideas & Experiments: [[Ideas Hub]] • [[Ideas.base]]
- Task Tracker: [[Tasks Hub]] • [[Tasks.base]]
"""
    with open(project_file, "w", encoding="utf-8") as f:
        f.write(content)

    tasks = [
        ("Ingest multi-year NBA player game logs and box scores for Dynasty Basketball Predictor", 5, "🔴 High", [
            "Download and clean 15 years of game logs from NBA stats API and Basketball-Reference",
            "Store normalized player career records in DuckDB with unique player IDs",
            "Handle player name aliases, team trades, and rookie draft year metadata",
            "Verify zero missing records across all regular season box scores"
        ]),
        ("Implement fantasy scoring metric pipeline Goods vs Bads for Dynasty Basketball Predictor", 11, "🔴 High", [
            "Code parameterized scoring engine: Goods (PTS, REB, AST, STL, BLK) vs Bads (FGA-FG, FTA-FT, TOV)",
            "Compute per-game and per-36 minute fantasy averages for all historical player seasons",
            "Add situational filters for starting vs bench games and minute restriction samples",
            "Validate computed fantasy scores against Yahoo and Sleeper league totals"
        ]),
        ("Build player aging curve and career trajectory baseline for Dynasty Basketball Predictor", 18, "🔴 High", [
            "Generate empirical aging curves by positional archetype across ages 19 through 38",
            "Calculate career mileage indices based on cumulative regular season and playoff minutes",
            "Train baseline Ridge and XGBoost models to establish performance benchmark",
            "Evaluate baseline MAE on next-season fantasy production forecasting"
        ]),
        ("Train transformer sequence model for multi-year FPPG projections for Dynasty Basketball Predictor", 26, "🔴 High", [
            "Build PyTorch Dataset generating multi-year sequential feature tensors",
            "Implement Transformer Encoder architecture with multi-head self-attention",
            "Train multi-task heads for next-season FPPG, 3-year curve, and breakout probability",
            "Run walk-forward cross-validation and generate 10th/50th/90th percentile confidence bounds"
        ]),
        ("Develop breakout and sell-high anomaly detection engine for Dynasty Basketball Predictor", 34, "🟡 Medium", [
            "Scrape consensus dynasty rankings and ADP from Sleeper and trade calculators",
            "Formulate surplus valuation metric (Model 3-Year Expected Points minus Market ADP)",
            "Classify buy-low targets (high model trajectory, suppressed market price)",
            "Classify sell-high candidates (peak market value, impending model age cliff)"
        ]),
        ("Build interactive dynasty trade and player valuation UI for Dynasty Basketball Predictor", 42, "🟡 Medium", [
            "Scaffold Streamlit web dashboard with player search and comparison views",
            "Plot career projection cones with historical comparables and aging trajectories",
            "Implement 2-team trade evaluation tool calculating total 3-year net fantasy asset delta",
            "Export weekly actionable trade targets to vault note in 30_Ideas/"
        ]),
    ]
    for task_desc, days, priority, checklist in tasks:
        due = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        spawn_atomic_task(task_desc, priority, due, title, checklist, today)

    print(f"✅ Compiled Blueprint: 10_Projects/{title}/{title}.md & 6 Sprint Tasks")
    return project_file

def compile_job_recruiter(target_dir, today):
    title = "Job Recruiter Agent"
    today_str = today.strftime("%Y-%m-%d")
    target_date = (today + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    project_file = os.path.join(target_dir, f"{title}.md")

    content = f"""---
title: "{title}"
type: project
project_type: software-ai
status: active
priority: "🔴 High"
start_date: "{today_str}"
target_date: "{target_date}"
tags:
  - project
  - software
  - agents
  - career
  - llm
  - reinforcement-learning
  - defense-tech
---

# 🎯 Project: {title} (Xavier Platform)

> [!important] Mission Objective
> Build and deploy the "Xavier Career Intelligence Platform" — an autonomous AI executive recruiter and industry intelligence system custom-tailored for Christian Picofazzi (Senior Lead RL/AI/ML Engineer at Lockheed Martin AI Center, Active Secret Clearance). The platform scrapes high-intent direct-from-employee LinkedIn posts and web sources using Gemini 2.5 Flash with Google Search Grounding, computes multi-horizon financial models (3-5Y and 5-10Y), performs gap analysis across 5 target sectors, and maintains an evolutionary career knowledge graph.

---

## 🏛️ System Architecture Blueprint

```mermaid
graph TD
    subgraph Ingestion & Live Grounding Layer
        Gemini[Gemini 2.5 Flash + Google Search Grounding]
        LI[LinkedIn Employee Hiring Posts Scraper<br/>site:linkedin.com/posts direct signals]
        Portals[Greenhouse / Lever / YC / Tech Portals]
        News[Crunchbase / TechCrunch / Funding Signals]
    end

    subgraph Backend Core (Node.js / Express / TypeScript)
        Server[Express API Gateway & Runner]
        ProfileMatch[Christian Profile Matcher<br/>RL, Sim-to-Real, UE5.5, Clearance, San Diego/Remote]
        SectorBalance[Portfolio Balancer & Concentration Diagnostic<br/>5 Strategic Industry Verticals]
        CompEngine[Dynamic Compensation & Financial Horizon Engine<br/>3-5Y Liquid Value & 5-10Y Career Capital]
        GraphEngine[Evolutionary Graph Loop<br/>Semantic Triples & Liked/Disliked Features]
    end

    subgraph Frontend Application (React 18 + Vite + Tailwind)
        UI[Main Dashboard & Tab State Engine]
        Pie[Recharts Sector Allocation Pie Chart]
        TrendLine[Compensation Trend Line Graph 7D/30D/90D]
        NetMap[LinkedIn Professional Connection Mapper]
        D3Graph[D3.js Dynamic Career Skills Ontology Graph]
        CompareModal[Side-by-Side Job Comparer & Gap Analyzer]
    end

    subgraph Automated Services & Vault Integration
        Cron[Morning Opportunity Digest Cron]
        BriefSync[Daily Briefing & Vault Task Sync]
    end

    Gemini --> Server
    LI --> Server
    Portals --> Server
    News --> Server

    Server --> ProfileMatch
    ProfileMatch --> SectorBalance
    SectorBalance --> CompEngine
    CompEngine --> GraphEngine

    GraphEngine --> UI
    UI --> Pie
    UI --> TrendLine
    UI --> NetMap
    UI --> D3Graph
    UI --> CompareModal

    Server --> Cron
    Cron --> BriefSync
```

### Candidate Grounding Profile & Alignment Heuristics
- **Candidate Target**: Christian Picofazzi
- **Current Position**: Senior Lead RL/AI/ML Engineer, Lockheed Martin AI Center
- **Security Clearance**: Active Secret Security Clearance (leverage for high-barrier defense & commercial autonomy roles)
- **Core Specialties**: Deep Reinforcement Learning (PPO, MARL, Hierarchical RL), Sim-to-Real / Sim-to-Sim, Guidance Navigation & Control (GNC), Computer Vision, Unreal Engine 5.5, JSBSim, MLOps, PyTorch, JAX
- **Geographic Constraint**: San Diego, CA (Onsite/Hybrid) OR 100% Fully Remote (US)
- **Five Strategic Sectors**:
  1. *Defense Tech & Autonomous Systems* (e.g., Anduril, Shield AI, Palantir)
  2. *Commercial Autonomy & Robotics* (e.g., AVs, humanoid robotics)
  3. *Healthcare & Biotech AI* (e.g., surgical robotics, protein folding)
  4. *Manufacturing & Industrial Logistics* (e.g., supply chain sim-to-real)
  5. *Commercial Tech & Quantitative Finance* (e.g., algorithmic trading, simulation)

---

## 🎯 Phased Milestones & Build Sprints

### Phase 1: Scraping Harness & Live Grounding Engine (Days 1–10)
- [ ] Scaffold Node.js/Express backend (`server.ts`) integrating `@google/genai` with Gemini 2.5 Flash and Google Search Grounding
- [ ] Build LinkedIn Employee Post crawler targeting direct-from-manager hiring announcements (`site:linkedin.com/posts`)
- [ ] Implement geographic filter (San Diego, CA or US Remote) and clearance requirement identifier
- [ ] Configure structured JSON response schema mapping job title, hiring manager, compensation range, and quote snippet
- [ ] Set up local development environment with `tsx` hot-reloading and `.env` secret management

### Phase 2: Candidate Profiling, Alignment Heuristics & Financial Engine (Days 11–22)
- [ ] Program algorithmic compatibility scoring formula evaluating candidate fit against role requirements
- [ ] Implement automated gap analysis comparing Christian's Lockheed background to target sectors
- [ ] Build Multi-Horizon Financial Model:
  - *Medium-Term Horizon (3–5 Years)*: Base salary, sign-on bonus, and equity vesting schedule
  - *Long-Term Horizon (5–10 Years)*: Industry growth macro velocity, equity upside, and career capital
- [ ] Implement disliked feature flags (e.g. legacy C maintenance, pure DevOps ops) with transparent explanations
- [ ] Write comprehensive unit tests for alignment heuristics and compensation parsing

### Phase 3: Interactive Visualizer, Sector Analytics & D3 Graph (Days 23–34)
- [ ] Build React 18 frontend with Vite, Tailwind CSS, Lucide icons, and Motion transitions
- [ ] Implement Recharts Sector Distribution Pie Chart with concentration warning diagnostics
- [ ] Build interactive Dynamic Compensation Trend Chart with 7-Day, 30-Day, and 90-Day range toggles
- [ ] Integrate LinkedIn Professional Connection Mapper to surface warm referral pathways
- [ ] Construct D3.js interactive Career Skills Ontology and Company Connection Graph

### Phase 4: Feedback Loop, Daily Digest & Production Hardening (Days 35–45)
- [ ] Implement User Grading modal allowing Christian to provide 1–5 star ratings and qualitative notes
- [ ] Build the Graph Learning loop that converts user ratings into semantic triples and recalibrates search weights
- [ ] Configure morning automated cron service feeding top 3 daily opportunities directly into [[Daily Briefing]]
- [ ] Bundle and optimize application using `esbuild` into standalone production server
- [ ] Complete security review ensuring clearance and contact data remain strictly local and private

---

## 📋 Active Sprint Tasks (40_Tasks/)

| Task Name | Priority | Due Date | Status |
| :--- | :--- | :--- | :--- |
| [[Setup Express backend and Gemini live search scraping endpoint for Job Recruiter Agent]] | 🔴 High | `{(today + datetime.timedelta(days=5)).strftime('%Y-%m-%d')}` | `todo` |
| [[Implement Christian candidate profile alignment heuristics for Job Recruiter Agent]] | 🔴 High | `{(today + datetime.timedelta(days=11)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build multi-horizon financial projection and compensation model for Job Recruiter Agent]] | 🔴 High | `{(today + datetime.timedelta(days=18)).strftime('%Y-%m-%d')}` | `todo` |
| [[Develop React dashboard and Recharts sector allocation charts for Job Recruiter Agent]] | 🟡 Medium | `{(today + datetime.timedelta(days=26)).strftime('%Y-%m-%d')}` | `todo` |
| [[Implement D3 career skills knowledge graph and connection mapper for Job Recruiter Agent]] | 🟡 Medium | `{(today + datetime.timedelta(days=34)).strftime('%Y-%m-%d')}` | `todo` |
| [[Deploy automated daily opportunity digest and feedback loop for Job Recruiter Agent]] | 🔴 High | `{(today + datetime.timedelta(days=42)).strftime('%Y-%m-%d')}` | `todo` |

---

## 🔗 Related Vault Notes
- Origin Specification: [[Job Recruiter Agent]]
- Active Job Pipeline: [[Job Search]] • [[Job Interviews]] • [[Akiva Setup]] • [[Autonomy Interview Prep]]
- Agent Technology: [[AI Agents]] • [[Knowledge Hub]]
- Task Tracker: [[Tasks Hub]] • [[Tasks.base]]
"""
    with open(project_file, "w", encoding="utf-8") as f:
        f.write(content)

    tasks = [
        ("Setup Express backend and Gemini live search scraping endpoint for Job Recruiter Agent", 5, "🔴 High", [
            "Initialize Express.js TypeScript server with tsx and esbuild pipeline",
            "Configure @google/genai SDK client using Gemini 2.5 Flash and Google Search tool",
            "Build crawler query targeting LinkedIn employee posts: site:linkedin.com/posts hiring",
            "Implement structured JSON output parser extracting manager name, title, quote, and URL"
        ]),
        ("Implement Christian candidate profile alignment heuristics for Job Recruiter Agent", 11, "🔴 High", [
            "Ground alignment engine with Christian's profile: Lockheed Senior Lead RL/AI/ML, Secret Clearance, MS AI/ML",
            "Code compatibility algorithm weighting Sim-to-Real, Unreal Engine 5.5, GNC, and PyTorch/JAX",
            "Enforce strict location criteria: San Diego CA (onsite/hybrid) or 100% US Remote",
            "Build automatic gap analysis generator contrasting defense background with target industry"
        ]),
        ("Build multi-horizon financial projection and compensation model for Job Recruiter Agent", 18, "🔴 High", [
            "Implement multi-period financial model evaluating 3-5 year and 5-10 year compensation horizons",
            "Model base salary, signing bonus, and 4-year equity vesting cliffs with realistic sector drift",
            "Enforce strict $200k/yr compensation floor filter with explicit alert flags",
            "Write deterministic Monte Carlo engine simulating volatility curves per industry vertical"
        ]),
        ("Develop React dashboard and Recharts sector allocation charts for Job Recruiter Agent", 26, "🟡 Medium", [
            "Scaffold React 18 + Vite dashboard with Midnight Slate theme and Tailwind styling",
            "Render Recharts interactive Sector Distribution Pie Chart with over-concentration warnings",
            "Build Dynamic Compensation Trend Line Graph with 7D, 30D, and 90D range toggle selectors",
            "Create side-by-side job comparison modal with compatibility breakdowns"
        ]),
        ("Implement D3 career skills knowledge graph and connection mapper for Job Recruiter Agent", 34, "🟡 Medium", [
            "Develop D3.js force-directed knowledge graph displaying skills, industries, and company nodes",
            "Build LinkedIn contact referral mapper identifying warm connection pathways to posters",
            "Implement instant dislike tagging for user-penalized traits (legacy maintenance, pure devops)",
            "Enable interactive node click inspection with related job listings"
        ]),
        ("Deploy automated daily opportunity digest and feedback loop for Job Recruiter Agent", 42, "🔴 High", [
            "Build user rating feedback modal converting star ratings and notes into semantic graph triples",
            "Create morning background cron job to execute scheduled market discovery scans",
            "Format top-scoring daily job discoveries and sync directly into Pico-Vault Daily Briefing",
            "Bundle production application with esbuild and verify zero secret leakage"
        ]),
    ]
    for task_desc, days, priority, checklist in tasks:
        due = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        spawn_atomic_task(task_desc, priority, due, title, checklist, today)

    print(f"✅ Compiled Blueprint: 10_Projects/{title}/{title}.md & 6 Sprint Tasks")
    return project_file

def compile_custom_hotsauce(target_dir, today):
    title = "Custom Hotsauce Business"
    today_str = today.strftime("%Y-%m-%d")
    target_date = (today + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    project_file = os.path.join(target_dir, f"{title}.md")

    content = f"""---
title: "{title}"
type: project
project_type: physical-commerce
status: active
priority: "🔴 High"
start_date: "{today_str}"
target_date: "{target_date}"
tags:
  - project
  - business
  - food
  - ecommerce
  - physical-product
  - maker
  - culinary
---

# 🌶️ Project: {title}

> [!important] Mission Objective
> Launch a bespoke direct-to-consumer hot sauce company and interactive digital platform where customers design customized artisan hot sauces online. Features an animated, drag-and-drop digital bottle builder (selecting fermented/fresh pepper bases, fruits, and gourmet aromatics), integrated with compliant small-batch culinary manufacturing, FDA/Cottage Food safety controls (pH < 3.8), automated custom thermal labeling, and direct-to-door fulfillment.

---

## 🏛️ System Architecture & Process Blueprint

```mermaid
graph TD
    subgraph Digital Customer Experience (Web & E-Commerce)
        User[Customer on Web / Mobile]
        Builder[Interactive Bottle Builder App<br/>Drag & Drop Layer Animation]
        BaseSelect[Base Pepper Selection<br/>Fermented Habanero / Ghost / Roasted Jalapeño]
        Addins[Flavor & Spice Add-ins<br/>3 Free Included + Surcharged Premium]
        RuleEngine[Flavor Pairing AI Engine<br/>Complementary Notes & Clash Warnings]
        Cart[Order Cart & Stripe Checkout]
    end

    subgraph Order Management & Recipe Translation
        OrderQueue[Order Management System]
        RecipeEngine[Weight & Measurement Translator<br/>Grams Formulation Manifest]
        LabelGen[Automated Label Generator<br/>Custom Sauce Name, Heat Index, Ingredients]
    end

    subgraph Physical Culinary Operations & Production
        RawSupplies[Supply Storage: Peppers, Vinegar, Fruits, Spices]
        Ferment[Lacto-Fermentation Vessels<br/>Salt Brine & pH Tracking]
        CookBatch[Precision Batch Blending & Cooking<br/>Commercial Immersion Blender]
        SafetyCCP[Critical Control Point CCP<br/>Calibrated Digital pH Test < 3.8]
        HotFill[Hot Fill & Hold at 185°F<br/>5 oz Glass Woozy Bottles]
    end

    subgraph Finishing, Packaging & Fulfillment
        CapSeal[Cap Inserter & Tamper-Evident Heat Shrink Band]
        PrintLabel[Munbyn Thermal Color Label Print<br/>Custom Customer Name & Batch #]
        BoxPack[Protective Corrugated Mailer & Custom Insert]
        Ship[USPS Ground Advantage / Pirate Ship]
        Delivery[Customer Unboxing & Reorder QR Code]
    end

    User --> Builder
    Builder --> BaseSelect
    BaseSelect --> Addins
    Addins --> RuleEngine
    RuleEngine --> Cart
    Cart --> OrderQueue

    OrderQueue --> RecipeEngine
    OrderQueue --> LabelGen
    RecipeEngine --> CookBatch
    RawSupplies --> Ferment
    Ferment --> CookBatch
    CookBatch --> SafetyCCP
    SafetyCCP --> HotFill
    HotFill --> CapSeal

    LabelGen --> PrintLabel
    CapSeal --> PrintLabel
    PrintLabel --> BoxPack
    BoxPack --> Ship
    Ship --> Delivery
    Delivery -.->|Scan QR to Reorder / Tweak| Builder
```

### Flavor Architecture & Unit Economics

| Component Category | Available Options | Pricing Logic | Unit Cost Impact |
| :--- | :--- | :--- | :--- |
| **Pepper Bases (40% vol)** | Fermented Red Habanero, Fire Ghost Pepper, Roasted Jalapeño-Poblano, Aged Scotch Bonnet | Base Included | ~$1.10 / bottle |
| **Acid & Liquid Base (35% vol)** | Organic Apple Cider Vinegar, White Distilled Vinegar, Fresh Lime Juice | Base Included | ~$0.45 / bottle |
| **Standard Add-ins (15% vol)** | Roasted Garlic, Sweet Vidalia Onion, Mango, Cilantro, Smoked Paprika, Carrots | 3 Included Free | ~$0.65 / bottle |
| **Premium Add-ins (10% vol)** | Black Garlic, Bourbon Oak Infusion, White Truffle Oil, Hot Honey, Carolina Reaper Dust | +$1.25 surcharge each | ~$0.55 / add-in |
| **Packaging & Hardware** | 5 oz Glass Woozy Bottle, Dripper, Cap, Tamper Shrink Band, Custom Label | Included in Base | ~$1.20 / unit |
| **Summary Economics** | **Retail Price: $14.00 base ($16.50 avg cart)** | **COGS: ~$3.40 - $4.00** | **Gross Margin: ~74%** |

---

## 🎯 Phased Milestones & Build Sprints

### Phase 1: Culinary Formulation, Fermentation Protocols & Food Safety Compliance (Days 1–10)
- [ ] Standardize and bench-test 3 master pepper mash recipes (Fermented Habanero, Roasted Jalapeño-Poblano, and Ghost Pepper)
- [ ] Establish strict acidified food protocol: digital pH meter calibration, target equilibrium pH < 3.8, and hot-fill-and-hold pasteurization (185°F for 3 min)
- [ ] Complete California Cottage Food Operation (CFO Class A/B) permit documentation or secure local commercial commissary kitchen lease
- [ ] Formulate standard recipe conversion tables (translating digital UI percentage bars into exact culinary grams)
- [ ] Conduct 14-day ambient shelf stability and separation challenge tests

### Phase 2: Interactive Bottle Builder Web Application & Cart (Days 11–22)
- [ ] Build responsive web application featuring an animated bottle filling visualizer (liquid layer animations reacting to user ingredient selections)
- [ ] Implement drag-and-drop ingredient selector with base pepper, 3 free standard add-ins, and paid premium add-ins
- [ ] Construct the Flavor Pairing Recommendation Engine to suggest complementary pairings (e.g., Mango + Habanero + Lime) and alert against unpalatable clashes
- [ ] Integrate dynamic heat-level meter (Mild, Medium, Hot, Extra Hot, Nuclear) updating in real time as ingredients change
- [ ] Connect Stripe checkout, order confirmation emails, and automated receipt generation

### Phase 3: Sourcing, Packaging & Pilot Batch Production (Days 23–34)
- [ ] Source bulk inventory: 5 oz glass woozy bottles, 24mm continuous thread caps, orifice reducers (dripper tops), and tamper-evident shrink bands
- [ ] Setup on-demand custom label printing workflow (Munbyn / Primera label printer) dynamically printing the customer's custom sauce name and nutrition facts
- [ ] Purchase commercial kitchen equipment: high-powered immersion blender, induction cooker, precision digital scales, and Apera pH20 meter
- [ ] Execute an initial 20-bottle alpha pilot run for sensory blind tasting, drop-testing packaging, and timing kitchen turnaround
- [ ] Finalize custom unboxing presentation: branded corrugated mailer boxes, kraft protective sleeves, and printed instruction cards

### Phase 4: Commercial Launch, Fulfillment Automation & Brand Marketing (Days 35–45)
- [ ] Integrate shipping automation API (Pirate Ship / ShipStation) to auto-generate USPS Ground Advantage shipping labels on order placement
- [ ] Launch direct-to-consumer storefront with video walkthroughs and customer review spotlights
- [ ] Package and send PR sample boxes to hot sauce influencers, Reddit r/hotsauce, and local artisan food bloggers
- [ ] Implement reorder QR codes on every bottle label allowing customers to reorder their custom formulation with one click
- [ ] Review launch metrics, customer satisfaction scores, and supply chain reorder triggers

---

## 📋 Active Sprint Tasks (40_Tasks/)

| Task Name | Priority | Due Date | Status |
| :--- | :--- | :--- | :--- |
| [[Standardize base pepper fermentation recipes and pH testing protocol for Custom Hotsauce Business]] | 🔴 High | `{(today + datetime.timedelta(days=5)).strftime('%Y-%m-%d')}` | `todo` |
| [[Research FDA cottage food regulations and commercial kitchen licensing for Custom Hotsauce Business]] | 🔴 High | `{(today + datetime.timedelta(days=11)).strftime('%Y-%m-%d')}` | `todo` |
| [[Source bottles tamper-evident shrink bands and custom label printer for Custom Hotsauce Business]] | 🟡 Medium | `{(today + datetime.timedelta(days=18)).strftime('%Y-%m-%d')}` | `todo` |
| [[Build interactive animated bottle builder UI with drag-and-drop ingredients for Custom Hotsauce Business]] | 🔴 High | `{(today + datetime.timedelta(days=26)).strftime('%Y-%m-%d')}` | `todo` |
| [[Integrate e-commerce checkout custom flavor surcharge and order queue for Custom Hotsauce Business]] | 🟡 Medium | `{(today + datetime.timedelta(days=34)).strftime('%Y-%m-%d')}` | `todo` |
| [[Execute 20-bottle pilot production run and sensory blind testing for Custom Hotsauce Business]] | 🔴 High | `{(today + datetime.timedelta(days=42)).strftime('%Y-%m-%d')}` | `todo` |

---

## 🔗 Related Vault Notes
- Origin Note: [[Custom Hotsauce Business]]
- Business & Operations: [[Creating a Brand]] • [[LLC]] • [[Financial Plan]]
- Pipeline & Ideas: [[Ideas Hub]] • [[Ideas.base]]
- Task Tracker: [[Tasks Hub]] • [[Tasks.base]]
"""
    with open(project_file, "w", encoding="utf-8") as f:
        f.write(content)

    tasks = [
        ("Standardize base pepper fermentation recipes and pH testing protocol for Custom Hotsauce Business", 5, "🔴 High", [
            "Test 3 base mash recipes: Fermented Habanero, Roasted Jalapeño-Poblano, and Ghost Pepper",
            "Establish lacto-fermentation brine ratios (2.5% to 3.5% non-iodized salt)",
            "Calibrate Apera digital pH meter and document protocol ensuring final pH < 3.8",
            "Verify shelf stability and emulsion hold with 0.15% xanthan gum"
        ]),
        ("Research FDA cottage food regulations and commercial kitchen licensing for Custom Hotsauce Business", 11, "🔴 High", [
            "Review California Department of Public Health (CDPH) Cottage Food Operations Class A/B requirements",
            "Investigate acidified food Better Process Control School (BPCS) certification rules",
            "Locate and compare 3 local San Diego commercial commissary kitchens with hourly rates",
            "Draft standard operating procedures (SOP) for hot-fill-and-hold at 185°F"
        ]),
        ("Source bottles tamper-evident shrink bands and custom label printer for Custom Hotsauce Business", 18, "🟡 Medium", [
            "Order sample cases of 5 oz flint glass woozy bottles with 24mm neck finish",
            "Source orifice reducers, ribbed plastic caps, and heat shrink bands",
            "Procure Munbyn thermal label printer and oil/water resistant continuous label rolls",
            "Test heat gun shrink band application timing and seal durability"
        ]),
        ("Build interactive animated bottle builder UI with drag-and-drop ingredients for Custom Hotsauce Business", 26, "🔴 High", [
            "Develop React/Three.js or Canvas bottle mockup with animated ingredient fill levels",
            "Build drag-and-drop ingredient trays for base peppers, aromatics, and spices",
            "Implement recommendation engine giving flavor harmony tips and warning of bad clashes",
            "Connect live Scoville heat estimation index bar that recalculates on each selection"
        ]),
        ("Integrate e-commerce checkout custom flavor surcharge and order queue for Custom Hotsauce Business", 34, "🟡 Medium", [
            "Build pricing engine: $14 base with 3 ingredients, +$1.25 per additional premium add-in",
            "Integrate Stripe Elements for seamless mobile-friendly checkout",
            "Generate backend kitchen fulfillment manifest converting percentages to gram weights",
            "Create automated email notification system with custom bottle preview and order ID"
        ]),
        ("Execute 20-bottle pilot production run and sensory blind testing for Custom Hotsauce Business", 42, "🔴 High", [
            "Cook and bottle 20 pilot units spanning diverse customer recipe combinations",
            "Log batch temperatures, fill times, and final measured equilibrium pH readings",
            "Conduct blind sensory tasting panel evaluating heat balance, acidity, and texture",
            "Package in corrugated shipping cartons and test simulated shipping drop resistance"
        ]),
    ]
    for task_desc, days, priority, checklist in tasks:
        due = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        spawn_atomic_task(task_desc, priority, due, title, checklist, today)

    print(f"✅ Compiled Blueprint: 10_Projects/{title}/{title}.md & 6 Sprint Tasks")
    return project_file

def compile_generic_software(title, source_text, target_dir, today):
    today_str = today.strftime("%Y-%m-%d")
    target_date = (today + datetime.timedelta(days=45)).strftime("%Y-%m-%d")
    project_file = os.path.join(target_dir, f"{title}.md")

    content = f"""---
title: "{title}"
type: project
project_type: software-ai
status: active
priority: "🔴 High"
start_date: "{today_str}"
target_date: "{target_date}"
tags:
  - project
  - software
  - ai-ml
  - full-stack
---

# 🚀 Project: {title}

> [!important] Mission Objective
> Develop, evaluate, and ship an end-to-end production application combining modern AI algorithms with an intuitive, responsive user interface.

---

## 🏛️ System Architecture Blueprint

```mermaid
graph TD
    User[User / Client Interface] --> Frontend[Frontend: Next.js / React / Streamlit]
    Frontend --> API[API Gateway: FastAPI / Python]
    API --> Logic[Core Service: Agent / Optimization Engine]
    Logic --> Vector[Vector & Document Store]
    Logic --> Models[Inference: Local SLM / Gemini API]
    Logic --> DB[(Relational DB: SQLite / Postgres)]
```

### Technical Stack & Dependencies
- **Frontend**: Next.js (TypeScript) / Streamlit
- **Backend API**: FastAPI (Python 3.11+)
- **AI / ML Engine**: PyTorch / LangChain / custom agent harness
- **Data & Storage**: SQLite / PostgreSQL / ChromaDB
- **Containerization**: [[Docker]] & Docker Compose

---

## 🎯 Phased Milestones & Build Sprints

### Milestone 1: Data Contracts & Architecture Scaffold (Days 1–10)
- [ ] Define JSON schemas and API data contracts
- [ ] Scaffold repository with FastAPI backend and frontend client
- [ ] Set up local Dockerized development environment

### Milestone 2: Core Algorithm & Model Pipeline (Days 11–25)
- [ ] Implement core data ingestion and feature engineering pipelines
- [ ] Build and benchmark the primary model/optimization algorithm
- [ ] Add unit tests and performance benchmarks

### Milestone 3: UI & Interactive Dashboard (Days 26–35)
- [ ] Build interactive telemetry dashboard and parameter controls
- [ ] Integrate error handling and session state
- [ ] Implement export functionality (CSV / JSON / PDF)

### Milestone 4: Verification, Security & Production Packaging (Days 36–45)
- [ ] Run end-to-end integration tests
- [ ] Audit credentials, environment variables, and authentication
- [ ] Build production container and write deployment guide

---

## 🔗 Related Vault Notes
- Technical Reference: [[Knowledge Hub]] • [[AI Agents]] • [[Simple Edge Serving]]
- Action Sprints: [[Tasks Hub]] • [[Tasks.base]]
"""
    with open(project_file, "w", encoding="utf-8") as f:
        f.write(content)

    tasks = [
        (f"Define schema and data contracts for {title}", 7, "🔴 High", None),
        (f"Scaffold FastAPI backend and client repo for {title}", 12, "🔴 High", None),
        (f"Implement core processing engine for {title}", 20, "🔴 High", None),
        (f"Integrate model inference pipeline for {title}", 27, "🟡 Medium", None),
        (f"Build interactive frontend dashboard for {title}", 34, "🟡 Medium", None),
        (f"End-to-end integration tests and Docker deploy for {title}", 42, "🔴 High", None),
    ]
    for task_desc, days, priority, checklist in tasks:
        due = (today + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
        spawn_atomic_task(task_desc, priority, due, title, checklist, today)

    print(f"✅ Compiled Generic Software Project: 10_Projects/{title}/{title}.md")
    return project_file

def compile_project_by_name(project_name, today=None):
    if today is None:
        today = datetime.date.today()

    clean_name = project_name.strip()
    target_dir = os.path.join(PROJECTS_DIR, clean_name)
    os.makedirs(target_dir, exist_ok=True)

    lower_name = clean_name.lower()
    if "trend scraper" in lower_name:
        compile_trend_scraper(target_dir, today)
        update_home_dashboards(clean_name, "Software / AI")
    elif "dynasty basketball" in lower_name or "basketball predictor" in lower_name:
        compile_dynasty_basketball(target_dir, today)
        update_home_dashboards(clean_name, "Software / AI")
    elif "job recruiter" in lower_name or "recruiter agent" in lower_name or "xavier" in lower_name:
        compile_job_recruiter(target_dir, today)
        update_home_dashboards(clean_name, "Software / AI")
    elif "hotsauce" in lower_name or "hot sauce" in lower_name:
        compile_custom_hotsauce(target_dir, today)
        update_home_dashboards(clean_name, "Physical / Commerce")
    else:
        source_text = ""
        source_file = find_source_note(clean_name)
        if source_file:
            with open(source_file, "r", encoding="utf-8") as f:
                source_text = f.read()
        compile_generic_software(clean_name, source_text, target_dir, today)
        update_home_dashboards(clean_name, "Software / AI")

def main():
    parser = argparse.ArgumentParser(description="Pico Vault Idea-to-Project Compiler")
    parser.add_argument("--idea", type=str, help="Name of idea/inspo note to compile into an active project")
    parser.add_argument("--new", type=str, help="New project name to create from scratch")
    parser.add_argument("--type", choices=["software", "diy", "commerce"], help="Force project type")
    parser.add_argument("--priority-all", action="store_true", help="Compile all 4 priority ideas into full project blueprints")
    args = parser.parse_args()

    today = datetime.date.today()

    if args.priority_all:
        print("🚀 Compiling all 4 Priority Project Blueprints...")
        priority_projects = [
            "Trend Scraper",
            "Dynasty Basketball Predictor",
            "Job Recruiter Agent",
            "Custom Hotsauce Business"
        ]
        for proj in priority_projects:
            compile_project_by_name(proj, today)
        print("\n🎉 All 4 Priority Project Blueprints successfully compiled!")
        return

    project_title = args.new or args.idea
    if not project_title:
        print("Please provide --idea <name>, --new <name>, or --priority-all")
        return

    compile_project_by_name(project_title, today)
    print(f"🎉 Project compilation complete for [[{project_title}]]!")

if __name__ == "__main__":
    main()
