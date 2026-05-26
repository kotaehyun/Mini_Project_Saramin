# `chains/` 코드 리뷰

`chains/` 폴더는 채용공고 데이터를 단계별로 처리하는 핵심 로직을 담고 있습니다. 이름은 LangChain의 chain에서 왔지만, 모든 파일이 꼭 LangChain 객체만 다루는 것은 아닙니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `preprocess_chain.py` | 크롤링 결과 정제, 중복 제거, LLM용 설명 생성 |
| `filter_chain.py` | 사용자 프로필과 공고를 LLM으로 비교 평가 |
| `summary_chain.py` | 평가 결과 통계, 부족 스킬, 학습 경로 생성 |

## `preprocess_chain.py`

크롤링된 공고 데이터를 LLM에 넣기 좋은 형태로 정리합니다.

### 함수 구조

- `filter_invalid_jobs(jobs)`: 회사명과 공고명이 없는 데이터를 제거합니다.
- `remove_duplicate_jobs(jobs)`: 회사명과 공고명 조합이 같은 공고를 중복으로 판단해 제거합니다.
- `preprocess_jobs(jobs)`: 문자열 공백 제거, 빈값 처리, 스킬 중복 제거, `job_description` 생성까지 수행합니다.
- `_generate_job_description(job)`: 공고 딕셔너리를 LLM 프롬프트용 자연어 텍스트로 만듭니다.
- `run_preprocess_pipeline(jobs)`: 위 함수들을 순서대로 실행하는 전체 전처리 파이프라인입니다.

### 데이터 흐름

```text
raw_jobs
  -> filter_invalid_jobs()
  -> remove_duplicate_jobs()
  -> preprocess_jobs()
  -> processed_jobs
```

### 공부 포인트

- 원본 데이터를 바로 LLM에 넣지 않고, 필드 정리 후 설명 문자열을 만들어 넣습니다.
- `set()`으로 중복 스킬을 제거하지만, 순서가 바뀔 수 있습니다. 순서가 중요하면 다른 방식이 필요합니다.
- `job.get("field", "기본값")` 패턴은 딕셔너리에 키가 없을 때 안전하게 기본값을 쓰는 방식입니다.

## `filter_chain.py`

LLM을 호출해서 공고와 사용자 프로필의 적합도를 평가합니다.

### 함수 구조

- `create_filter_jobs_chain(llm=None)`: LLM 객체가 없으면 기본 `ChatOpenAI`를 만들고, 프롬프트 체인을 생성합니다.
- `evaluate_job(user_profile, job, filter_chain)`: 공고 1개를 평가하고 회사명, 제목, URL 같은 기본 정보를 결과에 추가합니다.
- `evaluate_jobs(user_profile, jobs)`: 여러 공고를 순회하며 `evaluate_job()`을 반복 호출합니다.

### 데이터 흐름

```text
user_profile + processed_job
  -> chain_input
  -> filter_chain.invoke()
  -> evaluation_result
```

### 공부 포인트

- LLM 입력값은 프롬프트 변수 이름과 정확히 맞아야 합니다.
- API 호출 제한을 고려해 공고마다 `time.sleep(1)`을 둡니다.
- `evaluate_job()`은 실패 시 `None`을 반환합니다. 호출하는 쪽에서 `if result:`로 성공한 결과만 모읍니다.

## `summary_chain.py`

여러 공고 평가 결과를 합쳐 통계와 학습 계획을 만듭니다.

### 함수 구조

- `summarize_results(user_profile, evaluation_results)`: 전체 요약 딕셔너리를 생성합니다.
- `_generate_learning_path(user_profile, missing_core_skills, missing_certs)`: 부족 스킬과 자격증을 바탕으로 학습 단계를 만듭니다.
- `print_summary(summary)`: 콘솔 출력용 요약을 출력합니다.

### 주요 계산

- `Counter`로 결과 분류 개수와 부족 스킬 빈도를 셉니다.
- `fit_score` 기준으로 상위 3개 추천 공고를 뽑습니다.
- 즉시지원, 보완후지원, 비추천 개수를 이용해 지원 가능 비율을 계산합니다.

### 개선 후보

- LLM 응답 필드가 누락되어도 안정적으로 처리하도록 기본값 검증을 더 강화할 수 있습니다.
- `filter_chain.py`의 API 호출 대기 시간은 설정값으로 빼면 테스트와 운영에서 조절하기 쉽습니다.
- `summary_chain.py`의 학습 계획은 현재 규칙 기반입니다. 사용자 수준이나 목표 기간을 반영하면 더 좋아집니다.
