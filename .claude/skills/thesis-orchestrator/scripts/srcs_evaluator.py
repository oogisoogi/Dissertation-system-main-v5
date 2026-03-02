#!/usr/bin/env python3
"""
SRCS Evaluator - 통합 SRCS 평가 시스템
전체 연구 클레임을 종합 평가하고 품질 보고서 생성
"""

import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Any

from cross_validator import extract_claims_from_file
from workflow_constants import (
    SRCS_WEIGHTS_BY_TYPE,
    SRCS_DEFAULT_THRESHOLD as DEFAULT_THRESHOLD,
    SRCS_GRADE_BANDS,
    SRCS_AXIS_GRADE_BANDS,
    OVERCONFIDENCE_PATTERNS as _OVERCONFIDENCE_PATTERNS,
)

# Backward-compatible alias
SRCS_WEIGHTS = SRCS_WEIGHTS_BY_TYPE["default"]


def get_srcs_weights(research_type: str = "default") -> dict:
    """Get SRCS weights for a given research type."""
    return SRCS_WEIGHTS_BY_TYPE.get(research_type, SRCS_WEIGHTS_BY_TYPE["default"])


# 클레임 유형 키워드
CLAIM_TYPE_KEYWORDS = {
    "THEORETICAL": ["theory", "theoretical", "framework", "model", "according to", "posits", "argues"],
    "EMPIRICAL": ["study", "research", "found", "effect", "correlation", "significant", "p<", "p =", "r=", "d="],
    "FACTUAL": ["total of", "number of", "consists of", "defined as", "participants", "sample", "data"],
    "INTERPRETIVE": ["suggests", "indicates", "implies", "may", "might", "could"],
    "SPECULATIVE": ["could potentially", "future", "might lead", "may result"],
    "METHODOLOGICAL": ["method", "methodology", "procedure", "protocol",
                       "design", "sampling", "instrument", "measure",
                       "validity", "reliability", "rigor"],
}


def _detect_overconfidence(text: str) -> bool:
    """Detect overconfidence patterns in text (lightweight check for US penalty).

    This is NOT the full Hallucination Firewall (see gra_validator.py).
    It only checks a subset of BLOCK/SOFTEN patterns for uncertainty scoring.
    """
    for pattern in _OVERCONFIDENCE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def classify_claim_type(claim: dict) -> str:
    """클레임 유형 분류"""
    # 명시적 유형이 있으면 사용
    if "claim_type" in claim and claim["claim_type"]:
        return claim["claim_type"]

    # 텍스트에서 자동 분류
    text = claim.get("text", "").lower()

    for claim_type, keywords in CLAIM_TYPE_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text:
                return claim_type

    return "FACTUAL"  # 기본값


def calculate_citation_score(claim: dict) -> float:
    """Citation Score (출처 품질) 계산"""
    sources = claim.get("sources", [])
    if not sources:
        return 0.0

    total_score = 0
    for source in sources:
        source_score = 0

        # 출처 유형
        source_type = source.get("type", "")
        if source_type == "PRIMARY":
            source_score += 40
        elif source_type == "SECONDARY":
            source_score += 25
        else:
            source_score += 10

        # 검증 여부
        if source.get("verified", False):
            source_score += 30

        # 참조 존재
        if source.get("reference"):
            source_score += 20

        # DOI 존재
        if source.get("doi"):
            source_score += 10

        total_score += min(source_score, 100)

    return min(total_score / len(sources), 100)


