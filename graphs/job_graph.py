# LangGraph 기반 전체 워크플로우

from langgraph.graph import StateGraph, END
from typing import Dict, List, Any, TypedDict
from crawlers.saramin_crawler import crawl_saramin_jobs
from chains.preprocess_chain import run_preprocess_pipeline
from chains.filter_chain import evaluate_jobs
from chains.summary_chain import summarize_results, print_summary
import json

"""
[9️⃣ LangGraph 워크플로우]

전체 흐름을 상태 기반으로 제어

START
  ↓
[노드 1] crawl_jobs_node: 크롤링
  ↓
[노드 2] preprocess_jobs_node: 전처리
  ↓
[노드 3] filter_jobs_node: LLM 필터링
  ↓
[노드 4] summarize_result_node: 요약
  ↓
END
"""


class JobSearchState(TypedDict):
    """그래프의 상태 (state)"""
    
    # 입력
    keyword: str
    user_profile: Dict[str, Any]
    
    # 중간 결과
    raw_jobs: List[Dict[str, Any]]
    processed_jobs: List[Dict[str, Any]]
    evaluation_results: List[Dict[str, Any]]
    
    # 최종 결과
    summary: Dict[str, Any]
    error: str


def create_job_search_graph():
    """
    LangGraph 워크플로우 생성
    """
    
    # [1] 상태 그래프 초기화
    workflow = StateGraph(JobSearchState)
    
    # [2] 노드 정의
    workflow.add_node("crawl_jobs", crawl_jobs_node)
    workflow.add_node("preprocess_jobs", preprocess_jobs_node)
    workflow.add_node("filter_jobs", filter_jobs_node)
    workflow.add_node("summarize_results", summarize_result_node)
    
    # [3] 엣지 (노드 간 연결) 정의
    workflow.add_edge("crawl_jobs", "preprocess_jobs")
    workflow.add_edge("preprocess_jobs", "filter_jobs")
    workflow.add_edge("filter_jobs", "summarize_results")
    workflow.add_edge("summarize_results", END)
    
    # [4] 진입점 설정
    workflow.set_entry_point("crawl_jobs")
    
    # [5] 그래프 컴파일
    graph = workflow.compile()
    
    return graph


# ====== 노드 함수들 ======

def crawl_jobs_node(state: JobSearchState) -> JobSearchState:
    """
    [노드 1] 크롤링
    
    - URL 자동 생성
    - BeautifulSoup 크롤링
    - 공고 상세 URL 추출
    """
    
    print("\n" + "=" * 80)
    print("🔍 [노드 1] 크롤링 시작")
    print("=" * 80)
    
    keyword = state["keyword"]
    
    try:
        # 크롤링 실행
        raw_jobs = crawl_saramin_jobs(keyword, max_pages=2)
        
        state["raw_jobs"] = raw_jobs
        state["error"] = ""
        
        print(f"✓ {len(raw_jobs)}개 공고 크롤링 완료")
        
    except Exception as e:
        print(f"❌ 크롤링 오류: {e}")
        state["raw_jobs"] = []
        state["error"] = f"크롤링 실패: {str(e)}"
    
    return state


def preprocess_jobs_node(state: JobSearchState) -> JobSearchState:
    """
    [노드 2] 전처리
    
    - 빈값 제거
    - 중복 제거
    - 필드 정제
    - LLM용 텍스트 생성
    """
    
    print("\n" + "=" * 80)
    print("🔄 [노드 2] 전처리 시작")
    print("=" * 80)
    
    raw_jobs = state["raw_jobs"]
    
    if not raw_jobs:
        print("⚠️  크롤링된 공고가 없습니다")
        state["processed_jobs"] = []
        state["error"] = "크롤링 결과 없음"
        return state
    
    try:
        # 전처리 파이프라인 실행
        processed_jobs = run_preprocess_pipeline(raw_jobs)
        
        state["processed_jobs"] = processed_jobs
        state["error"] = ""
        
        print(f"✓ {len(processed_jobs)}개 공고 정제 완료")
        
    except Exception as e:
        print(f"❌ 전처리 오류: {e}")
        state["processed_jobs"] = []
        state["error"] = f"전처리 실패: {str(e)}"
    
    return state


def filter_jobs_node(state: JobSearchState) -> JobSearchState:
    """
    [노드 3] LLM 필터링
    
    - 프롬프트 생성
    - LLM 평가 (사용자 이력 vs 공고)
    - JSON 파싱
    - 점수 및 판정 산출
    """
    
    print("\n" + "=" * 80)
    print("🤖 [노드 3] LLM 필터링 시작")
    print("=" * 80)
    
    processed_jobs = state["processed_jobs"]
    user_profile = state["user_profile"]
    
    if not processed_jobs:
        print("⚠️  정제된 공고가 없습니다")
        state["evaluation_results"] = []
        state["error"] = "처리할 공고 없음"
        return state
    
    try:
        # LLM 필터링 실행
        evaluation_results = evaluate_jobs(user_profile, processed_jobs)
        
        state["evaluation_results"] = evaluation_results
        state["error"] = ""
        
        print(f"✓ {len(evaluation_results)}개 공고 평가 완료")
        
    except Exception as e:
        print(f"❌ 필터링 오류: {e}")
        state["evaluation_results"] = []
        state["error"] = f"LLM 필터링 실패: {str(e)}"
    
    return state


