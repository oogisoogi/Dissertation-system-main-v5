---
description: 자연어 트리거로 워크플로우 빠른 시작 (사용자가 "시작하자", "연구하자" 등을 입력하면 자동 실행)
allowed-tools: Bash(*), Write(*), Read(*), AskUserQuestion(*)
---

# 박사논문 연구 워크플로우 빠른 시작

사용자가 자연어로 연구 시작 의사를 표현하면 자동으로 워크플로우 초기화 및 모드 선택이 진행됩니다.

## 자연어 트리거 패턴

다음과 같은 표현을 감지하면 이 커맨드가 자동 실행됩니다:

### 시작 표현
- "시작하자", "시작할게", "시작합니다"
- "연구를 시작하자", "연구 시작", "연구하자"
- "논문을 쓰자", "논문 작성 시작", "논문연구를 시작하자"
- "박사논문 연구를 시작하자", "학위논문 시작"
- "Let's start", "Start research", "Begin thesis"

### 도움 요청 표현
- "논문 연구를 도와줘", "연구 도와줘"
- "박사논문 쓰는 걸 도와줘"
- "Help me with my thesis", "Assist with research"

---

## 실행 프로세스

### Step 1: 환영 메시지

사용자에게 환영 메시지를 표시합니다:

```
┌─────────────────────────────────────────────────────────────┐
│  🎓 박사논문 연구 워크플로우에 오신 것을 환영합니다!         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  이 시스템은 연구 주제 탐색부터 학술지 투고까지,            │
│  박사급 AI 에이전트가 체계적으로 논문 연구를 지원합니다.    │
│                                                              │
│  📊 주요 기능:                                               │
│  ├─ 15개 전문 에이전트 기반 문헌검토                        │
│  ├─ 양적/질적/혼합연구 설계 지원                            │
│  ├─ GRA 기반 품질 보증 (할루시네이션 방지)                  │
│  ├─ 장별 논문 작성 및 검토                                  │
│  └─ 학술지 선정 및 투고 전략                                │
│                                                              │
│  🚀 지금부터 연구 시작 방법을 선택해주세요!                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

### Step 1.5: 시뮬레이션 모드 선택 (MANDATORY — 반드시 먼저 표시)

**이 단계는 절대 생략할 수 없습니다.** 사용자가 "시작하자" 등으로 워크플로우를 시작하면, 환영 메시지 직후 반드시 이 시뮬레이션 모드 선택을 먼저 표시합니다.

AskUserQuestion으로 시뮬레이션 모드를 선택합니다:

```yaml
questions:
  - question: "논문 시뮬레이션 모드를 선택하세요. 연구 품질(pTCS/SRCS 75+)은 모든 모드에서 동일합니다. 차이는 분량과 소요 시간뿐입니다."
    header: "시뮬레이션"
    multiSelect: false
    options:
      - label: "Quick Simulation (권장 — 빠른 검증)"
        description: "압축된 박사급 논문 (20-30p, 1-2시간). Ch 1-5 모두 작성. 전체 흐름 확인 및 방향 검증에 최적. 학회 발표 수준."

      - label: "Full Simulation (최종 완성)"
        description: "상세한 박사급 논문 (145-155p, 5-7시간). Ch 1-5 모두 작성. 최종 학위논문 및 학술지 투고용. Journal article 수준."

      - label: "Quick → Full (단계적 완성)"
        description: "1단계: Quick으로 전체 초안 작성 → 2단계: 사용자 검토 및 방향 확인 → 3단계: Full로 정교화. 가장 안전한 접근 (6-9시간)."

      - label: "Smart Autopilot (AI 자동 선택)"
        description: "AI가 연구 복잡도와 불확실성을 분석하여 최적 모드를 자동 결정. 불확실성 높으면 Quick, 낮으면 Full을 자동 선택."
