#!/usr/bin/env python3
"""Validated Executor - Wrapper for Safe Agent Execution.

This module provides validation-wrapped execution for thesis workflow agents.
It is completely independent and does not modify existing code.

Design Principles:
- Additive-Only: Wraps existing execution, doesn't modify it
- Independent: Can be used optionally via environment variable
- Fail-Fast: Raises errors immediately when validation fails
- Non-invasive: Can be removed without affecting existing workflow

Usage:
    # Option 1: Environment variable
    export USE_VALIDATION=true

    # Option 2: Direct usage
    from validated_executor import ValidatedExecutor
    executor = ValidatedExecutor(working_dir)
    executor.execute_step(115, agent_function)
"""

from pathlib import Path
from typing import Callable, Any, Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime
import os
import sys

# Import our independent validator
from workflow_validator import (
    WorkflowValidator,
    DependencyValidator,
    ValidationError,
    DependencyError,
    ValidationResult
)


# ============================================================================
# Execution Result Data Class
# ============================================================================

@dataclass
class ExecutionResult:
    """Result of validated execution."""
    success: bool
    step: int
    agent_name: str
    execution_time: float
    pre_validation: ValidationResult
    post_validation: ValidationResult
    error: Optional[Exception] = None

    def __str__(self) -> str:
        if self.success:
            return (
                f"✅ Step {self.step} ({self.agent_name}) executed successfully\n"
                f"   Execution time: {self.execution_time:.2f}s"
            )
        else:
            return (
                f"❌ Step {self.step} ({self.agent_name}) failed\n"
                f"   Error: {self.error}"
            )


# ============================================================================
# Main Validated Executor Class
# ============================================================================

