# app/services/bug_sync.py
"""
Bug Sync Service
----------------
Called on every login AND on every dashboard refresh (via /api/bugs/sync).

What it does:
  1. Reads mock_bugs.json (mock substitute for the live Bugzilla API)
  2. For each bug in the file:
       - If the bug does NOT exist in the DB → insert it with all related data
       - If the bug ALREADY exists → update its fields (upsert)
  3. Deletes bugs from the DB that no longer appear in mock_bugs.json
     (keeps the DB in sync if bugs are removed from the source)

In production, replace the _load_bugs_from_mock() call with a real
Bugzilla REST API call.
"""

import json
import os
import re
import requests
from datetime import datetime

from app.extensions import db
from app.models.bug import Bug
from app.models.bug_comments import BugComment
from app.models.bug_tests import BugTest
from app.models.ml_analysis import MLAnalysis
from app.models.user import User
from app.config import Config


# Path to mock_bugs.json — sits at the project root
MOCK_BUGS_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "mock_bugs.json"
)

# Address of mock_api_server.py for ChatHPE ML analysis
CHATHPE_URL = "http://127.0.0.1:8080"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _normalize_spaces(value):
    return re.sub(r"\s+", " ", value).strip()


def _parse_execution_datetime(raw):
    if not raw:
        return None
    clean = raw.strip()
    if clean.endswith(" UTC"):
        clean = clean[:-4]
    for fmt in ("%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue
    return None


def _parse_iso_datetime(raw):
    if not raw:
        return None
    clean = raw.strip()
    if clean.endswith("Z"):
        clean = clean[:-1]
    for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(clean, fmt)
        except ValueError:
            continue
    return None


def _parse_int(raw):
    if raw is None:
        return None
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return None


def _parse_test_metadata(comment_text):
    """Parses the tab-separated metadata block from comment[0].text."""
    parsed = {}
    if not comment_text:
        return parsed
    for line in comment_text.splitlines():
        clean_line = line.strip()
        if not clean_line or ":" not in clean_line:
            continue
        key, value = clean_line.split(":", 1)
        parsed[_normalize_spaces(key)] = value.strip()
    return parsed


def _map_bug_status(source_status):
    s = (source_status or "").strip().upper()
    if s == "REPRODUCE":
        return "running"
    if s == "OPEN":
        return "pending"
    if s in ("CLOSED", "VERIFIED"):
        return "completed"
    return "pending"


def _map_bug_type(source_status):
    s = (source_status or "").strip().upper()
    return "repro" if s == "REPRODUCE" else "test"


def _extract_section(text, keyword):
    """Pull the paragraph after a keyword heading from a markdown blob."""
    lines      = text.splitlines()
    collecting = False
    result     = []
    for line in lines:
        if keyword.lower() in line.lower():
            collecting = True
            continue
        if collecting:
            if line.strip().startswith("**") and result:
                break
            if line.strip():
                result.append(line.strip())
    return " ".join(result).strip() or text[:300]


def _generate_ml_analysis(bug_code, comments):
    """
    Calls the mock ChatHPE server to generate ML analysis for a bug.
    Returns a dict or None if the server is not available.
    """
    texts = [c["text"] for c in comments if isinstance(c, dict) and c.get("text")]
    if not texts:
        return None

    prompt = (
        f"Bug {bug_code} - Engineer Comments:\n\n"
        + "\n\n---\n\n".join(texts)
        + "\n\nExtract:\n"
          "1. **Repro Actions**: Steps to reproduce\n"
          "2. **Config Changes**: Config changes needed\n"
          "3. **Repro Readiness**: Yes / No / Partial\n"
          "4. **Summary**: One paragraph summary\n"
    )

    try:
        resp = requests.post(
            f"{CHATHPE_URL}/v2.8/call/chatlite",
            json={"user_query": prompt},
            timeout=8,
        )
        resp.raise_for_status()
        message = resp.json().get("message", "")
        return {
            "repro_actions":   _extract_section(message, "Repro Actions"),
            "config_changes":  _extract_section(message, "Config Changes"),
            "repro_readiness": _extract_section(message, "Repro Readiness"),
            "summary":         message,
        }
    except Exception:
        # Silent fail — ML analysis is non-critical
        return None


# ── Data source ───────────────────────────────────────────────────────────────

def _load_bugs_from_mock():
    """
    Reads mock_bugs.json from disk.
    In production, replace this with a real Bugzilla REST API call.
    """
    try:
        with open(MOCK_BUGS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"[BugSync] mock_bugs.json not found at {MOCK_BUGS_FILE}")
        return []
    except json.JSONDecodeError as e:
        print(f"[BugSync] Invalid mock_bugs.json: {e}")
        return []


# ── Main sync function ────────────────────────────────────────────────────────

def fetch_and_sync_bugs():
    """
    Upserts all bugs from mock_bugs.json into the main database.

    - New bugs are inserted with their tests, comments, and ML analysis.
    - Existing bugs have their status and priority updated.
    - Bugs no longer in the source file are deleted from the DB.

    Called automatically on login (auth.py) and on dashboard refresh
    (bugDashboard.py /api/bugs/sync route).
    """
    bug_rows = _load_bugs_from_mock()
    if not bug_rows:
        print("[BugSync] No bugs to sync.")
        return

    source_codes = {str(row.get("Bug Id", "")).strip() for row in bug_rows}
    source_codes.discard("")

    inserted = 0
    updated  = 0
    deleted  = 0

    try:
        # ── Delete bugs that no longer exist in the source ────────────────
        existing_bugs = Bug.query.all()
        for b in existing_bugs:
            if b.bug_code not in source_codes:
                db.session.delete(b)
                deleted += 1

        db.session.flush()

        # ── Upsert each bug from source ───────────────────────────────────
        for row in bug_rows:
            bug_code = str(row.get("Bug Id", "")).strip()
            if not bug_code:
                continue

            source_status  = row.get("Status")
            assignee_email = (row.get("Assignee") or "").strip()

            # Look up engineer by email
            engineer = None
            if assignee_email:
                engineer = User.query.filter(
                    db.func.lower(User.email) == assignee_email.lower()
                ).first()

            existing = Bug.query.filter_by(bug_code=bug_code).first()

            if existing:
                # ── Update existing bug ────────────────────────────────────
                existing.priority    = (row.get("Priority") or "P2").strip()
                existing.status      = _map_bug_status(source_status)
                existing.bug_type    = _map_bug_type(source_status)
                existing.engineer_id = engineer.id if engineer else existing.engineer_id
                existing.resource_group = (row.get("Build") or "").strip() or existing.resource_group
                existing.summary     = (row.get("Component") or "").strip() or existing.summary
                updated += 1

            else:
                # ── Insert new bug ─────────────────────────────────────────
                new_bug = Bug(
                    bug_code=bug_code,
                    priority=(row.get("Priority") or "P2").strip(),
                    status=_map_bug_status(source_status),
                    engineer_id=engineer.id if engineer else None,
                    bug_type=_map_bug_type(source_status),
                    resource_group=(row.get("Build") or "").strip() or None,
                    summary=(row.get("Component") or "").strip() or None,
                )
                db.session.add(new_bug)
                db.session.flush()  # get new_bug.id

                # Parse test metadata from comment[0]
                comments         = row.get("Comments") or []
                first_comment    = comments[0] if comments and isinstance(comments[0], dict) else {}
                metadata         = _parse_test_metadata(first_comment.get("text", ""))

                raw_test_name = metadata.get("Test Name")
                test_name     = None
                if raw_test_name:
                    test_name = raw_test_name.replace("\\", "/").rsplit("/", 1)[-1]

                test_ring_name = metadata.get("Test Ring Name")

                # Insert Bug_Tests row
                db.session.add(BugTest(
                    bug_id=new_bug.id,
                    test_name=test_name,
                    test_plan_name=metadata.get("Test Plan Name"),
                    test_ring_name=test_ring_name,
                    execution_start=_parse_execution_datetime(metadata.get("Execution Start")),
                    execution_end=_parse_execution_datetime(metadata.get("Execution End")),
                    controller_types=metadata.get("Controller Types"),
                    number_of_nodes=_parse_int(metadata.get("Number Of Nodes")),
                    failure_type=metadata.get("Failure Type"),
                    build_version=metadata.get("Build Version"),
                    nfs_path=metadata.get("NFS Path"),
                    odin_link=metadata.get("Odin Link"),
                    signature=metadata.get("Signature"),
                    station_name=test_ring_name,
                ))

                # Insert Bug_Comments rows
                for comment in comments:
                    if not isinstance(comment, dict):
                        continue
                    db.session.add(BugComment(
                        bug_id=new_bug.id,
                        comment_bugzilla_id=_parse_int(comment.get("id")),
                        creator=comment.get("creator"),
                        creation_time=_parse_iso_datetime(comment.get("creation_time")),
                        text=comment.get("text"),
                    ))

                # Generate and insert ML_Analysis
                ml_data = _generate_ml_analysis(bug_code, comments)
                db.session.add(MLAnalysis(
                    bug_id=new_bug.id,
                    repro_actions=ml_data["repro_actions"]   if ml_data else None,
                    config_changes=ml_data["config_changes"]  if ml_data else None,
                    repro_readiness=ml_data["repro_readiness"] if ml_data else None,
                    summary=ml_data["summary"]          if ml_data else None,
                ))

                inserted += 1

        db.session.commit()
        print(f"[BugSync] Done — inserted: {inserted}, updated: {updated}, deleted: {deleted}")

    except Exception as e:
        db.session.rollback()
        print(f"[BugSync] Sync failed: {e}")
        raise