```

선택 결과를 변수에 저장:
- **"Quick Simulation" 선택 시**: `simulation_mode = "quick"`
- **"Full Simulation" 선택 시**: `simulation_mode = "full"`
- **"Quick → Full" 선택 시**: `simulation_mode = "both"`
- **"Smart Autopilot" 선택 시**: `simulation_mode = "smart"`

> **참고**: 이 선택은 HITL-2(문헌검토 승인), HITL-3(연구설계 승인) 시점에서 변경(override) 가능합니다.

---

### Step 2-1: 대분류 선택

AskUserQuestion으로 사용자에게 3가지 대분류 중 선택을 요청합니다.

```yaml
questions:
  - question: "어떤 방식으로 연구를 시작하시겠습니까?"
    header: "시작 방식"
    multiSelect: false
    options:
      - label: "새로운 연구 시작 (주제/질문/자유 입력)"
        description: "연구 주제나 질문을 입력하여 처음부터 시작합니다. 가장 일반적인 방법입니다."

      - label: "자료 기반 시작 (논문/프로포절/문헌검토 업로드)"
        description: "기존 자료를 업로드하여 분석 기반으로 시작합니다."

      - label: "학습모드 (연구방법론 학습)"
        description: "논문 연구 방법론을 체계적으로 학습합니다. 8개 트랙 튜토리얼을 제공합니다."
```

- **"학습모드" 선택 시**: Mode D 직행 → Step 3-5로 이동
- **"새로운 연구 시작" 선택 시**: Step 2-2a로 이동
- **"자료 기반 시작" 선택 시**: Step 2-2b로 이동
- **"Other" 선택 시**: Step 2-1로 복귀 또는 워크플로우 취소

---

### Step 2-2a: 새로운 연구 시작 세부 선택

```yaml
questions:
  - question: "어떤 입력 방식을 사용하시겠습니까?"
    header: "입력 방식"
    multiSelect: false
    options:
      - label: "연구 주제 입력 (가장 일반적)"
        description: "관심 주제를 입력하면, AI가 연구질문을 도출하고 문헌검토를 수행합니다. 예: '조직 내 심리적 안전감이 혁신 행동에 미치는 영향'"

      - label: "연구질문 직접 입력"
        description: "이미 명확한 연구질문이 있다면 바로 문헌검토 단계로 진입합니다. 예: 'AI 도입이 조직 학습에 어떤 영향을 미치는가?'"

      - label: "자유 형식 입력 (상세 방향 기술)"
        description: "주제, 방법론, 변수 등을 자유롭게 기술하면 AI가 구조화합니다. 예: '심리적 안전감이 팀 혁신에 미치는 영향을 양적연구로, 리더십의 조절효과를 보고 싶어요'"
```

- **"연구 주제 입력" 선택 시**: Mode A → Step 3-1로 이동
- **"연구질문 직접 입력" 선택 시**: Mode B → Step 3-2로 이동
- **"자유 형식 입력" 선택 시**: Mode G → Step 3-7로 이동
- **"Other" 선택 시**: Step 2-1로 복귀

---

### Step 2-2b: 자료 기반 시작 세부 선택

```yaml
questions:
  - question: "어떤 자료를 기반으로 시작하시겠습니까?"
    header: "자료 유형"
    multiSelect: false
    options:
      - label: "선행연구 논문 업로드 (남의 논문 분석)"
        description: "선행연구 논문(PDF)을 업로드하면, AI가 논문을 분석하여 새로운 가설과 연구 설계를 제안합니다."

      - label: "연구 프로포절 업로드 (나의 계획서 실행)"
        description: "이미 작성한 연구 프로포절이 있다면, 계획을 추출하여 체계적으로 실행합니다."

      - label: "기존 문헌검토 활용"
        description: "이미 작성한 문헌검토가 있다면, 이를 분석하여 연구 갭을 식별하고 연구 설계로 진행합니다."
