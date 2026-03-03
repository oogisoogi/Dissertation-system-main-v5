#!/usr/bin/env python3
"""Single Source of Truth for all workflow constants.

Every module that needs TOTAL_STEPS, PHASES, AGENT_STEP_MAP, PHASE_DIRS,
or TRANSLATION_TRIGGERS must import from this file. No other file should
define these values independently.

Usage:
    from workflow_constants import TOTAL_STEPS, PHASES, PHASE_DIRS
"""

# ---------------------------------------------------------------------------
# Total number of steps in the workflow
# ---------------------------------------------------------------------------
TOTAL_STEPS = 150

# ---------------------------------------------------------------------------
# Phase definitions: (phase_name, start_step, end_step)
# ---------------------------------------------------------------------------
PHASES = [
    ("phase0", 1, 18),
    ("phase1-wave1", 19, 34),
    ("phase1-wave2", 35, 50),
    ("phase1-wave3", 51, 66),
    ("phase1-wave4", 67, 74),
    ("phase1-wave5", 75, 82),
    ("hitl-2", 83, 88),
    ("phase2", 89, 108),
    ("phase3", 109, 132),
    ("phase4", 133, 146),
    ("completion", 147, 150),
]

# ---------------------------------------------------------------------------
# Phase → directory mapping (used by context_loader, performance_collector)
# ---------------------------------------------------------------------------
PHASE_DIRS = {
    "phase0": "00-session",
    "phase1": "01-literature",
    "phase2": "02-research-design",
    "phase3": "03-thesis",
    "phase4": "04-publication",
}

# Extended mapping including wave-level keys (used by performance_collector)
PHASE_DIRS_EXTENDED = {
    "phase0": "00-session",
    "phase1-wave1": "01-literature",
    "phase1-wave2": "01-literature",
    "phase1-wave3": "01-literature",
    "phase1-wave4": "01-literature",
    "phase1-wave5": "01-literature",
    "phase2-quantitative": "02-research-design",
    "phase2-qualitative": "02-research-design",
    "phase2-mixed": "02-research-design",
    "phase2-philosophical": "02-research-design",
    "phase3": "03-thesis",
    "phase4": "04-publication",
}

# ---------------------------------------------------------------------------
# Agent → step mapping (used by Hook for automatic checklist/session sync)
# ---------------------------------------------------------------------------
AGENT_STEP_MAP = {
    # Phase 0
    'topic-explorer': 9,

    # Phase 1 Wave 1
    'literature-searcher': 23,
    'seminal-works-analyst': 27,
    'trend-analyst': 31,
    'methodology-scanner': 33,

    # Phase 1 Wave 2
    'theoretical-framework-analyst': 38,
    'empirical-evidence-analyst': 42,
    'gap-identifier': 46,
    'variable-relationship-analyst': 49,

    # Phase 1 Wave 3
    'critical-reviewer': 54,
    'methodology-critic': 58,
    'limitation-analyst': 62,
    'future-direction-analyst': 65,

    # Phase 1 Wave 4
    'synthesis-agent': 70,
    'conceptual-model-builder': 73,

    # Phase 1 Wave 5
    'plagiarism-checker': 77,
    'unified-srcs-evaluator': 80,
    'research-synthesizer': 82,

    # Phase 2
    'hypothesis-developer': 95,
    'research-model-developer': 96,
    'sampling-designer': 97,
    'statistical-planner': 98,
    'paradigm-consultant': 99,
    'participant-selector': 100,
    'qualitative-data-designer': 101,
    'qualitative-analysis-planner': 102,
    'mixed-methods-designer': 103,
    'integration-strategist': 104,
    'philosophical-method-designer': 95,
    'source-text-selector': 96,
    'argument-construction-designer': 97,
    'philosophical-analysis-planner': 98,

    # Phase 3
    'thesis-architect': 113,
    'thesis-writer': None,  # Multiple steps (115, 117, 119, 121, 123)
    'thesis-reviewer': 125,

    # Phase 4
    'publication-strategist': 136,
    'manuscript-formatter': 142,

    # Simulation
    'simulation-controller': 150,
    'alphago-evaluator': 151,
    'autopilot-manager': 152,
    'thesis-writer-quick-rlm': None,  # Multiple chapters
}

# ---------------------------------------------------------------------------
# Wave/Phase boundaries that trigger auto-translation
# ---------------------------------------------------------------------------
TRANSLATION_TRIGGERS = {
    33: 'wave1',   # After methodology-scanner
    49: 'wave2',   # After variable-relationship-analyst
    65: 'wave3',   # After future-direction-analyst
    73: 'wave4',   # After conceptual-model-builder
    82: 'wave5',   # After research-synthesizer (Phase 1 complete)
    108: 'phase2',  # After Phase 2 completion
    132: 'phase3',  # After Phase 3 completion
    146: 'phase4',  # After Phase 4 completion
}


