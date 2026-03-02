#!/usr/bin/env python3
"""pTCS (predicted Thesis Confidence Score) Calculator.

This module calculates confidence scores at 4 levels:
- Claim-level: Individual claim confidence (0-100)
- Agent-level: Agent output confidence (0-100)
- Phase-level: Phase completion confidence (0-100)
- Workflow-level: Overall thesis confidence (0-100)

Design Principle:
- Real-time calculation (every agent execution)
- Automatic scoring (no manual input)
- Fast computation (<100ms per claim)
- Color-coded visualization (Red/Yellow/Cyan/Green)

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import json
import sys
import warnings
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from workflow_constants import PTCS_COLOR_BANDS, PHASE_WEIGHTS


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class ClaimPTCS:
    """Claim-level pTCS result."""
    claim_id: str
    claim_text: str
    claim_type: str

    # pTCS score (0-100)
    ptcs: float

    # Breakdown (4 components)
    source_quality: float      # /40
    claim_type_appropriate: float  # /25
    uncertainty_acknowledgment: float  # /20
    grounding_depth: float     # /15

    # Color coding
    color: str  # "red" | "yellow" | "cyan" | "green"
    confidence_level: str  # "low" | "medium" | "good" | "high"

    # Metadata
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AgentPTCS:
    """Agent-level pTCS result."""
    agent_name: str

    # pTCS score (0-100)
    ptcs: float

    # Breakdown (4 components)
    avg_claim_ptcs: float      # /50
    coverage_completeness: float  # /25
    cross_reference_consistency: float  # /15
    hallucination_firewall_pass: float  # /10

    # Claim statistics
    total_claims: int
    low_confidence_claims: int  # pTCS < 60
    medium_confidence_claims: int  # 60-70
    good_confidence_claims: int  # 71-85
    high_confidence_claims: int  # 86-100

    # Color coding
    color: str
    confidence_level: str

    # Metadata
    timestamp: str
    output_file: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PhasePTCS:
    """Phase-level pTCS result."""
    phase_number: int
    phase_name: str

    # pTCS score (0-100)
    ptcs: float

    # Breakdown (3 components)
    avg_agent_ptcs: float      # /60
    outputs_completeness: float  # /25
    dependency_satisfaction: float  # /15

    # Agent statistics
    total_agents: int
    completed_agents: int
    agent_ptcs_scores: Dict[str, float]

    # Color coding
    color: str
    confidence_level: str

    # Metadata
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WorkflowPTCS:
    """Workflow-level pTCS result."""
    project_name: str

    # pTCS score (0-100)
    ptcs: float

    # Breakdown (3 components)
    phase_weighted_avg: float  # /70
    cross_phase_consistency: float  # /20
    overall_srcs: float  # /10

    # Phase breakdown
    phase_scores: Dict[int, float]
    phase_weights: Dict[int, float]

    # Overall statistics
    total_claims: int
    confidence_distribution: Dict[str, int]

    # Color coding
    color: str
    confidence_level: str

    # Metadata
    timestamp: str

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# pTCS Calculator
# ============================================================================

class PTCSCalculator:
    """Calculate pTCS at all levels (Claim → Agent → Phase → Workflow)."""

    # Color thresholds
    THRESHOLDS = {
        'low': (0, 60),      # Red
        'medium': (61, 70),  # Yellow
        'good': (71, 85),    # Cyan
        'high': (86, 100)    # Green
    }

    # Claim type base scores
    CLAIM_TYPE_SCORES = {
        'FACTUAL': lambda has_source: 100 if has_source else 0,
        'EMPIRICAL': lambda has_data: 100 if has_data else 0,
        'THEORETICAL': lambda has_framework: 100 if has_framework else 50,
        'METHODOLOGICAL': lambda has_method: 100 if has_method else 60,
        'INTERPRETIVE': lambda _: 70,  # Base score 70
        'SPECULATIVE': lambda _: 40    # Base score 40
    }

    def __init__(self):
        """Initialize pTCS calculator."""
        pass

    # ========================================================================
    # Level 1: Claim-level pTCS
    # ========================================================================

    def calculate_claim_ptcs(self, claim: dict) -> ClaimPTCS:
        """Calculate pTCS for a single GroundedClaim.

        Args:
            claim: GroundedClaim dictionary with keys:
                - id: str
                - text: str
                - claim_type: str (FACTUAL, EMPIRICAL, etc.)
                - sources: List[dict]
                - confidence: int (0-100)
                - uncertainty: str

        Returns:
            ClaimPTCS object with score and breakdown
        """
        claim_id = claim.get('id', 'UNKNOWN')
        claim_text = claim.get('text', '')
        claim_type = claim.get('claim_type', 'INTERPRETIVE')
        sources = claim.get('sources', [])
        confidence = claim.get('confidence', 50)
        uncertainty = claim.get('uncertainty', '')

        # Component 1: Source Quality (40%)
        source_quality = self._calculate_source_quality(sources)

        # Component 2: Claim Type Appropriateness (25%)
        claim_type_score = self._calculate_claim_type_score(
            claim_type, sources, claim
        )

        # Component 3: Uncertainty Acknowledgment (20%)
        uncertainty_score = self._calculate_uncertainty_score(
            uncertainty, confidence
        )

        # Component 4: Grounding Depth (15%)
        grounding_score = self._calculate_grounding_depth(sources)

        # Total pTCS (0-100)
        ptcs = (
            source_quality +
            claim_type_score +
            uncertainty_score +
            grounding_score
        )

        # Color coding
        color, confidence_level = self._get_color_coding(ptcs)

        return ClaimPTCS(
            claim_id=claim_id,
            claim_text=claim_text[:100],  # Truncate for display
            claim_type=claim_type,
            ptcs=round(ptcs, 1),
            source_quality=round(source_quality, 1),
            claim_type_appropriate=round(claim_type_score, 1),
            uncertainty_acknowledgment=round(uncertainty_score, 1),
            grounding_depth=round(grounding_score, 1),
            color=color,
            confidence_level=confidence_level,
            timestamp=datetime.now().isoformat()
        )

    def _calculate_source_quality(self, sources: List[dict]) -> float:
        """Calculate source quality score (0-40).

        Breakdown:
        - DOI present: 20 points
        - Primary source count: 10 points each (max 20)
        - Verified status: 10 points

        Total: 50 points, scaled to 40
        """
        if not sources:
            return 0.0

        score = 0

        # Has DOI? (20 points)
        has_doi = any(s.get('doi') for s in sources)
        if has_doi:
            score += 20

        # Primary source count (10 points each, max 20)
        primary_count = sum(1 for s in sources if s.get('type') == 'PRIMARY')
        score += min(primary_count * 10, 20)

        # Verified status (10 points)
        verified = any(s.get('verified', False) for s in sources)
        if verified:
            score += 10

        # Scale 50 → 40
        return (score / 50) * 40

    def _calculate_claim_type_score(
        self,
        claim_type: str,
        sources: List[dict],
        claim: dict
    ) -> float:
        """Calculate claim type appropriateness (0-25).

        Each claim type has specific requirements:
        - FACTUAL: Must have source
        - EMPIRICAL: Must have data
        - THEORETICAL: Should have framework reference
        - INTERPRETIVE: Base score 70
        - SPECULATIVE: Base score 40
        """
        has_source = len(sources) > 0
        has_data = 'data' in str(claim).lower()
        has_framework = any('framework' in str(s).lower() for s in sources)
        has_method = 'method' in str(claim).lower()

        # Get base score (0-100)
        if claim_type in self.CLAIM_TYPE_SCORES:
            if claim_type == 'FACTUAL':
                base_score = self.CLAIM_TYPE_SCORES[claim_type](has_source)
            elif claim_type == 'EMPIRICAL':
                base_score = self.CLAIM_TYPE_SCORES[claim_type](has_data)
            elif claim_type == 'THEORETICAL':
                base_score = self.CLAIM_TYPE_SCORES[claim_type](has_framework)
            elif claim_type == 'METHODOLOGICAL':
                base_score = self.CLAIM_TYPE_SCORES[claim_type](has_method)
            else:
                base_score = self.CLAIM_TYPE_SCORES[claim_type](None)
        else:
            base_score = 50  # Unknown type

        # Scale 100 → 25
        return (base_score / 100) * 25

    def _calculate_uncertainty_score(
        self,
        uncertainty: str,
        confidence: int
    ) -> float:
        """Calculate uncertainty acknowledgment (0-20).

        Breakdown:
        - Has uncertainty field: 50%
        - Confidence level (0-100): 50%
        """
        score = 0

        # Has uncertainty field? (50%)
        if uncertainty and len(uncertainty.strip()) > 0:
            score += 50

        # Confidence level (50%)
        score += (confidence / 100) * 50

        # Scale 100 → 20
        return (score / 100) * 20

    def _calculate_grounding_depth(self, sources: List[dict]) -> float:
        """Calculate grounding depth (0-15).

        Based on number of sources (max 4 = 100 points).
        """
        source_count = len(sources)

        # Max 4 sources = 100 points
        score = min(source_count * 25, 100)

        # Scale 100 → 15
        return (score / 100) * 15

    # ========================================================================
    # Level 2: Agent-level pTCS
    # ========================================================================

    def calculate_agent_ptcs(
        self,
        claims: List[dict],
        agent_name: str,
        required_sections: Optional[List[str]] = None,
        output_file: Optional[str] = None
    ) -> AgentPTCS:
        """Calculate pTCS for an agent output.

        Args:
            claims: List of GroundedClaim dictionaries
            agent_name: Name of the agent
            required_sections: List of required section names
            output_file: Path to output file

        Returns:
            AgentPTCS object with score and breakdown
        """
        if not claims:
            # No claims → score 0
            return AgentPTCS(
                agent_name=agent_name,
                ptcs=0.0,
                avg_claim_ptcs=0.0,
                coverage_completeness=0.0,
                cross_reference_consistency=0.0,
                hallucination_firewall_pass=0.0,
                total_claims=0,
                low_confidence_claims=0,
                medium_confidence_claims=0,
                good_confidence_claims=0,
                high_confidence_claims=0,
                color='red',
                confidence_level='low',
                timestamp=datetime.now().isoformat(),
                output_file=output_file
            )

        # Calculate claim-level pTCS for all claims
        claim_ptcs_list = [self.calculate_claim_ptcs(c) for c in claims]

        # Component 1: Average Claim pTCS (50%)
        avg_claim_ptcs = sum(c.ptcs for c in claim_ptcs_list) / len(claim_ptcs_list)
        avg_claim_score = (avg_claim_ptcs / 100) * 50

        # Component 2: Coverage Completeness (25%)
        coverage_score = self._calculate_coverage(required_sections, output_file, claims) * 25

        # Component 3: Cross-Reference Consistency (15%)
        consistency_score = self._calculate_cross_reference_consistency(claims) * 15

        # Component 4: Hallucination Firewall Pass Rate (10%)
        # (Simplified: check for red flags)
        firewall_score = self._calculate_firewall_pass(claims) * 10

        # Total pTCS (0-100)
        ptcs = (
            avg_claim_score +
            coverage_score +
            consistency_score +
            firewall_score
        )

        # Statistics (SOT-A: PTCS_COLOR_BANDS)
        _r = PTCS_COLOR_BANDS["red"]
        _y = PTCS_COLOR_BANDS["yellow"]
        _c = PTCS_COLOR_BANDS["cyan"]
        _g = PTCS_COLOR_BANDS["green"]
        low_count = sum(1 for c in claim_ptcs_list if _r[0] <= c.ptcs <= _r[1])
        medium_count = sum(1 for c in claim_ptcs_list if _y[0] <= c.ptcs <= _y[1])
        good_count = sum(1 for c in claim_ptcs_list if _c[0] <= c.ptcs <= _c[1])
        high_count = sum(1 for c in claim_ptcs_list if c.ptcs >= _g[0])

        # Color coding
        color, confidence_level = self._get_color_coding(ptcs)

        return AgentPTCS(
            agent_name=agent_name,
            ptcs=round(ptcs, 1),
            avg_claim_ptcs=round(avg_claim_score, 1),
            coverage_completeness=round(coverage_score, 1),
            cross_reference_consistency=round(consistency_score, 1),
            hallucination_firewall_pass=round(firewall_score, 1),
            total_claims=len(claims),
            low_confidence_claims=low_count,
            medium_confidence_claims=medium_count,
            good_confidence_claims=good_count,
            high_confidence_claims=high_count,
            color=color,
            confidence_level=confidence_level,
            timestamp=datetime.now().isoformat(),
            output_file=output_file
        )

    def _calculate_coverage(
        self,
        required_sections: Optional[List[str]],
        output_file: Optional[str] = None,
        claims: Optional[List[dict]] = None
    ) -> float:
        """Calculate coverage completeness (0-1).

        Checks how many required sections are present in the output.
        """
        if not required_sections:
            # TODO: Define AGENT_REQUIRED_SECTIONS in workflow_constants.py
            # for actual coverage measurement. Current default inflates score by ~6.25 points.
            warnings.warn(
                f"Coverage defaulting to 1.0 (required_sections not defined). "
                f"Define required_sections for accurate scoring.",
                stacklevel=2,
            )
            return 1.0

        found_sections = set()

        # Strategy 1: Check output file for markdown headings
        if output_file:
            output_path = Path(output_file)
            if output_path.exists():
                try:
                    content = output_path.read_text(encoding='utf-8')
                    for section in required_sections:
                        for line in content.splitlines():
                            if line.strip().startswith('#') and section.lower() in line.lower():
                                found_sections.add(section)
                                break
                except (OSError, UnicodeDecodeError):
                    pass

        # Strategy 2: Fall back to claim text if output file insufficient
        if claims and len(found_sections) < len(required_sections):
            all_text = ' '.join(c.get('text', '') for c in claims).lower()
            for section in required_sections:
                if section not in found_sections and section.lower() in all_text:
                    found_sections.add(section)

        return len(found_sections) / len(required_sections)

    def _calculate_cross_reference_consistency(self, claims: List[dict]) -> float:
        """Calculate cross-reference consistency (0-1).

        Factors:
        - Source overlap across claims (60%): shared sources = higher consistency
        - Claim type coherence (40%): same-type claims = more coherent output
        """
        if len(claims) <= 1:
            return 1.0  # Single claim is self-consistent

        # Factor 1: Source overlap (60%)
        all_refs = []
        for claim in claims:
            for source in claim.get('sources', []):
                ref = source.get('reference', '') or source.get('doi', '')
                if ref:
                    all_refs.append(ref)

        if all_refs:
            unique_refs = len(set(all_refs))
            total_refs = len(all_refs)
            # Higher overlap ratio = more consistency
            overlap_ratio = 1 - (unique_refs / total_refs) if total_refs > 1 else 0
            source_consistency = min(overlap_ratio * 2, 1.0)
        else:
            source_consistency = 0.5  # No sources = neutral (not penalized heavily)

        # Factor 2: Claim type coherence (40%)
        types = [c.get('claim_type', 'UNKNOWN') for c in claims]
        if types:
            most_common_count = max(types.count(t) for t in set(types))
            type_coherence = most_common_count / len(types)
        else:
            type_coherence = 0.5

        return source_consistency * 0.6 + type_coherence * 0.4

    def _calculate_firewall_pass(self, claims: List[dict]) -> float:
        """Calculate hallucination firewall pass rate (0-1).

        Check for red flag phrases:
        - "모든 연구가 일치"
        - "100%"
        - "예외 없이"
        - "확실히"
        - "명백히"
        """
        red_flags = [
            "모든 연구가 일치",
            "100%",
            "예외 없이",
            "all research agrees",
            "without exception",
            "absolutely",
            "definitely",
            "obviously"
        ]

        total_claims = len(claims)
        flagged_claims = 0

        for claim in claims:
            claim_text = claim.get('text', '').lower()
            if any(flag.lower() in claim_text for flag in red_flags):
                flagged_claims += 1

        # Pass rate = (total - flagged) / total
        if total_claims == 0:
            return 1.0

        return (total_claims - flagged_claims) / total_claims

    # ========================================================================
    # Level 3: Phase-level pTCS
    # ========================================================================

    def calculate_phase_ptcs(
        self,
        phase_number: int,
        agent_ptcs_scores: Dict[str, float],
        required_outputs: List[str],
        present_outputs: List[str],
        dependencies: Dict[int, List[int]],
        completed_steps: List[int]
    ) -> PhasePTCS:
        """Calculate pTCS for a phase.

        Args:
            phase_number: Phase number (0-4)
            agent_ptcs_scores: Dict of {agent_name: ptcs_score}
            required_outputs: List of required output files
            present_outputs: List of present output files
            dependencies: Step dependencies
            completed_steps: List of completed step numbers

        Returns:
            PhasePTCS object with score and breakdown
        """
        phase_names = {
            0: "Initialization",
            1: "Literature Review",
            2: "Research Design",
            3: "Thesis Writing",
            4: "Publication Strategy"
        }
        phase_name = phase_names.get(phase_number, f"Phase {phase_number}")

        if not agent_ptcs_scores:
            # No agents completed yet
            return PhasePTCS(
                phase_number=phase_number,
                phase_name=phase_name,
                ptcs=0.0,
                avg_agent_ptcs=0.0,
                outputs_completeness=0.0,
                dependency_satisfaction=0.0,
                total_agents=0,
                completed_agents=0,
                agent_ptcs_scores={},
                color='red',
                confidence_level='low',
                timestamp=datetime.now().isoformat()
            )

        # Component 1: Average Agent pTCS (60%)
        avg_agent_ptcs = sum(agent_ptcs_scores.values()) / len(agent_ptcs_scores)
        avg_agent_score = (avg_agent_ptcs / 100) * 60

        # Component 2: Outputs Completeness (25%)
        outputs_score = (len(present_outputs) / len(required_outputs)) * 25 if required_outputs else 25

        # Component 3: Dependency Satisfaction (15%)
        dependency_score = self._calculate_dependency_satisfaction(
            dependencies, completed_steps
        ) * 15

        # Total pTCS (0-100)
        ptcs = avg_agent_score + outputs_score + dependency_score

        # Color coding
        color, confidence_level = self._get_color_coding(ptcs)

        return PhasePTCS(
            phase_number=phase_number,
            phase_name=phase_name,
            ptcs=round(ptcs, 1),
            avg_agent_ptcs=round(avg_agent_score, 1),
            outputs_completeness=round(outputs_score, 1),
            dependency_satisfaction=round(dependency_score, 1),
            total_agents=len(agent_ptcs_scores),
            completed_agents=len(agent_ptcs_scores),
            agent_ptcs_scores=agent_ptcs_scores,
            color=color,
            confidence_level=confidence_level,
            timestamp=datetime.now().isoformat()
        )

    def _calculate_dependency_satisfaction(
        self,
        dependencies: Dict[int, List[int]],
        completed_steps: List[int]
    ) -> float:
        """Calculate dependency satisfaction (0-1).

        All dependencies satisfied = 1.0
        """
        if not dependencies:
            return 1.0

        total_deps = 0
        satisfied_deps = 0

        for step, required_steps in dependencies.items():
            for required_step in required_steps:
                total_deps += 1
                if required_step in completed_steps:
                    satisfied_deps += 1

        if total_deps == 0:
            return 1.0

        return satisfied_deps / total_deps

    # ========================================================================
    # Level 4: Workflow-level pTCS
    # ========================================================================

    def calculate_workflow_ptcs(
        self,
        project_name: str,
        phase_scores: Dict[int, float],
        cross_phase_consistency: float,
        overall_srcs: float,
        total_claims: int,
        confidence_distribution: Dict[str, int]
    ) -> WorkflowPTCS:
        """Calculate pTCS for entire workflow.

        Args:
            project_name: Project name
            phase_scores: Dict of {phase_number: ptcs_score}
            cross_phase_consistency: Cross-phase consistency (0-100)
            overall_srcs: Overall SRCS score (0-100)
            total_claims: Total number of claims
            confidence_distribution: Distribution by confidence level

        Returns:
            WorkflowPTCS object with score and breakdown
        """
        # Phase weights (from SOT-A)
        phase_weights = PHASE_WEIGHTS

        # Component 1: Phase-weighted Average (70%)
        phase_weighted_sum = sum(
            phase_scores.get(p, 0) * phase_weights[p]
            for p in range(5)
        )
        phase_weighted_score = phase_weighted_sum * 0.7

        # Component 2: Cross-phase Consistency (20%)
        consistency_score = (cross_phase_consistency / 100) * 20

        # Component 3: Overall SRCS (10%)
        srcs_score = (overall_srcs / 100) * 10

        # Total pTCS (0-100)
        ptcs = phase_weighted_score + consistency_score + srcs_score

        # Color coding
        color, confidence_level = self._get_color_coding(ptcs)

        return WorkflowPTCS(
            project_name=project_name,
            ptcs=round(ptcs, 1),
            phase_weighted_avg=round(phase_weighted_score, 1),
            cross_phase_consistency=round(consistency_score, 1),
            overall_srcs=round(srcs_score, 1),
            phase_scores=phase_scores,
            phase_weights=phase_weights,
            total_claims=total_claims,
            confidence_distribution=confidence_distribution,
            color=color,
            confidence_level=confidence_level,
            timestamp=datetime.now().isoformat()
        )

    # ========================================================================
    # Utilities
    # ========================================================================

    def _get_color_coding(self, ptcs: float) -> Tuple[str, str]:
        """Get color coding for pTCS score (SOT-A: PTCS_COLOR_BANDS).

        Returns:
            (color, confidence_level)
        """
        level_names = {'red': 'low', 'yellow': 'medium', 'cyan': 'good', 'green': 'high'}
        for color, (low, high) in PTCS_COLOR_BANDS.items():
            if low <= ptcs <= high:
                return (color, level_names[color])
        return ('red', 'low')

    def get_color_emoji(self, color: str) -> str:
        """Get emoji for color."""
        color_map = {
            'red': '🔴',
            'yellow': '🟡',
            'cyan': '🔵',
            'green': '🟢'
        }
        return color_map.get(color, '⚪')


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for pTCS calculator."""
    import argparse

    parser = argparse.ArgumentParser(description="pTCS Calculator")
    parser.add_argument("--test", action="store_true", help="Run test calculation")

    args = parser.parse_args()

    if args.test:
        # Test claim-level pTCS
        calc = PTCSCalculator()

        test_claim = {
            'id': 'TEST-001',
            'text': 'AI systems cannot possess subjective experience',
            'claim_type': 'THEORETICAL',
            'sources': [
                {'type': 'PRIMARY', 'doi': '10.1234/test', 'verified': True},
                {'type': 'SECONDARY', 'verified': False}
            ],
            'confidence': 85,
            'uncertainty': 'Limited empirical evidence for consciousness theories'
        }

        result = calc.calculate_claim_ptcs(test_claim)

        print("\n" + "="*70)
        print("pTCS Calculation Test")
        print("="*70)
        print(f"\nClaim: {result.claim_text}")
        print(f"Type: {result.claim_type}")
        print(f"\npTCS Score: {result.ptcs}/100 {calc.get_color_emoji(result.color)}")
        print(f"Confidence Level: {result.confidence_level}")
        print(f"\nBreakdown:")
        print(f"  Source Quality:        {result.source_quality:.1f}/40")
        print(f"  Claim Type Appropriate: {result.claim_type_appropriate:.1f}/25")
        print(f"  Uncertainty Ack:       {result.uncertainty_acknowledgment:.1f}/20")
        print(f"  Grounding Depth:       {result.grounding_depth:.1f}/15")
        print("="*70)

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
