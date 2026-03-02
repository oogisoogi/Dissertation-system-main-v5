---
description: Wave/Phase Gate 자동 검증
context: fork
agent: general-purpose
---

# Gate 검증

Wave Gate 또는 Phase Gate를 자동 검증합니다.

## 역할

이 커맨드는 **GateController**를 실행하여:
- Gate 통과 조건 검증
- pTCS + SRCS 통합 평가
- Auto-retry 로직 (실패 시)
- 상태 추적 및 기록

## Gate 종류

### Wave Gates (Phase 1 only)
```
Gate 1: Wave 1 완료 후 (문헌탐색 4개 에이전트)
Gate 2: Wave 2 완료 후 (이론/실증 4개 에이전트)
Gate 3: Wave 3 완료 후 (비판적 검토 4개 에이전트)
Gate 4: Wave 4 완료 후 (종합 2개 에이전트)
```

### Phase Gates
```
Phase 0: Initialization
Phase 1: Literature Review
Phase 2: Research Design
Phase 3: Thesis Writing
Phase 4: Publication Strategy
```

## Gate 통과 조건

| Gate Type | pTCS Threshold | SRCS Threshold |
|-----------|----------------|----------------|
| Wave Gate | ≥70 | ≥75 |
| Phase Gate | ≥75 | ≥75 |

**결정 로직**: pTCS가 강한 기준 (pTCS < threshold → 자동 FAIL)

## 실행 방법

```bash
# Wave Gate 검증
/thesis:validate-gate wave 1

# Phase Gate 검증
/thesis:validate-gate phase 1
```

## Implementation

```python
import sys
import subprocess
import json
from pathlib import Path

# Parse arguments
args = "$ARGUMENTS".split()
if len(args) < 2:
    print("Usage: /thesis:validate-gate <wave|phase> <number>")
    sys.exit(1)

gate_type = args[0].lower()
gate_number = args[1]

if gate_type not in ("wave", "phase"):
    print(f"❌ Error: Invalid gate type '{gate_type}'. Use 'wave' or 'phase'.")
    sys.exit(1)

# Find working directory from session marker
marker_file = Path("thesis-output") / ".current-working-dir.txt"
if marker_file.exists():
    working_dir = Path(marker_file.read_text().strip())
else:
    print("❌ Error: No active session found (.current-working-dir.txt missing)")
    sys.exit(1)

# Locate the deterministic gate validation script
scripts_dir = Path(".claude") / "skills" / "thesis-orchestrator" / "scripts"
validate_script = scripts_dir / "validate_gate.py"

if not validate_script.exists():
    print(f"❌ Error: validate_gate.py not found at {validate_script}")
    sys.exit(1)

# Execute deterministic gate validation (no LLM, pure Python computation)
print(f"\n🚪 Validating {gate_type.capitalize()} Gate {gate_number}...")
print(f"   Using deterministic validator: validate_gate.py")
print("="*70)

result = subprocess.run(
    [sys.executable, str(validate_script), gate_type, gate_number, "--dir", str(working_dir)],
    capture_output=True, text=True
)

try:
    gate_result = json.loads(result.stdout)
except json.JSONDecodeError:
    print(f"❌ Error: Failed to parse gate validation output")
    if result.stderr:
        print(f"   stderr: {result.stderr[:500]}")
    sys.exit(1)

# Display result
if "error" in gate_result:
    print(f"\n❌ Error: {gate_result['error']}")
else:
    print(f"\n📊 Gate Scores:")
    print(f"  SRCS: {gate_result.get('srcs_score', 0)}/100")
    print(f"  Consistency: {gate_result.get('consistency_score', 0)}/100")
    print(f"  pTCS (proxy): {gate_result.get('ptcs_proxy', 0)}/100")

    print(f"\n🎯 Decision: {gate_result['decision']}")
    if gate_result.get('passed'):
        print(f"  ✅ Gate {gate_number} PASSED")
    else:
        print(f"  ❌ Gate {gate_number} FAILED")

    print(f"\n💬 Reasoning:")
    print(f"  {gate_result.get('reasoning', 'N/A')}")

print("="*70)

# Save gate status
gate_status_file = working_dir / f"gate-status-{gate_type}-{gate_number}.json"
with open(gate_status_file, 'w') as f:
    json.dump(gate_result, f, indent=2, ensure_ascii=False)
print(f"\n💾 Gate status saved to: {gate_status_file}")

sys.exit(0 if gate_result.get('passed') else 1)
```

## Auto-Retry 로직

### Wave Gates
- 실패 시 최대 **3회** 자동 재시도
- 재시도 시 해당 Wave 전체 재실행

### Phase Gates
- 실패 시 최대 **2회** 자동 재시도
- 재시도 시 해당 Phase 전체 재실행

## 출력 예시

### PASS
```
🚪 Validating Wave Gate 1...
══════════════════════════════════════════════════════════════════════

📊 Gate Scores:
  pTCS: 82.0/100
  SRCS: 78.0/100
  Combined: 80.4/100

🎯 Decision: PASS
  ✅ Gate 1 PASSED

💬 Reasoning:
  Both pTCS (82.0) and SRCS (78.0) meet thresholds. Combined score: 80.4
══════════════════════════════════════════════════════════════════════
```

### FAIL (with retry)
```
🚪 Validating Wave Gate 2...
══════════════════════════════════════════════════════════════════════

📊 Gate Scores:
  pTCS: 68.0/100
  SRCS: 80.0/100
  Combined: 72.8/100

🎯 Decision: FAIL
  ❌ Gate 2 FAILED

💬 Reasoning:
  pTCS (68.0) below threshold (70). Automatic FAIL.

⚠️  Auto-retry enabled: Attempt 1/3
   Re-running Wave 2 agents...
══════════════════════════════════════════════════════════════════════
```

## 상태 추적

Gate 상태는 다음에 저장됩니다:
```
thesis-output/[project]/
└── gate-status-wave-1.json
└── gate-status-phase-1.json
```

## 사용 시점

- ✅ Wave 완료 후 (Phase 1)
- ✅ Phase 완료 후 (모든 Phase)
- ✅ 품질 게이트 강제 시

## 관련 명령어

- `/thesis:evaluate-dual-confidence` - pTCS + SRCS 평가
- `/thesis:calculate-ptcs` - pTCS 계산
- `/thesis:monitor-confidence` - 실시간 모니터링

$ARGUMENTS