def get_phase_for_step(step: int) -> str:
    """Get the phase name for a given step number.

    Args:
        step: Step number (1-150)

    Returns:
        Phase name string

    Raises:
        ValueError: If step is out of range
    """
    if step < 1 or step > TOTAL_STEPS:
        raise ValueError(f"Step must be between 1 and {TOTAL_STEPS}, got {step}")

    for phase_name, start, end in PHASES:
        if start <= step <= end:
            return phase_name

    return "unknown"


def get_phase_dir(phase: str) -> str:
    """Get the directory name for a phase.

    Args:
        phase: Phase key (e.g. 'phase1', 'phase2')

    Returns:
        Directory name (e.g. '01-literature')

    Raises:
        ValueError: If phase is not recognized
    """
    if phase in PHASE_DIRS:
        return PHASE_DIRS[phase]
    if phase in PHASE_DIRS_EXTENDED:
        return PHASE_DIRS_EXTENDED[phase]
    raise ValueError(f"Unknown phase: {phase}. Valid: {list(PHASE_DIRS.keys())}")


# ---------------------------------------------------------------------------
# HITL checkpoint → step mapping (used by autopilot for auto-approval)
# ---------------------------------------------------------------------------
HITL_STEPS = {
    'HITL-0': 8,    # Phase 0: Initial setup approval
    'HITL-1': 18,   # Phase 0: Research question finalization
    'HITL-2': 83,   # Phase 1: Literature review approval
    'HITL-3': 89,   # Phase 2: Research type confirmation
    'HITL-4': 108,  # Phase 2: Research design approval
    'HITL-5': 109,  # Phase 3: Thesis format selection
    'HITL-6': 114,  # Phase 3: Outline approval
    'HITL-7': 125,  # Phase 3: Draft review
    'HITL-8': 146,  # Phase 4: Final approval
}

# ---------------------------------------------------------------------------
# Autopilot default settings (written to session.json when activated)
# ---------------------------------------------------------------------------
AUTOPILOT_DEFAULTS = {
    'enabled': False,
    'mode': 'full',        # full | semi | review-only
    'hitl_mode': 'manual',  # auto-approve | manual | review-only
    'started_at': None,
    'target': 'completion',  # completion | phase0 | phase1 | phase2 | phase3 | phase4
    'paused': False,
    'pause_reason': None,
}

# ---------------------------------------------------------------------------
# Simulation Mode Constants (Quick/Full thesis output)
# ---------------------------------------------------------------------------
SIMULATION_MODES = {
    'quick': {
        'label': 'Quick Simulation',
        'pages_min': 20,
        'pages_max': 30,
        'chapter_pages': {'ch1': 4, 'ch2': 6, 'ch3': 5, 'ch4': 5, 'ch5': 4},
        'estimated_hours': '1-2',
        'writer_agent': 'thesis-writer-quick-rlm',
    },
    'full': {
        'label': 'Full Simulation',
        'pages_min': 145,
        'pages_max': 155,
        'chapter_pages': {'ch1': 15, 'ch2': 45, 'ch3': 25, 'ch4': 35, 'ch5': 20},
        'estimated_hours': '5-7',
        'writer_agent': 'thesis-writer-rlm',
    },
    'both': {
        'label': 'Quick → Review → Full',
        'estimated_hours': '6-9',
    },
    'smart': {
        'label': 'Smart Mode',
        'uncertainty_thresholds': {'high': 0.7, 'low': 0.3},
    },
}
DEFAULT_SIMULATION_MODE = 'full'
VALID_SIMULATION_MODES = set(SIMULATION_MODES.keys())

# ===========================================================================
# Quality Gate Thresholds & Scoring Constants (SOT-A)
# ===========================================================================

# ---------------------------------------------------------------------------
# Quality Gate Thresholds
# ---------------------------------------------------------------------------
SRCS_DEFAULT_THRESHOLD = 75
PLAGIARISM_THRESHOLD = 15
DWC_THRESHOLD = 80

PTCS_THRESHOLDS = {
    "claim": 60, "agent": 70, "phase": 75, "workflow": 75,
}
PTCS_COLOR_BANDS = {
    "red": (0, 60), "yellow": (61, 70), "cyan": (71, 85), "green": (86, 100),
}
DUAL_CONFIDENCE_THRESHOLDS = {
    "ptcs_agent": 70, "ptcs_wave": 70, "ptcs_phase": 75,
    "srcs_wave": 75, "srcs_phase": 75,
}
DUAL_CONFIDENCE_WEIGHTS = {"ptcs": 0.60, "srcs": 0.40}
PHASE_WEIGHTS = {0: 0.05, 1: 0.30, 2: 0.20, 3: 0.35, 4: 0.10}

