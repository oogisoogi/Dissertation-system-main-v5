# Decision Log

본 문서는 시스템 아키텍처의 주요 설계 결정을 기록합니다.

---

## ADR-001: SOT 4-Domain 아키텍처 도입

**일시**: 2026-01 (v4)
**상태**: 채택됨

**맥락**: 수치 파라미터, 오케스트레이션 로직, 런타임 상태, 프롬프트 템플릿이 여러 파일에 혼재되어 값 드리프트와 불일치가 발생함.

**결정**: 4개 도메인으로 분리
- SOT-A (workflow_constants.py): 모든 수치 파라미터
- SOT-B (SKILL.md): 오케스트레이션 로직 (수정 금지)
- SOT-C (session.json): 런타임 상태 (단일 기록자)
- SOT-D (prompt/WORKFLOW.md): 시스템 프롬프트 소스

**결과**: 값 변경 시 SOT-A 한 곳만 수정하면 10+ 소비 파일에 자동 전파.

---

## ADR-002: SOT-A 중앙집중화 (Quality Architecture v4)

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 임계값, 가중치, 패턴이 `ptcs_calculator.py`, `confidence_monitor.py`, `cross_validator.py`, `gra_validator.py`, `srcs_evaluator.py`, `dual_confidence_system.py`, `gate_controller.py`, `ptcs_enforcer.py` 등 10개 파일에 인라인으로 정의되어 있었음. 예: `ALERT_THRESHOLDS`가 `confidence_monitor.py`에, `CONTRADICTION_PATTERNS`가 `cross_validator.py`에, `HALLUCINATION_PATTERNS`가 `gra_validator.py`에 각각 독립 정의.

**결정**: 모든 수치 상수를 `workflow_constants.py`로 이동하고, 소비 파일은 import만 수행.

**이관된 상수**:
- 품질 임계값: SRCS, Plagiarism, DWC, pTCS (4레벨), Dual Confidence
- SRCS 가중치: 6개 연구유형별 (default, quantitative, qualitative, philosophical, slr, mixed)
- 재시도 제한: Agent(3), Wave(3), Phase(2)
- Cross-Validator: 최소 공유단어(2), 최소 단어길이(4), 심각도 가중치, 모순 패턴, 불용어
- GRA: 6개 주장유형별 신뢰도 임계값, 4개 환각 패턴 카테고리 (한영 이중)
- 경고 임계값, 에이전트 출력 파일 매핑, Wave 파일 (파생)

**영향**: `WAVE_FILES`가 `AGENT_OUTPUT_FILES`에서 파생됨 → 파일명 드리프트 원천 차단.

---

## ADR-003: No Fake Scores 원칙

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: `gate-automation.py`에서 import 실패 시 `consistency_score = 85`, `srcs_score = 85.7`로 하드코딩하여 gate가 항상 통과함. `validate-gate.md`에서도 `wave_ptcs = 82.0`, `wave_srcs = 78.0`을 placeholder로 사용. `plagiarism` 점수는 항상 `8.7`로 고정.

**결정**: 모든 가짜 폴백 점수를 제거. 계산 불가 시 `False` 반환하여 정직하게 실패.

**제거된 가짜 값**:
| 위치 | 이전 가짜 값 | 변경 후 |
| --- | --- | --- |
| gate-automation.py 교차검증 | 85 | 에러 메시지와 함께 False |
| gate-automation.py SRCS | 85.7 | 에러 메시지와 함께 False |
| gate-automation.py 표절 | 8.7 | 파일에서 regex 추출 |
| validate-gate.md wave pTCS | 82.0 | SRCS + consistency 계산 |
| validate-gate.md wave SRCS | 78.0 | srcs_evaluator 계산 |

**결과**: Gate가 실제 품질을 반영. 검증 모듈 장애 시 명확한 실패 신호 전달.

---

## ADR-004: 결정론적 Gate 검증 (validate_gate.py)

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 기존 `validate-gate.md` 커맨드는 `GateController`를 인라인 임포트하면서 placeholder 점수를 사용. Gate 판정에 LLM 해석이 개입할 여지가 있었음.

**결정**: `validate_gate.py`를 독립 스크립트로 분리. 모든 계산은 결정론적 Python. `validate-gate.md`는 subprocess로 실행 후 결과만 표시하는 프레젠테이션 레이어로 전환.

