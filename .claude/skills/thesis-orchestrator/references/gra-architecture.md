# GRA (Grounded Research Architecture) 3계층 아키텍처

할루시네이션을 원천 차단하고 학술적 엄밀성을 보장하는 3계층 품질 보증 시스템.

## Layer 1: Agent Self-Verification

각 Sub-agent 내장 검증 시스템.

### GroundedClaim 출력 스키마

```yaml
claims:
  - id: "[PREFIX]-[NUMBER]"  # 예: LIT-001, TFA-003
    text: "[주장 내용]"
    claim_type: FACTUAL|EMPIRICAL|THEORETICAL|METHODOLOGICAL|INTERPRETIVE|SPECULATIVE
    sources:
      - type: PRIMARY|SECONDARY|TERTIARY
        reference: "[저자 (연도), 저널/출판사]"
        doi: "[DOI if available]"
        verified: true|false
    confidence: [0-100]
    effect_size: "[효과크기 if applicable]"
    uncertainty: "[불확실성 명시]"
```

### 클레임 유형별 기준

| 유형 | 설명 | 최소 신뢰도 | 필수 출처 |
|------|------|------------|----------|
| FACTUAL | 검증 가능한 객관적 사실 | 95 | PRIMARY/SECONDARY |
| EMPIRICAL | 실증연구 결과 | 85 | PRIMARY 필수 |
| THEORETICAL | 이론적 주장 | 75 | PRIMARY 필수 |
| METHODOLOGICAL | 방법론적 주장 | 80 | SECONDARY 이상 |
| INTERPRETIVE | 해석적 주장 | 70 | 근거 명시 |
| SPECULATIVE | 추측/제안 | 60 | 제한 없음 |

### Hallucination Firewall

생성 시점 차단 규칙:

| 레벨 | 동작 | 패턴 예시 |
|------|------|----------|
| BLOCK | 출력 차단 | "모든 연구가 일치", "100%", "예외 없이", "항상", "절대로" |
| REQUIRE_SOURCE | 출처 없으면 차단 | "p < .001", "효과크기 d = X" (단독) |
| SOFTEN | 경고 + 완화 권고 | "확실히", "명백히", "분명히", "틀림없이" |
| VERIFY | 검증 태그 추가 | "OO가 주장", "일반적으로", "대부분" |

### Mini-SRCS 자기 평가

각 에이전트가 출력 전 자체 평가:
- CS (Citation Score): 출처의 권위성과 적절성
- GS (Grounding Score): 주장의 근거 충분성
- 임계값 미달 시 재작업 또는 경고 태그

## Layer 2: Cross-Validation Gates

Wave 간 결과 교차 검증 시스템.

### Gate 구조

```
Wave N 완료
    │
    ▼
┌─────────────────────────────────────┐
│  Cross-Validation Gate N            │
├─────────────────────────────────────┤
│  1. 에이전트 간 모순 탐지           │
│  2. 중복 클레임 병합                │
│  3. 누락 영역 식별                  │
│  4. 품질 임계값 검사                │
└─────────────────────────────────────┘
    │
    ├─ PASS → Wave N+1 진행
    └─ FAIL → 재검토 또는 HITL 개입
```

### 검증 항목

1. **일관성 검사**: 동일 주제에 대한 상충 주장 탐지
2. **커버리지 검사**: 필수 분석 영역 누락 여부
3. **인용 검증**: 교차 인용 정확성 확인
4. **품질 검사**: SRCS 점수 임계값 확인

### Gate 통과 기준

| Gate | 위치 | 통과 조건 |
|------|------|----------|
| Gate 1 | Wave 1 → 2 | 기초 문헌 50편 이상, 검색 전략 문서화 |
| Gate 2 | Wave 2 → 3 | 이론적 프레임워크 도출, 주요 변수 식별 |
| Gate 3 | Wave 3 → 4 | 연구 갭 3개 이상 식별, 비판적 분석 완료 |
| Gate 4 | Wave 4 → 5 | 문헌종합 완료, 개념모델 도출 |

## Layer 3: Unified SRCS Evaluation

전체 연구 결과에 대한 최종 품질 평가.

### SRCS 4축 평가

| 축 | 설명 | 가중치 (EMPIRICAL) | 평가 기준 |
|----|------|-------------------|----------|
| CS | Citation Score | 0.35 | 출처 권위성, 최신성, 관련성 |
| GS | Grounding Score | 0.35 | 근거 충분성, 논리적 연결 |
| US | Uncertainty Score | 0.10 | 불확실성 적절 표현 |
| VS | Verifiability Score | 0.20 | 검증가능성, 재현가능성 |

