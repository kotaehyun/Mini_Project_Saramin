# 결과 포맷팅 및 저장

import json
import os
from typing import Dict, List, Any
from datetime import datetime
import csv

"""
평가 결과를 다양한 형식으로 저장 및 포맷팅
"""


def save_results_as_json(
    evaluation_results: List[Dict],
    summary: Dict,
    output_dir: str = "data/results"
) -> str:
    """
    JSON 형식으로 결과 저장
    
    Args:
        evaluation_results: 평가 결과 리스트
        summary: 요약 정보
        output_dir: 저장 디렉토리
    
    Returns:
        저장된 파일 경로
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_results_{timestamp}.json"
    filepath = os.path.join(output_dir, filename)
    
    output_data = {
        "timestamp": datetime.now().isoformat(),
        "total_jobs": len(evaluation_results),
        "evaluations": evaluation_results,
        "summary": summary,
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"✓ JSON 저장: {filepath}")
    return filepath


def save_results_as_csv(
    evaluation_results: List[Dict],
    output_dir: str = "data/results"
) -> str:
    """
    CSV 형식으로 결과 저장 (간단한 표 형식)
    
    Args:
        evaluation_results: 평가 결과 리스트
        output_dir: 저장 디렉토리
    
    Returns:
        저장된 파일 경로
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"evaluation_results_{timestamp}.csv"
    filepath = os.path.join(output_dir, filename)
    
    if not evaluation_results:
        print("⚠️  저장할 결과가 없습니다")
        return filepath
    
    # CSV 컬럼 정의
    fieldnames = [
        "번호",
        "회사명",
        "직무명",
        "적합도점수",
        "판정",
        "지원추천",
        "일치스킬",
        "부족핵심스킬",
        "부족우대스킬",
        "부족자격증",
        "최종판단",
        "URL",
    ]
    
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in evaluation_results:
            writer.writerow({
                "번호": result.get("index", ""),
                "회사명": result.get("company", ""),
                "직무명": result.get("title", ""),
                "적합도점수": result.get("fit_score", ""),
                "판정": result.get("result", ""),
                "지원추천": result.get("apply_level", ""),
                "일치스킬": ", ".join(result.get("matched_skills", [])),
                "부족핵심스킬": ", ".join(result.get("missing_core_skills", [])),
                "부족우대스킬": ", ".join(result.get("missing_optional_skills", [])),
                "부족자격증": ", ".join(result.get("missing_certs", [])),
                "최종판단": result.get("reason", ""),
                "URL": result.get("url", ""),
            })
    
    print(f"✓ CSV 저장: {filepath}")
    return filepath


