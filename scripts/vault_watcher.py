#!/usr/bin/env python3
"""
Vault Watcher Daemon for pico-vault
-----------------------------------
Monitors 00_Inbox/Quick Capture.md and 00_Inbox/ for new notes, tasks, ideas, 
and inspiration media. When changes are detected and writing settles,
it automatically triggers vault_ingest.py to triage, categorize, and link entries.

Zero external dependencies required (uses robust mtime polling with debouncing).

Usage:
    python scripts/vault_watcher.py             # Runs in foreground/background loop
    python scripts/vault_watcher.py --once      # Process once if changed, then exit
    python scripts/vault_watcher.py --interval 2# Check every 2 seconds (default 1.5s)
"""

import os
import sys
import time
import datetime
import argparse
import io

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Ensure vault scripts can be imported
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)

import vault_ingest

VAULT_ROOT = os.path.dirname(SCRIPT_DIR)
INBOX_FILE = os.path.join(VAULT_ROOT, "00_Inbox", "Quick Capture.md")
INBOX_DIR = os.path.join(VAULT_ROOT, "00_Inbox")

def log(msg):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

def has_unprocessed_entries():
    """Checks whether Quick Capture.md contains non-empty lines in the dropzone."""
    if not os.path.exists(INBOX_FILE):
        return False
    try:
        with open(INBOX_FILE, "r", encoding="utf-8") as f:
            lines = f.readlines()
        dropzone_marker = "<!-- New raw inputs land below this line -->"
        marker_idx = -1
        for i, l in enumerate(lines):
            if dropzone_marker in l:
                marker_idx = i
                break
        if marker_idx == -1:
            return False
        
        in_footer = False
        for l in lines[marker_idx + 1:]:
            if l.strip().startswith("---") or "Ingestion Instructions" in l:
                in_footer = True
            if not in_footer:
                clean = l.strip()
                if clean and not clean.startswith("###"):
                    return True
        return False
    except Exception as e:
        log(f"Error reading inbox file: {e}")
        return False

def check_unfiled_inbox_files():
    """Checks if any new .md files exist in 00_Inbox besides Quick Capture.md."""
    if not os.path.exists(INBOX_DIR):
        return []
    unfiled = []
    for f in os.listdir(INBOX_DIR):
        if f.endswith(".md") and f != "Quick Capture.md":
            unfiled.append(os.path.join(INBOX_DIR, f))
    return unfiled

def process_unfiled_files(unfiled_files, vault_index):
    """Processes standalone markdown files dropped directly into 00_Inbox/."""
    for file_path in unfiled_files:
        try:
            filename = os.path.basename(file_path)
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            
            # Check frontmatter or content for type hints
            first_lines = content[:500].lower()
            if "type: idea" in first_lines or "idea:" in first_lines:
                entry = {
                    "type": "idea",
                    "title": filename[:-3],
                    "domain": "AI/Tech",
                    "folder_sub": "AI & Tech",
                    "raw": content[:200],
                    "created": datetime.date.today().strftime("%Y-%m-%d")
                }
                dest = vault_ingest.create_idea_note(entry, vault_index)
                os.remove(file_path)
                log(f"Filed unfiled idea note: {filename} -> {dest}")
            elif "type: task" in first_lines or "task:" in first_lines or "- [ ]" in first_lines:
                entry = {
                    "type": "task",
                    "title": filename[:-3],
                    "priority": "🟡 Medium",
                    "due_date": (datetime.date.today() + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
                    "raw": content[:200],
                    "created": datetime.date.today().strftime("%Y-%m-%d")
                }
                dest = vault_ingest.create_task_note(entry, vault_index)
                os.remove(file_path)
                log(f"Filed unfiled task note: {filename} -> {dest}")
            elif "type: inspiration" in first_lines or "inspo:" in first_lines:
                entry = {
                    "type": "inspiration",
                    "title": filename[:-3],
                    "category": "AI & Autonomous Agents",
                    "url": "",
                    "raw": content[:200],
                    "created": datetime.date.today().strftime("%Y-%m-%d")
                }
                dest = vault_ingest.create_inspiration_note(entry, vault_index)
                os.remove(file_path)
                log(f"Filed unfiled inspo note: {filename} -> {dest}")
            else:
                # Move to 20_Areas/Personal/
                target = os.path.join(VAULT_ROOT, "20_Areas", "Personal", filename)
                os.rename(file_path, target)
                log(f"Filed unfiled general note: {filename} -> 20_Areas/Personal/")
        except Exception as e:
            log(f"Failed to process unfiled note {file_path}: {e}")

def run_watcher(poll_interval=1.5, debounce_delay=2.0, run_once=False):
    log("==================================================")
    log("🤖 Autonomous Vault Watcher Daemon Started")
    log(f"   Monitoring: {INBOX_FILE}")
    log(f"   Poll Interval: {poll_interval}s | Debounce: {debounce_delay}s")
    log("==================================================")

    last_mtime = 0
    last_change_time = 0
    pending_ingest = False

    if os.path.exists(INBOX_FILE):
        last_mtime = os.path.getmtime(INBOX_FILE)
        # Check on startup if items are already waiting
        if has_unprocessed_entries():
            log("⚡ Unprocessed items detected in Quick Capture on startup. Ingesting...")
            vault_ingest.process_inbox()

    while True:
        try:
            current_time = time.time()

            # 1. Check for standalone unfiled notes in 00_Inbox/
            unfiled = check_unfiled_inbox_files()
            if unfiled:
                log(f"📂 Found {len(unfiled)} unfiled notes in 00_Inbox. Triaging...")
                v_index = vault_ingest.get_vault_index()
                process_unfiled_files(unfiled, v_index)

            # 2. Check Quick Capture.md modification
            if os.path.exists(INBOX_FILE):
                mtime = os.path.getmtime(INBOX_FILE)
                if mtime != last_mtime:
                    last_mtime = mtime
                    last_change_time = current_time
                    pending_ingest = True
                    log("📝 Quick Capture modified. Waiting for user to finish writing...")

            # 3. Debounce trigger
            if pending_ingest and (current_time - last_change_time >= debounce_delay):
                if has_unprocessed_entries():
                    log("⚡ Writing settled. Processing new dropzone entries...")
                    vault_ingest.process_inbox()
                    last_mtime = os.path.getmtime(INBOX_FILE)
                else:
                    log("ℹ️ No new dropzone entries to process.")
                pending_ingest = False

            if run_once:
                break

            time.sleep(poll_interval)
        except KeyboardInterrupt:
            log("🛑 Vault Watcher stopped by user.")
            break
        except Exception as e:
            log(f"⚠️ Unexpected error in watcher loop: {e}")
            time.sleep(poll_interval)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Vault Watcher Daemon")
    parser.add_argument("--interval", type=float, default=1.5, help="Polling interval in seconds")
    parser.add_argument("--debounce", type=float, default=2.0, help="Debounce delay in seconds")
    parser.add_argument("--once", action="store_true", help="Process once and exit")
    args = parser.parse_args()

    run_watcher(poll_interval=args.interval, debounce_delay=args.debounce, run_once=args.once)
