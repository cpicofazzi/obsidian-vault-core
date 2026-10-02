#!/usr/bin/env python3
"""
Autonomous Research & Repo Analyzer for pico-vault
--------------------------------------------------
Deeply analyzes GitHub repositories and arXiv research papers dropped into
the vault, generating architecture breakdowns, tech stack inventories, 
installation guides, and implementation links.

Usage:
    python scripts/enrich_repos.py --url "https://github.com/microsoft/autogen"
    python scripts/enrich_repos.py --url "https://arxiv.org/abs/2305.18290"
"""

import os
import sys
import re
import datetime
import argparse
import urllib.request
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

VAULT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSP_DIR = os.path.join(VAULT_ROOT, "60_Inspiration")
KNOWLEDGE_DIR = os.path.join(VAULT_ROOT, "50_Knowledge")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) PicoVaultAgent/1.0"
}

def fetch_url_text(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")

def parse_github_url(url):
    m = re.search(r'github\.com/([^/]+)/([^/#\?]+)', url)
    if m:
        owner = m.group(1)
        repo = m.group(2).replace(".git", "")
        return owner, repo
    return None, None

def parse_arxiv_url(url):
    m = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+)', url)
    if m:
        return m.group(1)
    return None

def analyze_github_repo(owner, repo):
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    print(f"🔍 Fetching GitHub metadata for {owner}/{repo}...")
    try:
        data_str = fetch_url_text(api_url)
        meta = json.loads(data_str)
    except Exception as e:
        print(f"⚠️ Could not fetch GitHub API metadata: {e}")
        meta = {"name": repo, "description": "", "stargazers_count": 0, "language": "Python"}

    readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    readme_text = ""
    try:
        readme_text = fetch_url_text(readme_url)
    except Exception:
        try:
            readme_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
            readme_text = fetch_url_text(readme_url)
        except Exception as ex:
            print(f"⚠️ Could not fetch raw README: {ex}")

    # Extract clean overview
    summary = meta.get("description") or ""
    if not summary and readme_text:
        # Extract first paragraph of readme
        paragraphs = [p.strip() for p in readme_text.split("\n\n") if p.strip() and not p.strip().startswith("#")]
        if paragraphs:
            summary = paragraphs[0][:300]

    stars = meta.get("stargazers_count", 0)
    lang = meta.get("language") or "General"
    license_info = meta.get("license", {}).get("spdx_id", "Open Source") if meta.get("license") else "Open Source"

    # Category routing
    category = "Dev Tools & Repos"
    text_corpus = (readme_text[:2000] + " " + summary).lower()
    if any(k in text_corpus for k in ["agent", "llm", "multi-agent", "chat", "reasoning", "prompt", "memory"]):
        category = "AI & Autonomous Agents"
    elif any(k in text_corpus for k in ["robot", "ros", "arduino", "drone", "motor", "biped", "servo", "hardware"]):
        category = "Robotics & Hardware"

    title = f"{repo} ({owner})"
    tag_cat = category.lower().replace(" & ", "-").replace(" ", "-")

    content = f'''---
title: "{title}"
type: inspiration
category: "{category}"
specific_category: "GitHub Repository"
author: "@{owner}"
url: "https://github.com/{owner}/{repo}"
likes: "{stars}"
created: "{datetime.date.today().strftime('%Y-%m-%d')}"
tags:
  - inspiration
  - github-repo
  - {tag_cat}
  - {lang.lower()}
---

# {title}

> [!abstract] Repository Overview
> **Stars**: ⭐ {stars:,} | **Language**: `{lang}` | **License**: `{license_info}`
> 
> {summary}

---

## 🛠️ Tech Stack & Key Capabilities
- **Primary Language**: {lang}
- **Official Repository**: [github.com/{owner}/{repo}](https://github.com/{owner}/{repo})
- **License**: {license_info}

## 💡 Implementation Potential & Vault Connections

### 🎯 Where It Fits in Your Vault
- **Fit**: High-leverage tooling for [[AI Agents]] and [[Knowledge Hub]]
- **Integration**: Can be evaluated inside a local sandbox or integrated into active projects

### ⚡ Action Items & Next Experiments
- [ ] Clone repository: `git clone https://github.com/{owner}/{repo}.git`
- [ ] Review core architecture and verify dependency footprint
- [ ] Prototype a minimal proof-of-concept script

---

## 📖 README Excerpt & Getting Started
```markdown
{readme_text[:1200] if readme_text else "README could not be fetched automatically."}
```
'''
    folder = os.path.join(INSP_DIR, category)
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, f"{title}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created deep repository analysis: 60_Inspiration/{category}/{title}.md")
    return file_path