```

- **"선행연구 논문 업로드" 선택 시**: Mode E → Step 3-3로 이동
- **"연구 프로포절 업로드" 선택 시**: Mode F → Step 3-6으로 이동
- **"기존 문헌검토 활용" 선택 시**: Mode C → Step 3-4로 이동
- **"Other" 선택 시**: Step 2-1로 복귀

---

### Step 3: 모드별 추가 정보 수집

선택된 모드에 따라 추가 정보를 수집합니다.

#### 3-1. Mode A (연구 주제 입력) 선택 시

```yaml
questions:
  - question: "연구하고 싶은 주제나 관심사를 입력해주세요"
    header: "연구 주제"
    # 사용자가 직접 텍스트 입력 (자유 입력)

  - question: "어떤 학문 분야의 연구인가요?"
    header: "학문 분야"
    multiSelect: false
    options:
      - label: "경영학/경제학"
        description: "조직행동, 전략, 마케팅, 재무, 회계 등"
      - label: "사회과학"
        description: "심리학, 사회학, 정치학, 커뮤니케이션 등"
      - label: "인문학"
        description: "철학, 문학, 역사, 언어학 등"
      - label: "자연과학/공학"
        description: "물리, 화학, 생물, 컴퓨터과학, 공학 등"
      - label: "의학/보건학"
        description: "임상의학, 보건정책, 간호학 등"
      - label: "교육학"
        description: "교육심리, 교육과정, 교육공학 등"

  - question: "연구 유형을 미리 정하셨나요? (나중에 변경 가능)"
    header: "연구 유형"
    multiSelect: false
    options:
      - label: "아직 미정 (권장)"
        description: "문헌검토 후 결정합니다. 가장 유연한 접근입니다."
      - label: "양적연구 (설문/실험)"
        description: "가설 검증, 통계 분석이 필요한 연구"
      - label: "질적연구 (인터뷰/관찰)"
        description: "현상의 심층적 이해, 이론 개발이 필요한 연구"
      - label: "혼합연구"
        description: "양적+질적 방법을 통합하는 연구"
```

인용 스타일 선택 (모든 모드 공통):

```yaml
questions:
  - question: "논문의 인용 스타일을 선택하세요"
    header: "인용 스타일"
    multiSelect: false
    options:
      - label: "APA 7th Edition (권장)"
        description: "사회과학/경영학/교육학 표준. 본문 (Author, Year) 형식, 미주(endnotes) 사용."
      - label: "Chicago 17th Edition"
        description: "인문학/역사학 표준. 각주(footnotes) 방식, Bibliography 사용."
      - label: "MLA 9th Edition"
        description: "어문학/인문학 표준. 본문 (Author Page) 형식, Works Cited 사용."
      - label: "Harvard Referencing"
        description: "영연방권 대학교 표준. 본문 (Author Year) 형식, Reference List 사용."
```

**다음 단계**: 입력받은 정보로 `/thesis:init` 실행 → `/thesis:start topic [주제]`

---

#### 3-2. Mode B (연구질문 직접 입력) 선택 시

```yaml
questions:
  - question: "연구질문을 입력해주세요 (예: AI가 조직 학습에 미치는 영향은?)"
    header: "연구질문"
    # 사용자가 직접 텍스트 입력

  - question: "어떤 학문 분야의 연구인가요?"
    header: "학문 분야"
    multiSelect: false
    options:
      - label: "경영학/경제학"
      - label: "사회과학"
      - label: "인문학"
      - label: "자연과학/공학"
      - label: "의학/보건학"
      - label: "교육학"

  - question: "문헌검토 깊이를 선택하세요"
    header: "문헌검토"
    multiSelect: false
    options:
      - label: "Standard (권장)"
        description: "최근 10년, 핵심 문헌 50편 내외. 대부분의 연구에 적합합니다."
      - label: "Comprehensive (심층)"
        description: "최근 20년, 100편 이상. 체계적 문헌검토가 필요한 경우."
      - label: "Quick (빠름)"
        description: "최근 5년, 30편 내외. 시간이 제한적인 경우."
```

**다음 단계**: `/thesis:init` → `/thesis:start question "[연구질문]"`

---

#### 3-3. Mode E (선행연구 논문 업로드) 선택 시

```yaml
questions:
  - question: "논문 파일을 업로드할 준비가 되셨나요?"
    header: "논문 업로드"
    multiSelect: false
    options:
      - label: "예, 파일 경로를 알려드리겠습니다"
        description: "user-resource/uploaded-papers/ 폴더에 논문을 넣고 경로를 제공합니다."
      - label: "파일을 직접 첨부하겠습니다"
        description: "Claude Code 대화창에 PDF 파일을 드래그&드롭합니다."
      - label: "아직 준비 안 됨"
        description: "다른 모드를 추천드립니다."

  - question: "분석 깊이를 선택하세요 (논문 길이에 따라 조정)"
    header: "분석 깊이"
    multiSelect: false
    options:
      - label: "Comprehensive (권장)"
        description: "가장 상세한 분석. 6-15개 가설 생성. 60-90분 소요."
      - label: "Standard"
        description: "표준 분석. 3-8개 가설 생성. 40-60분 소요."
      - label: "Quick"
        description: "빠른 분석. 2-5개 가설 생성. 20-30분 소요."
