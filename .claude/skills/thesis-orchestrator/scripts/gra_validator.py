#!/usr/bin/env python3
"""GRA (Grounded Research Architecture) validation module.

This module implements the GRA quality assurance system including:
- Hallucination Firewall
- GroundedClaim schema validation
- SRCS (Source-Reliability-Confidence-Scope) scoring
"""

import json
import re
import sys
from pathlib import Path
from typing import Any

# Valid claim types
VALID_CLAIM_TYPES = {
    "FACTUAL",
    "EMPIRICAL",
    "THEORETICAL",
    "METHODOLOGICAL",
    "INTERPRETIVE",
    "SPECULATIVE",
}

# Valid source types
VALID_SOURCE_TYPES = {"PRIMARY", "SECONDARY", "TERTIARY"}

# Import from SOT-A (workflow_constants)
from workflow_constants import (
    GRA_CONFIDENCE_THRESHOLDS as CONFIDENCE_THRESHOLDS,
    HALLUCINATION_PATTERNS,
)

# Claim types that require PRIMARY source
REQUIRES_PRIMARY = {"EMPIRICAL", "THEORETICAL"}

# SRCS scoring is delegated to srcs_evaluator (single source of truth)
from srcs_evaluator import (
    calculate_citation_score as _srcs_calculate_citation_score,
    calculate_grounding_score as _srcs_calculate_grounding_score,
    calculate_uncertainty_score as _srcs_calculate_uncertainty_score,
    calculate_verifiability_score as _srcs_calculate_verifiability_score,
    calculate_weighted_srcs as _srcs_calculate_weighted,
    SRCS_WEIGHTS,
)


def detect_hallucination_patterns(text: str) -> dict[str, Any]:
    """Detect hallucination patterns in text.

    Args:
        text: Text to analyze

    Returns:
        Dictionary with detection results
    """
    matches = []
    highest_level = "PASS"
    level_priority = {"BLOCK": 4, "REQUIRE_SOURCE": 3, "SOFTEN": 2, "VERIFY": 1, "PASS": 0}

    for level, patterns in HALLUCINATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches.append({
                    "level": level,
                    "pattern": pattern,
                    "match": re.search(pattern, text, re.IGNORECASE).group(),
                })
                if level_priority[level] > level_priority[highest_level]:
                    highest_level = level

    return {
        "level": highest_level,
        "matches": matches,
    }


def get_confidence_threshold(claim_type: str) -> int:
    """Get the confidence threshold for a claim type.

    Args:
        claim_type: Type of claim

    Returns:
        Minimum confidence threshold
    """
    return CONFIDENCE_THRESHOLDS.get(claim_type, 70)


def requires_primary_source(claim_type: str) -> bool:
    """Check if a claim type requires PRIMARY source.

    Args:
        claim_type: Type of claim

    Returns:
        True if PRIMARY source is required
    """
    return claim_type in REQUIRES_PRIMARY


