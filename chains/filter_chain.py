# LLM 필터링 체인

from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from prompts.filter_prompt import create_filter_chain
from config import LLM_MODEL, LLM_TEMPERATURE

"""
필터링 체인: 각 공고를 사용자와 비교하여 평가
"""


def create_filter_jobs_chain(llm=None):
    """
    공고 필터링 체인 생성
    
    Args:
        llm: LangChain LLM 객체 (None이면 기본값 사용)
    
    Returns:
        공고 필터링 체인
    """
    
    if llm is None:
        llm = ChatOpenAI(
            model=LLM_MODEL,
            temperature=LLM_TEMPERATURE,
            max_tokens=2000,
        )
    
    # 프롬프트 + LLM + 파서 체인 생성
    filter_chain = create_filter_chain(llm)
    
    return filter_chain


def evaluate_job(
    user_profile: Dict[str, Any],
    job: Dict[str, Any],
    filter_chain
) -> Dict[str, Any]:
    """
    개별 공고를 사용자 프로필과 비교하여 평가
    
    Args:
        user_profile: 사용자 이력 정보
        job: 크롤링/정제된 공고 정보
        filter_chain: LLM 필터링 체인
    
    Returns:
        평가 결과 (JSON)
    """
    
    try:
        # 프롬프트 입력 구성
        chain_input = {
            "user_name": user_profile.get("name", "사용자"),
            "skills": ", ".join(user_profile.get("skills", [])) or "없음",
            "certifications": ", ".join(user_profile.get("certifications", [])) or "없음",
            "education": user_profile.get("education", "미지정"),
            "career_level": user_profile.get("career_level", "신입"),
            "preferred_employment_types": ", ".join(user_profile.get("preferred_employment_types", [])) or "무관",
            "preferred_locations": ", ".join(user_profile.get("preferred_locations", [])) or "무관",
            "interested_jobs": ", ".join(user_profile.get("interested_jobs", [])) or "무관",
            "job_description": job.get("job_description", ""),
        }
        
        # LLM 체인 실행
        result = filter_chain.invoke(chain_input)
        
        # 결과에 기본 정보 추가
        result["company"] = job.get("company", "미상")
        result["title"] = job.get("title", "공고명 미상")
        result["url"] = job.get("url")
        result["index"] = job.get("index", 0)
        
        return result
        
    except Exception as e:
        print(f"❌ 평가 중 오류: {e}")
        return None


def evaluate_jobs(
    user_profile: Dict[str, Any],
    jobs: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    모든 공고 평가 (LLM 호출)
    
    Args:
        user_profile: 사용자 이력 정보
        jobs: 정제된 공고 리스트
    
    Returns:
        평가 결과 리스트
    """
    
    print(f"\n[평가] LLM으로 {len(jobs)}개 공고 평가 중...")
    
    # LLM 체인 생성
    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        max_tokens=2000,
    )
    filter_chain = create_filter_jobs_chain(llm)
    
    # 각 공고 평가
    results = []
    
    for idx, job in enumerate(jobs, 1):
        print(f"  [{idx}/{len(jobs)}] {job['company']} - {job['title']}")
        
        job["index"] = idx
        result = evaluate_job(user_profile, job, filter_chain)
        
        if result:
            results.append(result)
        
        # API 호출 제한 대비 딜레이
        import time
        time.sleep(1)
    
    print(f"✓ {len(results)}개 공고 평가 완료")
    return results