def calculate_grounding_score(claim: dict, research_type: str = "default") -> float:
    """Grounding Score (근거 품질) 계산"""
    text = claim.get("text", "")
    sources = claim.get("sources", [])
    score = 0

    # 출처 존재
    if sources:
        score += 30

    if research_type == "philosophical":
        # 철학적 근거 패턴 (통계 대신 논증적 근거)
        philosophical_patterns = [
            (r"(?:argues?|contends?|maintains?)\s+that", 15),  # 논증 인용
            (r"(?:entails?|implies?|follows?\s+from)", 15),    # 논리적 함의
            (r"(?:necessary|sufficient)\s+condition", 10),     # 필요/충분 조건
            (r"(?:prima\s+facie|a\s+priori|a\s+posteriori)", 10),  # 철학 용어
            (r"(?:premise|conclusion|therefore|thus)", 10),    # 논증 구조
            (r"(?:objection|reply|counter-?argument)", 10),    # 반론 구조
        ]
        for pattern, points in philosophical_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
    elif research_type == "qualitative":
        # 질적 연구 근거 패턴
        qualitative_patterns = [
            (r"(?:theme|thematic|code|coding|category)", 15),
            (r"(?:participant|informant|interviewee)\s+(?:reported|stated|described)", 15),
            (r"(?:thick\s+description|rich\s+description|detailed\s+account)", 10),
            (r"(?:triangulat|member\s+check|peer\s+debrief|audit\s+trail)", 10),
            (r"(?:saturat|data\s+saturation|theoretical\s+saturation)", 10),
            (r"(?:lived\s+experience|phenomeno|hermeneutic|narrative)", 10),
            (r"(?:quotation|verbatim|in\s+vivo\s+code)", 10),
            # Korean
            (r"(?:주제|테마|코드|범주)\s*(?:도출|발견|확인)", 15),
            (r"(?:참여자|면담자|응답자)\s*(?:보고|진술|기술)", 15),
            (r"(?:삼각측정|동료검토|감사추적)", 10),
        ]
        for pattern, points in qualitative_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
    elif research_type == "slr":
        # 체계적 문헌 고찰 근거 패턴
        slr_patterns = [
            (r"(?:PRISMA|systematic\s+review|meta-analysis)", 15),
            (r"(?:inclusion|exclusion)\s+criteria", 15),
            (r"(?:database|PubMed|Scopus|Web\s+of\s+Science)\s+search", 10),
            (r"(?:quality\s+assessment|risk\s+of\s+bias|GRADE)", 10),
            (r"(?:screening|selection)\s+(?:process|procedure)", 10),
            (r"(?:heterogeneity|I²|forest\s+plot|funnel\s+plot)", 10),
        ]
        for pattern, points in slr_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
    elif research_type == "mixed":
        # 혼합연구 근거 패턴 (양적+질적 모두 인정)
        mixed_patterns = [
            # Quantitative evidence
            (r"(?:p\s*[<>=]|effect\s+size|significant)", 10),
            (r"(?:\d+(?:\.\d+)?%|\d+\s*participants)", 10),
            # Qualitative evidence
            (r"(?:theme|code|participant\s+reported)", 10),
            (r"(?:triangulat|convergent|sequential)", 10),
            # Integration evidence (bonus)
            (r"(?:integrat|mixed|combin|converg)\s+(?:method|design|approach)", 15),
            (r"(?:quantitative|qualitative)\s+(?:strand|phase|component)", 10),
        ]
        for pattern, points in mixed_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += points
    else:
        # default/quantitative: 기존 empirical/statistical 분기
        claim_type = claim.get("claim_type", "") or classify_claim_type(claim)

        if claim_type in ("THEORETICAL", "INTERPRETIVE", "METHODOLOGICAL", "SPECULATIVE"):
            # Non-empirical grounding patterns
            theoretical_patterns = [
                (r"(?:according\s+to|as\s+described\s+by)\s+\w+", 15),
                (r"(?:theory|framework|model|paradigm)", 15),
                (r"(?:suggests?|indicates?|implies?)\s+that", 10),
                (r"(?:consistent\s+with|supports?)\s+\w+", 10),
                (r"(?:previous\s+research|prior\s+(?:studies|work|literature))", 10),
                (r"(?:conceptual|theoretical)\s+\w+", 10),
            ]
            for pattern, points in theoretical_patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    score += points
        else:
            # Empirical/statistical grounding (FACTUAL, EMPIRICAL)
            has_statistics = False
            if re.search(r"[rdb]=\s*-?\d+\.?\d*", text, re.IGNORECASE):
                score += 25
                has_statistics = True
            if re.search(r"p\s*[<>=]\s*\.?\d+", text, re.IGNORECASE):
                score += 20
                has_statistics = True

            # 구체적 표현
            if re.search(r"\d+(?:\.\d+)?%", text):
                score += 10
                has_statistics = True
            if re.search(r"\d+\s*(?:participants|samples|studies)", text, re.IGNORECASE):
                score += 15

            # Penalize: statistics present but no sources cited
            if has_statistics and not sources:
                score -= 15

    return max(0, min(score, 100))


