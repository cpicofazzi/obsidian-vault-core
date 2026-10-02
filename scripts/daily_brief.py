#!/usr/bin/env python3
"""
Daily AI Briefing & Serendipity Engine for pico-vault
----------------------------------------------------
Compiles a morning briefing in 01_Dashboard/Daily Briefing.md:
- 🔴 Top priority tasks due soon
- 💡 Idea spotlight from 30_Ideas/
- 🛠️ DIY build of the week from 60_Inspiration/
- 🧠 Spaced-repetition concept from 50_Knowledge/
- 🔮 Serendipity Engine cross-pollinating ML algorithms with maker projects

Usage:
    python scripts/daily_brief.py
"""

import os
import sys
import re
import random
import datetime

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TASKS_DIR = os.path.join(VAULT_ROOT, "40_Tasks")
IDEAS_DIR = os.path.join(VAULT_ROOT, "30_Ideas")
INSP_DIR = os.path.join(VAULT_ROOT, "60_Inspiration")
KNOWLEDGE_DIR = os.path.join(VAULT_ROOT, "50_Knowledge")
DASHBOARD_DIR = os.path.join(VAULT_ROOT, "01_Dashboard")
BRIEFING_FILE = os.path.join(DASHBOARD_DIR, "Daily Briefing.md")

def get_active_tasks():
    tasks = []
    if not os.path.exists(TASKS_DIR):
        return tasks
    for f in os.listdir(TASKS_DIR):
        if f.endswith(".md") and f != "Tasks Hub.md":
            p = os.path.join(TASKS_DIR, f)
            with open(p, "r", encoding="utf-8", errors="ignore") as file:
                text = file.read()
            # Extract status, priority, due
            status_m = re.search(r'status:\s*([a-zA-Z0-9_\-]+)', text)
            status = status_m.group(1).lower() if status_m else "todo"
            if status == "done":
                continue
            
            prio_m = re.search(r'priority:\s*"?([^"\n]+)"?', text)
            prio = prio_m.group(1) if prio_m else "🟡 Medium"
            
            due_m = re.search(r'due_date:\s*"?([^"\n]+)"?', text)
            due = due_m.group(1) if due_m else "No date"

            proj_m = re.search(r'project:\s*"?([^"\n]+)"?', text)
            project = proj_m.group(1) if proj_m else "General"

            title = f[:-3]
            # Priority rank: High=0, Med=1, Low=2
            rank = 0 if "high" in prio.lower() else (1 if "med" in prio.lower() else 2)
            tasks.append({
                "title": title,
                "priority": prio,
                "due": due,
                "project": project,
                "rank": rank
            })
    tasks.sort(key=lambda x: (x["rank"], x["due"]))
    return tasks

def get_random_note(folder):
    candidates = []
    for root, dirs, files in os.walk(folder):
        for f in files:
            if f.endswith(".md") and not f.endswith("Hub.md") and not f.endswith(".base"):
                candidates.append((f[:-3], os.path.join(root, f)))
    return random.choice(candidates) if candidates else (None, None)

def get_diy_inspiration():
    diy_folders = [
        os.path.join(INSP_DIR, "Robotics & Hardware"),
        os.path.join(INSP_DIR, "Woodworking & Workshop"),
        os.path.join(INSP_DIR, "Gardening & Homestead")
    ]
    candidates = []
    for folder in diy_folders:
        if os.path.exists(folder):
            for f in os.listdir(folder):
                if f.endswith(".md"):
                    candidates.append((f[:-3], os.path.join(folder, f)))
    return random.choice(candidates) if candidates else (None, None)

def generate_serendipity_pairing(ml_concept, idea_title, diy_title):
    pairings = [
        f"**Idea Cross-Pollination**: What if you applied [[{ml_concept}]] to optimize the predictive logic in [[{idea_title}]]?",
        f"**Hardware Integration**: How could an embedded edge model using [[{ml_concept}]] enhance the telemetry or autonomous control in [[{diy_title}]]?",
        f"**Product Innovation**: Could the core feedback mechanism from [[{idea_title}]] be adapted to run locally on a low-power microcontroller like in [[{diy_title}]]?"
    ]
    return random.choice(pairings)

def main():
    today = datetime.date.today()
    date_str = today.strftime("%A, %B %d, %Y")
    today_iso = today.strftime("%Y-%m-%d")

    active_tasks = get_active_tasks()
    top_tasks = active_tasks[:4]

    idea_name, idea_path = get_random_note(IDEAS_DIR)
    ml_name, ml_path = get_random_note(KNOWLEDGE_DIR)
    diy_name, diy_path = get_diy_inspiration()

    # Read summaries
    idea_desc = "Review concept and outline initial requirements."
    if idea_path:
        with open(idea_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for l in lines:
            if l.startswith("> [!tip]") or l.startswith("> [!abstract]"):
                idea_desc = l.strip()
                break

    ml_desc = "Core machine learning theory and mathematical architecture."
    if ml_path:
        with open(ml_path, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        for l in lines:
            if l.startswith("> [!abstract]") or l.startswith("> [!quote]"):
                ml_desc = l.strip()
                break

    serendipity_text = generate_serendipity_pairing(ml_name, idea_name, diy_name)

    task_rows = []
    if top_tasks:
        for t in top_tasks:
            task_rows.append(f"- [ ] **[[{t['title']}]]** — {t['priority']} | Due: `{t['due']}` | {t['project']}")
    else:
        task_rows.append("- [x] No overdue or pending high-priority tasks. Ready for new project sprints!")

    tasks_md = "\n".join(task_rows)

    briefing_content = f'''---
title: "Daily Briefing"
type: briefing
date: "{today_iso}"
tags:
  - briefing
  - daily
  - command-center
---

# 🌅 Morning Briefing: {date_str}

> [!tip] Focus of the Day
> Maintain momentum on active project sprints. Build, prototype, and execute.

---

## 🔴 Priority Action Items (Next Up)

{tasks_md}

*See complete queue in [[Tasks Hub|Tasks Hub]] or [[Tasks.base]].*

---

## 💡 Idea Spotlight
**[[{idea_name}]]**
{idea_desc}
- [ ] Review scope and consider compiling into a full sprint via `python scripts/compile_project.py --idea "{idea_name}"`

---

## 🛠️ DIY Build of the Week
**[[{diy_name}]]**
- Workshop inspiration from [[Inspiration Hub]]
- [ ] Review components and bill of materials for weekend build

---

## 🧠 Spaced-Repetition: Machine Learning Architecture
**[[{ml_name}]]**
{ml_desc}
- Explore connections in [[Knowledge Hub]]

---

## 🔮 The Serendipity Engine (Cross-Pollination)

> [!quote] Unexpected Intersection
> {serendipity_text}

---

## ⚡ Quick Links
- [[Home|Command Center]] • [[Quick Capture|Quick Capture]] • [[Tasks Hub|Tasks]] • [[Ideas Hub|Ideas]] • [[Inspiration Hub|Inspiration]]
'''
    os.makedirs(DASHBOARD_DIR, exist_ok=True)
    with open(BRIEFING_FILE, "w", encoding="utf-8") as f:
        f.write(briefing_content)

    print(f"✅ Daily Briefing generated: 01_Dashboard/Daily Briefing.md")

if __name__ == "__main__":
    main()
