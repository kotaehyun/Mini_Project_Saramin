# 데이터 스키마 (Pydantic)

from pydantic import BaseModel, Field
from typing import List, Optional

"""
사용자 이력 정보 스키마
"""


class UserProfile(BaseModel):
    """사용자 이력 정보"""
    name: str = Field(..., description="이름")
    skills: List[str] = Field(default=[], description="보유 기술 스택")
    certifications: List[str] = Field(default=[], description="자격증")
    preferred_employment_types: List[str] = Field(default=[], description="희망 근무형태 (정규직, 계약직 등)")
    preferred_locations: List[str] = Field(default=[], description="희망 근무지역")
    education: str = Field(default="미지정", description="최종학력 (고졸, 초대졸, 학사, 석사 등)")
    career_level: str = Field(default="신입", description="경력 (신입, 1~3년, 3~5년, 5년이상 등)")
    interested_jobs: List[str] = Field(default=[], description="관심 직무")


"""
크롤링된 공고 정보 스키마
"""


class JobPosting(BaseModel):
    """공고 정보 (검색결과 페이지에서 수집 가능한 항목)"""
    company: str = Field(..., description="회사명")
    title: str = Field(..., description="공고명")
    url: Optional[str] = Field(None, description="공고 상세 URL")
    location: str = Field(default="미상", description="근무지역")
    career: str = Field(default="미상", description="경력 요구사항")
    employment_type: str = Field(default="미상", description="근무형태")
    deadline: str = Field(default="미등록", description="마감일")
    required_skills: List[str] = Field(default=[], description="요구 스킬")
    
    # 아래 필드는 상세페이지 크롤링 필요 (현재 미구현)
    education: Optional[str] = Field(None, description="학력 요구사항")
    requirements: Optional[str] = Field(None, description="자격요건")
    preferred: Optional[str] = Field(None, description="우대사항")


"""
LLM 필터링 결과 스키마
"""


class EvaluationResult(BaseModel):
    """공고별 적합성 평가 결과"""
    index: int = Field(..., description="순번")
    company: str = Field(..., description="회사명")
    title: str = Field(..., description="공고명")
    url: Optional[str] = Field(None, description="공고 상세 URL")
    
    # 최종 판정
    result: str = Field(..., description="적합 | 보완필요 | 부적합")
    fit_score: int = Field(..., description="적합도 점수 (0-100)", ge=0, le=100)
    apply_level: str = Field(..., description="즉시지원 | 보완후지원 | 비추천")
    
    # 스킬 분석
    matched_skills: List[str] = Field(default=[], description="일치한 스킬")
    missing_core_skills: List[str] = Field(default=[], description="핵심 부족 스킬")
    missing_optional_skills: List[str] = Field(default=[], description="우대사항 기반 부족 스킬")
    missing_certs: List[str] = Field(default=[], description="부족 자격증")
    
    # 조건 분석
    requirements_check: str = Field(..., description="자격요건 충족 여부 설명")
    preferred_check: str = Field(..., description="우대사항 충족 여부 설명")
    career_check: str = Field(..., description="경력 조건 판단")
    education_check: str = Field(..., description="학력 조건 판단")
    employment_type_check: str = Field(..., description="근무형태 판단")
    location_check: str = Field(..., description="근무지역 판단")
    
    # 신입/취준생 기준
    junior_friendly: bool = Field(..., description="신입/취준생 지원 가능 여부")
    junior_reason: str = Field(..., description="신입/취준생 기준 설명")
    
    # 최종 판단
    reason: str = Field(..., description="최종 판단 이유")
    study_priority: List[str] = Field(default=[], description="우선 학습할 기술")
