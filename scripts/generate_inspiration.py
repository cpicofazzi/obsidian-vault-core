import os
import csv
import re
import datetime

VAULT_ROOT = r"c:\Users\picof\Documents\pico-vault"
CSV_PATH = os.path.join(VAULT_ROOT, "scripts", "saved_posts.csv")
INSP_ROOT = os.path.join(VAULT_ROOT, "60_Inspiration")

CATEGORY_MAP = {
    "AI Agent Frameworks & Memory": "AI & Autonomous Agents",
    "AI Generative & Creative": "AI & Autonomous Agents",
    "Open-Source Drops": "Dev Tools & Repos",
    "Python / Data Science": "Dev Tools & Repos",
    "Robotics & RL": "Robotics & Hardware",
    "IoT & Microcontrollers": "Robotics & Hardware",
    "DIY Electronics": "Robotics & Hardware",
    "DIY / Woodworking": "Woodworking & Workshop",
    "Gardening & Homesteading": "Gardening & Homestead",
    "Soccer Training": "Athletics & Training",
    "Home Gym / Fitness": "Athletics & Training",
    "Language Learning": "Culture & Lifestyle",
    "Other": "Culture & Lifestyle",
    "Tech / AI & Coding": "AI & Autonomous Agents", # default, but sub-refined below
}

def sanitize(text):
    clean = re.sub(r'[\\/*?:"<>|\[\]]', "", text).strip()
    return clean[:70] if len(clean) > 70 else clean

