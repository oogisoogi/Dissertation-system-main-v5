#!/usr/bin/env python3
"""Chapter Consistency Validator: Cross-chapter quality verification.

Validates consistency across all thesis chapters (post-writing, pre-review):
1. Term consistency: Same concept with different spellings
2. Citation consistency: Same reference with different formats
3. Numeric consistency: Same statistic cited differently
4. Cross-reference validity: References to non-existent chapters/sections

Runs after all chapters are written (step 125+) and before thesis-reviewer (step 132).

Design Principle:
    All checks are deterministic regex-based — no LLM judgment.
    Mechanical detection = zero missed issues.

Usage:
    python3 chapter_consistency_validator.py /path/to/03-thesis/

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-03-01
"""

import json
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent))
from workflow_constants import CROSS_VALIDATOR_SEVERITY_WEIGHTS as SEVERITY_PENALTY


# ============================================================================
# 1. Term Consistency
# ============================================================================

# Synonym groups — variants of the same concept that should be uniform
TERM_VARIANT_GROUPS = [
    # English academic terms
    [r"\bAI\b", r"\bartificial intelligence\b"],
    [r"\bML\b", r"\bmachine learning\b"],
    [r"\bDL\b", r"\bdeep learning\b"],
    [r"\bNLP\b", r"\bnatural language processing\b"],
    [r"\bRQ\b", r"\bresearch question\b"],
    [r"\bSLR\b", r"\bsystematic literature review\b"],
    [r"\bAGI\b", r"\bartificial general intelligence\b"],
    # Korean academic terms
    [r"\b인공지능\b", r"\bAI\b"],
    [r"\b기계학습\b", r"\b머신러닝\b"],
    [r"\b심층학습\b", r"\b딥러닝\b"],
    [r"\b연구질문\b", r"\b연구 질문\b", r"\b연구문제\b"],
    [r"\b문헌검토\b", r"\b문헌 검토\b", r"\b선행연구 검토\b"],
]


def find_term_variants(chapters: list[Path]) -> list[dict]:
    """Detect term inconsistencies across chapters.

    Args:
        chapters: List of chapter file paths

    Returns:
        List of term variant issues
    """
    issues = []

    for group in TERM_VARIANT_GROUPS:
        # Track which variants appear in which chapters
        variant_locations: dict[str, list[str]] = defaultdict(list)

        for chapter_path in chapters:
            content = chapter_path.read_text(encoding="utf-8")
            for pattern in group:
                if re.search(pattern, content, re.IGNORECASE):
                    variant_locations[pattern].append(chapter_path.name)

        # If multiple variants are used, flag inconsistency
        used_variants = {p: chs for p, chs in variant_locations.items() if chs}
        if len(used_variants) > 1:
            issues.append({
                "type": "TERM_INCONSISTENCY",
                "severity": "LOW",
                "variants": {p: chs for p, chs in used_variants.items()},
                "recommendation": (
                    f"Choose one term and use consistently. "
                    f"Variants found: {list(used_variants.keys())}"
                ),
            })

    return issues


# ============================================================================
# 2. Citation Consistency
# ============================================================================

# Citation patterns: (Author, Year) or Author (Year)
CITATION_PATTERN = re.compile(
    r"(?:"
    r"\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?),?\s*(\d{4})\)"  # (Author, 2024)
    r"|"
    r"([A-Z][a-z]+(?:\s+(?:et\s+al\.?|&\s+[A-Z][a-z]+))?)\s*\((\d{4})\)"    # Author (2024)
    r")"
)


