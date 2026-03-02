#!/usr/bin/env python3
"""
RLM Context Monitor Hook

Automatically detects when agents should use RLM mode based on:
1. Input context size exceeding thresholds
2. Task complexity indicating high information density
3. Agent type and workload characteristics

Based on "Recursive Language Models" (Zhang et al., 2025) - arXiv:2512.24601v1

Hook Event: PreToolUse
Triggers: Before Task tool execution with subagent_type
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple


# RLM activation thresholds (from paper Section 4)
RLM_CHAR_THRESHOLD = 100000  # ~25K tokens
RLM_FILE_COUNT_THRESHOLD = 4
RLM_TOTAL_SIZE_THRESHOLD = 200000  # Conservative for safety

# High information-density task types (from paper Section 3.1)
HIGH_DENSITY_TASKS = {
    'synthesis',           # Integrating multiple sources
    'screening',           # Filtering large datasets
    'validation',          # Cross-checking claims
    'aggregation',         # Combining partial results
    'comprehensive_analysis',
    'cross_validation',
    'literature_review',
    'plagiarism_check',
    'quality_evaluation'
}

# Agents that benefit most from RLM (Tier 1 + Tier 2 from design plan)
RLM_PRIORITY_AGENTS = {
    # Tier 1 (immediate)
    'synthesis-agent',
    'literature-searcher',
    'thesis-writer',

    # Tier 2 (medium-term)
    'unified-srcs-evaluator',
    'plagiarism-checker',
    'conceptual-model-builder',
    'variable-relationship-analyst',

    # Tier 3 (long-term)
    'cross-validator',
    'thesis-reviewer',
    'research-synthesizer'
}


def get_context_files(agent_name: str, working_dir: str) -> List[Dict[str, any]]:
    """
    Identify input files for a given agent based on naming conventions.

    Returns:
        List of dicts with 'path' and 'size' keys
    """
    files = []
    temp_dir = Path(working_dir) / "thesis-output" / "_temp"

    if not temp_dir.exists():
        return files

    # Pattern matching for agent input files
    patterns = {
        'synthesis-agent': [
            r'^\d+-.*\.md$',  # All Wave 1-3 outputs (01-literature-search.md, etc.)
        ],
        'literature-searcher': [
            r'^session\.json$',
            r'^topic-analysis\.md$',
        ],
        'thesis-writer': [
            r'^13-literature-synthesis\.md$',
            r'^14-conceptual-model\.md$',
            r'^.*-design\.md$',
        ],
        'unified-srcs-evaluator': [
            r'^.*-claims\.md$',
            r'^\d+-.*\.md$',
        ],
        'plagiarism-checker': [
            r'^13-literature-synthesis\.md$',
            r'^chapter-\d+\.md$',
        ],
        'conceptual-model-builder': [
            r'^13-literature-synthesis\.md$',
            r'^08-variable-relationship-analysis\.md$',
        ]
    }

    agent_patterns = patterns.get(agent_name, [r'.*\.md$'])

    for file_path in temp_dir.glob('*.md'):
        for pattern in agent_patterns:
            if re.match(pattern, file_path.name):
                try:
                    size = file_path.stat().st_size
                    files.append({
                        'path': str(file_path),
                        'size': size
                    })
                except Exception:
                    pass

    # Also check session.json
    session_file = temp_dir / 'session.json'
    if session_file.exists():
        try:
            size = session_file.stat().st_size
            files.append({
                'path': str(session_file),
                'size': size
            })
        except Exception:
            pass

    return files


def classify_task_complexity(agent_name: str, prompt: str) -> str:
    """
    Classify task complexity based on agent type and prompt keywords.

    Returns:
        'constant' | 'linear' | 'quadratic' (from paper Section 2.2)
    """
    prompt_lower = prompt.lower()

    # Quadratic complexity indicators (OOLONG-Pairs style)
    if any(keyword in prompt_lower for keyword in [
        'cross-reference', 'compare all', 'pairwise', 'validate against all',
        'contradiction', 'consistency check', 'cross-validation'
    ]):
        return 'quadratic'

    # Linear complexity indicators (OOLONG style)
    if any(keyword in prompt_lower for keyword in [
        'synthesize', 'aggregate', 'integrate', 'combine',
        'screen', 'filter', 'scan', 'review all'
    ]):
        return 'linear'

    # Constant complexity (S-NIAH style)
    return 'constant'


def estimate_information_density(files: List[Dict[str, any]], agent_name: str) -> float:
    """
    Estimate information density of input context.

    Returns:
        0.0-1.0 score (higher = more dense)
    """
    if not files:
        return 0.0

    total_size = sum(f['size'] for f in files)
    file_count = len(files)

    # Base density on file count and size
    density_score = 0.0

    # More files = higher density
    if file_count >= 10:
        density_score += 0.4
    elif file_count >= 5:
        density_score += 0.2

    # Large total size = higher density
    if total_size >= 500000:  # 500KB
        density_score += 0.4
    elif total_size >= 200000:  # 200KB
        density_score += 0.2

    # Agent-specific density adjustments
    if agent_name in RLM_PRIORITY_AGENTS:
        density_score += 0.2

    return min(density_score, 1.0)


def should_use_rlm(
    agent_name: str,
    prompt: str,
    working_dir: str
) -> Tuple[bool, Dict[str, any]]:
    """
    Determine if RLM mode should be activated.

    Returns:
        (should_activate, diagnostic_info)
    """
    diagnostic = {
        'agent_name': agent_name,
        'decision': False,
        'reason': [],
        'context_files': [],
        'total_chars': 0,
        'file_count': 0,
        'task_complexity': 'constant',
        'information_density': 0.0
    }

    # Check 1: Priority agent list
    is_priority_agent = agent_name in RLM_PRIORITY_AGENTS
    if is_priority_agent:
        diagnostic['reason'].append(f"Priority agent: {agent_name}")

    # Check 2: Get context files
    context_files = get_context_files(agent_name, working_dir)
    diagnostic['context_files'] = [f['path'] for f in context_files]
    diagnostic['file_count'] = len(context_files)

    total_size = sum(f['size'] for f in context_files)
    diagnostic['total_chars'] = total_size

    # Check 3: Task complexity
    task_complexity = classify_task_complexity(agent_name, prompt)
    diagnostic['task_complexity'] = task_complexity

    # Check 4: Information density
    info_density = estimate_information_density(context_files, agent_name)
    diagnostic['information_density'] = info_density

    # Decision logic (from paper Section 4 and design plan)
    activate = False

    # Rule 1: Context size threshold
    if total_size > RLM_CHAR_THRESHOLD:
        activate = True
        diagnostic['reason'].append(
            f"Context size ({total_size:,} chars) exceeds threshold ({RLM_CHAR_THRESHOLD:,})"
        )

    # Rule 2: File count threshold
    if len(context_files) >= RLM_FILE_COUNT_THRESHOLD:
        activate = True
        diagnostic['reason'].append(
            f"File count ({len(context_files)}) exceeds threshold ({RLM_FILE_COUNT_THRESHOLD})"
        )

    # Rule 3: High information density + priority agent
    if info_density >= 0.6 and is_priority_agent:
        activate = True
        diagnostic['reason'].append(
            f"High information density ({info_density:.2f}) for priority agent"
        )

    # Rule 4: Quadratic complexity tasks always use RLM
    if task_complexity == 'quadratic':
        activate = True
        diagnostic['reason'].append(
            f"Quadratic complexity task detected"
        )

    # Rule 5: Linear complexity + large context
    if task_complexity == 'linear' and total_size > 50000:
        activate = True
        diagnostic['reason'].append(
            f"Linear complexity with large context ({total_size:,} chars)"
        )

    diagnostic['decision'] = activate

    return activate, diagnostic


def inject_rlm_instructions(original_prompt: str, diagnostic: Dict[str, any]) -> str:
    """
    Inject RLM mode instructions into agent prompt.

    Returns:
        Modified prompt with RLM instructions prepended
    """
    context_files_str = '\n'.join([f"- {path}" for path in diagnostic['context_files']])

    rlm_header = f"""
