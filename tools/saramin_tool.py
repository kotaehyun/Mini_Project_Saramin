# LangChain @tool로 래핑된 크롤링 함수

from langchain.tools import tool
from typing import List, Dict
from crawlers.saramin_crawler import crawl_saramin_jobs as _crawl_saramin_jobs
from models.schemas import JobPosting

"""
[6️⃣ LangChain @tool 래핑]

기존 크롤링 함수 crawl_saramin_jobs()는 순수 함수로 유지하고,
@tool 데코레이터를 붙인 별도 함수로 LangChain 에이전트/체인에서 사용
"""


@tool
def search_saramin_jobs(keyword: str) -> List[Dict]:
    """
    사람인 구인공고 검색 및 크롤링 (LangChain Tool)
    
    이 함수는 사용자 검색어를 입력받아 사람인에서 
    구인공고를 크롤링하고 정보를 반환합니다.
    
    Args:
        keyword: 검색할 직무 (예: "AI 개발자", "백엔드 개발자")
    
    Returns:
        공고 정보 딕셔너리 리스트
    
    Example:
        >>> jobs = search_saramin_jobs("AI 개발자")
        >>> len(jobs)
        20
        >>> jobs[0].keys()
        dict_keys(['company', 'title', 'url', 'location', ...])
    """
    
    # 기존 함수 호출 (미니 프로젝트이므로 1페이지만)
    jobs = _crawl_saramin_jobs(keyword, max_pages=2)
    
    print(f"🔍 Tool 실행: {len(jobs)}개 공고 검색됨")
    return jobs


# 테스트용
if __name__ == "__main__":
    # @tool 함수 호출 테스트
    result = search_saramin_jobs("AI 개발자")
    print(f"\n검색 결과: {len(result)}개 공고")
    
    if result:
        print("\n첫 번째 공고:")
        for key, value in result[0].items():
            print(f"  {key}: {value}")