**파이프라인**:
1. session.json에서 research_type 로드
2. 출력 파일 수집 (_temp/ → 01-literature/)
3. SRCS 계산 (결정론적)
4. Cross-validation 일관성 계산 (결정론적)
5. pTCS proxy = srcs × 0.70 + consistency × 0.30
6. DualConfidenceCalculator로 판정

**결과**: Gate 판정의 재현성 보장. 동일 입력 → 동일 결과.

---

## ADR-005: Lightweight GRA PreToolUse Hook

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 기존 GRA 검증은 사후 검증(post-hoc)만 수행. 환각이 파일에 기록된 후에야 발견됨.

**결정**: `lightweight-gra-hook.py`를 PreToolUse hook으로 등록. Write/Edit 시 `thesis-output/**/*.md` 대상으로 BLOCK 패턴 검사.

**설계 제약**:
- stdlib만 사용 (hook 환경에서 project module import 불가)
- 패턴은 SOT-A에서 복제 (import 불가 → 인라인)
- Fail-open: 예외 발생 시 통과 (exit(0))
- BLOCK 패턴 매칭 → exit(2) = 쓰기 차단
- REQUIRE_SOURCE 패턴 → stderr 경고만 (차단 안 함)

**차단 패턴 예시**: "all research agrees", "definitively proven", "undeniable fact"

**결과**: 환각이 디스크에 기록되기 전에 실시간 차단. 첫 번째 능동적 품질 시행.

---

## ADR-006: 연구유형별 SRCS Grounding 패턴 확장

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: MEMORY.md에 기록된 문제 — "SRCS GS score penalizes qualitative research (regex looks for p-values/effect sizes)". 질적 연구가 양적 연구 중심의 근거 점수에 의해 체계적으로 불이익을 받음.

**결정**: `srcs_evaluator.py`에 3개 연구유형 전용 grounding 패턴 추가:
- **qualitative**: themes, participant reports, thick description, triangulation, saturation, lived experience
- **slr**: PRISMA, inclusion/exclusion criteria, database search, quality assessment, heterogeneity
- **mixed**: 양적+질적 증거 패턴 + 통합 증거 보너스

SRCS 가중치도 연구유형별 차별화 (SOT-A):
- qualitative: CS=0.40, GS=0.25 (default GS=0.30 대비 감소)
- slr: CS=0.40
- philosophical: CS=0.35, US=0.25

**결과**: 질적/SLR/혼합 연구가 각자의 증거 유형으로 공정하게 평가됨.

---

## ADR-007: Cross-Validator 오탐(False Positive) 감소

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: `similar_context()` 함수가 두 텍스트 간 "the" 한 단어만 공유해도 유사한 맥락으로 판단하여 서로 다른 주제의 텍스트를 비교하고 거짓 모순을 보고함.

**결정**:
- 최소 공유 단어 수: 1 → 2 (SOT-A `CROSS_VALIDATOR_MIN_SHARED_WORDS`)
- 최소 단어 길이: 없음 → 4자 이상 (SOT-A `CROSS_VALIDATOR_MIN_WORD_LENGTH`)
- 불용어 필터 추가 (SOT-A `CROSS_VALIDATOR_STOPWORDS`)
- 모순 패턴을 단일 단어에서 다단어 정규식으로 변경 (예: `positive effect` → `positive\s+(?:effect|impact|relationship|correlation|association)`)
- 대소문자 무시 매칭 (`re.IGNORECASE`)

**결과**: 서로 다른 주제의 텍스트 간 거짓 모순 보고 대폭 감소.

---

## ADR-008: Wave Gate 완화 정책

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: Wave gate에서 `MANUAL_REVIEW` 또는 `PASS_WITH_CAUTION` 판정 시 `RuntimeError`로 실행 중단. 이로 인해 경계선 결과에서 워크플로우가 불필요하게 중단됨.

**결정**:
- `MANUAL_REVIEW`: 경고 출력 후 진행 (이전: 중단)
- `PASS_WITH_CAUTION`: 경고 출력 후 진행 (이전: 중단)
- Gate 상태에 `"passed_with_caution"` 구분 추가 (이전: `"passed"`로 통합)

