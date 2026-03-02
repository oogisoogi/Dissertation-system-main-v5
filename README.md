# Dissertation Research Workflow System v5

AI 기반 박사논문 연구 워크플로우 시뮬레이션 시스템

> 연구 아이디어 입력 → 150페이지 완성 논문 출력

## 개요

본 시스템은 박사논문 연구의 전 과정을 시뮬레이션하는 AI 워크플로우 시스템입니다. 연구 주제 탐색부터 문헌검토, 연구설계, 논문 작성, 학술지 투고 전략까지 전 과정을 116개의 전문 AI 에이전트가 수행합니다.

## 주요 기능

- **7가지 입력 모드**: 연구 주제, 연구질문, 논문 업로드, 프로포절 업로드, 자유입력 등
- **5단계 연구 파이프라인**: 초기화 → 문헌검토 → 연구설계 → 논문작성 → 출판전략
- **5가지 연구 유형 지원**: 양적연구, 질적연구, 혼합연구, 철학연구, SLR
- **GRA 아키텍처**: 실시간 환각 차단 + 사후 4축 평가의 이중 품질보증
- **시뮬레이션 모드**: Quick(20-30쪽) / Full(150쪽+) 선택 가능
- **Autopilot 모드**: 불확실성 기반 자동/수동 전환
- **이중 언어 출력**: 영어 연구 + 한국어 번역
- **SOT 4-Domain 아키텍처**: 단일 진실 소스(Single Source of Truth) 기반 설계

## v5 주요 변경사항 (Quality Architecture v4)

| 변경 사항 | 설명 |
| --- | --- |
| SOT-A 중앙집중화 | 10+ 파일에 분산된 상수를 `workflow_constants.py`로 통합 |
| No Fake Scores | 가짜 폴백 점수(85, 85.7 등) 완전 제거, fail-honest 설계 |
| 결정론적 Gate 검증 | `validate_gate.py`로 LLM 없이 Python만으로 gate 판정 |
| 실시간 GRA Hook | Write/Edit 시 환각 패턴 차단 (PreToolUse lightweight hook) |
| 연구유형별 SRCS | 질적/SLR/혼합연구 전용 grounding 패턴 추가 |
| 챕터 일관성 검증 | 교차 챕터 용어/인용/수치/참조 일관성 자동 검증 |
| 피드백 추출기 | 리뷰 보고서 → 구조화된 수정 지시서 자동 변환 |
| Wave Gate 완화 | MANUAL_REVIEW 시 경고 후 진행 (이전: 중단) |

## 시스템 구성

| 구성 요소         | 수량  | 설명                                          |
| ----------------- | ----- | --------------------------------------------- |
| AI 에이전트       | 116개 | 문헌검색, 가설생성, 연구설계 등 전문 에이전트 |
| 인터랙티브 커맨드 | 44개  | 워크플로우 제어 슬래시 커맨드                 |
| 핵심 스크립트     | 55개  | 검증, 게이트 관리, 품질 평가 등               |
| Pre/Post 훅       | 9개   | 실시간 품질 감시 및 자동화                    |
| 품질 게이트       | 4개   | Wave/Phase 간 교차 검증                       |

## 빠른 시작

### 사전 요구사항

