#!/usr/bin/env python3
"""Performance Collector: Read-Only Metrics Gathering.

This module collects performance metrics from completed workflow runs
WITHOUT modifying any existing files. It reads from:
- session.json (workflow state)
- gate-status-*.json (gate validation results)
- Agent output files (for length/quality analysis)
- confidence-monitor snapshots (pTCS/SRCS data)

All output is written to a NEW file in the improvement-data/ directory.
No existing files are modified.

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-31
"""

import sys
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from path_utils import get_working_dir_from_session


# ============================================================================
# Constants
# ============================================================================

VERSION = "1.0.0"

# Agent definitions per wave/phase (maps to checklist steps).
# NOTE: This registry aligns with workflow_constants.AGENT_STEP_MAP (SOT-A)
# and WAVE_FILES. When adding/removing agents, update both locations.
AGENT_REGISTRY = {
    "phase1-wave1": [
        "literature-searcher", "seminal-works-analyst",
        "trend-analyst", "methodology-scanner",
    ],
    "phase1-wave2": [
        "theoretical-framework-analyst", "empirical-evidence-analyst",
        "gap-identifier", "variable-relationship-analyst",
    ],
    "phase1-wave3": [
        "critical-reviewer", "methodology-critic",
        "limitation-analyst", "future-direction-analyst",
    ],
    "phase1-wave4": [
        "synthesis-agent", "conceptual-model-builder",
    ],
    "phase1-wave5": [
        "plagiarism-checker", "unified-srcs-evaluator",
        "research-synthesizer",
    ],
    "phase2-quantitative": [
        "hypothesis-developer", "research-model-developer",
        "sampling-designer", "statistical-planner",
    ],
    "phase2-qualitative": [
        "paradigm-consultant", "participant-selector",
        "qualitative-data-designer", "qualitative-analysis-planner",
    ],
    "phase2-mixed": [
        "mixed-methods-designer", "integration-strategist",
    ],
    "phase3": [
        "thesis-architect", "thesis-writer", "thesis-reviewer",
        "plagiarism-checker",
    ],
    "phase4": [
        "publication-strategist", "manuscript-formatter",
    ],
}

# Output directories expected per phase (from single source of truth)
from workflow_constants import PHASE_DIRS_EXTENDED as OUTPUT_DIRS


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class AgentMetrics:
    """Performance metrics for a single agent."""

    agent_name: str
    phase: str
    wave: Optional[str]

    # Quality scores (None if not available)
    ptcs: Optional[float] = None
    srcs: Optional[float] = None

    # Execution info
    retry_count: int = 0
    success: bool = True
    output_file_count: int = 0
    total_output_length: int = 0

    # Quality flags
    hallucination_triggers: int = 0
    low_confidence_claims: int = 0
    total_claims: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GateMetrics:
    """Performance metrics for a gate validation."""

    gate_id: str
    gate_type: str  # "wave" | "phase"
    passed: bool
    ptcs: Optional[float] = None
    srcs: Optional[float] = None
    combined: Optional[float] = None
    attempts: int = 1
    decision: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PerformanceReport:
    """Complete performance report for a workflow run."""

    run_id: str
    timestamp: str
    version: str

    # Scope
    phase: Optional[str] = None
    wave: Optional[str] = None

    # Agent metrics
    agents: Dict[str, dict] = None

    # Gate metrics
    gates: Dict[str, dict] = None

    # Overall summary
    overall: Dict[str, Any] = None

    def __post_init__(self):
        if self.agents is None:
            self.agents = {}
        if self.gates is None:
            self.gates = {}
        if self.overall is None:
            self.overall = {}

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Performance Collector (Read-Only)
# ============================================================================