def validate_claim(claim: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a GroundedClaim.

    Args:
        claim: Claim dictionary to validate

    Returns:
        Tuple of (is_valid, list of errors/warnings)
    """
    errors = []
    is_valid = True

    # Check required fields
    required_fields = ["id", "text", "claim_type", "sources", "confidence"]
    for field in required_fields:
        if field not in claim:
            errors.append(f"Missing required field: {field}")
            is_valid = False

    if not is_valid:
        return False, errors

    # Validate claim type
    if claim["claim_type"] not in VALID_CLAIM_TYPES:
        errors.append(f"Invalid claim_type: {claim['claim_type']}. Must be one of {VALID_CLAIM_TYPES}")
        is_valid = False

    # Check for hallucination patterns
    hallucination_result = detect_hallucination_patterns(claim["text"])
    if hallucination_result["level"] == "BLOCK":
        errors.append(f"Hallucination pattern detected (BLOCK): {hallucination_result['matches']}")
        is_valid = False
    elif hallucination_result["level"] == "REQUIRE_SOURCE":
        # Check if sources are provided
        if not claim.get("sources"):
            errors.append(f"Hallucination: Statistical claim requires source: {hallucination_result['matches']}")
            is_valid = False

    # Validate sources
    sources = claim.get("sources", [])
    for i, source in enumerate(sources):
        if source.get("type") not in VALID_SOURCE_TYPES:
            errors.append(f"Invalid source type at index {i}: {source.get('type')}")
            is_valid = False

    # Check PRIMARY source requirement
    if requires_primary_source(claim["claim_type"]):
        has_primary = any(s.get("type") == "PRIMARY" for s in sources)
        if not has_primary:
            errors.append(f"{claim['claim_type']} claim requires at least one PRIMARY source")
            is_valid = False

    # Check confidence threshold (tiered enforcement)
    threshold = get_confidence_threshold(claim["claim_type"])
    confidence = claim.get("confidence", 0)
    claim_type = claim["claim_type"]
    if confidence < threshold:
        errors.append(
            f"Confidence {confidence} below threshold {threshold} for {claim_type}"
        )
        # Tiered hard fail based on claim type
        if claim_type in ("FACTUAL", "EMPIRICAL", "METHODOLOGICAL"):
            is_valid = False
        elif claim_type == "THEORETICAL":
            if confidence < (threshold - 10):  # 65 미만 hard fail
                is_valid = False
        else:  # INTERPRETIVE, SPECULATIVE
            if confidence < (threshold - 15):  # 55/45 미만 hard fail
                is_valid = False

    return is_valid, errors


def calculate_citation_score(claim: dict[str, Any]) -> float:
    """Calculate Citation Score (CS) - delegates to srcs_evaluator."""
    return _srcs_calculate_citation_score(claim)


def calculate_grounding_score(claim: dict[str, Any], research_type: str = "default") -> float:
    """Calculate Grounding Score (GS) - delegates to srcs_evaluator."""
    return _srcs_calculate_grounding_score(claim, research_type=research_type)


def calculate_uncertainty_score(claim: dict[str, Any]) -> float:
    """Calculate Uncertainty Score (US) - delegates to srcs_evaluator."""
    return _srcs_calculate_uncertainty_score(claim)


def calculate_verifiability_score(claim: dict[str, Any], research_type: str = "default") -> float:
    """Calculate Verifiability Score (VS) - delegates to srcs_evaluator."""
    return _srcs_calculate_verifiability_score(claim, research_type=research_type)


def calculate_srcs_score(claim: dict[str, Any], research_type: str = "default") -> dict[str, float]:
    """Calculate full SRCS score for a claim.

    Delegates to srcs_evaluator (single source of truth).

    Args:
        claim: Claim dictionary
        research_type: Research type for weight/pattern selection

    Returns:
        Dictionary with individual and total scores
    """
    from srcs_evaluator import get_srcs_weights

    cs = _srcs_calculate_citation_score(claim)
    gs = _srcs_calculate_grounding_score(claim, research_type=research_type)
    us = _srcs_calculate_uncertainty_score(claim)
    vs = _srcs_calculate_verifiability_score(claim, research_type=research_type)

    scores = {"cs": cs, "gs": gs, "us": us, "vs": vs}
    total = _srcs_calculate_weighted(scores, research_type=research_type)

    return {
        "cs": round(cs, 2),
        "gs": round(gs, 2),
        "us": round(us, 2),
        "vs": round(vs, 2),
        "total": round(total, 2),
    }


def generate_validation_report(
    claims: list[dict[str, Any]], research_type: str = "default"
) -> dict[str, Any]:
    """Generate a validation report for multiple claims.

    Args:
        claims: List of claim dictionaries
        research_type: Research type for SRCS weight/pattern selection

    Returns:
        Validation report dictionary
    """
    claim_reports = []
    total_valid = 0
    total_srcs = 0

    for claim in claims:
        is_valid, errors = validate_claim(claim)
        srcs_scores = calculate_srcs_score(claim, research_type=research_type)

        if is_valid:
            total_valid += 1

        total_srcs += srcs_scores["total"]

        claim_reports.append({
            "id": claim.get("id"),
            "is_valid": is_valid,
            "srcs_scores": srcs_scores,
            "errors": errors,
        })

    total_claims = len(claims)
    pass_rate = (total_valid / total_claims * 100) if total_claims > 0 else 0
    average_srcs = (total_srcs / total_claims) if total_claims > 0 else 0

    return {
        "total_claims": total_claims,
        "valid_claims": total_valid,
        "invalid_claims": total_claims - total_valid,
        "pass_rate": round(pass_rate, 2),
        "average_srcs": round(average_srcs, 2),
        "claims": claim_reports,
    }


def validate_from_stdin() -> None:
    """Read JSON from stdin and validate.

    Used as a hook for PostToolUse validation.
    """
    try:
        input_data = json.load(sys.stdin)

        # Check if this is tool output with claims
        tool_output = input_data.get("tool_output", "")
        file_path = input_data.get("tool_input", {}).get("file_path", "")

        # Only validate markdown files in thesis-output
        if not file_path or "thesis-output" not in file_path:
            sys.exit(0)

        if not file_path.endswith(".md"):
            sys.exit(0)

        # Try to extract claims from the file if it exists
        if Path(file_path).exists():
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Check for hallucination patterns in the content
            result = detect_hallucination_patterns(content)
            if result["level"] == "BLOCK":
                print(json.dumps({
                    "error": "GRA-001",
                    "message": f"Hallucination patterns detected: {result['matches']}",
                    "action": "BLOCK",
                }))
                sys.exit(2)  # Block the action

            if result["level"] == "REQUIRE_SOURCE":
                print(json.dumps({
                    "warning": "GRA-002",
                    "message": f"Statistical claims require sources: {result['matches']}",
                    "action": "WARN",
                }))

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception as e:
        print(json.dumps({"error": str(e)}), file=sys.stderr)
        sys.exit(0)


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="GRA validation tools")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate claims from JSON file")
    validate_parser.add_argument("file", type=Path, help="JSON file with claims")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check text for hallucination patterns")
    check_parser.add_argument("text", help="Text to check")

    # Hook command (reads from stdin)
    subparsers.add_parser("hook", help="Run as PostToolUse hook (reads stdin)")

    args = parser.parse_args()

    if args.command == "validate":
        with open(args.file, encoding="utf-8") as f:
            data = json.load(f)

        claims = data.get("claims", [data] if "id" in data else [])
        research_type = data.get("research_type", "default")
        report = generate_validation_report(claims, research_type=research_type)
        print(json.dumps(report, ensure_ascii=False, indent=2))

    elif args.command == "check":
        result = detect_hallucination_patterns(args.text)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "hook":
        validate_from_stdin()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
