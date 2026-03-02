#!/usr/bin/env python3
"""
Context Recovery Hook

Automatically recovers workflow context after context resets or session resumption.
Enables long-running workflows to span multiple Claude Code sessions.

Hook Event: PreToolUse
Triggers: Before Task tool execution when resuming from previous session

Philosophy: MINIMALLY INVASIVE
- Does NOT modify workflow commands
- ONLY rebuilds context from saved state
- Enables seamless workflow resumption
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, List

# Add scripts directory to path
SCRIPT_DIR = Path(__file__).parent.parent.parent / "skills" / "thesis-orchestrator" / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))


# Resume-triggering commands
RESUME_COMMANDS = {
    '/thesis:resume',
    'thesis:resume',
    'resume-workflow'
}


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


def load_session_state(session_dir: Path) -> Optional[Dict]:
    """Load session state from session.json."""
    try:
        session_file = session_dir / "00-session" / "session.json"
        if not session_file.exists():
            return None

        with open(session_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    except Exception as e:
        print(f"⚠️  Failed to load session state: {e}")
        return None


def load_checklist_state(session_dir: Path) -> Optional[Dict]:
    """Load checklist state to determine last completed step."""
    try:
        checklist_file = session_dir / "00-session" / "todo-checklist.md"
        if not checklist_file.exists():
            return None

        with open(checklist_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Count completed primary steps only (exclude indented sub-items)
        import re
        completed_steps = []
        for match in re.finditer(r'^- \[[xX]\] (\d+)\.', content, re.MULTILINE):
            completed_steps.append(int(match.group(1)))
        completed = len(completed_steps)

        return {
            'total_completed': completed,
            'last_completed_step': max(completed_steps) if completed_steps else 0,
            'completed_steps': completed_steps
        }

    except Exception as e:
        print(f"⚠️  Failed to load checklist state: {e}")
        return None


def build_recovery_context(session_dir: Path) -> Dict:
    """
    Build comprehensive context for workflow resumption.

    Returns:
        Dictionary with recovered context
    """
    context = {
        'session_dir': str(session_dir),
        'recovery_timestamp': datetime.now().isoformat(),
        'recovered': False,
        'research_question': None,
        'current_phase': None,
        'current_step': 0,
        'completed_work': {},
        'next_action': None
    }

    # Load session state
    session_state = load_session_state(session_dir)
    if session_state:
        context['research_question'] = session_state.get('research', {}).get('topic')
        context['current_phase'] = session_state.get('workflow', {}).get('current_phase')
        context['current_step'] = session_state.get('workflow', {}).get('current_step', 0)
        context['recovered'] = True

    # Load checklist state
    checklist_state = load_checklist_state(session_dir)
    if checklist_state:
        context['last_completed_step'] = checklist_state['last_completed_step']
        context['completed_steps'] = checklist_state['completed_steps']

    # Identify completed work
    completed_work = {}

    # Check Phase 1 (Literature Review)
    lit_dir = session_dir / "01-literature"
    if lit_dir.exists():
        lit_files = list(lit_dir.glob("wave*.md"))
        if lit_files:
            completed_work['phase1'] = {
                'status': 'in_progress' if len(lit_files) < 15 else 'completed',
                'files': [f.name for f in lit_files],
                'file_count': len(lit_files)
            }

    # Check Phase 2 (Research Design)
    design_dir = session_dir / "02-research-design"
    if design_dir.exists():
        design_files = list(design_dir.glob("*.md"))
        if design_files:
            completed_work['phase2'] = {
                'status': 'completed',
                'files': [f.name for f in design_files]
            }

    # Check Phase 3 (Thesis)
    thesis_dir = session_dir / "03-thesis"
    if thesis_dir.exists():
        chapter_files = list(thesis_dir.glob("chapter*.md"))
        if chapter_files:
            completed_work['phase3'] = {
                'status': 'in_progress' if len(chapter_files) < 5 else 'completed',
                'chapters': [f.name for f in chapter_files],
                'chapter_count': len(chapter_files)
            }

    context['completed_work'] = completed_work

    # Determine next action
    if context['current_step'] <= 82:
        context['next_action'] = 'Continue Phase 1 (Literature Review)'
    elif context['current_step'] <= 108:
        context['next_action'] = 'Continue Phase 2 (Research Design)'
    elif context['current_step'] <= 132:
        context['next_action'] = 'Continue Phase 3 (Thesis Writing)'
    elif context['current_step'] <= 146:
        context['next_action'] = 'Continue Phase 4 (Publication Strategy)'
    else:
        context['next_action'] = 'Workflow complete'

    return context


def inject_recovery_context(original_prompt: str, recovery_context: Dict) -> str:
    """
    Inject recovery context into prompt for resumed agents.

    Returns:
        Modified prompt with context prepended
    """
    if not recovery_context['recovered']:
        return original_prompt

    recovery_header = f"""
