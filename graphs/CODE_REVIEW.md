# `graphs/` 코드 리뷰

`graphs/` 폴더는 여러 처리 단계를 LangGraph 워크플로우로 연결합니다. 이 프로젝트의 중심 흐름을 이해하려면 `job_graph.py`를 읽는 것이 가장 좋습니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `job_graph.py` | 크롤링, 전처리, LLM 평가, 요약 노드를 연결하고 실행 |

## `JobSearchState`

`JobSearchState`는 워크플로우 전체에서 공유하는 상태 딕셔너리의 타입입니다.

```text
입력:
  keyword
  user_profile

중간 결과:
  raw_jobs
  processed_jobs
  evaluation_results

최종 결과:
  summary
  error
```

초보자 관점에서는 이 `state`가 프로그램의 공용 가방이라고 보면 됩니다. 각 노드는 가방에서 필요한 값을 꺼내고, 처리 결과를 다시 가방에 넣습니다.

## 함수 구조

### 그래프 생성

- `create_job_search_graph()`: LangGraph의 `StateGraph`를 만들고 노드와 엣지를 연결합니다.

연결 순서:

```text
crawl_jobs
  -> preprocess_jobs
  -> filter_jobs
  -> summarize_results
  -> END
```

### 노드 함수

- `crawl_jobs_node(state)`: 검색어로 사람인 공고를 크롤링하고 `raw_jobs`에 저장합니다.
- `preprocess_jobs_node(state)`: `raw_jobs`를 정제해서 `processed_jobs`에 저장합니다.
- `filter_jobs_node(state)`: `processed_jobs`와 `user_profile`을 비교해 `evaluation_results`를 만듭니다.
- `summarize_result_node(state)`: 평가 결과를 요약해 `summary`를 만듭니다.

### 실행 함수

- `run_job_search_workflow(keyword, user_profile)`: 콘솔용 전체 워크플로우 실행 함수입니다.
- `run_job_search_workflow_with_progress(keyword, user_profile, status, render_status)`: Streamlit에서 진행 상태를 표시하기 위한 실행 함수입니다.

## 공부 포인트

- LangGraph 방식은 노드와 엣지로 흐름을 명시합니다.
- 각 노드 함수는 같은 `state` 구조를 입력받고 다시 반환합니다.
- 실패하면 `state["error"]`에 메시지를 넣고 다음 단계가 멈추거나 빈 결과를 반환합니다.
- Streamlit용 함수는 LangGraph 컴파일 그래프를 직접 쓰지 않고 노드 함수를 순서대로 호출합니다. 대신 상태 표시를 세밀하게 할 수 있습니다.

## 개선 후보

- `crawl_jobs_node()`에서 `max_pages=2`가 하드코딩되어 있습니다. `config.MAX_PAGES`나 사용자 입력을 쓰면 설정 관리가 쉬워집니다.
- `json` import는 파일 상단과 하단 테스트 코드에서 중복되며, 상단 import는 현재 불필요합니다.
- 에러가 생겼을 때 다음 노드로 갈지 말지 조건부 엣지를 쓰면 LangGraph의 장점을 더 살릴 수 있습니다.