def find_citation_variants(chapters: list[Path]) -> list[dict]:
    """Detect citation format inconsistencies across chapters.

    Args:
        chapters: List of chapter file paths

    Returns:
        List of citation variant issues
    """
    # Collect all citations: (author_normalized, year) -> {formats: set, chapters: set}
    citations: dict[tuple, dict] = defaultdict(lambda: {"formats": set(), "chapters": set()})

    for chapter_path in chapters:
        content = chapter_path.read_text(encoding="utf-8")
        for m in CITATION_PATTERN.finditer(content):
            if m.group(1):  # (Author, Year) format
                author = m.group(1).strip()
                year = m.group(2)
                fmt = f"({author}, {year})"
            else:  # Author (Year) format
                author = m.group(3).strip()
                year = m.group(4)
                fmt = f"{author} ({year})"

            # Normalize author for grouping
            author_norm = re.sub(r"\s+", " ", author.lower().strip())
            key = (author_norm, year)

            citations[key]["formats"].add(fmt)
            citations[key]["chapters"].add(chapter_path.name)

    # Find citations with multiple formats
    issues = []
    for (author, year), info in citations.items():
        if len(info["formats"]) > 1:
            issues.append({
                "type": "CITATION_INCONSISTENCY",
                "severity": "MEDIUM",
                "author": author,
                "year": year,
                "formats": list(info["formats"]),
                "chapters": list(info["chapters"]),
                "recommendation": f"Use consistent citation format for {author} ({year})",
            })

    return issues


# ============================================================================
# 3. Numeric Consistency
# ============================================================================

# Pattern: context word(s) + number with optional % or decimal
STAT_PATTERN = re.compile(
    r"(\b[a-zA-Z가-힣]+(?:\s+[a-zA-Z가-힣]+)?)\s+"
    r"(?:was|is|were|are|of|=|:)?\s*"
    r"(\d+(?:\.\d+)?%?)"
)


def cross_check_numbers(chapters: list[Path]) -> list[dict]:
    """Detect numeric inconsistencies across chapters.

    Same statistic cited with different values in different chapters.

    Args:
        chapters: List of chapter file paths

    Returns:
        List of numeric inconsistency issues
    """
    # Collect (context, value) pairs per chapter
    chapter_stats: dict[str, list[tuple[str, str]]] = {}

    for chapter_path in chapters:
        content = chapter_path.read_text(encoding="utf-8")
        stats = []
        for m in STAT_PATTERN.finditer(content):
            context = m.group(1).strip().lower()
            value = m.group(2).strip()
            stats.append((context, value))
        chapter_stats[chapter_path.name] = stats

    # Cross-compare between chapters
    issues = []
    chapter_names = list(chapter_stats.keys())

    for i, ch1 in enumerate(chapter_names):
        for ch2 in chapter_names[i + 1:]:
            for ctx1, val1 in chapter_stats[ch1]:
                for ctx2, val2 in chapter_stats[ch2]:
                    # Same context, different value
                    if ctx1 == ctx2 and val1 != val2:
                        v1 = _parse_numeric(val1)
                        v2 = _parse_numeric(val2)
                        if v1 is not None and v2 is not None and v1 != v2:
                            diff_pct = abs(v1 - v2) / max(v1, v2, 1) * 100
                            if diff_pct > 5:  # Ignore trivial rounding differences
                                severity = (
                                    "HIGH" if diff_pct > 20
                                    else "MEDIUM" if diff_pct > 10
                                    else "LOW"
                                )
                                issues.append({
                                    "type": "NUMERIC_INCONSISTENCY",
                                    "severity": severity,
                                    "context": ctx1,
                                    "value1": val1,
                                    "value2": val2,
                                    "chapter1": ch1,
                                    "chapter2": ch2,
                                    "diff_pct": round(diff_pct, 1),
                                })

    return issues


def _parse_numeric(value: str) -> Optional[float]:
    """Parse numeric value from string."""
    try:
        return float(value.replace("%", ""))
    except ValueError:
        return None


# ============================================================================
# 4. Cross-Reference Validity
# ============================================================================

# Patterns for cross-references
CROSS_REF_PATTERNS = [
    # English: "Chapter N", "Section N.M", "see Chapter N"
    re.compile(r"(?:Chapter|chapter|Ch\.?)\s*(\d+)", re.IGNORECASE),
    re.compile(r"(?:Section|section|Sec\.?)\s*(\d+(?:\.\d+)*)", re.IGNORECASE),
    # Korean: "제N장", "N장", "N절"
    re.compile(r"제\s*(\d+)\s*장"),
    re.compile(r"(\d+)\s*장"),
    re.compile(r"(\d+(?:\.\d+)?)\s*절"),
]


