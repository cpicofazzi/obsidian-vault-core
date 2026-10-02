#!/usr/bin/env python3
"""
Mobile Share-to-Vault Intake & Webhook Server for pico-vault
------------------------------------------------------------
Lightweight HTTP webhook server listening on port 8765 (configurable).
Accepts mobile share payloads from iOS Shortcuts, Android HTTP Shortcuts,
or curl requests, appends them directly into 00_Inbox/Quick Capture.md,
and immediately triggers vault_ingest.py to triage and file them.

Zero external dependencies required (built entirely with Python standard library).

Usage:
    python scripts/mobile_intake.py                      # Listen on 0.0.0.0:8765
    python scripts/mobile_intake.py --port 8765          # Custom port
    python scripts/mobile_intake.py --token MySecret     # Require Bearer token
    python scripts/mobile_intake.py --no-ingest          # Only append to inbox, don't auto-ingest
    python scripts/mobile_intake.py --test               # Send a loopback test request
"""

import os
import sys
import re
import json
import argparse
import datetime
import threading
import subprocess
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

# Configure Windows console encoding for Unicode/Emojis
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
VAULT_ROOT = os.path.dirname(SCRIPT_DIR)
INBOX_FILE = os.path.join(VAULT_ROOT, "00_Inbox", "Quick Capture.md")
INGEST_SCRIPT = os.path.join(SCRIPT_DIR, "vault_ingest.py")

file_lock = threading.Lock()

def log(msg, level="INFO"):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    prefix = {
        "INFO": "⚡",
        "AUTH": "🔒",
        "INTAKE": "📥",
        "INGEST": "🚀",
        "WARN": "⚠️",
        "ERROR": "❌"
    }.get(level, "ℹ️")
    print(f"[{now}] {prefix} {msg}", flush=True)

def format_entry(payload: dict) -> tuple[str, str]:
    """
    Translates incoming JSON payload into formatted markdown bullet and category.
    Supported types: inspo | task | idea | research
    """
    raw_type = str(payload.get("type") or "").strip().lower()
    url = str(payload.get("url") or "").strip()
    text = str(
        payload.get("text")
        or payload.get("content")
        or payload.get("body")
        or payload.get("title")
        or payload.get("note")
        or ""
    ).strip()
    priority = str(payload.get("priority") or "").strip()
    due = str(payload.get("due") or payload.get("due_date") or "").strip()

    # Smart fallback classification if type wasn't explicitly provided
    if not raw_type:
        text_lower = text.lower()
        if any(text_lower.startswith(p) for p in ["inspo:", "media:", "link:"]) or "#inspo" in text_lower:
            raw_type = "inspo"
        elif text.startswith("- [ ]") or any(text_lower.startswith(p) for p in ["task:", "todo:"]):
            raw_type = "task"
        elif any(text_lower.startswith(p) for p in ["idea:", "app:", "startup:"]):
            raw_type = "idea"
        elif any(text_lower.startswith(p) for p in ["research:", "topic:", "paper:"]):
            raw_type = "research"
        elif url:
            raw_type = "inspo"
        else:
            raw_type = "note"

    if raw_type in ["inspo", "inspiration", "media"]:
        clean_text = re.sub(r'^(inspo:\s*|media:\s*|link:\s*)', '', text, flags=re.IGNORECASE).strip()
        if clean_text and url:
            if url in clean_text:
                line = f"- Inspo: {clean_text}"
            else:
                line = f"- Inspo: {clean_text} {url}"
        elif url:
            line = f"- Inspo: {url}"
        else:
            line = f"- Inspo: {clean_text}"
        return line, "inspo"

    elif raw_type in ["task", "todo"]:
        clean_text = re.sub(r'^(- \[[ x]\]\s*|task:\s*|todo:\s*)', '', text, flags=re.IGNORECASE).strip()
        if priority and not any(p in clean_text.lower() for p in ["!high", "p1", "!low", "p3", "urgent"]):
            clean_text = f"{clean_text} {priority}"
        if due and "due:" not in clean_text.lower():
            clean_text = f"{clean_text} due:{due}"
        
        line = f"- [ ] {clean_text}"
        if url and url not in line:
            line = f"{line} ({url})"
        return line, "task"

    elif raw_type in ["idea", "concept"]:
        clean_text = re.sub(r'^idea:\s*', '', text, flags=re.IGNORECASE).strip()
        line = f"- Idea: {clean_text}"
        if url and url not in line:
            line = f"{line} {url}"
        return line, "idea"

    elif raw_type in ["research", "topic", "paper"]:
        clean_text = re.sub(r'^(research:\s*|topic:\s*|paper:\s*)', '', text, flags=re.IGNORECASE).strip()
        line = f"- Research: {clean_text}"
        if url and url not in line:
            line = f"{line} {url}"
        return line, "research"

    else:
        # Generic Note fallback
        clean_text = re.sub(r'^- \s*', '', text).strip()
        if clean_text and url:
            line = f"- {clean_text} {url}"
        elif url:
            line = f"- Inspo: {url}"
        else:
            line = f"- {clean_text}"
        return line, "note"

