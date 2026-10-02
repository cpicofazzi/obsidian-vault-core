#!/usr/bin/env python3
"""
Vault Ingestion & Smart Intake Engine for pico-vault
----------------------------------------------------
Automatically ingests raw notes, tasks, ideas, research queries, and inspiration media,
classifies them, formats them with Obsidian Flavored Markdown & properties,
links them to relevant vault knowledge hubs, and registers them in Obsidian Bases.

Usage:
    python scripts/vault_ingest.py                  # Processes 00_Inbox/Quick Capture.md
    python scripts/vault_ingest.py --dry-run        # Preview actions without modifying files
    python scripts/vault_ingest.py --input "..."    # Ingest a single raw string directly
"""

import os
import re
import sys
import datetime
import argparse
import io

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INBOX_FILE = os.path.join(VAULT_ROOT, "00_Inbox", "Quick Capture.md")
TASKS_DIR = os.path.join(VAULT_ROOT, "40_Tasks")
IDEAS_DIR = os.path.join(VAULT_ROOT, "30_Ideas")
KNOWLEDGE_DIR = os.path.join(VAULT_ROOT, "50_Knowledge")
AREAS_DIR = os.path.join(VAULT_ROOT, "20_Areas")
INSP_ROOT = os.path.join(VAULT_ROOT, "60_Inspiration")

def get_vault_index():
    """Build a mapping of note names (lowercase) to canonical note basenames."""
    index = {}
    for root, dirs, files in os.walk(VAULT_ROOT):
        rel = os.path.relpath(root, VAULT_ROOT)
        if rel.startswith(".obsidian") or rel.startswith(".agents") or rel.startswith(".git"):
            continue
        for f in files:
            if f.endswith(".md"):
                base = f[:-3]
                index[base.lower()] = base
    return index

def auto_wikilink(text, current_title, vault_index):
    """Automatically convert mentions of known vault notes into [[Wikilinks]]."""
    cur_lower = current_title.lower()
    for lower_name, canonical_name in sorted(vault_index.items(), key=lambda x: len(x[0]), reverse=True):
        if len(lower_name) < 4 or lower_name == cur_lower:
            continue
        # Avoid double-linking if already inside [[...]]
        pattern = rf'(?<!\[\[)\b({re.escape(canonical_name)})\b(?!\]\])'
        text = re.sub(pattern, rf'[[\1]]', text, flags=re.IGNORECASE)
    return text

def sanitize_filename(name):
    clean = re.sub(r'\[\[(.*?)\]\]', r'\1', name)
    clean = re.sub(r'[\\/*?:"<>|\[\]]', "", clean).strip()
    return clean[:80] if len(clean) > 80 else clean