**결과**: 워크플로우 처리량 향상. 경계선 결과는 감사 로그에 구분 기록되어 사후 분석 가능.

---

## ADR-009: GRA 검증 강화 (고신뢰 주장 유형)

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 기존 GRA 검증에서 신뢰도 미달은 항상 경고만 발생 (hard fail 없음). 사실적 주장(FACTUAL)이 낮은 신뢰도로도 통과 가능.

**결정**: 주장 유형별 차별화된 hard-fail 정책:
- FACTUAL, EMPIRICAL, METHODOLOGICAL: 임계값 미달 시 hard fail
- THEORETICAL: 임계값 대비 10점 이상 미달 시 hard fail
- INTERPRETIVE, SPECULATIVE: 임계값 대비 15점 이상 미달 시 hard fail

**결과**: 높은 확신을 요구하는 주장 유형에 대한 품질 시행 강화.

---

## ADR-010: 챕터 일관성 검증기 도입

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 개별 챕터 품질 검증은 존재하나 챕터 간 교차 일관성 검증이 없음. 17챕터 논문에서 용어, 수치, 인용 형식 불일치가 발견됨.

**결정**: `chapter_consistency_validator.py` 도입. 4가지 결정론적 검사:
1. 용어 일관성: 동일 개념의 다른 표기 감지 (12 영어 + 5 한국어 변형 그룹)
2. 인용 일관성: 동일 참고문헌의 다른 인용 형식 감지
3. 수치 일관성: 동일 맥락 다른 수치 감지 (5% 차이 임계값)
4. 교차 참조 유효성: 존재하지 않는 챕터/절 참조 감지

**실행 시점**: 논문 작성(step 125+) → 리뷰어(step 132) 사이

**결과**: 독자가 즉시 발견할 수 있는 기계적 불일치를 자동 포착.

---

## ADR-011: 피드백 추출기 도입

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: thesis-reviewer의 리뷰 보고서를 수정 에이전트에게 전달할 때 LLM이 재해석하면서 정보 손실 발생.

**결정**: `feedback_extractor.py`가 리뷰 보고서(`review-report-chN.md`)를 결정론적 regex로 파싱하여 구조화된 `revision-brief-chN.json` 생성.

**추출 항목**: 점수 테이블, DWC 하위점수, 최종 판정 (PASS/REVISE/REWRITE), 이슈 목록, 심각도 분류, 우선순위 행동 목록

**결과**: 리뷰 → 수정 파이프라인에서 정보 손실 제거.

---

## ADR-012: 재시도 피드백 3채널 전달

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 에이전트 재시도 시 피드백이 `_retry_feedback` kwarg으로만 전달되어 소비 시스템이 제한적.

**결정**: 3채널 피드백 전달:
1. **kwarg**: 기존 `_retry_feedback` 매개변수
2. **Prompt 주입**: 호출자가 `prompt` kwarg을 전달하면 피드백 텍스트를 프롬프트 앞에 추가
3. **Sidecar 파일**: `_temp/retry-feedback-{agent_name}.json`에 구조화된 JSON 기록

**결과**: 어떤 소비 시스템이든 재시도 피드백에 접근 가능. 감사(audit) 목적으로도 활용.

---

## ADR-013: Context Recovery 60초 쿨다운

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: 컨텍스트 복구가 매 tool use마다 트리거되어 반복적 recovery injection으로 컨텍스트 윈도우 오염.

**결정**: `/tmp/dissertation-recovery-timestamp` 파일로 타임스탬프 기반 60초 쿨다운 구현.

**결과**: 분당 최대 1회 컨텍스트 복구. 컨텍스트 윈도우 오염 방지.

---

## ADR-014: SPECULATIVE 주장 유형 재분류

**일시**: 2026-03-01
**상태**: 채택됨

**맥락**: SPECULATIVE 주장이 실증적/통계적 grounding 브랜치에서 평가되어 p-value나 effect size가 없다는 이유로 불이익을 받음.

**결정**: SPECULATIVE을 비실증적/이론적 grounding 브랜치로 이동.

**결과**: 추론적 주장이 통계적 증거 부재로 인한 체계적 불이익에서 해방.

---