# 🔄 CONTEXT RECOVERY

**Session Resumption Detected**

**Research Question**: {recovery_context['research_question']}

**Current Progress**:
- Phase: {recovery_context['current_phase']}
- Step: {recovery_context['current_step']} / 150
- Last completed: Step {recovery_context.get('last_completed_step', 0)}

**Completed Work**:
"""

    for phase, details in recovery_context['completed_work'].items():
        recovery_header += f"\n- {phase.upper()}: {details['status']}"
        if 'file_count' in details:
            recovery_header += f" ({details['file_count']} files)"
        elif 'chapter_count' in details:
            recovery_header += f" ({details['chapter_count']} chapters)"

    recovery_header += f"""

**Next Action**: {recovery_context['next_action']}

**Instructions for Resumed Execution**:
1. Review the completed work in: {recovery_context['session_dir']}
2. Continue from the current step without repeating completed work
3. Maintain consistency with previous outputs
4. Use existing files as context for your task

---

# Original Task

{original_prompt}
"""

    return recovery_header.strip()


def log_recovery(session_dir: Path, recovery_context: Dict) -> None:
    """Log context recovery event."""
    try:
        log_dir = session_dir / "00-session"
        log_file = log_dir / "context-recovery.log"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"Recovery Timestamp: {recovery_context['recovery_timestamp']}\n")
            f.write(f"Research Question: {recovery_context['research_question']}\n")
            f.write(f"Current Step: {recovery_context['current_step']}\n")
            f.write(f"Current Phase: {recovery_context['current_phase']}\n")
            f.write(f"Next Action: {recovery_context['next_action']}\n")
            f.write(f"Completed Work: {json.dumps(recovery_context['completed_work'], indent=2)}\n")
            f.write(f"{'='*60}\n")

    except Exception:
        pass


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PreToolUse hook for automatic context recovery.

    This hook runs BEFORE Task tool execution and injects recovered
    context when resuming a workflow after context reset.

    Args:
        context: Hook context

    Returns:
        Modified context with recovery info (if applicable)
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only process Task tool calls
    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')
    original_prompt = tool_input.get('prompt', '')

    if not subagent_type or not original_prompt:
        return context

    # Check if this is a resume scenario
    # Heuristic: if prompt contains resume keywords or session dir exists
    is_resume = any(keyword in original_prompt.lower() for keyword in ['resume', 'continue', 'restart'])

    # OR check if session exists and has progress > 0
    session_dir = find_session_dir(working_dir)
    if session_dir:
        session_state = load_session_state(session_dir)
        if session_state:
            current_step = session_state.get('workflow', {}).get('current_step', 0)
            if current_step > 1:  # Session has made progress
                is_resume = True

    if not is_resume:
        return context  # Not a resume scenario, no action needed

    # Build recovery context
    if not session_dir:
        return context  # Can't recover without session

    # Timestamp guard: prevent re-triggering within 60 seconds (v4)
    import tempfile
    guard_file = Path(tempfile.gettempdir()) / "dissertation-recovery-timestamp"
    now = datetime.now().timestamp()
    if guard_file.exists():
        try:
            last_recovery = float(guard_file.read_text().strip())
            if now - last_recovery < 60:
                return context  # Too soon since last recovery
        except (ValueError, OSError):
            pass
    try:
        guard_file.write_text(str(now))
    except OSError:
        pass

    print(f"\n{'='*60}")
    print(f"🔄 Context Recovery Initiated")
    print(f"{'='*60}")

    try:
        recovery_context = build_recovery_context(session_dir)

        print(f"   Session: {session_dir.name}")
        print(f"   Research: {recovery_context['research_question'][:80]}...")
        print(f"   Progress: Step {recovery_context['current_step']}/150")
        print(f"   Phase: {recovery_context['current_phase']}")

        # Log recovery
        log_recovery(session_dir, recovery_context)

        # Inject recovery context into prompt
        modified_prompt = inject_recovery_context(original_prompt, recovery_context)

        # Modify tool_input
        modified_input = tool_input.copy()
        modified_input['prompt'] = modified_prompt

        # Update context
        context['tool_input'] = modified_input

        print(f"   ✅ Context recovered and injected")
        print(f"   Next: {recovery_context['next_action']}")

    except Exception as e:
        print(f"   ⚠️  Recovery failed: {e}")
        print(f"   Continuing without context injection")

    print(f"{'='*60}\n")

    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'literature-searcher',
            'prompt': 'Resume literature search from previous session...'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"Context modified: {result['tool_input']['prompt'] != test_context['tool_input']['prompt']}")