def summarize_result_node(state: JobSearchState) -> JobSearchState:
    """
    [노드 4] 요약 및 분석
    
    - 결과 통계
    - 부족 스킬 분석
    - 학습 우선순위
    - 추천 공고 제시
    """
    
    print("\n" + "=" * 80)
    print("📊 [노드 4] 요약 및 분석 시작")
    print("=" * 80)
    
    evaluation_results = state["evaluation_results"]
    user_profile = state["user_profile"]
    
    if not evaluation_results:
        print("⚠️  평가 결과가 없습니다")
        state["summary"] = {}
        state["error"] = "평가 결과 없음"
        return state
    
    try:
        # 요약 생성
        summary = summarize_results(user_profile, evaluation_results)
        
        state["summary"] = summary
        state["error"] = ""
        
        # 콘솔에 출력
        print_summary(summary)
        
    except Exception as e:
        print(f"❌ 요약 오류: {e}")
        state["summary"] = {}
        state["error"] = f"요약 생성 실패: {str(e)}"
    
    return state


# ====== 실행 함수 ======

def run_job_search_workflow(
    keyword: str,
    user_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """
    전체 워크플로우 실행
    
    Args:
        keyword: 검색 직무 (예: "AI 개발자")
        user_profile: 사용자 이력 정보
    
    Returns:
        최종 상태 (raw_jobs, processed_jobs, evaluation_results, summary)
    """
    
    print("\n" + "🚀 " * 40)
    print("사람인 공고 필터링 워크플로우 시작")
    print("🚀 " * 40)
    
    # 그래프 생성
    graph = create_job_search_graph()
    
    # 초기 상태
    initial_state: JobSearchState = {
        "keyword": keyword,
        "user_profile": user_profile,
        "raw_jobs": [],
        "processed_jobs": [],
        "evaluation_results": [],
        "summary": {},
        "error": "",
    }
    
    # 그래프 실행
    final_state = graph.invoke(initial_state)
    
    print("\n" + "🎉 " * 40)
    print("워크플로우 완료!")
    print("🎉 " * 40)
    
    return final_state


def run_job_search_workflow_with_progress(
    keyword: str,
    user_profile: Dict[str, Any],
    status: Dict[str, str],
    render_status,
) -> Dict[str, Any]:
    """
    Streamlit UI에서 단계별 진행상황을 보여주기 위한 실행 함수.

    기존 LangGraph 노드 함수는 그대로 재사용하고, 각 노드 실행 전후에
    status 딕셔너리를 갱신하여 화면에 표시한다.
    """

    state: JobSearchState = {
        "keyword": keyword,
        "user_profile": user_profile,
        "raw_jobs": [],
        "processed_jobs": [],
        "evaluation_results": [],
        "summary": {},
        "error": "",
    }

    def update_step(step_name: str, step_status: str):
        status[step_name] = step_status
        render_status(status)

    update_step("검색 URL 생성", "완료")

    update_step("사람인 공고 크롤링", "진행중")
    state = crawl_jobs_node(state)
    update_step("사람인 공고 크롤링", "실패" if state.get("error") else "완료")
    if state.get("error"):
        return state

    update_step("공고 데이터 전처리", "진행중")
    state = preprocess_jobs_node(state)
    update_step("공고 데이터 전처리", "실패" if state.get("error") else "완료")
    if state.get("error"):
        return state

    update_step("LLM 적합도 평가", "진행중")
    state = filter_jobs_node(state)
    update_step("LLM 적합도 평가", "실패" if state.get("error") else "완료")
    if state.get("error"):
        return state

    update_step("결과 요약 생성", "진행중")
    state = summarize_result_node(state)
    update_step("결과 요약 생성", "실패" if state.get("error") else "완료")

    return state


if __name__ == "__main__":
    # 테스트용 사용자 프로필
    test_user = {
        "name": "홍길동",
        "skills": ["Python", "SQL", "FastAPI"],
        "certifications": ["정보처리기사"],
        "preferred_employment_types": ["정규직"],
        "preferred_locations": ["서울", "경기"],
        "education": "학사",
        "career_level": "신입",
        "interested_jobs": ["AI 개발자", "백엔드 개발자"],
    }
    
    # 워크플로우 실행
    final_state = run_job_search_workflow("AI 개발자", test_user)
    
    # 결과 저장
    import json
    with open("data/results/final_result.json", "w", encoding="utf-8") as f:
        json.dump(final_state, f, ensure_ascii=False, indent=2)
    
    print("\n✓ 결과 저장: data/results/final_result.json")
