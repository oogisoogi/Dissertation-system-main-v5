#!/usr/bin/env python3
"""pTCS Enforcer: Retry-until-pass Logic.

This module enforces pTCS thresholds by automatically retrying agent execution
until the threshold is met.

Core Principle (User Requirement):
- "pTCS를 강한 기준으로 사용"
- "기준에 충족하지 못할 경우, 해당 기준에 충족할 때까지 작업을 반복"

Enforcement Strategy:
1. Execute agent
2. Calculate pTCS
3. If pTCS < threshold → Retry
4. Repeat until pass (or max retries reached)

Author: Claude Code (Thesis Orchestrator Team)
Date: 2026-01-20
"""

import sys
import json
from pathlib import Path
from typing import Callable, Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict
import time

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))
from ptcs_calculator import PTCSCalculator, AgentPTCS
from workflow_constants import PTCS_THRESHOLDS, MAX_RETRIES_AGENT


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class EnforcementResult:
    """Result of enforcement (retry-until-pass)."""

    # Agent info
    agent_name: str

    # Final status
    success: bool
    final_ptcs: float
    attempts: int

    # Threshold
    threshold: float

    # Attempt history
    attempt_history: List[Dict[str, Any]]

    # Timing
    total_time_seconds: float
    timestamp: str

    # Final output
    final_output: Optional[Any] = None

    def to_dict(self) -> dict:
        return asdict(self)


# ============================================================================
# pTCS Enforcer
# ============================================================================

