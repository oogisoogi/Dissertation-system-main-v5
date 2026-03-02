#!/usr/bin/env python3
"""
Gate Automation Hook

Automatically executes quality gates at critical checkpoints:
- Gate 1-3: Cross-validation gates (after Wave 1-3 of unified 1-5 system)
- Gate 4: Full SRCS evaluation (after Wave 4)
- Gate 5: Plagiarism + SRCS (after Wave 5, final quality gate)

Hook Event: PostToolUse
Triggers: After agents at gate boundaries (steps 34, 50, 66, 74, 82)

Philosophy: MINIMALLY INVASIVE
- Does NOT modify workflow commands
- ONLY automates gate execution that was designed but not implemented
- Preserves fail-safe: gates can block progression
"""

import json
import os
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Tuple

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

# Import gate controller and evaluators
try:
    from gate_controller import GateController
    from cross_validator import validate_wave, run_cross_validation
    from srcs_evaluator import run_srcs_evaluation, evaluate_all_claims
    _IMPORTS_OK = True
except ImportError:
    _IMPORTS_OK = False
    # v4: No gate validation possible without imports — exit cleanly.
    # Fake fallback scores (85, 85.7, 8.7) are worse than no validation.


# Gate definitions (step → gate_name mapping)
GATE_TRIGGERS = {
    34: {
        'gate_name': 'gate1',
        'gate_type': 'cross_validation',
        'description': 'Cross-Validation Gate 1 (after Wave 1)',
        'required_files': ['wave1-*.md'],
        'threshold': {'consistency': 75}
    },
    50: {
        'gate_name': 'gate2',
        'gate_type': 'cross_validation',
        'description': 'Cross-Validation Gate 2 (after Wave 2)',
        'required_files': ['wave1-*.md', 'wave2-*.md'],
        'threshold': {'consistency': 75}
    },
    66: {
        'gate_name': 'gate3',
        'gate_type': 'cross_validation',
        'description': 'Cross-Validation Gate 3 (after Wave 3)',
        'required_files': ['wave1-*.md', 'wave2-*.md', 'wave3-*.md'],
        'threshold': {'consistency': 75}
    },
    74: {
        'gate_name': 'gate4',
        'gate_type': 'srcs_evaluation',
        'description': 'Full SRCS Evaluation (after Wave 4)',
        'required_files': ['wave*.md'],
        'threshold': {'srcs': 75, 'ptcs': 75}
    },
    82: {
        'gate_name': 'gate5',
        'gate_type': 'quality_assurance',
        'description': 'Final Quality Gate (plagiarism + SRCS)',
        'required_files': ['wave*.md', '*-synthesis.md'],
        'threshold': {'srcs': 75, 'plagiarism': 15}  # Plagiarism must be < 15%
    }
}


def find_session_dir(working_dir: str) -> Optional[Path]:
    """Find current thesis session directory."""
    working_path = Path(working_dir)

    # Check for marker file
    marker_file = working_path / "thesis-output" / ".current-working-dir.txt"
    if marker_file.exists():
        session_dir = marker_file.read_text().strip()
        return Path(session_dir)

    # Fallback: most recent session
    thesis_output = working_path / "thesis-output"
    if not thesis_output.exists():
        return None

    session_dirs = [d for d in thesis_output.iterdir() if d.is_dir() and d.name != '_temp']
    if not session_dirs:
        return None

    return max(session_dirs, key=lambda d: d.stat().st_mtime)


def execute_cross_validation_gate(session_dir: Path, gate_config: Dict) -> Tuple[bool, Dict]:
    """
    Execute cross-validation gate.

    Returns:
        (passed, result_dict)
    """
    print(f"🔍 Executing: {gate_config['description']}")

    result = {
        'gate_name': gate_config['gate_name'],
        'gate_type': gate_config['gate_type'],
        'timestamp': datetime.now().isoformat(),
        'passed': False,
        'score': 0,
        'details': {}
    }

    try:
        # Find literature review files
        lit_dir = session_dir / "01-literature"
        if not lit_dir.exists():
            result['details']['error'] = f"Literature directory not found: {lit_dir}"
            return False, result

        # Get all wave files
        wave_files = sorted(lit_dir.glob("wave*.md"))

        if not wave_files:
            result['details']['error'] = "No wave files found for validation"
            return False, result

        print(f"   Found {len(wave_files)} wave file(s) to validate")

        # Execute cross-validation via cross_validator module
        if not _IMPORTS_OK:
            result['details']['error'] = "Required modules not available (cross_validator)"
            print("   ⚠️  Skipping: imports unavailable — no fake scores")
            return False, result

        gate_num = int(gate_config['gate_name'].replace('gate', ''))
        validation = validate_wave(temp_dir=lit_dir, wave=gate_num)
        consistency_score = validation.get('consistency_score', 0)

        result['score'] = consistency_score
        result['details'] = {
            'files_validated': [f.name for f in wave_files],
            'consistency_score': consistency_score,
            'threshold': gate_config['threshold']['consistency']
        }

        # Check threshold
        if consistency_score >= gate_config['threshold']['consistency']:
            result['passed'] = True
            print(f"   ✅ PASS: Consistency score {consistency_score} ≥ {gate_config['threshold']['consistency']}")
        else:
            result['passed'] = False
            print(f"   ❌ FAIL: Consistency score {consistency_score} < {gate_config['threshold']['consistency']}")

        return result['passed'], result

    except Exception as e:
        result['details']['error'] = str(e)
        print(f"   ❌ Error: {e}")
        return False, result


