#!/usr/bin/env python3
"""
Cross Validator - Wave 간 교차 검증 모듈
에이전트 출력 간 일관성 검사 및 모순 탐지
"""

import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any


from workflow_constants import (
    WAVE_FILES,
    CROSS_VALIDATOR_SEVERITY_WEIGHTS as SEVERITY_WEIGHTS,
    CONTRADICTION_PATTERNS,
    CROSS_VALIDATOR_STOPWORDS,
    CROSS_VALIDATOR_MIN_SHARED_WORDS,
    CROSS_VALIDATOR_MIN_WORD_LENGTH,
)


def extract_claims_from_file(file_path: Path) -> list[dict]:
    """마크다운 파일에서 Claims 섹션 추출"""
    if not file_path.exists():
        return []

    content = file_path.read_text(encoding="utf-8")
    return extract_claims_from_content(content, str(file_path))


def extract_claims_from_content(content: str, source: str = "") -> list[dict]:
    """컨텐츠에서 Claims 추출.

    Args:
        content: Markdown content containing ## Claims section with ```yaml block
        source: Source file path for diagnostics

    Returns:
        List of claim dictionaries
    """
    import warnings

    claims = []

    # Claims 섹션 찾기
    claims_match = re.search(
        r"##\s*Claims.*?```ya?ml\s*(.*?)```", content, re.DOTALL | re.IGNORECASE
    )

    if not claims_match:
        if source:
            warnings.warn(
                f"No '## Claims' section with ```yaml block found in {source}. "
                f"Cross-validation will skip this file.",
                stacklevel=2,
            )
        return []

    yaml_content = claims_match.group(1).strip()
    if not yaml_content:
        if source:
            warnings.warn(
                f"Empty YAML block in Claims section of {source}.",
                stacklevel=2,
            )
        return []

    try:
        data = yaml.safe_load(yaml_content)
        if data and "claims" in data:
            claims_list = data["claims"]
            if isinstance(claims_list, list):
                for claim in claims_list:
                    if isinstance(claim, dict):
                        claim["source_file"] = source
                        claims.append(claim)
            else:
                warnings.warn(
                    f"'claims' key in {source} is not a list (got {type(claims_list).__name__}).",
                    stacklevel=2,
                )
        elif data:
            warnings.warn(
                f"YAML in {source} parsed but missing 'claims' key. "
                f"Available keys: {list(data.keys()) if isinstance(data, dict) else 'N/A'}",
                stacklevel=2,
            )
    except yaml.YAMLError as e:
        warnings.warn(
            f"YAML parse error in Claims section of {source}: {e}",
            stacklevel=2,
        )

    return claims


def detect_inconsistencies(claims: list[dict]) -> list[dict]:
    """클레임 간 불일치 탐지"""
    inconsistencies = []

    # 클레임 쌍 비교
    for i, claim1 in enumerate(claims):
        for claim2 in claims[i + 1 :]:
            # 같은 에이전트의 클레임은 비교하지 않음
            if claim1.get("agent") == claim2.get("agent"):
                continue

            text1 = claim1.get("text", "").lower()
            text2 = claim2.get("text", "").lower()

            # 모순 패턴 검사
            contradiction = check_contradiction(text1, text2)
            if contradiction:
                inconsistencies.append(
                    {
                        "type": "CONTRADICTION",
                        "claim1_id": claim1.get("id"),
                        "claim2_id": claim2.get("id"),
                        "agent1": claim1.get("agent"),
                        "agent2": claim2.get("agent"),
                        "topic": contradiction["topic"],
                        "severity": "HIGH",
                        "details": f"'{claim1.get('text')}' vs '{claim2.get('text')}'",
                    }
                )
                continue

            # 수치 불일치 검사
            numeric_issue = check_numeric_inconsistency(text1, text2)
            if numeric_issue:
                inconsistencies.append(
                    {
                        "type": "NUMERIC_MISMATCH",
                        "claim1_id": claim1.get("id"),
                        "claim2_id": claim2.get("id"),
                        "agent1": claim1.get("agent"),
                        "agent2": claim2.get("agent"),
                        "topic": numeric_issue["topic"],
                        "severity": numeric_issue["severity"],
                        "details": f"Values: {numeric_issue['value1']} vs {numeric_issue['value2']}",
                    }
                )

    return inconsistencies


