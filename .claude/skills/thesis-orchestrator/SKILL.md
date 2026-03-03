---
name: thesis-orchestrator
description: 박사논문 연구 워크플로우 총괄 오케스트레이터. 사용자가 (1) /thesis 명령어를 사용하거나, (2) "시작하자", "연구를 시작하자", "논문연구를 시작하자" 등 자연어로 연구 시작 의사를 표현하거나, (3) 논문 연구, 문헌검토, 연구설계, 논문작성 관련 작업을 요청하거나, (4) 학술적 연구 지원이 필요할 때 PROACTIVELY 사용. GRA(Grounded Research Architecture) 기반 품질 보증 시스템으로 학술적 엄밀성 보장.
---

# Thesis Orchestrator

박사급 논문 연구를 위한 통합 워크플로우 오케스트레이터.

## 핵심 원칙

```
┌─────────────────────────────────────────────────────────────┐
│  🎯 최우선 원칙: 학술적 품질 (Quality First)                │
├─────────────────────────────────────────────────────────────┤
│  1. 모든 Sub-agent는 opus 모델 사용                         │
│  2. 모든 실행은 순차(Sequential) 방식                       │
│  3. 모든 출력에 GRA Hook 검증 적용                          │
│  4. 비용/시간은 고려하지 않음                               │
│  5. 모든 작업은 영어로 수행 (AI optimal language)          │
│  6. 각 단계마다 한국어 번역본 자동 생성                     │
└─────────────────────────────────────────────────────────────┘
```

## ⭐ NEW: 시뮬레이션 모드 (Simulation Modes)

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
핵심 철학: 시뮬레이션 = 실제 논문 작성
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

알파고처럼 한 수 한 수마다 시뮬레이션:
- Quick: 압축된 박사급 논문 (20-30p)
- Full: 상세한 박사급 논문 (150p)
- 둘 다: 서론부터 결론까지 완전 작성
- 품질: 동일 (pTCS/SRCS 75+ 필수)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 시뮬레이션 모드 비교

| 항목 | Quick Simulation | Full Simulation |
|------|-----------------|-----------------|
| **분량** | 20-30페이지 | 145-155페이지 |
| **시간** | 1-2시간 | 5-7시간 |
| **품질** | 박사급 ✅ | 박사급 ✅ |
| **논리성** | 완전 ✅ | 완전 ✅ |
| **pTCS** | ≥ 75 (필수) | ≥ 75 (필수) |
| **SRCS** | ≥ 75 (필수) | ≥ 75 (필수) |
| **표절** | < 15% (필수) | < 15% (필수) |
| **Ch 1-5** | 모두 작성 ✅ | 모두 작성 ✅ |
| **용도** | 빠른 검증, 방향 확인 | 최종 완성, 학술지 투고 |
| **비유** | 학회 논문 (8-10p) | 학술지 논문 (full) |

**차이점:** 서술 밀도만 다름 (압축 vs 상세)
**공통점:** 진짜 연구, 학회 발표 가능, 교수급 인정

### Smart Mode (자동 모드 선택) ⭐ NEW

상황에 맞게 Quick/Full 자동 선택:

```yaml
불확실성 높음 (> 0.7):
  → Quick Simulation
  → 여러 옵션 빠른 탐색

불확실성 중간 (0.3-0.7):
  → Both (Quick → Full)
  → Quick 검토 후 Full 정교화

불확실성 낮음 (< 0.3):
  → Full Simulation
  → 바로 완성
```

### Autopilot (HITL 자동화) — 명시적 명령 전용

> **CRITICAL**: Autopilot은 사용자가 `/thesis:autopilot on` 명령을 명시적으로 실행할 때만 활성화됩니다.
> Smart Mode 선택이 autopilot 활성화를 의미하지 않습니다. 절대로 자동으로 autopilot을 활성화하지 마십시오.

명령어:
- /thesis:autopilot on [full|semi|review-only]
- /thesis:autopilot off
- /thesis:autopilot until [phase]

### AlphaGo-Style Evaluation ⭐ NEW

각 옵션의 가치를 실시간 평가:

