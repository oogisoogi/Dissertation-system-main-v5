# CLAUDE.md — Dissertation Research Workflow System v5

이 파일은 Claude Code가 본 프로젝트를 이해하기 위한 컨텍스트 문서입니다.

## 프로젝트 개요

AI 기반 박사논문 연구 워크플로우 시뮬레이션 시스템. 연구 주제 입력부터 150페이지 논문 완성까지 116개 전문 에이전트가 자동 수행합니다.

## SOT (Single Source of Truth) 4-Domain 아키텍처

본 시스템은 진실의 단일 소스(SOT) 원칙에 따라 4개 도메인으로 분리됩니다:

| Domain | 파일 | 역할 | 수정 권한 |
| --- | --- | --- | --- |
| **SOT-A** | `.claude/skills/thesis-orchestrator/scripts/workflow_constants.py` | 모든 수치 파라미터 | 개발자 |
| **SOT-B** | `.claude/skills/thesis-orchestrator/SKILL.md` | Claude Code 오케스트레이션 로직 | **수정 금지** |
| **SOT-C** | `thesis-output/<project>/00-session/session.json` | 런타임 상태 | 오케스트레이터만 |
| **SOT-D** | `prompt/doctoral-research-workflow.md` | 범용 시스템 프롬프트 소스 | 개발자 |

### SOT-A 핵심 상수 (workflow_constants.py)

- `TOTAL_STEPS = 150`: 전체 워크플로우 단계 수
- `PHASE_DEFINITIONS`: 11개 단계 정의 (phase0 ~ completion)
- `AGENT_STEP_MAP`: 25개 에이전트 → 단계 매핑
- `AGENT_OUTPUT_FILES`: 17개 에이전트 → 출력 파일명 매핑
- `WAVE_FILES`: `AGENT_OUTPUT_FILES`에서 파생 (직접 정의 금지)
- `SRCS_WEIGHTS_BY_TYPE`: 6개 연구유형별 SRCS 가중치
- `PTCS_THRESHOLDS`: claim=60, agent=70, phase=75, workflow=75
- `PTCS_PROXY_WEIGHTS`: srcs=0.70, consistency=0.30
- `HALLUCINATION_PATTERNS`: 4 카테고리 (BLOCK/REQUIRE_SOURCE/SOFTEN/VERIFY), 한영 이중

### SOT-C 상태 관리

- `session.json`의 `workflow.current_phase`가 진행 상태의 ground truth
- 3-File Architecture: `session.json` + `todo-checklist.md` + `final-insights.md`
- 단일 기록자 원칙: 오케스트레이터만 session.json 수정 가능

## 품질 보증 체계

### 7계층 품질 시스템

| 계층 | 메커니즘 | 파일 | 특성 |
| --- | --- | --- | --- |
| L1 | Lightweight GRA Hook | `hooks/pre-tool-use/lightweight-gra-hook.py` | 실시간, stdlib만, fail-open |
| L2 | GRA Hallucination Firewall | `scripts/gra_validator.py` | 에이전트 출력 검증 |
| L3 | SRCS 4축 평가 | `scripts/srcs_evaluator.py` | 연구유형별 가중치 |
| L4 | pTCS 4레벨 점수 | `scripts/ptcs_calculator.py` | claim/agent/phase/workflow |
| L5 | Cross-Validator | `scripts/cross_validator.py` | Wave 간 일관성 |
| L6 | Chapter Consistency | `scripts/chapter_consistency_validator.py` | 챕터 간 교차 검증 |
| L7 | DWC Compliance | doctoral-writing skill | 챕터별 학술 글쓰기 |

### 품질 임계값

```python
SRCS >= 75          # 추론 및 주장 품질
PLAGIARISM < 15%    # 표절 유사도
DWC >= 80           # 학술 글쓰기 준수
pTCS >= 75          # 논문 완성도 (workflow 레벨)
```

### Gate 검증 — 결정론적 Python