def check_contradiction(text1: str, text2: str) -> dict | None:
    """모순 패턴 검사 (주제 유사성 검증 포함)"""
    for pattern1, pattern2 in CONTRADICTION_PATTERNS:
        has_p1_in_t1 = re.search(pattern1, text1, re.IGNORECASE)
        has_p2_in_t2 = re.search(pattern2, text2, re.IGNORECASE)
        has_p1_in_t2 = re.search(pattern1, text2, re.IGNORECASE)
        has_p2_in_t1 = re.search(pattern2, text1, re.IGNORECASE)

        if (has_p1_in_t1 and has_p2_in_t2) or (has_p1_in_t2 and has_p2_in_t1):
            # Topic similarity check — skip if texts are about different topics
            if not similar_context(text1, text2):
                continue

            common_words = set(text1.lower().split()) & set(text2.lower().split())
            topic_words = [
                w for w in common_words
                if w not in CROSS_VALIDATOR_STOPWORDS
                and len(w) >= CROSS_VALIDATOR_MIN_WORD_LENGTH
            ]
            topic = " ".join(topic_words[:3]) if topic_words else "effect direction"
            return {"topic": topic}

    return None


def check_numeric_inconsistency(text1: str, text2: str) -> dict | None:
    """수치 불일치 검사"""
    # 숫자와 맥락 추출
    num_pattern = r"(\w+(?:\s+\w+)?)\s+(?:was|is|were|are)?\s*(\d+(?:\.\d+)?%?)"

    matches1 = re.findall(num_pattern, text1)
    matches2 = re.findall(num_pattern, text2)

    for context1, value1 in matches1:
        for context2, value2 in matches2:
            # 비슷한 맥락인지 확인
            if similar_context(context1, context2):
                # 값이 다른지 확인
                v1 = parse_numeric(value1)
                v2 = parse_numeric(value2)

                if v1 is not None and v2 is not None and v1 != v2:
                    diff_pct = abs(v1 - v2) / max(v1, v2, 1) * 100

                    severity = "LOW"
                    if diff_pct > 20:
                        severity = "HIGH"
                    elif diff_pct > 10:
                        severity = "MEDIUM"

                    return {
                        "topic": context1,
                        "value1": value1,
                        "value2": value2,
                        "severity": severity,
                    }

    return None


def similar_context(ctx1: str, ctx2: str) -> bool:
    """맥락 유사성 검사 (불용어 제외, 의미어 기반)"""
    words1 = {
        w for w in ctx1.lower().split()
        if w not in CROSS_VALIDATOR_STOPWORDS
        and len(w) >= CROSS_VALIDATOR_MIN_WORD_LENGTH
    }
    words2 = {
        w for w in ctx2.lower().split()
        if w not in CROSS_VALIDATOR_STOPWORDS
        and len(w) >= CROSS_VALIDATOR_MIN_WORD_LENGTH
    }
    common = words1 & words2
    return len(common) >= CROSS_VALIDATOR_MIN_SHARED_WORDS


def parse_numeric(value: str) -> float | None:
    """숫자 파싱"""
    try:
        clean = value.replace("%", "")
        return float(clean)
    except ValueError:
        return None


def calculate_consistency_score(
    claims: list[dict], inconsistencies: list[dict]
) -> float:
    """일관성 점수 계산"""
    if not claims:
        return 100.0

    total_penalty = 0
    for inc in inconsistencies:
        severity = inc.get("severity", "MEDIUM")
        penalty = SEVERITY_WEIGHTS.get(severity, 8)
        total_penalty += penalty

    max_penalty = len(claims) * 10
    score = max(0, 100 - (total_penalty / max_penalty * 100))
    return round(score, 1)


def evaluate_gate(validation_result: dict, threshold: float = 75) -> dict:
    """교차 검증 게이트 평가"""
    score = validation_result.get("consistency_score", 0)
    inconsistencies = validation_result.get("inconsistencies", [])

    passed = score >= threshold
    warnings = None

    # 불일치가 있으면 경고 생성
    if passed and inconsistencies:
        low_severity_only = all(inc.get("severity") == "LOW" for inc in inconsistencies)
        if low_severity_only:
            warnings = [
                f"경미한 불일치 발견: {len(inconsistencies)}건. 검토 권장."
            ]
        else:
            warnings = [
                f"일부 불일치 발견: {len(inconsistencies)}건. 검토 권장."
            ]

    return {
        "passed": passed,
        "score": score,
        "threshold": threshold,
        "warnings": warnings,
        "inconsistency_count": len(inconsistencies),
    }