# 🔄 RLM MODE ACTIVATED

**Reason**: {'; '.join(diagnostic['reason'])}

**Context Statistics**:
- Total characters: {diagnostic['total_chars']:,}
- File count: {diagnostic['file_count']}
- Task complexity: {diagnostic['task_complexity']}
- Information density: {diagnostic['information_density']:.2f}

**Input Files**:
{context_files_str}

**RLM Instructions**:

You MUST use RLM (Recursive Language Model) mode for this task. Follow these steps:

1. **Initialize RLM Environment**:
```python
from .claude.libs.rlm_core import RLMEnvironment, RLMPatterns, RLMOptimizer

# Load all input files as REPL variables
context_files = {{}}
for file_path in {diagnostic['context_files']}:
    with open(file_path, 'r', encoding='utf-8') as f:
        context_files[file_path] = f.read()

rlm = RLMEnvironment(
    context_data=context_files,
    max_recursion_depth=2,
    model_preference="haiku"  # Use Haiku for sub-calls to control costs
)

# Estimate cost before proceeding
cost_estimate = RLMOptimizer.estimate_cost(
    input_size={diagnostic['total_chars']},
    num_sub_calls=10,  # Adjust based on chunking strategy
    model="haiku"
)
print(f"Estimated cost: ${{cost_estimate['estimated_cost_usd']:.2f}}")
```

