# 데이터 전처리 체인

from typing import List, Dict

"""
[7️⃣ 전처리 체인]

크롤링된 공고 정보를 정제하고 LLM 평가용으로 준비
"""


def preprocess_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    크롤링 결과 정제
    
    1. 빈값 제거 (None, 빈 문자열)
    2. 중복 스킬 제거
    3. 공고별 텍스트 생성 (LLM 프롬프트용)
    4. 데이터 정규화
    
    Args:
        jobs: 크롤링된 공고 리스트
    
    Returns:
        정제된 공고 리스트
    """
    
    processed_jobs = []
    
    for job in jobs:
        try:
            cleaned_job = {}
            
            # 기본 필드 정제
            cleaned_job["company"] = job.get("company", "미상").strip()
            cleaned_job["title"] = job.get("title", "미상").strip()
            cleaned_job["url"] = job.get("url", "").strip() or None
            cleaned_job["location"] = job.get("location", "미상").strip()
            cleaned_job["career"] = job.get("career", "미상").strip()
            cleaned_job["employment_type"] = job.get("employment_type", "미상").strip()
            cleaned_job["deadline"] = job.get("deadline", "미등록").strip()
            
            # 스킬 정제 (중복 제거)
            skills = job.get("required_skills", [])
            if isinstance(skills, list):
                # 중복 제거 + 공백 제거
                cleaned_job["required_skills"] = list(
                    set(skill.strip() for skill in skills if skill.strip())
                )
            else:
                cleaned_job["required_skills"] = []
            
            # 선택사항 필드
            cleaned_job["education"] = job.get("education", "").strip() or None
            cleaned_job["requirements"] = job.get("requirements", "").strip() or None
            cleaned_job["preferred"] = job.get("preferred", "").strip() or None
            
            # [중요] LLM 프롬프트용 텍스트 생성
            cleaned_job["job_description"] = _generate_job_description(cleaned_job)
            
            processed_jobs.append(cleaned_job)
            
        except Exception as e:
            print(f"⚠️  공고 정제 중 오류: {e}")
            continue
    
    print(f"✓ {len(processed_jobs)}개 공고 정제 완료")
    return processed_jobs


def _generate_job_description(job: Dict) -> str:
    """
    LLM 평가용 공고 텍스트 생성
    
    크롤링된 정보를 자연스러운 텍스트로 변환하여
    LLM이 이해하기 쉽게 만듦
    """
    
    parts = []
    
    parts.append(f"회사: {job['company']}")
    parts.append(f"직무: {job['title']}")
    parts.append(f"근무지역: {job['location']}")
    parts.append(f"경력요구: {job['career']}")
    parts.append(f"근무형태: {job['employment_type']}")
    
    if job.get("education"):
        parts.append(f"학력: {job['education']}")
    
    if job.get("required_skills"):
        parts.append(f"요구기술: {', '.join(job['required_skills'])}")
    
    if job.get("requirements"):
        parts.append(f"자격요건: {job['requirements']}")
    
    if job.get("preferred"):
        parts.append(f"우대사항: {job['preferred']}")
    
    parts.append(f"마감일: {job['deadline']}")
    
    return "\n".join(parts)


def remove_duplicate_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    동일한 공고 제거 (회사명 + 공고명 기준)
    """
    
    seen = set()
    unique_jobs = []
    
    for job in jobs:
        key = (job["company"], job["title"])
        if key not in seen:
            seen.add(key)
            unique_jobs.append(job)
    
    print(f"✓ {len(jobs) - len(unique_jobs)}개 중복 공고 제거됨")
    return unique_jobs


def filter_invalid_jobs(jobs: List[Dict]) -> List[Dict]:
    """
    필수 필드가 없는 불완전한 공고 제거
    """
    
    valid_jobs = []
    
    for job in jobs:
        # 필수 필드: company, title, url
        if job.get("company") and job.get("title"):
            valid_jobs.append(job)
        else:
            print(f"⚠️  불완전한 공고 제거: {job}")
    
    print(f"✓ {len(jobs) - len(valid_jobs)}개 불완전한 공고 제거됨")
    return valid_jobs


# 전체 파이프라인
def run_preprocess_pipeline(jobs: List[Dict]) -> List[Dict]:
    """
    전처리 전체 파이프라인
    1. 불완전한 공고 제거
    2. 중복 제거
    3. 필드 정제
    4. LLM 텍스트 생성
    """
    
    print("\n[전처리] 파이프라인 시작...")
    
    jobs = filter_invalid_jobs(jobs)
    jobs = remove_duplicate_jobs(jobs)
    jobs = preprocess_jobs(jobs)
    
    print("[전처리] 완료!")
    return jobs