def calculate_uncertainty_score(claim: dict) -> float:
    """Uncertainty Score (불확실성 표현) 계산"""
    text = claim.get("text", "")
    uncertainty = claim.get("uncertainty", "")
    score = 35  # 기본 점수 (reduced from 50: honest baseline)

    # 불확실성 명시
    if uncertainty:
        score += 30

    # 적절한 한정 표현 (English + Korean)
    hedging_patterns = [
        "suggests", "may", "might", "could", "possible", "likely", "tends to",
        "~일 수 있", "가능성", "경향", "일부", "대체로", "아마",
    ]
    for pattern in hedging_patterns:
        if pattern.lower() in text.lower():
            score += 10
            break

    # 조건부 표현
    if "if" in text.lower() or "when" in text.lower():
        score += 10

    # Penalize overconfidence (BLOCK/SOFTEN patterns → -20)
    if _detect_overconfidence(text):
        score -= 20

    return max(0, min(score, 100))


def calculate_verifiability_score(claim: dict, research_type: str = "default") -> float:
    """Verifiability Score (검증가능성) 계산"""
    sources = claim.get("sources", [])
    if not sources:
        return 20.0

    total_score = 0
    for source in sources:
        source_score = 20

        # DOI 존재
        if source.get("doi"):
            source_score += 40
            # Common bonuses for DOI sources
            if source.get("verified", False):
                source_score += 30
            ref = source.get("reference", "")
            if re.search(r"\d{4}", ref):
                source_score += 10
            if len(ref) > 30:
                source_score += 5
        elif research_type == "philosophical":
            # 철학 원전은 DOI가 없어도 판본/번역 정보로 검증 가능
            ref = source.get("reference", "")
            if re.search(r"\d{4}", ref):  # 연도
                source_score += 20
            if len(ref) > 30:  # 상세 서지정보
                source_score += 15
            if source.get("verified", False):
                source_score += 25
        else:
            # Non-DOI, non-philosophical fallback
            if source.get("verified", False):
                source_score += 30
            ref = source.get("reference", "")
            if re.search(r"\d{4}", ref):
                source_score += 10
            if len(ref) > 30:
                source_score += 5

        total_score += min(source_score, 100)

    return min(total_score / len(sources), 100)


def calculate_weighted_srcs(scores: dict, research_type: str = "default") -> float:
    """가중치 적용 종합 점수 계산"""
    weights = get_srcs_weights(research_type)
    weighted = 0
    for axis, weight in weights.items():
        weighted += scores.get(axis, 0) * weight
    return round(weighted, 1)


def check_threshold(scores: dict, threshold: float = DEFAULT_THRESHOLD, research_type: str = "default") -> dict:
    """임계값 확인"""
    total = calculate_weighted_srcs(scores, research_type)
    return {
        "passed": total >= threshold,
        "total": total,
        "threshold": threshold,
        "margin": round(total - threshold, 1),
    }


def evaluate_claim(claim: dict, research_type: str = "default") -> dict:
    """개별 클레임 SRCS 평가"""
    scores = {
        "cs": calculate_citation_score(claim),
        "gs": calculate_grounding_score(claim, research_type),
        "us": calculate_uncertainty_score(claim),
        "vs": calculate_verifiability_score(claim, research_type),
    }
    scores["total"] = calculate_weighted_srcs(scores, research_type)

    return {
        "id": claim.get("id", "UNKNOWN"),
        "text": claim.get("text", "")[:100] + "..." if len(claim.get("text", "")) > 100 else claim.get("text", ""),
        "claim_type": classify_claim_type(claim),
        "scores": scores,
        "passed": scores["total"] >= DEFAULT_THRESHOLD,
    }