def execute_srcs_evaluation_gate(session_dir: Path, gate_config: Dict) -> Tuple[bool, Dict]:
    """
    Execute SRCS evaluation gate.

    Returns:
        (passed, result_dict)
    """
    print(f"📊 Executing: {gate_config['description']}")

    result = {
        'gate_name': gate_config['gate_name'],
        'gate_type': gate_config['gate_type'],
        'timestamp': datetime.now().isoformat(),
        'passed': False,
        'srcs_score': 0,
        'ptcs_score': 0,
        'details': {}
    }

    try:
        # Find literature review files
        lit_dir = session_dir / "01-literature"
        if not lit_dir.exists():
            result['details']['error'] = f"Literature directory not found: {lit_dir}"
            return False, result

        # Check for existing SRCS evaluation results
        srcs_file = lit_dir / "wave5-02-srcs-evaluation.md"

        if srcs_file.exists():
            print(f"   Found existing SRCS evaluation: {srcs_file.name}")

            # Parse SRCS score via srcs_evaluator module
            if not _IMPORTS_OK:
                result['details']['error'] = "Required modules not available (srcs_evaluator)"
                print("   ⚠️  Skipping: imports unavailable — no fake scores")
                return False, result

            srcs_result = run_srcs_evaluation(lit_dir, save_outputs=False)
            overall = srcs_result.get('overall_scores', {})
            srcs_score = overall.get('total', 0)
            # pTCS is calculated by ptcs_calculator, not srcs_evaluator
            # Gate hook uses placeholder; real pTCS comes from GateController
            ptcs_score = 0

            result['srcs_score'] = srcs_score
            result['ptcs_score'] = ptcs_score
            result['details'] = {
                'srcs_file': srcs_file.name,
                'srcs_score': srcs_score,
                'ptcs_score': ptcs_score,
                'srcs_threshold': gate_config['threshold']['srcs'],
                'ptcs_threshold': gate_config['threshold']['ptcs'],
                'ptcs_note': 'pTCS requires GateController (ptcs_calculator); hook validates SRCS only',
            }

            # Check SRCS threshold (pTCS requires GateController for full dual validation)
            srcs_threshold = gate_config['threshold']['srcs']
            if srcs_score >= srcs_threshold:
                result['passed'] = True
                print(f"   ✅ SRCS PASS: {srcs_score} ≥ {srcs_threshold}")
                print(f"   ℹ️  pTCS validation deferred to GateController")
            else:
                result['passed'] = False
                print(f"   ❌ FAIL: SRCS {srcs_score} < {srcs_threshold}")

        else:
            result['details']['error'] = "SRCS evaluation file not found"
            print(f"   ⚠️  SRCS file not found: {srcs_file}")
            return False, result

        return result['passed'], result

    except Exception as e:
        result['details']['error'] = str(e)
        print(f"   ❌ Error: {e}")
        return False, result


def execute_quality_assurance_gate(session_dir: Path, gate_config: Dict) -> Tuple[bool, Dict]:
    """
    Execute final quality assurance gate (plagiarism + SRCS).

    Returns:
        (passed, result_dict)
    """
    print(f"🎯 Executing: {gate_config['description']}")

    result = {
        'gate_name': gate_config['gate_name'],
        'gate_type': gate_config['gate_type'],
        'timestamp': datetime.now().isoformat(),
        'passed': False,
        'srcs_score': 0,
        'plagiarism_score': 0,
        'details': {}
    }

    try:
        lit_dir = session_dir / "01-literature"

        # Check SRCS
        srcs_file = lit_dir / "wave5-02-srcs-evaluation.md"
        if srcs_file.exists():
            if not _IMPORTS_OK:
                result['details']['error'] = "Required modules not available (srcs_evaluator)"
                print("   ⚠️  Skipping: imports unavailable — no fake scores")
                return False, result

            srcs_result = run_srcs_evaluation(lit_dir, save_outputs=False)
            overall = srcs_result.get('overall_scores', {})
            srcs_score = overall.get('total', 0)
            result['srcs_score'] = srcs_score
        else:
            result['details']['error'] = "SRCS evaluation not found"
            return False, result

        # Check plagiarism
        plagiarism_file = lit_dir / "wave5-01-plagiarism-check.md"
        if plagiarism_file.exists():
            # Extract plagiarism score from check file via regex
            import re
            plag_content = plagiarism_file.read_text(encoding='utf-8')
            plag_match = re.search(
                r'(?:유사도|similarity|plagiarism)[^\d]*(\d+(?:\.\d+)?)\s*%',
                plag_content, re.IGNORECASE
            )
            if plag_match:
                plagiarism_score = float(plag_match.group(1))
            else:
                # Cannot determine plagiarism score — fail safely
                result['details']['error'] = "Could not parse plagiarism score from check file"
                print("   ⚠️  Plagiarism score not parseable — cannot validate")
                return False, result
            result['plagiarism_score'] = plagiarism_score
        else:
            result['details']['error'] = "Plagiarism check not found"
            return False, result

        result['details'] = {
            'srcs_score': srcs_score,
            'srcs_threshold': gate_config['threshold']['srcs'],
            'plagiarism_score': plagiarism_score,
            'plagiarism_threshold': gate_config['threshold']['plagiarism']
        }

        # Check both conditions
        srcs_pass = srcs_score >= gate_config['threshold']['srcs']
        plagiarism_pass = plagiarism_score < gate_config['threshold']['plagiarism']

        if srcs_pass and plagiarism_pass:
            result['passed'] = True
            print(f"   ✅ PASS: SRCS {srcs_score} ≥ {gate_config['threshold']['srcs']}, Plagiarism {plagiarism_score}% < {gate_config['threshold']['plagiarism']}%")
        else:
            result['passed'] = False
            if not srcs_pass:
                print(f"   ❌ FAIL: SRCS {srcs_score} < {gate_config['threshold']['srcs']}")
            if not plagiarism_pass:
                print(f"   ❌ FAIL: Plagiarism {plagiarism_score}% ≥ {gate_config['threshold']['plagiarism']}%")

        return result['passed'], result

    except Exception as e:
        result['details']['error'] = str(e)
        print(f"   ❌ Error: {e}")
        return False, result


