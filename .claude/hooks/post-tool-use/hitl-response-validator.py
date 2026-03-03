#!/usr/bin/env python3
"""PostToolUse hook: Validate AskUserQuestion responses.

Detects empty/ambiguous user selections and outputs a MANDATORY STOP directive.
Prevents Claude from hallucinating user choices and auto-advancing workflows.

Design constraints:
- stdlib only (json, re, sys)
- Reads tool result from stdin JSON
- Outputs to stderr (visible to Claude as hook feedback)
- PostToolUse cannot block with exit(2), but stderr messages are treated
  as user instructions per CLAUDE.md rules

Exit codes:
- 0: Always (PostToolUse cannot block)
"""
import json
import re
import sys


# Known valid selection patterns - if the answer contains one of these,
# it's likely a real user selection
VALID_ANSWER_INDICATORS = [
    # Option labels from quick-start.md
    r"Quick Simulation",
    r"Full Simulation",
    r"Quick.*Full",
    r"Smart Mode",
    # Category selections
    r"새로운 연구",
    r"자료 기반",
    r"학습모드",
    # Input method selections
    r"연구 주제",
    r"연구질문",
    r"자유 형식",
    # Generic indicators that a real selection was made
    r"선택|selected|chose|picked",
    # Any option label (quoted text)
    r'"[^"]{3,}"',
    # Research types
    r"양적연구|질적연구|혼합연구",
    r"quantitative|qualitative|mixed",
    # Disciplines
    r"경영학|사회과학|인문학|자연과학|의학|교육학",
    # Citation styles
    r"APA|Chicago|MLA|Harvard",
    # File-related
    r"파일 경로|직접 첨부|업로드",
    # Approval/rejection
    r"승인|거부|수정",
    # Learning tracks
    r"Track \d",
    # Any substantive text after "answered"
    r"answered your questions:\s*\S{3,}",
]

# Patterns that indicate EMPTY or NO response
EMPTY_RESPONSE_PATTERNS = [
    # "User has answered your questions: ." (empty answer)
    r"answered your questions:\s*\.\s*You can",
    # "User has answered your questions:  You can" (whitespace only)
    r"answered your questions:\s+You can",
    # "User has answered your questions: . " (period only)
    r"answered your questions:\s*\.\s*$",
]


def validate_response(tool_output: str) -> tuple[bool, str]:
    """Validate AskUserQuestion response.

    Returns:
        (is_valid, reason)
    """
    if not tool_output or not isinstance(tool_output, str):
        return False, "Tool output is empty or not a string"

    # Check for explicit empty patterns
    for pattern in EMPTY_RESPONSE_PATTERNS:
        if re.search(pattern, tool_output, re.IGNORECASE):
            return False, f"Empty response detected (pattern: {pattern})"

    # Check if any valid selection indicator is present
    for pattern in VALID_ANSWER_INDICATORS:
        if re.search(pattern, tool_output, re.IGNORECASE):
            return True, "Valid selection detected"

    # If "answered" is in the output but no valid indicator found, suspicious
    if "answered your questions" in tool_output.lower():
        # Extract the answer portion
        parts = tool_output.split("answered your questions:")
        if len(parts) > 1:
            answer_part = parts[1].split("You can now")[0].strip()
            # Strip punctuation
            answer_clean = answer_part.strip(" .\t\n")
            if len(answer_clean) < 3:
                return False, f"Answer too short: '{answer_part}'"

    return True, "No issues detected"


try:
    data = json.load(sys.stdin)

    tool_name = data.get("tool_name", "")
    if tool_name != "AskUserQuestion":
        sys.exit(0)

    # Get the tool output/result
    tool_output = data.get("tool_output", "")
    if not tool_output:
        tool_output = str(data.get("tool_result", ""))

    is_valid, reason = validate_response(tool_output)

    if not is_valid:
        # Output MANDATORY STOP directive to stderr
        warning = {
            "HITL_GUARD": "MANDATORY_STOP",
            "severity": "CRITICAL",
            "message": (
                "AskUserQuestion returned an EMPTY or AMBIGUOUS response. "
                "The user's selection was NOT captured. "
                "You MUST NOT proceed to the next step. "
                "You MUST re-ask the question or explicitly confirm "
                "what the user selected before continuing."
            ),
            "reason": reason,
            "raw_output_preview": tool_output[:300] if tool_output else "(empty)",
            "required_action": [
                "1. STOP all workflow progression",
                "2. Inform the user that their selection was not captured",
                "3. Re-display the question using AskUserQuestion",
                "4. Only proceed after receiving a valid, non-empty selection",
            ],
        }
        print(json.dumps(warning, ensure_ascii=False), file=sys.stderr)

    sys.exit(0)

except Exception:
    # Fail-open: any error = pass through
    sys.exit(0)
