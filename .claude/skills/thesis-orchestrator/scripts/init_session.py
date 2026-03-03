#!/usr/bin/env python3
"""Session initialization module for doctoral research workflow (v2.3.0).

CHANGELOG from v2.2.0:
- Added Mode F (proposal) to VALID_MODES
- Added Mode G (custom input) via entry_path parameter
- Added proposal_metadata to session schema
- Added entry_path and custom_preferences to research section
- Mode-specific folder creation (00-paper-based-design vs 00-proposal-analysis)
- VERSION constant used dynamically in valid_versions

This module handles the creation and management of research sessions,
including directory structure creation and session state management.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import path utilities
from path_utils import slugify, generate_working_dir_name, validate_path_consistency

# Import folder structure creator (updated)
from create_folder_structure import create_research_folder_structure

# Import citation style configuration (single source of truth)
from citation_style_config import (
    VALID_CITATION_STYLES,
    DEFAULT_CITATION_STYLE,
    get_citation_config,
    get_display_name,
)

# Import shared constants (single source of truth)
from workflow_constants import TOTAL_STEPS, DEFAULT_SIMULATION_MODE, VALID_SIMULATION_MODES

# Constants
VERSION = "2.3.0"
VALID_MODES = {"topic", "question", "review", "learning", "paper-upload", "proposal"}
VALID_RESEARCH_TYPES = {"quantitative", "qualitative", "mixed", "philosophical", None}
VALID_LANGUAGES = {"korean", "english", "bilingual"}
VALID_THESIS_FORMATS = {"traditional_5chapter", "three_paper", "monograph"}


def get_repo_root() -> Path:
    """Find repository root by searching for specific marker then .git.

    Prioritizes project-specific markers over generic .git to avoid
    finding parent repositories. Falls back to environment variable
    or hardcoded paths.

    Returns:
        Path: Absolute path to repository root
    """
    current = Path(__file__).resolve()

    # Method 1: Search for marker file/directory name (PRIORITIZED)
    for parent in [current] + list(current.parents):
        if (parent / 'Dissertation-system-main-v4').exists() or \
           (parent.name == 'Dissertation-system-main-v4'):
            return parent

    # Method 2: Search for .git directory
    for parent in [current] + list(current.parents):
        if (parent / '.git').exists():
            return parent

    # Method 3: Environment variable
    if 'THESIS_REPO_ROOT' in os.environ:
        return Path(os.environ['THESIS_REPO_ROOT'])

    # Method 4: Hardcoded fallback
    fallback = Path.home() / 'Desktop/AIagentsAutomation/Dissertation-system-main-v4'
    if fallback.exists():
        return fallback

    # Method 5: Relative from script location
    return Path(__file__).parent.parent.parent.parent


def get_current_timestamp() -> str:
    """Return current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def create_session(
    topic: str,
    mode: str,
    output_dir: Path,
    research_type: str | None = None,
    discipline: str | None = None,
    paper_path: str | None = None,
    citation_style: str | None = None,
    entry_path: str | None = None,
    custom_preferences: dict[str, Any] | None = None,
    simulation_mode: str | None = None,
) -> dict[str, Any]:
    """Create a new session structure with path consistency.

    Args:
        topic: Research topic or question
        mode: Input mode (topic, question, review, learning, paper-upload, proposal)
        output_dir: Already-created output directory path
        research_type: Research type (quantitative, qualitative, mixed, philosophical)
        discipline: Academic discipline
        paper_path: Path to uploaded paper (for paper-upload/proposal mode)
        citation_style: Citation style key (apa7, chicago17, mla9, harvard, ieee)
        entry_path: Entry path identifier (e.g., "custom" for Mode G)
        custom_preferences: Pre-parsed preferences from custom input (Mode G)
        simulation_mode: Simulation mode (quick, full, both, smart)

    Returns:
        A dictionary containing the session structure
    """
    timestamp = get_current_timestamp()
    topic_slug = slugify(topic)

    # Resolve citation style with validation
    style_key = citation_style if citation_style in VALID_CITATION_STYLES else DEFAULT_CITATION_STYLE
    citation_config = get_citation_config(style_key)

    session_data = {
        "version": VERSION,
        "working_dir": output_dir.name,  # NEW: Directory name
        "created_at": timestamp,
        "updated_at": timestamp,
        "research": {
            "topic": topic,
            "topic_slug": topic_slug,  # NEW: English slug
            "mode": mode,
            "type": research_type,
            "discipline": discipline,
            "research_questions": [],
            "hypotheses": [],
        },
        "workflow": {
            "current_phase": "phase0",
            "current_step": 1,
            "total_steps": TOTAL_STEPS,
            "last_checkpoint": None,
            "last_agent": None,
        },
        "paths": {  # NEW: Explicit path management
            "base_dir": str(output_dir.parent),
            "output_dir": output_dir.name,
            "absolute_path": str(output_dir.resolve()),
        },
        "options": {
            "literature_depth": "comprehensive",
            "theoretical_framework": "existing",
            "citation_style": style_key,
            "citation_config": citation_config,
            "language": "korean",
            "thesis_format": "traditional_5chapter",
            "simulation_mode": simulation_mode if simulation_mode in VALID_SIMULATION_MODES else DEFAULT_SIMULATION_MODE,
        },
        "quality": {
            "srcs_scores": [],
            "gra_validations": [],
            "plagiarism_checks": [],
        },
        "context_snapshots": [],
    }

    # Add entry_path if provided (e.g., "custom" for Mode G)
    if entry_path:
        session_data["research"]["entry_path"] = entry_path

    # Add custom_preferences if provided (Mode G)
    if custom_preferences and entry_path == "custom":
        session_data["research"]["custom_preferences"] = custom_preferences

    # Add paper metadata if in paper-upload mode
    if mode == "paper-upload" and paper_path:
        session_data["paper_metadata"] = {
            "original_path": paper_path,
            "uploaded_at": timestamp,
            "analysis_status": "pending",
        }

    # Add proposal metadata if in proposal mode
    if mode == "proposal" and paper_path:
        session_data["proposal_metadata"] = {
            "original_path": paper_path,
            "uploaded_at": timestamp,
            "analysis_status": "pending",
            "completeness_score": None,
            "extracted_plan": None,
        }

    return session_data