- [Claude Code CLI](https://docs.anthropic.com/en/docs/claude-code) 설치
- Python 3.10+
- Node.js 18+

### 실행

```bash
# 프로젝트 디렉토리 진입
cd Dissertation-system-main-v5

# 의존성 설치
pip install -e ".[dev]"
npm install

# Claude Code에서 워크플로우 시작
# 방법 1: 슬래시 커맨드
/thesis:start

# 방법 2: 빠른 시작
/thesis:quick-start

# 방법 3: 논문 업로드 기반
/thesis:start-paper-upload

# 방법 4: 프로포절 업로드 기반
/thesis:start-proposal-upload
```

## 워크플로우 구조

```
Phase 0: 초기화
  └─ 입력 모드 선택 (A~G) → 연구유형 설정

Phase 1: 문헌검토 (5 Waves)
  ├─ Wave 1: 문헌검색 · 핵심문헌 · 트렌드 · 방법론 스캔
  ├─ Wave 2: 이론적 프레임워크 · 실증분석 · 갭 식별 · 변수관계
  ├─ Wave 3: 비판적 검토 · 방법론 비평 · 한계점 · 미래방향
  ├─ Wave 4: 종합 · 개념모델 구축
  └─ Wave 5: 표절검사 · SRCS 평가 · 최종 종합

Phase 2: 연구설계
  ├─ 양적연구: 가설개발 → 연구모델 → 표본설계 → 통계계획
  ├─ 질적연구: 패러다임 → 참여자선정 → 자료수집 → 분석전략
  ├─ 혼합연구: 설계유형 → 양적+질적 → 통합전략
  └─ 철학연구 / SLR: 전용 설계 파이프라인

Phase 3: 논문작성
  └─ 아웃라인 설계 → 챕터별 집필 → DWC 검증 → 품질검토

Phase 4: 출판전략
  └─ 학술지 선정 → 원고 포맷팅
```

## 품질 보증 체계

### 이중 품질보증 (Real-time + Post-hoc)

| 계층 | 메커니즘 | 시점 |
| --- | --- | --- |
| L1 | Lightweight GRA Hook | Write/Edit 시 실시간 차단 |
| L2 | GRA Hallucination Firewall | 에이전트 출력 검증 |
| L3 | SRCS 4축 평가 (CS/GS/US/VS) | Wave/Phase Gate |
| L4 | pTCS 4레벨 점수 | 전체 워크플로우 추적 |
| L5 | Cross-Validator | Wave 간 일관성 검증 |
| L6 | Chapter Consistency | 챕터 간 교차 검증 |
| L7 | DWC (Doctoral Writing Compliance) | 챕터별 학술 글쓰기 준수 |

### 품질 임계값

| 메트릭 | 임계값 | 설명 |
| --- | --- | --- |
| pTCS | >= 75 | 논문 완성도 예측 |
| SRCS | >= 75 | 추론 및 주장 품질 |
| Plagiarism | < 15% | 표절 유사도 |
| DWC | >= 80 | 학술 글쓰기 준수 |

## SOT (Single Source of Truth) 4-Domain 아키텍처

| Domain | 파일 | 역할 |
| --- | --- | --- |
| SOT-A | `workflow_constants.py` | 모든 수치 파라미터 (150 steps, 임계값, 가중치) |
| SOT-B | `SKILL.md` | Claude Code 오케스트레이션 (수정 금지) |
| SOT-C | `session.json` | 런타임 상태 (단일 기록자: 오케스트레이터) |
| SOT-D | `prompt/WORKFLOW.md` | 범용 시스템 프롬프트 소스 |

## 기술 스택

- **AI 프레임워크**: Claude Code CLI (Agents, Skills, Commands, Hooks)
- **백엔드**: Python 3.10+, Node.js
- **품질 관리**: Ruff, pre-commit hooks, pytest
- **CI/CD**: GitHub Actions

## 프로젝트 구조

```
.claude/
  ├─ agents/thesis/      # 116개 전문 AI 에이전트
  ├─ commands/thesis/     # 44개 인터랙티브 커맨드
  ├─ skills/              # 핵심 스킬 및 오케스트레이터 (55개 스크립트)
  └─ hooks/               # Pre/Post 검증 훅 (9개)
prompt/                   # 워크플로우 설계 문서 (SOT-D)
tests/                    # 단위/통합/E2E 테스트
user-resource/            # 사용자 업로드 자료 (논문, 프로포절)
thesis-output/            # 생성된 논문 출력물
```

## 관련 문서

- [USER_MANUAL.md](./USER_MANUAL.md) - 상세 사용자 매뉴얼
- [ARCHITECTURE-AND-PHILOSOPHY.md](./ARCHITECTURE-AND-PHILOSOPHY.md) - 시스템 아키텍처 및 설계 철학
- [decision-log.md](./decision-log.md) - 아키텍처 결정 기록
- [copyright.md](./copyright.md) - 저작권 정보

## 저작권

Copyright (c) 2025-2026 최윤식 (Yoonsik, Choi). All rights reserved.

자세한 내용은 [copyright.md](./copyright.md)를 참조하세요.
