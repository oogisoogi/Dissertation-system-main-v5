#!/usr/bin/env python3
"""Deterministic Simulation Mode Router.

All simulation routing is performed in a single Python process — deterministic,
no LLM judgment. session.json read → mode resolution → execution plan → JSON report.

Design Principle:
    "Tasks requiring exact, 100% reproducible results must be Python code."
    Simulation mode routing is a critical branching decision that determines
    the entire Phase 3 execution path. It must be deterministic on every run.

Usage:
    python3 simulation_router.py --dir /path/to/thesis-output/project/

Output:
    JSON object with execution_path, agent sequence, page targets,
    and quality thresholds. The orchestrator follows this plan exactly.

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-03-02
"""

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from workflow_constants import (
    DEFAULT_SIMULATION_MODE,
    SIMULATION_MODES,
    VALID_SIMULATION_MODES,
    SRCS_DEFAULT_THRESHOLD,
    PTCS_THRESHOLDS,
    PLAGIARISM_THRESHOLD,
    DWC_THRESHOLD,
)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ExecutionStep:
    """A single step in the execution plan."""
    order: int
    agent: str | None
    action: str
    args: dict = field(default_factory=dict)
    output: str | None = None


@dataclass
class BothPhase:
    """A phase in the Both (Quick → Review → Full) execution path."""
    phase: str          # "A", "B", "C"
    label: str
    execution_path: str | None = None
    output_subdir: str | None = None
    writer_agent: str | None = None
    use_simulation_controller: bool = False
    action: str | None = None
    options: list[str] | None = None


@dataclass
class SmartResolution:
    """Resolution details for Smart mode."""
    uncertainty: float
    thresholds: dict
    decision_reason: str


@dataclass
class RoutingDecision:
    """Complete routing decision — the single output of this script."""
    simulation_mode: str        # Original mode from session.json
    resolved_mode: str          # Actual mode after smart resolution
    execution_path: str         # "quick" | "full" | "both"
    writer_agent: str | None = None
    use_simulation_controller: bool = False
    skip_outline: bool = False
    page_targets: dict = field(default_factory=dict)
    total_pages: str = ""
    estimated_hours: str = ""
    quality_thresholds: dict = field(default_factory=dict)
    steps: list[dict] = field(default_factory=list)
    phases: list[dict] | None = None  # For "both" mode only
    smart_resolution: dict | None = None  # For "smart" mode only
    timestamp: str = ""

    def to_dict(self) -> dict:
        """Convert to dict, excluding None values for clean JSON."""
        result = asdict(self)
        return {k: v for k, v in result.items() if v is not None}


# ============================================================================
# Core Functions
# ============================================================================