def save_session(session: dict[str, Any], path: Path) -> None:
    """Save session to a JSON file.

    Args:
        session: Session dictionary to save
        path: Path to save the session file
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session, f, ensure_ascii=False, indent=2)


def load_session(path: Path) -> dict[str, Any]:
    """Load session from a JSON file.

    Args:
        path: Path to the session file

    Returns:
        Session dictionary

    Raises:
        FileNotFoundError: If session file doesn't exist
    """
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def create_output_structure(base_dir: Path, research_title: str, mode: str = "topic") -> Path:
    """Create the output directory structure for a research project.

    Uses slugify to ensure consistent English directory naming.
    Mode-specific folders are created conditionally.

    Args:
        base_dir: Base directory for thesis output
        research_title: Title of the research project
        mode: Input mode (determines which special folders to create)

    Returns:
        Path to the created output directory
    """
    today = datetime.now().strftime("%Y-%m-%d")

    # Use slugify instead of sanitize_filename
    dir_name = generate_working_dir_name(research_title, today)

    # Create full path
    output_dir = base_dir / dir_name

    # Core folders (always created)
    folders = [
        "00-session",
        "01-literature",
        "02-research-design",
        "03-thesis",
        "04-publication",
    ]

    for folder in folders:
        (output_dir / folder).mkdir(parents=True, exist_ok=True)

    # Mode-specific folders (conditional)
    if mode == "paper-upload":
        (output_dir / "00-paper-based-design").mkdir(parents=True, exist_ok=True)
    elif mode == "proposal":
        (output_dir / "00-proposal-analysis").mkdir(parents=True, exist_ok=True)

    return output_dir


def ensure_archive_structure(repo_root: Path) -> None:
    """Ensure _archive/ directory structure exists at repo root.

    Creates _archive/references/ and _archive/obsolete/ directories,
    and a skeleton cleanup-manifest.json if missing. Idempotent.

    Args:
        repo_root: Repository root path
    """
    archive_dir = repo_root / "_archive"
    (archive_dir / "references").mkdir(parents=True, exist_ok=True)
    (archive_dir / "obsolete").mkdir(parents=True, exist_ok=True)

    manifest_path = archive_dir / "cleanup-manifest.json"
    if not manifest_path.exists():
        skeleton = {
            "version": "1.0.0",
            "created_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
            "description": "Tracks files moved from project root during cleanup.",
            "categories": {
                "references": {"description": "Useful documentation", "files": []},
                "obsolete": {"description": "Development artifacts safe to delete", "files": []},
            },
            "cleanup_status": {
                "moved_at": None,
                "deletion_approved": False,
                "deletion_approved_at": None,
                "retained_files": [],
            },
        }
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(skeleton, f, ensure_ascii=False, indent=2)


def validate_session(session: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a session structure.

    Args:
        session: Session dictionary to validate

    Returns:
        Tuple of (is_valid, list of error messages)
    """
    errors = []

    # Check required top-level fields
    required_fields = ["version", "working_dir", "research", "workflow", "paths", "options", "quality"]
    for field in required_fields:
        if field not in session:
            errors.append(f"Missing required field: {field}")

    if errors:
        return False, errors

    # Validate version
    valid_versions = {"1.0.0", "2.0.0", "2.1.0", "2.2.0", VERSION}
    if session["version"] not in valid_versions:
        errors.append(f"Invalid version: {session['version']}")

    # Validate paths section
    if "paths" in session:
        paths = session["paths"]
        if "output_dir" not in paths or "absolute_path" not in paths:
            errors.append("Missing required path fields")

    # Validate research section
    research = session.get("research", {})
    if research.get("mode") not in VALID_MODES:
        errors.append(f"Invalid mode: {research.get('mode')}")

    if research.get("type") not in VALID_RESEARCH_TYPES:
        errors.append(f"Invalid research type: {research.get('type')}")

    # Validate workflow section
    workflow = session.get("workflow", {})
    if not isinstance(workflow.get("current_step"), int) or workflow.get("current_step", 0) < 1:
        errors.append("current_step must be a positive integer")

    # Validate citation style (in options)
    options = session.get("options", {})
    citation_style = options.get("citation_style")
    if citation_style and citation_style not in VALID_CITATION_STYLES:
        errors.append(f"Invalid citation style: {citation_style}")

    return len(errors) == 0, errors


