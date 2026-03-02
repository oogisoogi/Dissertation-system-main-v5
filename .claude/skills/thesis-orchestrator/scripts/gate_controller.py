#!/usr/bin/env python3
"""Gate Controller: Automated Gate Validation.

This module provides automated gate control for the thesis workflow:
- Wave Gates (Phase 1): Gate 1, 2, 3
- Phase Gates (Phase 0-4): Phase completion validation

Gate Logic:
1. Agent executes → pTCS enforcement (retry-until-pass)
2. Wave/Phase completes → Dual validation (pTCS + SRCS)
3. Gate passed → Continue to next stage
4. Gate failed → Automatic rework

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from ptcs_calculator import PTCSCalculator
from ptcs_enforcer import PTCSEnforcer, EnforcementResult
from dual_confidence_system import (
    DualConfidenceCalculator,
    DualConfidenceValidator,
    GateDecision
)
from workflow_constants import MAX_RETRIES_WAVE, MAX_RETRIES_PHASE


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class GateStatus:
    """Status of a gate (Wave or Phase)."""

    gate_id: str  # "wave-1", "phase-0", etc.
    gate_type: str  # "wave" | "phase"
    gate_number: int

    # Status
    status: str  # "pending" | "in_progress" | "passed" | "failed"
    attempts: int

    # Scores (if evaluated)
    ptcs: Optional[float] = None
    srcs: Optional[float] = None
    combined: Optional[float] = None

    # Decision (if evaluated)
    decision: Optional[str] = None
    reasoning: Optional[str] = None

    # Timestamps
    started_at: Optional[str] = None
    completed_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkflowGateReport:
    """Overall gate status report."""

    project_name: str

    # All gates
    gates: List[GateStatus]

    # Summary
    total_gates: int
    passed_gates: int
    failed_gates: int
    pending_gates: int

    # Current status
    current_gate: Optional[str] = None
    workflow_status: str = "in_progress"  # "in_progress" | "completed" | "failed"

    # Timestamp
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            **asdict(self),
            'gates': [g.to_dict() for g in self.gates]
        }


# ============================================================================
# Gate Controller
# ============================================================================

class GateController:
    """Automated gate controller for thesis workflow.

    Manages:
    - Wave Gates (Phase 1): Gates 1-4 (after Waves 1-4)
    - Phase Gates (Phase 0-4): Phase completion validation

    Wave numbering follows the unified 1-5 system:
      Wave 1: Literature search (4 agents) → Gate 1
      Wave 2: Theory/Empirical analysis (4 agents) → Gate 2
      Wave 3: Critical review (4 agents) → Gate 3
      Wave 4: Synthesis (2 agents) → Gate 4
      Wave 5: Quality assurance (no gate, final output)
    """

    # Gate definitions (unified Wave 1-5 system, 4 gates)
    WAVE_GATES = {
        1: {
            'wave': 1,
            'name': 'Cross-Validation Gate 1',
            'description': 'Wave 1 완료 후 (문헌탐색 4개 에이전트)',
        },
        2: {
            'wave': 2,
            'name': 'Cross-Validation Gate 2',
            'description': 'Wave 2 완료 후 (이론/실증 4개 에이전트)',
        },
        3: {
            'wave': 3,
            'name': 'Cross-Validation Gate 3',
            'description': 'Wave 3 완료 후 (비판적 검토 4개 에이전트)',
        },
        4: {
            'wave': 4,
            'name': 'Synthesis Gate',
            'description': 'Wave 4 완료 후 (종합 2개 에이전트)',
        },
    }

    PHASE_GATES = {
        0: {'name': 'Initialization Gate', 'critical_steps': [1, 7]},
        1: {'name': 'Literature Review Gate', 'critical_steps': list(range(19, 89))},
        2: {'name': 'Research Design Gate', 'critical_steps': [108]},
        3: {'name': 'Thesis Writing Gate', 'critical_steps': [111, 115, 117, 119, 121, 123, 129, 130]},
        4: {'name': 'Publication Strategy Gate', 'critical_steps': [136, 138, 139]}
    }

    def __init__(
        self,
        working_dir: Path,
        dual_validator: Optional[DualConfidenceValidator] = None,
        verbose: bool = True
    ):
        """Initialize gate controller.

        Args:
            working_dir: Working directory (project root)
            dual_validator: Dual confidence validator (optional)
            verbose: Print detailed logs (default True)
        """
        self.working_dir = Path(working_dir)
        self.dual_validator = dual_validator or DualConfidenceValidator()
        self.verbose = verbose

        # Gate status tracking
        self.gate_statuses: Dict[str, GateStatus] = {}

        # Initialize all gates as pending
        self._initialize_gates()

    # ========================================================================
    # Initialization
    # ========================================================================

    def _initialize_gates(self):
        """Initialize all gate statuses as pending."""

        # Wave gates (1-4, matching unified Wave 1-5 system)
        for gate_num in [1, 2, 3, 4]:
            gate_id = f"wave-{gate_num}"
            self.gate_statuses[gate_id] = GateStatus(
                gate_id=gate_id,
                gate_type="wave",
                gate_number=gate_num,
                status="pending",
                attempts=0
            )

        # Phase gates
        for phase_num in range(5):
            gate_id = f"phase-{phase_num}"
            self.gate_statuses[gate_id] = GateStatus(
                gate_id=gate_id,
                gate_type="phase",
                gate_number=phase_num,
                status="pending",
                attempts=0
            )

    # ========================================================================
    # Wave Gate Validation
    # ========================================================================

    def validate_wave_gate(
        self,
        gate_number: int,
        wave_ptcs: float,
        wave_srcs: float,
        auto_retry: bool = True,
        max_retries: int = MAX_RETRIES_WAVE
    ) -> GateDecision:
        """Validate Wave Gate with dual confidence.

        Args:
            gate_number: Gate number (1-3)
            wave_ptcs: Wave-level pTCS score
            wave_srcs: Wave-level SRCS score
            auto_retry: Automatically retry if failed (default True)
            max_retries: Maximum retry attempts (from SOT-A)

        Returns:
            GateDecision

        Raises:
            RuntimeError: If gate fails after max retries
        """
        gate_id = f"wave-{gate_number}"
        gate_status = self.gate_statuses[gate_id]

        self._log(f"\n{'='*70}")
        self._log(f"🚪 WAVE GATE {gate_number} VALIDATION")
        self._log(f"{'='*70}")
        self._log(f"Gate: {self.WAVE_GATES[gate_number]['name']}")
        self._log(f"Wave: {self.WAVE_GATES[gate_number]['wave']}")
        self._log("")

        # Mark as in progress
        gate_status.status = "in_progress"
        gate_status.started_at = datetime.now().isoformat()
        gate_status.attempts += 1

        # Validate using dual confidence
        try:
            decision = self.dual_validator.dual_calculator.validate_wave_gate(
                wave_number=gate_number,
                wave_ptcs=wave_ptcs,
                wave_srcs=wave_srcs
            )

            # Update gate status
            gate_status.ptcs = wave_ptcs
            gate_status.srcs = wave_srcs
            gate_status.combined = decision.combined
            gate_status.decision = decision.decision
            gate_status.reasoning = decision.reasoning

            # Check if passed
            if decision.passed:
                # PASS
                gate_status.status = "passed"
                gate_status.completed_at = datetime.now().isoformat()

                self._log(f"✅ GATE {gate_number} PASSED")
                self._log(f"   pTCS: {wave_ptcs}/100")
                self._log(f"   SRCS: {wave_srcs}/100")
                self._log(f"   Combined: {decision.combined}/100")
                self._log(f"   Decision: {decision.decision}")
                self._log("")

                return decision

            else:
                # FAIL
                self._log(f"❌ GATE {gate_number} FAILED")
                self._log(f"   pTCS: {wave_ptcs}/100")
                self._log(f"   SRCS: {wave_srcs}/100")
                self._log(f"   Decision: {decision.decision}")
                self._log(f"   Reasoning: {decision.reasoning}")
                self._log("")

                # Check if should retry
                if auto_retry and gate_status.attempts < max_retries:
                    self._log(f"⚠️  Auto-retry enabled. Retrying wave...")
                    self._log(f"   Attempts: {gate_status.attempts}/{max_retries}")
                    self._log("")

                    # Mark as failed but will retry
                    gate_status.status = "failed"

                    # Raise exception to trigger retry
                    raise RuntimeError(
                        f"Wave Gate {gate_number} failed. Auto-retry triggered."
                    )

                else:
                    # Max retries exceeded or auto-retry disabled
                    gate_status.status = "failed"
                    gate_status.completed_at = datetime.now().isoformat()

                    raise RuntimeError(
                        f"Wave Gate {gate_number} failed after "
                        f"{gate_status.attempts} attempts. "
                        f"Reasoning: {decision.reasoning}"
                    )

        except Exception as e:
            gate_status.status = "failed"
            gate_status.completed_at = datetime.now().isoformat()
            raise

    # ========================================================================
    # Phase Gate Validation
    # ========================================================================

    def validate_phase_gate(
        self,
        phase_number: int,
        phase_ptcs: float,
        phase_srcs: float,
        auto_retry: bool = True,
        max_retries: int = MAX_RETRIES_PHASE
    ) -> GateDecision:
        """Validate Phase Gate with dual confidence.

        Args:
            phase_number: Phase number (0-4)
            phase_ptcs: Phase-level pTCS score
            phase_srcs: Phase-level SRCS score
            auto_retry: Automatically retry if failed (default True)
            max_retries: Maximum retry attempts (from SOT-A)

        Returns:
            GateDecision

        Raises:
            RuntimeError: If gate fails after max retries
        """
        gate_id = f"phase-{phase_number}"
        gate_status = self.gate_statuses[gate_id]

        self._log(f"\n{'='*70}")
        self._log(f"🚪 PHASE {phase_number} GATE VALIDATION")
        self._log(f"{'='*70}")
        self._log(f"Phase: {self.PHASE_GATES[phase_number]['name']}")
        self._log("")

        # Mark as in progress
        gate_status.status = "in_progress"
        gate_status.started_at = datetime.now().isoformat()
        gate_status.attempts += 1

        # Validate using dual confidence
        try:
            decision = self.dual_validator.dual_calculator.validate_phase_gate(
                phase_number=phase_number,
                phase_ptcs=phase_ptcs,
                phase_srcs=phase_srcs
            )

            # Update gate status
            gate_status.ptcs = phase_ptcs
            gate_status.srcs = phase_srcs
            gate_status.combined = decision.combined
            gate_status.decision = decision.decision
            gate_status.reasoning = decision.reasoning

            # Check decision
            if decision.decision == "PASS":
                # PASS
                gate_status.status = "passed"
                gate_status.completed_at = datetime.now().isoformat()

                self._log(f"✅ PHASE {phase_number} GATE PASSED")
                self._log(f"   pTCS: {phase_ptcs}/100")
                self._log(f"   SRCS: {phase_srcs}/100")
                self._log(f"   Combined: {decision.combined}/100")
                self._log("")

                return decision

            elif decision.decision == "MANUAL_REVIEW":
                # MANUAL REVIEW required
                gate_status.status = "passed_with_caution"  # Distinct from clean "passed"
                gate_status.completed_at = datetime.now().isoformat()

                self._log(f"⚠️  PHASE {phase_number} GATE: MANUAL REVIEW REQUIRED")
                self._log(f"   pTCS: {phase_ptcs}/100 (passed)")
                self._log(f"   SRCS: {phase_srcs}/100 (below threshold)")
                self._log(f"   Reasoning: {decision.reasoning}")
                self._log(f"   → Proceeding with caution")
                self._log("")

                return decision

            else:
                # FAIL
                self._log(f"❌ PHASE {phase_number} GATE FAILED")
                self._log(f"   pTCS: {phase_ptcs}/100")
                self._log(f"   SRCS: {phase_srcs}/100")
                self._log(f"   Decision: {decision.decision}")
                self._log(f"   Reasoning: {decision.reasoning}")
                self._log("")

                # Check if should retry
                if auto_retry and gate_status.attempts < max_retries:
                    self._log(f"⚠️  Auto-retry enabled. Retrying phase...")
                    self._log(f"   Attempts: {gate_status.attempts}/{max_retries}")
                    self._log("")

                    gate_status.status = "failed"

                    raise RuntimeError(
                        f"Phase {phase_number} gate failed. Auto-retry triggered."
                    )

                else:
                    # Max retries exceeded
                    gate_status.status = "failed"
                    gate_status.completed_at = datetime.now().isoformat()

                    raise RuntimeError(
                        f"Phase {phase_number} gate failed after "
                        f"{gate_status.attempts} attempts. "
                        f"Reasoning: {decision.reasoning}"
                    )

        except Exception as e:
            gate_status.status = "failed"
            gate_status.completed_at = datetime.now().isoformat()
            raise

    # ========================================================================
    # Status Reporting
    # ========================================================================

    def get_gate_status(self, gate_id: str) -> GateStatus:
        """Get status of a specific gate.

        Args:
            gate_id: Gate ID (e.g., "wave-1", "phase-0")

        Returns:
            GateStatus
        """
        return self.gate_statuses.get(gate_id)

    def get_workflow_status(self, project_name: str) -> WorkflowGateReport:
        """Get overall workflow gate status.

        Args:
            project_name: Project name

        Returns:
            WorkflowGateReport with all gate statuses
        """
        # Collect all gates
        all_gates = list(self.gate_statuses.values())

        # Count by status (passed_with_caution counts as passed)
        total_gates = len(all_gates)
        passed_gates = sum(1 for g in all_gates if g.status in ("passed", "passed_with_caution"))
        failed_gates = sum(1 for g in all_gates if g.status == "failed")
        pending_gates = sum(1 for g in all_gates if g.status == "pending")

        # Find current gate (first non-passed)
        current_gate = None
        for gate in all_gates:
            if gate.status != "passed":
                current_gate = gate.gate_id
                break

        # Determine workflow status
        if failed_gates > 0:
            workflow_status = "failed"
        elif passed_gates == total_gates:
            workflow_status = "completed"
        else:
            workflow_status = "in_progress"

        return WorkflowGateReport(
            project_name=project_name,
            gates=all_gates,
            total_gates=total_gates,
            passed_gates=passed_gates,
            failed_gates=failed_gates,
            pending_gates=pending_gates,
            current_gate=current_gate,
            workflow_status=workflow_status
        )

    def save_workflow_status(
        self,
        project_name: str,
        output_path: Path
    ):
        """Save workflow status to JSON file.

        Args:
            project_name: Project name
            output_path: Path to save status
        """
        report = self.get_workflow_status(project_name)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)

        self._log(f"\n📄 Workflow status saved: {output_path}")

    # ========================================================================
    # Utilities
    # ========================================================================

    def _log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for gate controller."""
    import argparse

    parser = argparse.ArgumentParser(description="Gate Controller")
    parser.add_argument("--test", action="store_true", help="Run test validation")

    args = parser.parse_args()

    if args.test:
        # Test gate validation

        print("\n" + "="*70)
        print("Gate Controller Test")
        print("="*70)

        # Create controller
        controller = GateController(
            working_dir=Path.cwd(),
            verbose=True
        )

        # Test 1: Wave Gate 1 (Pass)
        print("\n[Test 1] Wave Gate 1 - Both scores pass")
        print("─"*70)
        try:
            decision1 = controller.validate_wave_gate(
                gate_number=1,
                wave_ptcs=82,
                wave_srcs=78,
                auto_retry=False
            )
            print(f"✅ TEST 1 PASSED: {decision1.decision}")
        except Exception as e:
            print(f"❌ TEST 1 FAILED: {e}")

        # Test 2: Wave Gate 2 (pTCS fail)
        print("\n[Test 2] Wave Gate 2 - pTCS fails (강한 기준)")
        print("─"*70)
        try:
            decision2 = controller.validate_wave_gate(
                gate_number=2,
                wave_ptcs=68,  # Below threshold (70)
                wave_srcs=80,
                auto_retry=False
            )
            print(f"❌ TEST 2 UNEXPECTED PASS")
        except RuntimeError as e:
            print(f"✅ TEST 2 PASSED (expected failure)")

        # Test 3: Phase Gate 0 (Pass)
        print("\n[Test 3] Phase Gate 0 - Both scores pass")
        print("─"*70)
        try:
            decision3 = controller.validate_phase_gate(
                phase_number=0,
                phase_ptcs=85,
                phase_srcs=80,
                auto_retry=False
            )
            print(f"✅ TEST 3 PASSED: {decision3.decision}")
        except Exception as e:
            print(f"❌ TEST 3 FAILED: {e}")

        # Test 4: Get workflow status
        print("\n[Test 4] Workflow Status Report")
        print("─"*70)
        report = controller.get_workflow_status("test-project")
        print(f"Total Gates: {report.total_gates}")
        print(f"Passed: {report.passed_gates}")
        print(f"Failed: {report.failed_gates}")
        print(f"Pending: {report.pending_gates}")
        print(f"Current Gate: {report.current_gate}")
        print(f"Workflow Status: {report.workflow_status}")

        print("\n" + "="*70)

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
