# 요약 체인: 전체 결과 분석 및 추천

from typing import List, Dict, Any
from collections import Counter
import json

"""
최종 요약: 전체 결과를 분석하여 통계, 부족 스킬, 학습 계획 제시
"""


def summarize_results(
    user_profile: Dict[str, Any],
    evaluation_results: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    평가 결과를 종합 분석
    
    Args:
        user_profile: 사용자 이력
        evaluation_results: LLM 평가 결과 리스트
    
    Returns:
        요약 정보:
        - fit_category_count: 적합/보완필요/부적합 개수
        - recommended_jobs: 추천 공고 (상위 3개)
        - top_missing_skills: 자주 부족한 스킬
        - learning_path: 학습 우선순위
        - success_rate: 지원 가능 비율
    """
    
    print("\n[요약] 전체 결과 분석 중...")
    
    summary = {
        "total_jobs_evaluated": len(evaluation_results),
        "statistics": {},
        "recommended_jobs": [],
        "top_missing_skills": [],
        "top_missing_certs": [],
        "learning_recommendations": {},
        "success_rate": 0,
    }
    
    if not evaluation_results:
        return summary
    
    # 1. 카테고리별 개수 집계
    result_counts = Counter()
    apply_level_counts = Counter()
    
    for eval_result in evaluation_results:
        result_counts[eval_result.get("result", "미분류")] += 1
        apply_level_counts[eval_result.get("apply_level", "미분류")] += 1
    
    summary["statistics"]["by_result"] = dict(result_counts)
    summary["statistics"]["by_apply_level"] = dict(apply_level_counts)
    
    # 2. 추천 공고 (fit_score 상위 3개)
    sorted_jobs = sorted(
        evaluation_results,
        key=lambda x: x.get("fit_score", 0),
        reverse=True
    )
    
    summary["recommended_jobs"] = [
        {
            "rank": idx + 1,
            "company": job.get("company", "미상"),
            "title": job.get("title", "공고명 미상"),
            "fit_score": job.get("fit_score", 0),
            "apply_level": job.get("apply_level", "미분류"),
            "url": job.get("url"),
        }
        for idx, job in enumerate(sorted_jobs[:3])
    ]
    
    # 3. 자주 부족한 스킬 분석
    all_missing_core = []
    all_missing_optional = []
    
    for eval_result in evaluation_results:
        all_missing_core.extend(
            eval_result.get("missing_core_skills", [])
        )
        all_missing_optional.extend(
            eval_result.get("missing_optional_skills", [])
        )
    
    # 중복 제거 및 빈도순 정렬
    core_skill_counts = Counter(all_missing_core)
    optional_skill_counts = Counter(all_missing_optional)
    
    summary["top_missing_skills"] = {
        "core": [
            {"skill": skill, "count": count}
            for skill, count in core_skill_counts.most_common(5)
        ],
        "optional": [
            {"skill": skill, "count": count}
            for skill, count in optional_skill_counts.most_common(5)
        ]
    }
    
    # 4. 자주 부족한 자격증
    all_missing_certs = []
    for eval_result in evaluation_results:
        all_missing_certs.extend(
            eval_result.get("missing_certs", [])
        )
    
    cert_counts = Counter(all_missing_certs)
    summary["top_missing_certs"] = [
        {"cert": cert, "count": count}
        for cert, count in cert_counts.most_common(3)
    ]
    
    # 5. 학습 우선순위
    # 각 공고의 study_priority를 합쳐서 빈도순 정렬
    all_study_priorities = []
    for eval_result in evaluation_results:
        all_study_priorities.extend(
            eval_result.get("study_priority", [])
        )
    
    study_priority_counts = Counter(all_study_priorities)
    summary["learning_recommendations"]["priority_skills"] = [
        {"skill": skill, "frequency": count}
        for skill, count in study_priority_counts.most_common(10)
    ]
    
    # 6. 지원 성공률
    apply_count = apply_level_counts.get("즉시지원", 0)
    apply_support_count = apply_level_counts.get("보완후지원", 0)
    total = len(evaluation_results)
    
    if total > 0:
        summary["success_rate"] = {
            "immediate_apply": apply_count,
            "with_preparation": apply_support_count,
            "not_recommended": apply_level_counts.get("비추천", 0),
            "immediate_rate_percent": round((apply_count / total) * 100, 1),
            "apply_possible_rate_percent": round(
                ((apply_count + apply_support_count) / total) * 100, 1
            ),
        }
    
    # 7. 학습 경로 제안
    summary["learning_recommendations"]["recommended_path"] = _generate_learning_path(
        user_profile,
        summary["top_missing_skills"]["core"],
        summary["top_missing_certs"]
    )
    
    print("✓ 요약 완료")
    return summary


def _generate_learning_path(
    user_profile: Dict[str, Any],
    missing_core_skills: List[Dict],
    missing_certs: List[Dict]
) -> List[Dict]:
    """
    사용자 맞춤형 학습 계획 생성
    
    Returns:
        {
            "phase": 1,
            "name": "기초 스킬",
            "duration": "1-2주",
            "tasks": [...]
        }
    """
    
    path = []
    
    # Phase 1: 핵심 부족 스킬
    if missing_core_skills:
        path.append({
            "phase": 1,
            "name": "핵심 기술 학습",
            "duration": "2-4주",
            "priority_skills": [s["skill"] for s in missing_core_skills[:3]],
            "reason": "90% 이상의 공고에서 요구하는 핵심 기술",
        })
    
    # Phase 2: 우대사항
    path.append({
        "phase": 2,
        "name": "우대사항 기술 학습",
        "duration": "2-3주",
        "description": "채용 경쟁력 상승",
    })
    
    # Phase 3: 자격증
    if missing_certs:
        path.append({
            "phase": 3,
            "name": "자격증 준비",
            "duration": "4-6주",
            "priority_certs": [c["cert"] for c in missing_certs[:2]],
            "description": "자격요건 충족",
        })
    
    # Phase 4: 포트폴리오
    path.append({
        "phase": 4,
        "name": "포트폴리오 구성",
        "duration": "2-3주",
        "description": "학습한 기술 기반 실제 프로젝트 제작",
    })
    
    return path


def print_summary(summary: Dict[str, Any]):
    """
    요약 정보 출력 (콘솔용 포맷)
    """
    
    print("\n" + "=" * 80)
    print("📊 [평가 요약]")
    print("=" * 80)
    
    print(f"\n✓ 총 평가 공고: {summary['total_jobs_evaluated']}개")
    
    # 카테고리별 통계
    print("\n[결과 분류]")
    for result_type, count in summary["statistics"].get("by_result", {}).items():
        print(f"  {result_type}: {count}개")
    
    # 지원 추천
    print("\n[지원 추천도]")
    success_info = summary.get("success_rate", {})
    print(f"  즉시지원 가능: {success_info.get('immediate_apply', 0)}개 ({success_info.get('immediate_rate_percent', 0)}%)")
    print(f"  보완 후 지원: {success_info.get('with_preparation', 0)}개 ({success_info.get('apply_possible_rate_percent', 0)}%)")
    
    # 추천 공고
    print("\n[추천 공고 TOP 3]")
    for job in summary["recommended_jobs"]:
        print(f"  {job['rank']}. {job['company']} - {job['title']} (점수: {job['fit_score']}/100)")
    
    # 부족 스킬
    print("\n[자주 부족한 핵심 스킬]")
    for skill_info in summary["top_missing_skills"]["core"][:3]:
        print(f"  {skill_info['skill']}: {skill_info['count']}개 공고에서 요구")
    
    # 학습 계획
    print("\n[추천 학습 계획]")
    for phase in summary["learning_recommendations"].get("recommended_path", []):
        print(f"  Phase {phase['phase']}: {phase['name']} ({phase['duration']})")
        if "priority_skills" in phase:
            print(f"    → {', '.join(phase['priority_skills'])}")
    
    print("\n" + "=" * 80)
