#!/usr/bin/env python3
"""Feedback Extractor: Parse thesis-reviewer output into structured revision briefs.

Parses review-report-chN.md (thesis-reviewer output) to generate
revision-brief-chN.json — a structured, prioritized list of revision actions.

Design Principle:
    "Feedback extraction is deterministic regex parsing — no LLM re-interpretation."
    This prevents information loss when converting review → revision instructions.

Usage:
    python3 feedback_extractor.py /path/to/review-report-ch1.md
    python3 feedback_extractor.py /path/to/03-thesis/ --all

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-03-01
"""

import json
import re
import sys
from pathlib import Path
from typing import Optional


def extract_review_feedback(report_path: Path) -> dict:
    """Parse thesis-reviewer report into structured feedback.

    Parsing strategy (based on thesis-reviewer.md actual output format):
    1. Score table extraction (Korean markdown table)
    2. DWC sub-scores extraction
    3. Final verdict extraction
    4. Issue list extraction (numbered items with bold headers)
    5. Priority-sorted action list generation

    Args:
        report_path: Path to review-report-chN.md

    Returns:
        Structured feedback dictionary with scores, issues, and prioritized actions
    """
    content = report_path.read_text(encoding="utf-8")

    # Extract chapter number from filename
    ch_match = re.search(r"ch(\d+)", report_path.stem)
    chapter_num = int(ch_match.group(1)) if ch_match else 0

    # ── 1. Score table extraction ──
    # Pattern: | N. 항목 | 가중치% | 점수/100 | 임계값+ | 상태 |
    score_pattern = (
        r"\|\s*\d+\.\s*(.+?)\s*\|\s*(\d+)%\s*\|\s*(\d+)/100\s*\|\s*(\d+)\+\s*\|\s*(✅|⚠️|❌)\s*\|"
    )
    scores = {}
    for m in re.finditer(score_pattern, content):
        criterion_name = m.group(1).strip()
        scores[criterion_name] = {
            "weight": int(m.group(2)),
            "score": int(m.group(3)),
            "threshold": int(m.group(4)),
            "status": m.group(5),
        }

    # ── 2. DWC sub-scores extraction ──
    # Pattern: | 항목 | 점수/100 | 통과/미달 |
    dwc_pattern = r"\|\s*(.+?)\s*\|\s*(\d+)/100\s*\|\s*(통과|미달)\s*\|"
    dwc_scores = {}
    for m in re.finditer(dwc_pattern, content):
        item_name = m.group(1).strip()
        # Skip if it looks like the main score table (has % weight)
        if "%" in item_name:
            continue
        dwc_scores[item_name] = {
            "score": int(m.group(2)),
            "passed": m.group(3) == "통과",
        }

    # ── 3. Final verdict extraction ──
    verdict = "UNKNOWN"
    verdict_patterns = [
        (r"✅\s*통과", "PASS"),
        (r"⚠️\s*수정\s*후\s*재검토", "REVISE"),
        (r"❌\s*재작성\s*필요", "REWRITE"),
        # English fallbacks
        (r"✅\s*PASS", "PASS"),
        (r"⚠️\s*REVISE", "REVISE"),
        (r"❌\s*REWRITE", "REWRITE"),
    ]
    for pattern, v in verdict_patterns:
        if re.search(pattern, content):
            verdict = v
            break

    # ── 4. Issue list extraction (numbered items with bold headers) ──
    # Pattern: 1. **Issue Title**: Description...
    issue_pattern = r"(?:^|\n)\s*(\d+)\.\s*\*\*(.+?)\*\*[:\s]*(.+?)(?=\n\s*\d+\.|\n\n|\Z)"
    issues = []
    for m in re.finditer(issue_pattern, content, re.DOTALL):
        issue_num = int(m.group(1))
        title = m.group(2).strip()
        description = m.group(3).strip()
        # Clean up multi-line descriptions
        description = re.sub(r"\s+", " ", description)

        # Classify severity based on keywords
        severity = _classify_issue_severity(title, description)

        issues.append({
            "number": issue_num,
            "title": title,
            "description": description[:500],  # Truncate very long descriptions
            "severity": severity,
        })

    # ── 5. Identify DWC failures and criteria failures ──
    all_issues = list(issues)  # Copy

    # Add DWC failures as issues
    for item_name, dwc in dwc_scores.items():
        if not dwc["passed"]:
            all_issues.append({
                "number": 0,
                "title": f"DWC 미달: {item_name}",
                "description": f"{item_name} 점수 {dwc['score']}/100 — 임계값 미달",
                "severity": "CRITICAL",
                "type": "DWC_FAIL",
            })

    # Add criteria failures as issues
    for criterion, score_info in scores.items():
        if score_info["status"] == "❌":
            all_issues.append({
                "number": 0,
                "title": f"평가기준 미달: {criterion}",
                "description": (
                    f"{criterion} 점수 {score_info['score']}/100 "
                    f"(임계값 {score_info['threshold']}+)"
                ),
                "severity": "CRITICAL",
                "type": "CRITERIA_FAIL",
            })
        elif score_info["status"] == "⚠️":
            all_issues.append({
                "number": 0,
                "title": f"평가기준 주의: {criterion}",
                "description": (
                    f"{criterion} 점수 {score_info['score']}/100 "
                    f"(임계값 {score_info['threshold']}+) — 경계선"
                ),
                "severity": "WARNING",
                "type": "CRITERIA_WARNING",
            })

    # ── 6. Priority-sorted action list ──
    prioritized_actions = sorted(all_issues, key=lambda x: (
        0 if x.get("type") == "DWC_FAIL" else
        1 if x.get("severity") == "CRITICAL" else
        2 if x.get("type") == "CRITERIA_FAIL" else
        3 if x.get("severity") == "WARNING" else
        4
    ))

    return {
        "chapter": chapter_num,
        "source_file": report_path.name,
        "verdict": verdict,
        "scores": scores,
        "dwc_scores": dwc_scores,
        "issues": issues,
        "prioritized_actions": prioritized_actions,
        "total_issues": len(all_issues),
        "critical_count": sum(1 for i in all_issues if i.get("severity") == "CRITICAL"),
        "warning_count": sum(1 for i in all_issues if i.get("severity") == "WARNING"),
    }