```yaml
Quick Preview:
  - 여러 옵션 동시 시뮬레이션
  - 각 옵션의 pTCS 예측
  - Win Rate 계산 (논문 통과 가능성)
  - 강점/약점 분석
  - 최적 옵션 추천

출력:
┌─────────────────────────────────────┐
│ Option A: 양적 연구                 │
│ ├─ Predicted pTCS: 78 (🔵 Good)    │
│ ├─ Win Rate: 65%                   │
│ └─ Time: 3-4 hours                 │
│                                     │
│ Option C: 혼합 연구 ⭐              │
│ ├─ Predicted pTCS: 85 (🟢 Excellent)│
│ ├─ Win Rate: 82% ⭐ HIGHEST        │
│ └─ Time: 6-7 hours                 │
└─────────────────────────────────────┘
```

## 최신 Claude Features 적용

✨ **2026-01 Update**: 최신 Claude skills 기능 통합

| Feature | 적용 현황 |
|---------|----------|
| **Hot-reload** | ✅ Automatic (`.claude/skills/` 구조 사용) |
| **Context Forking** | ✅ 리소스 집약적 commands에 `context: fork` 적용 |
| **Agent Field** | ✅ 작업 유형별 최적 agent 지정 |
| **Simulation Modes** | ✅ Quick/Full 이중 모드 ⭐ NEW |
| **Smart Mode** | ✅ 지능형 자동 모드 선택 ⭐ NEW |

### Context Forking 적용 Commands
- 핵심 파이프라인: `run-literature-review`, `run-research-design`, `run-writing`
- 계산 집약적: `evaluate-srcs`, `check-plagiarism`, `validate-phase`, `validate-all`
- 검증: `run-writing-validated`, `start`, `run-publication`

**효과**: 메인 컨텍스트 보호, Error isolation, 리소스 최적화

## 워크플로우 개요

- **Input**: 연구주제 | 연구질문 | 기존문헌검토 | 학습모드 | 선행연구논문 | 연구프로포절 ⭐ | 자유입력 ⭐
- **Output**: 문헌검토 패키지 + 연구설계서 + 논문 초안 + 투고 전략
- **Quality Level**: 박사급 전문가 수준
- **Research Types**: 양적연구, 질적연구, 혼합연구, 철학적/이론적 연구

## 실행 순서

모든 에이전트는 **순차 실행**되며, 이전 에이전트 결과를 누적 참조합니다.

### Phase 0: 초기화
```
자연어 트리거: "시작하자", "연구하자" → /thesis:quick-start 자동 실행 ⭐ NEW
/thesis:init → session.json + todo-checklist.md 생성
/thesis:start [mode] [input] → 워크플로우 시작
/thesis:start paper-upload --paper-path [파일] → 논문 기반 연구 설계 (Mode E)
/thesis:start-proposal-upload --proposal-path [파일] → 프로포절 기반 연구 수행 (Mode F) ⭐
/thesis:start topic --entry-path custom → 자유 입력 기반 시작 (Mode G) ⭐
```

### Phase 1: 문헌검토 (15개 에이전트 순차 실행)
```
Wave 1 (English):
  literature-searcher → seminal-works-analyst → trend-analyst → methodology-scanner
  └─ Gate 1: Cross-Validation
  └─ @academic-translator → Korean translation ⭐

Wave 2 (English):
  theoretical-framework-analyst → empirical-evidence-analyst → gap-identifier → variable-relationship-analyst
  └─ Gate 2: Cross-Validation
  └─ @academic-translator → Korean translation ⭐

Wave 3 (English):
  critical-reviewer → methodology-critic → limitation-analyst → future-direction-analyst
  └─ Gate 3: Cross-Validation
  └─ @academic-translator → Korean translation ⭐

Wave 4 (English):
  synthesis-agent → conceptual-model-builder
  └─ Full SRCS Evaluation
  └─ @academic-translator → Korean translation ⭐

Wave 5 (English):
  plagiarism-checker → unified-srcs-evaluator → research-synthesizer
  └─ Final Quality Gate
  └─ @academic-translator → Korean translation ⭐
```