def create_checklist(output_dir: Path, research_type: str | None = None) -> Path:
    """Create the 150-step todo checklist.

    Delegates to checklist_manager.create_checklist() as the single source of truth,
    then marks step 1 as completed (session initialization).

    Args:
        output_dir: Output directory for the checklist
        research_type: Research type for conditional checklist entries (e.g. 'philosophical')

    Returns:
        Path to the created checklist file
    """
    from checklist_manager import create_checklist as _cm_create_checklist
    from checklist_manager import update_step_status

    checklist_path = _cm_create_checklist(output_dir, research_type=research_type)
    update_step_status(checklist_path, step=1, status="completed")
    return checklist_path


def initialize_workflow(
    topic: str,
    mode: str,
    base_dir: Path,
    research_type: str | None = None,
    discipline: str | None = None,
    paper_path: str | None = None,
    citation_style: str | None = None,
    entry_path: str | None = None,
    custom_preferences: dict[str, Any] | None = None,
    simulation_mode: str | None = None,
) -> Path:
    """Initialize a complete research workflow with path consistency.

    This is the main entry point for workflow initialization.
    Creates the output directory structure, session file, and checklist.

    Args:
        topic: Research topic or question
        mode: Input mode (topic, question, review, learning, paper-upload, proposal)
        base_dir: Base directory for thesis output
        research_type: Research type (quantitative, qualitative, mixed, philosophical)
        discipline: Academic discipline
        paper_path: Path to uploaded paper (for paper-upload/proposal mode)
        citation_style: Citation style key (apa7, chicago17, mla9, harvard, ieee)
        entry_path: Entry path identifier (e.g., "custom" for Mode G)
        custom_preferences: Pre-parsed preferences from custom input (Mode G)
        simulation_mode: Simulation mode (quick, full, both, smart)

    Returns:
        Path to the output directory
    """
    # ===== PATH VALIDATION (Tier 1 + Validation) =====
    # Convert to absolute path
    base_dir = base_dir.resolve()

    # Check if base_dir is inside skill directory (warning only)
    skill_dir = Path(__file__).parent.parent.resolve()
    if base_dir.is_relative_to(skill_dir):
        print(f"⚠️  WARNING: Output directory is inside skill directory!")
        print(f"   Skill dir: {skill_dir}")
        print(f"   Output dir: {base_dir}")
        print(f"   Consider using project root: {get_repo_root() / 'thesis-output'}")
        print()

    # Validate directory exists or can be created
    if base_dir.exists():
        if not base_dir.is_dir():
            raise ValueError(f"Base directory path exists but is not a directory: {base_dir}")
    else:
        # Try to create parent directory to verify writability
        try:
            base_dir.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            raise PermissionError(f"Cannot create base directory (permission denied): {base_dir}")
        except Exception as e:
            raise RuntimeError(f"Cannot create base directory: {base_dir}\nError: {e}")

    # Check write permissions
    if not os.access(base_dir, os.W_OK):
        raise PermissionError(f"Base directory is not writable: {base_dir}")

    print(f"✅ Path validation passed: {base_dir}")
    # ===== END PATH VALIDATION =====

    # Ensure _archive/ structure at repo root
    ensure_archive_structure(get_repo_root())

    # Create output directory structure (mode-aware)
    output_dir = create_output_structure(base_dir, topic, mode=mode)

    # Create session
    session = create_session(
        topic=topic,
        mode=mode,
        output_dir=output_dir,
        research_type=research_type,
        discipline=discipline,
        paper_path=paper_path,
        citation_style=citation_style,
        entry_path=entry_path,
        custom_preferences=custom_preferences,
        simulation_mode=simulation_mode,
    )

    # Copy uploaded paper if in paper-upload mode
    if mode == "paper-upload" and paper_path:
        import shutil
        paper_src = Path(paper_path)
        if paper_src.exists():
            paper_dest = output_dir / "00-paper-based-design" / paper_src.name
            shutil.copy2(paper_src, paper_dest)
            print(f"📄 논문 파일 복사됨: {paper_src.name} → {paper_dest}")
        else:
            print(f"⚠️  경고: 논문 파일을 찾을 수 없습니다: {paper_path}")

    # Copy proposal file if in proposal mode
    if mode == "proposal" and paper_path:
        import shutil
        proposal_src = Path(paper_path)
        if proposal_src.exists():
            proposal_dest = output_dir / "00-proposal-analysis" / proposal_src.name
            shutil.copy2(proposal_src, proposal_dest)
            print(f"📄 프로포절 파일 복사됨: {proposal_src.name} → {proposal_dest}")
        else:
            print(f"⚠️  경고: 프로포절 파일을 찾을 수 없습니다: {paper_path}")

    # Validate session
    is_valid, errors = validate_session(session)
    if not is_valid:
        raise ValueError(f"Invalid session structure: {errors}")

    # Save session to 00-session/
    session_path = output_dir / "00-session" / "session.json"
    save_session(session, session_path)

    # Validate path consistency
    is_consistent, error_msg = validate_path_consistency(
        session_path, output_dir.name
    )
    if not is_consistent:
        raise RuntimeError(f"Path consistency check failed: {error_msg}")

    # Create checklist in 00-session/
    create_checklist(output_dir / "00-session", research_type=research_type)

    # Print user-friendly output
    print("\n" + "=" * 70)
    print(f"🎯 워크플로우 초기화 완료 (v{VERSION})")
    print("=" * 70)
    print(f"📁 작업 디렉토리: {output_dir}")
    print(f"📄 세션 파일: {session_path}")
    print(f"✅ 체크리스트: {output_dir / '00-session' / 'todo-checklist.md'}")
    print(f"🔗 Topic Slug: {session['research']['topic_slug']}")
    print("\n💡 위 디렉토리에서 모든 작업이 진행됩니다.")
    print("💡 모든 에이전트가 동일한 디렉토리를 사용합니다.")
    print("=" * 70 + "\n")

    # Create .current-working-dir marker
    marker_file = base_dir / ".current-working-dir.txt"
    marker_file.write_text(str(output_dir), encoding='utf-8')

    return output_dir