# ---------------------------------------------------------------------------
# SRCS Scoring
# ---------------------------------------------------------------------------
SRCS_WEIGHTS_BY_TYPE = {
    "default":       {"cs": 0.35, "gs": 0.35, "us": 0.10, "vs": 0.20},
    "quantitative":  {"cs": 0.35, "gs": 0.35, "us": 0.10, "vs": 0.20},
    "qualitative":   {"cs": 0.40, "gs": 0.25, "us": 0.15, "vs": 0.20},
    "philosophical": {"cs": 0.30, "gs": 0.30, "us": 0.15, "vs": 0.25},
    "slr":           {"cs": 0.40, "gs": 0.30, "us": 0.10, "vs": 0.20},
    "mixed":         {"cs": 0.35, "gs": 0.30, "us": 0.10, "vs": 0.25},
}
SRCS_GRADE_BANDS = {"A": 90, "B": 80, "C": 75, "D": 60}  # >= threshold
SRCS_AXIS_GRADE_BANDS = {"A": 85, "B": 70}  # per-axis grade (CS/GS/US/VS)

# ---------------------------------------------------------------------------
# Retry/Operational
# ---------------------------------------------------------------------------
MAX_RETRIES_AGENT = 3
MAX_RETRIES_WAVE = 3
MAX_RETRIES_PHASE = 2

# pTCS proxy weights (used when real claim-level pTCS is unavailable)
PTCS_PROXY_WEIGHTS = {"srcs": 0.70, "consistency": 0.30}

# ---------------------------------------------------------------------------
# Cross-Validator
# ---------------------------------------------------------------------------
CROSS_VALIDATOR_MIN_SHARED_WORDS = 2
CROSS_VALIDATOR_MIN_WORD_LENGTH = 4
CROSS_VALIDATOR_SEVERITY_WEIGHTS = {"HIGH": 15, "MEDIUM": 8, "LOW": 3}
CONTRADICTION_PATTERNS = [
    (r"positive\s+(?:effect|impact|relationship|correlation|association)",
     r"negative\s+(?:effect|impact|relationship|correlation|association)"),
    (r"(?:statistically\s+)?significant",
     r"(?:not|no)\s+(?:statistically\s+)?significant"),
    (r"(?:supports?|confirms?|validates?)",
     r"(?:contradicts?|refutes?|rejects?)"),
    (r"(?:increases?|improves?|enhances?)",
     r"(?:decreases?|reduces?|diminishes?)"),
    (r"(?:strong|robust|substantial)",
     r"(?:weak|fragile|negligible)"),
    # Korean contradiction patterns
    (r"긍정적\s*(?:영향|효과|관계)", r"부정적\s*(?:영향|효과|관계)"),
    (r"통계적으로\s*유의", r"통계적으로\s*유의하지\s*않"),
    (r"(?:지지|확인|검증)", r"(?:반박|부정|기각)"),
    (r"(?:증가|향상|강화)", r"(?:감소|저하|약화)"),
]
CROSS_VALIDATOR_STOPWORDS = {
    "the", "a", "an", "is", "was", "are", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "could",
    "should", "may", "might", "shall", "can", "to", "of", "in", "for",
    "on", "with", "at", "by", "from", "as", "into", "through", "during",
    "before", "after", "above", "below", "between", "under", "about",
    "and", "but", "or", "nor", "not", "no", "so", "if", "than", "that",
    "this", "these", "those", "it", "its", "they", "them", "their",
    "we", "our", "he", "she", "his", "her", "which", "what", "who",
    "study", "research", "results", "data", "analysis", "found",
    "showed", "indicated", "demonstrated", "revealed", "suggest",
}