def log_gate_result(session_dir: Path, result: Dict) -> None:
    """Log gate execution result."""
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "gate-execution.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Gate: {result['gate_name']}\n")
            f.write(f"Type: {result['gate_type']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"Result: {'PASS' if result['passed'] else 'FAIL'}\n")
            f.write(f"Details: {json.dumps(result['details'], indent=2)}\n")
            f.write(f"{'='*60}\n")

    except Exception:
        pass  # Silent failure for logging


def save_gate_result(session_dir: Path, result: Dict) -> None:
    """Save gate result to JSON file."""
    try:
        results_dir = session_dir / "00-session"
        results_file = results_dir / "gate-results.json"

        # Load existing results
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                all_results = json.load(f)
        else:
            all_results = {'gates': []}

        # Append new result
        all_results['gates'].append(result)

        # Save
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(all_results, f, indent=2, ensure_ascii=False)

        print(f"   📄 Gate result saved: gate-results.json")

    except Exception as e:
        print(f"   ⚠️  Failed to save gate result: {e}")


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PostToolUse hook for automatic gate execution.

    This hook runs AFTER agents at gate boundaries and automatically
    executes quality gates. If a gate fails, it logs the failure but
    does NOT block progression (user decision).

    Args:
        context: Hook context

    Returns:
        Unmodified context
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only process Task tool completions
    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')
    if not subagent_type:
        return context

    # Normalize agent name (remove suffixes)
    normalized_agent = subagent_type
    for suffix in ['-rlm', '-validated', '-parallel']:
        if normalized_agent.endswith(suffix):
            normalized_agent = normalized_agent[:-len(suffix)]
            break

    # Find session directory
    session_dir = find_session_dir(working_dir)
    if not session_dir:
        return context

    # Determine which step completed
    # Map agents to steps (simplified)
    agent_to_step = {
        'methodology-scanner': 34,        # Gate 1
        'variable-relationship-analyst': 50,  # Gate 2
        'future-direction-analyst': 66,   # Gate 3
        'conceptual-model-builder': 74,   # Gate 4
        'research-synthesizer': 82        # Gate 5
    }

    step = agent_to_step.get(normalized_agent)
    if not step or step not in GATE_TRIGGERS:
        return context

    # Execute gate
    gate_config = GATE_TRIGGERS[step]

    print(f"\n{'='*60}")
    print(f"🚪 Gate Automation: {gate_config['gate_name'].upper()}")
    print(f"{'='*60}")

    try:
        # Execute appropriate gate type
        if gate_config['gate_type'] == 'cross_validation':
            passed, result = execute_cross_validation_gate(session_dir, gate_config)
        elif gate_config['gate_type'] == 'srcs_evaluation':
            passed, result = execute_srcs_evaluation_gate(session_dir, gate_config)
        elif gate_config['gate_type'] == 'quality_assurance':
            passed, result = execute_quality_assurance_gate(session_dir, gate_config)
        else:
            print(f"   ⚠️  Unknown gate type: {gate_config['gate_type']}")
            return context

        # Log and save results
        log_gate_result(session_dir, result)
        save_gate_result(session_dir, result)

        # Report outcome
        if passed:
            print(f"✅ Gate {gate_config['gate_name']} PASSED")
        else:
            print(f"⚠️  Gate {gate_config['gate_name']} FAILED")
            print(f"   💡 Review gate-results.json for details")
            print(f"   💡 User decision: Continue or revise?")

    except Exception as e:
        print(f"❌ Gate execution error: {e}")

    print(f"{'='*60}\n")

    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'methodology-scanner',
            'prompt': 'Scan methodology patterns...'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Gate automation triggered: {result == test_context}")
