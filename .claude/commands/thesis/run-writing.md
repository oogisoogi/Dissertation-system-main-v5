---
description: 논문 작성 파이프라인 실행. 아웃라인 설계부터 장별 집필, 품질 검토까지 수행합니다.
context: fork
agent: general-purpose
---

# 논문 작성 파이프라인 실행

## 역할

이 커맨드는 **Phase 3 (Writing) 파이프라인**을 실행합니다.

## 전제 조건

- Phase 2 (Research Design) 완료
- HITL-4 승인 완료
- HITL-5 (논문 형식/인용 스타일) 선택 완료

## 실행 순서

### Step 0: ⭐ Load Doctoral-Writing Skill (MANDATORY - NEW)

**Before any writing begins, the doctoral-writing skill is automatically loaded.**

```bash
# Automatically verify doctoral-writing skill availability
✅ doctoral-writing skill loaded
   - SKILL.md: Available
   - references/:
     • clarity-checklist.md: Available
     • common-issues.md: Available
     • before-after-examples.md: Available
     • discipline-guides.md: Available
```

**All subsequent agents (@thesis-architect, @thesis-writer, @thesis-reviewer) inherit this skill context.**

**Purpose**:
- Ensures consistent writing quality across all chapters
- Provides foundational clarity and conciseness principles
- Mandatory compliance enforced by thesis-reviewer (80+ threshold)

**No user action required** - automatic system integration.

---

### Step 0.5: ⭐ Simulation Mode Routing (MANDATORY — Deterministic Python)

**결정론적 Python 스크립트로 실행 경로를 결정합니다. LLM 판단 없음.**

> Design Principle: "Tasks requiring exact, 100% reproducible results must be Python code."
> — validate_gate.py와 동일한 원칙 적용

```bash
# 결정론적 라우팅: simulation_router.py가 JSON 실행 계획을 반환
cd $(git rev-parse --show-toplevel) && \
python3 .claude/skills/thesis-orchestrator/scripts/simulation_router.py \
  --dir "thesis-output/<session-dir>"
```

**출력 예시 (JSON):**
```json
{
  "simulation_mode": "quick",
  "resolved_mode": "quick",
  "execution_path": "quick",
  "writer_agent": "thesis-writer-quick-rlm",
  "use_simulation_controller": true,
  "skip_outline": true,
  "page_targets": {"ch1": 4, "ch2": 6, "ch3": 5, "ch4": 5, "ch5": 4},
  "quality_thresholds": {"ptcs_min": 75, "srcs_min": 75, "dwc_min": 80, "plagiarism_max_percent": 15},
  "steps": [
    {"order": 1, "agent": "simulation-controller", "action": "write", "args": {"mode": "quick", "phase": "phase3"}},
    {"order": 2, "agent": "thesis-reviewer", "action": "review", "args": {"dwc_threshold": 80}},
    {"order": 3, "agent": "plagiarism-checker", "action": "check"},
    {"order": 4, "agent": null, "action": "integrate", "output": "thesis-final.md"},
    {"order": 5, "agent": null, "action": "export-docx"}
  ]
}
```

**라우팅 후 동작:**

| `execution_path` | 동작 | 비고 |
|-------------------|------|------|
| `"full"` | 아래 Step 1부터 진행 (기존 경로 100% 보존) | 기본값, 하위 호환성 |
| `"quick"` | JSON의 `steps` 배열 순서대로 에이전트 실행 | simulation-controller → thesis-reviewer(DWC 80+) → plagiarism-checker → integrate → export |
| `"both"` | JSON의 `phases` 배열 순서대로 (Quick → HITL → Full) | Phase A: Quick, Phase B: 사용자 검토, Phase C: Full |

**⚠️ 품질 기준은 모든 모드에서 동일합니다** (`quality_thresholds` 참조):
- pTCS ≥ 75, SRCS ≥ 75, DWC ≥ 80, Plagiarism < 15%

**⚠️ "smart" 모드는 `simulation_router.py`가 불확실성을 결정론적으로 계산하여 quick/full/both 중 하나로 자동 해소합니다** (`smart_resolution` 필드 참조).

**Quick/Both 경로 완료 후**: HITL-7 (초안 검토) → Phase 4 (Publication)로 진행

---

#### Full Execution Path (`execution_path == "full"`)

**기존 경로를 100% 그대로 유지합니다. 아래 Step 1부터 진행합니다.**

---

### Step 1: 아웃라인 설계
```
@thesis-architect → thesis-outline.md
```
→ HITL-6 (아웃라인 승인)

### Step 2: 장별 집필 (반복)

**Each chapter follows this process:**