def _load_session(working_dir: Path) -> dict:
    """Load session.json from the working directory.

    Read-only access — respects Single Writer Principle.

    Args:
        working_dir: Project working directory (e.g., thesis-output/slug-date/)

    Returns:
        Session dictionary, or empty dict if not found/invalid.
    """
    session_path = working_dir / "00-session" / "session.json"
    if not session_path.exists():
        return {}
    try:
        return json.loads(session_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _load_simulation_mode(session: dict) -> str:
    """Extract simulation_mode from session data.

    Applies strict validation against VALID_SIMULATION_MODES (from SOT-A).
    Falls back to DEFAULT_SIMULATION_MODE ('full') for any invalid/missing value.

    Args:
        session: Session dictionary (from session.json)

    Returns:
        Validated simulation mode string.
    """
    mode = session.get("options", {}).get("simulation_mode", DEFAULT_SIMULATION_MODE)
    if mode not in VALID_SIMULATION_MODES:
        return DEFAULT_SIMULATION_MODE
    return mode


def _compute_uncertainty(session: dict) -> float:
    """Compute uncertainty score from Phase 1-2 quality data.

    Deterministic calculation — no LLM judgment.

    Uses SRCS scores stored in session.json by gate validations:
    - High avg SRCS (≥90) → low uncertainty (0.1)
    - Medium-high (≥80)   → low uncertainty (0.3)
    - Medium (≥70)        → medium uncertainty (0.5)
    - Low (<70)           → high uncertainty (0.8)
    - No data             → high uncertainty (0.7, conservative default)

    Args:
        session: Session dictionary

    Returns:
        Uncertainty score (0.0 to 1.0)
    """
    srcs_scores = session.get("quality", {}).get("srcs_scores", [])

    if not srcs_scores:
        return 0.7  # No data → conservative (0.7 = boundary → "both" mode)

    # Extract numeric total scores from all SRCS evaluations
    total_scores = []
    for entry in srcs_scores:
        if isinstance(entry, dict):
            total = entry.get("total")
            if total is None:
                total = entry.get("overall_score")
            if isinstance(total, (int, float)):
                total_scores.append(float(total))

    if not total_scores:
        return 0.7  # No valid scores → conservative (boundary → "both" mode)

    avg_srcs = sum(total_scores) / len(total_scores)

    # Deterministic mapping: score → uncertainty
    if avg_srcs >= 90.0:
        return 0.1
    elif avg_srcs >= 80.0:
        return 0.3
    elif avg_srcs >= 70.0:
        return 0.5
    else:
        return 0.8


def _resolve_smart_mode(session: dict) -> tuple[str, float]:
    """Resolve 'smart' mode to an actual execution mode.

    Uses uncertainty thresholds from SIMULATION_MODES['smart'] (SOT-A):
    - uncertainty > high_threshold (0.7) → quick
    - uncertainty < low_threshold (0.3)  → full
    - otherwise                          → both

    Args:
        session: Session dictionary

    Returns:
        Tuple of (resolved_mode, uncertainty_score)
    """
    uncertainty = _compute_uncertainty(session)
    thresholds = SIMULATION_MODES.get("smart", {}).get(
        "uncertainty_thresholds", {"high": 0.7, "low": 0.3}
    )

    if uncertainty > thresholds["high"]:
        return "quick", uncertainty
    elif uncertainty < thresholds["low"]:
        return "full", uncertainty
    else:
        return "both", uncertainty


def _build_quality_thresholds() -> dict:
    """Build quality thresholds from SOT-A constants.

    All modes share identical quality requirements — this is a core design
    principle of the simulation system. Quick and Full differ only in page
    count, never in quality standards.

    Returns:
        Dictionary with threshold values from workflow_constants.py
    """
    return {
        "ptcs_min": PTCS_THRESHOLDS["workflow"],       # 75
        "srcs_min": SRCS_DEFAULT_THRESHOLD,             # 75
        "dwc_min": DWC_THRESHOLD,                       # 80
        "plagiarism_max_percent": PLAGIARISM_THRESHOLD,  # 15
    }


def _build_quick_plan(mode_config: dict, quality: dict) -> RoutingDecision:
    """Build execution plan for Quick mode.

    Quick path:
        simulation-controller(quick) → thesis-reviewer(DWC 80+)
        → plagiarism-checker → integrate → export-docx

    simulation-controller internally invokes thesis-writer-quick-rlm
    with RLM enabled (max_context_files=15, progressive compression).
    """
    return RoutingDecision(
        simulation_mode="quick",
        resolved_mode="quick",
        execution_path="quick",
        writer_agent=mode_config.get("writer_agent", "thesis-writer-quick-rlm"),
        use_simulation_controller=True,
        skip_outline=True,
        page_targets=mode_config.get("chapter_pages", {}),
        total_pages=f"{mode_config.get('pages_min', 20)}-{mode_config.get('pages_max', 30)}",
        estimated_hours=mode_config.get("estimated_hours", "1-2"),
        quality_thresholds=quality,
        steps=[
            asdict(ExecutionStep(
                order=1,
                agent="simulation-controller",
                action="write",
                args={"mode": "quick", "phase": "phase3"},
            )),
            asdict(ExecutionStep(
                order=2,
                agent="thesis-reviewer",
                action="review",
                args={"dwc_threshold": DWC_THRESHOLD},
            )),
            asdict(ExecutionStep(
                order=3,
                agent="plagiarism-checker",
                action="check",
            )),
            asdict(ExecutionStep(
                order=4,
                agent=None,
                action="integrate",
                output="thesis-final.md",
            )),
            asdict(ExecutionStep(
                order=5,
                agent=None,
                action="export-docx",
            )),
        ],
    )


def _build_full_plan(mode_config: dict, quality: dict) -> RoutingDecision:
    """Build execution plan for Full mode.

    Full path (existing pipeline, 100% preserved):
        thesis-architect → thesis-writer(Ch1-5) → thesis-reviewer(DWC 80+)
        → plagiarism-checker → integrate → export-docx

    thesis-writer uses thesis-writer-rlm with RLM enabled for full-length
    chapters (15-45 pages each).
    """
    return RoutingDecision(
        simulation_mode="full",
        resolved_mode="full",
        execution_path="full",
        writer_agent=mode_config.get("writer_agent", "thesis-writer-rlm"),
        use_simulation_controller=False,
        skip_outline=False,
        page_targets=mode_config.get("chapter_pages", {}),
        total_pages=f"{mode_config.get('pages_min', 145)}-{mode_config.get('pages_max', 155)}",
        estimated_hours=mode_config.get("estimated_hours", "5-7"),
        quality_thresholds=quality,
        steps=[
            asdict(ExecutionStep(
                order=1,
                agent="thesis-architect",
                action="outline",
            )),
            asdict(ExecutionStep(
                order=2,
                agent="thesis-writer",
                action="write",
                args={"chapters": [1, 2, 3, 4, 5]},
            )),
            asdict(ExecutionStep(
                order=3,
                agent="thesis-reviewer",
                action="review",
                args={"dwc_threshold": DWC_THRESHOLD},
            )),
            asdict(ExecutionStep(
                order=4,
                agent="plagiarism-checker",
                action="check",
            )),
            asdict(ExecutionStep(
                order=5,
                agent=None,
                action="integrate",
                output="thesis-final.md",
            )),
            asdict(ExecutionStep(
                order=6,
                agent=None,
                action="export-docx",
            )),
        ],
    )


def _build_both_plan(quality: dict) -> RoutingDecision:
    """Build execution plan for Both mode (Quick → Review → Full).

    Phase A: Quick execution (saves to 03-thesis/quick/)
    Phase B: HITL review (user decides: accept / upgrade / revise)
    Phase C: Full execution if approved (saves to 03-thesis/)
    """
    quick_config = SIMULATION_MODES.get("quick", {})
    full_config = SIMULATION_MODES.get("full", {})

    return RoutingDecision(
        simulation_mode="both",
        resolved_mode="both",
        execution_path="both",
        estimated_hours=SIMULATION_MODES.get("both", {}).get("estimated_hours", "6-9"),
        quality_thresholds=quality,
        phases=[
            asdict(BothPhase(
                phase="A",
                label="Quick Execution",
                execution_path="quick",
                output_subdir="03-thesis/quick/",
                writer_agent=quick_config.get("writer_agent", "thesis-writer-quick-rlm"),
                use_simulation_controller=True,
            )),
            asdict(BothPhase(
                phase="B",
                label="HITL Review",
                action="user_review",
                options=["accept_quick", "upgrade_to_full", "revise_and_retry"],
            )),
            asdict(BothPhase(
                phase="C",
                label="Full Execution (if approved)",
                execution_path="full",
                output_subdir="03-thesis/",
                writer_agent=full_config.get("writer_agent", "thesis-writer-rlm"),
                use_simulation_controller=False,
            )),
        ],
    )


def route_simulation(working_dir: Path) -> dict:
    """Deterministic simulation mode routing — no LLM, pure computation.

    Pipeline:
        1. Load session.json (read-only)
        2. Extract and validate simulation_mode
        3. Resolve 'smart' mode via deterministic uncertainty calculation
        4. Build execution plan from SOT-A constants
        5. Return structured JSON routing decision

    Args:
        working_dir: Absolute path to project working directory

    Returns:
        Dictionary with complete routing decision
    """
    # 1. Load session (read-only)
    session = _load_session(working_dir)

    # 2. Extract and validate simulation_mode
    simulation_mode = _load_simulation_mode(session)

    # 3. Resolve smart mode
    resolved_mode = simulation_mode
    uncertainty = None

    if simulation_mode == "smart":
        resolved_mode, uncertainty = _resolve_smart_mode(session)

    # 4. Build quality thresholds (identical for all modes — from SOT-A)
    quality = _build_quality_thresholds()

    # 5. Build execution plan based on resolved mode
    if resolved_mode == "quick":
        mode_config = SIMULATION_MODES.get("quick", {})
        decision = _build_quick_plan(mode_config, quality)
    elif resolved_mode == "both":
        decision = _build_both_plan(quality)
    else:
        # "full" or any unrecognized → default to full (backwards compatibility)
        mode_config = SIMULATION_MODES.get("full", {})
        decision = _build_full_plan(mode_config, quality)

    # Override simulation_mode if it was originally 'smart'
    if simulation_mode == "smart":
        decision.simulation_mode = "smart"
        decision.smart_resolution = asdict(SmartResolution(
            uncertainty=uncertainty,
            thresholds=SIMULATION_MODES["smart"]["uncertainty_thresholds"],
            decision_reason=f"Uncertainty {uncertainty:.2f} → {resolved_mode} mode",
        ))

    decision.timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    return decision.to_dict()


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """CLI entry point for deterministic simulation routing."""
    parser = argparse.ArgumentParser(
        description=(
            "Deterministic Simulation Mode Router — no LLM, pure Python computation. "
            "Reads session.json and returns a structured JSON execution plan."
        ),
    )
    parser.add_argument(
        "--dir",
        required=True,
        type=Path,
        help="Absolute path to project working directory (e.g., thesis-output/slug-date/)",
    )

    args = parser.parse_args()

    # Validate directory exists
    if not args.dir.exists():
        error = {
            "error": f"Working directory not found: {args.dir}",
            "execution_path": "full",
            "resolved_mode": "full",
            "fallback": True,
        }
        print(json.dumps(error, ensure_ascii=False, indent=2))
        sys.exit(1)

    result = route_simulation(args.dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # Always exit 0 on success — routing never fails because invalid modes
    # gracefully fall back to 'full'
    sys.exit(0)


if __name__ == "__main__":
    main()
