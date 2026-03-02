#!/usr/bin/env python3
"""
Retry Enforcer Hook

Automatically retries failed agents up to MAX_RETRIES times.
Implements retry-until-pass logic for quality assurance.

Hook Event: PostToolUse
Triggers: After Task tool failure (error or low quality output)

Philosophy: MINIMALLY INVASIVE
- Does NOT modify workflow commands
- ONLY adds retry logic for failed agents
- Improves workflow resilience
"""

import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Retry configuration
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 0  # v4: Removed sleep(5) — no consuming process reads the retry signal

# Failure detection patterns
FAILURE_PATTERNS = [
    'error:',
    'failed to',
    'unable to',
    'could not',
    'exception:',
    'timeout',
    'api error',
    'rate limit'
]

# Quality thresholds for auto-retry
MIN_CONFIDENCE_SCORE = 60
MIN_OUTPUT_LENGTH = 500  # characters


def find_session_dir(working_dir: str) -> Optional[Path]:
    """Find current thesis session directory."""
    working_path = Path(working_dir)

    marker_file = working_path / "thesis-output" / ".current-working-dir.txt"
    if marker_file.exists():
        session_dir = marker_file.read_text().strip()
        return Path(session_dir)

    thesis_output = working_path / "thesis-output"
    if not thesis_output.exists():
        return None

    session_dirs = [d for d in thesis_output.iterdir() if d.is_dir() and d.name != '_temp']
    if not session_dirs:
        return None

    return max(session_dirs, key=lambda d: d.stat().st_mtime)


def load_retry_state(session_dir: Path, agent_name: str) -> Dict:
    """
    Load retry state for an agent.

    Returns:
        Dict with retry count and history
    """
    try:
        retry_file = session_dir / "00-session" / "retry-state.json"

        if not retry_file.exists():
            return {'count': 0, 'history': []}

        with open(retry_file, 'r', encoding='utf-8') as f:
            all_states = json.load(f)

        return all_states.get(agent_name, {'count': 0, 'history': []})

    except Exception:
        return {'count': 0, 'history': []}


def save_retry_state(session_dir: Path, agent_name: str, retry_state: Dict) -> None:
    """Save retry state for an agent."""
    try:
        retry_file = session_dir / "00-session" / "retry-state.json"

        # Load all states
        if retry_file.exists():
            with open(retry_file, 'r', encoding='utf-8') as f:
                all_states = json.load(f)
        else:
            all_states = {}

        # Update state for this agent
        all_states[agent_name] = retry_state

        # Save
        with open(retry_file, 'w', encoding='utf-8') as f:
            json.dump(all_states, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"   ⚠️  Failed to save retry state: {e}")


def detect_failure(tool_output: Dict) -> Optional[str]:
    """
    Detect if agent execution failed.

    Returns:
        Failure reason string if failed, None if success
    """
    # Check for explicit failure flag
    if not tool_output.get('success', True):
        return "Explicit failure flag"

    # Check output content
    output_content = str(tool_output).lower()

    for pattern in FAILURE_PATTERNS:
        if pattern in output_content:
            return f"Failure pattern detected: {pattern}"

    return None


def detect_low_quality(tool_output: Dict, agent_name: str) -> Optional[str]:
    """
    Detect if output quality is below threshold.

    Returns:
        Quality issue string if low quality, None if acceptable
    """
    # Check output length (heuristic for completeness)
    output_str = str(tool_output)
    if len(output_str) < MIN_OUTPUT_LENGTH:
        return f"Output too short: {len(output_str)} < {MIN_OUTPUT_LENGTH} chars"

    # Check for confidence score (if available)
    # This would parse pTCS or SRCS scores from output
    # Simplified for now
    if 'confidence' in output_str.lower():
        # Try to extract confidence score
        import re
        confidence_match = re.search(r'confidence[:\s]+(\d+)', output_str, re.IGNORECASE)
        if confidence_match:
            confidence = int(confidence_match.group(1))
            if confidence < MIN_CONFIDENCE_SCORE:
                return f"Confidence too low: {confidence} < {MIN_CONFIDENCE_SCORE}"

    return None


def should_retry(
    agent_name: str,
    retry_state: Dict,
    failure_reason: Optional[str],
    quality_issue: Optional[str]
) -> bool:
    """
    Determine if agent should be retried.

    Returns:
        True if should retry, False otherwise
    """
    # Check retry limit
    if retry_state['count'] >= MAX_RETRIES:
        return False

    # Retry if there's a failure or quality issue
    return failure_reason is not None or quality_issue is not None


