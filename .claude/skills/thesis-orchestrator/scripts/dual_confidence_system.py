#!/usr/bin/env python3
"""Dual Confidence System: pTCS + SRCS Integration.

This module integrates pTCS (predictive) and SRCS (evaluative) into a
unified confidence assessment system.

Design:
- pTCS (60%): Real-time prediction, all agents (broad coverage)
- SRCS (40%): Gated evaluation, critical points (deep quality)

Decision Matrix:
- pTCS is the STRONGER criterion (user requirement)
- pTCS < threshold → FAIL (regardless of SRCS)
- pTCS ≥ threshold + SRCS ≥ threshold → PASS
- pTCS ≥ threshold + SRCS < threshold → MANUAL_REVIEW

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from ptcs_calculator import PTCSCalculator, WorkflowPTCS
from ptcs_enforcer import PTCSEnforcer
from workflow_constants import DUAL_CONFIDENCE_THRESHOLDS, DUAL_CONFIDENCE_WEIGHTS


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class DualConfidenceScore:
    """Combined pTCS + SRCS confidence score."""

    # Individual scores
    ptcs: float  # 0-100
    srcs: float  # 0-100

    # Weighted combination (pTCS 60% + SRCS 40%)
    combined: float  # 0-100

    # Decision
    decision: str  # "PASS" | "FAIL" | "MANUAL_REVIEW"
    reasoning: str

    # Metadata
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GateDecision:
    """Gate validation decision (Wave or Phase)."""

    # Gate info
    gate_type: str  # "wave" | "phase"
    gate_number: int

    # Scores
    ptcs: float
    srcs: float
    combined: float

    # Thresholds
    ptcs_threshold: float
    srcs_threshold: float

    # Decision
    passed: bool
    decision: str  # "PASS" | "FAIL" | "PASS_WITH_CAUTION" | "MANUAL_REVIEW"
    reasoning: str

    # Metadata
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# Dual Confidence Calculator
# ============================================================================

class DualConfidenceCalculator:
    """Calculate combined pTCS + SRCS confidence scores.

    Weight Distribution:
    - pTCS: 60% (real-time, broad coverage)
    - SRCS: 40% (gated, deep quality)
    """

    # Weights (from SOT-A)
    PTCS_WEIGHT = DUAL_CONFIDENCE_WEIGHTS["ptcs"]
    SRCS_WEIGHT = DUAL_CONFIDENCE_WEIGHTS["srcs"]

    # Default thresholds (from SOT-A)
    DEFAULT_THRESHOLDS = DUAL_CONFIDENCE_THRESHOLDS

    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None
    ):
        """Initialize dual confidence calculator.

        Args:
            thresholds: Custom thresholds (optional)
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.ptcs_calc = PTCSCalculator()

    # ========================================================================
    # Combined Score Calculation
    # ========================================================================

    def calculate_combined_score(
        self,
        ptcs: float,
        srcs: float
    ) -> DualConfidenceScore:
        """Calculate combined confidence score.

        Formula:
            combined = ptcs * 0.60 + srcs * 0.40

        Decision Logic (pTCS is STRONGER):
            - If pTCS < threshold → FAIL (강한 기준)
            - If pTCS ≥ threshold and SRCS ≥ threshold → PASS
            - If pTCS ≥ threshold and SRCS < threshold → MANUAL_REVIEW

        Args:
            ptcs: pTCS score (0-100)
            srcs: SRCS score (0-100)

        Returns:
            DualConfidenceScore with decision
        """
        # Calculate weighted combination
        combined = ptcs * self.PTCS_WEIGHT + srcs * self.SRCS_WEIGHT

        # Decision logic (pTCS is STRONGER)
        if ptcs < self.thresholds['ptcs_wave']:
            # pTCS failed → Automatic FAIL
            decision = "FAIL"
            reasoning = (
                f"pTCS ({ptcs:.1f}) below threshold ({self.thresholds['ptcs_wave']}). "
                f"pTCS is the stronger criterion - automatic FAIL."
            )

        elif ptcs >= self.thresholds['ptcs_wave'] and srcs >= self.thresholds['srcs_wave']:
            # Both passed → PASS
            decision = "PASS"
            reasoning = (
                f"Both pTCS ({ptcs:.1f}) and SRCS ({srcs:.1f}) meet thresholds. "
                f"Combined score: {combined:.1f}"
            )

        elif ptcs >= self.thresholds['ptcs_wave'] and srcs < self.thresholds['srcs_wave']:
            # pTCS passed, SRCS failed → MANUAL_REVIEW
            decision = "MANUAL_REVIEW"
            reasoning = (
                f"pTCS ({ptcs:.1f}) passed but SRCS ({srcs:.1f}) below threshold "
                f"({self.thresholds['srcs_wave']}). Manual review recommended to "
                f"investigate deep quality issues detected by SRCS."
            )

        else:
            # Should not reach here
            decision = "UNKNOWN"
            reasoning = "Unexpected decision state"

        return DualConfidenceScore(
            ptcs=round(ptcs, 1),
            srcs=round(srcs, 1),
            combined=round(combined, 1),
            decision=decision,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat()
        )

    # ========================================================================
    # Gate Validation
    # ========================================================================

    def validate_wave_gate(
        self,
        wave_number: int,
        wave_ptcs: float,
        wave_srcs: float
    ) -> GateDecision:
        """Validate Wave Gate (Phase 1 only).

        Args:
            wave_number: Wave number (1-5)
            wave_ptcs: Wave-level pTCS (0-100)
            wave_srcs: Wave-level SRCS (0-100)

        Returns:
            GateDecision with pass/fail status
        """
        # Calculate combined score
        dual_score = self.calculate_combined_score(wave_ptcs, wave_srcs)

        # Determine if passed (MANUAL_REVIEW also passes with caution)
        passed = dual_score.decision in ("PASS", "MANUAL_REVIEW")

        # Map decision to gate-specific decision
        if dual_score.decision == "PASS":
            gate_decision = "PASS"
        elif dual_score.decision == "FAIL":
            gate_decision = "FAIL"
        elif dual_score.decision == "MANUAL_REVIEW":
            gate_decision = "PASS_WITH_CAUTION"
        else:
            gate_decision = "UNKNOWN"

        return GateDecision(
            gate_type="wave",
            gate_number=wave_number,
            ptcs=wave_ptcs,
            srcs=wave_srcs,
            combined=dual_score.combined,
            ptcs_threshold=self.thresholds['ptcs_wave'],
            srcs_threshold=self.thresholds['srcs_wave'],
            passed=passed,
            decision=gate_decision,
            reasoning=dual_score.reasoning,
            timestamp=datetime.now().isoformat()
        )

    def validate_phase_gate(
        self,
        phase_number: int,
        phase_ptcs: float,
        phase_srcs: float
    ) -> GateDecision:
        """Validate Phase Gate (Phase 0-4).

        Args:
            phase_number: Phase number (0-4)
            phase_ptcs: Phase-level pTCS (0-100)
            phase_srcs: Phase-level SRCS (0-100)

        Returns:
            GateDecision with pass/fail status
        """
        # Use phase thresholds
        ptcs_threshold = self.thresholds['ptcs_phase']
        srcs_threshold = self.thresholds['srcs_phase']

        # Decision logic (pTCS STRONGER)
        if phase_ptcs < ptcs_threshold:
            # pTCS failed → FAIL
            passed = False
            decision = "FAIL"
            reasoning = (
                f"Phase {phase_number} pTCS ({phase_ptcs:.1f}) below threshold "
                f"({ptcs_threshold}). Automatic FAIL."
            )

        elif phase_ptcs >= ptcs_threshold and phase_srcs >= srcs_threshold:
            # Both passed → PASS
            passed = True
            decision = "PASS"
            reasoning = (
                f"Phase {phase_number} passed. pTCS: {phase_ptcs:.1f}, "
                f"SRCS: {phase_srcs:.1f}"
            )

        elif phase_ptcs >= ptcs_threshold and phase_srcs < srcs_threshold:
            # pTCS passed, SRCS failed → MANUAL_REVIEW
            passed = False  # Still considered failure (need manual review)
            decision = "MANUAL_REVIEW"
            reasoning = (
                f"Phase {phase_number} pTCS ({phase_ptcs:.1f}) passed but "
                f"SRCS ({phase_srcs:.1f}) below threshold ({srcs_threshold}). "
                f"Manual review required."
            )

        else:
            passed = False
            decision = "UNKNOWN"
            reasoning = "Unexpected decision state"

        # Calculate combined score
        combined = phase_ptcs * self.PTCS_WEIGHT + phase_srcs * self.SRCS_WEIGHT

        return GateDecision(
            gate_type="phase",
            gate_number=phase_number,
            ptcs=phase_ptcs,
            srcs=phase_srcs,
            combined=combined,
            ptcs_threshold=ptcs_threshold,
            srcs_threshold=srcs_threshold,
            passed=passed,
            decision=decision,
            reasoning=reasoning,
            timestamp=datetime.now().isoformat()
        )

    # ========================================================================
    # Workflow-level Assessment
    # ========================================================================

    def assess_workflow_confidence(
        self,
        workflow_ptcs: float,
        overall_srcs: float
    ) -> DualConfidenceScore:
        """Assess overall workflow confidence.

        Args:
            workflow_ptcs: Workflow-level pTCS (0-100)
            overall_srcs: Overall SRCS (unified across all phases)

        Returns:
            DualConfidenceScore for entire thesis
        """
        return self.calculate_combined_score(workflow_ptcs, overall_srcs)


