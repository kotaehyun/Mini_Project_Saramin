# `models/` 코드 리뷰

`models/` 폴더는 프로젝트에서 주고받는 데이터의 모양을 정의합니다. Pydantic 모델은 "이 데이터는 이런 필드를 가져야 한다"는 약속을 코드로 표현합니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `schemas.py` | 사용자 프로필, 채용공고, 평가 결과 스키마 정의 |

## `schemas.py`

### `UserProfile`

사용자 이력 정보를 표현합니다.

주요 필드:

- `name`: 이름
- `skills`: 보유 기술 목록
- `certifications`: 자격증 목록
- `preferred_employment_types`: 희망 근무형태
- `preferred_locations`: 희망 지역
- `education`: 최종 학력
- `career_level`: 경력 수준
- `interested_jobs`: 관심 직무

### `JobPosting`

크롤링한 채용공고 정보를 표현합니다.

주요 필드:

- `company`: 회사명
- `title`: 공고명
- `url`: 상세 URL
- `location`: 근무지역
- `career`: 경력 조건
- `employment_type`: 근무형태
- `deadline`: 마감일
- `required_skills`: 요구 스킬
- `education`, `requirements`, `preferred`: 상세 페이지에서 더 정확히 가져올 수 있는 선택 필드

### `EvaluationResult`

LLM이 평가한 공고별 결과를 표현합니다.

주요 필드:

- `result`: 적합, 보완필요, 부적합
- `fit_score`: 0부터 100까지의 적합도 점수
- `apply_level`: 즉시지원, 보완후지원, 비추천
- `matched_skills`: 일치한 스킬
- `missing_core_skills`: 부족한 핵심 스킬
- `missing_optional_skills`: 부족한 우대 스킬
- `reason`: 최종 판단 이유
- `study_priority`: 우선 학습할 기술

## 공부 포인트

- `BaseModel`을 상속하면 데이터 검증과 문서화가 쉬워집니다.
- `Field(default=..., description=...)`는 기본값과 설명을 함께 적는 방식입니다.
- `Optional[str]`은 값이 문자열이거나 `None`일 수 있다는 뜻입니다.
- `Field(..., description=...)`에서 `...`은 필수 입력이라는 뜻입니다.

## 개선 후보

- 현재 실제 워크플로우 대부분은 Pydantic 모델 인스턴스보다 딕셔너리를 사용합니다. 안정성을 높이려면 크롤링 결과와 LLM 결과를 모델로 검증하는 단계를 추가할 수 있습니다.
- 리스트 기본값에 `default=[]`를 쓰고 있습니다. Pydantic에서는 보통 안전하게 처리되지만, 관례적으로는 `default_factory=list`가 더 명확합니다.