```

**다음 단계**:
1. 파일 경로 확인/입력 받기
2. `/thesis:init` → `/thesis:start paper-upload --paper-path [경로]`

---

#### 3-4. Mode C (기존 문헌검토 활용) 선택 시

```yaml
questions:
  - question: "문헌검토 파일을 어떻게 제공하시겠습니까?"
    header: "파일 제공"
    multiSelect: false
    options:
      - label: "파일 경로 제공"
        description: "user-resource/ 폴더에 문헌검토 파일을 넣고 경로를 알려주세요."
      - label: "직접 첨부"
        description: "Claude Code 대화창에 파일을 드래그&드롭합니다."

  - question: "문헌검토의 주요 초점은 무엇인가요?"
    header: "초점 영역"
    multiSelect: false
    options:
      - label: "연구 갭 식별 (권장)"
        description: "기존 문헌의 한계를 찾고 새로운 연구 기회를 발견합니다."
      - label: "이론적 프레임워크 구축"
        description: "문헌을 바탕으로 이론적 토대를 구축합니다."
      - label: "방법론 설계"
        description: "선행연구의 방법론을 분석하여 새로운 설계를 제안합니다."
```

**다음 단계**: `/thesis:init` → `/thesis:start review`

---

#### 3-5. Mode D (학습모드) 선택 시

```yaml
questions:
  - question: "어떤 연구방법론을 학습하고 싶으신가요?"
    header: "학습 트랙"
    multiSelect: false
    options:
      - label: "Track 1: 논문의 기초"
        description: "논문이란 무엇인가? 학술적 글쓰기의 특성과 구조."
      - label: "Track 2: 연구 설계 기초"
        description: "연구질문 수립, 가설 설정, 변수와 조작적 정의."
      - label: "Track 3: 문헌검토 방법론"
        description: "체계적 문헌검토, 비판적 읽기, 문헌 매트릭스 작성."
      - label: "Track 4: 양적연구 방법론"
        description: "연구설계 유형, 표본추출, 통계분석, 신뢰도/타당도."
      - label: "Track 5: 질적연구 방법론"
        description: "질적연구 패러다임, 자료수집, 코딩, 신뢰성 확보."
      - label: "Track 6: 혼합연구 방법론"
        description: "혼합연구 설계 유형, 자료 통합 전략."
      - label: "Track 7: 학술적 글쓰기"
        description: "APA/MLA/Chicago 스타일, 논증 구조, 표절 방지."
      - label: "Track 8: 종합 실습"
        description: "미니 연구 프로젝트 수행, 단계별 피드백."

  - question: "학습 방식을 선택하세요"
    header: "학습 방식"
    multiSelect: false
    options:
      - label: "개념 학습 + 실습 (권장)"
        description: "이론 학습 후 즉시 실습 과제를 통해 적용합니다."
      - label: "개념 학습만"
        description: "이론과 개념을 먼저 학습합니다."
      - label: "실습 위주"
        description: "최소한의 설명 후 바로 실습에 집중합니다."
```

**다음 단계**: `/thesis:init` → `/thesis:start learning --track [N]`

---

#### 3-6. Mode F (연구 프로포절 업로드) 선택 시

```yaml
questions:
  - question: "프로포절 파일을 어떻게 제공하시겠습니까?"
    header: "파일 업로드"
    multiSelect: false
    options:
      - label: "예, 파일 경로를 알려드리겠습니다"
        description: "user-resource/proposals/ 폴더에 프로포절을 넣고 경로를 제공합니다."
      - label: "파일을 직접 첨부하겠습니다"
        description: "Claude Code 대화창에 파일을 드래그&드롭합니다."
      - label: "아직 준비 안 됨"
        description: "다른 모드를 추천드립니다."

  - question: "프로포절의 완성도는 어느 정도인가요?"
    header: "완성도"
    multiSelect: false
    options:
      - label: "완성본 (제출용 수준)"
        description: "모든 섹션이 작성된 상태입니다."
      - label: "초안 (Draft)"
        description: "일부 섹션이 미완성이거나 수정이 필요합니다."