# ---------------------------------------------------------------------------
# GRA Hallucination Firewall (bilingual)
# ---------------------------------------------------------------------------
GRA_CONFIDENCE_THRESHOLDS = {
    "FACTUAL": 95, "EMPIRICAL": 85, "THEORETICAL": 75,
    "METHODOLOGICAL": 80, "INTERPRETIVE": 70, "SPECULATIVE": 60,
}
HALLUCINATION_PATTERNS = {
    "BLOCK": [
        # Korean
        r"모든\s*연구가?\s*일치", r"항상\s*그렇", r"절대로",
        r"완벽하게", r"전혀\s*없", r"모두\s*동의",
        # English
        r"all\s+(?:research|studies|evidence)\s+(?:agrees?|confirms?|shows?)",
        r"(?:definitively|conclusively)\s+(?:proven|established|demonstrated)",
        r"without\s+any\s+exception",
        r"(?:absolutely|unquestionably|indisputably)\s+(?:certain|true|clear)",
        r"there\s+is\s+no\s+(?:doubt|question|debate)",
        r"every\s+(?:scholar|researcher|expert)\s+agrees?",
    ],
    "REQUIRE_SOURCE": [
        # Korean
        r"p\s*[<>=]\s*\.?\d+", r"효과크기\s*[drf]\s*=\s*[\d.]+",
        r"[rβ]\s*=\s*[\d.]+", r"\d+%의\s*분산",
        # English
        r"(?:effect\s+size|Cohen'?s?\s*d)\s*=\s*[\d.]+",
        r"(?:r|β|beta)\s*=\s*[\d.]+", r"\d+%\s*(?:of\s+)?(?:the\s+)?variance",
        r"(?:OR|RR|HR)\s*=\s*[\d.]+",
    ],
    "SOFTEN": [
        # Korean
        r"100\s*%", r"예외\s*없이", r"확실히", r"명백히", r"분명히",
        r"틀림없이", r"의심의\s*여지\s*없이",
        # English
        r"100\s*%\s*(?:of|certain|sure|agree)", r"without\s+(?:any\s+)?exception",
        r"(?:certainly|clearly|obviously|undoubtedly|undeniably)\s+\w+",
        r"it\s+is\s+(?:clear|obvious|evident|undeniable)\s+that",
        r"beyond\s+(?:any\s+)?(?:doubt|question)",
    ],
    "VERIFY": [
        # Korean
        r"일반적으로", r"대부분의?\s*연구", r"많은\s*연구", r"흔히",
        # English
        r"(?:generally|typically|usually|commonly|often)",
        r"(?:most|many|numerous)\s+(?:studies|researchers?|scholars?)",
        r"it\s+is\s+(?:widely|commonly|generally)\s+(?:accepted|known|recognized)",
        r"the\s+(?:majority|bulk)\s+of\s+(?:research|evidence|literature)",
    ],
}
# Overconfidence subset (used by srcs_evaluator US scoring)
OVERCONFIDENCE_PATTERNS = (
    HALLUCINATION_PATTERNS["BLOCK"] + HALLUCINATION_PATTERNS["SOFTEN"]
)

# ---------------------------------------------------------------------------
# Alert Thresholds (confidence_monitor)
# ---------------------------------------------------------------------------
ALERT_THRESHOLDS = {
    "claim_critical": 50, "claim_warning": 60,
    "agent_critical": 60, "agent_warning": 70,
}

# ---------------------------------------------------------------------------
# AGENT_OUTPUT_FILES: agent role → actual output filename (SOT-A)
# Verified against 5 completed projects' actual output files.
# ---------------------------------------------------------------------------
AGENT_OUTPUT_FILES = {
    # Wave 1 (Literature Search)
    "literature-searcher":           "01-literature-search-strategy.md",
    "seminal-works-analyst":         "02-seminal-works-analysis.md",
    "trend-analyst":                 "03-research-trend-analysis.md",
    "methodology-scanner":           "04-methodology-scan.md",
    # Wave 2 (Theoretical Analysis)
    "theoretical-framework-analyst": "05-theoretical-framework.md",
    "empirical-evidence-analyst":    "06-empirical-evidence-synthesis.md",
    "gap-identifier":                "07-research-gap-analysis.md",
    "variable-relationship-analyst": "08-variable-relationship-analysis.md",
    # Wave 3 (Critical Review)
    "critical-reviewer":             "09-critical-review.md",
    "methodology-critic":            "10-methodology-critique.md",
    "limitation-analyst":            "11-limitation-analysis.md",
    "future-direction-analyst":      "12-future-research-directions.md",
    # Wave 4 (Synthesis)
    "synthesis-agent":               "13-literature-synthesis.md",
    "conceptual-model-builder":      "14-conceptual-model.md",
    # Wave 5 (Quality Assurance)
    "plagiarism-checker":            "15-plagiarism-report.md",
    "unified-srcs-evaluator":        "quality-report.md",
    "research-synthesizer":          "research-synthesis.md",
}

_WAVE_AGENTS = {
    1: ["literature-searcher", "seminal-works-analyst",
        "trend-analyst", "methodology-scanner"],
    2: ["theoretical-framework-analyst", "empirical-evidence-analyst",
        "gap-identifier", "variable-relationship-analyst"],
    3: ["critical-reviewer", "methodology-critic",
        "limitation-analyst", "future-direction-analyst"],
    4: ["synthesis-agent", "conceptual-model-builder"],
    5: ["plagiarism-checker", "unified-srcs-evaluator",
        "research-synthesizer"],
}

# WAVE_FILES: derived from AGENT_OUTPUT_FILES (never define filenames here directly)
WAVE_FILES = {
    wave: [AGENT_OUTPUT_FILES[agent] for agent in agents]
    for wave, agents in _WAVE_AGENTS.items()
}