### Phase 2: 연구설계 (English + Korean translation)
연구유형에 따라 분기:
- 양적: hypothesis-developer → research-model-developer → sampling-designer → statistical-planner
- 질적: paradigm-consultant → participant-selector → qualitative-data-designer → qualitative-analysis-planner
- 혼합: 양적 + 질적 + mixed-methods-designer → integration-strategist
- 철학적: philosophical-method-designer → source-text-selector → argument-construction-designer → philosophical-analysis-planner
└─ @academic-translator → Korean translation ⭐

### Phase 3: 논문작성 (English + Korean translation) ⭐ **[DOCTORAL-WRITING MANDATORY]**

**⭐ NEW: All Phase 3 writing tasks MUST use the doctoral-writing skill.**

**Writing Quality Pipeline:**
```
Step 0: Load doctoral-writing skill (automatic)
  ↓
thesis-architect → thesis-writer (장별) → thesis-reviewer → plagiarism-checker
  ↓ doctoral-writing     ↓ doctoral-writing      ↓ doctoral-writing check
  └─ principles          └─ compliance           └─ verification (80+ required)
└─ @academic-translator → Korean translation ⭐
└─ export-docx (Word 통합 - English & Korean versions)
```

**Doctoral-Writing Integration:**

| Agent | Required Skill | Quality Standard |
|-------|----------------|------------------|
| `thesis-architect` | doctoral-writing | Clear, concise outline structure |
| `thesis-writer` | doctoral-writing | Clarity, conciseness, academic rigor in all chapters |
| `thesis-writer-rlm` | doctoral-writing | RLM workflow + doctoral-writing principles |
| `thesis-reviewer` | doctoral-writing | 6th criterion: Doctoral-Writing Compliance (20% weight, 80+ threshold) |

**Core Principles Applied:**
1. **Clarity (명료성)**: Subject-verb clarity, defined terminology
2. **Conciseness (간결성)**: 20-25 words/sentence (guideline), no redundancies
3. **Academic Rigor (학술적 엄격성)**: Evidence-based, precise terminology
4. **Logical Flow (논리적 흐름)**: Clear transitions, one idea/paragraph

**Quality Gates:**
- Each chapter must achieve Doctoral-Writing Compliance score of 80+
- If < 80, automatic FAIL → revision required
- No exceptions - this is a foundational writing standard

**References Available:**
- `doctoral-writing/references/clarity-checklist.md`
- `doctoral-writing/references/common-issues.md`
- `doctoral-writing/references/before-after-examples.md`
- `doctoral-writing/references/discipline-guides.md`

**Integration with GRA:**
- Doctoral-writing principles align with GRA quality requirements
- Clarity enhances Grounding Score (GS)
- Conciseness improves Citation Score (CS)
- Academic Rigor maintains Verifiability Score (VS)

### Phase 4: 투고전략
publication-strategist → manuscript-formatter

## Bilingual Output Architecture

영어 원본 + 한국어 번역 이중 언어 출력 구조:

| 파일 | 용도 |
|------|------|
| `session.json` | 세션 상태, HITL 스냅샷, 번역 메타데이터 |
| `todo-checklist.md` | 150단계 진행 상태 추적 |
| `research-synthesis.md` | 연구 결과 압축본 (English) |
| `research-synthesis-ko.md` | 연구 결과 압축본 (Korean) ⭐ |
| `*.md` | 모든 영어 출력물 |
| `*-ko.md` | 모든 한국어 번역본 ⭐ |

**Language Strategy**:
- Primary language: English (AI optimal performance)
- Secondary language: Korean (automatic translation after each phase)
- All agents work in English
- @academic-translator creates Korean versions

## GRA 품질 보증

See [references/gra-architecture.md](references/gra-architecture.md) for details.

### GroundedClaim 스키마 (필수)

모든 에이전트 출력은 다음 형식 준수:
```yaml
claims:
  - id: "[PREFIX]-001"
    text: "[주장]"
    claim_type: FACTUAL|EMPIRICAL|THEORETICAL|METHODOLOGICAL|INTERPRETIVE|SPECULATIVE
    sources:
      - type: PRIMARY|SECONDARY
        reference: "[인용]"
        doi: "[DOI]"
        verified: true|false
    confidence: [0-100]
    uncertainty: "[불확실성 명시]"
```