def _classify_issue_severity(title: str, description: str) -> str:
    """Classify issue severity based on keywords.

    Args:
        title: Issue title
        description: Issue description

    Returns:
        "CRITICAL", "WARNING", or "INFO"
    """
    text = (title + " " + description).lower()

    critical_keywords = [
        "재작성", "rewrite", "심각", "critical", "필수", "required",
        "누락", "missing", "오류", "error", "잘못", "incorrect",
        "표절", "plagiarism", "위반", "violation",
    ]
    warning_keywords = [
        "수정", "revise", "개선", "improve", "보완", "supplement",
        "권장", "recommend", "부족", "insufficient", "약", "weak",
    ]

    for kw in critical_keywords:
        if kw in text:
            return "CRITICAL"
    for kw in warning_keywords:
        if kw in text:
            return "WARNING"
    return "INFO"


def extract_all_chapter_feedback(thesis_dir: Path) -> list[dict]:
    """Extract feedback from all review reports in a directory.

    Args:
        thesis_dir: Path to 03-thesis/ directory

    Returns:
        List of feedback dictionaries, one per chapter
    """
    results = []
    for report_path in sorted(thesis_dir.glob("review-report-ch*.md")):
        try:
            feedback = extract_review_feedback(report_path)
            results.append(feedback)
        except Exception as e:
            results.append({
                "chapter": 0,
                "source_file": report_path.name,
                "error": str(e),
            })
    return results


def save_revision_brief(feedback: dict, output_path: Path) -> None:
    """Save structured feedback as revision brief JSON.

    Args:
        feedback: Feedback dictionary from extract_review_feedback()
        output_path: Output path for revision-brief-chN.json
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(feedback, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def main():
    """CLI entry point."""
    if len(sys.argv) < 2:
        print("Usage: feedback_extractor.py <review-report.md|thesis-dir> [--all]")
        print("  Single file: feedback_extractor.py review-report-ch1.md")
        print("  All chapters: feedback_extractor.py /path/to/03-thesis/ --all")
        sys.exit(1)

    path = Path(sys.argv[1])
    all_mode = "--all" in sys.argv

    if all_mode and path.is_dir():
        # Process all review reports
        results = extract_all_chapter_feedback(path)
        for feedback in results:
            if "error" in feedback:
                print(f"  Error: {feedback['source_file']}: {feedback['error']}")
                continue
            ch_num = feedback["chapter"]
            output_path = path / f"revision-brief-ch{ch_num}.json"
            save_revision_brief(feedback, output_path)
            print(
                f"  Ch.{ch_num}: {feedback['verdict']} "
                f"({feedback['critical_count']} critical, "
                f"{feedback['warning_count']} warnings) "
                f"-> {output_path.name}"
            )
    elif path.is_file():
        # Process single review report
        feedback = extract_review_feedback(path)
        ch_num = feedback["chapter"]
        output_path = path.parent / f"revision-brief-ch{ch_num}.json"
        save_revision_brief(feedback, output_path)
        print(json.dumps(feedback, ensure_ascii=False, indent=2))
        print(f"\nSaved to: {output_path}")
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()