def trigger_retry(
    agent_name: str,
    original_prompt: str,
    retry_count: int,
    failure_reason: str
) -> Dict:
    """
    Trigger agent retry with enhanced prompt.

    Returns:
        Dict with retry configuration
    """
    enhanced_prompt = f"""
# 🔄 RETRY ATTEMPT {retry_count}/{MAX_RETRIES}

**Previous Attempt Failed**:
{failure_reason}

**Instructions for Retry**:
1. Review the failure reason above
2. Adjust your approach to avoid the same failure
3. Ensure output meets all quality requirements:
   - Minimum {MIN_OUTPUT_LENGTH} characters
   - Confidence score ≥ {MIN_CONFIDENCE_SCORE}
   - GroundedClaim YAML schema (if applicable)
   - Complete and well-structured response

4. If you encounter the same issue, try an alternative approach

---

# Original Task

{original_prompt}
"""

    return {
        'should_retry': True,
        'retry_count': retry_count,
        'enhanced_prompt': enhanced_prompt,
        'delay_seconds': RETRY_DELAY_SECONDS
    }


def log_retry_attempt(session_dir: Path, agent_name: str, retry_info: Dict) -> None:
    """Log retry attempt."""
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "retry-log.txt"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Agent: {agent_name}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Retry Attempt: {retry_info['retry_count']}/{MAX_RETRIES}\n")
            f.write(f"Reason: {retry_info.get('reason', 'Unknown')}\n")
            f.write(f"{'='*60}\n")

    except Exception:
        pass


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PostToolUse hook for automatic retry enforcement.

    This hook runs AFTER Task tool completion and checks for failures
    or low quality. If detected and retry limit not exceeded, it triggers
    a retry with enhanced prompt.

    Args:
        context: Hook context

    Returns:
        Modified context with retry configuration (if applicable)
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    tool_output = context.get('tool_output', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only process Task tool completions
    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')
    original_prompt = tool_input.get('prompt', '')

    # Normalize agent name (remove suffixes)
    normalized_agent = subagent_type
    for suffix in ['-rlm', '-validated', '-parallel']:
        if normalized_agent.endswith(suffix):
            normalized_agent = normalized_agent[:-len(suffix)]
            break

    if not normalized_agent:
        return context

    # Find session directory
    session_dir = find_session_dir(working_dir)
    if not session_dir:
        return context

    # Load retry state
    retry_state = load_retry_state(session_dir, normalized_agent)

    # Detect failure or low quality
    failure_reason = detect_failure(tool_output)
    quality_issue = detect_low_quality(tool_output, subagent_type)

    # Determine if should retry
    if not should_retry(normalized_agent, retry_state, failure_reason, quality_issue):
        # No retry needed or limit exceeded
        if retry_state['count'] >= MAX_RETRIES:
            print(f"\n⚠️  Agent {subagent_type} failed after {MAX_RETRIES} retries")
            print(f"   Last reason: {failure_reason or quality_issue}")
            print(f"   💡 Manual intervention required\n")

        return context

    # Trigger retry
    retry_count = retry_state['count'] + 1
    reason = failure_reason or quality_issue

    print(f"\n{'='*60}")
    print(f"🔄 Retry Enforcer: {normalized_agent}")
    print(f"{'='*60}")
    print(f"   Attempt: {retry_count}/{MAX_RETRIES}")
    print(f"   Reason: {reason}")

    # Create retry configuration
    retry_config = trigger_retry(
        normalized_agent,
        original_prompt,
        retry_count,
        reason
    )

    # Update retry state
    retry_state['count'] = retry_count
    retry_state['history'].append({
        'attempt': retry_count,
        'timestamp': datetime.now().isoformat(),
        'reason': reason
    })

    save_retry_state(session_dir, normalized_agent, retry_state)
    log_retry_attempt(session_dir, normalized_agent, {
        'retry_count': retry_count,
        'reason': reason
    })

    print(f"{'='*60}\n")

    # Modify context to trigger retry
    # Note: This is a signal to the orchestrator, not actual re-execution
    # Actual retry would need orchestrator support
    context['retry_requested'] = True
    context['retry_config'] = retry_config

    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'literature-searcher',
            'prompt': 'Search for literature...'
        },
        'tool_output': {
            'success': False,
            'error': 'API timeout'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Retry requested: {result.get('retry_requested', False)}")
    if result.get('retry_config'):
        print(f"Retry count: {result['retry_config']['retry_count']}")
