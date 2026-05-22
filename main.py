# 메인 진입점

import os
import sys
import json
from typing import Dict, Any

# 현재 경로를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graphs.job_graph import run_job_search_workflow
from utils.output_formatter import (
    save_results_as_json,
    save_results_as_csv,
    generate_markdown_report,
    print_table_format,
)
from models.schemas import UserProfile

"""
[🔟 main.py - 실행 예시]

사용자가 입력한 검색어와 이력을 기반으로 전체 워크플로우 실행
"""


def load_user_profile(filepath: str = None) -> Dict[str, Any]:
    """
    사용자 이력 로드 (JSON 파일 또는 기본값)
    
    Args:
        filepath: 사용자 이력 JSON 파일 경로
    
    Returns:
        사용자 프로필 딕셔너리
    """
    
    # 기본 사용자 프로필 (테스트용)
    default_profile = {
        "name": "홍길동",
        "skills": ["Python", "SQL", "FastAPI", "LangChain"],
        "certifications": ["정보처리기사"],
        "preferred_employment_types": ["정규직", "계약직"],
        "preferred_locations": ["서울", "경기"],
        "education": "학사",
        "career_level": "신입",
        "interested_jobs": ["AI 개발자", "백엔드 개발자"],
    }
    
    if filepath and os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                user_profile = json.load(f)
            print(f"✓ 사용자 이력 로드: {filepath}")
            return user_profile
        except Exception as e:
            print(f"⚠️  파일 로드 실패: {e}")
            print("기본 프로필 사용")
            return default_profile
    
    return default_profile


def get_user_input() -> tuple[str, Dict]:
    """
    콘솔에서 사용자 입력 받기
    
    Returns:
        (검색어, 사용자 프로필)
    """
    
    print("\n" + "=" * 80)
    print("📝 사람인 구인공고 필터링 시스템")
    print("=" * 80)
    
    # 사용자 선택: 기본값 사용 vs 파일 로드 vs 수동 입력
    print("\n[옵션 선택]")
    print("1. 기본 프로필 사용 (테스트)")
    print("2. JSON 파일에서 로드")
    print("3. 수동 입력")
    
    choice = input("선택 (1/2/3): ").strip()
    
    if choice == "2":
        filepath = input("이력 파일 경로 (data/user_profile.json): ").strip()
        if not filepath:
            filepath = "data/user_profile.json"
        user_profile = load_user_profile(filepath)
    elif choice == "3":
        print("\n[사용자 정보 입력]")
        user_profile = {
            "name": input("이름: ") or "사용자",
            "skills": input("보유 기술 (쉼표 구분): ").split(","),
            "certifications": input("자격증 (쉼표 구분): ").split(","),
            "preferred_employment_types": input("희망 근무형태 (정규직, 계약직 등): ").split(","),
            "preferred_locations": input("희망 지역 (쉼표 구분): ").split(","),
            "education": input("최종 학력 (고졸/초대졸/학사/석사): ") or "학사",
            "career_level": input("경력 (신입/1~3년/3~5년 등): ") or "신입",
            "interested_jobs": input("관심 직무 (쉼표 구분): ").split(","),
        }
    else:
        user_profile = load_user_profile()
    
    # 검색어 입력
    print("\n[검색 직무 입력]")
    keyword = input("검색할 직무 (예: AI 개발자, 백엔드 개발자): ").strip()
    
    if not keyword:
        keyword = "AI 개발자"
        print(f"기본값 사용: {keyword}")
    
    return keyword, user_profile


def main():
    """
    메인 실행 함수
    """
    
    # [1] 사용자 입력
    keyword, user_profile = get_user_input()
    
    print(f"\n검색어: {keyword}")
    print(f"사용자: {user_profile.get('name', '미지정')}")
    print(f"보유 기술: {', '.join(user_profile.get('skills', []))}")
    
    # [2] 워크플로우 실행
    try:
        final_state = run_job_search_workflow(keyword, user_profile)
        
        # [3] 결과 처리
        evaluation_results = final_state.get("evaluation_results", [])
        summary = final_state.get("summary", {})
        
        if not evaluation_results:
            print("\n⚠️  평가 결과가 없습니다")
            return
        
        # [4] 결과 저장
        print("\n[결과 저장 중...]")
        
        # JSON 저장
        json_path = save_results_as_json(evaluation_results, summary)
        
        # CSV 저장
        csv_path = save_results_as_csv(evaluation_results)
        
        # 마크다운 보고서 저장
        md_path = generate_markdown_report(user_profile, evaluation_results, summary)
        
        # [5] 콘솔 출력
        print_table_format(evaluation_results, limit=10)
        
        # [6] 저장 위치 출력
        print("\n" + "=" * 80)
        print("📁 결과 저장 완료")
        print("=" * 80)
        print(f"- JSON: {json_path}")
        print(f"- CSV: {csv_path}")
        print(f"- 보고서: {md_path}")
        print("\n✓ 프로그램 종료")
        
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


def demo_mode():
    """
    데모 모드: 입력 없이 자동 실행
    """
    
    print("\n🎬 데모 모드 실행...")
    
    # 테스트 사용자 프로필
    user_profile = {
        "name": "홍길동",
        "skills": ["Python", "LangChain", "SQL", "FastAPI"],
        "certifications": ["정보처리기사"],
        "preferred_employment_types": ["정규직"],
        "preferred_locations": ["서울", "경기"],
        "education": "학사",
        "career_level": "신입",
        "interested_jobs": ["AI 개발자", "백엔드 개발자"],
    }
    
    keyword = "AI 개발자"
    
    # 워크플로우 실행
    final_state = run_job_search_workflow(keyword, user_profile)
    
    # 결과
    evaluation_results = final_state.get("evaluation_results", [])
    summary = final_state.get("summary", {})
    
    if evaluation_results:
        save_results_as_json(evaluation_results, summary)
        save_results_as_csv(evaluation_results)
        generate_markdown_report(user_profile, evaluation_results, summary)
        print_table_format(evaluation_results)


if __name__ == "__main__":
    import sys
    
    # 명령줄 인자 확인
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_mode()
    else:
        sys.exit(main())

"""
====== 실행 방법 ======

[1] 대화형 모드 (기본값)
    python main.py
    
    사용자가 직무와 이력을 입력받음
    결과를 JSON, CSV, Markdown으로 저장
    콘솔에 테이블 형식으로 출력

[2] 데모 모드
    python main.py --demo
    
    미리 설정된 사용자로 자동 실행
    테스트/프리뷰용

[3] 프로그래밍 방식
    from graphs.job_graph import run_job_search_workflow
    
    user_profile = {...}
    final_state = run_job_search_workflow("AI 개발자", user_profile)
    
    evaluation_results = final_state["evaluation_results"]
    summary = final_state["summary"]
"""