def evaluate_all_claims(claims: list[dict], threshold: float = DEFAULT_THRESHOLD, research_type: str = "default") -> dict:
    """전체 클레임 평가"""
    evaluated = []
    below_threshold = []
    by_type: dict[str, dict] = {}

    for claim in claims:
        result = evaluate_claim(claim, research_type)
        evaluated.append(result)

        claim_type = result["claim_type"]
        if claim_type not in by_type:
            by_type[claim_type] = {"count": 0, "total_score": 0, "scores": []}
        by_type[claim_type]["count"] += 1
        by_type[claim_type]["total_score"] += result["scores"]["total"]
        by_type[claim_type]["scores"].append(result["scores"]["total"])

        if result["scores"]["total"] < threshold:
            below_threshold.append({
                "id": result["id"],
                "score": result["scores"]["total"],
                "claim_type": claim_type,
                "text": result["text"],
            })

    # 유형별 평균 계산
    for claim_type, data in by_type.items():
        data["avg_score"] = round(data["total_score"] / max(data["count"], 1), 1)
        del data["total_score"]
        del data["scores"]

    # 전체 점수 계산
    if evaluated:
        overall_cs = sum(e["scores"]["cs"] for e in evaluated) / len(evaluated)
        overall_gs = sum(e["scores"]["gs"] for e in evaluated) / len(evaluated)
        overall_us = sum(e["scores"]["us"] for e in evaluated) / len(evaluated)
        overall_vs = sum(e["scores"]["vs"] for e in evaluated) / len(evaluated)
        overall_total = sum(e["scores"]["total"] for e in evaluated) / len(evaluated)
    else:
        overall_cs = overall_gs = overall_us = overall_vs = overall_total = 0

    overall_scores = {
        "cs": round(overall_cs, 1),
        "gs": round(overall_gs, 1),
        "us": round(overall_us, 1),
        "vs": round(overall_vs, 1),
        "total": round(overall_total, 1),
    }

    passed_count = len([e for e in evaluated if e["passed"]])
    pass_rate = round(passed_count / max(len(evaluated), 1) * 100, 1)

    return {
        "evaluation_date": datetime.now().strftime("%Y-%m-%d"),
        "total_claims": len(claims),
        "evaluated_claims": evaluated,
        "by_type": by_type,
        "overall_scores": overall_scores,
        "pass_rate": pass_rate,
        "below_threshold": below_threshold,
        "grade": assign_grade(overall_total),
    }


def assign_grade(score: float) -> str:
    """등급 부여 (SOT-A: SRCS_GRADE_BANDS)"""
    for grade in ("A", "B", "C", "D"):
        if score >= SRCS_GRADE_BANDS[grade]:
            return grade
    return "F"


def generate_summary(result: dict, output_path: Path) -> None:
    """srcs-summary.json 생성"""
    summary = {
        "evaluation_date": result.get("evaluation_date", datetime.now().strftime("%Y-%m-%d")),
        "total_claims": result.get("total_claims", 0),
        "by_type": result.get("by_type", {}),
        "overall_scores": result.get("overall_scores", {}),
        "pass_rate": result.get("pass_rate", 0),
        "below_threshold": result.get("below_threshold", []),
        "inconsistencies": result.get("inconsistencies", []),
        "grade": result.get("grade", "F"),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False))