def parse_entry(raw_line):
    line = raw_line.strip()
    if not line or line.startswith("<!--") or line.startswith("#") or line.startswith(">"):
        return None

    today_str = datetime.date.today().strftime("%Y-%m-%d")

    # Strip markdown list bullets first (- , * , + )
    clean_line = re.sub(r'^[-*+]\s+', '', line).strip()

    # 1. Inspo & Media detection
    if (clean_line.lower().startswith("inspo:") or 
        clean_line.lower().startswith("media:") or 
        clean_line.lower().startswith("link:") or 
        "http://" in clean_line or "https://" in clean_line or
        "#inspo" in clean_line.lower()):
        
        raw_clean = re.sub(r'^(inspo:\s*|media:\s*|link:\s*)', '', clean_line, flags=re.IGNORECASE).strip()
        url_match = re.search(r'(https?://[^\s]+)', raw_clean)
        url = url_match.group(1) if url_match else ""
        desc = raw_clean.replace(url, "").strip() if url else raw_clean
        desc = re.sub(r'#inspo\b', '', desc, flags=re.IGNORECASE).strip()
        if not desc:
            desc = f"Media Inspo {datetime.datetime.now().strftime('%H%M%S')}"

        # Categorize
        category = "AI & Autonomous Agents"
        t_low = desc.lower()
        if any(w in t_low for w in ["running", "mobility", "fitness", "kettlebell", "lacrosse", "soccer", "posture", "stretch", "hyrox", "gym", "squat"]):
            category = "Athletics & Training"
        elif any(w in t_low for w in ["gardening", "plant", "lavender", "pruning", "seed", "mosquito", "soil", "herb", "bed"]):
            category = "Gardening & Homestead"
        elif any(w in t_low for w in ["japan", "food", "kyoto", "tokyo", "travel", "sandwich", "book", "san diego", "movie", "anime", "recipe", "fest"]):
            category = "Culture & Lifestyle"
        elif any(w in t_low for w in ["robot", "arduino", "drone", "electronics", "motor", "hardware", "esp32", "uav", "aerospace"]):
            category = "Robotics & Hardware"
        elif any(w in t_low for w in ["adirondack", "woodworking", "workbench", "clamp", "jig", "lumber"]):
            category = "Woodworking & Workshop"
        elif any(w in t_low for w in ["github", "repo", "linux", "vs code", "docker", "kubernetes", "sqlite", "scraper", "cli", "python"]):
            category = "Dev Tools & Repos"

        title = sanitize_filename(desc)
        return {
            "type": "inspiration",
            "title": title,
            "category": category,
            "url": url,
            "raw": line,
            "created": today_str
        }

    # 2. Task detection
    if line.startswith("- [ ]") or clean_line.lower().startswith("task:") or clean_line.lower().startswith("todo:"):
        clean = re.sub(r'^(- \[[ x]\]\s*|task:\s*|todo:\s*)', '', line if line.startswith("- [ ]") else clean_line, flags=re.IGNORECASE).strip()
        clean = re.sub(r'^(task:\s*|todo:\s*)', '', clean, flags=re.IGNORECASE).strip()
        priority = "🟡 Medium"
        if "!high" in clean.lower() or "p1" in clean.lower() or "urgent" in clean.lower():
            priority = "🔴 High"
            clean = re.sub(r'(!high|p1|urgent)', '', clean, flags=re.IGNORECASE).strip()
        elif "!low" in clean.lower() or "p3" in clean.lower():
            priority = "🟢 Low"
            clean = re.sub(r'(!low|p3)', '', clean, flags=re.IGNORECASE).strip()

        due_match = re.search(r'due:(\d{4}-\d{2}-\d{2})', clean)
        due_date = due_match.group(1) if due_match else (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d")
        if due_match:
            clean = clean.replace(due_match.group(0), "").strip()

        title = sanitize_filename(clean)
        return {
            "type": "task",
            "title": title,
            "priority": priority,
            "due_date": due_date,
            "raw": line,
            "created": today_str
        }

    # 3. Idea detection
    if clean_line.lower().startswith("idea:") or "app" in clean_line.lower() or "startup" in clean_line.lower():
        clean = re.sub(r'^idea:\s*', '', clean_line, flags=re.IGNORECASE).strip()
        domain = "AI/Tech"
        folder_sub = "AI & Tech"
        if any(w in clean.lower() for w in ["business", "brand", "commerce", "store", "sauce", "food", "apparel"]):
            domain = "Business"
            folder_sub = "Business & Commerce"
        elif any(w in clean.lower() for w in ["music", "art", "game", "sports", "dj", "map"]):
            domain = "Creative"
            folder_sub = "Creative & Sports"

        title = sanitize_filename(clean)
        return {
            "type": "idea",
            "title": title,
            "domain": domain,
            "folder_sub": folder_sub,
            "raw": line,
            "created": today_str
        }

    # 4. Research detection
    if clean_line.lower().startswith("research:") or clean_line.lower().startswith("topic:") or clean_line.lower().startswith("paper:"):
        clean = re.sub(r'^(research:\s*|topic:\s*|paper:\s*)', '', clean_line, flags=re.IGNORECASE).strip()
        subfolder = "AI & Machine Learning"
        if any(w in clean.lower() for w in ["rl", "reinforcement", "policy", "actor-critic", "gymnasium", "q-learning", "ppo", "dpo", "reward"]):
            subfolder = "Reinforcement Learning/Environments & Theory"
        elif any(w in clean.lower() for w in ["docker", "k8s", "kubernetes", "helm", "edge", "deploy", "serving"]):
            subfolder = "Edge & Cloud Systems"

        title = sanitize_filename(clean)
        return {
            "type": "research",
            "title": title,
            "subfolder": subfolder,
            "raw": line,
            "created": today_str
        }

    # 5. Fallback: Quick Note
    clean = re.sub(r'^- \s*', '', line).strip()
    title = sanitize_filename(clean)
    return {
        "type": "note",
        "title": title,
        "raw": line,
        "created": today_str
    }

def create_inspiration_note(entry, vault_index, dry_run=False):
    # If URL is a GitHub repo or arXiv paper, use deep research analyzer
    url = entry.get("url", "")
    if url and ("github.com/" in url or "arxiv.org/" in url) and not dry_run:
        try:
            import enrich_repos
            analyzed_path = enrich_repos.process_url(url)
            if analyzed_path:
                return analyzed_path
        except Exception as e:
            print(f"⚠️ enrich_repos fallback: {e}")

    title = entry["title"]
    category = entry["category"]
    folder = os.path.join(INSP_ROOT, category)
    filename = f"{title}.md"
    path = os.path.join(folder, filename)

    fits = []
    actions = []
    if category == "Athletics & Training":
        fits.append("- **Fit**: Integrates with [[Industry FC]] and [[2025 Workouts]]")
        actions.append("- [ ] Test drill or recovery protocol during next training session")
    elif category == "Gardening & Homestead":
        fits.append("- **Fit**: Integrates with [[Gardening]] and [[Custom Hotsauce Business]]")
        actions.append("- [ ] Apply technique to garden beds or indoor seedling station")
    elif category == "AI & Autonomous Agents":
        fits.append("- **Fit**: Maps to [[AI Agents]] and [[Job Search]]")
        actions.append("- [ ] Review architecture pattern and test local implementation")
    elif category == "Dev Tools & Repos":
        fits.append("- **Fit**: Tooling for [[Trend Scraper]] and [[Simple Edge Serving]]")
        actions.append("- [ ] Clone repo or test CLI tool in local sandbox")
    elif category == "Robotics & Hardware":
        fits.append("- **Fit**: Connects to [[Gymnasium Environments]] and hardware builds")
        actions.append("- [ ] Review BOM and circuit schematics")
    elif category == "Woodworking & Workshop":
        fits.append("- **Fit**: Workshop setup and DIY builds")
        actions.append("- [ ] Check material dimensions and tool requirements")
    else:
        fits.append("- **Fit**: Curated reference for [[Trip Planner]] or [[San Diego Move]]")
        actions.append("- [ ] Save key dates or locations to itinerary")

    tag_cat = category.lower().replace(" & ", "-").replace(" ", "-")
    content = f'''---
title: "{title}"
type: inspiration
category: "{category}"
url: "{entry.get('url', '')}"
created: "{entry['created']}"
tags:
  - inspiration
  - {tag_cat}
---

# {title}

> [!quote] Content Summary
> {entry['raw']}

---

## 💡 Implementation Potential & Vault Connections

### 🎯 Where It Fits in Your Vault
{chr(10).join(fits)}

### ⚡ Action Items & Experiments
{chr(10).join(actions)}

---

## 📌 Context & Metadata
- **Original Link**: {f'<{entry.get("url")}>' if entry.get('url') else 'None recorded'}
- **Domain Category**: [[Inspiration Hub|{category}]]
'''
    content = auto_wikilink(content, title, vault_index)
    if not dry_run:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[{'DRY-RUN' if dry_run else 'CREATED'}] Inspiration -> 60_Inspiration/{category}/{filename}")
    return path

def create_task_note(entry, vault_index, dry_run=False):
    title = entry["title"]
    filename = f"{title}.md"
    path = os.path.join(TASKS_DIR, filename)

    content = f'''---
title: "{title}"
type: task
status: todo
priority: "{entry['priority']}"
due_date: "{entry['due_date']}"
project: ""
created: "{entry['created']}"
completed_date: ""
tags:
  - task
---

# {title}

> [!todo] Task Summary
> {entry['raw']}

## Action Items
- [ ] Initial scoping and preparation
- [ ] Execution
- [ ] Verification and sign-off

## Related
- Hub: [[Tasks Hub]]
'''
    content = auto_wikilink(content, title, vault_index)
    if not dry_run:
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[{'DRY-RUN' if dry_run else 'CREATED'}] Task -> 40_Tasks/{filename}")
    return path

def create_idea_note(entry, vault_index, dry_run=False):
    title = entry["title"]
    folder = os.path.join(IDEAS_DIR, entry["folder_sub"])
    filename = f"{title}.md"
    path = os.path.join(folder, filename)

    content = f'''---
title: "{title}"
type: idea
stage: "💡 Spark"
domain: "{entry['domain']}"
effort: "Medium"
value: "High"
created: "{entry['created']}"
updated: "{entry['created']}"
tags:
  - idea
  - {entry['domain'].lower().replace('/', '-')}
---

# {title}

> [!tip] Value Proposition
> {entry['raw']}

## The Core Concept
- 

## Target Audience / Use Cases
- 

## Technical Scoping & Architecture
- **Potential Stack**: 
- **Key Integrations**: 

## Next Action Items
- [ ] Outline high-level requirements
- [ ] Evaluate domain viability & user feedback
- [ ] Define proof-of-concept scope

## Related
- Hub: [[Ideas Hub]]
'''
    content = auto_wikilink(content, title, vault_index)
    if not dry_run:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[{'DRY-RUN' if dry_run else 'CREATED'}] Idea -> 30_Ideas/{entry['folder_sub']}/{filename}")
    return path

def create_research_note(entry, vault_index, dry_run=False):
    title = entry["title"]
    folder = os.path.join(KNOWLEDGE_DIR, entry["subfolder"].replace("/", os.sep))
    filename = f"{title}.md"
    path = os.path.join(folder, filename)

    content = f'''---
title: "{title}"
type: research
tags:
  - research
  - technical
status: active
created: "{entry['created']}"
updated: "{entry['created']}"
aliases: []
---

# {title}

> [!abstract] Research Focus
> Ingested exploration topic: {entry['raw']}

## Executive Summary
- Core motivation, architecture, and current state-of-the-art methodology.

## Theoretical Background & Mathematical Formulation
$$
$$

## Key Components & Architecture
- 

## Comparative Analysis & Tradeoffs
- Advantages vs prior approaches
- Limitations and compute bottlenecks

## Implementation Notes & Code
```python
# Implementation scaffold
```

## References & Vault Connections
- Hub: [[Knowledge Hub]]
'''
    content = auto_wikilink(content, title, vault_index)
    if not dry_run:
        os.makedirs(folder, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
    print(f"[{'DRY-RUN' if dry_run else 'CREATED'}] Research -> 50_Knowledge/{entry['subfolder']}/{filename}")
    return path

def process_inbox(dry_run=False):
    if not os.path.exists(INBOX_FILE):
        print(f"Quick Capture file not found: {INBOX_FILE}")
        return

    with open(INBOX_FILE, "r", encoding="utf-8") as f:
        lines = f.readlines()

    dropzone_marker = "<!-- New raw inputs land below this line -->"
    marker_idx = -1
    for i, l in enumerate(lines):
        if dropzone_marker in l:
            marker_idx = i
            break

    if marker_idx == -1:
        print("Dropzone marker not found in Quick Capture.md. Check file format.")
        return

    header_lines = lines[:marker_idx + 1]
    intake_lines = []
    footer_lines = []
    in_footer = False

    for l in lines[marker_idx + 1:]:
        if l.strip().startswith("---") or "Ingestion Instructions" in l:
            in_footer = True
        if in_footer:
            footer_lines.append(l)
        else:
            # Ignore subheaders like ### 🎨 Inspo Dropzone
            if l.strip() and not l.strip().startswith("###"):
                intake_lines.append(l)

    if not intake_lines:
        print("No raw entries found in Quick Capture dropzone.")
        return

    vault_index = get_vault_index()
    processed_count = 0

    for raw_line in intake_lines:
        entry = parse_entry(raw_line)
        if not entry:
            continue
        if entry["type"] == "inspiration":
            create_inspiration_note(entry, vault_index, dry_run=dry_run)
            processed_count += 1
        elif entry["type"] == "task":
            create_task_note(entry, vault_index, dry_run=dry_run)
            processed_count += 1
        elif entry["type"] == "idea":
            create_idea_note(entry, vault_index, dry_run=dry_run)
            processed_count += 1
        elif entry["type"] == "research":
            create_research_note(entry, vault_index, dry_run=dry_run)
            processed_count += 1
        elif entry["type"] == "note":
            p = os.path.join(AREAS_DIR, "Personal", f"{entry['title']}.md")
            if not dry_run:
                with open(p, "w", encoding="utf-8") as f:
                    f.write(f"# {entry['title']}\n\n{entry['raw']}\n")
            print(f"[{'DRY-RUN' if dry_run else 'CREATED'}] Note -> 20_Areas/Personal/{entry['title']}.md")
            processed_count += 1

    if not dry_run and processed_count > 0:
        # Preserve subheaders in dropzone
        preserved_dropzone = "\n### 🎨 Inspo Dropzone (Media, Repos, DIY, Reels)\n\n### ⚡ Quick Tasks & Ideas Dropzone\n\n"
        new_content = "".join(header_lines) + preserved_dropzone + "".join(footer_lines)
        with open(INBOX_FILE, "w", encoding="utf-8") as f:
            f.write(new_content)
        print(f"Successfully processed and cleared {processed_count} items from Quick Capture!")

def main():
    parser = argparse.ArgumentParser(description="Pico Vault Smart Ingestion Engine")
    parser.add_argument("--dry-run", action="store_true", help="Preview intake actions without writing")
    parser.add_argument("--input", type=str, help="Process a single raw entry directly")
    args = parser.parse_args()

    if args.input:
        entry = parse_entry(args.input)
        if not entry:
            print("Could not parse input entry.")
            return
        v_idx = get_vault_index()
        if entry["type"] == "inspiration": create_inspiration_note(entry, v_idx, args.dry_run)
        elif entry["type"] == "task": create_task_note(entry, v_idx, args.dry_run)
        elif entry["type"] == "idea": create_idea_note(entry, v_idx, args.dry_run)
        elif entry["type"] == "research": create_research_note(entry, v_idx, args.dry_run)
    else:
        process_inbox(dry_run=args.dry_run)

if __name__ == "__main__":
    main()