```
Chapter 1:
  @thesis-writer → chapter-1-introduction.md
    ✅ Applies doctoral-writing principles:
       - Clarity: Clear subject-verb structure
       - Conciseness: Sentences <25 words (guideline)
       - Academic Rigor: Evidence-based claims
       - Logical Flow: Clear transitions
    ✅ References doctoral-writing/references/ as needed

  @thesis-reviewer → review-report-ch1.md
    ✅ Evaluates 6 criteria (including doctoral-writing compliance)
    ✅ Doctoral-Writing Compliance Score: must be 80+
    ✅ If < 80, automatic FAIL → revision required

  → HITL (장 검토)
    ✅ User reviews thesis-reviewer's report
    ✅ User verifies doctoral-writing compliance
    ✅ User approves or requests revision

Chapter 2:
  [Same process as Chapter 1]

Chapter 3:
  [Same process as Chapter 1]

Chapter 4:
  [Same process as Chapter 1]

Chapter 5:
  [Same process as Chapter 1]
```

**Quality Gates at Each Chapter:**
1. **Writer compliance**: thesis-writer applies doctoral-writing principles
2. **Reviewer verification**: thesis-reviewer scores doctoral-writing compliance (must be 80+)
3. **User approval**: HITL checkpoint confirms quality

**Pass Criteria per Chapter:**
- Doctoral-Writing Compliance ≥ 80 (NON-NEGOTIABLE)
- Overall Quality Score ≥ 75
- All 6 criteria meet individual thresholds

### Step 3: 최종 표절 검사
```
@plagiarism-checker → final-plagiarism-report.md
```

### Step 4: 최종 통합
```
모든 장 통합 → thesis-final.md
```
→ HITL-7 (초안 검토)

### Step 5: Word 문서 생성
```
/thesis:export-docx → 박사논문_<topic-slug>_전체.docx
```
모든 장을 하나의 Word 파일로 통합하여 다운로드 및 편집 가능하게 변환

## 품질 검증

**각 장 작성 후 6가지 기준으로 검증:**

### 기존 5개 기준 (MAINTAINED)
1. **학술적 엄밀성** (20% weight, threshold: 75+)
   - 주장의 근거 충분성
   - 출처의 신뢰성
   - 논증의 타당성

2. **논리적 일관성** (20% weight, threshold: 75+)
   - 장 간 연결성
   - 논증 흐름
   - 용어 일관성

3. **인용 정확성** (15% weight, threshold: 80+)
   - 형식 준수 (APA/Chicago/etc.)
   - 참고문헌 일치
   - 페이지 번호 정확성

4. **문체 및 표현** (15% weight, threshold: 70+)
   - 학술적 어조
   - 문법/맞춤법
   - 가독성

5. **형식 준수** (10% weight, threshold: 80+)
   - 제목/부제 형식
   - 표/그림 형식
   - 번호 체계

### ⭐ 신규 필수 기준 (NEW - MANDATORY)
6. **Doctoral-Writing Compliance** (20% weight, threshold: 80+)
   - 6.1 Sentence-Level Clarity (25%)
     - Clear subject-verb relationships
     - Appropriate sentence length
     - Active voice for research actions
   - 6.2 Word-Level Precision (20%)
     - Technical terms defined
     - Consistent terminology
     - Precise word choice
   - 6.3 Paragraph-Level Coherence (20%)
     - Clear topic sentences
     - One idea per paragraph
     - Effective transitions
   - 6.4 Conciseness (15%)
     - No redundancies
     - Wordy phrases eliminated
     - Nominalizations minimized
   - 6.5 Academic Rigor (10%)
     - Evidence-based claims
     - Proper citations
     - Scholarly tone
   - 6.6 Language-Specific (10%)
     - Korean/English specific checks

**CRITICAL**: If Doctoral-Writing Compliance < 80, automatic FAIL → chapter must be revised.

### Integration with GRA
- **SRCS 평가** (MAINTAINED)
  - Citation Score (CS)
  - Grounding Score (GS)
  - Uncertainty Score (US)
  - Verifiability Score (VS)

**Doctoral-writing principles enhance SRCS scores:**
- Clarity → improves Grounding Score
- Conciseness → improves Citation Score
- Academic Rigor → improves Verifiability Score

## 출력

```
thesis-output/<session-dir>/
├── 00-session/
│   └── session.json (updated with word_document path)
├── 03-thesis/
│   ├── chapter1-introduction.md
│   ├── chapter2-literature-review.md
│   ├── chapter3-methodology.md
│   ├── chapter4-results.md
│   ├── chapter5-conclusion.md
│   └── 박사논문_<topic-slug>_전체.docx ⭐ (NEW)
└── _temp/
    ├── thesis-outline.md
    └── review-report-ch[N].md
```

## 완료 후

HITL-7 승인 후 Phase 4 (Publication)로 진행