```

**다음 단계**:
1. 파일 경로 확인/입력 받기
2. `/thesis:init` → `/thesis:start-proposal-upload --proposal-path [경로]`

---

#### 3-7. Mode G (자유 형식 입력) 선택 시

자유 형식 입력은 AskUserQuestion의 "Other" 옵션을 활용합니다.

```yaml
questions:
  - question: "연구에 대한 생각을 자유롭게 입력해주세요. 주제, 방법론, 변수, 제약조건 등 알고 계신 것을 모두 적어주세요."
    header: "자유 입력"
    multiSelect: false
    options:
      - label: "한국어로 입력하겠습니다"
        description: "예: '심리적 안전감이 팀 혁신에 미치는 영향을 양적연구로, 리더십의 조절효과를 보고 싶어요. IT기업 팀장-팀원 쌍 200명 정도를 생각하고 있습니다.'"
      - label: "I'll write in English"
        description: "E.g.: 'I want to study how AI adoption affects organizational learning in Korean SMEs, using a mixed methods approach.'"
```

사용자가 "Other"를 선택하여 자유 텍스트를 입력하면, `@custom-input-parser`가 텍스트를 분석하여 구조화합니다.
분석 결과를 사용자에게 확인받은 후 Mode A 또는 Mode B로 라우팅합니다.

**다음 단계**: `@custom-input-parser` 분석 → 사용자 확인 → `/thesis:init --entry-path custom --custom-preferences '[JSON]'`

---

### Step 4: 세션 초기화 및 워크플로우 시작

수집된 정보를 바탕으로 자동으로 워크플로우를 초기화하고 시작합니다.

```bash
# 1. 세션 초기화 (수집된 정보 사용 — simulation_mode 필수 전달)
python3 .claude/skills/thesis-orchestrator/scripts/init_session.py \
  --mode [선택된 모드] \
  --simulation-mode [Step 1.5에서 선택된 값: quick|full|both|smart] \
  --discipline "[학문 분야]" \
  --type "[연구 유형]" \
  --citation-style [인용 스타일 키: apa7|chicago17|mla9|harvard|ieee] \
  --base-dir thesis-output \
  "[입력된 주제/질문]"

# 2. 워크플로우 시작 (모드별 분기)
# Mode A: /thesis:start topic "[주제]"
# Mode B: /thesis:start question "[연구질문]"
# Mode C: /thesis:start review --review-path "[경로]"
# Mode D: /thesis:start learning --track [N]
# Mode E: /thesis:start paper-upload --paper-path "[경로]"
# Mode F: /thesis:start-proposal-upload --proposal-path "[경로]"
# Mode G: /thesis:start topic --entry-path custom --custom-preferences '[JSON]'
```

---

### Step 5: 진행 상태 안내

워크플로우가 시작되면 사용자에게 진행 상태를 안내합니다:

```
┌─────────────────────────────────────────────────────────────┐
│  ✅ 워크플로우 초기화 완료!                                  │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  📁 작업 디렉토리:                                           │
│     thesis-output/[연구제목-2026-01-28]/                   │
│                                                              │
│  📋 선택된 모드: [Mode A: 연구 주제 입력]                    │
│  🎮 시뮬레이션: [Quick / Full / Both / Smart]               │
│  📚 학문 분야: [경영학/경제학]                               │
│  🔬 연구 유형: [아직 미정]                                   │
│                                                              │
│  🚀 다음 단계:                                               │
│     Phase 0 → 주제 탐색 및 연구질문 도출 (5-10분)           │
│     Phase 1 → 심층 문헌검토 (15개 에이전트, 2-3시간)        │
│     Phase 2 → 연구 설계 (30-60분)                           │
│     Phase 3 → 논문 작성 (장별, 3-5시간)                     │
│     Phase 4 → 투고 전략 (30분)                              │
│                                                              │
│  💡 언제든지 /thesis:status 로 진행 상태를 확인할 수 있습니다 │
│                                                              │
└─────────────────────────────────────────────────────────────┘

지금부터 연구를 시작합니다...
```

---

## 에러 처리

### 불완전한 정보 입력
사용자가 필수 정보를 제공하지 않은 경우:
```
⚠️  필수 정보가 누락되었습니다.
다시 입력해주시거나, /thesis:init 명령으로 수동 초기화를 진행해주세요.
```

### 파일 경로 오류 (Mode C, E, F)
파일을 찾을 수 없는 경우:
```
⚠️  파일을 찾을 수 없습니다: [경로]