def append_to_inbox(formatted_line: str, category: str) -> bool:
    """Safely appends the formatted bullet into 00_Inbox/Quick Capture.md."""
    if not os.path.exists(INBOX_FILE):
        log(f"Inbox file not found at {INBOX_FILE}", level="ERROR")
        return False

    with file_lock:
        try:
            with open(INBOX_FILE, "r", encoding="utf-8") as f:
                lines = f.readlines()

            inserted = False
            target_header = "### 🎨 Inspo Dropzone" if category == "inspo" else "### ⚡ Quick Tasks & Ideas Dropzone"
            
            # 1. Try to place under matching subheader
            for i, line_content in enumerate(lines):
                if line_content.strip().startswith(target_header):
                    lines.insert(i + 1, f"{formatted_line}\n")
                    inserted = True
                    break

            # 2. Fallback: Place right below dropzone marker
            if not inserted:
                dropzone_marker = "<!-- New raw inputs land below this line -->"
                for i, line_content in enumerate(lines):
                    if dropzone_marker in line_content:
                        lines.insert(i + 1, f"\n{formatted_line}\n")
                        inserted = True
                        break

            # 3. Last resort: append to bottom
            if not inserted:
                lines.append(f"\n{formatted_line}\n")

            with open(INBOX_FILE, "w", encoding="utf-8") as f:
                f.writelines(lines)

            log(f"Saved into Quick Capture: {formatted_line}", level="INTAKE")
            return True

        except Exception as e:
            log(f"Failed to write to Quick Capture.md: {e}", level="ERROR")
            return False

def run_vault_ingest() -> tuple[bool, str]:
    """Triggers vault_ingest.py in a clean subprocess and returns output."""
    try:
        cmd = [sys.executable, INGEST_SCRIPT]
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        combined_output = (proc.stdout or "").strip()
        if proc.stderr:
            combined_output += ("\n" + proc.stderr.strip() if combined_output else proc.stderr.strip())
        
        success = (proc.returncode == 0)
        return success, combined_output
    except Exception as e:
        return False, str(e)