class PTCSEnforcer:
    """Enforce pTCS thresholds with retry-until-pass logic.

    Core Principle:
    - pTCS < threshold → Automatic retry
    - Retry until pass OR max attempts reached
    - No manual override (강제 실행)
    """

    # Default thresholds (from SOT-A)
    DEFAULT_THRESHOLDS = PTCS_THRESHOLDS

    # Default max retries (from SOT-A)
    DEFAULT_MAX_RETRIES = MAX_RETRIES_AGENT

    def __init__(
        self,
        thresholds: Optional[Dict[str, float]] = None,
        max_retries: int = DEFAULT_MAX_RETRIES,
        verbose: bool = True
    ):
        """Initialize enforcer.

        Args:
            thresholds: Custom thresholds (optional)
            max_retries: Maximum retry attempts (default 3)
            verbose: Print detailed logs (default True)
        """
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.max_retries = max_retries
        self.verbose = verbose
        self.calc = PTCSCalculator()

    # ========================================================================
    # Core Enforcement Logic
    # ========================================================================

    def enforce_agent_execution(
        self,
        agent_name: str,
        agent_function: Callable,
        threshold: Optional[float] = None,
        extract_claims_function: Optional[Callable] = None,
        **agent_kwargs
    ) -> EnforcementResult:
        """Execute agent with pTCS enforcement (retry-until-pass).

        Args:
            agent_name: Name of the agent
            agent_function: Agent execution function
            threshold: pTCS threshold (default: 70 for agents)
            extract_claims_function: Function to extract claims from output
            **agent_kwargs: Arguments to pass to agent_function

        Returns:
            EnforcementResult with success status and attempt history

        Raises:
            RuntimeError: If max retries exceeded without passing threshold
        """
        # Use default threshold if not provided
        threshold = threshold or self.thresholds['agent']

        # Start timer
        start_time = time.time()

        # Attempt history
        attempt_history = []

        self._log(f"\n{'='*70}")
        self._log(f"🔒 pTCS ENFORCEMENT: {agent_name}")
        self._log(f"{'='*70}")
        self._log(f"Threshold: {threshold}/100")
        self._log(f"Max Retries: {self.max_retries}")
        self._log("")

        # Retry loop
        for attempt in range(1, self.max_retries + 1):
            self._log(f"[Attempt {attempt}/{self.max_retries}] Executing {agent_name}...")

            try:
                # Execute agent
                agent_output = agent_function(**agent_kwargs)

                # Extract claims (if function provided)
                if extract_claims_function:
                    claims = extract_claims_function(agent_output)
                else:
                    # Assume output is already claims or has 'claims' key
                    if isinstance(agent_output, dict) and 'claims' in agent_output:
                        claims = agent_output['claims']
                    elif isinstance(agent_output, list):
                        claims = agent_output
                    else:
                        # No claims found - use empty list
                        claims = []

                # Calculate pTCS
                agent_ptcs = self.calc.calculate_agent_ptcs(
                    claims=claims,
                    agent_name=agent_name
                )

                # Record attempt
                attempt_record = {
                    'attempt': attempt,
                    'ptcs': agent_ptcs.ptcs,
                    'threshold': threshold,
                    'passed': agent_ptcs.ptcs >= threshold,
                    'claims_count': agent_ptcs.total_claims,
                    'low_confidence_claims': agent_ptcs.low_confidence_claims,
                    'timestamp': datetime.now().isoformat()
                }
                attempt_history.append(attempt_record)

                # Log result
                emoji = self.calc.get_color_emoji(agent_ptcs.color)
                self._log(f"  Result: pTCS {agent_ptcs.ptcs}/100 {emoji}")
                self._log(f"  Claims: {agent_ptcs.total_claims} total, "
                         f"{agent_ptcs.low_confidence_claims} low-confidence")

                # Check threshold
                if agent_ptcs.ptcs >= threshold:
                    # SUCCESS!
                    self._log(f"\n✅ PASS: pTCS ({agent_ptcs.ptcs}) ≥ threshold ({threshold})")

                    total_time = time.time() - start_time

                    return EnforcementResult(
                        agent_name=agent_name,
                        success=True,
                        final_ptcs=agent_ptcs.ptcs,
                        attempts=attempt,
                        threshold=threshold,
                        attempt_history=attempt_history,
                        total_time_seconds=round(total_time, 2),
                        timestamp=datetime.now().isoformat(),
                        final_output=agent_output
                    )
                else:
                    # FAIL - Retry needed
                    self._log(f"\n❌ FAIL: pTCS ({agent_ptcs.ptcs}) < threshold ({threshold})")

                    if attempt < self.max_retries:
                        # Generate and inject feedback for next attempt
                        claim_ptcs_list = [self.calc.calculate_claim_ptcs(c) for c in claims]
                        feedback = self._generate_retry_feedback(claim_ptcs_list)

                        # 1. Keep existing kwarg (backward compatibility)
                        agent_kwargs['_retry_feedback'] = feedback

                        # 2. Prompt injection (if caller passes prompt kwarg)
                        if 'prompt' in agent_kwargs:
                            feedback_text = self._format_retry_feedback(feedback)
                            agent_kwargs['prompt'] = (
                                f"{feedback_text}\n\n{agent_kwargs['prompt']}"
                            )

                        # 3. File-based sidecar (always written)
                        self._write_feedback_sidecar(
                            agent_name, attempt, feedback
                        )

                        self._log_retry_feedback(feedback)
                        self._log(f"⚠️  Retrying with feedback... "
                                  f"({self.max_retries - attempt} attempts remaining)")
                        self._log(f"\n{'─'*70}\n")
                        # Continue to next attempt
                    else:
                        # Max retries exceeded
                        self._log(f"\n❌ MAX RETRIES EXCEEDED ({self.max_retries} attempts)")

                        total_time = time.time() - start_time

                        result = EnforcementResult(
                            agent_name=agent_name,
                            success=False,
                            final_ptcs=agent_ptcs.ptcs,
                            attempts=attempt,
                            threshold=threshold,
                            attempt_history=attempt_history,
                            total_time_seconds=round(total_time, 2),
                            timestamp=datetime.now().isoformat(),
                            final_output=agent_output
                        )

                        # Raise exception (강제 중단)
                        raise RuntimeError(
                            f"Agent {agent_name} failed to meet pTCS threshold "
                            f"after {self.max_retries} attempts. "
                            f"Final pTCS: {agent_ptcs.ptcs}, "
                            f"Required: {threshold}"
                        )

            except Exception as e:
                # Agent execution error
                self._log(f"\n❌ ERROR during agent execution: {e}")

                attempt_record = {
                    'attempt': attempt,
                    'ptcs': 0,
                    'threshold': threshold,
                    'passed': False,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                attempt_history.append(attempt_record)

                if attempt >= self.max_retries:
                    total_time = time.time() - start_time

                    result = EnforcementResult(
                        agent_name=agent_name,
                        success=False,
                        final_ptcs=0,
                        attempts=attempt,
                        threshold=threshold,
                        attempt_history=attempt_history,
                        total_time_seconds=round(total_time, 2),
                        timestamp=datetime.now().isoformat(),
                        final_output=None
                    )

                    raise RuntimeError(
                        f"Agent {agent_name} failed after {self.max_retries} attempts. "
                        f"Last error: {e}"
                    )

        # Should not reach here
        raise RuntimeError("Enforcement loop exited unexpectedly")

    # ========================================================================
    # Batch Enforcement
    # ========================================================================

    def enforce_batch_execution(
        self,
        agents: List[Dict[str, Any]],
        continue_on_failure: bool = False
    ) -> Dict[str, EnforcementResult]:
        """Execute multiple agents with pTCS enforcement.

        Args:
            agents: List of agent configurations:
                [
                    {
                        'name': 'agent-name',
                        'function': agent_function,
                        'threshold': 70,  # optional
                        'kwargs': {...}   # optional
                    },
                    ...
                ]
            continue_on_failure: Continue to next agent even if one fails

        Returns:
            Dict of {agent_name: EnforcementResult}

        Raises:
            RuntimeError: If any agent fails and continue_on_failure=False
        """
        results = {}

        self._log(f"\n{'='*70}")
        self._log(f"🔒 BATCH ENFORCEMENT: {len(agents)} agents")
        self._log(f"{'='*70}\n")

        for i, agent_config in enumerate(agents, 1):
            agent_name = agent_config['name']
            agent_function = agent_config['function']
            threshold = agent_config.get('threshold', self.thresholds['agent'])
            agent_kwargs = agent_config.get('kwargs', {})

            self._log(f"[{i}/{len(agents)}] Processing {agent_name}...")

            try:
                result = self.enforce_agent_execution(
                    agent_name=agent_name,
                    agent_function=agent_function,
                    threshold=threshold,
                    **agent_kwargs
                )

                results[agent_name] = result

                if result.success:
                    self._log(f"✅ {agent_name} completed successfully\n")
                else:
                    self._log(f"❌ {agent_name} failed\n")

                    if not continue_on_failure:
                        raise RuntimeError(
                            f"Agent {agent_name} failed. Stopping batch execution."
                        )

            except Exception as e:
                self._log(f"❌ {agent_name} raised exception: {e}\n")

                if not continue_on_failure:
                    raise

        return results

    # ========================================================================
    # Utilities
    # ========================================================================

    def _generate_retry_feedback(self, claim_results: list) -> dict:
        """Generate claim-level feedback for retry attempt."""
        low_claims = sorted(
            [c for c in claim_results if c.ptcs < 60],
            key=lambda c: c.ptcs
        )

        return {
            'total_claims': len(claim_results),
            'avg_ptcs': round(
                sum(c.ptcs for c in claim_results) / max(len(claim_results), 1), 1
            ),
            'low_confidence_claims': [
                {
                    'id': c.claim_id,
                    'ptcs': c.ptcs,
                    'type': c.claim_type,
                    'weakest': self._identify_weakest_component(c),
                }
                for c in low_claims[:5]
            ],
            'common_weaknesses': self._identify_common_weaknesses(claim_results),
        }

    def _identify_weakest_component(self, claim_result) -> str:
        """Identify the weakest scoring component of a claim."""
        components = {
            'source_quality': (claim_result.source_quality, 40),
            'claim_type': (claim_result.claim_type_appropriate, 25),
            'uncertainty': (claim_result.uncertainty_acknowledgment, 20),
            'grounding': (claim_result.grounding_depth, 15),
        }
        # Find component with lowest percentage of its max
        weakest = min(
            components.items(),
            key=lambda x: x[1][0] / x[1][1] if x[1][1] > 0 else 0
        )
        return weakest[0]

    def _identify_common_weaknesses(self, claim_results: list) -> list:
        """Identify common weaknesses across all claims."""
        issues = []
        count = max(len(claim_results), 1)
        avg_source = sum(c.source_quality for c in claim_results) / count
        avg_uncertainty = sum(c.uncertainty_acknowledgment for c in claim_results) / count
        avg_grounding = sum(c.grounding_depth for c in claim_results) / count

        if avg_source < 20:  # < 50% of max 40
            issues.append('sources: Add PRIMARY sources with DOI')
        if avg_uncertainty < 10:  # < 50% of max 20
            issues.append('uncertainty: Add uncertainty field and hedging language')
        if avg_grounding < 7.5:  # < 50% of max 15
            issues.append('grounding: Increase source count (target: 2+ per claim)')
        return issues

    def _format_retry_feedback(self, feedback: dict) -> str:
        """Format retry feedback as a clear text prompt prefix."""
        lines = ["## RETRY: Previous attempt failed quality check"]
        weakest = feedback.get("low_confidence_claims", [{}])
        if weakest:
            lines.append(f"- Weakest component: {weakest[0].get('weakest', 'unknown')}")
        lines.append(f"- Average confidence: {feedback.get('avg_ptcs', 0):.1f}")
        for weakness in feedback.get("common_weaknesses", []):
            lines.append(f"- Issue: {weakness}")
        lines.append("Please address these issues in your revised output.\n")
        return "\n".join(lines)

    def _write_feedback_sidecar(
        self, agent_name: str, attempt: int, feedback: dict
    ) -> None:
        """Write feedback to a sidecar JSON file for external consumers."""
        try:
            # Look for _temp dir relative to working directory
            temp_dir = Path.cwd() / "_temp"
            temp_dir.mkdir(parents=True, exist_ok=True)
            feedback_file = temp_dir / f"retry-feedback-{agent_name}.json"
            feedback_file.write_text(json.dumps({
                "agent": agent_name,
                "attempt": attempt,
                "feedback": feedback,
                "formatted": self._format_retry_feedback(feedback),
                "timestamp": datetime.now().isoformat(),
            }, ensure_ascii=False, indent=2))
            self._log(f"   Feedback written to: {feedback_file}")
        except OSError:
            pass  # Non-critical — best effort

    def _log_retry_feedback(self, feedback: dict):
        """Log retry feedback in a readable format."""
        self._log(f"\n📋 RETRY FEEDBACK:")
        self._log(f"   Average pTCS: {feedback['avg_ptcs']}/100")
        self._log(f"   Low-confidence claims: {len(feedback['low_confidence_claims'])}")
        for claim in feedback['low_confidence_claims']:
            self._log(f"     - {claim['id']}: {claim['ptcs']} pts "
                      f"(weakest: {claim['weakest']})")
        if feedback['common_weaknesses']:
            self._log(f"   Common issues:")
            for issue in feedback['common_weaknesses']:
                self._log(f"     - {issue}")

    def _log(self, message: str):
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(message)

    def save_enforcement_report(
        self,
        result: EnforcementResult,
        output_path: Path
    ):
        """Save enforcement result to JSON file.

        Args:
            result: EnforcementResult object
            output_path: Path to save report
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

        self._log(f"\n📄 Enforcement report saved: {output_path}")


# ============================================================================
# Enforcement Decorator
# ============================================================================

def enforce_ptcs(
    threshold: float = 70,
    max_retries: int = 3,
    extract_claims: Optional[Callable] = None
):
    """Decorator to enforce pTCS threshold on agent function.

    Usage:
        @enforce_ptcs(threshold=75, max_retries=3)
        def my_agent(**kwargs):
            # Agent logic
            return output

    Args:
        threshold: pTCS threshold (default 70)
        max_retries: Maximum retry attempts (default 3)
        extract_claims: Function to extract claims from output

    Returns:
        Decorated function with enforcement
    """
    def decorator(agent_function: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            enforcer = PTCSEnforcer(max_retries=max_retries)

            # Get agent name from function
            agent_name = agent_function.__name__

            result = enforcer.enforce_agent_execution(
                agent_name=agent_name,
                agent_function=lambda: agent_function(*args, **kwargs),
                threshold=threshold,
                extract_claims_function=extract_claims
            )

            return result.final_output

        return wrapper

    return decorator


# ============================================================================
# CLI Interface
# ============================================================================

def main():
    """CLI interface for pTCS enforcer."""
    import argparse

    parser = argparse.ArgumentParser(description="pTCS Enforcer")
    parser.add_argument("--test", action="store_true", help="Run test enforcement")

    args = parser.parse_args()

    if args.test:
        # Test enforcement with mock agent

        def mock_agent(quality: str = 'good', **_kwargs):
            """Mock agent that returns claims with varying quality."""
            if quality == 'poor':
                # Low quality claims (pTCS ~50)
                claims = [
                    {
                        'id': f'MOCK-{i}',
                        'text': f'Claim {i}',
                        'claim_type': 'SPECULATIVE',
                        'sources': [],  # No sources
                        'confidence': 40,
                        'uncertainty': ''
                    }
                    for i in range(5)
                ]
            elif quality == 'medium':
                # Medium quality claims (pTCS ~65)
                claims = [
                    {
                        'id': f'MOCK-{i}',
                        'text': f'Claim {i}',
                        'claim_type': 'INTERPRETIVE',
                        'sources': [{'type': 'SECONDARY'}],
                        'confidence': 60,
                        'uncertainty': 'Some uncertainty'
                    }
                    for i in range(5)
                ]
            else:  # good
                # Good quality claims (pTCS ~80)
                claims = [
                    {
                        'id': f'MOCK-{i}',
                        'text': f'Claim {i}',
                        'claim_type': 'FACTUAL',
                        'sources': [
                            {'type': 'PRIMARY', 'doi': '10.1234/test', 'verified': True}
                        ],
                        'confidence': 85,
                        'uncertainty': 'Well-established'
                    }
                    for i in range(5)
                ]

            return claims

        # Test 1: Good quality (should pass on first attempt)
        print("\n" + "="*70)
        print("TEST 1: Good quality agent (expected: PASS on attempt 1)")
        print("="*70)

        enforcer = PTCSEnforcer(max_retries=3, verbose=True)

        try:
            result = enforcer.enforce_agent_execution(
                agent_name="mock-agent-good",
                agent_function=mock_agent,
                threshold=70,
                quality='good'
            )
            print(f"\n✅ TEST 1 PASSED")
            print(f"   Attempts: {result.attempts}")
            print(f"   Final pTCS: {result.final_ptcs}")
        except Exception as e:
            print(f"\n❌ TEST 1 FAILED: {e}")

        # Test 2: Medium quality (should fail, then succeed if we lower threshold)
        print("\n" + "="*70)
        print("TEST 2: Medium quality agent (expected: FAIL at threshold 70)")
        print("="*70)

        try:
            result = enforcer.enforce_agent_execution(
                agent_name="mock-agent-medium",
                agent_function=mock_agent,
                threshold=70,
                quality='medium'
            )
            print(f"\n❌ TEST 2 UNEXPECTED PASS")
        except RuntimeError as e:
            print(f"\n✅ TEST 2 PASSED (expected failure)")
            print(f"   Error: {e}")

        return 0

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