class PerformanceCollector:
    """Collects performance metrics from completed workflow runs.

    This class is STRICTLY READ-ONLY. It reads existing data files
    and produces a new performance report. It never modifies any
    existing files in the workflow.
    """

    def __init__(self, working_dir: Path, verbose: bool = True):
        """Initialize collector.

        Args:
            working_dir: Project working directory (thesis-output/<project>/)
            verbose: Print detailed logs
        """
        self.working_dir = Path(working_dir).resolve()
        self.verbose = verbose
        self.session_data: Dict[str, Any] = {}

    # ========================================================================
    # Main Collection
    # ========================================================================

    def collect(
        self,
        phase: Optional[str] = None,
        wave: Optional[str] = None,
    ) -> PerformanceReport:
        """Collect performance metrics for the specified scope.

        Args:
            phase: Phase to analyze (e.g., "phase1"). None = all.
            wave: Wave to analyze (e.g., "wave1"). None = all waves in phase.

        Returns:
            PerformanceReport with collected metrics
        """
        self._log(f"\n{'='*70}")
        self._log("PERFORMANCE COLLECTOR (Read-Only)")
        self._log(f"{'='*70}")
        self._log(f"Working dir: {self.working_dir}")
        self._log(f"Scope: phase={phase}, wave={wave}")
        self._log("")

        # Load session data
        self._load_session()

        # Generate run ID
        now = datetime.now(timezone.utc)
        run_id = now.strftime("%Y-%m-%d-%H%M%S")
        timestamp = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Collect agent metrics
        agent_metrics = self._collect_agent_metrics(phase, wave)

        # Collect gate metrics
        gate_metrics = self._collect_gate_metrics(phase)

        # Calculate overall summary
        overall = self._calculate_overall(agent_metrics, gate_metrics)

        report = PerformanceReport(
            run_id=run_id,
            timestamp=timestamp,
            version=VERSION,
            phase=phase,
            wave=wave,
            agents={name: m.to_dict() for name, m in agent_metrics.items()},
            gates={gid: m.to_dict() for gid, m in gate_metrics.items()},
            overall=overall,
        )

        self._log(f"\nCollected metrics for {len(agent_metrics)} agents, "
                   f"{len(gate_metrics)} gates")

        return report

    def save_report(self, report: PerformanceReport) -> Path:
        """Save performance report to improvement-data directory.

        Only creates NEW files. Never modifies existing ones.

        Args:
            report: PerformanceReport to save

        Returns:
            Path to saved report file
        """
        improvement_dir = self.working_dir / "00-session" / "improvement-data"
        improvement_dir.mkdir(parents=True, exist_ok=True)

        filename = f"performance-metrics-{report.run_id}.json"
        output_path = improvement_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report.to_dict(), f, indent=2, ensure_ascii=False)

        self._log(f"Report saved: {output_path}")
        return output_path

    # ========================================================================
    # Agent Metrics Collection (Read-Only)
    # ========================================================================

    def _collect_agent_metrics(
        self,
        phase: Optional[str],
        wave: Optional[str],
    ) -> Dict[str, AgentMetrics]:
        """Collect metrics for agents in the specified scope.

        Reads output files to determine success, output length, etc.
        Does NOT execute any agents or modify any files.
        """
        metrics = {}

        # Determine which agent groups to analyze
        target_groups = self._get_target_groups(phase, wave)

        for group_name, agents in target_groups.items():
            output_dir_name = OUTPUT_DIRS.get(group_name, "")
            output_dir = self.working_dir / output_dir_name

            for agent_name in agents:
                agent_metric = self._collect_single_agent(
                    agent_name, group_name, output_dir
                )
                metrics[agent_name] = agent_metric

        return metrics

    def _collect_single_agent(
        self,
        agent_name: str,
        group_name: str,
        output_dir: Path,
    ) -> AgentMetrics:
        """Collect metrics for a single agent by reading its output files."""
        # Determine phase and wave from group name
        if "wave" in group_name:
            parts = group_name.split("-")
            phase_name = parts[0]  # "phase1"
            wave_name = parts[1] if len(parts) > 1 else None  # "wave1"
        else:
            phase_name = group_name
            wave_name = None

        metric = AgentMetrics(
            agent_name=agent_name,
            phase=phase_name,
            wave=wave_name,
        )

        # Find output files matching this agent
        if output_dir.exists():
            agent_files = self._find_agent_outputs(output_dir, agent_name)
            metric.output_file_count = len(agent_files)
            metric.total_output_length = sum(
                f.stat().st_size for f in agent_files if f.exists()
            )
            metric.success = len(agent_files) > 0

            # Analyze claim quality from output files
            claims_data = self._extract_claims_from_files(agent_files)
            if claims_data:
                metric.total_claims = claims_data.get("total", 0)
                metric.low_confidence_claims = claims_data.get("low", 0)
                metric.hallucination_triggers = claims_data.get("hallucination", 0)

        # Read pTCS/SRCS from monitoring data if available
        ptcs_data = self._read_ptcs_for_agent(agent_name)
        if ptcs_data:
            metric.ptcs = ptcs_data.get("ptcs")
            metric.srcs = ptcs_data.get("srcs")
            metric.retry_count = ptcs_data.get("retry_count", 0)

        return metric

    def _find_agent_outputs(self, output_dir: Path, agent_name: str) -> List[Path]:
        """Find output files produced by an agent (read-only glob)."""
        results = []
        if not output_dir.exists():
            return results

        # Agent outputs follow naming conventions like:
        # wave1-literature-search-strategy.md, wave2-theoretical-framework.md
        # Map agent names to likely file patterns
        agent_patterns = {
            "literature-searcher": ["*literature-search*", "*search-strategy*"],
            "seminal-works-analyst": ["*seminal*"],
            "trend-analyst": ["*trend*"],
            "methodology-scanner": ["*methodology-scan*"],
            "theoretical-framework-analyst": ["*theoretical-framework*"],
            "empirical-evidence-analyst": ["*empirical*"],
            "gap-identifier": ["*gap*"],
            "variable-relationship-analyst": ["*variable-relationship*"],
            "critical-reviewer": ["*critical-review*"],
            "methodology-critic": ["*methodology-critic*"],
            "limitation-analyst": ["*limitation*"],
            "future-direction-analyst": ["*future-direction*"],
            "synthesis-agent": ["*synthesis*", "*literature-review-draft*"],
            "conceptual-model-builder": ["*conceptual-model*"],
            "plagiarism-checker": ["*plagiarism*"],
            "unified-srcs-evaluator": ["*srcs*", "*unified-srcs*"],
            "research-synthesizer": ["*research-synth*", "*insights*"],
            "hypothesis-developer": ["*hypothesis*"],
            "research-model-developer": ["*research-model*"],
            "sampling-designer": ["*sampling*"],
            "statistical-planner": ["*statistical*"],
            "thesis-architect": ["*outline*", "*architecture*"],
            "thesis-writer": ["*chapter*", "*thesis-draft*"],
            "thesis-reviewer": ["*review*", "*quality-report*"],
            "publication-strategist": ["*publication*", "*journal*"],
            "manuscript-formatter": ["*manuscript*", "*formatted*"],
        }

        patterns = agent_patterns.get(agent_name, [f"*{agent_name}*"])
        for pattern in patterns:
            results.extend(output_dir.glob(pattern))

        return list(set(results))  # Deduplicate

    def _extract_claims_from_files(self, files: List[Path]) -> Optional[Dict]:
        """Extract claim statistics from agent output files (read-only)."""
        total_claims = 0
        low_confidence = 0
        hallucination = 0

        for f in files:
            if not f.exists() or f.stat().st_size == 0:
                continue
            try:
                content = f.read_text(encoding='utf-8')
                # Count claim markers in GRA-formatted outputs
                total_claims += content.count("claim_type:")
                total_claims += content.count("- id: ")
                # Count low-confidence markers
                low_confidence += content.count("confidence: low")
                low_confidence += content.lower().count("low confidence")
                # Count hallucination-related markers
                hallucination += content.lower().count("unverified")
                hallucination += content.lower().count("hallucination")
            except (OSError, UnicodeDecodeError):
                continue

        if total_claims == 0 and low_confidence == 0:
            return None

        return {
            "total": total_claims,
            "low": low_confidence,
            "hallucination": hallucination,
        }

    def _read_ptcs_for_agent(self, agent_name: str) -> Optional[Dict]:
        """Read pTCS/SRCS data for an agent from monitoring files (read-only)."""
        # Check for monitoring snapshots
        session_dir = self.working_dir / "00-session"

        # Look for confidence monitor snapshots
        for snapshot_file in session_dir.glob("confidence-snapshot*.json"):
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                # Look for agent-specific data
                agents_data = data.get("agents", {})
                if agent_name in agents_data:
                    return agents_data[agent_name]
            except (json.JSONDecodeError, OSError):
                continue

        return None

    # ========================================================================
    # Gate Metrics Collection (Read-Only)
    # ========================================================================

    def _collect_gate_metrics(
        self, phase: Optional[str]
    ) -> Dict[str, GateMetrics]:
        """Collect gate validation results from gate-results.json.

        The gate-automation.py hook saves results to:
            00-session/gate-results.json  ({"gates": [...]})

        Each gate entry has: gate_name, gate_type, timestamp, passed,
        score/srcs_score/ptcs_score, details.
        """
        metrics = {}

        # Primary source: gate-results.json (written by gate-automation.py hook)
        gate_results_file = self.working_dir / "00-session" / "gate-results.json"
        if gate_results_file.exists():
            try:
                with open(gate_results_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                gates_list = data.get("gates", [])
                for gate_data in gates_list:
                    gate_name = gate_data.get("gate_name", "unknown")
                    gate_type = gate_data.get("gate_type", "unknown")

                    # Filter by phase if specified (gates 1-5 are phase1)
                    if phase:
                        gate_num = gate_name.replace("gate", "")
                        if phase == "phase1" and gate_num not in ("1", "2", "3", "4", "5"):
                            continue
                        elif phase != "phase1" and gate_num in ("1", "2", "3", "4", "5"):
                            continue

                    # Extract scores based on gate type
                    ptcs = gate_data.get("ptcs_score")
                    srcs = gate_data.get("srcs_score")
                    score = gate_data.get("score")  # cross_validation uses 'score'

                    details = gate_data.get("details", {})
                    if ptcs is None:
                        ptcs = details.get("ptcs_score")
                    if srcs is None:
                        srcs = details.get("srcs_score", details.get("srcs_threshold"))

                    metric = GateMetrics(
                        gate_id=gate_name,
                        gate_type=gate_type,
                        passed=gate_data.get("passed", False),
                        ptcs=ptcs,
                        srcs=srcs,
                        combined=score,  # consistency_score for cross_validation
                        attempts=1,
                        decision="PASS" if gate_data.get("passed") else "FAIL",
                    )
                    metrics[gate_name] = metric

            except (json.JSONDecodeError, OSError) as e:
                self._log(f"  Warning: Could not read {gate_results_file}: {e}")

        return metrics

    # ========================================================================
    # Overall Summary Calculation
    # ========================================================================

    def _calculate_overall(
        self,
        agent_metrics: Dict[str, AgentMetrics],
        gate_metrics: Dict[str, GateMetrics],
    ) -> Dict[str, Any]:
        """Calculate overall summary statistics."""
        if not agent_metrics:
            return {"status": "no_data"}

        # Agent-level stats
        ptcs_scores = [
            m.ptcs for m in agent_metrics.values()
            if m.ptcs is not None
        ]
        srcs_scores = [
            m.srcs for m in agent_metrics.values()
            if m.srcs is not None
        ]
        total_retries = sum(m.retry_count for m in agent_metrics.values())
        success_count = sum(1 for m in agent_metrics.values() if m.success)
        total_agents = len(agent_metrics)

        # Gate-level stats
        gate_count = len(gate_metrics)
        gate_passed = sum(1 for g in gate_metrics.values() if g.passed)

        return {
            "total_agents": total_agents,
            "successful_agents": success_count,
            "completion_rate": success_count / total_agents if total_agents > 0 else 0,
            "avg_ptcs": sum(ptcs_scores) / len(ptcs_scores) if ptcs_scores else None,
            "avg_srcs": sum(srcs_scores) / len(srcs_scores) if srcs_scores else None,
            "total_retries": total_retries,
            "total_gates": gate_count,
            "gates_passed": gate_passed,
            "gate_pass_rate": gate_passed / gate_count if gate_count > 0 else None,
        }

    # ========================================================================
    # Utilities (Read-Only)
    # ========================================================================

    def _load_session(self):
        """Load session.json (read-only)."""
        session_file = self.working_dir / "00-session" / "session.json"
        if session_file.exists():
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
                self._log(f"Loaded session: {session_file}")
            except (json.JSONDecodeError, OSError) as e:
                self._log(f"Warning: Could not load session: {e}")
        else:
            self._log("Warning: session.json not found")

    def _get_target_groups(
        self, phase: Optional[str], wave: Optional[str]
    ) -> Dict[str, List[str]]:
        """Get agent groups to analyze based on scope.

        For phase2, determines research type from session.json to select
        the correct agent sub-group (quantitative/qualitative/mixed).
        """
        if phase is None and wave is None:
            # For full analysis, determine phase2 research type from session
            result = {}
            for group_name, agents in AGENT_REGISTRY.items():
                if group_name.startswith("phase2-"):
                    # Only include matching research type
                    research_type = self._get_research_type()
                    if research_type and research_type in group_name:
                        result[group_name] = agents
                    elif not research_type:
                        # If unknown, include all phase2 groups
                        result[group_name] = agents
                else:
                    result[group_name] = agents
            return result

        result = {}
        for group_name, agents in AGENT_REGISTRY.items():
            if phase and not group_name.startswith(phase):
                continue
            if wave and wave not in group_name:
                continue
            result[group_name] = agents

        return result

    def _get_research_type(self) -> Optional[str]:
        """Read research type from session.json (read-only)."""
        research_type = self.session_data.get("research_type", "")
        type_map = {
            "quantitative": "quantitative",
            "qualitative": "qualitative",
            "mixed": "mixed",
        }
        return type_map.get(research_type)

    def _log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for performance collector."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Performance Collector - Read-only metrics gathering"
    )
    parser.add_argument(
        "--phase", type=str, default=None,
        help="Phase to analyze (e.g., 'phase1')"
    )
    parser.add_argument(
        "--wave", type=str, default=None,
        help="Wave to analyze (e.g., 'wave1')"
    )
    parser.add_argument(
        "--working-dir", type=str, default=None,
        help="Working directory (auto-detected from session if omitted)"
    )
    parser.add_argument(
        "--quiet", action="store_true",
        help="Suppress verbose output"
    )
    parser.add_argument(
        "--test", action="store_true",
        help="Run with test data"
    )

    args = parser.parse_args()

    if args.test:
        print("\n" + "=" * 70)
        print("Performance Collector - Test Mode")
        print("=" * 70)

        # Create a mock report
        report = PerformanceReport(
            run_id="test-001",
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            version=VERSION,
            phase="phase1",
            wave="wave1",
            agents={
                "literature-searcher": AgentMetrics(
                    agent_name="literature-searcher",
                    phase="phase1", wave="wave1",
                    ptcs=82.5, srcs=78.0,
                    retry_count=0, success=True,
                    output_file_count=2, total_output_length=4500,
                ).to_dict()
            },
            gates={
                "wave-1": GateMetrics(
                    gate_id="wave-1", gate_type="wave",
                    passed=True, ptcs=80.0, srcs=77.0,
                    combined=78.8, attempts=1, decision="PASS",
                ).to_dict()
            },
            overall={
                "total_agents": 4, "successful_agents": 4,
                "completion_rate": 1.0, "avg_ptcs": 79.3,
                "avg_srcs": 77.8, "total_retries": 0,
            },
        )
        print(json.dumps(report.to_dict(), indent=2))
        return 0

    # Real collection
    try:
        if args.working_dir:
            working_dir = Path(args.working_dir).resolve()
        else:
            working_dir = get_working_dir_from_session()

        collector = PerformanceCollector(
            working_dir=working_dir,
            verbose=not args.quiet,
        )
        report = collector.collect(phase=args.phase, wave=args.wave)
        output_path = collector.save_report(report)

        print(f"\nPerformance report saved: {output_path}")
        return 0

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Error collecting metrics: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