class ValidatedExecutor:
    """Executes workflow steps with validation before and after.

    This executor wraps agent execution with:
    1. Pre-execution dependency checking
    2. Agent execution
    3. Post-execution output validation
    4. Fail-fast error handling

    It is completely independent and can be enabled/disabled via
    environment variable USE_VALIDATION.

    Usage:
        executor = ValidatedExecutor(working_dir)
        result = executor.execute_step(
            step=115,
            agent_function=lambda: thesis_writer_chapter1(),
            agent_name="thesis-writer-ch1"
        )
    """

    def __init__(self, working_dir: Path, fail_fast: bool = True):
        """Initialize validated executor.

        Args:
            working_dir: Absolute path to workflow working directory
            fail_fast: If True, raise errors immediately on failure
        """
        self.working_dir = Path(working_dir)
        self.fail_fast = fail_fast

        # Initialize validators
        self.output_validator = WorkflowValidator(working_dir)
        self.dependency_validator = DependencyValidator(working_dir)

        # Execution history
        self.execution_history: List[ExecutionResult] = []

        # Statistics
        self.total_steps = 0
        self.successful_steps = 0
        self.failed_steps = 0

    def execute_step(
        self,
        step: int,
        agent_function: Callable[[], Any],
        agent_name: str,
        skip_pre_validation: bool = False,
        skip_post_validation: bool = False
    ) -> ExecutionResult:
        """Execute a workflow step with validation.

        This is the main execution method that wraps agent execution with:
        1. Pre-execution dependency validation
        2. Agent execution
        3. Post-execution output validation

        Args:
            step: Step number (1-150)
            agent_function: Function to execute (typically a task agent)
            agent_name: Name of the agent for logging
            skip_pre_validation: Skip dependency checking (for initial steps)
            skip_post_validation: Skip output validation (for info-only steps)

        Returns:
            ExecutionResult with detailed execution information

        Raises:
            ValidationError: If fail_fast=True and validation fails
            DependencyError: If fail_fast=True and dependencies not met
        """
        import time

        self.total_steps += 1
        start_time = time.time()

        print(f"\n{'='*70}")
        print(f"🔍 VALIDATED EXECUTION: Step {step} - {agent_name}")
        print(f"{'='*70}\n")

        # Phase 1: Pre-execution validation (dependency check)
        print(f"[1/3] Pre-execution validation...")

        if not skip_pre_validation:
            try:
                self.dependency_validator.enforce_dependencies(step)
                print(f"✅ Dependencies satisfied for step {step}")
                pre_validation = ValidationResult(
                    success=True,
                    step=step,
                    missing_files=[],
                    timestamp=datetime.now(),
                    message=f"Dependencies satisfied"
                )
            except DependencyError as e:
                print(f"❌ Dependency check failed: {e}")
                pre_validation = ValidationResult(
                    success=False,
                    step=step,
                    missing_files=[],
                    timestamp=datetime.now(),
                    message=str(e)
                )
                if self.fail_fast:
                    raise

                # Return failed result
                execution_time = time.time() - start_time
                result = ExecutionResult(
                    success=False,
                    step=step,
                    agent_name=agent_name,
                    execution_time=execution_time,
                    pre_validation=pre_validation,
                    post_validation=ValidationResult(
                        success=False,
                        step=step,
                        missing_files=[],
                        timestamp=datetime.now(),
                        message="Skipped due to dependency failure"
                    ),
                    error=e
                )
                self.execution_history.append(result)
                self.failed_steps += 1
                return result
        else:
            print(f"⏭️  Pre-validation skipped for step {step}")
            pre_validation = ValidationResult(
                success=True,
                step=step,
                missing_files=[],
                timestamp=datetime.now(),
                message="Skipped"
            )

        # Phase 2: Agent execution
        print(f"\n[2/3] Executing agent: {agent_name}...")

        try:
            agent_result = agent_function()
            print(f"✅ Agent execution completed")
        except Exception as e:
            print(f"❌ Agent execution failed: {e}")
            execution_time = time.time() - start_time

            post_validation = ValidationResult(
                success=False,
                step=step,
                missing_files=[],
                timestamp=datetime.now(),
                message="Skipped due to execution failure"
            )

            result = ExecutionResult(
                success=False,
                step=step,
                agent_name=agent_name,
                execution_time=execution_time,
                pre_validation=pre_validation,
                post_validation=post_validation,
                error=e
            )
            self.execution_history.append(result)
            self.failed_steps += 1

            if self.fail_fast:
                raise

            return result

        # Phase 3: Post-execution validation (output check)
        print(f"\n[3/3] Post-execution validation...")

        if not skip_post_validation:
            try:
                self.output_validator.enforce_step(step)
                print(f"✅ Required outputs validated for step {step}")
                post_validation = ValidationResult(
                    success=True,
                    step=step,
                    missing_files=[],
                    timestamp=datetime.now(),
                    message="All required outputs present"
                )
            except ValidationError as e:
                print(f"❌ Output validation failed: {e}")
                post_validation = ValidationResult(
                    success=False,
                    step=step,
                    missing_files=[],
                    timestamp=datetime.now(),
                    message=str(e)
                )

                execution_time = time.time() - start_time
                result = ExecutionResult(
                    success=False,
                    step=step,
                    agent_name=agent_name,
                    execution_time=execution_time,
                    pre_validation=pre_validation,
                    post_validation=post_validation,
                    error=e
                )
                self.execution_history.append(result)
                self.failed_steps += 1

                if self.fail_fast:
                    raise

                return result
        else:
            print(f"⏭️  Post-validation skipped for step {step}")
            post_validation = ValidationResult(
                success=True,
                step=step,
                missing_files=[],
                timestamp=datetime.now(),
                message="Skipped"
            )

        # Success!
        execution_time = time.time() - start_time

        result = ExecutionResult(
            success=True,
            step=step,
            agent_name=agent_name,
            execution_time=execution_time,
            pre_validation=pre_validation,
            post_validation=post_validation
        )

        self.execution_history.append(result)
        self.successful_steps += 1

        print(f"\n{'='*70}")
        print(f"✅ VALIDATED EXECUTION COMPLETE: Step {step}")
        print(f"   Execution time: {execution_time:.2f}s")
        print(f"{'='*70}\n")

        return result

    def execute_phase(
        self,
        phase: int,
        agent_mappings: Dict[int, Tuple[Callable, str]]
    ) -> Dict[int, ExecutionResult]:
        """Execute all steps in a phase with validation.

        Args:
            phase: Phase number (0-4)
            agent_mappings: Dictionary mapping step_number -> (agent_function, agent_name)

        Returns:
            Dictionary mapping step_number -> ExecutionResult
        """
        print(f"\n{'#'*70}")
        print(f"📋 EXECUTING PHASE {phase} WITH VALIDATION")
        print(f"{'#'*70}\n")

        results = {}

        for step, (agent_func, agent_name) in sorted(agent_mappings.items()):
            result = self.execute_step(step, agent_func, agent_name)
            results[step] = result

            if not result.success and self.fail_fast:
                print(f"\n⚠️  Stopping phase execution due to failure at step {step}")
                break

        return results

    def get_statistics(self) -> Dict[str, Any]:
        """Get execution statistics.

        Returns:
            Dictionary with execution statistics
        """
        return {
            "total_steps": self.total_steps,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "success_rate": (self.successful_steps / self.total_steps * 100) if self.total_steps > 0 else 0,
            "execution_history": self.execution_history
        }

    def print_summary(self):
        """Print execution summary."""
        stats = self.get_statistics()

        print(f"\n{'='*70}")
        print(f"📊 EXECUTION SUMMARY")
        print(f"{'='*70}")
        print(f"Total steps executed: {stats['total_steps']}")
        print(f"Successful: {stats['successful_steps']}")
        print(f"Failed: {stats['failed_steps']}")
        print(f"Success rate: {stats['success_rate']:.1f}%")
        print(f"{'='*70}\n")