## ADR-015: user-resource/ 디렉토리 구조 도입

**일시**: 2026-02
**상태**: 채택됨

**맥락**: 사용자 업로드 파일(논문, 프로포절)의 표준 배치 위치 필요.

**결정**: `user-resource/` 하위에 용도별 디렉토리:
- `user-resource/uploaded-papers/`: 분석 대상 선행연구 논문
- `user-resource/proposal/`: 연구 프로포절 및 추출 스크립트

**결과**: SKILL.md 파일 배치 규칙과 일관된 구조.

---

## ADR-016: 시뮬레이션 모드 필수 선택 (Mandatory Simulation Mode Selection)

**일시**: 2026-03-02
**상태**: 채택됨

**맥락**: Phase 3 (논문 작성)에서 Quick(20-30p)/Full(145-155p)/Both/Smart 시뮬레이션 모드가 존재하나, 모드 선택이 필수가 아니었음. 사용자가 "시작하자"로 워크플로우를 시작해도 모드 선택 없이 기본값(Full)이 자동 적용되어 사용자 의도와 불일치 발생 가능.

**결정**:
1. `quick-start.md`에 Step 1.5 추가: 환영 메시지 직후 시뮬레이션 모드 선택을 **반드시** 표시
2. `init_session.py`에 `--simulation-mode` CLI 인수 추가: 선택 결과를 `session.json`의 `options.simulation_mode`에 저장
3. `workflow_constants.py` (SOT-A)에 `SIMULATION_MODES`, `DEFAULT_SIMULATION_MODE`, `VALID_SIMULATION_MODES` 추가
4. 모든 모드에서 동일한 품질 기준 적용 (pTCS ≥ 75, SRCS ≥ 75, DWC ≥ 80, Plagiarism < 15%)

**Producer-Consumer 데이터 흐름**:
- Producer: `quick-start.md` (UI) → `init_session.py` (저장)
- Storage: `session.json` → `options.simulation_mode`
- Consumer: `simulation_router.py` (결정론적 라우팅)

**결과**: 모든 세션에서 사용자가 시뮬레이션 모드를 명시적으로 선택. 기본값 추측 없음.

---

## ADR-017: 결정론적 시뮬레이션 라우팅 (Deterministic Simulation Routing)

**일시**: 2026-03-02
**상태**: 채택됨

**맥락**: `run-writing.md`의 Step 0.5에서 시뮬레이션 모드에 따른 실행 경로 분기가 마크다운 산문(prose)으로 작성되어 LLM이 해석하여 경로를 결정하는 구조였음. 이는 시스템의 핵심 설계 원칙 — "Tasks requiring exact, 100% reproducible results must be Python code" (ADR-004, `validate_gate.py` 선례) — 에 위배됨.

**문제점**:
- 마크다운 테이블의 LLM 해석은 비결정론적 (동일 입력에 다른 결과 가능)
- 경로 분기는 전체 Phase 3 실행에 영향을 미치는 critical branching decision
- 기존 시스템의 모든 critical decision (gate 검증, SRCS, pTCS)은 이미 결정론적 Python

**결정**: `simulation_router.py` 생성 — `validate_gate.py`와 동일 패턴의 결정론적 Python 스크립트
- 입력: `--dir` (프로젝트 작업 디렉토리)
- 처리: session.json 읽기(read-only) → 모드 검증 → Smart 불확실성 계산 → 실행 계획 구축
- 출력: 구조화된 JSON (execution_path, steps/phases, quality_thresholds, page_targets)
- `run-writing.md`는 JSON 결과를 따르는 프레젠테이션 레이어로 전환 (validate-gate.md 선례)

**Smart 모드 불확실성 계산** (결정론적):
- SRCS 평균 ≥ 90 → uncertainty 0.1 → Full
- SRCS 평균 ≥ 80 → uncertainty 0.3 → Full
- SRCS 평균 ≥ 70 → uncertainty 0.5 → Both
- SRCS 평균 < 70 → uncertainty 0.8 → Quick
- 데이터 없음 → uncertainty 0.7 → Both (보수적)

**결과**: 시뮬레이션 라우팅의 재현성 보장. 동일 session.json → 동일 실행 계획. LLM 할루시네이션 원천 차단.