def validate_wave(temp_dir: Path, wave: int) -> dict:
    """Wave 출력 파일 검증"""
    expected_files = WAVE_FILES.get(wave, [])
    validated_files = []
    missing_files = []
    all_claims = []

    for fname in expected_files:
        file_path = temp_dir / fname
        if file_path.exists():
            validated_files.append(fname)
            claims = extract_claims_from_file(file_path)
            for claim in claims:
                claim["agent"] = fname.replace(".md", "")
            all_claims.extend(claims)
        else:
            missing_files.append(fname)

    inconsistencies = detect_inconsistencies(all_claims)
    consistency_score = calculate_consistency_score(all_claims, inconsistencies)

    result = {
        "wave": wave,
        "files_validated": len(validated_files),
        "files_expected": len(expected_files),
        "missing_files": missing_files,
        "total_claims": len(all_claims),
        "inconsistencies": inconsistencies,
        "consistency_score": consistency_score,
    }

    gate = evaluate_gate(result)
    result["gate_passed"] = gate["passed"]
    result["gate_warnings"] = gate.get("warnings")

    return result


def generate_validation_report(validation_result: dict) -> str:
    """검증 보고서 생성"""
    wave = validation_result.get("wave", 0)
    score = validation_result.get("consistency_score", 0)
    passed = validation_result.get("gate_passed", False)
    inconsistencies = validation_result.get("inconsistencies", [])

    lines = [
        f"# Cross-Validation Report - Wave {wave}",
        "",
        f"## 검증 결과 요약",
        f"- 일관성 점수 (Consistency Score): {score}/100",
        f"- 게이트 통과: {'✅ 통과' if passed else '❌ 실패'}",
        f"- 총 클레임 수: {validation_result.get('total_claims', 0)}",
        f"- 발견된 불일치: {len(inconsistencies)}건",
        "",
    ]

    if inconsistencies:
        lines.append("## 발견된 불일치")
        lines.append("")
        lines.append("| 유형 | 심각도 | 주제 | 상세 |")
        lines.append("|------|--------|------|------|")
        for inc in inconsistencies:
            lines.append(
                f"| {inc.get('type')} | {inc.get('severity')} | "
                f"{inc.get('topic', 'N/A')} | {inc.get('details', '')[:50]}... |"
            )
        lines.append("")

    # 권고사항
    lines.append("## 권고사항 (Recommendations)")
    if not passed:
        lines.append("### 즉시 조치 필요")
        lines.append("- 불일치 항목 검토 및 수정 필요")
        lines.append("- 수정 후 재검증 실행")
    elif inconsistencies:
        lines.append("### 검토 권장")
        lines.append("- 경미한 불일치가 발견됨")
        lines.append("- 진행 전 검토 권장")
    else:
        lines.append("- 추가 조치 불필요")

    return "\n".join(lines)


def run_cross_validation(temp_dir: Path, waves: list[int] | None = None) -> dict:
    """전체 교차 검증 실행"""
    if waves is None:
        waves = [1, 2, 3, 4, 5]

    wave_results = []
    total_score = 0
    total_waves = 0

    for wave in waves:
        result = validate_wave(temp_dir, wave)
        wave_results.append(result)
        if result["files_validated"] > 0:
            total_score += result["consistency_score"]
            total_waves += 1

    overall_consistency = round(total_score / max(total_waves, 1), 1)

    return {
        "validation_date": datetime.now().isoformat(),
        "waves_validated": waves,
        "wave_results": wave_results,
        "overall_consistency": overall_consistency,
        "gate_results": [
            {"wave": r["wave"], "passed": r["gate_passed"]} for r in wave_results
        ],
        "all_gates_passed": all(r["gate_passed"] for r in wave_results),
    }


def save_validation_result(result: dict, output_path: Path) -> None:
    """검증 결과 저장"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))


def main():
    """CLI 엔트리포인트"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: cross_validator.py <temp_dir> [wave_numbers...]")
        sys.exit(1)

    temp_dir = Path(sys.argv[1])
    waves = [int(w) for w in sys.argv[2:]] if len(sys.argv) > 2 else None

    result = run_cross_validation(temp_dir, waves)

    # 보고서 생성
    for wave_result in result["wave_results"]:
        report = generate_validation_report(wave_result)
        print(report)
        print("\n" + "=" * 50 + "\n")

    print(f"Overall Consistency: {result['overall_consistency']}/100")
    print(f"All Gates Passed: {result['all_gates_passed']}")

    # 결과 저장
    output_path = temp_dir / "cross-validation-result.json"
    save_validation_result(result, output_path)
    print(f"Result saved to: {output_path}")


if __name__ == "__main__":
    main()