# ============================================================================
# Dual Confidence Validator
# ============================================================================

class DualConfidenceValidator:
    """Validate agents/waves/phases using dual confidence system.

    Combines:
    - PTCSEnforcer: Real-time enforcement (retry-until-pass)
    - DualConfidenceCalculator: Combined pTCS + SRCS validation
    """

    def __init__(
        self,
        ptcs_enforcer: Optional[PTCSEnforcer] = None,
        dual_calculator: Optional[DualConfidenceCalculator] = None
    ):
        """Initialize dual validator.

        Args:
            ptcs_enforcer: pTCS enforcer (optional, creates default)
            dual_calculator: Dual calculator (optional, creates default)
        """
        self.ptcs_enforcer = ptcs_enforcer or PTCSEnforcer()
        self.dual_calculator = dual_calculator or DualConfidenceCalculator()

    # ========================================================================
    # Agent-level Validation
    # ========================================================================

    def validate_agent(
        self,
        agent_name: str,
        agent_function: callable,
        threshold: float = 70,
        **kwargs
    ):
        """Validate agent with pTCS enforcement.

        This uses pTCS only (SRCS not applicable at agent level).

        Args:
            agent_name: Name of agent
            agent_function: Agent execution function
            threshold: pTCS threshold (default 70)
            **kwargs: Arguments to pass to agent

        Returns:
            EnforcementResult from pTCS enforcer

        Raises:
            RuntimeError: If pTCS threshold not met after max retries
        """
        return self.ptcs_enforcer.enforce_agent_execution(
            agent_name=agent_name,
            agent_function=agent_function,
            threshold=threshold,
            **kwargs
        )

    # ========================================================================
    # Wave-level Validation (Phase 1 only)
    # ========================================================================

    def validate_wave(
        self,
        wave_number: int,
        wave_ptcs: float,
        wave_srcs: float
    ) -> GateDecision:
        """Validate Wave Gate with dual confidence.

        Args:
            wave_number: Wave number (1-5)
            wave_ptcs: Wave-level pTCS
            wave_srcs: Wave-level SRCS

        Returns:
            GateDecision

        Raises:
            RuntimeError: If gate fails
        """
        decision = self.dual_calculator.validate_wave_gate(
            wave_number=wave_number,
            wave_ptcs=wave_ptcs,
            wave_srcs=wave_srcs
        )

        if decision.decision == "FAIL":
            raise RuntimeError(
                f"Wave {wave_number} gate failed. "
                f"Reasoning: {decision.reasoning}"
            )
        elif decision.decision in ("PASS_WITH_CAUTION", "MANUAL_REVIEW"):
            # Allow to continue with warning (aligned with phase gate behavior)
            print(f"\n⚠️ WARNING: Wave {wave_number} requires review")
            print(f"   {decision.reasoning}")
            print(f"   Proceeding with caution...\n")

        return decision

    # ========================================================================
    # Phase-level Validation
    # ========================================================================

    def validate_phase(
        self,
        phase_number: int,
        phase_ptcs: float,
        phase_srcs: float
    ) -> GateDecision:
        """Validate Phase Gate with dual confidence.

        Args:
            phase_number: Phase number (0-4)
            phase_ptcs: Phase-level pTCS
            phase_srcs: Phase-level SRCS

        Returns:
            GateDecision

        Raises:
            RuntimeError: If gate fails (not MANUAL_REVIEW)
        """
        decision = self.dual_calculator.validate_phase_gate(
            phase_number=phase_number,
            phase_ptcs=phase_ptcs,
            phase_srcs=phase_srcs
        )

        if decision.decision == "FAIL":
            raise RuntimeError(
                f"Phase {phase_number} gate failed. "
                f"Reasoning: {decision.reasoning}"
            )
        elif decision.decision == "MANUAL_REVIEW":
            # Allow to continue with warning
            print(f"\n⚠️ WARNING: Phase {phase_number} requires manual review")
            print(f"   {decision.reasoning}")
            print(f"   Proceeding with caution...\n")

        return decision


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for dual confidence system."""
    import argparse

    parser = argparse.ArgumentParser(description="Dual Confidence System")
    parser.add_argument("--test", action="store_true", help="Run test calculation")

    args = parser.parse_args()

    if args.test:
        # Test dual confidence calculation

        print("\n" + "="*70)
        print("Dual Confidence System Test")
        print("="*70)

        calc = DualConfidenceCalculator()

        # Test Case 1: Both pass
        print("\n[Test 1] Both pTCS and SRCS pass")
        print("─"*70)
        result1 = calc.calculate_combined_score(ptcs=82, srcs=78)
        print(f"pTCS: {result1.ptcs}/100")
        print(f"SRCS: {result1.srcs}/100")
        print(f"Combined: {result1.combined}/100")
        print(f"Decision: {result1.decision}")
        print(f"Reasoning: {result1.reasoning}")

        # Test Case 2: pTCS pass, SRCS fail
        print("\n[Test 2] pTCS pass, SRCS fail")
        print("─"*70)
        result2 = calc.calculate_combined_score(ptcs=78, srcs=72)
        print(f"pTCS: {result2.ptcs}/100")
        print(f"SRCS: {result2.srcs}/100")
        print(f"Combined: {result2.combined}/100")
        print(f"Decision: {result2.decision}")
        print(f"Reasoning: {result2.reasoning}")

        # Test Case 3: pTCS fail (SRCS irrelevant)
        print("\n[Test 3] pTCS fail (강한 기준)")
        print("─"*70)
        result3 = calc.calculate_combined_score(ptcs=68, srcs=80)
        print(f"pTCS: {result3.ptcs}/100")
        print(f"SRCS: {result3.srcs}/100")
        print(f"Combined: {result3.combined}/100")
        print(f"Decision: {result3.decision}")
        print(f"Reasoning: {result3.reasoning}")

        print("\n" + "="*70)

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