def generate_markdown_report(
    user_profile: Dict,
    evaluation_results: List[Dict],
    summary: Dict,
    output_dir: str = "data/results"
) -> str:
    """
    마크다운 형식의 상세 보고서 생성
    
    Args:
        user_profile: 사용자 정보
        evaluation_results: 평가 결과
        summary: 요약 정보
        output_dir: 저장 디렉토리
    
    Returns:
        저장된 파일 경로
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{timestamp}.md"
    filepath = os.path.join(output_dir, filename)
    
    md_content = []
    
    # 헤더
    md_content.append("# 📋 구인공고 필터링 평가 보고서\n")
    md_content.append(f"**평가 일시**: {datetime.now().strftime('%Y년 %m월 %d일 %H:%M:%S')}\n")
    
    # 사용자 정보
    md_content.append("## 👤 사용자 정보\n")
    md_content.append(f"- **이름**: {user_profile.get('name', '미지정')}\n")
    md_content.append(f"- **경력**: {user_profile.get('career_level', '미지정')}\n")
    md_content.append(f"- **학력**: {user_profile.get('education', '미지정')}\n")
    md_content.append(f"- **보유 기술**: {', '.join(user_profile.get('skills', []))}\n")
    md_content.append(f"- **자격증**: {', '.join(user_profile.get('certifications', []))}\n")
    md_content.append(f"- **희망 지역**: {', '.join(user_profile.get('preferred_locations', []))}\n")
    md_content.append(f"- **희망 형태**: {', '.join(user_profile.get('preferred_employment_types', []))}\n\n")
    
    # 통계
    md_content.append("## 📊 평가 통계\n")
    md_content.append(f"- **총 평가 공고**: {summary.get('total_jobs_evaluated', len(evaluation_results))}개\n")
    
    stats = summary.get("statistics", {})
    md_content.append(f"- **적합**: {stats.get('by_result', {}).get('적합', 0)}개\n")
    md_content.append(f"- **보완필요**: {stats.get('by_result', {}).get('보완필요', 0)}개\n")
    md_content.append(f"- **부적합**: {stats.get('by_result', {}).get('부적합', 0)}개\n\n")
    
    # 지원 추천도
    success = summary.get("success_rate", {})
    md_content.append("## 🎯 지원 추천도\n")
    md_content.append(f"- **즉시지원 가능**: {success.get('immediate_apply', 0)}개 ({success.get('immediate_rate_percent', 0)}%)\n")
    md_content.append(f"- **보완 후 지원**: {success.get('with_preparation', 0)}개 ({success.get('apply_possible_rate_percent', 0)}%)\n\n")
    
    # 추천 공고
    md_content.append("## ⭐ 추천 공고 TOP 3\n\n")
    for job in summary.get("recommended_jobs", []):
        md_content.append(f"### {job['rank']}. {job['company']} - {job['title']}\n")
        md_content.append(f"- **적합도**: {job['fit_score']}/100\n")
        md_content.append(f"- **추천**: {job['apply_level']}\n")
        if job.get("url"):
            md_content.append(f"- **링크**: [{job['title']}]({job['url']})\n\n")
    
    # 부족 스킬
    md_content.append("## 🚀 자주 부족한 기술\n\n")
    md_content.append("### 핵심 스킬\n")
    for skill in summary.get("top_missing_skills", {}).get("core", [])[:5]:
        md_content.append(f"- **{skill['skill']}**: {skill['count']}개 공고에서 요구\n")
    
    # 학습 계획
    md_content.append("\n## 📚 추천 학습 계획\n\n")
    for phase in summary.get("learning_recommendations", {}).get("recommended_path", []):
        md_content.append(f"### Phase {phase.get('phase')}: {phase.get('name', '')}\n")
        md_content.append(f"**예상 기간**: {phase.get('duration', '')}\n")
        if phase.get("priority_skills"):
            md_content.append(f"**학습 대상**: {', '.join(phase['priority_skills'])}\n")
        md_content.append(f"{phase.get('description', '')}\n\n")
    
    # 상세 평가 결과
    md_content.append("## 📝 상세 평가 결과\n\n")
    for result in evaluation_results[:5]:  # 상위 5개만
        md_content.append(f"### {result.get('index')}. {result.get('company')} - {result.get('title')}\n")
        md_content.append(f"- **점수**: {result.get('fit_score')}/100\n")
        md_content.append(f"- **판정**: {result.get('result')}\n")
        md_content.append(f"- **이유**: {result.get('reason', '미기재')}\n")
        md_content.append(f"- **일치 기술**: {', '.join(result.get('matched_skills', []))}\n")
        md_content.append(f"- **부족 기술**: {', '.join(result.get('missing_core_skills', []))}\n\n")
    
    # 파일 저장
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("".join(md_content))
    
    print(f"✓ 마크다운 보고서 저장: {filepath}")
    return filepath


def print_table_format(
    evaluation_results: List[Dict],
    limit: int = 10
):
    """
    콘솔 테이블 형식으로 결과 출력
    """
    
    print("\n" + "=" * 150)
    print(f"{'순번':<5} {'회사':<20} {'직무':<20} {'적합':<8} {'점수':<6} {'추천':<12} {'일치 스킬':<30}")
    print("=" * 150)
    
    for idx, result in enumerate(evaluation_results[:limit], 1):
        print(
            f"{result.get('index', idx):<5} "
            f"{result.get('company', '')[:18]:<20} "
            f"{result.get('title', '')[:18]:<20} "
            f"{result.get('result', ''):<8} "
            f"{result.get('fit_score', 0):<6} "
            f"{result.get('apply_level', ''):<12} "
            f"{', '.join(result.get('matched_skills', []))[:28]:<30}"
        )
    
    print("=" * 150)
