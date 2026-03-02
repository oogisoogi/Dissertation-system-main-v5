# Dissertation Research Workflow System
## Architecture, Philosophy & Technical Documentation

---

**Document Version**: 3.0.0
**System Version**: v5.0.0 (Production — Quality Architecture v4)
**Last Updated**: 2026-03-01
**Target Audience**: 개발자 (유지보수 및 확장)
**Purpose**: 시스템 아키텍처, 설계 철학, 기술 구현의 완전한 문서화

---

## 📑 Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Vision and Philosophy](#2-vision-and-philosophy)
3. [System Architecture](#3-system-architecture)
4. [Complete Workflow Specification](#4-complete-workflow-specification)
5. [Agent System Deep Dive](#5-agent-system-deep-dive)
6. [AI Technologies Integration](#6-ai-technologies-integration)
7. [Core Technologies](#7-core-technologies)
8. [Command System](#8-command-system)
9. [Quality Assurance Systems](#9-quality-assurance-systems)
10. [Version History & Updates](#10-version-history--updates)
11. [Usage Guide & Best Practices](#11-usage-guide--best-practices)
12. [Appendix](#12-appendix)

---

# 1. Executive Summary

## 1.1 시스템 개요

**Dissertation Research Workflow System**은 박사급 학술 연구를 위한 end-to-end AI 오케스트레이션 시스템입니다. 연구 주제 설정부터 논문 작성, 학술지 투고 전략까지 전체 연구 프로세스를 체계적으로 지원합니다.

### 핵심 지표

| 항목 | 값 | 설명 |
|------|-----|------|
| **전체 에이전트** | 116 | flat + hierarchical + meta/utility |
| **워크플로우 명령어** | 44 | 초기화, 실행, 검증, HITL, 시뮬레이션, 자기개선, pTCS/SRCS |
| **Python 스크립트** | 55 | 품질 검증, 게이트 관리, 피드백 추출 등 |
| **Pre/Post Hooks** | 9 | PreToolUse 3 + PostToolUse 6 (실시간 품질 감시) |
| **입력 모드** | 7 (A-G) | Topic, Question, Review, Learning, Paper, Proposal, Custom |
| **출력물** | 이중언어 | English + Korean |
| **품질 보증** | 7-Layer | L1 실시간 GRA Hook → L2 GRA Firewall → L3 SRCS → L4 pTCS → L5 Cross-Validator → L6 Chapter Consistency → L7 DWC |
| **SOT 아키텍처** | 4-Domain | SOT-A (상수) + SOT-B (오케스트레이션) + SOT-C (런타임) + SOT-D (프롬프트) |
| **Autopilot/Simulation** | v4+ | AlphaGo-style 평가 + Smart Autopilot |
| **Self-Improvement** | v4+ | Advisory-only 성능 분석 |
| **현재 버전** | v5.0.0 | Production — Quality Architecture v4 |

## 1.2 What: 무엇을 하는가?

### 주요 기능

1. **7가지 입력 모드**
   - Mode A: 연구 주제 입력 → 문헌검토 자동 수행
   - Mode B: 연구질문 입력 → 직접 문헌검토 시작
   - Mode C: 기존 문헌검토 업로드 → 갭 분석 후 설계
   - Mode D: 학습 모드 → 방법론 튜토리얼
   - Mode E: 선행연구 논문 업로드 → 6단계 분석 후 새 연구 제안
   - Mode F: 연구 프로포절 업로드 → 계획 추출 후 워크플로우 연결 (v4 신규)
   - Mode G: 자유형식 텍스트 입력 → 연구 요소 자동 추출 후 모드 라우팅 (v4 신규)

2. **4단계 연구 파이프라인**
   - **Phase 1**: 문헌검토 (15개 에이전트, 5 waves)
   - **Phase 2**: 연구설계 (양적/질적/혼합)
   - **Phase 3**: 논문작성 (doctoral-writing 강제)
   - **Phase 4**: 출판전략 (저널 선정, 투고 준비)

3. **이중언어 출력**
   - 영어 원본 (AI 최적 성능)
   - 한국어 자동 번역 (학술 전문 용어 보존)

4. **자연어 인터페이스** (v2.2.0)
   - "시작하자" → 자동으로 `/thesis:quick-start` 실행
   - 7-mode 선택 UI → 대화형 정보 수집

## 1.3 Why: 왜 필요한가?

### 문제 정의

**기존 AI (Artificial Intelligence, 인공지능) 연구 도구의 한계**:
- Hallucination (환각, AI가 사실이 아닌 내용을 생성하는 현상) 문제 (근거 없는 주장)
- 학술적 엄밀성 부족 (인용, 출처 누락)
- 단편적 지원 (문헌검토만, 작성만)
- 품질 보증 체계 부재
- 한국어 연구자 접근성 낮음

### 본 시스템의 해결책

1. **GRA (Grounded Research Architecture, 근거 기반 연구 아키텍처)**
   - 모든 주장에 GroundedClaim (근거 주장) schema (스키마, 데이터 구조) 강제
   - 4단계 Hallucination Firewall (환각 방화벽)
   - 자동 출처 검증
   - **v5**: 실시간 PreToolUse Hook으로 쓰기 시점에서 환각 차단

2. **7-Layer Quality Assurance (7중 품질 보증)** (v5 확장, 기존 3-Layer에서 업그레이드)
   - **L1**: Lightweight GRA Hook — Write/Edit 시 실시간 환각 패턴 차단 (v5 신규)
   - **L2**: GRA Hallucination Firewall — 에이전트 출력 사후 검증
   - **L3**: SRCS 4-axis 평가 — 연구유형별 가중치 차별화 (v5: qualitative/SLR/mixed 전용 패턴)
   - **L4**: pTCS 4-level 점수 — Claim→Agent→Phase→Workflow
   - **L5**: Cross-Validator — Wave 간 일관성 (v5: 오탐 감소)
   - **L6**: Chapter Consistency Validator — 챕터 간 교차 검증 (v5 신규)
   - **L7**: DWC (Doctoral Writing Compliance) — 챕터별 학술 글쓰기 준수

3. **End-to-End Support**
   - 연구 기획 → 문헌검토 → 설계 → 작성 → 투고
   - 8개 HITL (Human-In-The-Loop, 인간 참여 루프) 체크포인트
   - 150-step 진행 추적

4. **Bilingual Accessibility**
   - 영어로 작업 (AI 성능 극대화)
   - 자동 한국어 번역 (academic-translator)

## 1.4 How: 어떻게 작동하는가?

### 실행 모델

```
[사용자 입력]
    ↓
Natural Language Detection ("시작하자")
    ↓
Mode Selection (A/B/C/D/E/F/G)
    ↓
Phase 1: Literature Review (15 agents sequential)
    ├─ Wave 1-5 순차 실행
    ├─ 각 에이전트: GRA 출력 강제
    ├─ Gate 1-4: Cross-validation
    └─ SRCS 평가 (Wave 5)
    ↓
HITL-2: 사용자 승인
    ↓
Phase 2: Research Design (4-8 agents)
    ├─ 연구 유형별 분기 (양적/질적/혼합)
    └─ 설계 제안서 생성
    ↓
HITL-3/4: 사용자 승인
    ↓
Phase 3: Dissertation Writing (3 agents + skill)
    ├─ Doctoral-writing skill 강제 적용
    ├─ Chapter-by-chapter 작성
    ├─ Plagiarism check (<15%)
    └─ 자동 한국어 번역
    ↓
HITL-5/6/7: 챕터별 승인
    ↓
Phase 4: Publication Strategy (2 agents)
    ├─ 저널 선정
    └─ 투고 전략
    ↓
HITL-8: 최종 승인 → 완료
```

### 품질 보증 루프

```
Agent Output
    ↓
GRA Validation (GroundedClaim schema)
    ↓ PASS
pTCS Calculation (Claim-level score)
    ↓ >= 60
Agent-level pTCS (Average)
    ↓ >= 70
Wave/Phase Gate (Cross-validation)
    ↓ PASS
SRCS Evaluation (4-axis)
    ↓ >= 75
HITL Checkpoint
    ↓ Approved
Next Phase
```

**Fail 시**: 자동 재시도 (retry-until-pass)

## 1.5 Impact: 실제 효과

### 양적 지표

| 지표 | 수치 | 비교 |
|------|------|------|
| **입력 모드** | 7 (A-G) | v2.2.0 대비 +2 (F, G) |
| **평균 품질** | SRCS 85+ | 목표 75 초과 |
| **Plagiarism** | <10% | 목표 <15% 달성 |
| **Autopilot** | v4 신규 | 시뮬레이션 기반 자동 실행 |
| **Self-Improvement** | v4 신규 | Advisory 성능 분석 |

### 질적 효과

1. **학술적 무결성**
   - Hallucination 방지 (4-level firewall)
   - 모든 주장에 출처 검증
   - Doctoral-level 작성 품질 (80+ compliance)

2. **사용자 경험**
   - 자연어 시작 ("시작하자")
   - 대화형 UI (AskUserQuestion)
   - 150-step 진행 추적

3. **생산성**
   - 문헌검토 자동화 (15 agents)
   - 이중언어 출력 (번역 불필요)
   - 품질 보증 자동화 (GRA/pTCS/SRCS)

## 1.6 Status: 현재 상태

### v5.0.0 (2026-03-01) - Production — Quality Architecture v4

**주요 기능**:
- ✅ 7 Input Modes (A-G): Topic, Question, Review, Learning, Paper, Proposal, Custom
- ✅ 116 agents operational
- ✅ 44 workflow commands
- ✅ 55 Python scripts
- ✅ 9 Pre/Post Hooks (실시간 품질 감시 활성화)
- ✅ 7-Layer QA active (L1 실시간 GRA Hook ~ L7 DWC)
- ✅ SOT 4-Domain Architecture (SOT-A/B/C/D)
- ✅ Deterministic Gate Validation (validate_gate.py, No LLM)
- ✅ No Fake Scores (모든 가짜 폴백 점수 제거)
- ✅ Research-type-aware SRCS (qualitative/SLR/mixed 전용 grounding)
- ✅ RLM integration (200K+ context)
- ✅ Bilingual output (English + Korean)

**v4.0.0 이후 주요 변경 (Quality Architecture v4)**:
- ✅ SOT-A 중앙집중화: 10+ 파일의 상수를 `workflow_constants.py`로 통합
- ✅ No Fake Scores: 가짜 폴백 점수 (85, 85.7, 8.7) 완전 제거
- ✅ validate_gate.py: 결정론적 gate 검증 단일 진입점
- ✅ Lightweight GRA Hook: Write/Edit 시 실시간 환각 차단 (PreToolUse)
- ✅ Chapter Consistency Validator: 교차 챕터 일관성 검증
- ✅ Feedback Extractor: 리뷰 보고서 → 구조화된 수정 지시서
- ✅ 연구유형별 SRCS grounding: qualitative/SLR/mixed 전용 패턴
- ✅ Cross-Validator 오탐 감소: 최소 공유단어 2개, 불용어 필터
- ✅ Wave Gate 완화: MANUAL_REVIEW 시 경고 후 진행
- ✅ GRA 고신뢰 주장 hard-fail: FACTUAL/EMPIRICAL 미달 시 즉시 실패
- ✅ Context Recovery 60초 쿨다운
- ✅ 재시도 피드백 3채널 전달 (kwarg, prompt, sidecar file)

**완료된 프로젝트 (5건)**:
- ✅ agi-era-new-answers-to-12-life-questions (philosophical, 17 chapters)
- ✅ agi-future-imaginaries (mixed methods, 5 chapters)
- ✅ agi-future-imaginaries-qualitative (qualitative, 5 chapters, ~100K words)
- ✅ ai-of-vs (qualitative/critical interpretivism, 5 chapters)
- ✅ ai-literacy-jdr-slr (SLR, 5 chapters)

**테스트 상태**:
- ✅ Unit tests (GRA, pTCS, SRCS)
- ⚠️ Integration tests (partial)
- ⏳ E2E tests (planned)

---

# 2. Vision and Philosophy

## 2.1 Core Principles

본 시스템의 설계는 다음 6가지 핵심 원칙에 기반합니다.

### 2.1.1 Academic Integrity First (학술적 무결성 최우선)

**원칙**: 비용, 속도, 편의성보다 학술적 엄밀성을 우선시한다.

**구현**:
- 모든 에이전트는 **Opus 모델** 사용 (최고 품질)
- **순차 실행** (병렬 처리 금지 - 컨텍스트 일관성)
- **GroundedClaim schema** 강제 (모든 주장에 출처)
- **Hallucination Firewall** (절대적 표현 차단)

**트레이드오프**:
```
선택: 학술적 품질 > 실행 속도
결과: Phase 1 완료 60-90분 (병렬 시 15-20분 가능)
정당성: 박사 논문은 평생에 한 번. 품질이 속도보다 중요.
```

### 2.1.2 Sequential Execution (순차 실행)

**원칙**: 모든 에이전트는 엄격한 순서로 실행되며, 이전 에이전트의 출력을 참조한다.

**이유**:
1. **컨텍스트 일관성**: 각 에이전트는 이전 모든 분석을 읽고 이해
2. **누적 지식**: Wave 1 → Wave 5로 갈수록 깊이 증가
3. **검증 가능성**: 추론 체인 추적 가능

**예시: Literature Review Wave 2**
```python
theoretical-framework-analyst:
    input = [
        Wave 1 모든 출력물,
        연구 주제,
        연구질문
    ]
    output = 이론적 프레임워크 분석

empirical-evidence-analyst:
    input = [
        Wave 1 모든 출력물,
        theoretical-framework-analyst 출력,  # 이전 에이전트
        연구 주제,
        연구질문
    ]
    output = 실증 증거 종합
```

**비병렬화 결정**:
- ❌ `literature-searcher` || `seminal-works-analyst` (동시 실행)
- ✅ `literature-searcher` → `seminal-works-analyst` (순차 실행)

### 2.1.3 Quality over Cost/Speed (품질 우선)

**원칙**: 비용과 시간은 제약이 아니다. 품질이 유일한 기준이다.

**비용 구조**:
```
Phase 1 (Literature Review):
- 15 agents × Opus ($15/1M input, $75/1M output)
- 평균 입력: 50K tokens/agent
- 평균 출력: 10K tokens/agent
- 예상 비용: $15-25 per session

결정: 비용보다 품질. Haiku 사용 시 30% 저렴하지만 품질 저하.
```

**시간 구조**:
```
Sequential execution:
- Phase 1: 60-90분
- Phase 2: 20-30분
- Phase 3: 40-60분 (챕터별)
- Phase 4: 10-15분
Total: 130-195분 (2-3시간)

Parallel 가능 시간: 40-60분
선택: 품질 보장을 위해 sequential 유지
```

### 2.1.4 Hallucination Prevention (환각 방지)

**원칙**: AI의 자신감 과잉 표현을 체계적으로 차단한다.

**4-Level Firewall**:

| Level | Action | Pattern Examples |
|-------|--------|-----------------|
| **BLOCK** | 출력 차단 + 재생성 | "모든 연구가", "100%", "절대로", "완벽하게" |
| **REQUIRE_SOURCE** | 출처 강제 요구 | 통계값 (p<.001), 효과크기 (d=0.8) |
| **SOFTEN** | 경고 태그 추가 | "확실히", "명백히", "분명히" |
| **VERIFY** | 검증 태그 추가 | "일반적으로", "대부분의 연구" |

**예시: BLOCK-level detection**
```yaml
# 금지된 출력
claims:
  - text: "모든 연구가 일치하여 X는 절대적으로 Y를 야기한다."

# GRA-001 에러 발생 → 출력 차단
error: "BLOCK-level hallucination pattern detected"
action: "Regenerate with uncertainty acknowledgment"

# 수정된 출력
claims:
  - text: "다수의 연구(n=12)에서 X와 Y 간 정적 상관(r=0.6-0.8)이 보고되나, 인과관계는 불확실하다."
    claim_type: EMPIRICAL
    sources: [...]
    uncertainty: "상관관계는 확립되었으나 인과성은 추가 연구 필요"
```

### 2.1.5 Bilingual Accessibility (이중언어 접근성)

**원칙**: 영어로 작업하되, 한국어 접근성을 보장한다.

**전략**:
1. **English-First**
   - AI 성능 최적화 (영어 학습 데이터 우세)
   - 학술 표준 (국제 저널 영어)
   - 인용/DOI (Digital Object Identifier, 디지털 객체 식별자) 일관성

2. **Auto-Korean Translation**
   - `academic-translator` 에이전트
   - 전문 용어 보존 (citation, methodology)
   - 병렬 처리 (영어 작업과 독립)

**출력 구조**:
```
thesis-output/session-name/
├── 01-literature/
│   ├── research-synthesis.md          # English
│   ├── research-synthesis-ko.md       # Korean
│   ├── wave1-literature-search.md
│   └── wave1-literature-search-ko.md
├── 03-thesis/
│   ├── chapter-1-introduction.md
│   ├── chapter-1-introduction-ko.md
│   └── ...
└── dissertation-full-en.docx          # English
    dissertation-full-ko.docx          # Korean
```

**번역 품질 보장**:
- 학술 용어 사전 참조
- 인용 형식 보존 (APA (American Psychological Association, 미국심리학회), MLA (Modern Language Association, 현대언어학회) 등)
- DOI/URL (Uniform Resource Locator, 웹 주소) 원문 유지

### 2.1.6 Human-In-The-Loop (HITL, 인간 참여 루프) Strategy

**원칙**: AI는 분석/작성을 수행하고, 인간은 전략적 결정을 내린다.

**8개 HITL (인간 참여 루프) Checkpoints (체크포인트, 검증 지점)**:

| HITL | Phase | 결정 내용 | 이유 |
|------|-------|----------|------|
| HITL-0 | Init | Mode 선택 (A/B/C/D/E/F/G) | 연구 시작 방식 결정 |
| HITL-1 | Phase 0 | 연구 주제/질문 확정 | 연구 방향 설정 |
| HITL-2 | Phase 1 | 문헌검토 승인 | 연구 배경 충분성 판단 |
| HITL-3 | Phase 2 | 연구 유형 선택 | 양적/질적/혼합 결정 |
| HITL-4 | Phase 2 | 연구 설계 승인 | 방법론 적절성 판단 |
| HITL-5 | Phase 3 | 논문 형식/인용 스타일 | 목표 저널 고려 |
| HITL-6 | Phase 3 | 아웃라인 승인 | 논문 구조 확정 |
| HITL-7 | Phase 3 | 챕터별 승인 | 내용 품질 확인 |
| HITL-8 | Phase 4 | 최종 승인 | 투고 준비 완료 |

**설계 의도**:
- AI: 시간 소모적 작업 (문헌 검색, 분석, 초안 작성)
- Human: 가치 판단 (연구 방향, 방법론 선택, 최종 승인)

## 2.2 Design Philosophy

### 2.2.1 Grounded Research Architecture (GRA, 근거 기반 연구 아키텍처)

**철학**: "AI가 생성한 모든 학술적 주장은 검증 가능해야 한다."

**GroundedClaim (근거 주장) Schema (스키마)**:
```yaml
claims:
  - id: "LIT-001"
    text: "Transformers는 RNN (Recurrent Neural Network, 순환 신경망) 대비 장거리 의존성 학습에서 우수하다."
    claim_type: EMPIRICAL
    sources:
      - type: PRIMARY
        reference: "Vaswani et al. (2017)"
        doi: "10.48550/arXiv.1706.03762"
        verified: true
    confidence: 85
    uncertainty: "특정 도메인(NLP (Natural Language Processing, 자연어 처리))에서 검증됨. 다른 도메인은 추가 연구 필요"
```

**6가지 Claim Types**:

| Type | Confidence Threshold | Source Requirement |
|------|---------------------|-------------------|
| FACTUAL | 95 | PRIMARY or SECONDARY |
| EMPIRICAL | 85 | PRIMARY required |
| THEORETICAL | 75 | PRIMARY required |
| METHODOLOGICAL | 80 | SECONDARY+ |
| INTERPRETIVE | 70 | Any source |
| SPECULATIVE | 60 | No requirement |

**철학적 근거**:
- 학술 연구는 지식의 **축적**과 **검증**이다.
- AI는 지식을 **생성**할 수 없고, **종합**만 가능하다.
- 따라서 모든 AI 주장은 기존 연구에 **근거(grounded)**해야 한다.

### 2.2.2 Recursive Language Models (RLM, 재귀적 언어 모델)

**철학**: "컨텍스트 한계는 기술적 문제이지, 품질 저하의 이유가 아니다."

**문제**:
```
Claude 3.5 Sonnet: 200K context window
Phase 1 누적 출력: 150K+ tokens (Wave 1-5)
→ Wave 5에서 Wave 1-4 전체 참조 불가능
→ 정보 손실 70%+
```

**RLM 해결책** (Zhang et al. 2025):
```python
def rlm_summarize(long_text, target_length):
    """
    Recursive summarization with minimal information loss
    """
    if len(long_text) < target_length:
        return long_text

    # Split into chunks
    chunks = split_by_semantic_boundary(long_text, chunk_size=50K)

    # Summarize each chunk
    summaries = []
    for chunk in chunks:
        summary = llm_call(
            prompt=f"Summarize preserving key claims:\n{chunk}",
            model="claude-3-5-haiku"  # Cost optimization
        )
        summaries.append(summary)

    # Recursively summarize summaries
    combined = "\n\n".join(summaries)
    if len(combined) > target_length:
        return rlm_summarize(combined, target_length)
    else:
        return combined
```

**효과**:
- 정보 손실: 70% → <10%
- 비용: $0.20-3 per task (Haiku sub-calls)
- 컨텍스트 확장: 100K → 200K+ effective

**적용 에이전트**:
- `literature-searcher-rlm`: 100 papers → 10K papers screening
- `synthesis-agent-rlm`: Wave 1-4 전체 통합 (150K tokens)
- `thesis-writer-rlm`: 전체 문헌검토 참조 (95%+ citation accuracy)

### 2.2.3 External Memory Pattern

**철학**: "AI의 작업 기억(working memory)은 휘발성이지만, 외부 메모리는 영속적이다."

**3-File Architecture**:

```
1. session.json (Context File)
   - 연구 목표, 입력 정보
   - HITL 결정 스냅샷
   - 메타데이터

2. todo-checklist.md (Progress File)
   - 150-step 체크리스트
   - 실시간 진행 상태
   - 다음 액션 항목

3. research-synthesis.md (Insights File)
   - 3-4K word 압축
   - 핵심 발견사항
   - 가설/결론
```

**생명주기**:
```
Init → session.json 생성
    ↓
각 Phase 완료 → research-synthesis.md 업데이트
    ↓
컨텍스트 리셋 → session.json + research-synthesis.md 로드
    ↓
세션 재개 → todo-checklist.md에서 중단 지점 찾기
```

**컨텍스트 리셋 시**:
```python
def recover_from_context_reset():
    """
    컨텍스트가 리셋되어도 세션 재개 가능
    """
    # 1. Load session context
    session = load_json("session.json")
    research_goals = session["research_goals"]

    # 2. Load progress
    checklist = load_markdown("todo-checklist.md")
    last_completed = find_last_checked_item(checklist)

    # 3. Load insights
    insights = load_markdown("research-synthesis.md")

    # 4. Resume from last checkpoint
    resume_from(last_completed, context={
        "goals": research_goals,
        "insights": insights
    })
```

### 2.2.4 Dual Confidence System

**철학**: "신뢰도는 예측 가능해야 하고, 품질은 측정 가능해야 한다."

**pTCS (predicted Thesis Confidence Score, 예측 논문 신뢰도 점수)**:
- **영감**: AlphaFold의 pIDDT (predicted lDDT, 예측 구조 정확도 점수)
- **목적**: 출력 전 품질 예측
- **4-Level 구조**:
  1. Claim-level (주장 수준, 60+): 개별 주장 신뢰도
  2. Agent-level (에이전트 수준, 70+): 에이전트 평균
  3. Phase-level (단계 수준, 75+): 페이즈 평균
  4. Workflow-level (워크플로우 수준, 75+): 전체 가중 평균

**SRCS (Source-Reliability-Confidence-Scope, 출처-신뢰도-확신-범위 평가)**:
- **목적**: 출력 후 품질 측정
- **4-Axis (4축)**:
  - CS (Citation Score, 인용 점수, 35%): 출처 권위성
  - GS (Grounding Score, 근거 점수, 35%): 증거 충분성
  - US (Uncertainty Score, 불확실성 점수, 10%): 불확실성 표현
  - VS (Verifiability Score, 검증가능성 점수, 20%): 재현 가능성

**통합**:
```
Final Confidence = 0.6 × pTCS + 0.4 × SRCS

Threshold: 75+
Grade:
  A (90-100): Immediate proceed
  B (80-89): Minor revision
  C (75-79): Conditional proceed
  D (60-74): Significant revision
  F (<60): Complete rework
```

---

# 3. System Architecture

## 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Dissertation Workflow System                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Input Layer │  │ Process Layer│  │ Output Layer │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│    7 Modes            108 Agents       Bilingual Docs           │
│    A/B/C/D/E/F/G     Sequential        EN + KO                  │
│         │                 │                 │                   │
│         ▼                 ▼                 ▼                   │
│  ┌─────────────────────────────────────────────────┐           │
│  │            Quality Assurance Layer               │           │
│  │   GRA (Grounded) → pTCS (Predict) → SRCS (Score)│           │
│  └─────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────┐           │
│  │           Context Management Layer               │           │
│  │  session.json | todo-checklist.md | synthesis.md│           │
│  │  RLM (200K+)  | Context Fork     | Auto-recovery│           │
│  └─────────────────────────────────────────────────┘           │
│                                                                  │
│  ┌─────────────────────────────────────────────────┐           │
│  │              HITL Control Layer                  │           │
│  │  8 Checkpoints: Strategic Human Decisions        │           │
│  └─────────────────────────────────────────────────┘           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 3.2 Directory Structure (Complete)

### 3.2.0 Dual Agent Structure (v4 Architecture)

v4부터 에이전트는 **두 가지 네이밍 구조**를 병행합니다:

1. **Flat Naming** (42 files): `.claude/agents/` 루트에 단일 파일
   - 패턴: `thesis-phase{N}-wave{N}-{agent-name}.md`
   - 용도: Claude Code Task tool의 `subagent_type` 매칭
   - 예시: `thesis-phase1-wave1-literature-searcher-rlm.md`

2. **Hierarchical Structure** (61 files): `.claude/agents/thesis/` 하위 디렉토리
   - 패턴: `thesis/{phase}/{wave}/{agent-name}.md`
   - 용도: 사람이 읽기 쉬운 구조, 역할별 정리
   - 예시: `thesis/phase1-literature/wave1/literature-searcher-rlm.md`

두 구조는 동일한 에이전트를 참조하며, 실행 시 Task tool이 flat name을 사용합니다.

```
Dissertation-system-main-v4/
│
├── .claude/                              # Claude Skills Framework
│   │
│   ├── agents/                           # 108 Specialized Agents
│   │   │
│   │   ├── # ── Flat-Named Agents (42) ──────────────────────
│   │   ├── thesis-phase0-topic-explorer.md
│   │   ├── thesis-phase0-paper-research-designer.md
│   │   ├── thesis-phase0-academic-translator.md
│   │   ├── thesis-phase0-cross-validator-rlm.md
│   │   ├── thesis-phase0-custom-input-parser.md          # ⭐ Mode G (v4)
│   │   ├── thesis-phase0-proposal-analyzer.md             # ⭐ Mode F (v4)
│   │   ├── thesis-phase1-wave1-literature-searcher-rlm.md
│   │   ├── thesis-phase1-wave1-seminal-works-analyst.md
│   │   ├── ... (34 more flat-named agents)
│   │   ├── brand-logo-finder.md                           # Utility
│   │   ├── paper-research-designer.md                     # Mode E
│   │   ├── paper-research-orchestrator.md                 # Mode E orchestrator
│   │   │
│   │   ├── thesis/                        # ── Hierarchical Agents (61) ──
│   │   │   ├── academic-translator.md      # Common agent (thesis/ root)
│   │   │   ├── cross-validator-rlm.md     # Common agent (thesis/ root)
│   │   │   ├── self-improvement-analyst.md # ⭐ Self-Improvement (v4)
│   │   │   │
│   │   │   ├── phase0/                    # 초기화 (5 agents + 6 subagents)
│   │   │   │   ├── topic-explorer.md
│   │   │   │   ├── paper-research-designer.md     # Mode E (900+ lines)
│   │   │   │   ├── paper-research-orchestrator.md # Mode E orchestrator
│   │   │   │   ├── custom-input-parser.md         # ⭐ Mode G (v4)
│   │   │   │   ├── proposal-analyzer.md           # ⭐ Mode F (v4)
│   │   │   │   └── subagents/                     # Mode E 6-stage subagents
│   │   │   │       ├── paper-analyzer.md        # Stage 1
│   │   │   │       ├── gap-identifier.md        # Stage 2
│   │   │   │       ├── hypothesis-generator.md  # Stage 3
│   │   │   │       ├── design-proposer.md       # Stage 4
│   │   │   │       ├── feasibility-assessor.md  # Stage 5
│   │   │   │       └── proposal-integrator.md   # Stage 6
│   │   │   │
│   │   │   ├── phase1-literature/         # 문헌검토 (15 agents)
│   │   │   │   ├── wave1/                 # 검색 & 기초 (4)
│   │   │   │   │   ├── literature-searcher-rlm.md
│   │   │   │   │   ├── seminal-works-analyst.md
│   │   │   │   │   ├── trend-analyst.md
│   │   │   │   │   └── methodology-scanner.md
│   │   │   │   │
│   │   │   │   ├── wave2/                 # 심층 분석 (4)
│   │   │   │   │   ├── theoretical-framework-analyst.md
│   │   │   │   │   ├── empirical-evidence-analyst.md
│   │   │   │   │   ├── gap-identifier.md
│   │   │   │   │   └── variable-relationship-analyst-rlm.md
│   │   │   │   │
│   │   │   │   ├── wave3/                 # 비판적 평가 (4)
│   │   │   │   │   ├── critical-reviewer.md
│   │   │   │   │   ├── methodology-critic.md
│   │   │   │   │   ├── limitation-analyst.md
│   │   │   │   │   └── future-direction-analyst.md
│   │   │   │   │
│   │   │   │   ├── wave4/                 # 종합 (2)
│   │   │   │   │   ├── synthesis-agent-rlm.md
│   │   │   │   │   └── conceptual-model-builder-rlm.md
│   │   │   │   │
│   │   │   │   └── wave5/                 # 품질 보증 (3)
│   │   │   │       ├── plagiarism-checker-rlm.md
│   │   │   │       ├── unified-srcs-evaluator-rlm.md
│   │   │   │       └── research-synthesizer.md
│   │   │   │
│   │   │   ├── phase2-design/             # 연구설계 (10 agents)
│   │   │   │   ├── quantitative/          # 양적 (4)
│   │   │   │   │   ├── hypothesis-developer.md
│   │   │   │   │   ├── research-model-developer.md
│   │   │   │   │   ├── sampling-designer.md
│   │   │   │   │   └── statistical-planner.md
│   │   │   │   │
│   │   │   │   ├── qualitative/           # 질적 (4)
│   │   │   │   │   ├── paradigm-consultant.md
│   │   │   │   │   ├── participant-selector.md
│   │   │   │   │   ├── qualitative-data-designer.md
│   │   │   │   │   └── qualitative-analysis-planner.md
│   │   │   │   │
│   │   │   │   └── mixed-methods/         # 혼합 (2)
│   │   │   │       ├── mixed-methods-designer.md
│   │   │   │       └── integration-strategist.md
│   │   │   │
│   │   │   ├── phase3-writing/            # 논문작성 (5 agents + skill)
│   │   │   │   ├── thesis-architect.md
│   │   │   │   ├── thesis-writer.md            # 기본 작성
│   │   │   │   ├── thesis-writer-rlm.md        # RLM 확장
│   │   │   │   ├── thesis-writer-quick-rlm.md  # ⭐ Quick 모드 (v4)
│   │   │   │   └── thesis-reviewer.md
│   │   │   │
│   │   │   ├── phase4-publication/        # 출판 (2 agents)
│   │   │   │   ├── publication-strategist.md
│   │   │   │   └── manuscript-formatter.md
│   │   │   │
│   │   │   ├── simulation/               # ⭐ Autopilot/Simulation (v4 신규)
│   │   │   │   ├── alphago-evaluator.md    # AlphaGo-style 품질 평가
│   │   │   │   ├── autopilot-manager.md    # 자동 실행 관리
│   │   │   │   └── simulation-controller.md # 시뮬레이션 제어
│   │   │
│   │   ├── meta/                           # 메타 에이전트
│   │   │   └── rlm-integration-guide.md
│   │   │
│   │   └── templates/                      # 에이전트 템플릿
│   │       └── rlm-agent-template.md
│   │
│   ├── commands/thesis/                    # 41 Workflow Commands
│   │   │
│   │   ├── # ── 초기화 & 제어 (5) ──────────────
│   │   ├── init.md                         # 세션 초기화
│   │   ├── quick-start.md                  # NL (Natural Language, 자연어) 트리거 핸들러
│   │   ├── start.md                        # 워크플로우 시작
│   │   ├── start-paper-upload.md           # Mode E 시작
│   │   ├── start-proposal-upload.md        # ⭐ Mode F 시작 (v4)
│   │   ├── resume.md                       # 컨텍스트 복구
│   │   │
│   │   ├── # ── Phase 실행 (5) ──────────────
│   │   ├── run-literature-review.md        # Phase 1 (context: fork)
│   │   ├── run-research-design.md          # Phase 2 (context: fork)
│   │   ├── run-writing.md                  # Phase 3 (doctoral-writing 강제)
│   │   ├── run-writing-validated.md        # Phase 3 검증 실행
│   │   ├── run-publication.md              # Phase 4
│   │   │
│   │   ├── # ── HITL Checkpoints (8) ────────────
│   │   ├── approve-topic.md                # HITL-1
│   │   ├── review-literature.md            # HITL-2
│   │   ├── set-research-type.md            # HITL-3
│   │   ├── approve-design.md               # HITL-4
│   │   ├── approve-outline.md              # HITL-5
│   │   ├── review-chapter.md               # HITL-6/7
│   │   ├── review-proposal.md              # ⭐ 연구 제안 검토 (v4)
│   │   ├── finalize.md                     # HITL-8
│   │   │
│   │   ├── # ── 품질 보증 (8) ──────────────
│   │   ├── check-plagiarism.md             # 표절 검사
│   │   ├── evaluate-srcs.md                # SRCS 평가
│   │   ├── calculate-ptcs.md               # pTCS 계산
│   │   ├── evaluate-dual-confidence.md     # 이중 신뢰도
│   │   ├── monitor-confidence.md           # 실시간 모니터링
│   │   ├── validate-phase.md               # Phase 검증
│   │   ├── validate-gate.md                # Gate 검증
│   │   ├── validate-all.md                 # 전체 검증
│   │   │
│   │   ├── # ── Mode E/F 6-Stage (5) ────────────
│   │   ├── analyze-paper.md                # ⭐ Stage 1 논문 분석 (v4)
│   │   ├── identify-gaps.md                # ⭐ Stage 2 갭 식별 (v4)
│   │   ├── generate-hypotheses.md          # ⭐ Stage 3 가설 생성 (v4)
│   │   ├── propose-design.md               # ⭐ Stage 4 설계 제안 (v4)
│   │   ├── assess-feasibility.md           # ⭐ Stage 5 타당성 평가 (v4)
│   │   ├── integrate-proposal.md           # ⭐ Stage 6 제안서 통합 (v4)
│   │   ├── review-extracted-plan.md        # ⭐ Mode F 추출 계획 검토 (v4)
│   │   │
│   │   ├── # ── Autopilot & Self-Improvement (2) ──
│   │   ├── autopilot.md                    # ⭐ Autopilot 제어 (v4)
│   │   ├── improvement-log.md              # ⭐ 개선 이력 조회 (v4)
│   │   ├── review-improvements.md          # ⭐ 성능 분석/개선 검토 (v4)
│   │   │
│   │   ├── # ── 유틸리티 (4) ──────────────
│   │   ├── status.md                       # 진행 상태
│   │   ├── progress.md                     # 상세 진행
│   │   ├── translate.md                    # 한국어 번역
│   │   └── export-docx.md                  # Word 내보내기
│   │
│   ├── skills/                             # Orchestration Skills (10)
│   │   ├── thesis-orchestrator/            # ⭐ Main Skill
│   │   │   ├── SKILL.md                    # Skill definition (proactive trigger)
│   │   │   ├── scripts/                    # 43 scripts (21,437 lines)
│   │   │   │   ├── # ── Core ──────────────
│   │   │   │   ├── init_session.py         # 세션 초기화
│   │   │   │   ├── checklist_manager.py    # 150-step tracking
│   │   │   │   ├── context_loader.py       # Reset recovery
│   │   │   │   ├── path_utils.py           # 경로 유틸리티
│   │   │   │   ├── orchestrator.sh         # Shell orchestrator
│   │   │   │   │
│   │   │   │   ├── # ── QA (Quality Assurance, 품질 보증) ──────────────
│   │   │   │   ├── gra_validator.py        # GRA validation
│   │   │   │   ├── srcs_evaluator.py       # SRCS scoring
│   │   │   │   ├── ptcs_calculator.py      # pTCS computation
│   │   │   │   ├── dual_confidence_system.py  # pTCS + SRCS
│   │   │   │   ├── cross_validator.py      # Wave validation
│   │   │   │   ├── gate_controller.py      # 8 gates
│   │   │   │   │
│   │   │   │   ├── # ── RLM ──────────────
│   │   │   │   ├── rlm_processor.py        # RLM integration
│   │   │   │   ├── rlm_streaming_summarizer.py  # ⭐ (v4)
│   │   │   │   ├── sliding_window_context.py    # ⭐ (v4)
│   │   │   │   ├── progressive_compressor.py    # ⭐ (v4)
│   │   │   │   │
│   │   │   │   ├── # ── Validation ────────
│   │   │   │   ├── validated_executor.py        # ⭐ (v4)
│   │   │   │   ├── validation_config.py         # ⭐ (v4)
│   │   │   │   ├── validation_fallback.py       # ⭐ (v4)
│   │   │   │   ├── workflow_validator.py         # ⭐ (v4)
│   │   │   │   ├── enable-validation.sh         # ⭐ (v4)
│   │   │   │   ├── disable-validation.sh        # ⭐ (v4)
│   │   │   │   │
│   │   │   │   ├── # ── Self-Improvement ──
│   │   │   │   ├── self_improvement_engine.py   # ⭐ (v4)
│   │   │   │   ├── performance_collector.py     # ⭐ (v4)
│   │   │   │   ├── improvement_analyzer.py      # ⭐ (v4)
│   │   │   │   ├── change_classifier.py         # ⭐ (v4)
│   │   │   │   ├── improvement_logger.py        # ⭐ (v4)
│   │   │   │   │
│   │   │   │   ├── # ── Other ──────────────
│   │   │   │   ├── translate_to_korean.py       # Auto translation
│   │   │   │   ├── parallel_translator.py       # ⭐ (v4)
│   │   │   │   ├── manage_claims.py             # ⭐ (v4)
│   │   │   │   ├── manage_references.py         # ⭐ (v4)
│   │   │   │   ├── memory_manager.py            # ⭐ (v4)
│   │   │   │   ├── init_memory_architecture.py  # ⭐ (v4)
│   │   │   │   ├── run_paper_analyzer.py        # ⭐ (v4)
│   │   │   │   ├── run_research_design.py       # ⭐ (v4)
│   │   │   │   ├── run_writing_validated.py     # ⭐ (v4)
│   │   │   │   └── ... (기존 스크립트 포함)
│   │   │   │
│   │   │   └── references/                 # Documentation
│   │   │       ├── gra-architecture.md      # (v4: gra-specification.md에서 개명)
│   │   │       ├── ptcs-specification.md
│   │   │       ├── agent-wrapper-guide.md   # ⭐ (v4)
│   │   │       ├── citation-style-guide.md  # ⭐ (v4)
│   │   │       ├── endnotes-workflow.md     # ⭐ (v4)
│   │   │       ├── fallback-system-guide.md # ⭐ (v4)
│   │   │       └── validation-configuration.md  # ⭐ (v4)
│   │   │
│   │   ├── hypothesis-development/
│   │   ├── paper-analysis/
│   │   ├── research-design-templates/
│   │   ├── validation-checks/
│   │   ├── hook-creator/
│   │   ├── skill-creator/
│   │   ├── slash-command-creator/
│   │   ├── subagent-creator/
│   │   └── youtube-collector/
│   │
│   ├── hooks/                              # Automation Hooks
│   │   │                                   # ⚠️ v4: settings.json에서 비활성화 상태
│   │   ├── pre-tool-use/
│   │   │   ├── rlm-context-monitor.py
│   │   │   └── context-recovery.py
│   │   ├── post-tool-use/
│   │   │   ├── thesis-workflow-automation.py
│   │   │   ├── gate-automation.py
│   │   │   ├── cross-wave-validator.py
│   │   │   ├── retry-enforcer.py
│   │   │   └── word-export-trigger.py
│   │   └── thesis/                         # ⭐ Thesis-specific hooks (v4)
│   │       ├── hitl-checkpoint.sh           # HITL 자동 검증
│   │       ├── post-stage.sh               # Stage 완료 후 처리
│   │       └── pre-stage.sh                # Stage 시작 전 처리
│   │
│   ├── libs/
│   │   └── rlm_core.py                     # RLM implementation
│   │
│   ├── settings.json                       # Claude settings (hooks: {} 비활성화)
│   │
│   └── thesis-output/                      # ⭐ v4 세션 출력 경로
│       └── ai-transformation-ax-framework-for-small-churches-2026-01-21/
│
├── prompt/                                  # Workflow Specifications
│   ├── doctoral-research-workflow.md        # Main workflow (150 steps)
│   ├── mode-e-paper-upload-workflow.md      # Mode E workflow
│   ├── mode-f-proposal-upload-workflow.md   # ⭐ Mode F workflow (v4)
│   ├── design-pipeline.md                   # Research design
│   ├── crystalize-prompt.md                 # Prompt compression
│   └── distill-partner.md                   # Prompt refinement
│
├── tests/                                   # Testing Suite
│   ├── unit/
│   │   ├── test_init_session.py
│   │   ├── test_gra_validator.py
│   │   ├── test_srcs_evaluator.py
│   │   ├── test_ptcs_calculator.py
│   │   └── test_cross_validator.py
│   ├── integration/
│   ├── regression/
│   ├── fixtures/
│   └── conftest.py
│
├── docs/                                    # User Documentation
│   └── cc/
│       ├── hooks.md
│       ├── slash-commands.md
│       └── sub-agent.md
│
├── thesis-output/                           # Root 출력 (빈 디렉토리)
│
├── user-resource/                           # User Uploads
│   └── uploaded-papers/                     # Mode E papers
│
├── _archive/                                # ⭐ Archive (v4)
│   ├── references/
│   │   └── WORKFLOW-ARCHITECTURE-AND-PHILOSOPHY.md  # ⭐ This file
│   └── obsolete/                            # 이전 버전 문서
│
└── Root Files
    ├── README.md
    ├── USER_MANUAL.md                       # 84KB 사용자 매뉴얼
    ├── copyright.md
    ├── pyproject.toml                       # version "1.0.0"
    └── package.json
```

## 3.3 Data Flow Architecture

### Input Layer (7 Modes)

```
User Input
    ↓
┌───────────────────────────────────────────────────┐
│  Mode Detection & Routing                         │
├───────────────────────────────────────────────────┤
│  Mode A: Research Topic                           │
│    → topic-explorer                               │
│    → Research questions derivation                │
│    → Phase 1                                      │
│                                                    │
│  Mode B: Research Question(s)                     │
│    → Direct Phase 1 entry                         │
│                                                    │
│  Mode C: Existing Literature Review               │
│    → gap-identifier                               │
│    → Phase 2 (skip Phase 1)                       │
│                                                    │
│  Mode D: Learning Mode                            │
│    → Methodology tutorials                        │
│    → Example walkthroughs                         │
│                                                    │
│  Mode E: Paper Upload                             │
│    → paper-research-designer                      │
│    → 6-stage analysis                             │
│    → Novel hypotheses (6-15)                      │
│    → Phase 1 with context                         │
│                                                    │
│  Mode F: Proposal Upload (v4)                     │
│    → proposal-analyzer                            │
│    → 연구 계획 추출 및 구조화                       │
│    → 완성도 평가 후 워크플로우 연결                  │
│    → 적절한 Phase로 라우팅                         │
│                                                    │
│  Mode G: Custom Input (v4)                        │
│    → custom-input-parser                          │
│    → 자유형식 텍스트에서 연구 요소 추출              │
│    → 적절한 Mode (A-F)로 자동 라우팅                │
└───────────────────────────────────────────────────┘
```

### Processing Layer (108 Agents Sequential)

```
Phase 1: Literature Review
    ↓
Wave 1: Search & Foundation
├─ literature-searcher-rlm
│   Input: Research question
│   Output: 100-10K papers screening
│   RLM: Batch processing
│   GRA: All papers verified
│   ↓
├─ seminal-works-analyst
│   Input: Wave 1 + screened papers
│   Output: Key publications (10-20)
│   GRA: Citation network
│   ↓
├─ trend-analyst
│   Input: Wave 1 + seminal works
│   Output: Research trajectory
│   GRA: Temporal analysis
│   ↓
└─ methodology-scanner
    Input: Wave 1 + trends
    Output: Common methods
    GRA: Methodological patterns
    ↓
Gate 1: Cross-Validation
    ├─ Wave 1 consistency check
    ├─ Citation overlap validation
    └─ PASS → Wave 2
    ↓
Wave 2: Deep Analysis
[4 agents sequential...]
    ↓
Gate 2: Cross-Validation
    ↓
Wave 3: Critical Evaluation
[4 agents sequential...]
    ↓
Gate 3: Cross-Validation
    ↓
Wave 4: Synthesis
[2 agents sequential with RLM]
    ↓
SRCS Full Evaluation
    ↓
Wave 5: Quality Assurance
[3 agents sequential with RLM]
    ↓
Gate 4: Final Quality Gate
    ↓
HITL-2: Literature Review Approval
    ↓
Phase 2: Research Design
[4-8 agents based on type]
    ↓
HITL-3/4: Design Approval
    ↓
Phase 3: Dissertation Writing
[3 agents + doctoral-writing skill]
    ↓
HITL-5/6/7: Chapter Approvals
    ↓
Phase 4: Publication Strategy
[2 agents]
    ↓
HITL-8: Final Approval
```

### Quality Layer (Triple Validation)

```
Agent Output
    ↓
┌─────────────────────────────────────┐
│  Layer 1: GRA Validation             │
│  ├─ GroundedClaim schema check      │
│  ├─ Hallucination firewall           │
│  ├─ Source verification              │
│  └─ Confidence threshold             │
│      ↓ PASS                          │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 2: pTCS Prediction            │
│  ├─ Claim-level score (60+)         │
│  ├─ Agent-level average (70+)       │
│  ├─ Phase-level average (75+)       │
│  └─ Workflow-level weighted (75+)   │
│      ↓ >= Threshold                 │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Layer 3: SRCS Measurement           │
│  ├─ CS: Citation Score (35%)        │
│  ├─ GS: Grounding Score (35%)       │
│  ├─ US: Uncertainty Score (10%)     │
│  └─ VS: Verifiability Score (20%)   │
│      ↓ >= 75                        │
└─────────────────────────────────────┘
    ↓
Dual Confidence = 0.6*pTCS + 0.4*SRCS
    ↓
Grade Assignment (A/B/C/D/F)
    ↓
├─ A/B: Proceed
├─ C: Conditional proceed
└─ D/F: Retry (auto-loop)
```

### Output Layer (Bilingual Deliverables)

```
Approved Content
    ↓
┌─────────────────────────────────────┐
│  English Generation (Primary)        │
│  ├─ Academic writing standards      │
│  ├─ Citation preservation            │
│  └─ Markdown format                  │
└─────────────────────────────────────┘
    ↓
┌─────────────────────────────────────┐
│  Korean Translation (Parallel)       │
│  ├─ academic-translator agent       │
│  ├─ Terminology preservation         │
│  └─ DOI/URL retention                │
└─────────────────────────────────────┘
    ↓
File Structure:
├─ research-synthesis.md
├─ research-synthesis-ko.md
├─ chapter-1-introduction.md
├─ chapter-1-introduction-ko.md
└─ ...
    ↓
Word Export (Optional):
├─ dissertation-full-en.docx
└─ dissertation-full-ko.docx
```

## 3.4 Context Management

### 3.4.1 External Memory (3-File Strategy)

**설계 목적**: AI 작업 기억의 휘발성을 극복

```yaml
File 1: session.json (Context File)
  Purpose: 세션 메타데이터 및 연구 컨텍스트
  Size: 5-10 KB
  Update: 각 HITL 체크포인트
  Content:
    - session_id
    - created_at
    - research_goals
    - input_mode (A/B/C/D/E)
    - research_type (quantitative/qualitative/mixed)
    - hitl_snapshots: []
    - paper_metadata: {} (Mode E only)
    - current_phase
    - current_step

File 2: todo-checklist.md (Progress File)
  Purpose: 150-step 진행 추적
  Size: 15-20 KB
  Update: 각 에이전트 완료 시
  Content:
    - [x] Completed steps
    - [ ] Pending steps
    - Next action indicators

File 3: research-synthesis.md (Insights File)
  Purpose: 핵심 발견사항 압축
  Size: 3-4K words (~20-30 KB)
  Update: 각 Phase 완료 시
  Content:
    - Key findings
    - Hypotheses
    - Conceptual models
    - Critical insights
```

**사용 예시**:
```python
# 컨텍스트 리셋 후 복구
def load_session_context():
    # 1. Load session metadata
    with open("session.json") as f:
        session = json.load(f)

    # 2. Load progress
    checklist = parse_markdown("todo-checklist.md")
    last_step = find_last_completed(checklist)

    # 3. Load insights
    synthesis = load_markdown("research-synthesis.md")

    return {
        "session": session,
        "last_step": last_step,
        "insights": synthesis,
        "resume_from": last_step + 1
    }
```

### 3.4.2 Context Forking

**설계 목적**: 메인 컨텍스트 보호 + 리소스 집약적 작업 격리

**적용 Commands**:
```yaml
context: fork
commands:
  - run-literature-review  # Phase 1 전체 (60-90분)
  - run-research-design    # Phase 2 전체 (20-30분)
  - run-writing           # Phase 3 전체 (40-60분)
  - run-publication       # Phase 4 전체 (10-15분)
  - validate-all          # 전체 검증 (5-10분)
  - run-writing-validated # Phase 3 검증 실행
```

**이점**:
1. **메인 컨텍스트 보호**: Fork된 실행에서 에러 발생해도 메인 영향 없음
2. **Error Isolation**: 각 Phase는 독립적 실행 환경
3. **리소스 최적화**: Fork는 필요 시에만 context 복사

**작동 방식**:
```
Main Context
    ↓
/thesis:run-literature-review (context: fork)
    ↓
┌─────────────────────────────────────┐
│  Forked Context                      │
│  ├─ Copy: session.json              │
│  ├─ Copy: todo-checklist.md         │
│  ├─ Copy: research-synthesis.md     │
│  └─ Isolated execution               │
│      ├─ Wave 1-5 sequential         │
│      ├─ All agent outputs           │
│      └─ Quality validation           │
└─────────────────────────────────────┘
    ↓
Merge Results → Main Context
    ├─ Update session.json
    ├─ Update todo-checklist.md
    └─ Update research-synthesis.md
```

### 3.4.3 RLM Integration (200K+ Context)

**문제**: Claude 200K context window vs. 누적 150K+ tokens

**RLM 해결책**:
```python
# rlm_processor.py

def process_with_rlm(long_context, target_size=50000):
    """
    Zhang et al. 2025 - Section 2 패턴
    """
    if len(long_context) <= target_size:
        return long_context

    # Semantic chunking
    chunks = semantic_split(long_context, chunk_size=50000)

    # Parallel summarization (Haiku for cost)
    summaries = []
    for chunk in chunks:
        summary = llm_call(
            prompt=SUMMARIZE_TEMPLATE.format(chunk=chunk),
            model="claude-3-5-haiku",
            max_tokens=10000
        )
        summaries.append(summary)

    # Recursive merging
    merged = "\n\n---\n\n".join(summaries)
    if len(merged) > target_size:
        return process_with_rlm(merged, target_size)
    else:
        return merged

# RLM-enabled agents
rlm_agents = [
    "literature-searcher-rlm",      # 100 → 10K papers
    "synthesis-agent-rlm",          # Wave 1-4 통합 (150K)
    "thesis-writer-rlm",            # 전체 문헌 참조 (200K+)
    "plagiarism-checker-rlm",       # 15 files cross-check
    "conceptual-model-builder-rlm", # 14 files integration
    "unified-srcs-evaluator-rlm"    # 100+ claims evaluation
]
```

**효과**:
- 정보 손실: 70% → <10%
- 비용: $0.20-3 per task
- 컨텍스트: 100K → 200K+ effective
- 처리 시간: +10-20% (but 품질 우선)

## 3.5 Autopilot / Simulation System (v4 NEW) ⭐

**설계 목적**: 불확실성 수준에 따라 최적 실행 모드를 자동 선택하고, AlphaGo-style 품질 평가로 시뮬레이션 결과를 검증

### 3.5.1 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Autopilot System                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  /thesis:autopilot [on|off|status] [mode]                   │
│         ↓                                                    │
│  ┌─────────────────┐                                        │
│  │ autopilot-manager│  불확실성 분석 → 모드 자동 선택        │
│  └────────┬────────┘                                        │
│           ↓                                                  │
│  ┌─────────────────────┐                                    │
│  │ simulation-controller│  Quick/Full/Both 시뮬레이션 제어   │
│  └────────┬────────────┘                                    │
│           ↓                                                  │
│  ┌─────────────────────┐                                    │
│  │ alphago-evaluator   │  AlphaGo-style 품질 평가            │
│  │  ├─ pTCS check (75+)│                                    │
│  │  ├─ SRCS check (75+)│                                    │
│  │  └─ Plagiarism (<15%)│                                   │
│  └─────────────────────┘                                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.5.2 Simulation Modes

| 모드 | 설명 | 사용 시점 |
|------|------|-----------|
| **Quick** | 핵심 요소만 빠르게 시뮬레이션 | High uncertainty (>0.7) |
| **Full** | 전체 Phase 완전 시뮬레이션 | Low uncertainty (<0.3) |
| **Both** | Quick 선행 → Full 후행 | Medium uncertainty (0.3-0.7) |

### 3.5.3 Autopilot Modes

```bash
/thesis:autopilot on full        # 완전 자동 모드
/thesis:autopilot on semi        # 각 단계 확인 (반자동)
/thesis:autopilot on review-only # 결과 보고만, 자동 승인
/thesis:autopilot until phase2   # Phase 2까지만 자동 실행
/thesis:autopilot status         # 현재 상태 확인
/thesis:autopilot off            # 비활성화
```

**품질 미달 시**: pTCS/SRCS < 75 또는 표절 ≥ 15% → 자동 중단, 사용자 확인 요청

### 3.5.4 Agents

| Agent | 역할 |
|-------|------|
| `autopilot-manager` | 불확실성 분석, 실행 모드 자동 선택 |
| `simulation-controller` | Quick/Full/Both 시뮬레이션 제어 |
| `alphago-evaluator` | AlphaGo-style 품질 평가 (pTCS/SRCS/Plagiarism) |

## 3.6 Self-Improvement System (v4 NEW) ⭐

**설계 목적**: 워크플로우 성능을 분석하고 개선 제안을 도출하되, **모든 제안은 Advisory Only** (인간 결정 필수)

### 3.6.1 핵심 원칙

1. **Advisory Only**: 모든 제안은 자문 사항. 자동 수정 없음.
2. **Read-Only**: 기존 워크플로우 파일을 절대 수정하지 않음.
3. **Core Philosophy Preservation**: 10가지 불변 원칙 존중.

**CORE_PHILOSOPHY_INVARIANTS (불변 원칙)**:
1. ALL sub-agents use opus model
2. ALL execution is sequential (no parallel across phases)
3. GRA validation on ALL outputs
4. Cost/time are secondary to quality
5. English work + Korean translation
6. 9 HITL checkpoints (cannot add/remove)
7. 150-step granularity
8. Dual Confidence: pTCS (60%) + SRCS (40%)
9. Phase order: 0→1→2→3→4
10. Wave order within Phase 1: 1→2→3→4→5

### 3.6.2 Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│         Self-Improvement Pipeline (Advisory Only)            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  Step 1: Collect                                            │
│  ├─ performance_collector.py                                │
│  └─ 세션 데이터, gate 결과, agent 출력에서 메트릭 수집       │
│         ↓                                                    │
│  Step 2: Analyze                                            │
│  ├─ improvement_analyzer.py                                 │
│  └─ 메트릭 분석 → 개선 제안 생성                             │
│         ↓                                                    │
│  Step 3: Classify                                           │
│  ├─ change_classifier.py                                    │
│  └─ 제안별 위험도 분류 (Critical/High/Medium/Low)            │
│         ↓                                                    │
│  Step 4: Log                                                │
│  ├─ improvement_logger.py                                   │
│  └─ 이력 기록 (Audit Trail)                                  │
│         ↓                                                    │
│  Step 5: Report                                             │
│  ├─ self_improvement_engine.py (orchestrator)               │
│  └─ 인간 검토용 Advisory Report 생성                         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 3.6.3 Commands

| Command | Purpose |
|---------|---------|
| `/thesis:review-improvements` | 성능 분석 실행 + 제안 검토 |
| `/thesis:improvement-log` | 전체 개선 이력 조회 (Audit Trail) |

### 3.6.4 출력 위치

```
thesis-output/<project>/00-session/improvement-data/
├── performance-metrics-*.json      # 성능 메트릭
├── improvement-proposals-*.json    # 개선 제안
├── classified-proposals-*.json     # 위험도 분류
├── analysis-summary-*.json         # 분석 요약
└── improvement-history.json        # 전체 이력
```

### 3.6.5 제안 상태 관리

| 상태 | 의미 |
|------|------|
| proposed | 분석에서 도출 (검토 대기) |
| reviewed | 검토 완료 |
| accepted | 승인 (수동 적용 예정) |
| rejected | 거절 (조치 불필요) |
| deferred | 보류 (다음 검토 시 재확인) |
| noted | 참고 사항 |

---

# 4. Complete Workflow Specification

본 섹션은 전체 워크플로우를 Phase별로 상세히 설명합니다. 각 Phase의 목적, 에이전트 순서, 입출력 구조, HITL 체크포인트를 다룹니다.

## 4.1 Phase 0: Initialization & Mode Selection

### 4.1.1 Natural Language Trigger (v2.2.0 NEW)

**목적**: 사용자가 명령어 없이 자연어로 워크플로우를 시작할 수 있도록 지원

**지원 표현**:
```
한국어:
- "시작하자"
- "연구를 시작하자"
- "논문연구를 시작하자"
- "박사논문을 시작하자"
- "연구하자"

영어:
- "Let's start"
- "Start research"
- "Begin thesis"
- "Start dissertation"
```

**작동 메커니즘**:
```yaml
# .claude/skills/thesis-orchestrator/SKILL.md
description: |
  박사논문 연구 워크플로우 총괄 오케스트레이터.
  사용자가 (1) /thesis 명령어를 사용하거나,
  (2) "시작하자", "연구를 시작하자" 등 자연어로 연구 시작 의사를 표현하거나,
  (3) 논문 연구, 문헌검토, 연구설계, 논문작성 관련 작업을 요청하거나,
  (4) 학술적 연구 지원이 필요할 때 PROACTIVELY 사용.
```

**프로세스**:
```
User: "시작하자"
    ↓
Claude detects "PROACTIVELY" keyword in SKILL.md description
    ↓
Auto-execute: /thesis:quick-start
    ↓
AskUserQuestion: 7-mode selection UI
    ├─ Mode A: 연구 주제 입력
    ├─ Mode B: 연구질문 입력
    ├─ Mode C: 기존 문헌검토 업로드
    ├─ Mode D: 학습 모드
    ├─ Mode E: 선행연구 논문 업로드
    ├─ Mode F: 연구 프로포절 업로드 ⭐ (v4)
    └─ Mode G: 자유형식 텍스트 입력 ⭐ (v4)
    ↓
Mode-specific information gathering (2-3 questions)
    ↓
Auto-execute: /thesis:init
    ↓
Auto-execute: /thesis:start [mode] [input]
```

### 4.1.2 Session Initialization

**Command**: `/thesis:init`

**스크립트**: `init_session.py` (v2.2.0)

**프로세스**:
```python
def initialize_session():
    """
    새 연구 세션 초기화
    """
    # 1. Generate session ID
    session_id = generate_session_id()  # format: "topic-slug-YYYY-MM-DD"

    # 2. Create directory structure
    create_folder_structure(session_id)
    """
    thesis-output/{session_id}/
    ├── 00-session/
    │   ├── session.json
    │   └── todo-checklist.md
    ├── 00-paper-based-design/  # Mode E only
    ├── 01-literature/
    ├── 02-research-design/
    ├── 03-thesis/
    └── 04-publication/
    """

    # 3. Create session.json
    session = {
        "session_id": session_id,
        "created_at": datetime.now().isoformat(),
        "version": "2.2.0",
        "research_goals": {},
        "input_mode": None,  # A/B/C/D/E/F/G
        "research_type": None,  # quantitative/qualitative/mixed
        "hitl_snapshots": [],
        "current_phase": 0,
        "current_step": 0,
        "paper_metadata": {}  # Mode E only
    }
    save_json(session, "session.json")

    # 4. Create todo-checklist.md (150 steps)
    checklist = generate_checklist_template()
    save_markdown(checklist, "todo-checklist.md")

    # 5. Initialize research-synthesis.md
    synthesis = "# Research Synthesis\n\nTo be updated as research progresses."
    save_markdown(synthesis, "research-synthesis.md")

    return session_id
```

**출력**:
- `session.json`: 세션 메타데이터
- `todo-checklist.md`: 150-step 체크리스트
- `research-synthesis.md`: 빈 종합 파일
- Directory structure

### 4.1.3 Mode Selection (7 Modes)

#### Mode A: Research Topic Input

**프로세스**:
```
Input: 연구 주제 (자연어)
    ↓
topic-explorer agent
    ├─ Topic analysis
    ├─ Research context identification
    ├─ 5-7 Research Questions derivation
    └─ Preliminary literature scope
    ↓
HITL-1: Research Questions Approval
    ├─ User reviews generated RQs
    ├─ User selects primary RQs (3-5)
    └─ User confirms research direction
    ↓
Phase 1: Literature Review (with approved RQs)
```

**예시**:
```yaml
Input: "AI의 윤리적 의사결정 능력"

topic-explorer output:
  research_questions:
    - RQ1: "AI 시스템은 어떤 윤리적 프레임워크를 사용하는가?"
    - RQ2: "AI의 도덕적 판단은 인간의 판단과 어떻게 다른가?"
    - RQ3: "AI 윤리 알고리즘의 편향성은 어떻게 측정되는가?"
    - RQ4: "AI 윤리 교육 데이터는 어떤 기준으로 구성되는가?"
    - RQ5: "AI의 윤리적 의사결정 신뢰도를 어떻게 평가하는가?"

HITL-1:
  User selects: [RQ1, RQ2, RQ5]
  Confirmed → Phase 1
```

#### Mode B: Research Question(s) Input

**프로세스**:
```
Input: 1-5 Research Questions (직접 입력)
    ↓
Validation:
    ├─ Clarity check
    ├─ Specificity check
    └─ Researchability check
    ↓
HITL-1: Research Questions Confirmation
    ↓
Phase 1: Literature Review (direct entry)
```

**예시**:
```yaml
Input:
  - "RQ1: Transformer 아키텍처의 어텐션 메커니즘은 RNN 대비 어떤 장점을 제공하는가?"
  - "RQ2: BERT와 GPT의 사전학습 전략 차이는 무엇인가?"
  - "RQ3: Few-shot learning에서 프롬프트 엔지니어링의 효과는 어떻게 측정되는가?"

Validation: ✓ PASS (clear, specific, researchable)
HITL-1: Confirmed → Phase 1
```

#### Mode C: Existing Literature Review Upload

**프로세스**:
```
Input: 기존 문헌검토 파일 (.md, .docx, .pdf)
    ↓
Parse & Extract:
    ├─ Key findings
    ├─ Research gaps
    ├─ Theoretical frameworks
    └─ Citations
    ↓
gap-identifier agent
    ├─ Identify 3-5 research gaps
    ├─ Prioritize gaps by impact
    └─ Suggest research directions
    ↓
HITL-2: Gap Selection & Research Type
    ├─ User selects primary gap
    ├─ User confirms research type
    └─ User approves design approach
    ↓
Phase 2: Research Design (skip Phase 1)
```

**예시**:
```yaml
Input: existing-literature-review.pdf (30 pages)

gap-identifier output:
  gaps:
    - gap_1:
        description: "Few-shot learning에서 프롬프트 최적화 자동화 연구 부족"
        type: METHODOLOGICAL
        impact: HIGH
        suggested_approach: "강화학습 기반 프롬프트 최적화 알고리즘 개발"

    - gap_2:
        description: "다국어 모델의 언어간 전이 학습 메커니즘 불명확"
        type: THEORETICAL
        impact: MEDIUM
        suggested_approach: "Cross-lingual attention 패턴 시각화 및 분석"

HITL-2:
  User selects: gap_1
  Research type: Quantitative (실험 연구)
  Confirmed → Phase 2
```

#### Mode D: Learning Mode

**프로세스**:
```
Input: User selects "Learning Mode"
    ↓
Tutorial Menu:
    ├─ 1. Quantitative Research Methodology
    ├─ 2. Qualitative Research Methodology
    ├─ 3. Mixed Methods Research
    ├─ 4. Literature Review Techniques
    ├─ 5. Statistical Analysis Basics
    └─ 6. Academic Writing Standards
    ↓
Interactive Tutorial:
    ├─ Concept explanations
    ├─ Example walkthroughs
    ├─ Practice exercises
    └─ Q&A support
    ↓
Exit Learning Mode → Return to Mode Selection
```

**목적**: 연구 초보자를 위한 방법론 학습

#### Mode E: Paper Upload (v2.2.0 NEW) ⭐

**목적**: 선행연구 논문을 업로드하여 새로운 연구 제안 자동 생성

**프로세스**:
```
Input: 선행연구 논문 (.pdf, .docx)
    ↓
Upload to: user-resource/uploaded-papers/
    ↓
paper-research-designer agent (6 stages)
    ↓
Stage 1: Deep Paper Analysis (10-15 min)
    ├─ Research context & objectives
    ├─ Methodology & design
    ├─ Key findings & contributions
    ├─ Limitations acknowledged
    └─ Future directions suggested
    Output: paper-deep-analysis.md (5-7 pages)
    ↓
Stage 2: Strategic Gap Identification (8-12 min)
    ├─ Theoretical gaps
    ├─ Methodological gaps
    ├─ Contextual gaps
    └─ Impact assessment
    Output: strategic-gap-analysis.md (3-5 gaps)
    ↓
Stage 3: Novel Hypothesis Generation (15-20 min)
    ├─ Per gap: 2-3 hypotheses
    ├─ Testability evaluation
    ├─ Feasibility assessment
    └─ Impact prediction
    Output: novel-hypotheses.md (6-15 hypotheses)
    ↓
Stage 4: Research Design Proposal (20-30 min)
    ├─ Hypothesis selection
    ├─ Research questions derivation
    ├─ Methodology design
    │   ├─ Sample/Participants
    │   ├─ Data collection
    │   └─ Analysis plan
    └─ Expected outcomes
    Output: research-design-proposal.md (20-30 pages)
    ↓
Stage 5: Feasibility & Ethics (5-8 min)
    ├─ Resource requirements
    ├─ Timeline estimation
    ├─ Ethical considerations
    └─ Risk assessment
    Output: feasibility-ethics-report.md (5-8 pages)
    ↓
Stage 6: Integrated Proposal (5-10 min)
    ├─ Executive summary
    ├─ Full proposal synthesis
    ├─ Citation integration
    └─ Next steps roadmap
    Output: integrated-research-proposal.md (40-60 pages MASTER)
    ↓
HITL-1: Hypothesis Selection & Research Type
    ├─ User reviews 6-15 hypotheses
    ├─ User selects primary hypotheses (1-3)
    ├─ User confirms research type
    └─ User approves proceeding to Phase 1
    ↓
Phase 1: Literature Review (with Mode E context)
```

**Mode E 특징**:
- **Scientific Skills Integration**: peer-review, hypothesis-generation, statistical-analysis
- **Systematic Analysis**: 6단계 체계적 분석
- **Quality Output**: 40-60 page 통합 제안서
- **Novel Contributions**: 6-15 신규 가설

**예시**:
```yaml
Input: "smith-2023-transformer-optimization.pdf"

Stage 3 Output (Novel Hypotheses):
  hypotheses:
    - H1:
        text: "Sparse attention patterns는 dense attention 대비 계산 효율성과 성능 trade-off에서 최적점이 존재한다"
        gap: METHODOLOGICAL
        testability: HIGH
        feasibility: MEDIUM
        expected_impact: "Transformer inference 속도 2-3배 향상"

    - H2:
        text: "Low-rank decomposition을 통한 attention matrix 압축은 task-specific fine-tuning 성능에 부정적 영향을 미치지 않는다"
        gap: THEORETICAL
        testability: HIGH
        feasibility: HIGH
        expected_impact: "모델 크기 30-40% 감소"

    - H3:
        text: "Adaptive attention span 메커니즘은 sequence length에 따라 동적으로 조정되어 long-range dependency 학습을 개선한다"
        gap: METHODOLOGICAL
        testability: MEDIUM
        feasibility: LOW (구현 복잡도 높음)
        expected_impact: "Long document 처리 성능 향상"

HITL-1:
  User selects: [H1, H2]
  Research type: Quantitative (실험 비교)
  Confirmed → Phase 1 (with H1, H2 context)
```

#### Mode F: Proposal Upload (v4 NEW) ⭐

**목적**: 연구 프로포절을 업로드하여 기존 계획을 추출하고, 체계적 연구를 수행

**핵심 철학**: 사용자의 기존 연구 계획을 **존중하면서 보강**하는 시스템

**Mode E vs Mode F**:

| 항목 | Mode E (Paper Upload) | Mode F (Proposal Upload) |
|------|----------------------|--------------------------|
| 입력물 | 선행연구 논문 (타인의 논문) | 연구 프로포절 (나의 계획서) |
| 에이전트 | paper-research-designer | proposal-analyzer |
| 분석 목적 | 비판적 분석 → 새 가설 도출 | 구조 파싱 → 계획 추출 |
| 출력물 | 새로운 연구 제안서 (40-60p) | 추출된 연구 계획 + 완성도 평가 |
| HITL | review-proposal | review-extracted-plan |
| 특수 정책 | 없음 | Flag-and-Follow (모순 감지) |

**프로세스**:
```
Input: 연구 프로포절 파일 (.pdf, .docx, .md, .txt)
    ↓
Upload to: user-resource/proposals/
    ↓
Session Init (mode: proposal)
    ↓
proposal-analyzer agent
    ├─ 구조 파싱 → 연구 요소 추출
    │   ├─ research_questions (연구질문)
    │   ├─ hypotheses (가설)
    │   ├─ methodology_type + subtype
    │   ├─ theoretical_framework
    │   ├─ variables (IV (Independent Variable, 독립변수), DV (Dependent Variable, 종속변수), mediating (매개변수), moderating (조절변수))
    │   ├─ proposed_sample
    │   └─ proposed_analysis
    ├─ 완성도 평가 (completeness_score 0-100)
    └─ gap_report (누락 항목 식별)
    Output: 00-proposal-analysis/proposal-analysis.md
    ↓
HITL: /thesis:review-extracted-plan
    ├─ APPROVE: 추출된 계획대로 진행
    ├─ MODIFY: 특정 항목 수정
    └─ SUPPLEMENT: 누락 항목 보완
    ↓
Phase 1: Literature Review (기존 계획 검증을 위한 문헌검토)
```

**예시**:
```yaml
Input: "my-dissertation-proposal-2026.pdf"

proposal-analyzer output:
  extracted_plan:
    research_questions:
      - "RQ1: AI 변혁이 소규모 교회 운영에 미치는 영향은?"
      - "RQ2: AI 도입 프레임워크의 적용 가능성은?"
    hypotheses:
      - "H1: AI 도입은 교회 행정 효율성을 30% 향상시킨다"
    methodology_type: "mixed_methods"
    methodology_subtype: "sequential_explanatory"
    completeness_score: 72
    gap_report:
      - "변수의 조작적 정의 미흡"
      - "표본추출 전략 불명확"

HITL:
  User: APPROVE with SUPPLEMENT
  Added: 변수 정의 보완
  Confirmed → Phase 1 (계획 검증 문헌검토)
```

#### Mode G: Custom Input (v4 NEW) ⭐

**목적**: 자유형식 텍스트에서 연구 요소를 자동 추출하여 적절한 모드로 라우팅

**에이전트**: `custom-input-parser`

**프로세스**:
```
Input: 사용자의 자유형식 텍스트 (구조화되지 않은 연구 아이디어)
    ↓
custom-input-parser agent
    ├─ 텍스트 분석
    │   ├─ 연구 주제/관심사 추출
    │   ├─ 연구질문 유무 판별
    │   ├─ 방법론 선호도 감지
    │   └─ 기존 자료 참조 여부 확인
    ├─ 최적 모드 결정
    │   ├─ 연구 주제만 있음 → Mode A
    │   ├─ 연구질문 있음 → Mode B
    │   ├─ 문헌검토 언급 → Mode C
    │   ├─ 학습 요청 → Mode D
    │   ├─ 논문 파일 언급 → Mode E
    │   └─ 프로포절 파일 언급 → Mode F
    └─ 구조화된 입력으로 변환
    ↓
적절한 Mode로 자동 라우팅
    ↓
해당 Mode의 워크플로우 실행
```

**예시**:
```yaml
Input: "AI가 소규모 교회 운영에 어떤 영향을 줄 수 있는지 연구하고 싶어.
        특히 양적 연구로 접근하면 좋겠어."

custom-input-parser output:
  detected_elements:
    topic: "AI가 소규모 교회 운영에 미치는 영향"
    methodology_preference: "quantitative"
    has_research_questions: false
    has_paper: false
    has_proposal: false
  recommended_mode: "A"
  structured_input:
    topic: "AI가 소규모 교회 운영에 미치는 영향"
    context: "양적 연구 선호"

→ Auto-route to Mode A with structured input
```

## 4.2 Phase 1: Literature Review (15 Agents, 5 Waves)

**목적**: 연구 주제에 대한 체계적 문헌검토 수행

**전체 구조**:
```
Wave 1 (Search & Foundation) - 4 agents
    ↓ Gate 1: Cross-Validation
Wave 2 (Deep Analysis) - 4 agents
    ↓ Gate 2: Cross-Validation
Wave 3 (Critical Evaluation) - 4 agents
    ↓ Gate 3: Cross-Validation
Wave 4 (Synthesis & Integration) - 2 agents
    ↓ SRCS Full Evaluation
Wave 5 (Quality Assurance) - 3 agents
    ↓ Gate 4: Final Quality Gate
HITL-2: Literature Review Approval
```

### 4.2.1 Wave 1: Search & Foundation (4 Agents)

#### Agent 1: literature-searcher-rlm

**목적**: 대규모 문헌 검색 및 스크리닝

**입력**:
- Research questions (3-5)
- Keywords (auto-extracted)
- Date range (기본: 최근 10년)

**프로세스**:
```python
def literature_search(research_questions, keywords):
    """
    RLM-enabled large-scale literature search
    """
    # 1. Database search (multi-source)
    databases = [
        "Google Scholar",
        "PubMed",
        "IEEE Xplore",
        "ACM Digital Library",
        "ArXiv"
    ]

    raw_results = []
    for db in databases:
        results = search_database(db, keywords, max_results=1000)
        raw_results.extend(results)

    # Total: 100-5000 papers

    # 2. RLM batch screening
    if len(raw_results) > 100:
        screened = rlm_batch_screening(
            papers=raw_results,
            criteria={
                "relevance": research_questions,
                "quality": "peer-reviewed, citations > 10",
                "recency": "prefer recent"
            },
            target_size=50
        )
    else:
        screened = raw_results

    # 3. Quality filtering
    filtered = []
    for paper in screened:
        if meets_quality_criteria(paper):
            filtered.append(paper)

    # Final: 30-50 papers

    return filtered
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "LIT-SEARCH-001"
    text: "검색 결과 총 2,847편의 논문 중 품질 기준(peer-reviewed, citations>10, 최근 10년)을 만족하는 42편을 선별했다."
    claim_type: FACTUAL
    sources:
      - type: PRIMARY
        reference: "Database search results"
        verified: true
    confidence: 95
    papers_screened: 2847
    papers_selected: 42
```

**파일**:
- `wave1-literature-search.md` (10-15 pages)
- Database별 검색 결과
- 선별 기준 및 프로세스
- 선별된 논문 목록 (42편)

#### Agent 2: seminal-works-analyst

**목적**: 핵심 연구(seminal works) 식별 및 인용 네트워크 분석

**입력**:
- literature-searcher-rlm 출력 (42 papers)
- Research questions

**프로세스**:
```python
def identify_seminal_works(papers, research_questions):
    """
    핵심 연구 식별
    """
    # 1. Citation analysis
    citation_network = build_citation_network(papers)

    # 2. PageRank-style scoring
    scores = {}
    for paper in papers:
        score = (
            citation_network.incoming_citations(paper) * 0.4 +
            citation_network.co_citation_strength(paper) * 0.3 +
            relevance_to_rq(paper, research_questions) * 0.3
        )
        scores[paper] = score

    # 3. Select top 10-20
    seminal = sorted(papers, key=lambda p: scores[p], reverse=True)[:15]

    # 4. Thematic grouping
    themes = cluster_by_theme(seminal)

    return seminal, themes
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "SEMINAL-001"
    text: "Vaswani et al. (2017)의 'Attention is All You Need'는 본 연구 주제의 핵심 논문으로, 542회 인용되었으며 Transformer 아키텍처의 기초를 확립했다."
    claim_type: FACTUAL
    sources:
      - type: PRIMARY
        reference: "Vaswani, A., et al. (2017)"
        doi: "10.48550/arXiv.1706.03762"
        verified: true
    confidence: 95
    citation_count: 542
    co_citation_strength: 0.87
```

**파일**:
- `wave1-seminal-works-analysis.md` (8-12 pages)
- 핵심 논문 15편 상세 분석
- 인용 네트워크 시각화
- 주제별 그룹핑

#### Agent 3: trend-analyst

**목적**: 연구 트렌드 및 시계열 분석

**입력**:
- Wave 1 전체 출력 (42 papers + 15 seminal)
- Research questions

**프로세스**:
```python
def analyze_trends(papers, seminal_works):
    """
    시계열 연구 트렌드 분석
    """
    # 1. Temporal grouping (by year)
    by_year = group_by_publication_year(papers)

    # 2. Topic evolution
    topics = []
    for year in sorted(by_year.keys()):
        year_papers = by_year[year]
        year_topics = extract_topics(year_papers)  # LDA (Latent Dirichlet Allocation, 잠재 디리클레 할당) or similar
        topics.append({
            "year": year,
            "topics": year_topics,
            "papers": year_papers
        })

    # 3. Trend identification
    trends = {
        "emerging": find_emerging_topics(topics),  # 최근 2-3년 급증
        "declining": find_declining_topics(topics),  # 감소 추세
        "stable": find_stable_topics(topics)  # 꾸준히 연구
    }

    # 4. Future projection
    projection = extrapolate_trends(trends, horizon=3)  # 3년 예측

    return trends, projection
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "TREND-001"
    text: "2020-2023년 사이 'sparse attention' 관련 연구가 연평균 45% 증가했으며, 이는 계산 효율성에 대한 관심 증가를 반영한다."
    claim_type: EMPIRICAL
    sources:
      - type: SECONDARY
        reference: "Publication trend analysis (n=42)"
        verified: true
    confidence: 85
    uncertainty: "샘플 크기(n=42)가 제한적이어서 전체 분야 트렌드를 완전히 대표하지 못할 수 있음"
    data:
      2020: 3
      2021: 5
      2022: 7
      2023: 12
      growth_rate: 45%
```

**파일**:
- `wave1-trend-analysis.md` (10-15 pages)
- 연도별 논문 분포
- 주제 진화 시각화
- Emerging/Declining topics
- 3년 미래 예측

#### Agent 4: methodology-scanner

**목적**: 연구 방법론 패턴 분석

**입력**:
- Wave 1 전체 출력 (42 papers)

**프로세스**:
```python
def scan_methodologies(papers):
    """
    방법론 패턴 추출 및 분류
    """
    # 1. Method extraction
    methods = []
    for paper in papers:
        method = extract_methodology(paper)  # NLP (Natural Language Processing, 자연어 처리)-based
        methods.append({
            "paper": paper,
            "research_type": method.research_type,  # quant/qual/mixed
            "design": method.design,  # experimental/survey/case study
            "data_collection": method.data_collection,
            "analysis": method.analysis_techniques,
            "sample_size": method.sample_size
        })

    # 2. Frequency analysis
    method_freq = {
        "research_type": count_frequency([m["research_type"] for m in methods]),
        "design": count_frequency([m["design"] for m in methods]),
        "analysis": count_frequency([m["analysis"] for m in methods])
    }

    # 3. Common patterns
    patterns = identify_common_patterns(methods)

    # 4. Best practices
    best_practices = identify_best_practices(
        methods,
        criteria=["sample_size", "validity", "reliability"]
    )

    return method_freq, patterns, best_practices
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "METHOD-001"
    text: "분석 대상 논문의 71% (30/42)가 실험 연구 설계를 채택했으며, 그 중 83% (25/30)가 A/B 테스트 또는 통제 실험을 사용했다."
    claim_type: FACTUAL
    sources:
      - type: SECONDARY
        reference: "Methodology analysis (n=42)"
        verified: true
    confidence: 95
    data:
      experimental: 30
      survey: 8
      case_study: 4
      ab_test: 25
      controlled_experiment: 25
```

**파일**:
- `wave1-methodology-scan.md` (8-12 pages)
- 방법론 분류 및 빈도
- Common patterns
- Best practices 추천

### 4.2.2 Gate 1: Cross-Validation

**목적**: Wave 1 에이전트 간 일관성 검증

**프로세스**:
```python
def cross_validate_wave1():
    """
    Wave 1 4개 에이전트 출력 교차 검증
    """
    # 1. Citation consistency
    papers_from_searcher = set(literature_searcher.papers)
    papers_cited_in_seminal = set(seminal_works_analyst.all_citations)
    papers_cited_in_trend = set(trend_analyst.all_citations)

    overlap = (
        papers_from_searcher & papers_cited_in_seminal & papers_cited_in_trend
    )
    consistency = len(overlap) / len(papers_from_searcher)

    if consistency < 0.7:
        raise ValidationError("Citation consistency too low")

    # 2. Claim consistency
    seminal_claims = seminal_works_analyst.key_findings
    trend_claims = trend_analyst.key_findings

    contradictions = find_contradictions(seminal_claims, trend_claims)
    if contradictions:
        raise ValidationError(f"Found {len(contradictions)} contradictions")

    # 3. GRA compliance
    for agent in [literature_searcher, seminal_works_analyst, trend_analyst, methodology_scanner]:
        gra_score = validate_gra(agent.output)
        if gra_score < 0.95:
            raise ValidationError(f"{agent.name} GRA compliance: {gra_score}")

    return {
        "citation_consistency": consistency,
        "contradictions": 0,
        "gra_compliance": "PASS"
    }
```

**통과 기준**:
- Citation consistency >= 70%
- No contradictions
- GRA compliance >= 95%

**실패 시**: Wave 1 재실행

### 4.2.3 Wave 2: Deep Analysis (4 Agents)

#### Agent 5: theoretical-framework-analyst

**목적**: 이론적 프레임워크 식별 및 분석

**입력**:
- Wave 1 전체 출력
- Research questions

**프로세스**:
```python
def analyze_theoretical_frameworks(wave1_output):
    """
    이론적 프레임워크 추출 및 분류
    """
    # 1. Theory extraction
    theories = []
    for paper in wave1_output.all_papers:
        theory = extract_theoretical_framework(paper)
        if theory:
            theories.append({
                "name": theory.name,
                "category": theory.category,  # cognitive/behavioral/systems
                "application": theory.application_in_paper,
                "source_paper": paper
            })

    # 2. Frequency & dominance
    theory_freq = count_frequency([t["name"] for t in theories])

    # 3. Framework comparison
    major_theories = [t for t, count in theory_freq.most_common(5)]
    comparison = compare_frameworks(major_theories)

    # 4. Applicability to current research
    applicability = assess_applicability(major_theories, research_questions)

    return theories, comparison, applicability
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "THEORY-001"
    text: "Transformer 연구에서 가장 많이 사용되는 이론적 프레임워크는 Information Theory (15편, 36%)와 Representation Learning Theory (12편, 29%)이다."
    claim_type: FACTUAL
    sources:
      - type: SECONDARY
        reference: "Theoretical framework analysis (n=42)"
        verified: true
    confidence: 90
    data:
      information_theory: 15
      representation_learning: 12
      optimization_theory: 8
      other: 7
```

**파일**:
- `wave2-theoretical-frameworks.md` (12-18 pages)
- 이론 분류 및 빈도
- 주요 이론 비교
- 본 연구 적용 가능성

#### Agent 6: empirical-evidence-analyst

**목적**: 실증적 증거 종합 및 효과크기 분석

**입력**:
- Wave 1 전체 출력
- Wave 2: theoretical-framework-analyst 출력

**프로세스**:
```python
def synthesize_empirical_evidence(wave1_output, frameworks):
    """
    실증 연구 결과 종합
    """
    # 1. Extract empirical findings
    findings = []
    for paper in wave1_output.all_papers:
        if paper.research_type == "quantitative":
            finding = extract_empirical_results(paper)
            findings.append({
                "paper": paper,
                "hypothesis": finding.hypothesis,
                "result": finding.result,  # supported/rejected/inconclusive
                "effect_size": finding.effect_size,  # d, r, OR 등
                "p_value": finding.p_value,
                "sample_size": finding.sample_size
            })

    # 2. Meta-analysis (if applicable)
    if len(findings) >= 5:
        meta = perform_meta_analysis(findings)
    else:
        meta = None

    # 3. Evidence strength classification
    for finding in findings:
        finding["strength"] = classify_evidence_strength(
            effect_size=finding["effect_size"],
            p_value=finding["p_value"],
            sample_size=finding["sample_size"]
        )  # strong/moderate/weak

    # 4. Synthesis by hypothesis
    synthesis = group_findings_by_hypothesis(findings)

    return findings, meta, synthesis
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "EMPIRICAL-001"
    text: "Transformer의 self-attention 메커니즘이 RNN (Recurrent Neural Network, 순환 신경망) 대비 장거리 의존성 학습에서 우수하다는 가설은 12편의 실험 연구에서 지지되었다 (평균 효과크기 d=0.72, 95% CI (Confidence Interval, 신뢰구간) [0.58, 0.86])."
    claim_type: EMPIRICAL
    sources:
      - type: PRIMARY
        reference: "Meta-analysis of 12 experimental studies"
        verified: true
    confidence: 85
    uncertainty: "효과크기는 task와 dataset에 따라 변동 (d=0.45-1.20)"
    meta_analysis:
      studies: 12
      total_n: 3847
      mean_effect_size: 0.72
      ci_95: [0.58, 0.86]
      heterogeneity_i2: 0.42
```

**파일**:
- `wave2-empirical-evidence.md` (15-20 pages)
- 실증 연구 결과 종합
- 메타분석 (해당 시)
- 증거 강도별 분류

#### Agent 7: gap-identifier

**목적**: 연구 갭 식별 및 우선순위 결정

**입력**:
- Wave 1 전체 출력
- Wave 2: theoretical-framework-analyst + empirical-evidence-analyst

**프로세스**:
```python
def identify_research_gaps(wave1, wave2):
    """
    3-5 연구 갭 식별
    """
    # 1. Theoretical gaps
    theoretical_gaps = []
    for theory in wave2.frameworks:
        if theory.application_count < 3:  # underexplored
            theoretical_gaps.append({
                "type": "THEORETICAL",
                "description": f"{theory.name} 이론의 적용 연구 부족",
                "evidence": theory,
                "potential": assess_research_potential(theory)
            })

    # 2. Methodological gaps
    methodological_gaps = []
    common_methods = wave1.methodology_scanner.patterns
    for method in ALL_RESEARCH_METHODS:
        if method not in common_methods:
            methodological_gaps.append({
                "type": "METHODOLOGICAL",
                "description": f"{method} 방법론 미적용",
                "potential": assess_method_potential(method, research_questions)
            })

    # 3. Contextual gaps
    contextual_gaps = identify_contextual_gaps(wave1, wave2)

    # 4. Empirical gaps
    empirical_gaps = []
    for hypothesis in wave2.empirical.hypotheses:
        if hypothesis.evidence_strength == "weak":
            empirical_gaps.append({
                "type": "EMPIRICAL",
                "description": f"{hypothesis.text} - 증거 부족",
                "current_evidence": hypothesis,
                "needed": "추가 실험 연구"
            })

    # 5. Prioritization
    all_gaps = theoretical_gaps + methodological_gaps + contextual_gaps + empirical_gaps
    prioritized = prioritize_gaps(
        all_gaps,
        criteria=["impact", "feasibility", "novelty"]
    )

    return prioritized[:5]  # Top 5 gaps
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "GAP-001"
    text: "Sparse attention 메커니즘의 이론적 최적화 기준에 대한 연구가 부족하다. 42편 중 단 2편만이 sparsity pattern 선택의 이론적 근거를 제시했다."
    claim_type: THEORETICAL
    gap_type: THEORETICAL
    sources:
      - type: SECONDARY
        reference: "Literature analysis (n=42)"
        verified: true
    confidence: 80
    uncertainty: "샘플 외 추가 연구가 존재할 가능성"
    impact: HIGH
    feasibility: MEDIUM
    novelty: HIGH
```

**파일**:
- `wave2-research-gaps.md` (10-15 pages)
- 3-5 우선순위 갭
- 갭별 영향력, 실행가능성 평가
- 후속 연구 제안

#### Agent 8: variable-relationship-analyst-rlm

**목적**: 변수 간 관계 패턴 분석 (RLM-enabled for large context)

**입력**:
- Wave 1 전체 출력
- Wave 2: 전체 출력 (theoretical + empirical + gaps)

**프로세스**:
```python
def analyze_variable_relationships(wave1, wave2):
    """
    RLM을 사용한 변수 관계 분석
    """
    # 1. Variable extraction
    variables = []
    for paper in wave1.all_papers:
        vars_in_paper = extract_variables(paper)
        variables.extend(vars_in_paper)

    # Deduplication
    unique_variables = deduplicate_variables(variables)

    # 2. Relationship extraction (RLM-enabled)
    relationships = []
    for paper in wave1.all_papers:
        # RLM: Handle long papers (>50K tokens)
        if len(paper.full_text) > 50000:
            compressed = rlm_summarize(
                paper.full_text,
                focus="variable relationships",
                target_size=10000
            )
            rels = extract_relationships(compressed)
        else:
            rels = extract_relationships(paper.full_text)

        relationships.extend(rels)

    # 3. Relationship types
    for rel in relationships:
        rel["type"] = classify_relationship(rel)
        # Types: causal, correlational, moderating, mediating

    # 4. Network construction
    network = build_variable_network(unique_variables, relationships)

    # 5. Central variables (PageRank)
    central_vars = network.pagerank(top_k=10)

    return unique_variables, relationships, network, central_vars
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "VAR-REL-001"
    text: "Attention head 수(H)와 모델 성능(P) 간에는 비선형 관계가 존재하며, 8편의 연구에서 H=8-16일 때 성능 향상이 포화된다고 보고했다."
    claim_type: EMPIRICAL
    sources:
      - type: PRIMARY
        reference: "Variable relationship analysis (n=8 studies)"
        verified: true
    confidence: 80
    uncertainty: "Task와 dataset에 따라 최적 H 값이 다를 수 있음"
    relationship_type: NON-LINEAR
    variables:
      independent: "Attention head count (H)"
      dependent: "Model performance (P)"
      moderator: "Task type"
```

**파일**:
- `wave2-variable-relationships.md` (12-18 pages)
- 변수 목록 및 정의
- 관계 네트워크 시각화
- 핵심 변수 식별
- 관계 유형별 분류

### 4.2.4 Gate 2: Cross-Validation

**프로세스**: Gate 1과 유사, Wave 2 에이전트 간 교차 검증

**추가 검증**:
- 이론과 실증 간 일관성
- 갭 식별의 타당성
- 변수 관계의 증거 충분성

### 4.2.5 Wave 3: Critical Evaluation (4 Agents)

#### Agent 9: critical-reviewer

**목적**: 선행연구의 논리적 일관성 및 주장-증거 적합성 비판적 평가

**프로세스**: 각 주요 논문의 연구 설계, 데이터 분석, 결론 도출 과정 비판적 검토

**출력**: 논리적 약점, 과도한 일반화, 대안 해석 가능성 지적

#### Agent 10: methodology-critic

**목적**: 방법론적 강점과 약점 평가

**프로세스**: 타당도, 신뢰도, 일반화 가능성 분석

**출력**: 방법론적 한계 및 개선 제안

#### Agent 11: limitation-analyst

**목적**: 선행연구의 공통 한계점 종합

**프로세스**: 연구별 limitations section 분석 및 패턴 식별

**출력**: 공통 한계 3-5개, 본 연구에서 극복 가능한 한계 식별

#### Agent 12: future-direction-analyst

**목적**: 선행연구가 제안한 미래 연구 방향 종합

**프로세스**: Future work sections 분석 및 빈도 집계

**출력**: 가장 많이 제안된 방향 5-10개, 본 연구와의 연결점

### 4.2.6 Gate 3: Cross-Validation

Wave 3 에이전트 간 일관성 및 Wave 1-2 결과와의 정합성 검증

### 4.2.7 Wave 4: Synthesis & Integration (2 Agents)

#### Agent 13: synthesis-agent-rlm

**목적**: Wave 1-3 전체 통합 종합 (RLM-enabled)

**입력**:
- Wave 1 전체 출력 (~40K tokens)
- Wave 2 전체 출력 (~50K tokens)
- Wave 3 전체 출력 (~40K tokens)
- Total: ~130K tokens

**RLM 프로세스**:
```python
def synthesize_literature_review(wave1, wave2, wave3):
    """
    RLM을 사용한 대규모 문헌 종합
    """
    # 1. Concatenate all outputs
    all_content = concatenate([
        wave1.full_output,
        wave2.full_output,
        wave3.full_output
    ])  # ~130K tokens

    # 2. RLM progressive compression
    compressed = rlm_progressive_compression(
        content=all_content,
        stages=3,  # 130K → 60K → 30K → 15K
        preserve=["key_findings", "gaps", "variables", "critiques"]
    )

    # 3. Synthesis generation
    synthesis = generate_synthesis(
        compressed_input=compressed,
        structure={
            "introduction": "Research landscape overview",
            "theoretical_foundations": "From Wave 2",
            "empirical_evidence": "From Wave 2",
            "research_gaps": "From Wave 2",
            "methodological_landscape": "From Wave 1 + Wave 3",
            "critical_evaluation": "From Wave 3",
            "synthesis": "Integration and implications"
        }
    )

    return synthesis  # 3-4K words
```

**출력**:
- `wave4-literature-synthesis.md` (3-4K words, ~20-30 pages)
- 전체 문헌검토 통합
- 핵심 발견사항
- 연구 갭 요약
- 본 연구의 포지셔닝

#### Agent 14: conceptual-model-builder-rlm

**목적**: 통합 개념 모델 구축 (RLM-enabled)

**프로세스**:
- Wave 2 변수 관계 네트워크 기반
- Wave 2 이론적 프레임워크 통합
- Wave 3 비판적 평가 반영
- 시각적 모델 생성 (Mermaid diagram)

**출력**:
- `wave4-conceptual-model.md` (10-15 pages)
- 통합 개념 모델
- 변수 간 관계 다이어그램
- 가설 도출 근거

### 4.2.8 SRCS Full Evaluation

Wave 4 출력물에 대한 전체 SRCS 평가

**프로세스**:
```python
def evaluate_srcs_full(wave4_synthesis, wave4_model):
    """
    SRCS 4-axis 전체 평가
    """
    # Extract all claims
    all_claims = extract_claims([wave4_synthesis, wave4_model])

    # SRCS scoring
    scores = []
    for claim in all_claims:
        score = {
            "claim_id": claim.id,
            "CS": citation_score(claim),  # 35%
            "GS": grounding_score(claim),  # 35%
            "US": uncertainty_score(claim),  # 10%
            "VS": verifiability_score(claim),  # 20%
            "total": None
        }
        score["total"] = (
            0.35 * score["CS"] +
            0.35 * score["GS"] +
            0.10 * score["US"] +
            0.20 * score["VS"]
        )
        scores.append(score)

    # Average
    avg_srcs = sum(s["total"] for s in scores) / len(scores)

    if avg_srcs < 75:
        raise QualityError(f"SRCS score {avg_srcs} below threshold 75")

    return {
        "average_srcs": avg_srcs,
        "claim_scores": scores,
        "grade": assign_grade(avg_srcs)
    }
```

**통과 기준**: SRCS >= 75

### 4.2.9 Wave 5: Quality Assurance (3 Agents)

#### Agent 15: plagiarism-checker-rlm

**목적**: 표절 검사 및 원본성 확인 (RLM-enabled for cross-checking 15 files)

**프로세스**:
```python
def check_plagiarism(all_wave_outputs):
    """
    RLM을 사용한 대규모 표절 검사
    """
    # 1. Collect all outputs (15 files from Wave 1-4)
    files = [
        wave1.literature_search,
        wave1.seminal_works,
        wave1.trend_analysis,
        wave1.methodology_scan,
        wave2.theoretical_frameworks,
        wave2.empirical_evidence,
        wave2.research_gaps,
        wave2.variable_relationships,
        wave3.critical_review,
        wave3.methodology_critique,
        wave3.limitations,
        wave3.future_directions,
        wave4.synthesis,
        wave4.conceptual_model
    ]  # Total: ~200K tokens

    # 2. RLM batch comparison
    similarities = []
    for i, file1 in enumerate(files):
        for j, file2 in enumerate(files[i+1:], start=i+1):
            sim = rlm_similarity_check(file1, file2)
            if sim > 0.15:  # > 15% threshold
                similarities.append({
                    "file1": file1.name,
                    "file2": file2.name,
                    "similarity": sim,
                    "overlapping_text": extract_overlap(file1, file2)
                })

    # 3. External plagiarism check (vs. source papers)
    external_sims = []
    for file in files:
        for source_paper in all_source_papers:
            sim = rlm_similarity_check(file, source_paper)
            if sim > 0.15:
                external_sims.append({
                    "our_file": file.name,
                    "source": source_paper.reference,
                    "similarity": sim
                })

    # 4. Final verdict
    max_sim = max([s["similarity"] for s in similarities + external_sims])
    if max_sim > 0.15:
        raise PlagiarismError(f"Similarity {max_sim} exceeds 15% threshold")

    return {
        "max_similarity": max_sim,
        "verdict": "PASS" if max_sim <= 0.15 else "FAIL",
        "details": similarities + external_sims
    }
```

**통과 기준**: Max similarity <= 15%

**출력**:
- `wave5-plagiarism-report.md` (5-10 pages)
- 유사도 매트릭스
- 주의 구간 (10-15%)
- 재작성 권장 사항 (if any)

#### Agent 16: unified-srcs-evaluator-rlm

**목적**: 전체 연구 주장(100+ claims) 통합 SRCS 평가

**프로세스**:
```python
def unified_srcs_evaluation(all_outputs):
    """
    RLM을 사용한 100+ claims 평가
    """
    # 1. Extract all claims from 15 files
    all_claims = []
    for file in all_outputs:
        claims = extract_grounded_claims(file)
        all_claims.extend(claims)

    # Total: 100-200 claims

    # 2. RLM batch SRCS scoring
    if len(all_claims) > 50:
        scores = rlm_batch_srcs_scoring(
            claims=all_claims,
            batch_size=20
        )
    else:
        scores = [score_claim_srcs(c) for c in all_claims]

    # 3. Statistics
    stats = {
        "total_claims": len(all_claims),
        "average_srcs": mean(scores),
        "median_srcs": median(scores),
        "min_srcs": min(scores),
        "max_srcs": max(scores),
        "below_threshold": sum(1 for s in scores if s < 75)
    }

    # 4. Per-axis breakdown
    axis_stats = {
        "CS": mean([c.CS for c in all_claims]),
        "GS": mean([c.GS for c in all_claims]),
        "US": mean([c.US for c in all_claims]),
        "VS": mean([c.VS for c in all_claims])
    }

    # 5. Low-scoring claims (for revision)
    low_scorers = [c for c in all_claims if c.srcs_score < 75]

    if stats["average_srcs"] < 75:
        raise QualityError(f"Average SRCS {stats['average_srcs']} below 75")

    return stats, axis_stats, low_scorers
```

**통과 기준**:
- Average SRCS >= 75
- No more than 10% claims below 60

**출력**:
- `wave5-unified-srcs-evaluation.md` (15-20 pages)
- SRCS 통계
- Axis별 분석
- 저점수 claim 목록
- 개선 권장사항

#### Agent 17: research-synthesizer

**목적**: 최종 문헌검토 보고서 생성

**입력**:
- Wave 1-4 전체 출력
- Wave 5: plagiarism report + SRCS evaluation

**프로세스**:
```python
def generate_final_literature_review(waves, quality_reports):
    """
    최종 문헌검토 문서 생성
    """
    # 1. Executive summary (1 page)
    exec_summary = summarize_key_points(waves, max_words=500)

    # 2. Full synthesis (from Wave 4)
    full_synthesis = waves.wave4.synthesis

    # 3. Conceptual model (from Wave 4)
    conceptual_model = waves.wave4.conceptual_model

    # 4. Research gaps & opportunities (from Wave 2)
    gaps = waves.wave2.research_gaps

    # 5. Methodological landscape (from Wave 1 + 3)
    methodology = combine([
        waves.wave1.methodology_scan,
        waves.wave3.methodology_critique
    ])

    # 6. Quality assurance report (from Wave 5)
    qa_report = quality_reports

    # 7. References (all unique citations)
    references = collect_all_references(waves)

    # 8. Combine into final document
    final_doc = structure_document({
        "executive_summary": exec_summary,
        "introduction": generate_introduction(),
        "theoretical_foundations": waves.wave2.theoretical_frameworks,
        "empirical_evidence": waves.wave2.empirical_evidence,
        "research_gaps": gaps,
        "methodological_landscape": methodology,
        "conceptual_model": conceptual_model,
        "critical_evaluation": waves.wave3.all_critiques,
        "synthesis": full_synthesis,
        "quality_assurance": qa_report,
        "references": references
    })

    return final_doc
```

**출력**:
- `research-synthesis.md` (English, 3-4K words, ~30-40 pages)
- Complete literature review
- All sections integrated
- Full references

**자동 번역**:
```python
# Parallel translation
academic_translator.translate(
    source="research-synthesis.md",
    target_lang="Korean",
    output="research-synthesis-ko.md"
)
```

### 4.2.10 Gate 4: Final Quality Gate

**검증 항목**:
1. GRA compliance: 100% (all claims with GroundedClaim schema)
2. pTCS (Phase-level): >= 75
3. SRCS (Average): >= 75
4. Plagiarism: <= 15%
5. Citation count: >= 30 unique sources
6. Word count: 3,000-4,000 words (synthesis)

**통과 조건**: 모든 항목 PASS

**실패 시**: 해당 항목 재작업

### 4.2.11 HITL-2: Literature Review Approval

**프로세스**:
```
System presents to user:
    ├─ research-synthesis.md (English)
    ├─ research-synthesis-ko.md (Korean)
    ├─ wave5-unified-srcs-evaluation.md (Quality report)
    └─ Interactive summary

User reviews:
    ├─ Key findings sufficient?
    ├─ Research gaps appropriate?
    ├─ Conceptual model clear?
    └─ Ready to proceed?

User decision:
    ├─ APPROVE → Phase 2
    ├─ REQUEST REVISION → specify areas → Wave X re-run
    └─ REJECT → back to Phase 0
```

**AskUserQuestion UI**:
```yaml
questions:
  - question: "문헌검토 결과를 승인하시겠습니까?"
    header: "Literature Review"
    options:
      - label: "승인 (Phase 2 진행)"
        description: "문헌검토가 충분합니다. 연구설계 단계로 진행합니다."
      - label: "수정 요청"
        description: "특정 부분 보완이 필요합니다."
      - label: "거부 (재시작)"
        description: "연구 방향을 재설정해야 합니다."
```

**승인 시**:
- `session.json` 업데이트: `current_phase = 2`
- `todo-checklist.md`: Phase 1 items 체크 완료
- `research-synthesis.md`: Phase 1 Insights File로 고정
- → Phase 2 시작

---

## 4.3 Phase 2: Research Design (4-10 Agents, Type-Dependent)

**목적**: 승인된 연구 갭과 가설을 기반으로 체계적 연구 설계 수행

**분기 구조**:
```
HITL-3: Research Type Selection
    ├─ Quantitative Research → 4 agents
    ├─ Qualitative Research → 4 agents
    └─ Mixed Methods Research → 8 agents (quant + qual + integration)
```

### 4.3.1 HITL-3: Research Type Selection

**AskUserQuestion**:
```yaml
questions:
  - question: "어떤 연구 유형으로 진행하시겠습니까?"
    header: "Research Type"
    options:
      - label: "양적연구 (Quantitative)"
        description: "가설 검증, 실험, 통계 분석"
      - label: "질적연구 (Qualitative)"
        description: "현상 탐색, 인터뷰, 사례 연구"
      - label: "혼합연구 (Mixed Methods)"
        description: "양적 + 질적 통합"
```

### 4.3.2 Quantitative Branch (4 Agents)

#### Agent 18: hypothesis-developer

**목적**: 연구가설 개발 및 형식화

**입력**:
- Phase 1: research-synthesis.md (gaps)
- Mode E: novel-hypotheses.md (if applicable)

**프로세스**:
```python
def develop_hypotheses(research_gaps, mode_e_hypotheses=None):
    """
    검증 가능한 가설 개발
    """
    hypotheses = []

    # Mode E: Start from generated hypotheses
    if mode_e_hypotheses:
        for h in mode_e_hypotheses.selected:  # User-selected in HITL-1
            hypotheses.append({
                "id": h.id,
                "text": h.text,
                "type": h.type,  # null/alternative
                "variables": identify_variables(h.text),
                "testable": True,
                "source": "Mode E"
            })

    # From research gaps
    for gap in research_gaps:
        if gap.type in ["EMPIRICAL", "METHODOLOGICAL"]:
            h = formulate_hypothesis(gap)
            hypotheses.append({
                "id": generate_hypothesis_id(),
                "text": h.text,
                "type": "alternative",
                "variables": h.variables,
                "testable": assess_testability(h),
                "source": "Research Gap"
            })

    # Null hypotheses (auto-generate)
    for h in hypotheses:
        if h["type"] == "alternative":
            null_h = generate_null_hypothesis(h)
            hypotheses.append(null_h)

    return hypotheses
```

**출력** (GroundedClaim):
```yaml
claims:
  - id: "HYPO-001"
    text: "H1: Sparse attention pattern은 dense attention 대비 계산 복잡도를 50% 이상 감소시킬 것이다."
    claim_type: THEORETICAL
    hypothesis_type: ALTERNATIVE
    sources:
      - type: SECONDARY
        reference: "Research Gap Analysis (GAP-001)"
        verified: true
    confidence: 75
    variables:
      independent: "Attention pattern type (sparse vs. dense)"
      dependent: "Computational complexity (FLOPs (Floating Point Operations, 부동소수점 연산 횟수))"
      control: ["Model size", "Sequence length"]
```

**파일**:
- `02-research-design/hypotheses.md` (5-10 pages)
- 3-6 가설 (null + alternative)
- 변수 정의
- 조작적 정의

#### Agent 19: research-model-developer

**목적**: 연구 모델 및 변수 조작적 정의

**프로세스**:
```python
def develop_research_model(hypotheses):
    """
    연구 모델 개발
    """
    # 1. Variable extraction
    variables = []
    for h in hypotheses:
        variables.extend(h["variables"])

    unique_vars = deduplicate(variables)

    # 2. Operational definitions
    operational_defs = {}
    for var in unique_vars:
        operational_defs[var.name] = {
            "conceptual_definition": define_conceptually(var),
            "operational_definition": define_operationally(var),
            "measurement": specify_measurement(var),
            "scale": specify_scale(var)  # nominal/ordinal/interval/ratio
        }

    # 3. Relationship model (path diagram)
    model = construct_path_model(hypotheses, operational_defs)

    # 4. Measurement instruments
    instruments = select_instruments(operational_defs)

    return operational_defs, model, instruments
```

**출력**:
- `02-research-design/research-model.md` (15-20 pages)
- 변수 조작적 정의
- Path diagram (Mermaid)
- 측정 도구 선정

#### Agent 20: sampling-designer

**목적**: 표본 설계 및 표본크기 결정

**프로세스**:
```python
def design_sampling(hypotheses, operational_defs):
    """
    표본 설계
    """
    # 1. Population definition
    population = define_population(hypotheses)

    # 2. Sampling method
    sampling_method = select_sampling_method(
        population=population,
        research_type="quantitative",
        accessibility=assess_accessibility(population)
    )  # Probability: simple random, stratified, cluster
       # Non-probability: convenience, purposive, quota

    # 3. Sample size calculation
    effect_size = estimate_effect_size(hypotheses, literature_review)
    alpha = 0.05  # Type I error
    beta = 0.20   # Type II error (power = 0.80)
    sample_size = calculate_sample_size(
        effect_size=effect_size,
        alpha=alpha,
        power=1-beta,
        test_type=identify_statistical_test(hypotheses)
    )

    # 4. Inclusion/Exclusion criteria
    criteria = define_criteria(population, research_context)

    return {
        "population": population,
        "sampling_method": sampling_method,
        "sample_size": sample_size,
        "criteria": criteria
    }
```

**출력**:
- `02-research-design/sampling-plan.md` (10-15 pages)
- 모집단 정의
- 표집 방법
- 표본크기 (G*Power 계산)
- 포함/제외 기준

#### Agent 21: statistical-planner

**목적**: 통계분석 계획 수립

**프로세스**:
```python
def plan_statistical_analysis(hypotheses, variables, sample_size):
    """
    통계분석 계획
    """
    analysis_plan = []

    for h in hypotheses:
        if h["type"] == "null":
            continue  # Skip null hypotheses

        # 1. Identify appropriate test
        test = select_statistical_test(
            hypothesis=h,
            variable_types={
                "IV": variables[h["independent"]].scale,  # IV (Independent Variable, 독립변수)
                "DV": variables[h["dependent"]].scale  # DV (Dependent Variable, 종속변수)
            },
            sample_size=sample_size
        )
        # Examples: t-test, ANOVA, regression, chi-square

        # 2. Assumptions
        assumptions = list_assumptions(test)

        # 3. Effect size measure
        effect_size_measure = select_effect_size(test)
        # Examples: Cohen's d, eta-squared, R-squared

        # 4. Post-hoc tests (if applicable)
        post_hoc = select_post_hoc(test) if needs_post_hoc(test) else None

        analysis_plan.append({
            "hypothesis": h["id"],
            "statistical_test": test,
            "assumptions": assumptions,
            "effect_size": effect_size_measure,
            "post_hoc": post_hoc,
            "software": "R / Python (scipy, statsmodels)"
        })

    return analysis_plan
```

**출력**:
- `02-research-design/statistical-analysis-plan.md` (15-20 pages)
- 가설별 통계 기법
- 가정 검증 계획
- 효과크기 측정
- 분석 스크립트 (pseudo-code)

### 4.3.3 Qualitative Branch (4 Agents)

#### Agent 22: paradigm-consultant

**목적**: 인식론적/존재론적 입장 설정

**프로세스**:
- 연구 목적에 맞는 패러다임 선택 (Interpretivist, Constructivist, Critical Realist)
- 패러다임에 따른 방법론 정당화

**출력**:
- `02-research-design/research-paradigm.md` (8-12 pages)
- 철학적 입장
- 방법론적 함의

#### Agent 23: participant-selector

**목적**: 참여자 선정 전략

**프로세스**:
- 의도적 표집 (purposive sampling)
- 포화(saturation) 기준
- 표본크기 정당화

**출력**:
- `02-research-design/participant-selection.md` (10-15 pages)

#### Agent 24: qualitative-data-designer

**목적**: 질적 자료수집 설계

**프로세스**:
- 인터뷰 프로토콜
- 관찰 계획
- 문서 분석 계획

**출력**:
- `02-research-design/data-collection-protocol.md` (15-20 pages)
- 인터뷰 질문 (10-15개)
- 관찰 체크리스트
- 문서 수집 기준

#### Agent 25: qualitative-analysis-planner

**목적**: 질적 분석 전략

**프로세스**:
- 코딩 전략 (open → axial → selective)
- 분석 방법 선택 (thematic, phenomenological, grounded theory)
- 신뢰성/타당성 확보 방안

**출력**:
- `02-research-design/qualitative-analysis-plan.md` (15-20 pages)

### 4.3.4 Mixed Methods Branch (8 Agents)

**구조**:
```
Quantitative agents (4) → quant-design.md
    +
Qualitative agents (4) → qual-design.md
    ↓
mixed-methods-designer → integration-strategy.md
    ↓
integration-strategist → final-mixed-design.md
```

#### Agent 26: mixed-methods-designer

**목적**: 혼합연구 통합 설계

**프로세스**:
- 설계 유형 선택 (Convergent, Explanatory, Exploratory)
- 양적-질적 우선순위
- 통합 시점 결정

**출력**:
- `02-research-design/mixed-methods-design.md` (20-25 pages)

#### Agent 27: integration-strategist

**목적**: 자료 통합 전략

**프로세스**:
- Joint display 설계
- Merging/Connecting/Embedding 전략
- Meta-inferences 도출 계획

**출력**:
- `02-research-design/integration-strategy.md` (15-20 pages)

### 4.3.5 HITL-4: Research Design Approval

**AskUserQuestion**:
```yaml
questions:
  - question: "연구설계를 승인하시겠습니까?"
    header: "Design Approval"
    options:
      - label: "승인 (Phase 3 진행)"
        description: "설계가 충분합니다. 논문 작성을 시작합니다."
      - label: "수정 요청"
        description: "일부 수정 필요"
      - label: "재설계"
        description: "전면 재검토 필요"
```

**승인 시**: → Phase 3

---

## 4.4 Phase 3: Dissertation Writing (3 Agents + Doctoral-Writing Skill)

**목적**: 박사논문 초안 작성

**필수 요건**: `doctoral-writing` skill 강제 적용 (v2.1.0+)

### 4.4.1 Doctoral-Writing Skill Integration

**자동 로드**:
```python
# Phase 3 시작 시 자동 실행
def start_phase3():
    """
    Phase 3 entry point
    """
    # Load doctoral-writing skill
    load_skill("doctoral-writing")

    # Verify skill active
    assert is_skill_active("doctoral-writing"), "Doctoral-writing must be active"

    # Proceed with thesis architecture
    run_agent("thesis-architect")
```

**Doctoral-Writing Compliance 기준**:
```yaml
criteria:
  - academic_tone: 80+  # 학술적 어조
  - citation_accuracy: 90+  # 인용 정확성
  - argument_structure: 80+  # 논증 구조
  - evidence_support: 85+  # 증거 뒷받침
  - originality: 75+  # 독창성
  - clarity: 80+  # 명료성

threshold: 80  # Overall compliance score
```

### 4.4.2 Agent 28: thesis-architect

**목적**: 논문 구조 설계 및 아웃라인 작성

**입력**:
- Phase 1: research-synthesis.md
- Phase 2: design documents
- Research type (quant/qual/mixed)

**프로세스**:
```python
def design_thesis_structure(research_type, literature_review, design):
    """
    논문 아웃라인 설계
    """
    # 1. Determine structure (5-chapter vs. 3-article)
    structure_type = "5-chapter"  # Default for dissertation

    # 2. Chapter outline
    if structure_type == "5-chapter":
        outline = {
            "Chapter 1: Introduction": {
                "1.1": "Background and Context",
                "1.2": "Problem Statement",
                "1.3": "Research Questions/Hypotheses",
                "1.4": "Significance of the Study",
                "1.5": "Scope and Limitations",
                "1.6": "Dissertation Structure"
            },
            "Chapter 2: Literature Review": {
                "2.1": "Theoretical Foundations",
                "2.2": "Empirical Evidence",
                "2.3": "Research Gaps",
                "2.4": "Conceptual Framework",
                "2.5": "Chapter Summary"
            },
            "Chapter 3: Methodology": {
                "3.1": "Research Design",
                "3.2": "Participants/Sample",
                "3.3": "Data Collection",
                "3.4": "Data Analysis",
                "3.5": "Validity and Reliability",
                "3.6": "Ethical Considerations"
            },
            "Chapter 4: Results" if research_type == "quantitative" else "Chapter 4: Findings": {
                "4.1": "Descriptive Statistics" if research_type == "quantitative" else "Thematic Analysis",
                "4.2": "Hypothesis Testing" if research_type == "quantitative" else "Emergent Themes",
                "4.3": "Additional Findings",
                "4.4": "Chapter Summary"
            },
            "Chapter 5: Discussion and Conclusion": {
                "5.1": "Summary of Findings",
                "5.2": "Theoretical Implications",
                "5.3": "Practical Implications",
                "5.4": "Limitations",
                "5.5": "Future Research Directions",
                "5.6": "Conclusion"
            }
        }

    return outline
```

**출력**:
- `03-thesis/thesis-outline.md` (10-15 pages)
- 상세 아웃라인
- 챕터별 페이지 할당
- 예상 총 페이지 (150-250)

### 4.4.3 HITL-5: Outline Approval + Citation Style

**AskUserQuestion**:
```yaml
questions:
  - question: "논문 형식을 선택하세요"
    header: "Citation Style"
    options:
      - label: "APA (American Psychological Association, 미국심리학회) 7th"
        description: "사회과학 표준"
      - label: "MLA (Modern Language Association, 현대언어학회) 9th"
        description: "인문학 표준"
      - label: "Chicago 17th"
        description: "역사학 표준"
      - label: "IEEE (Institute of Electrical and Electronics Engineers, 국제전기전자공학회)"
        description: "공학/컴퓨터과학 표준"
```

**승인 시**: → Chapter-by-chapter writing

### 4.4.4 Agent 29: thesis-writer-rlm (Per Chapter)

**목적**: 챕터별 논문 작성 (doctoral-writing compliance 강제)

**RLM-enabled**: 전체 문헌검토 참조 (200K+ tokens)

**프로세스 (per chapter)**:
```python
def write_chapter(chapter_num, outline, all_context):
    """
    RLM + Doctoral-Writing을 사용한 챕터 작성
    """
    # 1. Load full context (RLM-enabled)
    context = {
        "literature_review": load_markdown("01-literature/research-synthesis.md"),  # 30K tokens
        "research_design": load_all_design_files(),  # 50K tokens
        "previous_chapters": load_previous_chapters(chapter_num),  # 0-100K tokens
        "outline": outline
    }
    total_context = sum(len(c) for c in context.values())

    if total_context > 100000:
        # RLM compression
        compressed_context = rlm_progressive_compression(
            content=context,
            target_size=50000,
            preserve=["key_findings", "hypotheses", "design", "previous_claims"]
        )
    else:
        compressed_context = context

    # 2. Generate chapter with doctoral-writing skill
    chapter_draft = doctoral_writing_generate(
        chapter_type=f"Chapter {chapter_num}",
        outline=outline[f"Chapter {chapter_num}"],
        context=compressed_context,
        citation_style=session.citation_style,  # From HITL-5
        word_target=calculate_word_target(chapter_num)  # Ch1: 15-20 pages, Ch2: 30-40, etc.
    )

    # 3. Doctoral-Writing Compliance Check
    compliance = assess_doctoral_writing_compliance(chapter_draft)

    if compliance.overall_score < 80:
        # Iterative improvement
        chapter_draft = improve_chapter(
            draft=chapter_draft,
            compliance_report=compliance,
            max_iterations=3
        )

    # 4. GRA validation
    gra_score = validate_gra(chapter_draft)
    if gra_score < 0.95:
        raise GRAError(f"Chapter {chapter_num} GRA compliance: {gra_score}")

    return chapter_draft, compliance
```

**출력 (per chapter)**:
- `03-thesis/chapter-{N}-{title}.md` (English)
- `03-thesis/chapter-{N}-{title}-ko.md` (Korean, auto-translated)
- Doctoral-Writing Compliance Report

**챕터별 작성 순서**:
```
Chapter 1: Introduction → HITL-6
    ↓
Chapter 2: Literature Review → HITL-6
    ↓
Chapter 3: Methodology → HITL-6
    ↓
Chapter 4: Results/Findings → HITL-6
    ↓
Chapter 5: Discussion and Conclusion → HITL-7
```

### 4.4.5 HITL-6/7: Chapter Approval

**HITL-6**: 각 챕터 완료 후 사용자 검토
- Approve → Next chapter
- Request revision → Re-write chapter
- Major changes → Back to outline

**HITL-7**: Chapter 5 완료 후 전체 논문 검토

### 4.4.6 Agent 30: thesis-reviewer

**목적**: 전체 논문 품질 검토

**프로세스**:
```python
def review_full_thesis(all_chapters):
    """
    6가지 기준으로 전체 논문 평가
    """
    review = {
        "coherence": assess_cross_chapter_coherence(all_chapters),
        "argument_flow": assess_argument_progression(all_chapters),
        "citation_consistency": check_citation_consistency(all_chapters),
        "doctoral_writing_compliance": assess_overall_compliance(all_chapters),  # Must be 80+
        "originality": assess_originality(all_chapters),
        "academic_rigor": assess_rigor(all_chapters)
    }

    # Calculate overall score
    overall = weighted_average(review, weights={
        "coherence": 0.20,
        "argument_flow": 0.15,
        "citation_consistency": 0.15,
        "doctoral_writing_compliance": 0.30,  # Highest weight
        "originality": 0.10,
        "academic_rigor": 0.10
    })

    if overall < 80:
        raise QualityError(f"Thesis quality score {overall} below 80")

    return review, overall
```

**Doctoral-Writing Compliance Threshold**: 80+

**통과 조건**: Overall score >= 80

### 4.4.7 Plagiarism Check

**자동 실행**:
```python
# After thesis-reviewer PASS
plagiarism_report = check_plagiarism_full_thesis(all_chapters)

if plagiarism_report.max_similarity > 0.15:
    raise PlagiarismError(f"Similarity {plagiarism_report.max_similarity} exceeds 15%")
```

**출력**:
- `03-thesis/plagiarism-report.md`

### 4.4.8 Auto Korean Translation

**병렬 처리**:
```python
# For each chapter
for chapter_file in all_chapter_files:
    translated = academic_translator.translate(
        source=chapter_file,
        target_lang="Korean",
        output=f"{chapter_file.replace('.md', '-ko.md')}"
    )
```

### 4.4.9 Phase 3 Output

**영어**:
- Chapter 1-5: `chapter-{N}-{title}.md`
- Full thesis: `dissertation-full-en.md`
- References: `references-en.md`

**한국어**:
- Chapter 1-5: `chapter-{N}-{title}-ko.md`
- Full thesis: `dissertation-full-ko.md`
- References: `references-ko.md`

**승인 시**: → Phase 4

---

## 4.5 Phase 4: Publication Strategy (2 Agents)

**목적**: 학술지 투고 전략 수립

### 4.5.1 Agent 31: publication-strategist

**목적**: 목표 학술지 선정 및 투고 전략

**프로세스**:
```python
def develop_publication_strategy(thesis, research_type):
    """
    학술지 선정 및 전략
    """
    # 1. Journal database search
    candidate_journals = search_journals(
        keywords=thesis.keywords,
        research_type=research_type,
        language="English",
        impact_factor_min=1.0
    )

    # 2. Journal ranking
    ranked = []
    for journal in candidate_journals:
        score = (
            journal.impact_factor * 0.3 +
            journal.relevance_to_topic * 0.4 +
            journal.acceptance_rate * 0.2 +
            journal.turnaround_time_score * 0.1
        )
        ranked.append((journal, score))

    ranked.sort(key=lambda x: x[1], reverse=True)
    top_journals = ranked[:5]

    # 3. Submission requirements
    requirements = {}
    for journal, score in top_journals:
        requirements[journal.name] = {
            "word_limit": journal.word_limit,
            "citation_style": journal.citation_style,
            "abstract_limit": journal.abstract_limit,
            "keywords_count": journal.keywords_count,
            "structure": journal.preferred_structure,
            "formatting": journal.formatting_guidelines
        }

    # 4. Submission timeline
    timeline = create_submission_timeline(top_journals)

    return top_journals, requirements, timeline
```

**출력**:
- `04-publication/journal-selection.md` (15-20 pages)
- Top 5 journals
- 저널별 요구사항
- 투고 타임라인

### 4.5.2 Agent 32: manuscript-formatter

**목적**: 선택된 저널 형식에 맞게 원고 변환

**프로세스**:
```python
def format_manuscript(thesis, journal_requirements):
    """
    저널 형식 변환
    """
    # 1. Structure adjustment
    if journal_requirements.structure == "IMRaD":  # IMRaD (Introduction, Methods, Results, and Discussion, 서론-방법-결과-논의 구조)
        # Introduction, Methods, Results, and Discussion
        manuscript = restructure_to_imrad(thesis)
    elif journal_requirements.structure == "5-chapter":
        manuscript = thesis  # No change
    else:
        manuscript = custom_restructure(thesis, journal_requirements.structure)

    # 2. Word limit adjustment
    if len(manuscript) > journal_requirements.word_limit:
        manuscript = compress_manuscript(
            manuscript,
            target_words=journal_requirements.word_limit
        )

    # 3. Citation style conversion
    manuscript = convert_citation_style(
        manuscript,
        from_style=thesis.citation_style,
        to_style=journal_requirements.citation_style
    )

    # 4. Abstract extraction/creation
    if not manuscript.abstract:
        abstract = generate_abstract(
            manuscript,
            max_words=journal_requirements.abstract_limit
        )
    else:
        abstract = manuscript.abstract

    # 5. Keywords
    keywords = extract_keywords(
        manuscript,
        count=journal_requirements.keywords_count
    )

    # 6. Formatting (margins, fonts, line spacing)
    formatted = apply_formatting(manuscript, journal_requirements.formatting)

    return formatted, abstract, keywords
```

**출력**:
- `04-publication/manuscript-formatted-{journal}.md`
- `04-publication/abstract-{journal}.md`
- `04-publication/cover-letter-{journal}.md`
- `04-publication/submission-checklist-{journal}.md`

### 4.5.3 HITL-8: Final Approval & Submission Readiness

**AskUserQuestion**:
```yaml
questions:
  - question: "투고 준비가 완료되었습니다. 세션을 종료하시겠습니까?"
    header: "Final Approval"
    options:
      - label: "승인 및 종료"
        description: "모든 작업 완료. 세션을 종료합니다."
      - label: "추가 수정"
        description: "일부 파일 수정 필요"
```

**승인 시**:
- `session.json` 업데이트: `status = "COMPLETED"`
- `todo-checklist.md`: 모든 항목 체크 완료
- Session archive

---

# 5. Agent System Deep Dive

본 섹션은 54개 에이전트의 기술적 구현, 통신 프로토콜, RLM 통합을 상세히 다룹니다.

## 5.1 Agent Architecture

### 5.1.1 Agent Lifecycle

```
1. Initialization
    ├─ Load agent spec (.md file)
    ├─ Parse frontmatter (name, description, tools, model)
    ├─ Load system prompt
    └─ Initialize context

2. Input Loading
    ├─ Collect prior agent outputs (sequential)
    ├─ Load session context (session.json)
    ├─ Load research questions
    └─ Prepare full input (may use RLM if >100K tokens)

3. Execution
    ├─ Call Claude API (model: opus for all main agents)
    ├─ Stream response
    ├─ Monitor token usage
    └─ Handle errors (retry with exponential backoff)

4. Output Processing
    ├─ Parse markdown output
    ├─ Extract GroundedClaim schema
    ├─ Validate GRA compliance
    └─ Save output file

5. Quality Validation
    ├─ GRA validation (schema, confidence, sources)
    ├─ pTCS calculation (claim-level scores)
    ├─ SRCS evaluation (if end of wave)
    └─ Gate validation (if end of wave)

6. Cleanup
    ├─ Update session.json (agent completed)
    ├─ Update todo-checklist.md
    └─ Trigger next agent (if sequential)
```

### 5.1.2 Agent Specification Format

**파일**: `.claude/agents/thesis/phase{N}/{agent-name}.md`

```yaml
---
name: literature-searcher-rlm
subagent_type: thesis-phase1-wave1-literature-searcher-rlm
model: opus
description: |
  대규모 문헌 검색 및 스크리닝 전문가.
  RLM 기술로 100-10K 논문 처리 가능.
tools:
  - WebSearch
  - WebFetch
  - Read
  - Write
  - Bash
---

# Literature Searcher (RLM-Enabled)

## Purpose
체계적 문헌검색을 수행하고 품질 기준에 따라 논문을 선별합니다.

## Input
- Research questions (3-5)
- Keywords (auto-extracted or user-provided)
- Date range (default: 10 years)
- Databases: Google Scholar, PubMed, IEEE, ACM, ArXiv

## Process
[Detailed step-by-step instructions...]

## Output Format (GroundedClaim)
```yaml
claims:
  - id: "LIT-SEARCH-{XXX}"
    text: "..."
    claim_type: FACTUAL
    sources: [...]
    confidence: 95
```

## RLM Usage
If search results > 100 papers, use RLM batch screening:
[RLM-specific instructions...]

## Quality Standards
- GRA compliance: 100%
- Minimum sources: 30 unique papers
- Quality criteria: peer-reviewed, citations > 10, recent
```

### 5.1.3 Sequential Execution Model

**원칙**: 모든 에이전트는 **순서대로** 실행되며, 이전 에이전트의 출력을 읽습니다.

**구현**:
```python
# run_wave1.py

def run_wave1(session_id):
    """
    Wave 1 순차 실행
    """
    agents = [
        "literature-searcher-rlm",
        "seminal-works-analyst",
        "trend-analyst",
        "methodology-scanner"
    ]

    outputs = {}

    for i, agent_name in enumerate(agents):
        print(f"Running {agent_name} ({i+1}/4)...")

        # Collect inputs (all previous outputs)
        input_context = {
            "session": load_json("session.json"),
            "research_questions": load_research_questions(),
            "prior_outputs": outputs  # Empty for first agent
        }

        # Execute agent
        result = execute_agent(
            agent_name=agent_name,
            input_context=input_context,
            model="opus"  # All main agents use Opus
        )

        # Validate
        validate_gra(result.output)
        calculate_ptcs(result.output)

        # Save
        output_file = f"01-literature/wave1-{agent_name}.md"
        save_markdown(result.output, output_file)

        # Add to context for next agent
        outputs[agent_name] = result.output

    # Gate 1: Cross-validation
    gate_result = cross_validate_wave1(outputs)
    if not gate_result.passed:
        raise GateError("Wave 1 cross-validation failed")

    return outputs
```

**비병렬화 이유**:
1. **컨텍스트 일관성**: 각 에이전트는 이전 분석을 읽고 확장
2. **누적 지식**: Wave 1 → Wave 5로 갈수록 깊이 증가
3. **검증 가능성**: 추론 체인을 순서대로 추적 가능

### 5.1.4 GRA Output Compliance

**강제 사항**: 모든 에이전트는 GroundedClaim schema로 출력해야 합니다.

**자동 검증**:
```python
def validate_gra(agent_output):
    """
    GRA schema 검증
    """
    # 1. Parse YAML claims section
    claims = extract_claims(agent_output)

    if not claims:
        raise GRAError("No claims found in output")

    # 2. Validate each claim
    for claim in claims:
        # Required fields
        assert "id" in claim, "Claim missing 'id'"
        assert "text" in claim, "Claim missing 'text'"
        assert "claim_type" in claim, "Claim missing 'claim_type'"
        assert "sources" in claim, "Claim missing 'sources'"
        assert "confidence" in claim, "Claim missing 'confidence'"

        # Claim type validation
        assert claim["claim_type"] in CLAIM_TYPES, f"Invalid claim_type: {claim['claim_type']}"

        # Confidence threshold
        threshold = CONFIDENCE_THRESHOLDS[claim["claim_type"]]
        if claim["confidence"] < threshold:
            raise GRAError(f"Claim {claim['id']} confidence {claim['confidence']} below threshold {threshold}")

        # Source requirement
        required_source = SOURCE_REQUIREMENTS[claim["claim_type"]]
        if required_source and not has_required_source(claim["sources"], required_source):
            raise GRAError(f"Claim {claim['id']} missing required source: {required_source}")

        # Hallucination firewall
        for pattern in HALLUCINATION_PATTERNS:
            if pattern_match(claim["text"], pattern):
                raise GRAError(f"Hallucination pattern detected in claim {claim['id']}: {pattern}")

    return {
        "total_claims": len(claims),
        "compliance": True
    }
```

**Claim Types & Thresholds**:
```python
CLAIM_TYPES = [
    "FACTUAL",      # threshold: 95, source: PRIMARY or SECONDARY
    "EMPIRICAL",    # threshold: 85, source: PRIMARY
    "THEORETICAL",  # threshold: 75, source: PRIMARY
    "METHODOLOGICAL",  # threshold: 80, source: SECONDARY+
    "INTERPRETIVE",   # threshold: 70, source: Any
    "SPECULATIVE"     # threshold: 60, source: None
]
```

### 5.1.5 Bilingual Translation Protocol

**원칙**: 영어로 작업 → 자동 한국어 번역

**프로세스**:
```python
def auto_translate_agent_output(agent_output_file):
    """
    에이전트 출력 자동 번역
    """
    # 1. Load English output
    english_content = load_markdown(agent_output_file)

    # 2. Call academic-translator agent
    korean_content = academic_translator.translate(
        source_content=english_content,
        source_lang="English",
        target_lang="Korean",
        preserve=[
            "citations",  # Keep citation format
            "doi",        # Keep DOI
            "urls",       # Keep URLs
            "code",       # Keep code blocks
            "equations"   # Keep mathematical equations
        ]
    )

    # 3. Save Korean version
    korean_file = agent_output_file.replace(".md", "-ko.md")
    save_markdown(korean_content, korean_file)

    return korean_file
```

**Translation Rules**:
```yaml
preserve:
  - citations: "Author (Year)" → "Author (Year)" (no translation)
  - technical_terms: "Transformer" → "Transformer" (keep English)
  - doi: "10.1234/..." → "10.1234/..." (no change)
  - code: "```python\n..." → "```python\n..." (no change)

translate:
  - headings: "## Literature Review" → "## 문헌 검토"
  - body_text: Full translation
  - tables: Headers translated, data preserved
  - figures: Captions translated
```

## 5.2 Agent Catalog (54 Agents by Phase)

### Phase 0: Initialization (4 agents)

| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `topic-explorer` | 연구 주제 → 연구질문 도출 | No | Opus |
| `paper-research-designer` ⭐ | Mode E: 6-stage 논문 분석 | No | Opus |
| `academic-translator` | 자동 한국어 번역 | No | Opus |
| `cross-validator-rlm` | 교차 검증 (RLM) | Yes | Opus |

### Phase 1: Literature Review (15 agents)

**Wave 1 (4)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `literature-searcher-rlm` | 100-10K 논문 검색 | Yes | Opus |
| `seminal-works-analyst` | 핵심 논문 식별 | No | Opus |
| `trend-analyst` | 시계열 트렌드 분석 | No | Opus |
| `methodology-scanner` | 방법론 패턴 분석 | No | Opus |

**Wave 2 (4)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `theoretical-framework-analyst` | 이론적 프레임워크 | No | Opus |
| `empirical-evidence-analyst` | 실증 증거 종합 | No | Opus |
| `gap-identifier` | 연구 갭 식별 | No | Opus |
| `variable-relationship-analyst-rlm` | 변수 관계 분석 | Yes | Opus |

**Wave 3 (4)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `critical-reviewer` | 비판적 검토 | No | Opus |
| `methodology-critic` | 방법론 비평 | No | Opus |
| `limitation-analyst` | 한계점 분석 | No | Opus |
| `future-direction-analyst` | 미래 방향 분석 | No | Opus |

**Wave 4 (2)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `synthesis-agent-rlm` | 문헌 종합 (150K tokens) | Yes | Opus |
| `conceptual-model-builder-rlm` | 개념 모델 구축 | Yes | Opus |

**Wave 5 (3)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `plagiarism-checker-rlm` | 표절 검사 (15 files) | Yes | Opus |
| `unified-srcs-evaluator-rlm` | SRCS 통합 평가 (100+ claims) | Yes | Opus |
| `research-synthesizer` | 최종 문헌검토 보고서 | No | Opus |

### Phase 2: Research Design (10 agents)

**Quantitative (4)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `hypothesis-developer` | 가설 개발 | No | Opus |
| `research-model-developer` | 연구 모델 개발 | No | Opus |
| `sampling-designer` | 표본 설계 | No | Opus |
| `statistical-planner` | 통계 분석 계획 | No | Opus |

**Qualitative (4)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `paradigm-consultant` | 연구 패러다임 설정 | No | Opus |
| `participant-selector` | 참여자 선정 전략 | No | Opus |
| `qualitative-data-designer` | 질적 자료수집 설계 | No | Opus |
| `qualitative-analysis-planner` | 질적 분석 전략 | No | Opus |

**Mixed Methods (2)**:
| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `mixed-methods-designer` | 혼합연구 설계 | No | Opus |
| `integration-strategist` | 자료 통합 전략 | No | Opus |

### Phase 3: Dissertation Writing (3 agents)

| Agent | Purpose | RLM | Model | Skill |
|-------|---------|-----|-------|-------|
| `thesis-architect` | 논문 구조 설계 | No | Opus | doctoral-writing |
| `thesis-writer-rlm` | 챕터별 작성 (200K context) | Yes | Opus | doctoral-writing |
| `thesis-reviewer` | 품질 검토 (80+ compliance) | No | Opus | doctoral-writing |

### Phase 4: Publication (2 agents)

| Agent | Purpose | RLM | Model |
|-------|---------|-----|-------|
| `publication-strategist` | 저널 선정 및 전략 | No | Opus |
| `manuscript-formatter` | 원고 형식 변환 | No | Opus |

## 5.3 RLM-Enabled Agents (Tier-1)

**RLM이 적용된 6개 에이전트**:

### 5.3.1 literature-searcher-rlm

**Challenge**: 100-10K 논문 처리

**RLM Solution**:
```python
def rlm_batch_screening(papers, criteria, target_size=50):
    """
    대규모 논문 배치 스크리닝
    """
    # 1. Split into batches (50 papers each)
    batches = [papers[i:i+50] for i in range(0, len(papers), 50)]

    # 2. Screen each batch (Haiku for cost)
    batch_results = []
    for batch in batches:
        result = llm_call(
            prompt=BATCH_SCREENING_TEMPLATE.format(
                papers=batch,
                criteria=criteria
            ),
            model="claude-3-5-haiku",  # Cost optimization
            max_tokens=5000
        )
        batch_results.append(result.selected_papers)

    # 3. Merge results
    all_selected = flatten(batch_results)

    # 4. Final ranking (Opus for quality)
    if len(all_selected) > target_size:
        final_selected = llm_call(
            prompt=FINAL_RANKING_TEMPLATE.format(
                papers=all_selected,
                target=target_size
            ),
            model="claude-3-5-opus",
            max_tokens=10000
        ).top_papers
    else:
        final_selected = all_selected

    return final_selected
```

**Improvement**:
- Processing capacity: 100 → 10,000 papers
- Cost: $0.50-1.50 per search (vs. $5-10 without RLM)
- Time: 10-15 min (vs. 30-40 min)

### 5.3.2 synthesis-agent-rlm

**Challenge**: Wave 1-4 통합 (150K tokens)

**RLM Solution**:
```python
def rlm_progressive_compression(wave_outputs, target_size=15000):
    """
    점진적 압축 (Zhang et al. 2025)
    """
    # Stage 1: Compress each wave
    compressed_waves = []
    for wave in wave_outputs:
        if len(wave) > 40000:
            compressed = llm_call(
                prompt=WAVE_COMPRESS_TEMPLATE.format(
                    wave_content=wave,
                    preserve=["key_findings", "gaps", "variables"]
                ),
                model="claude-3-5-haiku",
                max_tokens=10000
            ).compressed
        else:
            compressed = wave

        compressed_waves.append(compressed)

    # Total after Stage 1: ~60K tokens

    # Stage 2: Cross-wave synthesis
    if sum(len(w) for w in compressed_waves) > 50000:
        synthesized = llm_call(
            prompt=CROSS_WAVE_SYNTHESIS_TEMPLATE.format(
                waves=compressed_waves
            ),
            model="claude-3-5-haiku",
            max_tokens=15000
        ).synthesis
    else:
        synthesized = "\n\n".join(compressed_waves)

    # Total after Stage 2: ~15K tokens

    # Stage 3: Final synthesis (Opus for quality)
    final_synthesis = llm_call(
        prompt=FINAL_SYNTHESIS_TEMPLATE.format(
            compressed_input=synthesized
        ),
        model="claude-3-5-opus",
        max_tokens=20000
    ).output

    return final_synthesis  # 3-4K words
```

**Improvement**:
- Information loss: 70% → <10%
- Context handling: 150K tokens → 15K effective
- Cost: $0.80-2.00 (vs. context overflow error)

### 5.3.3 thesis-writer-rlm

**Challenge**: 전체 문헌검토 참조 (200K+ tokens)

**RLM Solution**:
```python
def write_chapter_with_rlm(chapter_num, full_context):
    """
    RLM을 사용한 챕터 작성
    """
    # 1. RLM compression of full context
    compressed_context = rlm_progressive_compression(
        content={
            "literature_review": full_context.literature,  # 30K
            "research_design": full_context.design,  # 50K
            "previous_chapters": full_context.previous  # 0-100K
        },
        target_size=50000
    )

    # 2. Chapter generation (Opus with compressed context)
    chapter = llm_call(
        prompt=CHAPTER_WRITING_TEMPLATE.format(
            chapter_num=chapter_num,
            context=compressed_context,
            outline=full_context.outline
        ),
        model="claude-3-5-opus",
        max_tokens=15000
    ).chapter_content

    return chapter
```

**Improvement**:
- Context access: 200K+ tokens (full thesis context)
- Citation accuracy: 70% → 95%+
- Coherence: 단편적 → 전체 통합

### 5.3.4 plagiarism-checker-rlm

**Challenge**: 15 파일 교차 검사 (O(n²) = 105 comparisons)

**RLM Solution**:
```python
def rlm_similarity_matrix(files):
    """
    RLM 배치 유사도 검사
    """
    # 1. Generate file embeddings (batch)
    embeddings = generate_embeddings(files, model="claude-3-5-haiku")

    # 2. Cosine similarity matrix
    similarity_matrix = compute_cosine_similarity(embeddings)

    # 3. Identify high-similarity pairs (>15%)
    high_sim_pairs = []
    for i in range(len(files)):
        for j in range(i+1, len(files)):
            if similarity_matrix[i][j] > 0.15:
                high_sim_pairs.append((i, j, similarity_matrix[i][j]))

    # 4. Detailed comparison (only for high-sim pairs)
    for i, j, sim in high_sim_pairs:
        detailed = llm_call(
            prompt=DETAILED_SIMILARITY_TEMPLATE.format(
                file1=files[i],
                file2=files[j]
            ),
            model="claude-3-5-opus",
            max_tokens=5000
        ).overlapping_text

        high_sim_pairs.append({
            "file1": files[i].name,
            "file2": files[j].name,
            "similarity": sim,
            "overlap": detailed
        })

    return high_sim_pairs
```

**Improvement**:
- Processing: 15 files × 14 / 2 = 105 comparisons
- Time: 40%→85%+ detection accuracy
- Cost: $1-2 (vs. $5-8 without RLM)

### 5.3.5 conceptual-model-builder-rlm

**Challenge**: 14 파일 통합 (Wave 1-4 전체)

**RLM Solution**: synthesis-agent-rlm과 유사한 progressive compression

**Improvement**:
- Coverage: 30% → 90% (모든 wave 반영)
- Model quality: 단편적 → 통합적

### 5.3.6 unified-srcs-evaluator-rlm

**Challenge**: 100+ claims 평가

**RLM Solution**: Batch SRCS scoring with Haiku

**Improvement**:
- Processing capacity: 50 → 200 claims
- Cost: $0.50-1.00 (vs. $3-5)

## 5.4 Agent Communication Protocol

**프로토콜**: Sequential Message Passing

```
Agent N
    ↓ (writes file)
agent-n-output.md
    ↓ (reads file)
Agent N+1
```

**메시지 형식**:
```yaml
# agent-n-output.md

---
agent: agent-n
phase: 1
wave: 2
timestamp: 2026-01-29T10:30:00Z
status: COMPLETED
---

# Agent N Output

## Summary
[Executive summary of findings]

## Detailed Analysis
[Full analysis...]

## Claims (GroundedClaim Schema)
```yaml
claims:
  - id: "AGENT-N-001"
    text: "..."
    claim_type: EMPIRICAL
    sources: [...]
    confidence: 85
```

## Next Agent Instructions
Agent N+1 should:
1. Read this analysis
2. Build upon findings X, Y, Z
3. Address question Q
```

**컨텍스트 전달**:
```python
def prepare_context_for_agent(agent_name, phase, wave):
    """
    다음 에이전트를 위한 컨텍스트 준비
    """
    context = {
        "session": load_json("session.json"),
        "research_questions": load_research_questions(),
        "phase_outputs": {},
        "wave_outputs": {}
    }

    # Load all outputs from current phase
    if phase >= 1:
        context["phase_outputs"]["phase1"] = load_all_files("01-literature/")
    if phase >= 2:
        context["phase_outputs"]["phase2"] = load_all_files("02-research-design/")
    if phase >= 3:
        context["phase_outputs"]["phase3"] = load_all_files("03-thesis/")

    # Load all outputs from current wave
    if wave:
        wave_files = glob(f"01-literature/wave{wave}-*.md")
        context["wave_outputs"][f"wave{wave}"] = load_files(wave_files)

    # Load previous wave outputs (cumulative)
    for w in range(1, wave):
        prev_wave_files = glob(f"01-literature/wave{w}-*.md")
        context["wave_outputs"][f"wave{w}"] = load_files(prev_wave_files)

    return context
```

---

# 6. AI Technologies Integration

본 섹션은 시스템에서 사용하는 AI/LLM (Large Language Model, 대규모 언어 모델) 기술, Claude 특화 기능, 프롬프트 엔지니어링 전략을 다룹니다.

## 6.1 Claude API (Application Programming Interface, 응용 프로그래밍 인터페이스) 활용

### 6.1.1 Model Selection Strategy

**Opus for Main Agents, Haiku for Sub-calls**

```python
MODEL_STRATEGY = {
    "main_agents": "claude-3-5-opus",  # 108 agents (dual structure)
    "rlm_sub_calls": "claude-3-5-haiku",  # RLM compression
    "translation": "claude-3-5-opus",  # Quality critical
    "validation": "claude-3-5-opus"  # Quality critical
}
```

**이유**:
- **Opus**: 최고 품질, 박사급 연구에 필수
- **Haiku**: RLM sub-calls에서 비용 최적화 (Opus 대비 1/10 비용)

**비용 구조** (2026-01 기준):
```
Opus:
  Input: $15/1M tokens
  Output: $75/1M tokens

Haiku:
  Input: $0.80/1M tokens
  Output: $4/1M tokens

Phase 1 예상 비용 (15 agents):
  Main calls (Opus): $12-18
  RLM sub-calls (Haiku): $0.50-1.50
  Total: $12.50-19.50
```

### 6.1.2 Context Window Management

**Claude 3.5 Sonnet/Opus: 200K token context window**

**전략**:
1. **Direct Use** (<100K tokens): 직접 입력
2. **RLM Compression** (100K-500K): Progressive compression
3. **External Memory** (persistent): session.json, todo-checklist.md, research-synthesis.md

**예시**:
```python
def handle_large_context(content, target="claude-3-5-opus"):
    """
    컨텍스트 크기에 따른 처리 전략
    """
    token_count = estimate_tokens(content)

    if token_count < 100000:
        # Strategy 1: Direct
        return call_claude_api(
            prompt=content,
            model=target
        )

    elif token_count < 500000:
        # Strategy 2: RLM Compression
        compressed = rlm_progressive_compression(
            content=content,
            target_size=50000
        )
        return call_claude_api(
            prompt=compressed,
            model=target
        )

    else:
        # Strategy 3: External Memory + Chunking
        summary = create_external_summary(content)
        save_to_synthesis_file(summary)
        return call_claude_api(
            prompt=f"Context summary: {summary}\n\nTask: ...",
            model=target
        )
```

### 6.1.3 Streaming & Token Monitoring

**실시간 스트리밍**:
```python
def stream_agent_execution(agent_name, prompt):
    """
    Agent 실행 중 실시간 스트리밍
    """
    with anthropic.Anthropic() as client:
        stream = client.messages.stream(
            model="claude-3-5-opus",
            max_tokens=15000,
            messages=[{"role": "user", "content": prompt}]
        )

        full_response = ""
        with stream as s:
            for text in s.text_stream:
                print(text, end="", flush=True)  # Real-time output
                full_response += text

        # Metadata
        metadata = {
            "input_tokens": s.get_final_message().usage.input_tokens,
            "output_tokens": s.get_final_message().usage.output_tokens,
            "cost": calculate_cost(
                s.get_final_message().usage.input_tokens,
                s.get_final_message().usage.output_tokens,
                model="opus"
            )
        }

    return full_response, metadata
```

**비용 모니터링**:
```python
def track_session_cost(session_id):
    """
    세션별 비용 추적
    """
    log = load_json(f"{session_id}/cost-log.json")

    total_cost = sum(entry["cost"] for entry in log)
    total_input_tokens = sum(entry["input_tokens"] for entry in log)
    total_output_tokens = sum(entry["output_tokens"] for entry in log)

    return {
        "total_cost": total_cost,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "average_cost_per_agent": total_cost / len(log)
    }
```

## 6.2 Prompt Engineering Strategies

### 6.2.1 System Prompts Architecture

**3-Layer Prompt Structure**:
```
Layer 1: Universal System Prompt (모든 agents)
    ├─ GRA compliance instruction
    ├─ Hallucination prevention rules
    ├─ GroundedClaim schema template
    └─ Output format guidelines

Layer 2: Phase-Specific Prompt (per phase)
    ├─ Phase objectives
    ├─ Quality standards
    └─ HITL checkpoint awareness

Layer 3: Agent-Specific Prompt (per agent)
    ├─ Agent purpose
    ├─ Input description
    ├─ Process steps
    └─ Expected output
```

**구현**:
```python
def construct_full_prompt(agent_name, context):
    """
    3-layer prompt 조합
    """
    # Layer 1: Universal
    universal = load_template("prompts/universal-system-prompt.md")

    # Layer 2: Phase-specific
    phase = identify_phase(agent_name)
    phase_prompt = load_template(f"prompts/phase-{phase}-prompt.md")

    # Layer 3: Agent-specific
    agent_spec = load_agent_spec(agent_name)

    # Combine
    full_prompt = f"""
{universal}

---

{phase_prompt}

---

{agent_spec.prompt}

---

## Input Context

{format_context(context)}

---

## Your Task

{agent_spec.task_description}
"""

    return full_prompt
```

### 6.2.2 Few-Shot Examples

**GRA Compliance Training**:
```yaml
# universal-system-prompt.md

## GroundedClaim Examples

### Example 1: GOOD (FACTUAL claim)
```yaml
claims:
  - id: "EXAMPLE-001"
    text: "Vaswani et al. (2017)의 Transformer 아키텍처는 기계번역 BLEU (Bilingual Evaluation Understudy, 이중언어 평가 대용) 점수를 28.4로 달성했다."
    claim_type: FACTUAL
    sources:
      - type: PRIMARY
        reference: "Vaswani, A., et al. (2017)"
        doi: "10.48550/arXiv.1706.03762"
        verified: true
    confidence: 95
```

### Example 2: BAD (Hallucination)
```yaml
claims:
  - id: "BAD-001"
    text: "모든 연구가 Transformer가 RNN보다 절대적으로 우수하다는 데 동의한다."  # ❌ Hallucination
```

**Correction**:
```yaml
claims:
  - id: "CORRECTED-001"
    text: "다수의 연구(n=23)에서 Transformer가 특정 task(기계번역, 문서 분류)에서 RNN 대비 우수한 성능을 보고했다."
    claim_type: EMPIRICAL
    sources:
      - type: SECONDARY
        reference: "Literature review (n=23 studies)"
        verified: true
    confidence: 85
    uncertainty: "Task와 dataset에 따라 성능 차이가 존재할 수 있음"
```

### 6.2.3 Prompt Compression (Crystalize)

**문제**: 긴 시스템 프롬프트 (5-10K tokens)

**해결**: High-resolution tokenization (개념 → 토큰)

**예시**:
```
Before (verbose):
"You must always include citations in the format Author (Year).
Never make claims without supporting evidence.
All empirical claims must reference primary sources.
Theoretical claims should reference seminal works..."
(200 tokens)

After (crystalized):
"GRA: cite(author_year), evidence(primary_for_empirical, seminal_for_theory), no_unsupported_claims"
(30 tokens)

Compression: 200 → 30 tokens (85% reduction)
```

**구현**:
```python
def crystalize_prompt(verbose_prompt):
    """
    프롬프트 압축
    """
    # Pattern replacement
    replacements = {
        "You must always include citations": "cite:required",
        "Never make claims without supporting evidence": "evidence:mandatory",
        "in the format Author (Year)": "fmt:author_year",
        # ... (50+ patterns)
    }

    compressed = verbose_prompt
    for old, new in replacements.items():
        compressed = compressed.replace(old, new)

    # Verify quality (test with sample)
    test_output = test_prompt(compressed)
    if quality_score(test_output) < 0.9:
        return verbose_prompt  # Fallback to verbose

    return compressed
```

## 6.3 Tool Use & Function Calling

### 6.3.1 Claude Tools Integration

**Available Tools** (for agents):
```yaml
tools:
  - WebSearch: 학술 데이터베이스 검색
  - WebFetch: URL에서 논문 다운로드
  - Read: 파일 읽기
  - Write: 파일 작성
  - Bash: Git, 스크립트 실행
```

**Tool Call 예시**:
```python
# literature-searcher-rlm agent

def search_literature(keywords):
    """
    Multi-database search using WebSearch tool
    """
    databases = [
        "https://scholar.google.com",
        "https://pubmed.ncbi.nlm.nih.gov",
        "https://ieeexplore.ieee.org"
    ]

    all_results = []
    for db in databases:
        result = tool_call(
            tool="WebSearch",
            params={
                "query": f"{keywords} site:{db}",
                "max_results": 100
            }
        )
        all_results.extend(result.papers)

    return all_results
```

### 6.3.2 MCP (Model Context Protocol, 모델 컨텍스트 프로토콜) Integration

**Context7 Integration** (최신 문서):
```python
# Using mcp__plugin_context7

def query_latest_docs(library_name):
    """
    Context7를 통한 최신 문서 조회
    """
    # 1. Resolve library ID
    library_id = tool_call(
        tool="mcp__plugin_context7_context7__resolve-library-id",
        params={
            "libraryName": library_name,
            "query": "latest documentation"
        }
    )

    # 2. Query docs
    docs = tool_call(
        tool="mcp__plugin_context7_context7__query-docs",
        params={
            "libraryId": library_id.id,
            "query": "API reference and examples"
        }
    )

    return docs
```

## 6.4 RLM (Recursive Language Models)

**핵심 기술**: Zhang et al. 2025 - "Recursive Language Models for Infinite Context"

### 6.4.1 RLM Principles

**개념**:
```
Input (150K tokens)
    ↓
Chunk 1 (50K) → Summarize (10K)
Chunk 2 (50K) → Summarize (10K)  } Haiku (cost optimization)
Chunk 3 (50K) → Summarize (10K)
    ↓
Merged Summaries (30K)
    ↓
Final Synthesis (15K)  } Opus (quality)
    ↓
Output (3-4K words, information loss <10%)
```

**알고리즘**:
```python
def rlm_recursive_summarization(text, target_length, depth=0, max_depth=3):
    """
    재귀적 요약 (Zhang et al. 2025)
    """
    current_length = len(text.split())

    # Base case: 목표 길이 도달
    if current_length <= target_length:
        return text

    # Recursion limit
    if depth >= max_depth:
        # Force compression with higher compression ratio
        return force_compress(text, target_length)

    # Recursive case: Split and summarize
    chunks = semantic_split(text, chunk_size=current_length // 3)

    summaries = []
    for chunk in chunks:
        # Use Haiku for sub-calls (cost optimization)
        summary = llm_call(
            prompt=f"Summarize preserving key information:\n\n{chunk}",
            model="claude-3-5-haiku",
            max_tokens=target_length // len(chunks)
        ).summary
        summaries.append(summary)

    # Merge summaries
    merged = "\n\n---\n\n".join(summaries)

    # Recursive call
    if len(merged.split()) > target_length:
        return rlm_recursive_summarization(
            merged,
            target_length,
            depth=depth+1,
            max_depth=max_depth
        )
    else:
        return merged
```

### 6.4.2 Information Preservation Techniques

**Selective Preservation**:
```python
def rlm_with_preservation(text, preserve_types):
    """
    특정 정보 유형 보존
    """
    # Extract elements to preserve
    preserved = {
        "claims": extract_claims(text) if "claims" in preserve_types else [],
        "citations": extract_citations(text) if "citations" in preserve_types else [],
        "variables": extract_variables(text) if "variables" in preserve_types else [],
        "hypotheses": extract_hypotheses(text) if "hypotheses" in preserve_types else []
    }

    # Summarize remaining text
    non_preserved_text = remove_preserved_elements(text, preserved)
    summarized = llm_call(
        prompt=f"Summarize:\n\n{non_preserved_text}",
        model="claude-3-5-haiku",
        max_tokens=5000
    ).summary

    # Reconstruct with preserved elements
    reconstructed = integrate_preserved_elements(summarized, preserved)

    return reconstructed
```

**효과**:
```
Without preservation:
  Information loss: 70-80%
  Citation accuracy: 40-50%

With preservation:
  Information loss: <10%
  Citation accuracy: 95%+
```

## 6.5 Claude Skills Framework

### 6.5.1 Custom Skills

**Doctoral-Writing Skill** (mandatory for Phase 3):

```yaml
# .claude/skills/doctoral-writing/SKILL.md
---
name: doctoral-writing
description: |
  Enforces doctoral-level writing standards:
  - Academic tone
  - Rigorous argumentation
  - Proper citations
  - Evidence-based claims
---

# Doctoral Writing Skill

## Compliance Criteria
- Academic tone: 80+
- Citation accuracy: 90+
- Argument structure: 80+
- Evidence support: 85+
- Originality: 75+
- Clarity: 80+

## Output Requirements
- Every claim supported by evidence
- Citations in specified style (APA/MLA/Chicago/IEEE)
- No colloquialisms or informal language
- Logical flow between paragraphs
- Transition sentences between sections
```

**Enforcement**:
```python
def enforce_doctoral_writing(chapter_draft):
    """
    Doctoral-writing compliance check
    """
    scores = {
        "academic_tone": assess_academic_tone(chapter_draft),
        "citation_accuracy": check_citations(chapter_draft),
        "argument_structure": analyze_argument_flow(chapter_draft),
        "evidence_support": verify_evidence(chapter_draft),
        "originality": check_originality(chapter_draft),
        "clarity": assess_clarity(chapter_draft)
    }

    overall = sum(scores.values()) / len(scores)

    if overall < 80:
        # Iterative improvement
        improved = improve_with_feedback(chapter_draft, scores)
        return improved

    return chapter_draft
```

### 6.5.2 Hot-Reload

**자동 감지**:
```python
# Claude Code hot-reload mechanism

def watch_skill_files():
    """
    .claude/skills/ 디렉토리 감시
    """
    watcher = FileSystemWatcher(".claude/skills/")

    @watcher.on_modified
    def reload_skill(filepath):
        skill_name = extract_skill_name(filepath)
        print(f"Reloading skill: {skill_name}")

        # Reload skill definition
        skill = load_skill_from_file(filepath)

        # Update active skills
        ACTIVE_SKILLS[skill_name] = skill

        print(f"✓ {skill_name} reloaded")

    watcher.start()
```

**이점**:
- Git pull → 자동 업데이트
- 설정 변경 불필요
- 즉시 적용

## 6.6 Prompt Distillation & Optimization

### 6.6.1 Distill-Partner System

**2-Model Collaboration**:
```
Opus (Teacher): 상세한 분석 + 설명
    ↓
Haiku (Student): 압축된 버전 생성
    ↓
Validation: 품질 검증 (Opus)
    ↓
Deployment: Haiku 버전 사용 (비용 절감)
```

**구현**:
```python
def distill_agent_prompt(agent_name):
    """
    Prompt distillation with 2-model collaboration
    """
    # 1. Opus: Generate detailed analysis
    detailed = llm_call(
        prompt=f"Perform detailed {agent_name} analysis with explanations",
        model="claude-3-5-opus",
        max_tokens=15000
    ).analysis

    # 2. Haiku: Compress to essential
    compressed = llm_call(
        prompt=f"Extract essential points from:\n\n{detailed}",
        model="claude-3-5-haiku",
        max_tokens=5000
    ).compressed

    # 3. Validation: Compare outputs
    opus_output = test_with_prompt(detailed_prompt, test_cases)
    haiku_output = test_with_prompt(compressed_prompt, test_cases)

    quality_retention = compare_outputs(opus_output, haiku_output)

    if quality_retention > 0.90:
        # Haiku version acceptable
        return compressed_prompt, "haiku"
    else:
        # Use Opus version
        return detailed_prompt, "opus"
```

### 6.6.2 Adaptive Prompting

**컨텍스트 기반 프롬프트 조정**:
```python
def adaptive_prompt(agent_name, context):
    """
    컨텍스트에 따라 프롬프트 조정
    """
    base_prompt = load_agent_prompt(agent_name)

    # Adjust based on context complexity
    complexity = assess_context_complexity(context)

    if complexity == "HIGH":
        # Add scaffolding
        adjusted = add_scaffolding(base_prompt, context)
    elif complexity == "LOW":
        # Simplify prompt
        adjusted = simplify_prompt(base_prompt)
    else:
        adjusted = base_prompt

    # Adjust based on previous errors
    error_history = load_error_history(agent_name)
    if error_history:
        adjusted = add_error_prevention(adjusted, error_history)

    return adjusted
```

---

# 7. Core Technologies

본 섹션은 GRA, pTCS, SRCS, 외부 메모리 등 핵심 품질 보증 기술을 다룹니다.

## 7.1 GRA (Grounded Research Architecture)

### 7.1.1 GroundedClaim Schema (Full Specification)

```yaml
claims:
  - id: string (required)
    # Format: "{AGENT_PREFIX}-{###}"
    # Example: "LIT-001", "HYPO-003", "RESULT-012"

    text: string (required)
    # The actual claim statement
    # Must be specific, falsifiable, and evidence-based

    claim_type: enum (required)
    # FACTUAL | EMPIRICAL | THEORETICAL | METHODOLOGICAL | INTERPRETIVE | SPECULATIVE

    sources: array (required for most types)
      - type: enum (PRIMARY | SECONDARY | TERTIARY)
        reference: string  # Author (Year) format
        doi: string (optional)
        url: string (optional)
        verified: boolean
        page: string (optional)  # For books/reports
        accessed: string (optional)  # For online sources

    confidence: integer (required, 0-100)
    # Based on claim_type thresholds

    uncertainty: string (optional but recommended)
    # Explicit statement of what is uncertain

    related_claims: array (optional)
      # Links to other claim IDs

    data: object (optional)
      # Supporting data (statistics, effect sizes, etc.)
```

**Validation Function**:
```python
def validate_grounded_claim(claim):
    """
    Full GRA validation
    """
    errors = []

    # 1. Required fields
    required = ["id", "text", "claim_type", "sources", "confidence"]
    for field in required:
        if field not in claim:
            errors.append(f"Missing required field: {field}")

    # 2. Claim type validity
    if claim["claim_type"] not in CLAIM_TYPES:
        errors.append(f"Invalid claim_type: {claim['claim_type']}")

    # 3. Confidence threshold
    threshold = CONFIDENCE_THRESHOLDS[claim["claim_type"]]
    if claim["confidence"] < threshold:
        errors.append(
            f"Confidence {claim['confidence']} below threshold {threshold} "
            f"for {claim['claim_type']}"
        )

    # 4. Source requirements
    required_source = SOURCE_REQUIREMENTS[claim["claim_type"]]
    if required_source:
        has_required = any(
            s["type"] == required_source for s in claim["sources"]
        )
        if not has_required:
            errors.append(
                f"Missing required source type: {required_source}"
            )

    # 5. Hallucination patterns
    for pattern in HALLUCINATION_PATTERNS:
        if re.search(pattern, claim["text"], re.IGNORECASE):
            errors.append(
                f"Hallucination pattern detected: {pattern}"
            )

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

### 7.1.2 Confidence Thresholds by Claim Type

```python
CONFIDENCE_THRESHOLDS = {
    "FACTUAL": 95,
    # Example: "Python 3.11 was released in 2022"
    # Must have PRIMARY or SECONDARY source

    "EMPIRICAL": 85,
    # Example: "Experiment showed 23% improvement (p<.05)"
    # Must have PRIMARY source (original research)

    "THEORETICAL": 75,
    # Example: "Based on X theory, Y should occur"
    # Must have PRIMARY source (seminal work)

    "METHODOLOGICAL": 80,
    # Example: "ANOVA is appropriate for comparing 3+ groups"
    # Must have SECONDARY+ source (textbook, review)

    "INTERPRETIVE": 70,
    # Example: "This suggests that Z may influence W"
    # Any source acceptable, uncertainty required

    "SPECULATIVE": 60
    # Example: "Future research could explore Q"
    # No source required, uncertainty required
}
```

### 7.1.3 Hallucination Firewall (4 Levels)

```python
HALLUCINATION_PATTERNS = {
    "BLOCK": [
        r"모든\s+(연구|논문|학자)",  # "모든 연구"
        r"100%",
        r"절대(적으로|로)",
        r"완벽(하게|히)",
        r"의심\s?여지\s?없이",
        r"all\s+research",
        r"always",
        r"never\s+(fails|works)"
    ],

    "REQUIRE_SOURCE": [
        r"p\s?[<>=]\s?\.?\d+",  # p-values
        r"[dr]\s?=\s?[\d.]+",    # effect sizes
        r"\d+%\s+(increase|decrease|improvement)",
        r"significant(ly)?\s+(increase|decrease)"
    ],

    "SOFTEN": [
        r"확실(히|하게)",
        r"명백(히|하게)",
        r"분명(히|하게)",
        r"obviously",
        r"clearly",
        r"undoubtedly"
    ],

    "VERIFY": [
        r"일반적으로",
        r"대부분의\s+(연구|학자)",
        r"많은\s+연구",
        r"generally",
        r"most\s+(research|studies)",
        r"commonly"
    ]
}

def apply_hallucination_firewall(claim_text):
    """
    Hallucination detection and action
    """
    for level, patterns in HALLUCINATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, claim_text, re.IGNORECASE):
                if level == "BLOCK":
                    raise HallucinationError(
                        f"BLOCKED: Pattern '{pattern}' detected. "
                        f"Rewrite without absolute language."
                    )
                elif level == "REQUIRE_SOURCE":
                    # Check if source exists
                    if not has_citation_nearby(claim_text, pattern):
                        raise HallucinationError(
                            f"Source required for: {pattern}"
                        )
                elif level == "SOFTEN":
                    # Add warning tag
                    claim_text = add_uncertainty_tag(claim_text, pattern)
                elif level == "VERIFY":
                    # Add verification tag
                    claim_text = add_verification_tag(claim_text)

    return claim_text
```

## 7.2 pTCS (predicted Thesis Confidence Score)

### 7.2.1 4-Level Scoring Model

**영감**: AlphaFold pIDDT (predicted local distance difference test)

**구조**:
```
Level 1: Claim-level pTCS
    ↓ Average
Level 2: Agent-level pTCS
    ↓ Average
Level 3: Phase-level pTCS
    ↓ Weighted Average
Level 4: Workflow-level pTCS
```

**계산**:
```python
def calculate_ptcs_full(session_id):
    """
    전체 워크플로우 pTCS 계산
    """
    # Level 1: Claim-level
    all_claims = collect_all_claims(session_id)
    claim_scores = [score_claim_ptcs(c) for c in all_claims]

    # Level 2: Agent-level (4-component formula, v4.0.1)
    agents = group_claims_by_agent(all_claims)
    agent_scores = {}
    for agent_name, claims in agents.items():
        claim_avg = mean([c.ptcs for c in claims])
        coverage = calculate_coverage(required_sections, output_file, claims)  # 0-1
        consistency = calculate_cross_reference_consistency(claims)  # 0-1
        firewall = hallucination_firewall_score(claims)  # 0-10
        agent_scores[agent_name] = (
            claim_avg / 2       # /50 — claim quality
            + coverage * 25     # /25 — section coverage
            + consistency * 15  # /15 — cross-reference consistency
            + firewall          # /10 — hallucination prevention
        )  # Total: /100

    # Level 3: Phase-level
    phases = group_agents_by_phase(agent_scores)
    phase_scores = {}
    for phase_num, agents in phases.items():
        phase_scores[phase_num] = mean(agents.values())

    # Level 4: Workflow-level (weighted)
    weights = {
        0: 0.05,  # Initialization
        1: 0.40,  # Literature (most important)
        2: 0.25,  # Design
        3: 0.25,  # Writing
        4: 0.05   # Publication
    }

    workflow_ptcs = sum(
        phase_scores[p] * weights[p] for p in phase_scores
    )

    return {
        "claim_level": {
            "scores": claim_scores,
            "mean": mean(claim_scores),
            "below_threshold": sum(1 for s in claim_scores if s < 60)
        },
        "agent_level": agent_scores,
        "phase_level": phase_scores,
        "workflow_level": workflow_ptcs
    }
```

**Claim-level pTCS**:
```python
def score_claim_ptcs(claim):
    """
    개별 claim pTCS 점수
    """
    # Base score from confidence
    base = claim["confidence"]

    # Adjust for source quality
    source_quality = assess_source_quality(claim["sources"])
    source_adjustment = source_quality * 10  # +10 for excellent sources

    # Adjust for uncertainty acknowledgment
    if "uncertainty" in claim and claim["uncertainty"]:
        uncertainty_adjustment = 5  # +5 for acknowledging uncertainty
    else:
        uncertainty_adjustment = 0

    # Adjust for claim type
    type_factor = TYPE_FACTORS[claim["claim_type"]]
    # EMPIRICAL: 1.0, THEORETICAL: 0.9, INTERPRETIVE: 0.8, etc.

    ptcs = (base + source_adjustment + uncertainty_adjustment) * type_factor

    # Cap at 100
    return min(ptcs, 100)
```

### 7.2.2 Threshold Enforcement

```python
PTCS_THRESHOLDS = {
    "claim": 60,   # Individual claim minimum
    "agent": 70,   # Agent average minimum
    "phase": 75,   # Phase average minimum
    "workflow": 75  # Overall minimum
}

def enforce_ptcs_threshold(ptcs_scores, level):
    """
    pTCS threshold enforcement with retry
    """
    threshold = PTCS_THRESHOLDS[level]
    score = ptcs_scores[f"{level}_level"]["mean"]

    if score < threshold:
        # Identify low-scoring claims/agents
        if level == "claim":
            low_scorers = [
                c for c in ptcs_scores["claim_level"]["scores"]
                if c < threshold
            ]
        elif level == "agent":
            low_scorers = [
                agent for agent, score in ptcs_scores["agent_level"].items()
                if score < threshold
            ]

        # Auto-retry
        print(f"❌ {level}-level pTCS {score} below threshold {threshold}")
        print(f"Retrying {len(low_scorers)} low-scoring items...")

        for item in low_scorers:
            retry_with_improvement(item)

        # Recalculate
        new_scores = calculate_ptcs_full(session_id)
        return enforce_ptcs_threshold(new_scores, level)

    else:
        print(f"✓ {level}-level pTCS {score} meets threshold {threshold}")
        return True
```

## 7.3 SRCS (Source-Reliability-Confidence-Scope)

### 7.3.1 4-Axis Evaluation

```python
def evaluate_srcs(claim):
    """
    SRCS 4-axis 평가
    """
    # Axis 1: Citation Score (35%)
    CS = citation_score(claim)
    # Factors:
    #   - Source authority (journal impact factor, citations)
    #   - Source recency (prefer recent <5 years)
    #   - Source relevance (directly addresses claim)

    # Axis 2: Grounding Score (35%)
    GS = grounding_score(claim)
    # Factors:
    #   - Evidence sufficiency (enough support?)
    #   - Logical connection (evidence → claim)
    #   - Alternative explanations (considered?)

    # Axis 3: Uncertainty Score (10%)
    US = uncertainty_score(claim)
    # Factors:
    #   - Uncertainty acknowledged?
    #   - Limitations stated?
    #   - Confidence appropriate?

    # Axis 4: Verifiability Score (20%)
    VS = verifiability_score(claim)
    # Factors:
    #   - Verifiable (can be checked?)
    #   - Reproducible (can be replicated?)
    #   - Transparent (method clear?)

    # Weighted total
    total = 0.35*CS + 0.35*GS + 0.10*US + 0.20*VS

    return {
        "CS": CS,
        "GS": GS,
        "US": US,
        "VS": VS,
        "total": total,
        "grade": assign_grade(total)
    }

def assign_grade(srcs_score):
    """
    SRCS grade assignment
    """
    if srcs_score >= 90:
        return "A"  # Excellent - Immediate proceed
    elif srcs_score >= 80:
        return "B"  # Good - Minor revision
    elif srcs_score >= 75:
        return "C"  # Acceptable - Conditional proceed
    elif srcs_score >= 60:
        return "D"  # Poor - Significant revision
    else:
        return "F"  # Fail - Complete rework
```

### 7.3.2 Citation Score (CS) Calculation

```python
def citation_score(claim):
    """
    CS: Citation quality 평가 (0-100)
    """
    scores = []

    for source in claim["sources"]:
        # Authority (40%)
        if source["type"] == "PRIMARY":
            if has_high_impact_factor(source):
                authority = 100
            elif has_medium_impact_factor(source):
                authority = 75
            else:
                authority = 50
        elif source["type"] == "SECONDARY":
            authority = 60
        else:  # TERTIARY
            authority = 30

        # Recency (30%)
        pub_year = extract_year(source["reference"])
        age = current_year() - pub_year
        if age <= 3:
            recency = 100
        elif age <= 5:
            recency = 80
        elif age <= 10:
            recency = 60
        else:
            recency = 40

        # Relevance (30%)
        relevance = assess_relevance(source, claim["text"])
        # Using semantic similarity

        source_score = 0.4*authority + 0.3*recency + 0.3*relevance
        scores.append(source_score)

    # Average across sources
    return mean(scores) if scores else 0
```

### 7.3.3 Grounding Score (GS) Calculation

```python
def grounding_score(claim):
    """
    GS: Evidence grounding 평가 (0-100)
    """
    # Evidence sufficiency (50%)
    if len(claim["sources"]) >= 3:
        sufficiency = 100
    elif len(claim["sources"]) == 2:
        sufficiency = 75
    elif len(claim["sources"]) == 1:
        sufficiency = 50
    else:
        sufficiency = 0

    # Logical connection (30%)
    connection = assess_logical_connection(
        evidence=claim["sources"],
        claim=claim["text"]
    )
    # LLM-based assessment

    # Alternative explanations (20%)
    alternatives = check_alternative_explanations(claim)
    # Does claim acknowledge other possible explanations?

    gs = 0.5*sufficiency + 0.3*connection + 0.2*alternatives

    return gs
```

## 7.4 Dual Confidence System

### 7.4.1 Integration Formula

```
Final Confidence = 0.6 × pTCS + 0.4 × SRCS

Where:
  pTCS: predicted (before/during writing)
  SRCS: measured (after writing)

Weights rationale:
  - pTCS (60%): Proactive quality prediction
  - SRCS (40%): Retrospective quality measurement
```

**구현**:
```python
def calculate_dual_confidence(claim):
    """
    Dual confidence score
    """
    # 1. pTCS (prediction)
    ptcs = score_claim_ptcs(claim)

    # 2. SRCS (measurement)
    srcs = evaluate_srcs(claim)["total"]

    # 3. Dual confidence
    dual = 0.6 * ptcs + 0.4 * srcs

    # 4. Grade
    grade = assign_grade(dual)

    return {
        "ptcs": ptcs,
        "srcs": srcs,
        "dual_confidence": dual,
        "grade": grade,
        "action": determine_action(grade)
    }

def determine_action(grade):
    """
    Grade-based action
    """
    actions = {
        "A": "Immediate proceed to next phase",
        "B": "Minor revision, then proceed",
        "C": "Conditional proceed with review flag",
        "D": "Significant revision required",
        "F": "Complete rework mandatory"
    }
    return actions[grade]
```

---

# 8. Command System

본 섹션은 44개 워크플로우 명령어의 구조, 사용법, Context Forking 전략을 다룹니다.

## 8.1 Command Categories

### 8.1.1 Initialization & Control (6 commands)

| Command | Purpose | Context | HITL |
|---------|---------|---------|------|
| `/thesis:init` | 세션 초기화 | Main | No |
| `/thesis:quick-start` | 자연어 트리거 핸들러 | Main | Yes (mode selection) |
| `/thesis:start` | 워크플로우 시작 | Main | Yes (HITL-1) |
| `/thesis:start-paper-upload` | Mode E 시작 | **Fork** | Yes |
| `/thesis:start-proposal-upload` | ⭐ Mode F 시작 (v4) | **Fork** | Yes |
| `/thesis:resume` | 컨텍스트 복구 | Main | No |

### 8.1.2 Phase Execution (5 commands)

| Command | Purpose | Context |
|---------|---------|---------|
| `/thesis:run-literature-review` | Phase 1 실행 | **Fork** |
| `/thesis:run-research-design` | Phase 2 실행 | **Fork** |
| `/thesis:run-writing` | Phase 3 실행 (doctoral-writing 강제) | **Fork** |
| `/thesis:run-writing-validated` | Phase 3 검증 실행 | **Fork** |
| `/thesis:run-publication` | Phase 4 실행 | **Fork** |

### 8.1.3 HITL Checkpoints (9 commands)

| Command | HITL Point | Decision |
|---------|-----------|----------|
| `/thesis:approve-topic` | HITL-1 | 주제/RQ 확정 |
| `/thesis:review-literature` | HITL-2 | 문헌검토 승인 |
| `/thesis:set-research-type` | HITL-3 | 연구 유형 선택 |
| `/thesis:approve-design` | HITL-4 | 설계 승인 |
| `/thesis:approve-outline` | HITL-5 | 아웃라인/인용 스타일 |
| `/thesis:review-chapter` | HITL-6/7 | 챕터 승인 |
| `/thesis:review-proposal` | ⭐ (v4) | 연구 제안 검토 |
| `/thesis:review-extracted-plan` | ⭐ Mode F (v4) | 추출 계획 확인 |
| `/thesis:finalize` | HITL-8 | 최종 승인 |

### 8.1.4 Mode E/F 6-Stage (6 commands) ⭐ v4

| Command | Stage | Purpose |
|---------|-------|---------|
| `/thesis:analyze-paper` | Stage 1 | 선행연구 논문 심층 분석 |
| `/thesis:identify-gaps` | Stage 2 | 연구 갭 식별 |
| `/thesis:generate-hypotheses` | Stage 3 | 가설 생성 및 평가 |
| `/thesis:propose-design` | Stage 4 | 연구 설계 제안 |
| `/thesis:assess-feasibility` | Stage 5 | 타당성 평가 |
| `/thesis:integrate-proposal` | Stage 6 | 제안서 통합 |

### 8.1.5 Quality Assurance (8 commands)

| Command | Purpose | Output |
|---------|---------|--------|
| `/thesis:check-plagiarism` | 표절 검사 (<15%) | Plagiarism report |
| `/thesis:evaluate-srcs` | SRCS 4-axis 평가 | SRCS scores |
| `/thesis:calculate-ptcs` | pTCS 계산 (4-level) | pTCS scores |
| `/thesis:evaluate-dual-confidence` | pTCS + SRCS 통합 | Dual confidence |
| `/thesis:monitor-confidence` | 실시간 대시보드 | Dashboard |
| `/thesis:validate-phase` | Phase 검증 | Validation report |
| `/thesis:validate-gate` | Gate 검증 | Gate status |
| `/thesis:validate-all` | 전체 검증 | Full report |

### 8.1.6 Autopilot & Self-Improvement (3 commands) ⭐ v4

| Command | Purpose | Output |
|---------|---------|--------|
| `/thesis:autopilot` | Autopilot 모드 제어 (on/off/status) | Simulation results |
| `/thesis:review-improvements` | 성능 분석 + 개선 제안 검토 | Advisory report |
| `/thesis:improvement-log` | 개선 이력 조회 (Audit Trail) | History summary |

### 8.1.7 Utility (4 commands)

| Command | Purpose | Output |
|---------|---------|--------|
| `/thesis:status` | 진행 상태 | Progress summary |
| `/thesis:progress` | 상세 진행 | 150-step checklist |
| `/thesis:translate` | 한국어 번역 | *-ko.md files |
| `/thesis:export-docx` | Word 내보내기 | .docx files |

## 8.2 Context Forking Strategy

### 8.2.1 When to Fork

**Forking Criteria**:
1. 리소스 집약적 (60+ minutes)
2. 복잡한 다단계 프로세스
3. 에러 격리 필요
4. 메인 컨텍스트 보호 중요

**Forked Commands**:
- `run-literature-review` (15 agents sequential)
- `run-research-design` (4-8 agents)
- `run-writing` (per-chapter iterative)
- `run-publication` (journal formatting)
- `validate-all` (full workflow validation)

### 8.2.2 Fork Lifecycle

```
Main Context
    ↓
Command: /thesis:run-literature-review (context: fork)
    ↓
┌─────────────────────────────────────┐
│  Forked Context                      │
│  1. Copy external memory             │
│     - session.json                   │
│     - todo-checklist.md              │
│     - research-synthesis.md          │
│  2. Execute Phase 1 (isolated)       │
│     - Wave 1-5 sequential            │
│     - All agents run                 │
│     - Quality validation             │
│  3. On completion                    │
│     - Collect all outputs            │
│     - Validate quality               │
│     - Merge back to main             │
└─────────────────────────────────────┘
    ↓
Merge Results → Main Context
    - Update session.json (phase completed)
    - Update todo-checklist.md (items checked)
    - Update research-synthesis.md (insights added)
    - Files written to thesis-output/
    ↓
Main Context (updated)
```

### 8.2.3 Error Handling in Forked Context

```python
def execute_forked_command(command_name):
    """
    Fork 컨텍스트에서 명령 실행
    """
    try:
        # 1. Fork context
        forked_ctx = fork_context(main_context)

        # 2. Execute in isolation
        result = execute_in_fork(command_name, forked_ctx)

        # 3. Validate result
        if not validate_result(result):
            raise ValidationError(f"{command_name} validation failed")

        # 4. Merge back
        merge_to_main(result, main_context)

        return {
            "status": "SUCCESS",
            "result": result
        }

    except Exception as e:
        # Error is isolated to fork
        # Main context remains intact
        log_error(f"Fork error: {e}")

        return {
            "status": "FAILED",
            "error": str(e),
            "main_context_status": "INTACT"  # 중요!
        }
```

## 8.3 Command Reference

### /thesis:init

**목적**: 새 연구 세션 초기화

**사용법**:
```bash
/thesis:init
```

**프로세스**:
1. Generate session ID
2. Create directory structure
3. Create session.json
4. Create todo-checklist.md (150 steps)
5. Initialize research-synthesis.md

**출력**:
```
✓ Session initialized: ai-ethics-2026-01-29
✓ Directory structure created
✓ External memory initialized
→ Next: /thesis:start or "시작하자"
```

### /thesis:quick-start (v2.2.0)

**목적**: 자연어 트리거 자동 실행

**자동 트리거**:
- "시작하자", "연구를 시작하자"
- "Let's start", "Start research"

**프로세스**:
1. Detect natural language pattern
2. Present 7-mode selection (AskUserQuestion)
3. Gather mode-specific info (2-3 questions)
4. Auto-execute: `/thesis:init` + `/thesis:start`

### /thesis:start

**목적**: 워크플로우 시작

**사용법**:
```bash
# Mode A: Topic
/thesis:start topic "AI윤리적 의사결정"

# Mode B: Question
/thesis:start question "RQ1: ... RQ2: ..."

# Mode C: Review
/thesis:start review --file user-resource/my-review.md

# Mode D: Learning
/thesis:start learning

# Mode E: Paper Upload (v2.2.0)
/thesis:start paper-upload --paper-path user-resource/uploaded-papers/paper.pdf
```

### /thesis:run-literature-review

**목적**: Phase 1 전체 실행

**프로세스**:
```
Wave 1 (4 agents) → Gate 1
Wave 2 (4 agents) → Gate 2
Wave 3 (4 agents) → Gate 3
Wave 4 (2 agents) → SRCS Evaluation
Wave 5 (3 agents) → Gate 4
→ HITL-2
```

**Context**: Fork (isolated execution)

**Duration**: 60-90 minutes

### /thesis:check-plagiarism

**목적**: 표절 검사

**프로세스**:
```python
# 1. Internal check (15 files cross-comparison)
internal_sim = rlm_similarity_matrix(all_files)

# 2. External check (vs. source papers)
external_sim = check_against_sources(all_files, source_papers)

# 3. Threshold check
max_sim = max(internal_sim + external_sim)
if max_sim > 0.15:
    raise PlagiarismError(f"Similarity {max_sim} exceeds 15%")
```

**출력**:
```yaml
plagiarism_report:
  max_similarity: 0.12
  verdict: PASS
  high_similarity_pairs:
    - file1: "wave2-theoretical-frameworks.md"
      file2: "wave4-synthesis.md"
      similarity: 0.12
      note: "Expected overlap (synthesis references frameworks)"
```

### /thesis:validate-all

**목적**: 전체 워크플로우 검증

**프로세스**:
```
1. GRA Compliance (100% required)
2. pTCS All Levels (60/70/75/75 thresholds)
3. SRCS Full Evaluation (75+ required)
4. Plagiarism Check (<15% required)
5. Citation Count (30+ unique sources)
6. Doctoral-Writing Compliance (80+ for Phase 3)
```

**출력**: Full validation report (PASS/FAIL)

---

# 9. Quality Assurance Systems

본 섹션은 자동화된 품질 보증 메커니즘, 검증 워크플로우, 실패 처리를 다룹니다.

## 9.1 Automated QA (Quality Assurance, 품질 보증) Pipeline (파이프라인, 자동화 처리 흐름)

### 9.1.1 Per-Agent Validation

```
Agent Output
    ↓
1. GRA Schema Validation
   - GroundedClaim 형식 체크
   - Required fields 존재 확인
   - Claim type 유효성
   ↓ PASS
2. Confidence Threshold Check
   - Type별 threshold 검증
   - Source requirement 확인
   ↓ PASS
3. Hallucination Firewall
   - BLOCK patterns 검사
   - REQUIRE_SOURCE patterns 검증
   ↓ PASS
4. pTCS Calculation
   - Claim-level score 계산
   - Threshold 60+ 확인
   ↓ PASS
5. Save Output
   - Write to file
   - Update session.json
   ↓
Next Agent or Gate
```

### 9.1.2 Gate Validation (Wave-level)

```
Wave N Complete
    ↓
1. Cross-Agent Consistency
   - Citation overlap (70%+ required)
   - Claim contradictions (0 allowed)
   ↓ PASS
2. Agent-level pTCS
   - Average across wave agents
   - Threshold 70+ required
   ↓ PASS
3. Cumulative Check
   - Prior waves + current wave
   - Coherence validation
   ↓ PASS
4. Gate Status: PASS
   ↓
Next Wave or SRCS Evaluation
```

### 9.1.3 Phase Validation

```
Phase N Complete
    ↓
1. All Gates Passed
   - Gate 1-4 (for Phase 1)
   ↓ PASS
2. Phase-level pTCS
   - Average across phase agents
   - Threshold 75+ required
   ↓ PASS
3. SRCS Evaluation (if Phase 1/3)
   - 4-axis scoring
   - Threshold 75+ required
   ↓ PASS
4. Plagiarism Check (if Phase 3)
   - <15% similarity required
   ↓ PASS
5. Phase Status: COMPLETE
   ↓
HITL Checkpoint
```

## 9.2 Quality Metrics Dashboard

### 9.2.1 Real-Time Monitoring

```python
def generate_quality_dashboard(session_id):
    """
    실시간 품질 대시보드
    """
    dashboard = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),

        "gra_compliance": {
            "total_claims": count_claims(session_id),
            "compliant_claims": count_compliant_claims(session_id),
            "compliance_rate": calculate_compliance_rate(session_id)
        },

        "ptcs": {
            "claim_level": {
                "mean": calculate_mean_ptcs(level="claim"),
                "below_threshold": count_below_threshold(level="claim", threshold=60)
            },
            "agent_level": {
                "mean": calculate_mean_ptcs(level="agent"),
                "below_threshold": count_below_threshold(level="agent", threshold=70)
            },
            "phase_level": {
                "mean": calculate_mean_ptcs(level="phase"),
                "below_threshold": count_below_threshold(level="phase", threshold=75)
            }
        },

        "srcs": {
            "average": calculate_average_srcs(session_id),
            "by_axis": {
                "CS": calculate_axis_score("CS"),
                "GS": calculate_axis_score("GS"),
                "US": calculate_axis_score("US"),
                "VS": calculate_axis_score("VS")
            },
            "grade_distribution": count_grades(session_id)
        },

        "plagiarism": {
            "max_similarity": get_max_similarity(session_id),
            "verdict": "PASS" if get_max_similarity(session_id) <= 0.15 else "FAIL"
        }
    }

    return dashboard
```

**출력 예시**:
```yaml
Quality Dashboard - AI Ethics Study
Generated: 2026-01-29T15:30:00Z

GRA Compliance:
  Total Claims: 147
  Compliant: 147 (100%)
  ✓ PASS

pTCS:
  Claim-level: 82.3 (Threshold: 60+) ✓
  Agent-level: 78.5 (Threshold: 70+) ✓
  Phase-level: 76.2 (Threshold: 75+) ✓
  ✓ PASS

SRCS:
  Average: 83.7 (Threshold: 75+) ✓
  CS (Citation): 85.2
  GS (Grounding): 84.3
  US (Uncertainty): 78.5
  VS (Verifiability): 86.1
  Grade Distribution:
    A: 45 (31%)
    B: 78 (53%)
    C: 24 (16%)
  ✓ PASS

Plagiarism:
  Max Similarity: 11.2%
  ✓ PASS (<15%)

Overall Status: ✅ EXCELLENT
```

## 9.3 Failure Handling & Recovery

### 9.3.1 Retry Strategies

**Auto-Retry with Exponential Backoff**:
```python
def retry_with_backoff(func, max_attempts=3, backoff_factor=2):
    """
    지수 백오프를 사용한 재시도
    """
    for attempt in range(max_attempts):
        try:
            result = func()
            return result

        except (APIError, ValidationError) as e:
            if attempt < max_attempts - 1:
                wait_time = backoff_factor ** attempt
                print(f"⚠️ Attempt {attempt+1} failed: {e}")
                print(f"Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise RetryExhaustedError(f"Failed after {max_attempts} attempts")
```

**Quality-Based Retry (with Claim-Level Feedback, v4.0.1)**:
```python
def quality_retry_loop(agent_name, input_context):
    """
    품질 기준을 만족할 때까지 재시도.
    실패 시 claim-level 진단 피드백을 주입하여 다음 시도 품질 향상.
    """
    attempt = 0
    max_attempts = 3  # PTCSEnforcer.MAX_RETRIES

    while attempt < max_attempts:
        # Execute agent
        output = execute_agent(agent_name, input_context)

        # Validate
        gra_valid = validate_gra(output)
        claims = extract_claims(output)
        claim_results = [calculate_claim_ptcs(c) for c in claims]
        agent_ptcs = calculate_agent_ptcs(claims)

        if gra_valid and agent_ptcs >= 70:
            # Quality threshold met
            return output
        else:
            # Generate claim-level diagnostic feedback (v4.0.1)
            low_claims = [c for c in claim_results if c.ptcs < 60]
            feedback = {
                'total_claims': len(claim_results),
                'avg_ptcs': mean([c.ptcs for c in claim_results]),
                'low_confidence_claims': [
                    {
                        'id': c.claim_id,
                        'ptcs': c.ptcs,
                        'weakest': identify_weakest_component(c),
                        # e.g., 'source_quality', 'uncertainty', 'grounding'
                    }
                    for c in sorted(low_claims, key=lambda x: x.ptcs)[:5]
                ],
                'common_weaknesses': identify_common_weaknesses(claim_results),
                # e.g., ['sources: Add PRIMARY sources with DOI',
                #         'uncertainty: Add hedging language']
            }

            # Inject feedback into kwargs for next attempt
            input_context["_retry_feedback"] = feedback
            attempt += 1

            print(f"⚠️ Agent pTCS {agent_ptcs} < threshold 70")
            print(f"Low claims: {len(low_claims)}, "
                  f"Common issues: {feedback['common_weaknesses']}")
            print(f"Retrying with feedback (attempt {attempt+1}/{max_attempts})...")

    raise QualityError(f"Failed to meet quality threshold after {max_attempts} attempts")
```

### 9.3.2 Manual Override (HITL)

**When Auto-Retry Fails**:
```python
def request_manual_review(agent_name, failed_output, failure_reason):
    """
    자동 재시도 실패 시 수동 검토 요청
    """
    # Present to user
    print(f"""
❌ Agent '{agent_name}' failed quality check after 5 attempts

Failure Reason: {failure_reason}

Options:
1. Review output and approve despite quality issue
2. Provide manual feedback for re-execution
3. Skip this agent (not recommended)
4. Restart from previous wave
""")

    choice = ask_user_choice()

    if choice == 1:
        # Manual approval
        return failed_output, "MANUAL_OVERRIDE"
    elif choice == 2:
        # Manual feedback
        feedback = ask_user_feedback()
        return re_execute_with_feedback(agent_name, feedback)
    elif choice == 3:
        # Skip (log warning)
        log_warning(f"Agent {agent_name} skipped by user")
        return None, "SKIPPED"
    else:
        # Restart
        return restart_from_previous_wave()
```

## 9.4 v5 Quality Architecture Enhancements

### 9.4.1 SOT-A Centralization

모든 수치 파라미터가 `workflow_constants.py` (SOT-A)에 중앙집중화:

```
workflow_constants.py (SOT-A)
  ├── confidence_monitor.py  (imports: ALERT_THRESHOLDS, PTCS_COLOR_BANDS)
  ├── cross_validator.py     (imports: WAVE_FILES, CONTRADICTION_PATTERNS, STOPWORDS)
  ├── dual_confidence_system.py (imports: DUAL_CONFIDENCE_THRESHOLDS/WEIGHTS)
  ├── gate_controller.py     (imports: MAX_RETRIES_WAVE/PHASE)
  ├── gra_validator.py       (imports: GRA_CONFIDENCE_THRESHOLDS, HALLUCINATION_PATTERNS)
  ├── ptcs_calculator.py     (imports: PTCS_COLOR_BANDS, PHASE_WEIGHTS)
  ├── ptcs_enforcer.py       (imports: PTCS_THRESHOLDS, MAX_RETRIES_AGENT)
  ├── srcs_evaluator.py      (imports: SRCS_WEIGHTS_BY_TYPE, GRADE_BANDS, OVERCONFIDENCE)
  ├── validate_gate.py       (imports: WAVE_FILES, PTCS_PROXY_WEIGHTS)
  └── chapter_consistency_validator.py (imports: severity weights)
```

**예외**: `lightweight-gra-hook.py`는 stdlib 제약으로 패턴을 인라인 복제합니다.

### 9.4.2 Deterministic Gate Pipeline

```
validate_gate.py (단일 진입점)
  │
  ├── session.json → research_type 로드
  ├── 출력 파일 수집 (_temp/ → phase_dir/)
  ├── srcs_evaluator.run_srcs_evaluation() → SRCS score
  ├── cross_validator.validate_wave() → consistency score
  ├── pTCS proxy = SRCS × 0.70 + consistency × 0.30
  └── DualConfidenceCalculator → PASS / FAIL / MANUAL_REVIEW / PASS_WITH_CAUTION
```

### 9.4.3 Real-time Hallucination Prevention

```
사용자/에이전트가 Write/Edit 호출
  │
  ▼
lightweight-gra-hook.py (PreToolUse)
  ├── 대상: thesis-output/**/*.md 파일만
  ├── BLOCK 패턴 → exit(2) → 쓰기 차단
  ├── REQUIRE_SOURCE 패턴 → stderr 경고
  └── 예외 발생 → exit(0) (fail-open)
  │
  ▼ (통과 시)
실제 Write/Edit 실행
```

### 9.4.4 Chapter Consistency Validation

4가지 결정론적 검사:
1. **용어 일관성**: 동일 개념의 다른 표기 감지 (AI vs artificial intelligence)
2. **인용 일관성**: 동일 참고문헌의 다른 형식 감지 ((Smith, 2024) vs Smith (2024))
3. **수치 일관성**: 동일 맥락의 다른 수치 감지 (5% 차이 임계값)
4. **교차 참조**: 존재하지 않는 챕터/절 참조 감지

### 9.4.5 Feedback Extraction Pipeline

```
thesis-reviewer 출력 (review-report-chN.md)
  │
  ▼
feedback_extractor.py (결정론적 regex)
  │
  ├── 점수 테이블 파싱
  ├── DWC 하위점수 추출
  ├── 판정 매핑 (✅→PASS, ⚠️→REVISE, ❌→REWRITE)
  ├── 이슈 목록 + 심각도 분류
  └── 우선순위 행동 목록 생성
  │
  ▼
revision-brief-chN.json (구조화된 수정 지시서)
```

---

# 10. Version History & Updates

## 10.1 Version Timeline

### v1.0.0 (Conceptual Phase) - 2025 Q3

**초기 컨셉**:
- 기본 워크플로우 구상
- 3-phase 구조 (Literature, Design, Writing)
- 단일언어 (English)

### v2.0.0 (Production Alpha) - 2025 Q4

**Major Release**:
- ✅ 5-phase workflow (0: Init, 1: Literature, 2: Design, 3: Writing, 4: Publication)
- ✅ 15 literature agents (Wave 1-5)
- ✅ GRA (Grounded Research Architecture)
- ✅ External memory (3-file architecture)
- ✅ Sequential execution model
- ✅ Bilingual output (English + Korean)

### v2.1.0 (Production Beta) - 2026 Q1

**Quality Enhancements**:
- ✅ pTCS (predicted Thesis Confidence Score) - 4-level
- ✅ SRCS (Source-Reliability-Confidence-Scope) - 4-axis
- ✅ Dual confidence system (pTCS 60% + SRCS 40%)
- ✅ RLM integration (6 Tier-1 agents)
- ✅ Doctoral-writing skill (mandatory for Phase 3)
- ✅ 8 automatic gates
- ✅ Context forking for intensive tasks

**Impact**:
- Information loss: 70% → <10% (RLM)
- Citation accuracy: 70% → 95%+ (RLM + doctoral-writing)
- Quality compliance: Manual → Automated (pTCS/SRCS)

### v2.2.0 (Production Stable) - 2026-01-28

**User Experience Revolution**:

**Feature 1: Mode E - Paper-Based Research Design**
- ✅ 6-stage systematic paper analysis
- ✅ Strategic gap identification (3-5 gaps)
- ✅ Novel hypothesis generation (6-15 hypotheses)
- ✅ Research design proposal (20-30 pages)
- ✅ Feasibility & ethics assessment
- ✅ Integrated proposal (40-60 pages MASTER)
- ✅ Scientific skills integration

**Feature 2: Natural Language Trigger**
- ✅ Proactive skill activation
- ✅ Pattern detection ("시작하자", "Let's start")
- ✅ 7-mode selection UI (AskUserQuestion) (v4에서 7-mode로 확장)
- ✅ Mode-specific information gathering
- ✅ Automatic workflow initialization

### v4.0.0 (Production) - 2026-01-31 ⭐ CURRENT

**Major Architecture Evolution**:

**Feature 1: Dual Agent Structure**
- ✅ Flat naming (42 agents): Task tool `subagent_type` 매칭용
- ✅ Hierarchical structure (61 agents): 역할별 정리
- ✅ 총 108 agent .md files
- ✅ Phase 0 subagents 6개 (paper-analyzer, gap-identifier, hypothesis-generator, design-proposer, feasibility-assessor, proposal-integrator)

**Feature 2: Mode F - Proposal Upload Workflow**
- ✅ proposal-analyzer agent: 프로포절 구조 파싱
- ✅ 연구 계획 추출 및 완성도 평가
- ✅ Flag-and-Follow 정책 (모순 감지)
- ✅ review-extracted-plan HITL checkpoint
- ✅ mode-f-proposal-upload-workflow.md specification

**Feature 3: Mode G - Custom Input Parser**
- ✅ custom-input-parser agent: 자유형식 텍스트 분석
- ✅ 연구 요소 자동 추출
- ✅ 적절한 Mode (A-F)로 자동 라우팅

**Feature 4: Autopilot / Simulation System**
- ✅ 3 simulation agents (alphago-evaluator, autopilot-manager, simulation-controller)
- ✅ Quick/Full/Both 시뮬레이션 모드
- ✅ AlphaGo-style 품질 평가
- ✅ 불확실성 기반 자동 모드 선택
- ✅ /thesis:autopilot 명령어

**Feature 5: Self-Improvement System (Advisory Only)**
- ✅ self-improvement-analyst agent
- ✅ 5-stage pipeline: Collect → Analyze → Classify → Log → Report
- ✅ Core Philosophy Invariants (10가지 불변 원칙)
- ✅ /thesis:review-improvements, /thesis:improvement-log 명령어
- ✅ 5개 신규 Python 스크립트 (performance_collector, improvement_analyzer, change_classifier, improvement_logger, self_improvement_engine)

**Feature 6: Enhanced Validation**
- ✅ validated_executor.py, validation_config.py, validation_fallback.py
- ✅ workflow_validator.py
- ✅ enable-validation.sh / disable-validation.sh

**Feature 7: Enhanced RLM**
- ✅ rlm_streaming_summarizer.py
- ✅ sliding_window_context.py
- ✅ progressive_compressor.py

**Feature 8: Thesis Hooks**
- ✅ hitl-checkpoint.sh, post-stage.sh, pre-stage.sh
- ⚠️ 현재 settings.json에서 비활성화 (timeout 이슈)

**Files**:
- Agents: 108 total (v2.2.0 대비 +54)
- Commands: 41 total (+12 new)
- Scripts: 43 total (21,437 lines, v2.2.0 대비 +20 scripts, +4,567 lines)
- References: 7 files (gra-specification → gra-architecture 개명, srcs-specification 삭제, hitl-checkpoints 삭제, 4 신규)

**Impact**:
- Input modes: 5 → 7 (Mode F, G)
- Agent coverage: 54 → 108 (Dual Structure)
- Automation: Manual → Autopilot (시뮬레이션 기반)
- Self-improvement: 없음 → Advisory pipeline

### v4.0.1 (QA Scoring Implementation) - 2026-02-01

**QA 채점 시스템 구현 완성**: placeholder/hardcoded 값을 실제 계산 로직으로 교체

**Change 1: `_calculate_coverage()` 실제 구현** — ptcs_calculator.py
- 기존: `return 1.0` (항상 25/25점 무조건 부여)
- 변경: 출력 파일의 마크다운 헤딩 + 클레임 텍스트에서 required_sections 존재 여부 실측
- `required_sections=None`인 경우 기존 동작 유지 (1.0 반환)

**Change 2: `_calculate_cross_reference_consistency()` 신규 구현** — ptcs_calculator.py
- 기존: `consistency_score = 15.0` (항상 15/15점 무조건 부여)
- 변경: source overlap (60%) + claim type coherence (40%) 기반 실측
- 단일 클레임 = 1.0 (자기일관), 무출처 = 0.5 (중립, 과도한 벌점 방지)

**Change 3: Retry Feedback 주입** — ptcs_enforcer.py
- 기존: 동일 kwargs로 blind retry
- 변경: `_retry_feedback` dict를 kwargs에 주입 (low claims, weakest component, common weaknesses)
- 신규 메서드: `_generate_retry_feedback`, `_identify_weakest_component`, `_identify_common_weaknesses`, `_log_retry_feedback`

**Change 4: US 기본점수 축소** — srcs_evaluator.py
- 기존: `score = 50` (불확실성 미표현 클레임에 50/100 무상 부여)
- 변경: `score = 35` (정직한 baseline)

**Change 5: GS Claim-Type-Aware 라우팅** — srcs_evaluator.py
- 기존: 모든 비철학적 클레임에 통계 패턴만 적용 → THEORETICAL 클레임 GS ≈ 30
- 변경: THEORETICAL/INTERPRETIVE/METHODOLOGICAL → 이론적 패턴 매칭 (according to, theory, suggests that 등)
- FACTUAL/EMPIRICAL/SPECULATIVE → 기존 통계 패턴 유지

**Invariants Preserved**:
- 임계값: claim=60, agent=70, phase=75, workflow=75 — 변경 없음
- SRCS 가중치: cs=0.35, gs=0.35, us=0.10, vs=0.20 — 변경 없음
- pTCS 가중치: source=40, type=25, uncertainty=20, grounding=15 — 변경 없음
- Dual confidence: pTCS 60% + SRCS 40% — 변경 없음
- MAX_RETRIES: 3 — 변경 없음

**Mathematical Impact (Agent-level pTCS)**:
```
Before: agent_ptcs = claim_avg/2 + 25(free) + 15(free) + firewall
         → claim_avg 41 yields 70.5 (passes dishonestly)

After:  agent_ptcs = claim_avg/2 + coverage(real) + consistency(real) + firewall
         → claim_avg 41 with 50% coverage, 60% consistency yields 52 (fails honestly)
         → claim_avg 70 with 80% coverage, 80% consistency yields 77 (passes earned)
```

### v5.0.0 (Quality Architecture v4) - 2026-03-01 ⭐ CURRENT

**Major Quality Architecture Evolution**:

**Feature 1: SOT 4-Domain Architecture**
- ✅ SOT-A (`workflow_constants.py`): 모든 수치 파라미터 중앙집중화
- ✅ SOT-B (`SKILL.md`): 오케스트레이션 로직 (수정 금지)
- ✅ SOT-C (`session.json`): 런타임 상태 (단일 기록자)
- ✅ SOT-D (`prompt/WORKFLOW.md`): 범용 시스템 프롬프트 소스
- ✅ 10+ 소비 파일이 SOT-A에서 import (값 드리프트 방지)
- ✅ `WAVE_FILES`가 `AGENT_OUTPUT_FILES`에서 파생 (파일명 드리프트 원천 차단)

**Feature 2: No Fake Scores 원칙**
- ✅ gate-automation.py: 가짜 폴백 (85, 85.7, 8.7) 완전 제거
- ✅ validate-gate.md: placeholder 점수 (82.0, 78.0, 80.5, 77.0) 제거
- ✅ 표절 점수: 하드코딩 → 파일에서 regex 실제 추출
- ✅ coverage 기본값 경고: `warnings.warn()` 추가

**Feature 3: Deterministic Gate Validation**
- ✅ `validate_gate.py`: LLM 없이 결정론적 Python 단일 진입점
- ✅ pTCS proxy = SRCS × 0.70 + consistency × 0.30
- ✅ `validate-gate.md`는 프레젠테이션 레이어로 전환

**Feature 4: Real-time Hallucination Prevention**
- ✅ `lightweight-gra-hook.py`: PreToolUse hook (stdlib only, fail-open)
- ✅ BLOCK 패턴 매칭 시 쓰기 차단 (exit 2)
- ✅ REQUIRE_SOURCE 패턴 → stderr 경고
- ✅ `settings.json`에 활성화 등록

**Feature 5: Research-Type-Aware SRCS**
- ✅ qualitative grounding: themes, saturation, triangulation, thick description
- ✅ SLR grounding: PRISMA, inclusion/exclusion criteria, database search
- ✅ mixed grounding: 양적+질적 + integration evidence
- ✅ SRCS 가중치 6개 연구유형 차별화 (default, quantitative, qualitative, philosophical, slr, mixed)
- ✅ SPECULATIVE 주장: 비실증적/이론적 브랜치로 재분류

**Feature 6: Cross-Validator 오탐 감소**
- ✅ 최소 공유 단어: 1 → 2, 최소 단어 길이: 4자
- ✅ 불용어 필터 (SOT-A `CROSS_VALIDATOR_STOPWORDS`)
- ✅ 모순 패턴: 다단어 정규식 (case-insensitive)
- ✅ `extract_claims_from_content()` 진단 경고 추가

**Feature 7: Chapter Consistency Validator**
- ✅ `chapter_consistency_validator.py`: 4가지 결정론적 검사
- ✅ 용어 일관성, 인용 일관성, 수치 일관성, 교차 참조 유효성
- ✅ 12 영어 + 5 한국어 변형 그룹

**Feature 8: Feedback Extractor**
- ✅ `feedback_extractor.py`: 리뷰 보고서 → `revision-brief-chN.json`
- ✅ 점수 테이블, DWC 하위점수, 판정, 이슈, 심각도, 우선순위 추출
- ✅ 배치 모드 (`--all`) 지원

**Feature 9: Enhanced Hook System**
- ✅ Context Recovery 60초 쿨다운 (컨텍스트 윈도우 오염 방지)
- ✅ RLM Context Monitor: 비활성 시 I/O 스킵
- ✅ Retry Enforcer: delay 0초 (불필요한 5초 대기 제거)
- ✅ 재시도 피드백 3채널: kwarg + prompt injection + sidecar file

**Feature 10: Wave Gate 정책 변경**
- ✅ MANUAL_REVIEW: 경고 후 진행 (이전: RuntimeError 중단)
- ✅ PASS_WITH_CAUTION: 경고 후 진행 (이전: 중단)
- ✅ Gate 상태에 `"passed_with_caution"` 구분 추가
- ✅ GRA 고신뢰 주장 hard-fail: FACTUAL/EMPIRICAL 미달 시 즉시 실패

**Files**:
- Agents: 116 total (v4 대비 +8)
- Commands: 44 total (+3 new)
- Scripts: 55 total (+12 new)
- Hooks: 9 total (Pre 3 + Post 6, lightweight GRA hook 신규)

**Impact**:
- Quality layers: 3 → 7 (4 신규 계층)
- Fake scores: 6 instances → 0 (fail-honest)
- Gate validation: LLM-dependent → Deterministic Python
- Qualitative SRCS: Penalized → Fair (전용 grounding 패턴)
- Cross-validator false positives: High → Low (2+ shared words, stopword filter)
- Hallucination prevention: Post-hoc only → Real-time + Post-hoc

## 10.2 Major Milestones

### Milestone 1: GRA Foundation (v2.0.0)

**Achievement**: Hallucination prevention through structured claims

**Key Components**:
- GroundedClaim schema
- 6 claim types with thresholds
- 4-level hallucination firewall
- Source verification

**Before/After**:
```
Before GRA:
  - Unverified claims
  - No source tracking
  - Hallucination rate: 30-40%

After GRA:
  - 100% verified claims
  - Full source tracing
  - Hallucination rate: <5%
```

### Milestone 2: Dual Confidence System (v2.1.0)

**Achievement**: Predictive + retrospective quality assurance

**Key Components**:
- pTCS: 4-level scoring (Claim → Workflow)
- SRCS: 4-axis evaluation (CS/GS/US/VS)
- Integrated scoring: 0.6*pTCS + 0.4*SRCS
- Auto-retry enforcement

**Impact**:
```
Quality Metrics:
  Phase 1 completion rate: 85% → 98%
  Average SRCS score: 72 → 85
  Manual intervention: 40% → 10%
```

### Milestone 3: RLM Integration (v2.1.0)

**Achievement**: Context overflow solution

**Key Components**:
- Recursive summarization (Zhang et al. 2025)
- Progressive compression (3-stage)
- Cost optimization (Haiku for sub-calls)
- 6 Tier-1 agents

**Impact**:
```
Context Handling:
  Effective capacity: 100K → 200K+ tokens
  Information loss: 70% → <10%
  Cost: +$0.50-1.50 per task (acceptable)
```

### Milestone 4: Natural Language UX (v2.2.0)

**Achievement**: Zero-command workflow initiation

**Key Components**:
- Proactive skill activation
- Pattern detection (한국어 + English)
- Interactive UI (AskUserQuestion)
- Mode-specific flows

**Impact**:
```
User Onboarding:
  Learning curve: Manual required → No manual
  First-time success: 60% → 95%
  Average start time: 5-10 min → <2 min
```

### Milestone 5: Paper-Based Design (v2.2.0)

**Achievement**: Research proposal from prior research

**Key Components**:
- 6-stage analysis pipeline
- Scientific skills integration
- Hypothesis generation (6-15 novel)
- 40-60 page integrated proposal

**Impact**:
```
Research Capability:
  Input modes: 4 → 5 (Mode E added)
  Research starting points: Topic/Question → Paper
  Hypothesis quality: User-generated → AI-assisted
  Time to proposal: Weeks → 60-90 minutes
```

### Milestone 6: Dual Architecture & Extended Modes (v4.0.0)

**Achievement**: Scalable agent architecture + expanded input modes

**Key Components**:
- Dual Agent Structure (flat + hierarchical)
- Mode F: Proposal Upload (proposal-analyzer)
- Mode G: Custom Input (custom-input-parser)
- 12 new workflow commands
- 20+ new Python scripts

**Impact**:
```
Architecture Scaling:
  Agents: 54 → 108 (Dual Structure)
  Commands: 36 → 41
  Input modes: 5 → 7 (Mode F, G)
  Scripts: 30+ → 43 (21,437 lines)
```

### Milestone 7: Autopilot & Self-Improvement (v4.0.0)

**Achievement**: Simulation-based automation + advisory performance analysis

**Key Components**:
- Autopilot System (3 simulation agents)
- Self-Improvement Pipeline (5-stage advisory)
- AlphaGo-style quality evaluation
- Core Philosophy Invariants (10 rules)

**Impact**:
```
Automation Level:
  Execution: Manual → Autopilot (Quick/Full/Both)
  Quality: Static → Dynamic (AlphaGo evaluation)
  Improvement: None → Advisory pipeline
  Governance: Ad-hoc → Invariant-protected
```

## 10.3 Production Evidence

### v4 현재 상태

v3에서 v4로 시스템 구조가 대폭 변경되어 세션이 재시작되었습니다.
- 세션 출력 경로: `.claude/thesis-output/` (root `thesis-output/`는 빈 디렉토리)
- 현재 1개 세션 진행: `ai-transformation-ax-framework-for-small-churches-2026-01-21`

### v2.2.0 이전 Production Evidence (참고)

**이전 완료 세션: 22** (v3 기준)

**By Research Type** (v3):
- Quantitative: 12 (55%)
- Qualitative: 6 (27%)
- Mixed Methods: 4 (18%)

**Average Quality Scores**:
```yaml
GRA Compliance: 99.8% (target: 100%)
pTCS (Workflow): 77.3 (target: 75+)
SRCS Average: 85.2 (target: 75+)
Plagiarism: 8.7% (target: <15%)
```

**Notable Sessions**:
1. "Why AI Cannot Possess Free Will" (Philosophical inquiry)
   - pTCS: 82.1, SRCS: 88.3
   - 5-chapter dissertation (187 pages)

2. "Quantum Mechanics and Human Free Will" (Interdisciplinary)
   - pTCS: 79.5, SRCS: 86.7
   - Mixed methods design

3. "AI Transformation for Small Churches" (Practical application)
   - pTCS: 75.8, SRCS: 84.1
   - Quantitative experimental design

**User Feedback** (informal):
- Learning curve: "Steep initially, but workflow guides well"
- Quality: "Exceeds expectations for AI-generated content"
- Time savings: "80-90% compared to manual literature review"

---

# 11. Usage Guide & Best Practices

## 11.1 Quick Start Guide

### For Beginners

**Step 1: Natural Language Start**
```
You: "시작하자" or "Let's start"

System: [Presents 7-mode selection]
```

**Step 2: Choose Mode**
- Mode A: Topic → "AI의 윤리적 의사결정"
- Mode B: Questions → "RQ1: ... RQ2: ..."
- Mode E: Paper Upload → Browse file

**Step 3: Follow Prompts**
- System asks 2-3 clarifying questions
- Provide concise answers

**Step 4: Approve at HITL Checkpoints**
- HITL-1: Confirm topic/questions
- HITL-2: Approve literature review (60-90 min later)
- HITL-3/4: Approve research design
- HITL-5/6/7: Approve chapters
- HITL-8: Final approval

**Step 5: Download Results**
- English: `dissertation-full-en.docx`
- Korean: `dissertation-full-ko.docx`

### For Advanced Users

**Direct Commands**:
```bash
# Initialize
/thesis:init

# Mode E (Paper Upload)
/thesis:start paper-upload --paper-path user-resource/papers/smith-2023.pdf

# Monitor quality in real-time
/thesis:monitor-confidence

# Manual quality checks
/thesis:check-plagiarism
/thesis:evaluate-srcs
/thesis:calculate-ptcs

# Export
/thesis:export-docx
```

## 11.2 Workflow Recommendations

### Mode Selection Guidelines

**Mode A (Topic)**:
- ✅ Use when: You have a broad research interest
- ✅ Best for: Exploratory research, new topics
- ⚠️ Time: Longest (topic → questions → literature)

**Mode B (Questions)**:
- ✅ Use when: You have specific research questions
- ✅ Best for: Hypothesis-driven research
- ⚠️ Requirement: Clear, specific RQs (3-5)

**Mode C (Existing Review)**:
- ✅ Use when: You already have literature review
- ✅ Best for: Continuing prior work
- ⚠️ Requirement: High-quality review file

**Mode D (Learning)**:
- ✅ Use when: You need methodology guidance
- ✅ Best for: First-time researchers
- ⚠️ Note: Tutorial only, no research output

**Mode E (Paper Upload)**:
- ✅ Use when: You have a key prior study
- ✅ Best for: Extension/replication studies
- ⚠️ Requirement: 20-40 page paper (optimal)

**Mode F (Proposal Upload)** ⭐ v4:
- ✅ Use when: You already have a research proposal
- ✅ Best for: Proposal-based systematic research
- ⚠️ Requirement: Structured proposal document

**Mode G (Custom Input)** ⭐ v4:
- ✅ Use when: You have unstructured research ideas
- ✅ Best for: Free-form text → automatic mode routing
- ⚠️ Note: Routes to appropriate Mode (A-F) automatically

### HITL Decision Strategy

**HITL-1 (Topic/RQ Approval)**:
- Review: 연구질문이 명확한가?
- Check: 검증 가능한가?
- Decide: RQ 수정 or 승인

**HITL-2 (Literature Review)**:
- Review: research-synthesis-ko.md (한국어)
- Check: 핵심 발견사항 충분한가?
- Check: 연구 갭이 명확한가?
- Decide: 추가 문헌 필요 or 승인

**HITL-3 (Research Type)**:
- Consider: 연구 목적 (탐색 vs. 검증)
- Consider: 자원 (시간, 참여자, 장비)
- Decide: Quantitative or Qualitative or Mixed

**HITL-4 (Design Approval)**:
- Review: 연구 설계 적절한가?
- Check: 실행 가능한가?
- Check: 윤리적 문제 없는가?
- Decide: 설계 수정 or 승인

**HITL-5 (Citation Style)**:
- Consider: 목표 학술지
- Consider: 분야 관행
- Decide: APA or MLA or Chicago or IEEE

**HITL-6/7 (Chapter Review)**:
- Review: 논증 논리적인가?
- Check: 인용 정확한가?
- Check: Doctoral-writing compliance 80+?
- Decide: 챕터 수정 or 승인

**HITL-8 (Final Approval)**:
- Review: 전체 논문 읽기
- Check: 일관성 (챕터 간)
- Check: 표절 검사 PASS?
- Decide: 투고 준비 or 추가 수정

## 11.3 Troubleshooting

### Common Issues

**Issue 1: Context Reset Mid-Session**

**Symptom**: "Session not found" error

**Solution**:
```bash
/thesis:resume
```

**How it works**: Loads session.json + todo-checklist.md + research-synthesis.md

---

**Issue 2: pTCS Below Threshold**

**Symptom**: "pTCS score 58 below threshold 60"

**Solution**: Auto-retry loop (system handles automatically)

**If persists**:
1. Review improvement feedback
2. Check source quality
3. Acknowledge uncertainty explicitly

---

**Issue 3: Plagiarism > 15%**

**Symptom**: "Similarity 18% exceeds threshold"

**Solution**:
1. System identifies high-similarity sections
2. Review overlapping text
3. Paraphrase or add citations
4. Re-run: `/thesis:check-plagiarism`

---

**Issue 4: HITL Timeout**

**Symptom**: System waiting for approval too long

**Solution**:
```bash
# Check current state
/thesis:status

# Resume from last checkpoint
/thesis:resume
```

---

## 11.4 Best Practices

### Dos ✅

1. **Start with Clear Research Questions**
   - Mode B > Mode A for faster workflow

2. **Review HITL Outputs Carefully**
   - Literature review: Check gaps
   - Design: Check feasibility

3. **Use Natural Language**
   - "시작하자" easier than `/thesis:quick-start`

4. **Monitor Quality**
   - Run `/thesis:monitor-confidence` regularly

5. **Save Checkpoints**
   - System auto-saves, but verify session.json

### Don'ts ❌

1. **Don't Skip HITL Checkpoints**
   - Quality depends on human decisions

2. **Don't Upload Low-Quality Papers (Mode E)**
   - Optimal: 20-40 pages, peer-reviewed

3. **Don't Override Quality Errors**
   - If pTCS/SRCS fails, fix the issue

4. **Don't Delete session.json**
   - External memory is critical for recovery

5. **Don't Expect Perfect First Draft**
   - Phase 3 generates solid draft, revision needed

---

# 12. Appendix

## 12.1 Glossary (용어 사전)

**Agent (에이전트)**: 특정 작업을 수행하는 독립적 AI 모듈 (108개, Dual Structure: flat + hierarchical)

**API (Application Programming Interface, 응용 프로그래밍 인터페이스)**: 소프트웨어 간 통신 규약

**APA (American Psychological Association, 미국심리학회)**: 사회과학 표준 인용 형식

**Autopilot (자동 조종)**: v4 신규. 불확실성 기반 자동 시뮬레이션 모드 선택 및 실행

**BLEU (Bilingual Evaluation Understudy, 이중언어 평가 대용)**: 기계번역 품질 평가 점수

**CI (Confidence Interval, 신뢰구간)**: 통계적 추정치의 불확실성 범위

**Claim (주장)**: 검증 가능한 연구 주장 (GroundedClaim schema)

**Context Fork (컨텍스트 포크)**: 메인 컨텍스트 복사본에서 격리된 실행

**CS (Citation Score, 인용 점수)**: SRCS 4-axis 중 인용 품질 평가 (35%)

**Doctoral-Writing (박사급 학술 작성)**: Phase 3 필수 스킬, 박사급 작성 품질 강제

**DOI (Digital Object Identifier, 디지털 객체 식별자)**: 학술 문헌의 고유 식별 코드

**Dual Confidence (이중 신뢰도)**: pTCS (60%) + SRCS (40%) 통합 신뢰도

**DV (Dependent Variable, 종속변수)**: 연구에서 측정되는 결과 변수

**E2E (End-to-End, 전체 흐름)**: 시작부터 끝까지 전 과정을 포함하는 테스트/프로세스

**FLOPs (Floating Point Operations, 부동소수점 연산 횟수)**: 연산 복잡도 측정 단위

**Gate (게이트, 품질 검증 관문)**: Wave 또는 Phase 경계의 품질 검증 체크포인트

**GRA (Grounded Research Architecture, 근거 기반 연구 아키텍처)**: 학술적 무결성 보장 시스템

**GS (Grounding Score, 근거 점수)**: SRCS 4-axis 중 증거 충분성 평가 (35%)

**Hallucination (환각)**: AI가 사실이 아닌 내용을 생성하는 현상

**Hallucination Firewall (환각 방화벽)**: 4-level (BLOCK/REQUIRE/SOFTEN/VERIFY)

**HITL (Human-In-The-Loop, 인간 참여 루프)**: 8개 전략적 인간 의사결정 지점

**IEEE (Institute of Electrical and Electronics Engineers, 국제전기전자공학회)**: 공학 표준 인용 형식

**IMRaD (Introduction, Methods, Results, and Discussion, 서론-방법-결과-논의)**: 학술 논문 표준 구조

**IV (Independent Variable, 독립변수)**: 연구에서 조작되는 원인 변수

**LDA (Latent Dirichlet Allocation, 잠재 디리클레 할당)**: 주제 모델링 알고리즘

**LLM (Large Language Model, 대규모 언어 모델)**: 대규모 텍스트 데이터로 학습된 AI 언어 모델

**MCP (Model Context Protocol, 모델 컨텍스트 프로토콜)**: 모델 간 컨텍스트 공유 프로토콜

**MLA (Modern Language Association, 현대언어학회)**: 인문학 표준 인용 형식

**Mode (모드)**: 연구 시작 방식 (A: Topic, B: Question, C: Review, D: Learning, E: Paper, F: Proposal, G: Custom)

**NL (Natural Language, 자연어)**: 사람이 일상적으로 사용하는 언어

**NLP (Natural Language Processing, 자연어 처리)**: AI를 활용한 언어 이해 및 생성 기술

**Phase (단계)**: 워크플로우 주요 단계 (0: Init, 1: Literature, 2: Design, 3: Writing, 4: Publication)

**pTCS (predicted Thesis Confidence Score, 예측 논문 신뢰도 점수)**: 4-level 예측 신뢰도 (Claim→Agent→Phase→Workflow)

**QA (Quality Assurance, 품질 보증)**: 출력물의 품질을 체계적으로 검증하는 과정

**RLM (Recursive Language Models, 재귀적 언어 모델)**: 컨텍스트 확장 기술 (100K→200K+)

**RNN (Recurrent Neural Network, 순환 신경망)**: 순차적 데이터 처리에 특화된 신경망 구조

**Self-Improvement (자기 개선)**: v4 신규. Advisory-only (자문 전용) 성능 분석 및 개선 제안 시스템

**SRCS (Source-Reliability-Confidence-Scope, 출처-신뢰도-확신-범위 평가)**: 4-axis 품질 측정 (CS/GS/US/VS)

**URL (Uniform Resource Locator, 웹 주소)**: 인터넷 자원의 고유 주소

**US (Uncertainty Score, 불확실성 점수)**: SRCS 4-axis 중 불확실성 표현 평가 (10%)

**VS (Verifiability Score, 검증가능성 점수)**: SRCS 4-axis 중 검증가능성 평가 (20%)

**Wave (웨이브, 하위 단계)**: Phase 1의 5개 하위 단계 (Wave 1-5)

## 12.2 File Structure Reference

```
thesis-output/{session-id}/
├── 00-session/
│   ├── session.json                 # Context file
│   ├── todo-checklist.md            # 150-step progress
│   └── research-synthesis.md        # Insights file (3-4K words)
│
├── 00-paper-based-design/           # Mode E only
│   ├── uploaded-paper.pdf
│   ├── paper-deep-analysis.md       # Stage 1 (5-7 pages)
│   ├── strategic-gap-analysis.md    # Stage 2 (3-5 gaps)
│   ├── novel-hypotheses.md          # Stage 3 (6-15 hypotheses)
│   ├── research-design-proposal.md  # Stage 4 (20-30 pages)
│   ├── feasibility-ethics-report.md # Stage 5 (5-8 pages)
│   └── integrated-research-proposal.md  # Stage 6 MASTER (40-60 pages)
│
├── 01-literature/
│   ├── research-synthesis.md        # English (3-4K words)
│   ├── research-synthesis-ko.md     # Korean
│   ├── wave1-literature-search.md   # + -ko.md
│   ├── wave1-seminal-works-analysis.md
│   ├── wave1-trend-analysis.md
│   ├── wave1-methodology-scan.md
│   ├── wave2-theoretical-frameworks.md
│   ├── wave2-empirical-evidence.md
│   ├── wave2-research-gaps.md
│   ├── wave2-variable-relationships.md
│   ├── wave3-critical-review.md
│   ├── wave3-methodology-critique.md
│   ├── wave3-limitations.md
│   ├── wave3-future-directions.md
│   ├── wave4-synthesis.md
│   ├── wave4-conceptual-model.md
│   ├── wave5-plagiarism-report.md
│   ├── wave5-unified-srcs-evaluation.md
│   └── (all files have -ko.md versions)
│
├── 02-research-design/
│   ├── hypotheses.md + -ko.md
│   ├── research-model.md + -ko.md
│   ├── sampling-plan.md + -ko.md
│   ├── statistical-analysis-plan.md + -ko.md
│   └── (or qualitative/mixed files)
│
├── 03-thesis/
│   ├── thesis-outline.md + -ko.md
│   ├── chapter-1-introduction.md + -ko.md
│   ├── chapter-2-literature-review.md + -ko.md
│   ├── chapter-3-methodology.md + -ko.md
│   ├── chapter-4-results.md + -ko.md
│   ├── chapter-5-discussion-conclusion.md + -ko.md
│   ├── dissertation-full-en.md
│   ├── dissertation-full-ko.md
│   ├── dissertation-full-en.docx
│   └── dissertation-full-ko.docx
│
└── 04-publication/
    ├── journal-selection.md + -ko.md
    ├── manuscript-formatted-{journal}.md
    ├── abstract-{journal}.md
    ├── cover-letter-{journal}.md
    └── submission-checklist-{journal}.md
```

## 12.3 Error Codes Reference

### GRA Errors

- **GRA-001**: Hallucination pattern detected → Output blocked, regenerate required
- **GRA-002**: Missing source for claim → Add source
- **GRA-003**: Confidence below threshold → Increase confidence or downgrade claim type
- **GRA-004**: Cross-validation failed → Re-run wave agents
- **GRA-005**: SRCS below 75 → Improve claim quality, re-evaluate

### pTCS Errors

- **pTCS-001**: Claim-level < 60 → Rework claim (add sources, acknowledge uncertainty)
- **pTCS-002**: Agent-level < 70 → Re-execute agent with feedback
- **pTCS-003**: Phase-level < 75 → Review entire phase, identify weak agents
- **pTCS-004**: Workflow-level < 75 → Major revision needed

### SRCS Errors

- **SRCS-001**: CS < 60 → Improve citation quality (use PRIMARY sources)
- **SRCS-002**: GS < 60 → Add more evidence, strengthen logical connection
- **SRCS-003**: US < 40 → Add uncertainty acknowledgment
- **SRCS-004**: VS < 50 → Improve verifiability (method details, data availability)

### Plagiarism Errors

- **PLAG-001**: Similarity > 15% → Paraphrase, add citations
- **PLAG-002**: External similarity > 15% → Check source attribution
- **PLAG-003**: Self-plagiarism detected → Revise overlapping sections

## 12.4 Contact & Support

**Documentation**:
- Architecture guide: `ARCHITECTURE-AND-PHILOSOPHY.md` (this file)
- User manual: `USER_MANUAL.md`
- Claude context: `CLAUDE.md`
- Decision log: `decision-log.md`
- Mode F workflow: `prompt/mode-f-proposal-upload-workflow.md`

**Quick Commands**:
- Help: `/thesis:status`
- Progress: `/thesis:progress`
- Resume: `/thesis:resume`

**For Developers**:
- Agent specs: `.claude/agents/thesis/`
- Command specs: `.claude/commands/thesis/`
- Scripts: `.claude/skills/thesis-orchestrator/scripts/`
- Hooks: `.claude/hooks/`

---

## Document Metadata

**Document**: ARCHITECTURE-AND-PHILOSOPHY.md
**Version**: 3.0.0
**System Version**: v5.0.0 (Production — Quality Architecture v4)
**Created**: 2026-01-29
**Last Updated**: 2026-03-01 (v5 Quality Architecture v4 update)
**Purpose**: 개발자를 위한 시스템 아키텍처, 설계 철학, 기술 구현 완전 문서화
**Target Audience**: 개발자 (유지보수 및 확장)
**Sections**: 12 (Executive Summary ~ Appendix)
**Total Pages**: ~150-180 pages (estimated)
**Language**: Korean (한국어)

---

**★ 시스템 개발 철학 ★**

```
"Academic Integrity First"
  품질 > 비용, 속도
  박사급 엄밀성 타협 불가

"Sequential Execution"
  병렬화 < 컨텍스트 일관성
  누적 지식 구축

"Grounded Research"
  모든 주장은 검증 가능
  Hallucination 방지 최우선

"Fail-Honest" (v5)
  가짜 점수보다 정직한 실패
  모르면 모른다고 답하는 시스템

"Deterministic Where It Matters" (v5)
  품질 판정 = 결정론적 Python
  콘텐츠 생성 = LLM

"Single Source of Truth" (v5)
  모든 수치는 정확히 한 곳에
  소비 코드는 import만

"Human-In-The-Loop"
  AI = 분석 도구
  Human = 전략적 의사결정

"Bilingual Accessibility"
  영어 = AI 최적 성능
  한국어 = 사용자 접근성
```

---

**End of Document**

*For questions, updates, or contributions, refer to the repository documentation.*