def main():
    """Main entry point for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"Initialize a doctoral research workflow session (v{VERSION})"
    )
    parser.add_argument("topic", help="Research topic or question (or paper/proposal title)")
    parser.add_argument(
        "--mode",
        choices=sorted(VALID_MODES),
        default="topic",
        help="Input mode"
    )
    parser.add_argument(
        "--paper-path",
        help="Path to uploaded paper file (required for paper-upload mode)"
    )
    parser.add_argument(
        "--proposal-path",
        help="Path to proposal file (required for proposal mode)"
    )
    parser.add_argument(
        "--entry-path",
        help="Entry path identifier (e.g., 'custom' for Mode G free-form input)"
    )
    parser.add_argument(
        "--custom-preferences",
        help="JSON string of pre-parsed preferences from custom input (Mode G)"
    )
    parser.add_argument(
        "--base-dir",
        type=Path,
        default=get_repo_root() / "thesis-output",
        help="Base directory for output"
    )
    parser.add_argument(
        "--type",
        choices=["quantitative", "qualitative", "mixed", "philosophical"],
        help="Research type"
    )
    parser.add_argument(
        "--discipline",
        help="Academic discipline"
    )
    parser.add_argument(
        "--citation-style",
        choices=["apa7", "chicago17", "mla9", "harvard", "ieee"],
        default=None,
        help="Citation style (apa7, chicago17, mla9, harvard, ieee)"
    )
    parser.add_argument(
        "--simulation-mode",
        choices=["quick", "full", "both", "smart"],
        default=None,
        help="Simulation mode (quick, full, both, smart)"
    )

    args = parser.parse_args()

    # Validate paper-upload mode requirements
    if args.mode == "paper-upload" and not args.paper_path:
        parser.error("--paper-path is required when --mode is paper-upload")

    # Validate proposal mode requirements
    if args.mode == "proposal" and not args.proposal_path:
        parser.error("--proposal-path is required when --mode is proposal")

    # Resolve paper_path: use --proposal-path for proposal mode
    paper_path = args.paper_path
    if args.mode == "proposal":
        paper_path = args.proposal_path

    # Parse custom preferences JSON
    custom_preferences = None
    if args.custom_preferences:
        try:
            custom_preferences = json.loads(args.custom_preferences)
        except json.JSONDecodeError:
            parser.error("--custom-preferences must be valid JSON")

    try:
        output_dir = initialize_workflow(
            topic=args.topic,
            mode=args.mode,
            base_dir=args.base_dir,
            research_type=args.type,
            discipline=args.discipline,
            paper_path=paper_path,
            citation_style=args.citation_style,
            entry_path=args.entry_path,
            custom_preferences=custom_preferences,
            simulation_mode=args.simulation_mode,
        )

        print(f"✅ Success! Workflow initialized at: {output_dir}")
        print(f"Folder structure version: {VERSION}")

    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