def check_cross_references(chapters: list[Path]) -> list[dict]:
    """Detect broken cross-references.

    Args:
        chapters: List of chapter file paths

    Returns:
        List of broken reference issues
    """
    # Determine which chapters exist
    existing_chapters = set()
    for chapter_path in chapters:
        # Extract chapter number from filename (e.g., ch1.md, chapter-1.md)
        ch_match = re.search(r"ch(?:apter)?[-_]?(\d+)", chapter_path.stem, re.IGNORECASE)
        if ch_match:
            existing_chapters.add(int(ch_match.group(1)))

    issues = []
    for chapter_path in chapters:
        content = chapter_path.read_text(encoding="utf-8")

        for pattern in CROSS_REF_PATTERNS:
            for m in pattern.finditer(content):
                ref = m.group(1)
                # Extract chapter number (first digit before any dot)
                ref_ch = int(ref.split(".")[0])

                if ref_ch > 0 and ref_ch not in existing_chapters:
                    issues.append({
                        "type": "BROKEN_CROSS_REFERENCE",
                        "severity": "HIGH",
                        "reference": m.group(0),
                        "referenced_chapter": ref_ch,
                        "source_chapter": chapter_path.name,
                        "recommendation": (
                            f"Chapter {ref_ch} referenced in {chapter_path.name} "
                            f"does not exist. Available: {sorted(existing_chapters)}"
                        ),
                    })

    return issues


# ============================================================================
# Main Validator
# ============================================================================

def validate_chapter_consistency(chapter_dir: Path) -> dict:
    """Run all consistency checks across chapters.

    Args:
        chapter_dir: Path to directory containing chapter .md files

    Returns:
        Validation result with score, issues, and pass/fail status
    """
    # Find chapter files
    chapters = sorted(
        [f for f in chapter_dir.glob("ch*.md") if f.is_file()]
        + [f for f in chapter_dir.glob("chapter*.md") if f.is_file()]
    )

    if not chapters:
        return {
            "error": f"No chapter files found in {chapter_dir}",
            "score": 0,
            "passed": False,
        }

    # Run all checks
    term_issues = find_term_variants(chapters)
    citation_issues = find_citation_variants(chapters)
    numeric_issues = cross_check_numbers(chapters)
    ref_issues = check_cross_references(chapters)

    all_issues = term_issues + citation_issues + numeric_issues + ref_issues

    # Calculate score
    total_penalty = sum(
        SEVERITY_PENALTY.get(issue.get("severity", "LOW"), 3)
        for issue in all_issues
    )
    # Cap penalty relative to chapter count
    max_penalty = len(chapters) * 30
    score = max(0, 100 - (total_penalty / max(max_penalty, 1) * 100))
    score = round(score, 1)

    return {
        "chapters_checked": len(chapters),
        "chapter_files": [c.name for c in chapters],
        "score": score,
        "passed": score >= 75,
        "total_issues": len(all_issues),
        "issues_by_type": {
            "term_inconsistency": len(term_issues),
            "citation_inconsistency": len(citation_issues),
            "numeric_inconsistency": len(numeric_issues),
            "broken_cross_reference": len(ref_issues),
        },
        "issues": all_issues,
    }


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: chapter_consistency_validator.py <chapter_dir>")
        print("  chapter_dir: Path to 03-thesis/ or directory with ch*.md files")
        sys.exit(1)

    chapter_dir = Path(sys.argv[1])
    result = validate_chapter_consistency(chapter_dir)

    print(json.dumps(result, ensure_ascii=False, indent=2))

    if result.get("passed"):
        print(f"\n✅ Chapter consistency check PASSED (score: {result['score']}/100)")
    else:
        print(f"\n❌ Chapter consistency check FAILED (score: {result['score']}/100)")

    sys.exit(0 if result.get("passed") else 1)


if __name__ == "__main__":
    main()