def generate_quality_report(result: dict, output_path: Path) -> None:
    """quality-report.md 생성"""
    overall = result.get("overall_scores", {})
    by_type = result.get("by_type", {})
    below = result.get("below_threshold", [])
    inconsistencies = result.get("inconsistencies", [])

    lines = [
        "# 학술적 품질 보고서",
        "",
        "## 1. 평가 개요",
        f"- 평가 일시: {result.get('evaluation_date', 'N/A')}",
        f"- 총 클레임 수: {result.get('total_claims', 0)}",
        f"- 평가 에이전트: 15개",
        "",
        "## 2. SRCS 점수 요약",
        "| 축 | 점수 | 등급 |",
        "|----|------|------|",
        f"| CS (출처) | {overall.get('cs', 0)} | {_axis_grade(overall.get('cs', 0))} |",
        f"| GS (근거) | {overall.get('gs', 0)} | {_axis_grade(overall.get('gs', 0))} |",
        f"| US (불확실성) | {overall.get('us', 0)} | {_axis_grade(overall.get('us', 0))} |",
        f"| VS (검증가능성) | {overall.get('vs', 0)} | {_axis_grade(overall.get('vs', 0))} |",
        f"| **종합** | **{overall.get('total', 0)}** | **{result.get('grade', 'F')}** |",
        "",
        "## 3. 클레임 유형별 분석",
        "| 유형 | 수 | 평균 점수 | 통과율 |",
        "|------|---|----------|--------|",
    ]

    for claim_type, data in by_type.items():
        count = data.get("count", 0)
        avg = data.get("avg_score", 0)
        pass_pct = "N/A"
        lines.append(f"| {claim_type} | {count} | {avg} | {pass_pct} |")

    lines.extend([
        "",
        "## 4. 교차 일관성 검사",
        "### 4.1 발견된 불일치",
    ])

    if inconsistencies:
        lines.append("| 에이전트 1 | 에이전트 2 | 내용 | 해결 방안 |")
        lines.append("|-----------|-----------|------|----------|")
        for inc in inconsistencies[:5]:
            lines.append(f"| {inc.get('agent1', 'N/A')} | {inc.get('agent2', 'N/A')} | {inc.get('topic', 'N/A')} | 검토 필요 |")
    else:
        lines.append("불일치 없음")

    lines.extend([
        "",
        "### 4.2 일관성 점수",
        f"[{result.get('consistency_score', 100)}/100]",
        "",
        "## 5. 임계값 미달 클레임",
    ])

    if below:
        lines.append("| ID | 점수 | 문제 | 권고 |")
        lines.append("|----|------|------|------|")
        for item in below[:10]:
            lines.append(f"| {item.get('id')} | {item.get('score')} | 임계값 미달 | 출처 보강 |")
    else:
        lines.append("모든 클레임이 임계값을 통과했습니다.")

    # 최종 판정
    grade = result.get("grade", "F")
    if grade in ["A", "B"]:
        verdict = "✅ 통과"
    elif grade == "C":
        verdict = "⚠️ 조건부"
    else:
        verdict = "❌ 재검토"

    lines.extend([
        "",
        "## 6. 최종 판정",
        f"- **등급**: {grade}",
        f"- **통과 여부**: {verdict}",
        "",
        "## 7. 권고사항",
    ])

    if grade in ["A", "B"]:
        lines.append("### 7.1 즉시 수정 필요")
        lines.append("- 없음")
        lines.append("### 7.2 개선 권장")
        lines.append("- 일부 클레임의 출처 보강 권장")
    else:
        lines.append("### 7.1 즉시 수정 필요")
        lines.append("- 임계값 미달 클레임 수정")
        lines.append("- 출처 없는 주장에 참고문헌 추가")
        lines.append("### 7.2 개선 권장")
        lines.append("- 불확실성 표현 보강")
        lines.append("- DOI 추가로 검증가능성 향상")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines))


def _axis_grade(score: float) -> str:
    """축별 등급 (SOT-A: SRCS_AXIS_GRADE_BANDS)"""
    for grade in ("A", "B"):
        if score >= SRCS_AXIS_GRADE_BANDS[grade]:
            return grade
    return "C"


def _read_research_type(temp_dir: Path) -> str:
    """Read research type from session.json near the temp directory."""
    # session.json lives in 00-session/ which is a sibling of _temp/
    for candidate in [
        temp_dir.parent / "00-session" / "session.json",
        temp_dir / ".." / "00-session" / "session.json",
    ]:
        resolved = candidate.resolve()
        if resolved.is_file():
            try:
                data = json.loads(resolved.read_text(encoding="utf-8"))
                return data.get("research", {}).get("type", "default") or "default"
            except (json.JSONDecodeError, OSError):
                pass
    return "default"


def run_srcs_evaluation(temp_dir: Path, save_outputs: bool = True, research_type: str | None = None) -> dict:
    """전체 SRCS 평가 실행"""
    # Determine research type from parameter or session.json
    if research_type is None:
        research_type = _read_research_type(temp_dir)

    # 모든 파일에서 클레임 수집
    all_claims = []
    md_files = list(temp_dir.glob("*.md"))

    for file_path in md_files:
        claims = extract_claims_from_file(file_path)
        for claim in claims:
            claim["source_file"] = file_path.name
        all_claims.extend(claims)

    # 평가 실행
    result = evaluate_all_claims(all_claims, research_type=research_type)

    # 결과 저장
    if save_outputs:
        generate_summary(result, temp_dir / "srcs-summary.json")
        generate_quality_report(result, temp_dir / "quality-report.md")

    return result


def main():
    """CLI 엔트리포인트"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: srcs_evaluator.py <temp_dir>")
        sys.exit(1)

    temp_dir = Path(sys.argv[1])
    result = run_srcs_evaluation(temp_dir)

    print(f"Total Claims: {result['total_claims']}")
    print(f"Overall Score: {result['overall_scores']['total']}/100")
    print(f"Grade: {result['grade']}")
    print(f"Pass Rate: {result['pass_rate']}%")


if __name__ == "__main__":
    main()
