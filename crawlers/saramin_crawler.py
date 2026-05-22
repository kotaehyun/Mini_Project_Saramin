# 크롤링 핵심 로직 (기존 코드 유지 + 확장)

import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from typing import List, Dict, Optional
import time
from config import SEARCH_BASE_URL, BASE_URL, HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, MAX_PAGES

"""
[3️⃣ 검색 URL 도출 함수]
사용자 입력 검색어를 URL 인코딩하여 사람인 검색 URL 자동 생성
"""


def generate_search_url(keyword: str, page: int = 1) -> str:
    """
    검색어로부터 사람인 검색 URL 생성
    
    Args:
        keyword: 검색어 (예: "AI 개발자", "백엔드 개발자")
        page: 검색 결과 페이지 번호 (기본값: 1)
    
    Returns:
        완전한 사람인 검색 URL
    
    Example:
        >>> url = generate_search_url("AI 개발자", 1)
        >>> print(url)
        "https://www.saramin.co.kr/zf_user/search?search_area=main&search_done=y&search_optional_item=n&searchType=recently&searchword=AI%20%EA%B0%9C%EB%B0%9C%EC%9E%90&page=1"
    """
    # urllib.parse.quote로 검색어 URL 인코딩
    encoded_keyword = quote(keyword)
    
    # 사람인 검색 URL 생성
    # search_area: 검색 범위 (main=전체)
    # search_done: 검색 완료 여부 (y=검색됨)
    # searchType: 정렬방식 (recently=최신순)
    search_url = (
        f"{SEARCH_BASE_URL}?"
        f"search_area=main"
        f"&search_done=y"
        f"&search_optional_item=n"
        f"&searchType=recently"
        f"&searchword={encoded_keyword}"
        f"&page={page}"
    )
    
    return search_url


"""
[4️⃣ 공고 상세 URL 도출]
검색 결과에서 href를 절대 URL로 변환하는 헬퍼 함수
"""


def build_absolute_url(relative_url: str) -> str:
    """
    상대 URL을 절대 URL로 변환
    
    Args:
        relative_url: 상대 URL (예: "/zf_user/view?jd_no=...")
    
    Returns:
        절대 URL (예: "https://www.saramin.co.kr/zf_user/view?jd_no=...")
    """
    if relative_url.startswith("http"):
        return relative_url
    
    # urllib.parse.urljoin 사용하여 절대 URL 생성
    absolute_url = urljoin(BASE_URL, relative_url)
    return absolute_url


"""
[5️⃣ 확장된 크롤링 함수]
기존 requests+BeautifulSoup 방식 유지하면서 필드 확장
"""


def crawl_saramin_jobs(keyword: str, max_pages: int = MAX_PAGES) -> List[Dict]:
    """
    사람인에서 검색어에 해당하는 공고 크롤링
    
    Args:
        keyword: 검색어 (예: "AI 개발자")
        max_pages: 크롤링할 최대 페이지 수 (미니 프로젝트용 제한)
    
    Returns:
        공고 정보 딕셔너리 리스트
    
    Example:
        >>> jobs = crawl_saramin_jobs("AI 개발자", max_pages=1)
        >>> print(len(jobs))
        20
    """
    
    all_jobs = []
    
    for page in range(1, max_pages + 1):
        print(f"[크롤링] {keyword} - {page}페이지 수집 중...")
        
        # [1단계] 검색 URL 생성
        search_url = generate_search_url(keyword, page)
        
        try:
            # [2단계] HTTP 요청 (기존 방식 유지)
            response = requests.get(
                search_url,
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT
            )
            response.encoding = "utf-8"
            
            if response.status_code != 200:
                print(f"⚠️  페이지 요청 실패 (상태코드: {response.status_code})")
                continue
            
            # [3단계] BeautifulSoup으로 파싱
            soup = BeautifulSoup(response.text, "html.parser")
            
            # [4단계] 공고 항목 추출
            # 사람인 검색 결과는 구조가 자주 바뀌므로 현재/이전 구조를 함께 지원
            job_items = soup.select("div.item_recruit, div.cell.job_item")
            
            if not job_items:
                print(f"⚠️  공고 항목을 찾을 수 없습니다. HTML 구조 확인 필요")
                print(f"   현재 selector: 'div.item_recruit, div.cell.job_item'")
                continue
            
            # [5단계] 각 공고에서 정보 추출
            for job_item in job_items:
                try:
                    job_info = _extract_job_info(job_item)
                    if job_info:
                        all_jobs.append(job_info)
                except Exception as e:
                    print(f"⚠️  공고 추출 중 오류: {e}")
                    continue
            
            print(f"✓ {len(job_items)}개 공고 추출 완료")
            
            # 정중한 크롤링을 위한 딜레이
            time.sleep(2)
            
        except requests.exceptions.RequestException as e:
            print(f"❌ 요청 오류: {e}")
            continue
    
    print(f"\n[완료] 총 {len(all_jobs)}개 공고 수집됨")
    return all_jobs