2. **Pre-Filter with Code** (Figure 4a pattern):
```python
# Use regex/keywords to filter relevant sections BEFORE sub-LM calls
relevant_sections = rlm.repl_env['grep_content'](
    content=context_files,
    pattern=r"[YOUR_PATTERN]"  # Customize based on task
)
print(f"Filtered {{len(relevant_sections)}} relevant sections")
```

3. **Chunk and Process** (Figure 4b pattern):
```python
# Combine filtered content
all_content = "\\n\\n".join(relevant_sections)

# Chunk intelligently
chunks = rlm.repl_env['chunk_by_size'](
    text=all_content,
    chunk_size=50000,  # 1/4 of sub-LM limit
    overlap=500
)

# Process each chunk recursively
partial_results = []
for i, chunk in enumerate(chunks):
    result = rlm.repl_env['llm_query'](
        prompt=f\"\"\"
        [YOUR TASK-SPECIFIC PROMPT]

        Chunk {{i+1}}/{{len(chunks)}}:
        {{chunk}}

        Output: [REQUIRED FORMAT]
        \"\"\"
    )
    partial_results.append(result)
    print(f"Processed chunk {{i+1}}/{{len(chunks)}}")
```

4. **Aggregate Results**:
```python
# Synthesize partial results into final output
final_result = rlm.repl_env['llm_query'](
    prompt=f\"\"\"
    Synthesize these partial results into final output:

    {{chr(10).join([f"=== Part {{i+1}} ===\\n{{r}}" for i, r in enumerate(partial_results)])}}

    Requirements:
    - [YOUR OUTPUT REQUIREMENTS]
    - GroundedClaim format (if applicable)
    - No information loss (<10% threshold)
    \"\"\"
)
```

5. **Output RLM Statistics**:
```python
print("=== RLM Statistics ===")
print(rlm.get_stats())

# Include in output file
rlm_stats = {{
    "total_sub_calls": rlm.stats['total_sub_calls'],
    "input_chars_processed": {diagnostic['total_chars']},
    "chunks_processed": len(chunks),
    "estimated_cost_usd": cost_estimate['estimated_cost_usd']
}}
```

**CRITICAL**: You MUST use the RLM workflow above. Standard processing will fail due to context window limitations.

---

# Original Task

{original_prompt}
"""

    return rlm_header.strip()


def hook(context: Dict[str, any]) -> Dict[str, any]:
    """
    PreToolUse hook that monitors context and activates RLM mode when appropriate.

    Args:
        context: Hook context with 'tool_name', 'tool_input', 'working_directory'

    Returns:
        Modified context with RLM instructions if applicable
    """
    tool_name = context.get('tool_name', '')
    tool_input = context.get('tool_input', {})
    working_dir = context.get('working_directory', os.getcwd())

    # Only intercept Task tool calls with subagent_type
    if tool_name != 'Task':
        return context

    subagent_type = tool_input.get('subagent_type', '')
    original_prompt = tool_input.get('prompt', '')

    if not subagent_type or not original_prompt:
        return context

    # Check if RLM should be activated
    should_activate, diagnostic = should_use_rlm(
        agent_name=subagent_type,
        prompt=original_prompt,
        working_dir=working_dir
    )

    # Early return if RLM not needed — skip logging entirely (v4: minimize I/O)
    if not should_activate:
        return context

    # Log diagnostic info (only when activated)
    log_dir = Path(working_dir) / "thesis-output" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)

    log_file = log_dir / "rlm-activation.log"
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"\n--- RLM Check: {subagent_type} ---\n")
        f.write(json.dumps(diagnostic, indent=2, ensure_ascii=False))
        f.write(f"\nDecision: ACTIVATE\n")

    # Inject RLM instructions if activated
    if should_activate:
        modified_prompt = inject_rlm_instructions(original_prompt, diagnostic)

        # Modify tool_input
        modified_input = tool_input.copy()
        modified_input['prompt'] = modified_prompt

        # Update context
        context['tool_input'] = modified_input

        print(f"🔄 RLM Mode activated for {subagent_type}")
        print(f"   Reason: {'; '.join(diagnostic['reason'][:2])}")  # Show first 2 reasons
        print(f"   Files: {diagnostic['file_count']}, Size: {diagnostic['total_chars']:,} chars")

    return context


if __name__ == '__main__':
    # Test mode
    test_context = {
        'tool_name': 'Task',
        'tool_input': {
            'subagent_type': 'synthesis-agent',
            'prompt': 'Synthesize all Wave 1-3 results into literature review draft.'
        },
        'working_directory': os.getcwd()
    }

    result = hook(test_context)
    print("\n=== Test Result ===")
    print(f"RLM activated: {'🔄 RLM MODE ACTIVATED' in result['tool_input']['prompt']}")