### 점수 계산

```
Final Score = Σ(가중치 × 개별점수)
```

### 품질 등급

| 등급 | 점수 범위 | 조치 |
|------|----------|------|
| A | 90-100 | 즉시 진행 가능 |
| B | 80-89 | 경미한 보완 후 진행 |
| C | 75-79 | 보완 필요, 조건부 진행 |
| D | 60-74 | 상당한 수정 필요 |
| F | 60 미만 | 재작업 필수 |

**임계값: 75점 이상 필수**

### 최종 품질 인증

모든 클레임에 대해:
1. 전체 클레임 종합 평가
2. 교차 일관성 최종 검사
3. 학술적 기여도 평가
4. 품질 인증서 발급

## 에러 코드

| 코드 | 설명 | 처리 |
|------|------|------|
| GRA-001 | Hallucination 패턴 탐지 | 출력 차단 및 재생성 |
| GRA-002 | 출처 누락 | 출처 추가 요청 |
| GRA-003 | 신뢰도 미달 | 경고 태그 또는 재작업 |
| GRA-004 | 교차 검증 실패 | Gate 재통과 필요 |
| GRA-005 | SRCS 임계값 미달 | 품질 개선 후 재평가 |

---

## Simulation Modes & Context Efficiency (NEW)

시뮬레이션 모드와 컨텍스트 효율성 아키텍처.

### Quick vs Full Simulation Architecture

```
┌─────────────────────────────────────────────────────┐
│  Simulation Modes (동일한 GRA 품질 기준 적용)       │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Quick Mode (압축):                                 │
│  ┌───────────────────────────────────────┐         │
│  │ Input: 15+ files (100 pages)          │         │
│  │   ↓ [RLM Processing]                  │         │
│  │ RLM: Sliding window compression       │         │
│  │   ↓ [Progressive Compression]         │         │
│  │ Output: 20-30 pages                   │         │
│  │                                        │         │
│  │ GRA Check:                             │         │
│  │ ✅ pTCS ≥ 75 (필수)                   │         │
│  │ ✅ SRCS ≥ 75 (필수)                   │         │
│  │ ✅ Plagiarism < 15%                   │         │
│  │ ✅ All GRA layers applied             │         │
│  └───────────────────────────────────────┘         │
│                                                     │
│  Full Mode (상세):                                  │
│  ┌───────────────────────────────────────┐         │
│  │ Input: 15+ files (100 pages)          │         │
│  │   ↓ [Direct Processing]               │         │
│  │ Output: 145-155 pages                 │         │
│  │                                        │         │
│  │ GRA Check:                             │         │
│  │ ✅ pTCS ≥ 75 (필수)                   │         │
│  │ ✅ SRCS ≥ 75 (필수)                   │         │
│  │ ✅ Plagiarism < 15%                   │         │
│  │ ✅ All GRA layers applied             │         │
│  └───────────────────────────────────────┘         │
│                                                     │
│  핵심 철학:                                         │
│  Quick ≠ Lower Quality                             │
│  Quick = Professional Compression                  │
│  GRA 품질 기준은 동일 (75+ 필수)                    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### RLM (Recursive Language Model) Integration

대량 파일 효율적 처리 시스템.

```yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RLM Architecture:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Input: 15개 문헌검토 파일 (100 pages, ~50,000 tokens)

Step 1: Chunking
  ├─ Chunk 1: Files 1-5 (20 pages)
  ├─ Chunk 2: Files 6-10 (20 pages)
  └─ Chunk 3: Files 11-15 (20 pages)

Step 2: Progressive Compression
  ├─ Chunk 1 → Summary 1 (5 pages)
  ├─ Chunk 2 → Summary 2 (5 pages)
  └─ Chunk 3 → Summary 3 (5 pages)

Step 3: Final Synthesis
  └─ 3 Summaries → Integrated (15 pages, ~7,500 tokens)

Result:
  - Context savings: 85% (50k → 7.5k tokens)
  - Information loss: <10%
  - GRA quality: Maintained (all checks still applied)