def _extract_job_info(job_item) -> Optional[Dict]:
    """
    개별 공고 항목에서 정보 추출
    
    검색 결과 페이지에서 한번에 가져올 수 있는 필드:
    - company: 회사명
    - title: 공고명
    - location: 근무지역
    - career: 경력
    - employment_type: 근무형태
    - deadline: 마감일
    - url: 공고 상세 URL
    
    상세 페이지 필요 필드 (현재는 구현 미포함):
    - education: 학력
    - required_skills: 요구 스킬
    - requirements: 자격요건
    - preferred: 우대사항
    """
    
    try:
        info = {}
        
        # 1. 회사명 추출
        company_elem = job_item.select_one("strong.corp_name, div.corp_name")
        info["company"] = company_elem.get_text(strip=True) if company_elem else "미상"
        
        # 2. 공고 제목 및 URL 추출
        title_elem = job_item.select_one("h2.job_tit a, h2.job_title a, a.job_tit")
        if title_elem:
            info["title"] = title_elem.get_text(strip=True)
            # [4️⃣ 상세 URL 도출] href를 절대 URL로 변환
            relative_href = title_elem.get("href")
            info["url"] = build_absolute_url(relative_href) if relative_href else None
        else:
            info["title"] = "공고명 미상"
            info["url"] = None
        
        # 3~5. 근무 조건 추출
        condition_elems = job_item.select("div.job_condition > span")
        if condition_elems:
            conditions = [elem.get_text(" ", strip=True) for elem in condition_elems]
            info["location"] = conditions[0] if len(conditions) > 0 else "지역 미상"
            info["career"] = conditions[1] if len(conditions) > 1 else "경력 미상"
            info["education"] = conditions[2] if len(conditions) > 2 else None
            info["employment_type"] = conditions[3] if len(conditions) > 3 else "미상"
        else:
            location_elem = job_item.select_one("span.local")
            career_elem = job_item.select_one("span.career")
            employment_elem = job_item.select_one("span.job_type")
            info["location"] = location_elem.get_text(strip=True) if location_elem else "지역 미상"
            info["career"] = career_elem.get_text(strip=True) if career_elem else "경력 미상"
            info["education"] = None
            info["employment_type"] = employment_elem.get_text(strip=True) if employment_elem else "미상"
        
        # 6. 마감일 추출 (선택사항 - 없을 수 있음)
        deadline_elem = job_item.select_one("div.job_date span.date, span.deadline")
        info["deadline"] = deadline_elem.get_text(strip=True) if deadline_elem else "미등록"
        
        # 7. 요구 스킬 추출 (있을 경우)
        skill_elems = job_item.select("div.job_sector a, span.skill")
        skills = []
        for skill in skill_elems:
            skill_name = skill.get_text(strip=True)
            if skill_name and skill_name not in skills:
                skills.append(skill_name)
        info["required_skills"] = skills
        
        return info
        
    except Exception as e:
        print(f"❌ 정보 추출 오류: {e}")
        return None


# ====== 테스트용 함수 ======
if __name__ == "__main__":
    # URL 생성 테스트
    url = generate_search_url("AI 개발자", 1)
    print(f"생성된 URL: {url}\n")
    
    # 크롤링 테스트 (1페이지만)
    jobs = crawl_saramin_jobs("AI 개발자", max_pages=1)
    
    if jobs:
        print(f"\n첫 번째 공고 정보:")
        print(jobs[0])