# ============================================================================
# Convenience Functions
# ============================================================================

def should_use_validation() -> bool:
    """Check if validation should be used based on environment variable.

    Note: validation_config.py declares default="true" but we keep "false"
    here for backward compatibility. Changing to "true" would activate
    validation in all environments that haven't run enable-validation.sh,
    potentially surfacing hidden failures in existing pipelines.
    Use enable-validation.sh / disable-validation.sh to opt in/out.

    Returns:
        True if USE_VALIDATION=true, False otherwise
    """
    return os.environ.get("USE_VALIDATION", "false").lower() in ["true", "1", "yes"]


def create_executor(working_dir: Path, fail_fast: bool = True) -> ValidatedExecutor:
    """Create a validated executor if enabled, otherwise return None.

    This is a convenience function for opt-in validation.

    Args:
        working_dir: Absolute path to workflow working directory
        fail_fast: If True, raise errors immediately on failure

    Returns:
        ValidatedExecutor if USE_VALIDATION=true, None otherwise
    """
    if should_use_validation():
        print(f"✅ Validation enabled (USE_VALIDATION=true)")
        return ValidatedExecutor(working_dir, fail_fast)
    else:
        print(f"⏭️  Validation disabled (USE_VALIDATION not set)")
        return None


# ============================================================================
# CLI Interface (for manual testing)
# ============================================================================

def main():
    """CLI interface for manual testing."""
    import argparse

    parser = argparse.ArgumentParser(description="Test validated executor")
    parser.add_argument("working_dir", type=Path, help="Path to working directory")
    parser.add_argument("--step", type=int, required=True, help="Step to execute")
    parser.add_argument("--agent-name", type=str, default="test-agent", help="Agent name")
    parser.add_argument("--no-fail-fast", action="store_true", help="Don't fail fast")

    args = parser.parse_args()

    executor = ValidatedExecutor(args.working_dir, fail_fast=not args.no_fail_fast)

    # Dummy agent function
    def dummy_agent():
        print(f"  Executing dummy agent for step {args.step}...")
        return {"status": "completed"}

    result = executor.execute_step(args.step, dummy_agent, args.agent_name)

    print(f"\n{result}")

    return 0 if result.success else 1


if __name__ == "__main__":
    sys.exit(main())