def get_implementation_suggestions(broad_cat, specific_cat, summary, author):
    text = (summary + " " + specific_cat).lower()
    connections = []
    actions = []
    
    # 1. AI Agents & Memory
    if any(k in text for k in ["feynman", "research agent", "paper", "arxiv"]):
        connections.append("- **Fit**: Integrates with [[Research Paper Summarizer]] and [[Knowledge Hub]]")
        actions.append("- [ ] Test paper verification pipeline on recent RL papers")
    elif any(k in text for k in ["obsidian", "claude code", "skills", "pkm", "zazen"]):
        connections.append("- **Fit**: Enhances our current vault setup, [[obsidian-cli]], and [[obsidian-bases]]")
        actions.append("- [ ] Audit installed agent skills and test command-line vault automations")
    elif any(k in text for k in ["prime agent", "skillopt", "self-improving", "scaffolding"]):
        connections.append("- **Fit**: High relevance to your ML engineering work and [[AI Agents]]")
        actions.append("- [ ] Investigate test-time compute scaling and instruction optimization patterns")
    elif any(k in text for k in ["openworker", "coworker", "desktop app", "integrations"]):
        connections.append("- **Fit**: Relevant to [[Job Recruiter Agent]] and personal automation")
        actions.append("- [ ] Evaluate local desktop execution without cloud SaaS subscriptions")
    elif any(k in text for k in ["graph-of-agents", "multi-agent", "mixture-of-agents"]):
        connections.append("- **Fit**: Connects to [[Multi-Agent Reinforcement Learning Concepts]] and [[AI Agents]]")
        actions.append("- [ ] Implement coordinator filtering to reduce API token costs")
    elif any(k in text for k in ["code-review-graph", "tree-sitter", "token usage"]):
        connections.append("- **Fit**: Direct token optimization for large codebase navigation")
        actions.append("- [ ] Benchmark AST graph indexing vs full file dumps in coding workflows")

    # 2. Open-Source Repos & Dev Tools
    elif any(k in text for k in ["scrapling", "scraping", "crawler"]):
        connections.append("- **Fit**: Core component for [[Trend Scraper]] and [[Job Recruiter Agent]]")
        actions.append("- [ ] Benchmark Scrapling vs BeautifulSoup for stealth web data aggregation")
    elif any(k in text for k in ["pageindex", "vectorless", "reasoning-based rag"]):
        connections.append("- **Fit**: Alternative retrieval architecture for [[Secure Financial Advisor App]] and [[RAG]]")
        actions.append("- [ ] Evaluate hierarchical document tree search vs vector chunking")
    elif any(k in text for k in ["taxhacker", "receipt", "invoice", "financial"]):
        connections.append("- **Fit**: Directly maps to [[Secure Financial Advisor App]] and [[Financial Plan]]")
        actions.append("- [ ] Test local OCR and metadata extraction on uploaded tax receipts")
    elif any(k in text for k in ["ditto", "clone website", "react", "next.js"]):
        connections.append("- **Fit**: Accelerates frontend development for [[Body.me]] or landing pages")
        actions.append("- [ ] Test browser-capture to Vite component conversion")
    elif any(k in text for k in ["coolify", "openhands", "self-hosted", "paas"]):
        connections.append("- **Fit**: Connects to [[Simple Edge Serving]], [[Docker]], and [[Kubernetes]]")
        actions.append("- [ ] Deploy local sandbox container for hosting internal services")
    elif any(k in text for k in ["terraink", "map poster", "cartographic", "openstreetmap"]):
        connections.append("- **Fit**: Inspires map rendering techniques for [[Red Rising Space Map]]")
        actions.append("- [ ] Explore styling open-source vector coordinate data")
    elif any(k in text for k in ["frigate", "nvr", "home assistant", "security camera"]):
        connections.append("- **Fit**: Local AI security for [[Safe & Records]]")
        actions.append("- [ ] Review RTSP camera streams and edge object detection")

    # 3. Robotics, Hardware & IoT
    elif any(k in text for k in ["microduck", "duck robot", "reinforcement learning", "biped"]):
        connections.append("- **Fit**: Practical embodied AI combining [[CS 285 Intro to RL]] and robotics")
        actions.append("- [ ] Review Rust servo policy architecture for sim-to-real transfer")
    elif any(k in text for k in ["esp32", "plant monitor", "soil moisture", "dht11"]):
        connections.append("- **Fit**: Hardware automation for [[Gardening]]")
        actions.append("- [ ] Build automated ESP32 soil moisture sensor for indoor herb garden")
    elif any(k in text for k in ["rebot", "robotic arm", "devarm", "ros 2", "isaac sim"]):
        connections.append("- **Fit**: Advanced robotics simulation connecting to [[Gymnasium Environments]]")
        actions.append("- [ ] Check bill of materials for 6-axis open-source arm")
    elif any(k in text for k in ["uav", "solar airplane", "drone", "flight controller", "evtol"]):
        connections.append("- **Fit**: Aerodynamics, GNC, and embedded control")
        actions.append("- [ ] Review SpeedyBee F405 Wing flight controller and ArduPilot integration")
    elif any(k in text for k in ["art of electronics", "horowitz", "circuit", "dc circuit"]):
        connections.append("- **Fit**: Foundational electrical engineering reference in [[Knowledge Hub]]")
        actions.append("- [ ] Add key circuit blocks and op-amp schematics to study notes")

    # 4. Athletics, Soccer & Fitness
    elif any(k in text for k in ["isometric", "soccer performance", "acceleration", "stiffness"]):
        connections.append("- **Fit**: Direct athletic conditioning for [[Industry FC]] and [[2025 Workouts]]")
        actions.append("- [ ] Integrate wall-leaning acceleration and split squat isometrics into match prep")
    elif any(k in text for k in ["ball mastery", "cone drill", "japanese ball mastery", "dribbling"]):
        connections.append("- **Fit**: Technical footwork training for [[Industry FC]]")
        actions.append("- [ ] Add 6-minute Japanese ball mastery routine to pre-game warm-up")
    elif any(k in text for k in ["opengym", "workout tracker", "gym app", "self-hosted"]):
        connections.append("- **Fit**: Direct competitor and architectural benchmark for [[Body.me]]")
        actions.append("- [ ] Compare openGym data model with Body.me Streamlit CSV schema")
    elif any(k in text for k in ["running", "stride", "overstride", "ankles", "pose running"]):
        connections.append("- **Fit**: Biomechanical optimization for running sessions in [[2025 Workouts]]")
        actions.append("- [ ] Cue: lean forward from ankles to let gravity drive momentum")
    elif any(k in text for k in ["hyrox", "sub-60", "zone 2", "compromised running"]):
        connections.append("- **Fit**: High-intensity endurance programming for [[2025 Workouts]]")
        actions.append("- [ ] Test compromised running workout (intervals post-fatigue)")
    elif any(k in text for k in ["mobility", "anti-sitting", "hip flexor", "kettlebell"]):
        connections.append("- **Fit**: Daily desk recovery routine for lower back and hip health")
        actions.append("- [ ] Implement 10-movement anti-sitting routine during work breaks")
    elif any(k in text for k in ["mega mat", "pull-up bar", "costco", "home gym"]):
        connections.append("- **Fit**: Equipment upgrade for personal home gym")
        actions.append("- [ ] Pick up Costco Mega Mat rubber flooring for workout space")

    # 5. Gardening & Homesteading
    elif any(k in text for k in ["companion planting", "raised bed", "tomatoes", "peppers"]):
        connections.append("- **Fit**: Core methodology for [[Gardening]] and [[Custom Hotsauce Business]]")
        actions.append("- [ ] Plan companion beds: marigolds + basil with tomatoes; beans with peppers")
    elif any(k in text for k in ["pest control", "marigold", "copper tape", "dill"]):
        connections.append("- **Fit**: Organic pest management for vegetable and herb beds in [[Gardening]]")
        actions.append("- [ ] Apply copper tape barriers around raised bed rims")
    elif any(k in text for k in ["dragonfly", "mosquito", "water feature"]):
        connections.append("- **Fit**: Natural backyard vector control for outdoor relaxation")
        actions.append("- [ ] Set up shallow sun/shade water basin with vertical reeds")
    elif any(k in text for k in ["seed starting", "starter tray", "heat mat"]):
        connections.append("- **Fit**: Spring propagation setup for [[Gardening]]")
        actions.append("- [ ] Organize seed binder and prepare 72-cell trays with humidity dome")
    elif any(k in text for k in ["herb", "light map", "lavender", "pruning"]):
        connections.append("- **Fit**: Micro-climate optimization in [[Gardening]]")
        actions.append("- [ ] Position rosemary and thyme in full south sun; basil in east morning light")

    # 6. Culture, Travel, San Diego, Sci-Fi
    elif any(k in text for k in ["san diego", "gallagher square", "crssd", "waterfront park"]):
        connections.append("- **Fit**: Social calendar and lifestyle integration for [[San Diego Move]]")
        actions.append("- [ ] Check dates for upcoming Waterfront Park and Gallagher Square events")
    elif any(k in text for k in ["japan", "kyoto", "tokyo", "hamburg", "egg sandwich", "watch"]):
        connections.append("- **Fit**: Curated destination guide for [[Trip Planner]]")
        actions.append("- [ ] Bookmark Hikiniku to Come and Akihabara Yodobashi for Tokyo/Kyoto trip")
    elif any(k in text for k in ["red rising", "bastien lecouffe", "sci-fi"]):
        connections.append("- **Fit**: Visual world-building inspiration for [[Red Rising Space Map]]")
        actions.append("- [ ] Reference grimdark aesthetic for planetary solar system UI")
    elif any(k in text for k in ["bonobo", "lazarus", "anime", "soundtrack"]):
        connections.append("- **Fit**: Audio inspiration for [[Mixes on YouTube and SoundCloud]]")
        actions.append("- [ ] Study atmospheric electronic layering for personal music projects")
    elif any(k in text for k in ["adirondack", "corner clamp", "workbench", "woodworking"]):
        connections.append("- **Fit**: Workshop setup and DIY furniture builds")
        actions.append("- [ ] Acquire 90-degree corner clamps for true-square box glue-ups")

    if not connections:
        connections.append("- **Fit**: General reference and creative inspiration for future side projects")
    if not actions:
        actions.append("- [ ] Review tool documentation or save key workflow patterns")

    return "\n".join(connections), "\n".join(actions)