`validate_gate.py`가 모든 gate 판정의 단일 진입점:
1. `session.json`에서 `research_type` 로드
2. 출력 파일 수집 (`_temp/` → `01-literature/`)
3. SRCS 계산 (결정론적)
4. Cross-validation 일관성 계산 (결정론적)
5. pTCS proxy = `srcs * 0.70 + consistency * 0.30`
6. `DualConfidenceCalculator`로 PASS/FAIL/MANUAL_REVIEW 판정

### No Fake Scores 원칙

모든 점수는 실제 데이터에서 계산되어야 합니다. 폴백 가짜 점수(85, 85.7 등)는 금지. 계산 불가 시 정직하게 실패합니다.

## 파일 배치 규칙

프로젝트 루트에 허용되는 항목 (SKILL.md 규정):
- `.claude/`, `prompt/`, `tests/`, `user-resource/`, `thesis-output/`
- `README.md`, `USER_MANUAL.md`, `CLAUDE.md`, `copyright.md`
- `ARCHITECTURE-AND-PHILOSOPHY.md`, `decision-log.md`
- `package.json`, `pyproject.toml`, 설정 파일들

연구 출력물: `thesis-output/<slug>-<date>/` 하위에만 배치

## 워크플로우 핵심 경로

```
Phase 0 (Steps 1-18)   → 초기화, 모드 선택
Phase 1 (Steps 19-82)  → 문헌검토 (5 Waves + Gates)
  HITL-2 (Steps 83-88) → 문헌검토 결과 승인
Phase 2 (Steps 89-108) → 연구설계
Phase 3 (Steps 109-132)→ 논문 작성 + DWC 검증
Phase 4 (Steps 133-146)→ 출판 전략
Completion (147-150)   → 최종 완료
```

## 주요 커맨드

| 커맨드 | 설명 |
| --- | --- |
| `/thesis:start` | 워크플로우 시작 |
| `/thesis:status` | 진행 상태 확인 |
| `/thesis:resume` | 컨텍스트 리셋 후 재개 |
| `/thesis:validate-gate` | Gate 수동 검증 |
| `/thesis:calculate-ptcs` | pTCS 점수 계산 |
| `/thesis:monitor-confidence` | 실시간 신뢰도 모니터링 |
| `/thesis:export-docx` | Word 문서 내보내기 |
| `/thesis:translate` | 한국어 번역 |

## Hook 시스템

### PreToolUse Hooks
- **lightweight-gra-hook.py**: Write/Edit 시 환각 패턴 차단 (stdlib only, fail-open)
- **context-recovery.py**: 컨텍스트 리셋 감지 및 자동 복구 (60초 쿨다운)
- **rlm-context-monitor.py**: RLM 활성화 감시 (비활성 시 I/O 스킵)

### PostToolUse Hooks
- **gate-automation.py**: Wave/Phase 완료 시 자동 gate 검증
- **retry-enforcer.py**: 품질 미달 시 자동 재시도
- **thesis-workflow-automation.py**: 워크플로우 자동 진행
- **cross-wave-validator.py**: Wave 간 교차 검증
- **word-export-trigger.py**: 자동 Word 내보내기

## 개발 규칙

1. 수치 파라미터는 반드시 `workflow_constants.py` (SOT-A)에 정의
2. `WAVE_FILES`는 `AGENT_OUTPUT_FILES`에서 파생 — 직접 파일명 정의 금지
3. Hook의 CWD는 프로젝트 루트가 아닐 수 있음 → `cd $(git rev-parse --show-toplevel) &&` 접두사 필수
4. PreToolUse hook: exit(2)=차단, stderr=메시지; PostToolUse: exit(2)로 차단 불가
5. `_temp/` 디렉토리는 프로젝트 루트 기준 (하위 디렉토리 아님)
6. Lightweight hook은 stdlib만 사용 (workflow_constants import 불가)
7. session.json은 오케스트레이터만 수정 (단일 기록자 원칙)
