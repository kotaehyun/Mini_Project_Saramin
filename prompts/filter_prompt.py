# LLM 프롬프트 템플릿

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List

"""
[8️⃣ LLM 필터링 프롬프트]

LLM이 공고별 적합성을 판단하고 JSON으로 응답하도록 설계
"""


# 프롬프트용 응답 스키마
class JobEvaluation(BaseModel):
    """개별 공고 평가 결과"""
    company: str = Field(description="회사명")
    title: str = Field(description="공고명")
    result: str = Field(description="적합 | 보완필요 | 부적합")
    fit_score: int = Field(description="적합도 점수 (0-100)")
    apply_level: str = Field(description="즉시지원 | 보완후지원 | 비추천")
    
    matched_skills: List[str] = Field(description="일치한 스킬")
    missing_core_skills: List[str] = Field(description="핵심 부족 스킬")
    missing_optional_skills: List[str] = Field(description="우대사항 기반 부족 스킬")
    missing_certs: List[str] = Field(description="부족 자격증")
    
    requirements_check: str = Field(description="자격요건 판단")
    preferred_check: str = Field(description="우대사항 판단")
    career_check: str = Field(description="경력 조건 판단")
    education_check: str = Field(description="학력 조건 판단")
    employment_type_check: str = Field(description="근무형태 판단")
    location_check: str = Field(description="근무지역 판단")
    
    junior_friendly: bool = Field(description="신입/취준생 지원 가능 여부")
    junior_reason: str = Field(description="신입/취준생 관점 설명")
    
    reason: str = Field(description="최종 판단 이유 (50자 이상)")
    study_priority: List[str] = Field(description="우선 학습 기술 리스트")


def create_filter_prompt() -> ChatPromptTemplate:
    """
    공고 필터링 프롬프트 생성
    
    프롬프트 구조:
    1. 역할 설정
    2. 사용자 정보 제시
    3. 평가 기준 명확화
    4. 공고 정보 제시
    5. JSON 형식 강제
    """
    
    system_prompt = """당신은 취업 상담 AI 입니다.

사용자의 경력, 스킬, 자격증을 분석하여 구인공고가 사용자에게 얼마나 적합한지 판단합니다.

## 평가 기준

### 1. 일치도 계산
- 요구 스킬 중 보유한 스킬: +40%
- 자격요건 충족: +20%
- 우대사항 보유: +10%
- 경력/학력 적합: +15%
- 근무형태/지역 적합: +15%

### 2. 최종 판정 (fit_score 기반)
- 90점 이상: "적합" (apply_level: 즉시지원)
- 70~89점: "보완필요" (apply_level: 보완후지원)
- 70점 미만: "부적합" (apply_level: 비추천)

### 3. 신입/취준생 평가
- 신입이 지원 가능한 공고인지 별도 판단
- junior_friendly: true/false
- junior_reason: 구체적 설명

### 4. 분석 항목
각 항목을 구체적으로 기술:
- requirements_check: "자격요건" 항목과 사용자 정보 비교
- preferred_check: "우대사항" 항목과 사용자 보유 여부 비교
- career_check: 요구 경력과 사용자 경력 비교
- education_check: 요구 학력과 사용자 학력 비교
- employment_type_check: 희망 형태와 일치 여부
- location_check: 희망 지역과 일치 여부

### 5. 스킬 분석
- matched_skills: 공고 요구 스킬 중 사용자가 보유한 것
- missing_core_skills: 필수적인 부족 스킬 (top 3)
- missing_optional_skills: 우대사항에 포함된 부족 스킬 (top 3)

### 6. 학습 계획
- study_priority: 이 직무를 준비하기 위해 학습해야 할 기술 순서"""

    user_prompt = """## 사용자 정보

이름: {user_name}
보유 기술: {skills}
자격증: {certifications}
최종학력: {education}
경력: {career_level}
희망 근무형태: {preferred_employment_types}
희망 지역: {preferred_locations}
관심 직무: {interested_jobs}

## 평가할 공고

{job_description}

## 지시사항

1. 위의 사용자 정보와 공고 정보를 비교
2. 각 항목별로 구체적으로 판단
3. 반드시 JSON 형식으로만 응답
4. JSON 파싱 가능하도록 유효한 JSON만 출력
5. 한국어로 작성"""

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            ("user", user_prompt),
        ]
    )
    
    return prompt


def create_filter_chain(llm):
    """
    LLM 필터링 체인 생성
    
    Args:
        llm: LangChain LLM 객체 (ChatOpenAI 등)
    
    Returns:
        프롬프트 | LLM | 파서로 구성된 체인
    """
    
    prompt = create_filter_prompt()
    parser = JsonOutputParser(pydantic_object=JobEvaluation)
    
    # 체인 구성: Prompt -> LLM -> Parser
    chain = prompt | llm | parser
    
    return chain


if __name__ == "__main__":
    # 프롬프트 확인
    prompt = create_filter_prompt()
    
    # 테스트 입력
    test_input = {
        "user_name": "홍길동",
        "skills": "Python, LangChain, SQL, FastAPI",
        "certifications": "정보처리기사",
        "education": "학사",
        "career_level": "신입",
        "preferred_employment_types": "정규직, 계약직",
        "preferred_locations": "서울, 경기",
        "interested_jobs": "AI 개발자, 백엔드 개발자",
        "job_description": """회사: 테크 스타트업
직무: AI 백엔드 개발자
근무지역: 서울 강남
경력요구: 신입~1년
근무형태: 정규직
요구기술: Python, FastAPI, PyTorch, AWS
자격요건: 학사 이상, 프로그래밍 경험 1년 이상
우대사항: 머신러닝 프로젝트 경험, LangChain 사용 경험
마감일: 2024년 12월 31일"""
    }
    
    # 프롬프트 렌더링
    rendered = prompt.format(**test_input)
    print("생성된 프롬프트:")
    print("=" * 80)
    print(rendered)
    print("=" * 80)