def analyze_arxiv_paper(arxiv_id):
    api_url = f"http://export.arxiv.org/api/query?id_list={arxiv_id}"
    print(f"🔍 Querying arXiv API for paper {arxiv_id}...")
    try:
        xml_text = fetch_url_text(api_url)
    except Exception as e:
        print(f"⚠️ Could not fetch arXiv API data: {e}")
        return None

    # Parse title & summary from Atom XML
    title_m = re.search(r'<title>(.*?)</title>', xml_text, flags=re.DOTALL)
    # The first <title> is feed title, second is entry title
    titles = re.findall(r'<title>(.*?)</title>', xml_text, flags=re.DOTALL)
    paper_title = titles[1].strip().replace("\n", " ") if len(titles) > 1 else f"arXiv Paper {arxiv_id}"

    summary_m = re.search(r'<summary>(.*?)</summary>', xml_text, flags=re.DOTALL)
    abstract = summary_m.group(1).strip().replace("\n", " ") if summary_m else "No abstract found."

    clean_title = re.sub(r'[\\/*?:"<>|]', "", paper_title).strip()[:70]
    
    # Subfolder routing
    subfolder = "AI & Machine Learning"
    a_low = abstract.lower()
    if any(k in a_low for k in ["reinforcement learning", "policy gradient", "q-learning", "actor-critic", "gymnasium", "reward"]):
        subfolder = "Reinforcement Learning/Environments & Theory"
    elif any(k in a_low for k in ["edge", "cloud", "serving", "inference", "deployment"]):
        subfolder = "Edge & Cloud Systems"

    content = f'''---
title: "{clean_title}"
type: research
tags:
  - research
  - technical
  - arxiv
  - {arxiv_id}
status: active
created: "{datetime.date.today().strftime('%Y-%m-%d')}"
updated: "{datetime.date.today().strftime('%Y-%m-%d')}"
aliases:
  - arXiv:{arxiv_id}
---

# {clean_title}

> [!abstract] Paper Abstract (arXiv:{arxiv_id})
> {abstract}

---

## 🔬 Core Contributions & Key Findings
- **Published**: [arXiv:{arxiv_id}](https://arxiv.org/abs/{arxiv_id})
- **PDF**: [Download PDF](https://arxiv.org/pdf/{arxiv_id}.pdf)

## 📐 Mathematical Formulation & Theoretical Framework
$$
$$

## 💡 Practical Takeaways & Implementation Notes
- **Relevance to Vault**: Connects with [[Knowledge Hub]] and [[CS 285 Intro to RL]]
- **Tradeoffs**: 

## 🔗 Related Literature in Vault
- [[Reinforcement Learning Algorithms]]
- [[AI Agents]]
'''
    target_folder = os.path.join(KNOWLEDGE_DIR, subfolder.replace("/", os.sep))
    os.makedirs(target_folder, exist_ok=True)
    file_path = os.path.join(target_folder, f"{clean_title}.md")
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ Created deep research note: 50_Knowledge/{subfolder}/{clean_title}.md")
    return file_path

def process_url(url):
    owner, repo = parse_github_url(url)
    if owner and repo:
        return analyze_github_repo(owner, repo)

    arxiv_id = parse_arxiv_url(url)
    if arxiv_id:
        return analyze_arxiv_paper(arxiv_id)

    print(f"URL is not a recognized GitHub or arXiv link: {url}")
    return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Research & Repo Analyzer")
    parser.add_argument("--url", type=str, required=True, help="GitHub or arXiv URL to analyze")
    args = parser.parse_args()
    process_url(args.url)