class MobileIntakeHandler(BaseHTTPRequestHandler):
    server_version = "PicoVaultIntake/1.0"

    def _send_json_response(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        # Enable CORS for browser requests
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Vault-Token")
        self.end_headers()
        self.wfile.write(body)

    def _check_auth(self) -> bool:
        auth_token = getattr(self.server, "auth_token", None)
        if not auth_token:
            return True  # Open mode (no auth required)

        # 1. Check Authorization: Bearer <token>
        auth_header = self.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header[7:].strip()
            if token == auth_token:
                return True

        # 2. Check X-Vault-Token header
        custom_header = self.headers.get("X-Vault-Token", "").strip()
        if custom_header == auth_token:
            return True

        # 3. Check query param: ?token=<token>
        parsed = urllib.parse.urlparse(self.path)
        query_params = urllib.parse.parse_qs(parsed.query)
        if "token" in query_params and query_params["token"][0] == auth_token:
            return True

        return False

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Vault-Token")
        self.end_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path.rstrip("/")

        if path in ["", "/health", "/status", "/ping"]:
            auth_required = bool(getattr(self.server, "auth_token", None))
            self._send_json_response(200, {
                "status": "online",
                "service": "pico-vault mobile intake webhook",
                "auth_required": auth_required,
                "auto_ingest": getattr(self.server, "auto_ingest", True),
                "timestamp": datetime.datetime.now().isoformat()
            })
        else:
            self._send_json_response(404, {
                "status": "error",
                "error": "Not Found",
                "endpoints": ["GET /health", "POST /intake", "POST /"]
            })

    def do_POST(self):
        # 1. Authenticate
        if not self._check_auth():
            log(f"Unauthorized intake attempt from {self.client_address[0]}", level="AUTH")
            self._send_json_response(401, {
                "status": "error",
                "error": "Unauthorized",
                "message": "Valid Bearer token required. Provide header 'Authorization: Bearer <token>'."
            })
            return

        # 2. Read Body
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            raw_body = self.rfile.read(content_length).decode("utf-8", errors="replace")
        except Exception as e:
            self._send_json_response(400, {"status": "error", "error": f"Failed to read body: {e}"})
            return

        # 3. Parse Body (JSON or URL-encoded form or plain text)
        content_type = self.headers.get("Content-Type", "")
        payload = {}
        if "application/json" in content_type or raw_body.strip().startswith("{"):
            try:
                payload = json.loads(raw_body)
            except Exception as e:
                self._send_json_response(400, {"status": "error", "error": f"Invalid JSON: {e}"})
                return
        elif "application/x-www-form-urlencoded" in content_type:
            qs = urllib.parse.parse_qs(raw_body)
            payload = {k: v[0] for k, v in qs.items()}
        else:
            # Plain text fallback
            payload = {"text": raw_body.strip()}

        url = payload.get("url", "").strip()
        text = payload.get("text", "").strip()
        if not url and not text:
            self._send_json_response(400, {
                "status": "error",
                "error": "Empty payload. Expected at least 'url' or 'text' key."
            })
            return

        # 4. Format & Save to Quick Capture.md
        formatted_line, category = format_entry(payload)
        saved = append_to_inbox(formatted_line, category)
        if not saved:
            self._send_json_response(500, {
                "status": "error",
                "error": "Failed to append entry to Quick Capture.md"
            })
            return

        # 5. Optional Auto-Ingest
        auto_ingest = getattr(self.server, "auto_ingest", True)
        ingest_output = ""
        ingest_success = False

        if auto_ingest:
            log("Triggering vault_ingest.py to file entry immediately...", level="INGEST")
            ingest_success, ingest_output = run_vault_ingest()
            if ingest_success:
                log(f"Ingest completed successfully: {ingest_output.splitlines()[-1] if ingest_output else 'OK'}", level="INGEST")
            else:
                log(f"Ingest warning/error: {ingest_output}", level="WARN")

        self._send_json_response(200, {
            "status": "success",
            "message": "Captured into vault successfully",
            "type": category,
            "entry": formatted_line,
            "ingested": auto_ingest,
            "ingest_success": ingest_success if auto_ingest else None,
            "ingest_summary": ingest_output.splitlines()[-1] if ingest_output else None
        })

    def log_message(self, format, *args):
        # Override default BaseHTTPRequestHandler noisy log to keep terminal clean
        pass

def run_server(host="0.0.0.0", port=8765, token=None, auto_ingest=True):
    server = ThreadingHTTPServer((host, port), MobileIntakeHandler)
    server.auth_token = token
    server.auto_ingest = auto_ingest

    banner = f"""
========================================================================
⚡ Pico Vault - Mobile Share-to-Vault Webhook Server
========================================================================
📡 Listening on:      http://{host}:{port}
📥 Endpoints:         POST http://{host}:{port}/intake
                     GET  http://{host}:{port}/health
🔒 Auth Token:        {"[ACTIVE] Bearer token required" if token else "[OPEN] No authentication set"}
🚀 Auto-Ingest:       {"Enabled (triggers vault_ingest.py)" if auto_ingest else "Disabled (saves to dropzone only)"}
📂 Vault Inbox:       {INBOX_FILE}
========================================================================
Ready to receive shares from iOS Shortcuts, Android, and Webhooks!
Press Ctrl+C to stop.
"""
    print(banner, flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down mobile intake server gracefully...")
        server.server_close()
        print("Done.")

def send_test_loopback(port=8765, token=None):
    """Sends a loopback test request to verify the server is operating cleanly."""
    import urllib.request
    
    test_url = f"http://127.0.0.1:{port}/intake"
    test_payload = {
        "type": "inspo",
        "url": "https://github.com/fastai/fastcore",
        "text": "Fastcore utility library for supercharged Python programming"
    }

    req = urllib.request.Request(
        test_url,
        data=json.dumps(test_payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **({"Authorization": f"Bearer {token}"} if token else {})
        },
        method="POST"
    )

    print(f"Testing loopback POST to {test_url}...")
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print("Response:", json.dumps(data, indent=2))
            if data.get("status") == "success":
                print("✅ Test loopback successful!")
                return True
            else:
                print("❌ Unexpected test response:", data)
                return False
    except Exception as e:
        print(f"❌ Test loopback failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Pico Vault Mobile Share Intake Server")
    parser.add_argument("-H", "--host", default="0.0.0.0", help="Host interface to bind (default: 0.0.0.0)")
    parser.add_argument("-p", "--port", type=int, default=int(os.environ.get("VAULT_PORT", os.environ.get("PORT", 8765))), help="Port to listen on (default: 8765)")
    parser.add_argument("-t", "--token", default=os.environ.get("VAULT_AUTH_TOKEN", os.environ.get("MOBILE_INTAKE_TOKEN", None)), help="Optional Bearer token for authentication")
    parser.add_argument("--no-ingest", action="store_true", help="Do not trigger vault_ingest.py automatically after capture")
    parser.add_argument("--test", action="store_true", help="Send a test loopback request to an active server")

    args = parser.parse_args()

    if args.test:
        success = send_test_loopback(port=args.port, token=args.token)
        sys.exit(0 if success else 1)

    run_server(
        host=args.host,
        port=args.port,
        token=args.token,
        auto_ingest=not args.no_ingest
    )

if __name__ == "__main__":
    main()
