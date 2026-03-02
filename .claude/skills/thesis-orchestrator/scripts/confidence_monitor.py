#!/usr/bin/env python3
"""Confidence Monitor: Real-time pTCS + SRCS Dashboard.

This module provides real-time monitoring and visualization of confidence scores
throughout the thesis workflow.

Features:
- Real-time pTCS tracking (all agents)
- SRCS gate status monitoring
- Visual progress bars and color coding
- Alert system for low-confidence outputs
- Live dashboard display

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from ptcs_calculator import PTCSCalculator, ClaimPTCS, AgentPTCS, PhasePTCS
from gate_controller import GateController, GateStatus
from workflow_constants import ALERT_THRESHOLDS, PTCS_COLOR_BANDS


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class MonitorAlert:
    """Alert for low-confidence output."""

    alert_type: str  # "low_claim" | "low_agent" | "gate_fail"
    severity: str  # "info" | "warning" | "critical"
    message: str
    details: Dict[str, Any]
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MonitorSnapshot:
    """Snapshot of current monitoring state."""

    # Project info
    project_name: str
    current_phase: int
    current_step: Optional[int]

    # Real-time pTCS
    total_claims: int
    low_confidence_claims: int
    medium_confidence_claims: int
    good_confidence_claims: int
    high_confidence_claims: int

    # Agent status
    completed_agents: int
    total_agents_expected: int
    current_agent: Optional[str]
    current_agent_ptcs: Optional[float]

    # Gate status
    passed_gates: int
    failed_gates: int
    pending_gates: int
    current_gate: Optional[str]

    # Alerts
    active_alerts: List[MonitorAlert]

    # Timestamp
    timestamp: str

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'active_alerts': [a.to_dict() for a in self.active_alerts]
        }


# ============================================================================
# Confidence Monitor
# ============================================================================

class ConfidenceMonitor:
    """Real-time confidence monitoring system.

    Tracks:
    - Claim-level pTCS (all claims)
    - Agent-level pTCS (all agents)
    - Phase-level pTCS (all phases)
    - Gate status (all gates)
    - Active alerts
    """

    # Alert thresholds (from SOT-A)
    ALERT_THRESHOLDS = ALERT_THRESHOLDS

    def __init__(
        self,
        project_name: str,
        working_dir: Path,
        gate_controller: Optional[GateController] = None
    ):
        """Initialize confidence monitor.

        Args:
            project_name: Project name
            working_dir: Working directory
            gate_controller: Gate controller (optional)
        """
        self.project_name = project_name
        self.working_dir = Path(working_dir)
        self.gate_controller = gate_controller
        self.calc = PTCSCalculator()

        # Tracking
        self.claim_history: List[ClaimPTCS] = []
        self.agent_history: List[AgentPTCS] = []
        self.phase_history: List[PhasePTCS] = []
        self.alerts: List[MonitorAlert] = []

        # Current state
        self.current_phase = 0
        self.current_step: Optional[int] = None
        self.current_agent: Optional[str] = None

    # ========================================================================
    # Tracking Methods
    # ========================================================================

    def track_claim(self, claim_ptcs: ClaimPTCS):
        """Track a claim pTCS score.

        Args:
            claim_ptcs: ClaimPTCS object
        """
        self.claim_history.append(claim_ptcs)

        # Check for alerts
        if claim_ptcs.ptcs < self.ALERT_THRESHOLDS['claim_critical']:
            self._add_alert(
                alert_type="low_claim",
                severity="critical",
                message=f"Critical: Claim {claim_ptcs.claim_id} has very low confidence",
                details={
                    'claim_id': claim_ptcs.claim_id,
                    'claim_text': claim_ptcs.claim_text,
                    'ptcs': claim_ptcs.ptcs,
                    'threshold': self.ALERT_THRESHOLDS['claim_critical']
                }
            )
        elif claim_ptcs.ptcs < self.ALERT_THRESHOLDS['claim_warning']:
            self._add_alert(
                alert_type="low_claim",
                severity="warning",
                message=f"Warning: Claim {claim_ptcs.claim_id} has low confidence",
                details={
                    'claim_id': claim_ptcs.claim_id,
                    'claim_text': claim_ptcs.claim_text,
                    'ptcs': claim_ptcs.ptcs,
                    'threshold': self.ALERT_THRESHOLDS['claim_warning']
                }
            )

    def track_agent(self, agent_ptcs: AgentPTCS):
        """Track an agent pTCS score.

        Args:
            agent_ptcs: AgentPTCS object
        """
        self.agent_history.append(agent_ptcs)
        self.current_agent = agent_ptcs.agent_name

        # Check for alerts
        if agent_ptcs.ptcs < self.ALERT_THRESHOLDS['agent_critical']:
            self._add_alert(
                alert_type="low_agent",
                severity="critical",
                message=f"Critical: Agent {agent_ptcs.agent_name} has very low confidence",
                details={
                    'agent_name': agent_ptcs.agent_name,
                    'ptcs': agent_ptcs.ptcs,
                    'low_claims': agent_ptcs.low_confidence_claims,
                    'total_claims': agent_ptcs.total_claims,
                    'threshold': self.ALERT_THRESHOLDS['agent_critical']
                }
            )
        elif agent_ptcs.ptcs < self.ALERT_THRESHOLDS['agent_warning']:
            self._add_alert(
                alert_type="low_agent",
                severity="warning",
                message=f"Warning: Agent {agent_ptcs.agent_name} has low confidence",
                details={
                    'agent_name': agent_ptcs.agent_name,
                    'ptcs': agent_ptcs.ptcs,
                    'low_claims': agent_ptcs.low_confidence_claims,
                    'total_claims': agent_ptcs.total_claims,
                    'threshold': self.ALERT_THRESHOLDS['agent_warning']
                }
            )

    def track_phase(self, phase_ptcs: PhasePTCS):
        """Track a phase pTCS score.

        Args:
            phase_ptcs: PhasePTCS object
        """
        self.phase_history.append(phase_ptcs)
        self.current_phase = phase_ptcs.phase_number

    def _add_alert(
        self,
        alert_type: str,
        severity: str,
        message: str,
        details: Dict[str, Any]
    ):
        """Add alert to active alerts.

        Args:
            alert_type: Type of alert
            severity: Severity level
            message: Alert message
            details: Additional details
        """
        alert = MonitorAlert(
            alert_type=alert_type,
            severity=severity,
            message=message,
            details=details,
            timestamp=datetime.now().isoformat()
        )
        self.alerts.append(alert)

    # ========================================================================
    # Dashboard Generation
    # ========================================================================

    def generate_dashboard(self) -> str:
        """Generate real-time dashboard display.

        Returns:
            Dashboard string (formatted text)
        """
        # Get current statistics
        snapshot = self.get_snapshot()

        # Build dashboard
        lines = []
        lines.append("═" * 70)
        lines.append("           THESIS CONFIDENCE MONITOR (pTCS + SRCS)")
        lines.append("═" * 70)
        lines.append("")

        # Project info
        lines.append(f"Project: {self.project_name}")
        lines.append(f"Current Phase: {snapshot.current_phase}")
        if snapshot.current_agent:
            lines.append(f"Current Agent: {snapshot.current_agent}")
            if snapshot.current_agent_ptcs:
                emoji = self.calc.get_color_emoji(
                    self._get_color_from_ptcs(snapshot.current_agent_ptcs)
                )
                lines.append(f"Agent pTCS: {snapshot.current_agent_ptcs}/100 {emoji}")
        lines.append("")

        # Real-time pTCS Status
        lines.append("─" * 70)
        lines.append("📊 Real-time pTCS Status (Predictive)")
        lines.append("─" * 70)

        # Confidence distribution
        total_claims = snapshot.total_claims
        if total_claims > 0:
            lines.append(f"Total Claims: {total_claims}")
            lines.append(f"  🔴 Low (0-60):     {snapshot.low_confidence_claims:3d} "
                        f"({snapshot.low_confidence_claims/total_claims*100:5.1f}%)")
            lines.append(f"  🟡 Medium (61-70): {snapshot.medium_confidence_claims:3d} "
                        f"({snapshot.medium_confidence_claims/total_claims*100:5.1f}%)")
            lines.append(f"  🔵 Good (71-85):   {snapshot.good_confidence_claims:3d} "
                        f"({snapshot.good_confidence_claims/total_claims*100:5.1f}%)")
            lines.append(f"  🟢 High (86-100):  {snapshot.high_confidence_claims:3d} "
                        f"({snapshot.high_confidence_claims/total_claims*100:5.1f}%)")
        else:
            lines.append("No claims tracked yet")

        lines.append("")

        # Agent progress
        if snapshot.total_agents_expected > 0:
            progress_pct = (snapshot.completed_agents / snapshot.total_agents_expected) * 100
            bar_length = 40
            filled_length = int(bar_length * snapshot.completed_agents / snapshot.total_agents_expected)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)

            lines.append(f"Agent Progress: [{bar}] {progress_pct:.1f}%")
            lines.append(f"Completed: {snapshot.completed_agents}/{snapshot.total_agents_expected} agents")
        else:
            lines.append("Agent Progress: Not started")

        lines.append("")

        # Gate Status
        lines.append("─" * 70)
        lines.append("🎯 SRCS Gate Status (Evaluative)")
        lines.append("─" * 70)

        if self.gate_controller:
            report = self.gate_controller.get_workflow_status(self.project_name)

            # Wave gates
            lines.append("Wave Gates:")
            for gate_num in [1, 2, 3]:
                gate_id = f"wave-{gate_num}"
                gate_status = self.gate_controller.get_gate_status(gate_id)

                if gate_status.status == "passed":
                    lines.append(f"  Gate {gate_num}: ✅ PASSED "
                               f"(pTCS: {gate_status.ptcs:.1f}, SRCS: {gate_status.srcs:.1f})")
                elif gate_status.status == "failed":
                    lines.append(f"  Gate {gate_num}: ❌ FAILED "
                               f"(pTCS: {gate_status.ptcs:.1f}, SRCS: {gate_status.srcs:.1f})")
                elif gate_status.status == "in_progress":
                    lines.append(f"  Gate {gate_num}: ⏳ IN PROGRESS")
                else:
                    lines.append(f"  Gate {gate_num}: ⏭️  PENDING")

            lines.append("")

            # Phase gates
            lines.append("Phase Gates:")
            for phase_num in range(5):
                gate_id = f"phase-{phase_num}"
                gate_status = self.gate_controller.get_gate_status(gate_id)
                phase_names = ["Init", "Literature", "Design", "Writing", "Publication"]
                phase_name = phase_names[phase_num]

                if gate_status.status == "passed":
                    lines.append(f"  Phase {phase_num} ({phase_name}): ✅ PASSED "
                               f"(pTCS: {gate_status.ptcs:.1f}, SRCS: {gate_status.srcs:.1f})")
                elif gate_status.status == "failed":
                    lines.append(f"  Phase {phase_num} ({phase_name}): ❌ FAILED "
                               f"(pTCS: {gate_status.ptcs:.1f}, SRCS: {gate_status.srcs:.1f})")
                elif gate_status.status == "in_progress":
                    lines.append(f"  Phase {phase_num} ({phase_name}): ⏳ IN PROGRESS")
                else:
                    lines.append(f"  Phase {phase_num} ({phase_name}): ⏭️  PENDING")
        else:
            lines.append("Gate controller not initialized")

        lines.append("")

        # Alerts
        if snapshot.active_alerts:
            lines.append("─" * 70)
            lines.append("⚠️  Active Alerts")
            lines.append("─" * 70)

            # Show recent alerts (last 5)
            recent_alerts = snapshot.active_alerts[-5:]
            for i, alert in enumerate(recent_alerts, 1):
                severity_emoji = {
                    'info': 'ℹ️',
                    'warning': '⚠️',
                    'critical': '🔴'
                }[alert.severity]

                lines.append(f"{i}. {severity_emoji} {alert.message}")

            if len(snapshot.active_alerts) > 5:
                lines.append(f"\n... and {len(snapshot.active_alerts) - 5} more alerts")

            lines.append("")

        lines.append("─" * 70)
        lines.append(f"Last Updated: {snapshot.timestamp}")
        lines.append("═" * 70)

        return "\n".join(lines)

    def _get_color_from_ptcs(self, ptcs: float) -> str:
        """Get color coding from pTCS score (SOT-A: PTCS_COLOR_BANDS)."""
        for color, (low, high) in PTCS_COLOR_BANDS.items():
            if low <= ptcs <= high:
                return color
        return 'red'

    # ========================================================================
    # Snapshot
    # ========================================================================

    def get_snapshot(self) -> MonitorSnapshot:
        """Get current monitoring snapshot.

        Returns:
            MonitorSnapshot with current state
        """
        # Claim statistics
        total_claims = len(self.claim_history)
        # Binning uses SOT-A PTCS_COLOR_BANDS thresholds
        _r = PTCS_COLOR_BANDS["red"]
        _y = PTCS_COLOR_BANDS["yellow"]
        _c = PTCS_COLOR_BANDS["cyan"]
        _g = PTCS_COLOR_BANDS["green"]
        low_count = sum(1 for c in self.claim_history if _r[0] <= c.ptcs <= _r[1])
        medium_count = sum(1 for c in self.claim_history if _y[0] <= c.ptcs <= _y[1])
        good_count = sum(1 for c in self.claim_history if _c[0] <= c.ptcs <= _c[1])
        high_count = sum(1 for c in self.claim_history if _g[0] <= c.ptcs <= _g[1])

        # Agent statistics
        completed_agents = len(self.agent_history)
        total_agents_expected = 41  # Total agents in workflow

        # Current agent pTCS
        current_agent_ptcs = None
        if self.agent_history:
            current_agent_ptcs = self.agent_history[-1].ptcs

        # Gate statistics
        if self.gate_controller:
            report = self.gate_controller.get_workflow_status(self.project_name)
            passed_gates = report.passed_gates
            failed_gates = report.failed_gates
            pending_gates = report.pending_gates
            current_gate = report.current_gate
        else:
            passed_gates = 0
            failed_gates = 0
            pending_gates = 8
            current_gate = None

        return MonitorSnapshot(
            project_name=self.project_name,
            current_phase=self.current_phase,
            current_step=self.current_step,
            total_claims=total_claims,
            low_confidence_claims=low_count,
            medium_confidence_claims=medium_count,
            good_confidence_claims=good_count,
            high_confidence_claims=high_count,
            completed_agents=completed_agents,
            total_agents_expected=total_agents_expected,
            current_agent=self.current_agent,
            current_agent_ptcs=current_agent_ptcs,
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            pending_gates=pending_gates,
            current_gate=current_gate,
            active_alerts=self.alerts,
            timestamp=datetime.now().isoformat()
        )

    # ========================================================================
    # Save/Load
    # ========================================================================

    def save_snapshot(self, output_path: Path):
        """Save monitoring snapshot to JSON file.

        Args:
            output_path: Path to save snapshot
        """
        snapshot = self.get_snapshot()

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(snapshot.to_dict(), f, indent=2)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for confidence monitor."""
    import argparse

    parser = argparse.ArgumentParser(description="Confidence Monitor")
    parser.add_argument("--test", action="store_true", help="Run test monitor")

    args = parser.parse_args()

    if args.test:
        # Test monitoring

        print("\n" + "="*70)
        print("Confidence Monitor Test")
        print("="*70)

        # Create monitor
        monitor = ConfidenceMonitor(
            project_name="test-project",
            working_dir=Path.cwd()
        )

        # Simulate some claims
        for i in range(10):
            claim_ptcs = ClaimPTCS(
                claim_id=f"TEST-{i:03d}",
                claim_text=f"Test claim {i}",
                claim_type="THEORETICAL",
                ptcs=50 + (i * 5),  # 50, 55, 60, ..., 95
                source_quality=20.0,
                claim_type_appropriate=12.5,
                uncertainty_acknowledgment=10.0,
                grounding_depth=7.5,
                color='yellow',
                confidence_level='medium',
                timestamp=datetime.now().isoformat()
            )
            monitor.track_claim(claim_ptcs)

        # Simulate some agents
        for i in range(3):
            agent_ptcs = AgentPTCS(
                agent_name=f"test-agent-{i}",
                ptcs=60 + (i * 10),  # 60, 70, 80
                avg_claim_ptcs=30.0,
                coverage_completeness=20.0,
                cross_reference_consistency=10.0,
                hallucination_firewall_pass=10.0,
                total_claims=10,
                low_confidence_claims=2 - i,
                medium_confidence_claims=3,
                good_confidence_claims=3,
                high_confidence_claims=2 + i,
                color='cyan',
                confidence_level='good',
                timestamp=datetime.now().isoformat()
            )
            monitor.track_agent(agent_ptcs)

        # Generate and display dashboard
        dashboard = monitor.generate_dashboard()
        print(dashboard)

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
