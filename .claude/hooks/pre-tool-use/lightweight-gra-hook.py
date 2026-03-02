#!/usr/bin/env python3
"""Lightweight GRA hook — BLOCK/REQUIRE_SOURCE only, zero imports beyond stdlib.

This hook runs on every Write/Edit to thesis-output/*.md files and checks for:
- BLOCK patterns: Absolute statements that indicate hallucination -> exit(2) to block
- REQUIRE_SOURCE patterns: Statistical claims needing citations -> stderr warning (pass)

Design constraints:
- stdlib only (json, re, sys) — hook environment cannot import workflow modules
- No file I/O (reads stdin JSON only)
- All exceptions -> sys.exit(0) (fail-open to avoid blocking legitimate writes)
- Only applies to thesis-output/**/*.md files

Exit codes:
- 0: Pass (no issues or non-applicable file)
- 2: Block (hallucination pattern detected)
"""
import json
import re
import sys

# ── BLOCK patterns (absolute statements → hallucination) ──
# These are inlined because hook environment cannot import workflow_constants.
BLOCK_PATTERNS = [
    # Korean
    r"모든\s*연구가?\s*일치",
    r"항상\s*그렇",
    r"절대로",
    r"완벽하게",
    r"전혀\s*없",
    r"모두\s*동의",
    # English
    r"all\s+(?:research|studies|evidence)\s+(?:agrees?|confirms?|shows?)",
    r"(?:definitively|conclusively)\s+(?:proven|established|demonstrated)",
    r"without\s+any\s+exception",
    r"(?:absolutely|unquestionably|indisputably)\s+(?:certain|true|clear)",
    r"there\s+is\s+no\s+(?:doubt|question|debate)",
    r"every\s+(?:scholar|researcher|expert)\s+agrees?",
]

# ── REQUIRE_SOURCE patterns (statistical claims needing citations) ──
REQUIRE_SOURCE_PATTERNS = [
    r"p\s*[<>=]\s*\.?\d+",
    r"(?:effect\s+size|Cohen'?s?\s*d)\s*=\s*[\d.]+",
    r"(?:r|β|beta)\s*=\s*[\d.]+",
    r"\d+%\s*(?:of\s+)?(?:the\s+)?variance",
]

try:
    data = json.load(sys.stdin)

    # Only process Write and Edit tools
    tool_name = data.get("tool_name", "")
    if tool_name not in ("Write", "Edit"):
        sys.exit(0)

    # Only apply to thesis-output markdown files
    tool_input = data.get("tool_input", {})
    file_path = tool_input.get("file_path", "")
    if "thesis-output" not in file_path or not file_path.endswith(".md"):
        sys.exit(0)

    # Get content to check
    content = tool_input.get("content", "")
    if not content:
        content = tool_input.get("new_string", "")
    if not content:
        sys.exit(0)

    # Check BLOCK patterns
    for p in BLOCK_PATTERNS:
        m = re.search(p, content, re.IGNORECASE)
        if m:
            print(json.dumps({
                "error": "GRA-BLOCK: Hallucination pattern detected",
                "match": m.group(),
                "pattern": p,
                "file": file_path,
            }), file=sys.stderr)
            sys.exit(2)

    # Check REQUIRE_SOURCE patterns (warning only, does not block)
    for p in REQUIRE_SOURCE_PATTERNS:
        if re.search(p, content, re.IGNORECASE):
            print(
                json.dumps({
                    "warning": "GRA-REQUIRE_SOURCE: Statistical claim needs citation",
                    "pattern": p,
                    "file": file_path,
                }),
                file=sys.stderr,
            )

    sys.exit(0)

except Exception:
    # Fail-open: any error = pass through
    sys.exit(0)