### Hallucination Firewall

| 레벨 | 동작 | 패턴 |
|------|------|------|
| BLOCK | 출력 차단 | "모든 연구가 일치", "100%", "예외 없이" |
| REQUIRE_SOURCE | 출처 필수 | 통계치 단독 사용 |
| SOFTEN | 완화 권고 | "확실히", "명백히" |

### SRCS 4축 평가

| 축 | 설명 | 임계값 |
|----|------|--------|
| CS (Citation Score) | 출처 품질 | - |
| GS (Grounding Score) | 근거 품질 | - |
| US (Uncertainty Score) | 불확실성 표현 | - |
| VS (Verifiability Score) | 검증가능성 | - |
| **종합** | 가중 평균 | **75점 이상** |

### pTCS (predicted Thesis Confidence Score)

**AlphaFold pIDDT 영감**: 자체 신뢰도 예측 시스템

| Level | 설명 | Threshold |
|-------|------|-----------|
| Claim | 개별 주장 신뢰도 (0-100) | 60+ |
| Agent | 에이전트별 평균 (0-100) | 70+ |
| Phase | 페이즈별 평균 (0-100) | 75+ |
| Workflow | 전체 가중 평균 (0-100) | 75+ |

**Color Coding** (🔴 0-60, 🟡 61-70, 🔵 71-85, 🟢 86-100)

### Dual Confidence System

**pTCS (60%) + SRCS (40%)** 통합 평가

- **pTCS**: 실시간 예측 (모든 agents)
- **SRCS**: 심층 평가 (Gate 시점)
- **pTCS 우선**: pTCS < threshold → 자동 FAIL

## HITL 체크포인트

| Checkpoint | Phase | 사용자 결정 |
|------------|-------|------------|
| HITL-0 | Phase 0 | 연구유형, 학문분야 선택 |
| HITL-1 | Phase 0 | 연구질문 확정 |
| HITL-2 | Phase 1 | 문헌검토 결과 승인 |
| HITL-3 | Phase 2 | 연구유형 최종 확정 |
| HITL-4 | Phase 2 | 연구설계 승인 |
| HITL-5 | Phase 3 | 논문 형식 선택 |
| HITL-6 | Phase 3 | 아웃라인 승인 |
| HITL-7 | Phase 3 | 초안 검토 |
| HITL-8 | Phase 4 | 최종 완료 |

## 스크립트

### Core Scripts
| Script | 용도 |
|--------|------|
| `scripts/init_session.py` | 세션 초기화, 디렉토리 생성 |
| `scripts/checklist_manager.py` | 150단계 체크리스트 관리 |
| `scripts/context_loader.py` | 컨텍스트 리셋 복구 |
| `scripts/sequential_executor.py` | 순차 실행 제어 |
| `scripts/gra_validator.py` | GRA 검증 |
| `scripts/srcs_evaluator.py` | SRCS 4축 평가 |
| `scripts/cross_validator.py` | Wave 간 교차 검증 |
| `scripts/export_to_docx.js` | 모든 장을 Word 문서로 통합 (Phase 3 완료 후) |
| `scripts/translate_to_korean.py` | 영어 문서를 한국어로 자동 번역 ⭐ |

### pTCS Scripts (신규)
| Script | 용도 |
|--------|------|
| `scripts/ptcs_calculator.py` | pTCS 계산 엔진 (4-level) |
| `scripts/ptcs_enforcer.py` | Retry-until-pass 강제 실행 |
| `scripts/dual_confidence_system.py` | pTCS + SRCS 통합 |
| `scripts/gate_controller.py` | Gate 자동 검증 (8 gates) |
| `scripts/confidence_monitor.py` | 실시간 대시보드 |

## 커맨드

### 자연어 트리거 (Proactive) ⭐ NEW
사용자가 다음과 같은 표현을 사용하면 **자동으로** `/thesis:quick-start` 실행:
- "시작하자", "시작할게", "연구를 시작하자", "논문을 쓰자", "논문연구를 시작하자"
- "Let's start", "Start research", "Begin thesis"
- "논문 연구를 도와줘", "연구 도와줘", "Help me with my thesis"