다음 중 하나를 선택하세요:
1. 올바른 파일 경로 다시 제공
2. 파일을 user-resource/ 폴더에 업로드 후 재시도
3. 다른 모드로 변경
```

### 프로포절 파일 오류 (Mode F)
프로포절 파일이 손상되었거나 내용이 부족한 경우:
```
⚠️  프로포절 분석에 실패했습니다.

원인: [파일 손상 / 내용 부족 (5페이지 미만) / 지원하지 않는 형식]

다음 중 하나를 선택하세요:
1. 다른 프로포절 파일 제공
2. Mode A (주제 입력)로 변경
3. Mode G (자유 입력)로 상세 방향 직접 기술
```

### 모드 선택 취소
사용자가 "Other" 선택 또는 취소한 경우:
```
워크플로우 시작이 취소되었습니다.

다시 시작하려면:
- "연구를 시작하자" 입력
- 또는 /thesis:init 명령 실행
```

---

## 고급 옵션

### 빠른 시작 (질문 스킵)
이미 정보를 알고 있다면 직접 커맨드 사용:

```bash
# Mode A
/thesis:start topic "조직 심리적 안전감과 혁신"

# Mode B
/thesis:start question "AI가 조직 학습에 미치는 영향은?"

# Mode E
/thesis:start paper-upload --paper-path user-resource/papers/smith-2023.pdf

# Mode F
/thesis:start-proposal-upload --proposal-path user-resource/proposals/my-proposal.pdf
```

> **Note**: Mode G (자유 입력)는 UI 전용 모드입니다. `/thesis:quick-start`의 Step 2-2a에서 "자유 형식 입력"을 선택하여 사용하세요. 직접 커맨드로는 `--entry-path custom --custom-preferences '[JSON]'` 옵션을 사용할 수 있습니다.

### 세션 재개
이전에 시작한 세션을 계속하려면:

```bash
/thesis:resume
```

---

## 사용자 경험 최적화

### 응답 시간 최적화
- AskUserQuestion: 한 번에 최대 3개 질문
- 필수 정보만 수집 (나머지는 기본값 사용)
- 모드 선택 → 모드별 추가 질문 (2단계)

### 명확한 안내
- 각 옵션에 상세한 설명 제공
- 권장 옵션 명시 ("권장", "가장 일반적")
- 예시 제공

### 유연한 입력
- 자유 텍스트 입력 지원
- 파일 첨부 다중 방식 지원
- 나중에 변경 가능함을 명시

---

## Integration with Main Workflow

```
자연어 트리거 감지
  ↓
/thesis:quick-start (자동 실행)
  ↓
Step 1: 환영 메시지
Step 2: 모드 선택 (AskUserQuestion)
Step 3: 모드별 추가 정보 수집
Step 4: 세션 초기화
Step 5: 워크플로우 자동 시작
  ↓
Phase 0-4 진행...
```

---

## 예시 대화 흐름

### Example 1: Mode A (연구 주제)

```
사용자: 연구를 시작하자

Claude:
┌─────────────────────────────────────────────────┐
│  🎓 박사논문 연구 워크플로우에 오신 것을 환영합니다! │
└─────────────────────────────────────────────────┘

[모드 선택 UI 표시]
○ 연구 주제 입력 (가장 일반적)
○ 연구질문 직접 입력
○ 선행연구 논문 업로드
○ 기존 문헌검토 활용
○ 학습모드

사용자: [연구 주제 입력 선택]

Claude: [추가 질문]
- 연구 주제: "조직 내 심리적 안전감이 혁신에 미치는 영향"
- 학문 분야: [경영학/경제학 선택]
- 연구 유형: [아직 미정 선택]

Claude:
✅ 워크플로우 초기화 완료!
📁 thesis-output/psychological-safety-innovation-2026-01-28/
🚀 Phase 0 시작 - 주제 탐색 중...
```

### Example 2: Mode E (논문 업로드)

```
사용자: 논문연구를 시작하자

Claude: [환영 메시지 + 모드 선택]

사용자: [선행연구 논문 업로드 선택]

Claude: [추가 질문]
- 파일 업로드 방식: [파일 경로 제공 선택]
- 분석 깊이: [Comprehensive 선택]

사용자: user-resource/uploaded-papers/smith-2023.pdf

Claude:
✅ 논문 파일 확인됨: smith-2023.pdf
📄 @paper-research-designer 실행 중...
  Stage 1/6: 논문 심층 분석 (15분 예상)
```

---

$ARGUMENTS