def main():
    os.makedirs(INSP_ROOT, exist_ok=True)
    for sub in set(CATEGORY_MAP.values()):
        os.makedirs(os.path.join(INSP_ROOT, sub), exist_ok=True)

    with open(CSV_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"Loaded {len(rows)} posts from CSV.")

    created = 0
    seen_titles = set()

    for row in rows:
        summary = (row.get("summary") or "").strip()
        author = (row.get("author") or "").strip()
        url = (row.get("url") or "").strip()
        likes = (row.get("likes") or "").strip()
        broad_cat = (row.get("broad_category") or "").strip()
        spec_cat = (row.get("specific_category") or "").strip()
        keywords = (row.get("keywords") or "").strip()
        links_tools = (row.get("links_tools") or "").strip()
        hashtags = (row.get("hashtags") or "").strip()
        date_val = (row.get("date") or "").strip() or "2026-09-07"

        # Refine broad category for Tech / AI & Coding
        target_folder_name = CATEGORY_MAP.get(broad_cat, "AI & Autonomous Agents")
        if broad_cat == "Tech / AI & Coding":
            s_low = (summary + " " + spec_cat + " " + keywords).lower()
            if any(k in s_low for k in ["running", "mobility", "fitness", "kettlebell", "lacrosse", "soccer", "posture", "stretch", "hyrox"]):
                target_folder_name = "Athletics & Training"
            elif any(k in s_low for k in ["gardening", "plant", "lavender", "pruning", "seed", "mosquito"]):
                target_folder_name = "Gardening & Homestead"
            elif any(k in s_low for k in ["japan", "food", "kyoto", "tokyo", "travel", "sandwich", "book", "san diego", "movie", "anime"]):
                target_folder_name = "Culture & Lifestyle"
            elif any(k in s_low for k in ["robot", "arduino", "drone", "electronics", "motor", "hardware", "esp32", "uav", "aerospace"]):
                target_folder_name = "Robotics & Hardware"
            elif any(k in s_low for k in ["adirondack", "woodworking", "workbench"]):
                target_folder_name = "Woodworking & Workshop"
            elif any(k in s_low for k in ["github", "repo", "linux", "vs code", "docker", "kubernetes", "sqlite", "scraper"]):
                target_folder_name = "Dev Tools & Repos"
            else:
                target_folder_name = "AI & Autonomous Agents"

        # Determine note title
        # Try extracting a concise recognizable name from summary or specific_cat
        first_sentence = summary.split(".")[0].strip()
        first_sentence = re.sub(r'^(a creator|a developer|a tech creator|an educational|this is|a man|a young)\s+\w+\s*', '', first_sentence, flags=re.IGNORECASE)
        
        # Check specific names
        m = re.search(r'([A-Z][a-zA-Z0-9_\-\.]{2,25}(?:\.ai|\.sh|\.io|\.com)?(?:\s+[A-Z][a-zA-Z0-9_\-]+)?)', summary)
        candidate = m.group(1) if m else spec_cat
        
        if len(candidate) < 5 or candidate.lower() in ["instead", "give this", "nature is", "a developer"]:
            candidate = spec_cat if spec_cat else "Idea Note"

        base_title = sanitize(f"{candidate} ({author})") if author else sanitize(candidate)
        if not base_title:
            base_title = sanitize(f"Inspo {created + 1}")

        # Ensure uniqueness
        title = base_title
        counter = 1
        while title.lower() in seen_titles:
            title = f"{base_title} {counter}"
            counter += 1
        seen_titles.add(title.lower())

        # Build tags
        tags = ["inspiration"]
        tag_cat = target_folder_name.lower().replace(" & ", "-").replace(" ", "-")
        tags.append(tag_cat)
        if keywords:
            for kw in keywords.split(","):
                k_clean = re.sub(r'[^a-zA-Z0-9\-]', '', kw.strip().replace(" ", "-").replace("##", "")).lower()
                if k_clean and len(k_clean) > 2 and k_clean not in tags:
                    tags.append(k_clean)
        if hashtags:
            for ht in hashtags.split(","):
                h_clean = re.sub(r'[^a-zA-Z0-9\-]', '', ht.strip().replace(" ", "-").replace("##", "")).lower()
                if h_clean and len(h_clean) > 2 and h_clean not in tags:
                    tags.append(h_clean)

        tags_yaml = "\n".join([f"  - {t}" for t in tags[:8]])

        fit_text, action_text = get_implementation_suggestions(broad_cat, spec_cat, summary, author)

        note_content = f'''---
title: "{title}"
type: inspiration
category: "{target_folder_name}"
specific_category: "{spec_cat}"
author: "@{author}"
url: "{url}"
likes: "{likes}"
created: "{date_val}"
tags:
{tags_yaml}
---

# {title}

> [!quote] Content Summary
> {summary if summary else "No summary available."}

---

## 💡 Implementation Potential & Vault Connections

### 🎯 Where It Fits in Your Vault
{fit_text}

### ⚡ Action Items & Experiments
{action_text}

---

## 📌 Context & Metadata
- **Source Creator**: `@{author}`
- **Original Link**: [View on Instagram]({url})
- **Engagement**: {likes} likes
- **Domain Category**: [[Inspiration Hub|{target_folder_name}]]
'''
        if links_tools:
            note_content += f"- **Referenced Tools / URLs**: `{links_tools}`\n"

        folder_path = os.path.join(INSP_ROOT, target_folder_name)
        file_path = os.path.join(folder_path, f"{title}.md")
        
        with open(file_path, "w", encoding="utf-8") as nf:
            nf.write(note_content)
        created += 1

    print(f"Successfully generated {created} inspiration notes across {len(set(CATEGORY_MAP.values()))} subcategories!")

if __name__ == "__main__":
    main()