→ 5가지 모드 선택 UI 자동 표시 → 선택된 모드로 자동 분기

### 코어 커맨드
- `/thesis:quick-start` - 자연어 트리거로 빠른 시작 (자동 실행) ⭐
- `/thesis:init` - 워크플로우 초기화
- `/thesis:start [mode] [input]` - 워크플로우 시작
- `/thesis:status` - 진행 상태 확인
- `/thesis:resume` - 컨텍스트 리셋 후 재개

### 체크포인트 커맨드
- `/thesis:set-research-question` - 연구질문 확정 (HITL-1)
- `/thesis:review-literature` - 문헌검토 검토 (HITL-2)
- `/thesis:set-research-type` - 연구유형 확정 (HITL-3)
- `/thesis:approve-design` - 연구설계 승인 (HITL-4)
- `/thesis:set-format` - 논문 형식 설정 (HITL-5)
- `/thesis:approve-outline` - 아웃라인 승인 (HITL-6)
- `/thesis:review-draft` - 초안 검토 (HITL-7)
- `/thesis:finalize` - 최종 완료 (HITL-8)

### 유틸리티 커맨드
- `/thesis:check-plagiarism` - 표절 검사 (유사도 15% 미만)
- `/thesis:evaluate-srcs` - SRCS 4축 평가
- `/thesis:journal-search` - 학술지 검색
- `/thesis:format-manuscript` - 원고 포맷팅
- `/thesis:export-docx` - 모든 장을 하나의 Word 문서로 통합 (Phase 3 완료 후)
- `/thesis:translate [path]` - 영어 문서를 한국어로 번역 (자동 실행됨) ⭐

### pTCS 커맨드 (신규)
- `/thesis:monitor-confidence` - pTCS + SRCS 실시간 모니터링
- `/thesis:calculate-ptcs` - pTCS 점수 계산
- `/thesis:evaluate-dual-confidence` - pTCS + SRCS 통합 평가
- `/thesis:validate-gate [wave|phase] [N]` - Gate 자동 검증

## 에러 처리

| 실패 유형 | 처리 |
|----------|------|
| LOOP_EXHAUSTED | 부분 결과 반환 + 실패 지점 명시 |
| SOURCE_UNAVAILABLE | 대체 문헌 탐색 또는 스킵 |
| CONFLICT_UNRESOLVABLE | 양쪽 견해 병기 + 분석 |
| SRCS_BELOW_THRESHOLD | 재검토 플래그 |
| PLAGIARISM_DETECTED | 작업 중단 + 수정 요청 (15% 초과 시) |

## 사용 예시

```bash
# 연구 주제로 시작 (영어로 입력)
/thesis:start topic "Impact of AI on Organizational Innovation"

# 연구질문으로 시작 (영어로 입력)
/thesis:start question "How does digital transformation affect organizational learning in SMEs?"

# 기존 문헌검토 활용
/thesis:start review  # user-resource/ 폴더의 문헌검토 파일 참조

# 학습모드
/thesis:start learning

# 선행연구 논문 기반 연구 설계 (Mode E) ⭐ NEW
/thesis:start paper-upload --paper-path user-resource/uploaded-papers/smith-2023.pdf

# 수동 번역 (필요시)
/thesis:translate thesis-output/<session>/03-thesis/
```

## Bilingual Output Structure

워크플로우 실행 시 자동으로 생성되는 이중 언어 파일 구조:

```
thesis-output/<session-dir>/
├── 00-session/
│   └── session.json (includes translation metadata)
├── 01-literature-review/
│   ├── wave1-literature-search.md (English)
│   ├── wave1-literature-search-ko.md (Korean) ⭐
│   ├── wave2-theoretical-framework.md (English)
│   ├── wave2-theoretical-framework-ko.md (Korean) ⭐
│   ├── wave3-critical-review.md (English)
│   ├── wave3-critical-review-ko.md (Korean) ⭐
│   ├── wave4-synthesis.md (English)
│   ├── wave4-synthesis-ko.md (Korean) ⭐
│   └── wave5-final-report.md (English)
│   └── wave5-final-report-ko.md (Korean) ⭐
├── 02-research-design/
│   ├── research-design-report.md (English)
│   └── research-design-report-ko.md (Korean) ⭐
├── 03-thesis/
│   ├── chapter1-introduction.md (English)
│   ├── chapter1-introduction-ko.md (Korean) ⭐
│   ├── chapter2-literature-review.md (English)
│   ├── chapter2-literature-review-ko.md (Korean) ⭐
│   ├── chapter3-methodology.md (English)
│   ├── chapter3-methodology-ko.md (Korean) ⭐
│   ├── chapter4-results.md (English)
│   ├── chapter4-results-ko.md (Korean) ⭐
│   ├── chapter5-conclusion.md (English)
│   ├── chapter5-conclusion-ko.md (Korean) ⭐
│   ├── dissertation-full-en.docx (English Word)
│   └── dissertation-full-ko.docx (Korean Word) ⭐
└── 04-publication/
    ├── publication-strategy.md (English)
    └── publication-strategy-ko.md (Korean) ⭐
```

**Key Points**:
- All agents work in **English** (optimal AI performance)
- Automatic **Korean translation** after each wave/phase
- Both versions preserved in same directory
- Korean files have `-ko.md` suffix
- Citations, DOIs, author names stay in English (both versions)
- GRA schema preserved in both languages

## References

### Core Documentation
- [gra-architecture.md](references/gra-architecture.md) - GRA 3계층 아키텍처
- [grounded-claim-schema.md](references/grounded-claim-schema.md) - 클레임 스키마
- [srcs-evaluation.md](references/srcs-evaluation.md) - SRCS 평가 기준
- [hitl-checkpoints.md](references/hitl-checkpoints.md) - 체크포인트 정의
- [research-types.md](references/research-types.md) - 연구유형별 가이드

### pTCS Documentation (신규)
- [DUAL-CONFIDENCE-QUICK-GUIDE.md](DUAL-CONFIDENCE-QUICK-GUIDE.md) - 5분 퀵스타트
- [DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md](DUAL-CONFIDENCE-IMPLEMENTATION-REPORT.md) - 전체 구현 보고서
- [references/ptcs-specification.md](references/ptcs-specification.md) - pTCS 전체 사양서
- [SKILL-UPDATE-PROPOSAL.md](SKILL-UPDATE-PROPOSAL.md) - Claude skills 업데이트 제안서

## File Placement Convention

### Allowed Root Items (11)

Only the following items are permitted at the project root:

| Item | Type | Purpose |
|------|------|---------|
| `.claude/` | dir | System core (agents, commands, skills) |
| `.gitignore` | file | Git ignore rules |
| `_archive/` | dir | Cleaned-up files (gitignored) |
| `node_modules/` | dir | Node dependencies (gitignored) |
| `package.json` | file | Node package manifest |
| `package-lock.json` | file | Node lock file |
| `prompt/` | dir | Workflow prompt docs |
| `pyproject.toml` | file | Python project config |
| `tests/` | dir | Test suite |
| `thesis-output/` | dir | Research output |
| `user-resource/` | dir | User uploads |

### File Routing Rules

| File Type | Correct Location |
|-----------|-----------------|
| Research output | `thesis-output/<session>/` |
| Uploaded papers | `user-resource/uploaded-papers/` |
| Proposals | `user-resource/proposal/` |
| Dev reports | `_archive/obsolete/` |
| Reference docs | `_archive/references/` |
| Agent definitions | `.claude/agents/` |
| Commands | `.claude/commands/thesis/` |

### Anti-Patterns

```
BAD:  Write report to /IMPLEMENTATION-REPORT.md  (root pollution)
GOOD: Write report to /_archive/obsolete/IMPLEMENTATION-REPORT.md

BAD:  Save paper to /uploaded-paper.pdf  (root pollution)
GOOD: Save paper to /user-resource/uploaded-papers/uploaded-paper.pdf
```