Script: .claude/skills/thesis-orchestrator/scripts/rlm_processor.py
```

**RLM 품질 보증**:
- Compression 후에도 GRA Layer 1-3 모두 적용
- pTCS/SRCS 계산은 압축 후 결과물 기준
- 정보 손실 <10% 보장 (측정 가능)

### Agent/Subagent Architecture

컨텍스트 효율성을 위한 계층 구조.

```
┌─────────────────────────────────────────────────────┐
│  User Request (Natural Language)                    │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Main AI (System Prompt)                            │
│  - Subagent 목록 알고 있음                          │
│  - 적절한 Subagent 선택                             │
│  - Task tool로 독립 실행                            │
└─────────────────────────────────────────────────────┘
                      ↓
          ┌──────────┴──────────┐
          ↓                     ↓
┌───────────────────┐  ┌──────────────────────┐
│ Subagent 1        │  │ Subagent 2           │
│ (독립 컨텍스트)    │  │ (독립 컨텍스트)       │
│                   │  │                      │
│ - GRA Layer 1 ✅  │  │ - GRA Layer 1 ✅     │
│ - RLM 처리 ✅     │  │ - RLM 처리 ✅        │
│ - 품질 검증 ✅    │  │ - 품질 검증 ✅       │
└───────────────────┘  └──────────────────────┘
          ↓                     ↓
┌─────────────────────────────────────────────────────┐
│  Results Only (메인 컨텍스트로 반환)                │
│  - pTCS, SRCS 점수                                  │
│  - 생성된 파일 경로                                 │
│  - 품질 검증 결과                                   │
└─────────────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────────────┐
│  Hook Processing (자동)                             │
│  - 체크리스트 업데이트                              │
│  - 세션 상태 저장                                   │
│  - 다음 단계 제안                                   │
└─────────────────────────────────────────────────────┘
```

**컨텍스트 절약**:
```yaml
기존 방식 (비효율):
  - 모든 로직이 메인 컨텍스트 로드
  - ~8,000 tokens 소비

Subagent 방식 (효율):
  - 메인 컨텍스트: ~0 tokens (직접 호출)
  - Subagent: 독립 컨텍스트 (격리)
  - 결과만 반환

절약률: 96-100%
```

### Hook System Integration

반복 패턴 자동화 시스템.

```python
# .claude/hooks/post-tool-use/thesis-workflow-automation.py

AGENT_STEP_MAP = {
    # 기존 Phase 1-4 에이전트들...

    # Simulation agents (NEW)
    'simulation-controller': 150,
    'alphago-evaluator': 151,
    'autopilot-manager': 152,
    'thesis-writer-quick-rlm': None,
}

def hook(context):
    """
    Subagent 완료 후 자동 실행:
    1. 체크리스트 업데이트
    2. 세션 상태 저장
    3. GRA 품질 검증 결과 저장
    4. 다음 단계 제안 (사용자에게)
    """
    # GRA Layer 2 (Cross-Validation)와 통합
    # 시뮬레이션 완료 후에도 Gate 검증 수행
```

**Hook의 역할**:
- GRA Layer 2 (Cross-Validation) 자동 실행
- 품질 미달 시 자동 재시도 또는 사용자 알림
- 워크플로우 상태 추적 (session.json)

### AlphaGo-Style Evaluation with GRA

여러 옵션을 GRA 기준으로 평가.

```
┌─────────────────────────────────────────────────────┐
│  AlphaGo Evaluator                                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Input: 3 options (양적/질적/혼합)                  │
│                                                     │
│  Step 1: Quick 시뮬레이션 (병렬)                    │
│  ┌───────────────────────────────────────┐         │
│  │ Option A: Quick simulation            │         │
│  │   ↓ [GRA Layers 1-3 applied]          │         │
│  │ pTCS: 78, SRCS: 80                    │         │
│  └───────────────────────────────────────┘         │
│  ┌───────────────────────────────────────┐         │
│  │ Option B: Quick simulation            │         │
│  │   ↓ [GRA Layers 1-3 applied]          │         │
│  │ pTCS: 75, SRCS: 78                    │         │
│  └───────────────────────────────────────┘         │
│  ┌───────────────────────────────────────┐         │
│  │ Option C: Quick simulation            │         │
│  │   ↓ [GRA Layers 1-3 applied]          │         │
│  │ pTCS: 85, SRCS: 84 ⭐                 │         │
│  └───────────────────────────────────────┘         │
│                                                     │
│  Step 2: Win Rate Calculation                      │
│  ┌───────────────────────────────────────┐         │
│  │ pTCS 85 → base_rate 0.90              │         │
│  │ SRCS 84 → adjustment 0.98             │         │
│  │ Win Rate = 0.90 × 0.98 = 88%          │         │
│  └───────────────────────────────────────┘         │
│                                                     │
│  Output: Option C 추천 (88% 통과율)                 │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Win Rate = 논문 심사 통과 가능성**:
- pTCS/SRCS 기반 예측 알고리즘
- GRA 3계층 모두 통과한 옵션만 평가
- 높은 승률 = 높은 품질 + 낮은 위험

### Smart Mode with GRA

불확실성 기반 자동 모드 선택.

```yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Smart Mode Decision Algorithm:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: 불확실성 분석 (4가지 요인)
  - pTCS 변동성: 30%
  - 연구 참신성: 30%
  - 방법론 명확성: 20%
  - 데이터 가용성: 20%

Step 2: 모드 결정
  if uncertainty > 0.7:
    mode = "quick"
    reason = "High uncertainty → 빠른 탐색"

  elif uncertainty >= 0.3:
    mode = "both"
    reason = "Medium uncertainty → Quick + Full"

  else:
    mode = "full"
    reason = "Low uncertainty → 바로 완성"

Step 3: GRA 검증
  - 선택된 모드로 시뮬레이션 실행
  - GRA Layers 1-3 모두 적용
  - pTCS/SRCS ≥ 75 필수

Step 4: 품질 모니터링
  if pTCS < 75 or SRCS < 75:
    action = "pause_and_notify_user"
    alert = "Quality threshold not met"
    prompt_user = true

  else:
    action = "continue"
    next_phase = get_next_phase()

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Smart Mode와 GRA 통합**:
- 자동 모드 선택에도 GRA 품질 기준 엄격 적용
- 품질 미달 시 자동 중단 → 사용자 확인
- Gate 검증 자동 수행 (Hook 통합)

### Context Efficiency Metrics

컨텍스트 효율성 측정 및 최적화.

```yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
최종 컨텍스트 효율성:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phase 1 (비효율 - Python scripts):
  메인 컨텍스트: ~8,000 tokens
  GRA 적용: ✅ (하지만 비효율적)

Phase 2 (재설계 - Subagents):
  메인 컨텍스트: ~1,150 tokens (86% 절약)
  문제: Skill 중간 레이어 불필요
  GRA 적용: ✅

Phase 3 (최적화 - 최종):
  메인 컨텍스트: 0-300 tokens (96-100% 절약)
  RLM 처리: ✅ (85% 추가 절약)
  Hook 자동화: ✅
  GRA 적용: ✅ (품질 유지)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
측정 지표:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 메인 컨텍스트 사용량:
   - Before: ~8,000 tokens
   - After: 0-300 tokens
   - Savings: 96-100%

2. RLM 처리 효율:
   - Input: 50,000 tokens (15 files)
   - Output: 7,500 tokens (compressed)
   - Savings: 85%

3. 품질 유지:
   - pTCS: 75+ (Quick/Full 동일)
   - SRCS: 75+ (Quick/Full 동일)
   - GRA Layers: All applied ✅

4. 자동화율:
   - Hook 처리: 100% 자동
   - 품질 검증: 100% 자동
   - 재시도: 자동 (max 3회)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Architecture Philosophy

```yaml
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
핵심 원칙:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. 품질 타협 없음:
   ✅ Quick/Full 모두 GRA 3계층 적용
   ✅ pTCS/SRCS ≥ 75 필수
   ✅ 압축 != 품질 저하

2. 컨텍스트 효율성:
   ✅ Subagent 독립 실행
   ✅ RLM 대량 파일 처리
   ✅ 결과만 메인으로 반환

3. 자동화 최대화:
   ✅ Hook으로 반복 패턴 자동화
   ✅ Gate 검증 자동 수행
   ✅ 품질 미달 시 자동 재시도

4. 투명성:
   ✅ 모든 점수 계산 근거 명시
   ✅ 불확실성 분석 공개
   ✅ 사용자 최종 결정권

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 참조

- Subagents: `.claude/agents/thesis/simulation/`
- RLM Processor: `.claude/skills/thesis-orchestrator/scripts/rlm_processor.py`
- Hook: `.claude/hooks/post-tool-use/thesis-workflow-automation.py`
- Documentation: `.claude/skills/simulation-modes/`
