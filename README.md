# 사람인 미니 프로젝트 기반 LangChain/LangGraph 데모

사람인 채용공고 검색 흐름을 활용해 LangChain과 LangGraph의 실행 구조를 설명하는 학습용 미니 프로젝트입니다.

사용자 프로필과 채용공고 정보를 비교해 LLM이 지원 적합도와 보완할 역량을 평가하며, 이 과정을 LangGraph 노드 흐름과 LangChain 체인 구조로 나누어 보여줍니다.

현재 구현은 Python 기반 콘솔 모드와 Streamlit 웹앱을 지원합니다. 핵심 목적은 실제 서비스 백엔드 구축보다, 사람인 미니 프로젝트를 예시로 Agent, Chain, Graph, State, Tool 호출 흐름을 직관적으로 이해하는 데 있습니다.

React/Next 기반 화면으로 전환할 경우에도 별도 백엔드 분리보다는 데모 데이터와 시각화 중심의 프론트엔드 데모로 확장하는 방향을 전제로 합니다.

## 주요 기능

- 검색어 기반 사람인 검색 URL 생성
- 검색 결과 페이지에서 공고 기본 정보 크롤링
- 중복 공고 제거와 LLM 평가용 공고 설명 생성
- OpenAI 모델을 이용한 공고별 적합도 평가
- LangGraph 기반 단계별 워크플로우 실행 구조 시각화
- LangChain 체인과 Tool 호출 흐름 학습용 예시 제공
- 추천 공고, 부족 스킬, 부족 자격증, 학습 우선순위 요약
- JSON, CSV, Markdown 보고서 저장
- Streamlit 결과 대시보드와 다운로드 버튼 제공
- Three.js 기반 3D LangGraph 진행 화면 제공

## 기술 스택

| 영역        | 사용 기술                   |
| ----------- | --------------------------- |
| 언어        | Python                      |
| 크롤링      | requests, BeautifulSoup     |
| LLM 체인    | LangChain, langchain-openai |
| 워크플로우  | LangGraph                   |
| UI          | Streamlit                   |
| 시각화      | Three.js, OrbitControls     |
| 데이터 모델 | Pydantic                    |

> React/Next 전환은 현재 폴더 구조를 먼저 바꾸기보다, 기존 LangChain/LangGraph 흐름을 설명하기 위한 데모 UI를 완성한 뒤 필요 범위만 정리하는 방향으로 진행합니다.

## 동작 구조

이 프로젝트는 사람인 채용공고 탐색을 하나의 예시 업무로 두고, 입력부터 결과 저장까지의 흐름을 LangGraph 노드 단위로 분리합니다. 각 노드는 `JobSearchState`를 읽고 갱신하며, LangChain 체인은 공고 평가와 결과 요약에 사용됩니다.

```text
사용자 입력
  |
  v
사람인 검색 URL 생성
  |
  v
공고 목록 크롤링
  |
  v
전처리
  - 필수 필드 확인
  - 회사명 + 공고명 기준 중복 제거
  - LLM 평가용 job_description 생성
  |
  v
LLM 평가
  - 적합도 점수
  - 지원 추천 수준
  - 일치/부족 스킬
  - 조건별 판단
  |
  v
결과 요약
  - 추천 공고 TOP 3
  - 부족 스킬/자격증 빈도
  - 학습 우선순위와 학습 경로
  |
  v
JSON / CSV / Markdown 저장
```

LangGraph 노드는 [graphs/job_graph.py](graphs/job_graph.py)에 정의되어 있습니다.

```text
crawl_jobs
  -> preprocess_jobs
  -> filter_jobs
  -> summarize_results
  -> END
```

Streamlit 모드에서는 위 노드 실행 상태에 `검색 URL 생성`과 `결과 파일 저장` 표시 단계를 더해 진행 상황을 보여줍니다.

## 프로젝트 구조

폴더 구조는 현재 Python/Streamlit 구현 기준을 유지합니다. React/Next 기반 데모로 확장하더라도 기존 학습용 LangChain/LangGraph 예시는 reference로 남길 수 있습니다.

```text
saramin_project/
├── main.py                         # 콘솔 실행 진입점
├── config.py                       # URL, LLM, 크롤링, 결과 경로 설정
├── requirements.txt                # Python 의존성
├── app/
│   ├── streamlit_app.py            # Streamlit 앱과 xAI-inspired UI 테마
│   ├── dashboard.py                # 평가 결과 대시보드
│   ├── graph_visualizer.py         # Three.js 3D 워크플로우 생성
│   └── _generated/                 # 생성된 iframe HTML
├── crawlers/
│   └── saramin_crawler.py          # 검색 URL 생성과 사람인 목록 크롤링
├── chains/
│   ├── preprocess_chain.py         # 공고 정제와 설명 생성
│   ├── filter_chain.py             # LLM 평가 실행
│   └── summary_chain.py            # 결과 통계와 학습 추천 요약
├── graphs/
│   └── job_graph.py                # LangGraph 워크플로우
├── prompts/
│   └── filter_prompt.py            # 평가 프롬프트와 JSON 파서
├── models/
│   └── schemas.py                  # 사용자, 공고, 평가 결과 스키마
├── tools/
│   └── saramin_tool.py             # LangChain tool 래퍼
├── utils/
│   └── output_formatter.py         # 저장과 콘솔 출력 포맷터
└── data/
    ├── user_profile.json           # 프로필 예시
    └── results/                    # 실행 결과 저장 위치
```

## 폴더별 Python 코드 상세 흐름

이 섹션은 각 `.py` 파일이 전체 워크플로우에서 어디에 놓이는지, 왜 해당 구조를 쓰는지, 어떤 입력과 출력을 주고받는지 기준으로 정리합니다.

### 루트 파일

#### [main.py](main.py)

콘솔 실행 진입점입니다. 사용자가 터미널에서 `python main.py` 또는 `python main.py --demo`를 실행했을 때 전체 흐름을 시작합니다.

핵심 역할:

- 사용자 프로필을 기본값, JSON 파일, 수동 입력 중 하나로 준비합니다.
- 검색 키워드를 입력받습니다.
- [graphs/job_graph.py](graphs/job_graph.py)의 `run_job_search_workflow()`를 호출해 LangGraph 워크플로우를 실행합니다.
- 최종 상태에서 `evaluation_results`와 `summary`를 꺼내 JSON, CSV, Markdown으로 저장합니다.
- 콘솔에 결과 테이블을 출력합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `load_user_profile(filepath=None)` | 사용자 프로필 JSON을 읽거나 테스트용 기본 프로필을 반환 |
| `get_user_input()` | 콘솔에서 실행 옵션, 프로필, 검색 직무를 입력받음 |
| `main()` | 대화형 콘솔 모드 실행 |
| `demo_mode()` | 입력 없이 고정 프로필과 `AI 개발자` 키워드로 실행 |

왜 이렇게 구성했는가:

- 콘솔 모드는 Streamlit UI 없이도 핵심 LangGraph/LangChain 흐름을 테스트할 수 있어야 합니다.
- `main.py`는 비즈니스 로직을 직접 처리하지 않고 `graphs`, `utils`에 위임합니다. 그래서 실행 방식이 바뀌어도 크롤링, 평가, 저장 로직은 재사용됩니다.
- `sys.path.insert()`는 루트 기준 import를 보장하기 위한 장치입니다. 현재 프로젝트는 패키지 설치형 구조가 아니므로 직접 실행 시 import 경로가 흔들릴 수 있습니다.

실행 흐름:

```text
get_user_input()
  -> run_job_search_workflow(keyword, user_profile)
  -> save_results_as_json()
  -> save_results_as_csv()
  -> generate_markdown_report()
  -> print_table_format()
```

#### [config.py](config.py)

프로젝트 전역 설정을 모아둔 파일입니다.

핵심 설정:

| 변수 | 의미 |
| ---- | ---- |
| `BASE_URL`, `SEARCH_BASE_URL` | 사람인 기본 URL과 검색 URL |
| `HEADERS` | 크롤링 요청 시 사용할 User-Agent |
| `LLM_MODEL` | 평가에 사용할 OpenAI 모델명 |
| `LLM_TEMPERATURE` | JSON 응답 안정성을 위한 낮은 temperature |
| `REQUEST_TIMEOUT`, `MAX_RETRIES` | HTTP 요청 관련 설정 |
| `DATA_DIR`, `RESULTS_DIR` | 결과 저장 경로 |
| `MAX_PAGES` | 미니 프로젝트에서 크롤링할 최대 페이지 수 |

왜 이렇게 구성했는가:

- URL, 모델명, 저장 경로처럼 여러 파일에서 공유하는 값을 한 곳에서 관리하기 위해 사용합니다.
- `load_dotenv()`를 통해 `.env`의 `OPENAI_API_KEY`를 LangChain/OpenAI 클라이언트가 사용할 수 있게 합니다.
- `RESULTS_DIR`는 import 시점에 자동 생성되어 결과 저장 함수가 디렉터리 유무를 크게 신경 쓰지 않아도 됩니다.

### app 폴더

Streamlit 웹앱과 시각화 화면을 담당합니다. 콘솔 모드와 같은 LangGraph 흐름을 사용하지만, 입력과 결과 표시를 웹 화면에 맞게 확장합니다.

#### [app/streamlit_app.py](app/streamlit_app.py)

Streamlit 앱의 메인 진입점입니다.

핵심 역할:

- 페이지 설정과 CSS 테마를 적용합니다.
- 지원자 프로필 입력 폼을 렌더링합니다.
- 검색 직무를 입력받습니다.
- LangGraph 진행 상태를 단계별로 표시합니다.
- 워크플로우 실행 후 결과 파일을 저장하고 다운로드 버튼을 제공합니다.
- 결과 대시보드를 렌더링합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `apply_xai_theme()` | Streamlit 기본 UI에 다크 테마 CSS 적용 |
| `render_shell_intro()` | 상단 내비게이션과 첫 화면 렌더링 |
| `render_profile_intro()` | 프로필 입력 섹션 설명 렌더링 |
| `build_user_profile()` | 입력 폼 값을 `user_profile` dict로 변환 |
| `split_comma_text(value)` | 쉼표 입력 문자열을 리스트로 정리 |
| `render_status(status_area, status)` | 단계별 진행 상태를 metric으로 표시 |
| `render_graph(graph_area, status)` | 3D LangGraph 흐름도를 다시 렌더링 |
| `main()` | Streamlit 앱 전체 실행 |

왜 이렇게 구성했는가:

- Streamlit은 페이지가 상호작용마다 다시 실행되므로, UI 렌더링 함수와 데이터 구성 함수를 분리해 흐름을 읽기 쉽게 만들었습니다.
- `run_job_search_workflow_with_progress()`를 사용해 기존 LangGraph 노드 함수를 재사용하면서 화면 상태만 추가로 갱신합니다.
- 결과 저장은 콘솔 모드와 같은 [utils/output_formatter.py](utils/output_formatter.py)를 사용합니다. 즉, UI만 다르고 산출물 형식은 동일합니다.

실행 흐름:

```text
사용자 프로필 입력
  -> 검색 키워드 입력
  -> 워크플로우 실행 버튼
  -> run_job_search_workflow_with_progress()
  -> 결과 파일 저장
  -> render_dashboard()
  -> 다운로드 버튼 생성
```

#### [app/dashboard.py](app/dashboard.py)

LangGraph 실행 결과를 Streamlit 표, metric, expander로 보여주는 대시보드 파일입니다.

핵심 역할:

- 수집 공고 수, 전처리 후 공고 수, 평가 완료 공고 수를 표시합니다.
- 적합/보완필요/부적합 개수를 표시합니다.
- 추천 공고 TOP 3, 부족 스킬, 학습 우선순위를 표로 보여줍니다.
- 공고별 상세 평가 결과를 expander로 제공합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `_format_cell_for_table(value)` | list/dict/None 값을 Streamlit 표에 안전한 문자열로 변환 |
| `_format_rows_for_table(rows)` | 표 전체 행을 평탄화 |
| `_build_evaluation_summary_rows(evaluation_results)` | 상세 평가 표의 핵심 컬럼만 구성 |
| `_render_list(label, values)` | 스킬/자격증 같은 리스트 값을 출력 |
| `_render_check(label, value)` | 판단 설명 값을 출력 |
| `render_dashboard(final_state)` | 최종 상태를 받아 전체 대시보드 렌더링 |

왜 이렇게 구성했는가:

- Streamlit `st.dataframe()`은 내부적으로 pyarrow 변환을 사용합니다. list/dict가 섞이면 변환 오류가 날 수 있어 문자열로 평탄화합니다.
- 상세 정보는 한 화면에 모두 펼치면 복잡하므로 expander로 숨겨 사용자가 필요한 공고만 열어보게 합니다.

#### [app/graph_visualizer.py](app/graph_visualizer.py)

LangGraph 실행 흐름을 Three.js 기반 3D HTML로 생성하고 Streamlit iframe에 삽입합니다.

핵심 역할:

- 워크플로우 단계를 `NODE_STEPS`로 정의합니다.
- 각 단계의 데이터 계약을 `NODE_CONTRACTS`에 정리합니다.
- 현재 실행 상태에 따라 완료/진행중/실패/대기 색상을 계산합니다.
- Three.js 장면을 포함한 HTML 파일을 생성합니다.
- 생성된 HTML을 `app/_generated/langgraph_space_flow.html`에 저장하고 iframe으로 보여줍니다.

주요 데이터:

| 이름 | 의미 |
| ---- | ---- |
| `NODE_STEPS` | START부터 END까지 화면에 표시할 단계 목록 |
| `NODE_CONTRACTS` | 각 단계의 module, role, input, output, state reads/writes 설명 |

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `render_langgraph_flow(status=None)` | 상태값을 받아 3D 흐름도 HTML을 생성하고 iframe 렌더링 |

왜 이렇게 구성했는가:

- Streamlit 자체는 3D 렌더링 엔진이 없으므로 iframe 안에 독립 HTML/JS를 넣는 방식이 가장 단순합니다.
- LangGraph 학습용 프로젝트이므로 단순한 진행률 표시보다 “각 노드가 어떤 state를 읽고 쓰는지”를 함께 보여주는 것이 목적에 맞습니다.
- `NODE_CONTRACTS`는 코드 실행과 별개로 학습자가 데이터 흐름을 이해하기 위한 문서형 메타데이터입니다.

#### [app/__init__.py](app/__init__.py)

현재 내용은 비어 있습니다. `app` 폴더를 Python 패키지처럼 인식할 수 있게 두는 파일입니다.

왜 사용하는가:

- `from app.dashboard import render_dashboard` 같은 import를 안정적으로 사용하기 위한 관례적 파일입니다.
- 지금은 별도 초기화 로직이 필요 없으므로 비워두는 것이 적절합니다.

### crawlers 폴더

사람인 검색 결과 페이지에서 공고 목록을 수집하는 계층입니다. 외부 웹사이트 구조에 직접 의존하는 코드는 이 폴더에 모읍니다.

#### [crawlers/saramin_crawler.py](crawlers/saramin_crawler.py)

검색 URL 생성, HTTP 요청, HTML 파싱, 공고 정보 추출을 담당합니다.

핵심 역할:

- 검색어와 페이지 번호를 사람인 검색 URL로 변환합니다.
- `requests`로 검색 결과 HTML을 가져옵니다.
- `BeautifulSoup`으로 공고 카드 요소를 찾습니다.
- 회사명, 공고명, 상세 URL, 지역, 경력, 학력, 근무형태, 마감일, 요구 스킬을 추출합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `generate_search_url(keyword, page=1)` | 검색어를 URL 인코딩해 사람인 검색 URL 생성 |
| `build_absolute_url(relative_url)` | 상대 경로를 절대 URL로 변환 |
| `crawl_saramin_jobs(keyword, max_pages=MAX_PAGES)` | 여러 페이지의 공고를 수집 |
| `_extract_job_info(job_item)` | HTML 공고 카드 하나에서 필드 추출 |

왜 이렇게 구성했는가:

- URL 생성과 HTML 추출을 함수로 나누면 사람인 URL 규칙이나 selector가 바뀌었을 때 수정 범위가 작아집니다.
- `job_items = soup.select("div.item_recruit, div.cell.job_item")`처럼 selector를 복수로 둔 이유는 사람인 HTML 구조가 바뀔 가능성이 있기 때문입니다.
- 상세 페이지 본문 크롤링은 아직 포함하지 않습니다. 현재는 목록 페이지에서 노출되는 정보만으로 LLM 평가를 수행합니다.

데이터 흐름:

```text
keyword
  -> generate_search_url()
  -> requests.get()
  -> BeautifulSoup(response.text)
  -> soup.select(...)
  -> _extract_job_info()
  -> List[Dict]
```

### chains 폴더

LangChain 또는 체인 형태의 처리 단계를 담는 계층입니다. 크롤링된 데이터를 LLM이 평가할 수 있게 정리하고, 평가 결과를 요약합니다.

#### [chains/preprocess_chain.py](chains/preprocess_chain.py)

크롤링 결과를 LLM 평가에 적합한 형태로 정제합니다.

핵심 역할:

- 필수 필드가 부족한 공고를 제거합니다.
- 회사명 + 공고명 기준으로 중복 공고를 제거합니다.
- 문자열 공백과 빈값을 정리합니다.
- 요구 스킬 중복을 제거합니다.
- LLM 프롬프트에 넣을 `job_description` 문자열을 생성합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `filter_invalid_jobs(jobs)` | 회사명/공고명 등 필수 정보가 없는 공고 제거 |
| `remove_duplicate_jobs(jobs)` | 회사명 + 공고명 기준 중복 제거 |
| `preprocess_jobs(jobs)` | 필드 정제와 `job_description` 생성 |
| `_generate_job_description(job)` | 공고 dict를 LLM이 읽기 쉬운 텍스트로 변환 |
| `run_preprocess_pipeline(jobs)` | 전처리 전체 파이프라인 실행 |

왜 이렇게 구성했는가:

- LLM에 원본 dict를 그대로 넣는 것보다 자연어 설명으로 바꾸면 프롬프트가 안정적입니다.
- 중복 제거를 먼저 하면 같은 공고에 대해 LLM API를 반복 호출하는 비용을 줄일 수 있습니다.
- 필드 정제는 뒤 단계에서 `.strip()`, `.join()` 같은 처리를 안전하게 하기 위한 준비 작업입니다.

처리 순서:

```text
raw_jobs
  -> filter_invalid_jobs()
  -> remove_duplicate_jobs()
  -> preprocess_jobs()
  -> processed_jobs + job_description
```

#### [chains/filter_chain.py](chains/filter_chain.py)

정제된 공고를 사용자 프로필과 비교해 LLM 평가를 실행합니다.

핵심 역할:

- `ChatOpenAI` 객체를 생성합니다.
- [prompts/filter_prompt.py](prompts/filter_prompt.py)의 프롬프트/파서 체인을 가져옵니다.
- 사용자 프로필과 공고 설명을 프롬프트 입력값으로 구성합니다.
- 공고별 평가 결과 JSON에 회사명, 공고명, URL, index를 다시 붙입니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `create_filter_jobs_chain(llm=None)` | 공고 평가용 LangChain 체인 생성 |
| `evaluate_job(user_profile, job, filter_chain)` | 공고 1개 평가 |
| `evaluate_jobs(user_profile, jobs)` | 전체 공고를 순회하며 평가 |

왜 이렇게 구성했는가:

- LLM 호출 코드를 별도 체인으로 분리하면 콘솔, Streamlit, LangGraph 어디서든 같은 평가 방식을 재사용할 수 있습니다.
- `temperature=0.3`은 평가 결과가 매번 크게 흔들리지 않고 JSON 형식을 유지하도록 돕습니다.
- 공고별 `time.sleep(1)`은 API 호출 제한과 과도한 요청을 피하기 위한 완충 장치입니다.

#### [chains/summary_chain.py](chains/summary_chain.py)

공고별 평가 결과를 모아 전체 통계와 학습 추천을 생성합니다.

핵심 역할:

- 적합/보완필요/부적합 개수를 집계합니다.
- 지원 추천 단계별 개수를 집계합니다.
- 적합도 점수 기준 추천 공고 TOP 3를 뽑습니다.
- 자주 부족한 핵심 스킬, 우대 스킬, 자격증을 계산합니다.
- 학습 우선순위와 단계별 학습 경로를 만듭니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `summarize_results(user_profile, evaluation_results)` | 평가 결과 전체 요약 |
| `_generate_learning_path(user_profile, missing_core_skills, missing_certs)` | 학습 단계 추천 |
| `print_summary(summary)` | 콘솔용 요약 출력 |

왜 이렇게 구성했는가:

- 공고별 평가만 있으면 사용자가 “그래서 무엇을 먼저 해야 하는지” 판단하기 어렵습니다.
- `Counter`를 사용해 여러 공고에서 반복 등장하는 부족 역량을 우선순위로 바꿉니다.
- 추천 공고와 학습 경로를 함께 제공해 즉시 지원과 보완 학습을 나눠 볼 수 있습니다.

### graphs 폴더

LangGraph 워크플로우를 정의하는 계층입니다. 이 프로젝트의 중심 제어 흐름입니다.

#### [graphs/job_graph.py](graphs/job_graph.py)

크롤링, 전처리, LLM 평가, 요약을 LangGraph 노드로 연결합니다.

핵심 역할:

- `JobSearchState`로 그래프가 공유하는 상태 구조를 정의합니다.
- `StateGraph`에 노드를 등록합니다.
- 노드 간 edge를 정의합니다.
- 콘솔용 전체 실행 함수와 Streamlit 진행 표시용 실행 함수를 제공합니다.

주요 타입:

| 이름 | 의미 |
| ---- | ---- |
| `JobSearchState` | `keyword`, `user_profile`, `raw_jobs`, `processed_jobs`, `evaluation_results`, `summary`, `error`를 담는 상태 dict |

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `create_job_search_graph()` | LangGraph 노드와 edge를 정의하고 compile |
| `crawl_jobs_node(state)` | 사람인 공고 크롤링 후 `state.raw_jobs` 갱신 |
| `preprocess_jobs_node(state)` | 전처리 후 `state.processed_jobs` 갱신 |
| `filter_jobs_node(state)` | LLM 평가 후 `state.evaluation_results` 갱신 |
| `summarize_result_node(state)` | 요약 후 `state.summary` 갱신 |
| `run_job_search_workflow(keyword, user_profile)` | 콘솔/일반 실행용 그래프 실행 |
| `run_job_search_workflow_with_progress(...)` | Streamlit 상태 표시용 순차 실행 |

왜 LangGraph를 사용하는가:

- 이 프로젝트는 단순 함수 호출보다 “상태가 단계별로 어떻게 바뀌는지”를 학습하는 목적이 큽니다.
- LangGraph의 `StateGraph`는 각 노드가 동일한 state를 읽고 갱신하는 구조를 명확하게 보여줍니다.
- 이후 조건 분기, 재시도, 에러 처리, 사람 검토 단계 등을 추가하기 쉽습니다.

그래프 구조:

```text
JobSearchState 초기화
  -> crawl_jobs_node
  -> preprocess_jobs_node
  -> filter_jobs_node
  -> summarize_result_node
  -> END
```

Streamlit용 진행 표시 흐름:

```text
검색 URL 생성 완료 표시
  -> crawl_jobs_node 실행/상태 표시
  -> preprocess_jobs_node 실행/상태 표시
  -> filter_jobs_node 실행/상태 표시
  -> summarize_result_node 실행/상태 표시
```

### prompts 폴더

LLM에게 어떤 기준으로 평가를 시킬지 정의하는 계층입니다.

#### [prompts/filter_prompt.py](prompts/filter_prompt.py)

공고별 적합성 평가 프롬프트와 JSON 파서를 구성합니다.

핵심 역할:

- LLM 응답 구조를 `JobEvaluation` Pydantic 모델로 정의합니다.
- 시스템 프롬프트에 평가 기준, 점수 기준, 신입 평가 기준, 분석 항목을 명시합니다.
- 사용자 프롬프트에 사용자 정보와 공고 설명을 주입합니다.
- `JsonOutputParser`로 JSON 응답을 파싱합니다.
- `prompt | llm | parser` 형태의 LangChain 체인을 만듭니다.

주요 클래스/함수:

| 이름 | 역할 |
| ---- | ---- |
| `JobEvaluation` | LLM이 반환해야 하는 평가 JSON 스키마 |
| `create_filter_prompt()` | `ChatPromptTemplate` 생성 |
| `create_filter_chain(llm)` | 프롬프트, LLM, JSON 파서를 연결 |

왜 이렇게 구성했는가:

- LLM에게 “좋아 보인다” 수준의 자유 응답을 받으면 후처리와 표 렌더링이 어렵습니다.
- JSON 스키마를 강제하면 [chains/summary_chain.py](chains/summary_chain.py), [app/dashboard.py](app/dashboard.py), [utils/output_formatter.py](utils/output_formatter.py)가 같은 필드를 안정적으로 사용할 수 있습니다.
- 점수 기준과 판정 기준을 프롬프트 안에 명시해 평가 결과의 일관성을 높입니다.

체인 구조:

```text
ChatPromptTemplate
  -> ChatOpenAI
  -> JsonOutputParser
  -> Dict 형태 평가 결과
```

### models 폴더

프로젝트에서 다루는 주요 데이터 구조를 Pydantic 모델로 정의합니다.

#### [models/schemas.py](models/schemas.py)

사용자 프로필, 크롤링된 공고, 평가 결과의 스키마를 정의합니다.

핵심 클래스:

| 클래스 | 역할 |
| ------ | ---- |
| `UserProfile` | 이름, 보유 스킬, 자격증, 희망 조건, 경력, 관심 직무 |
| `JobPosting` | 사람인 목록에서 수집한 공고 정보 |
| `EvaluationResult` | LLM 평가 결과 |

왜 Pydantic을 사용하는가:

- 데이터 필드의 의미와 타입을 한 곳에서 문서화할 수 있습니다.
- `Field(description=...)` 덕분에 각 필드가 어떤 값을 의미하는지 코드만 봐도 이해하기 쉽습니다.
- 나중에 API 서버나 더 엄격한 검증을 붙일 때 현재 스키마를 그대로 확장할 수 있습니다.

현재 사용상 특징:

- 일부 흐름은 Pydantic 객체가 아니라 dict를 직접 사용합니다. 이 프로젝트는 학습용 데모라 가벼운 dict 흐름을 유지하면서, `schemas.py`는 데이터 계약 문서와 확장 기반 역할을 합니다.
- `JobPosting`의 `requirements`, `preferred`는 상세 페이지 크롤링을 추가할 때 활용할 수 있도록 미리 열어둔 필드입니다.

### tools 폴더

LangChain Tool로 외부 기능을 감싸는 계층입니다.

#### [tools/saramin_tool.py](tools/saramin_tool.py)

크롤링 함수를 LangChain `@tool`로 래핑합니다.

핵심 역할:

- [crawlers/saramin_crawler.py](crawlers/saramin_crawler.py)의 `crawl_saramin_jobs()`를 `search_saramin_jobs()`라는 Tool로 노출합니다.
- LangChain Agent 또는 Tool 호출 기반 체인에서 사람인 검색 기능을 사용할 수 있게 합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `search_saramin_jobs(keyword)` | 검색어를 받아 사람인 공고 리스트 반환 |

왜 이렇게 구성했는가:

- 크롤링 함수 자체는 순수 함수로 유지하고, LangChain 전용 래퍼만 별도로 둡니다.
- 이렇게 하면 일반 Python 실행, LangGraph 노드, LangChain Agent가 같은 크롤링 로직을 공유할 수 있습니다.
- 현재 LangGraph 메인 흐름은 직접 `crawl_saramin_jobs()`를 호출하지만, Agent 기반 구조를 실험할 때 이 Tool을 사용할 수 있습니다.

### utils 폴더

결과 저장과 콘솔 출력처럼 여러 실행 방식에서 공통으로 쓰는 보조 기능을 담습니다.

#### [utils/output_formatter.py](utils/output_formatter.py)

평가 결과를 JSON, CSV, Markdown으로 저장하고 콘솔 표로 출력합니다.

핵심 역할:

- 평가 전체 결과와 요약을 JSON으로 저장합니다.
- 핵심 컬럼을 CSV 표로 저장합니다.
- 사용자 정보, 통계, 추천 공고, 학습 계획, 상세 평가를 Markdown 보고서로 저장합니다.
- 콘솔에서 빠르게 볼 수 있는 표 형식으로 출력합니다.

주요 함수:

| 함수 | 역할 |
| ---- | ---- |
| `save_results_as_json(evaluation_results, summary, output_dir="data/results")` | 전체 결과 저장 |
| `save_results_as_csv(evaluation_results, output_dir="data/results")` | 표 형태 결과 저장 |
| `generate_markdown_report(user_profile, evaluation_results, summary, output_dir="data/results")` | 사람이 읽기 좋은 보고서 생성 |
| `print_table_format(evaluation_results, limit=10)` | 콘솔 표 출력 |

왜 이렇게 구성했는가:

- 콘솔 모드와 Streamlit 모드가 같은 저장 방식을 사용해야 결과물이 일관됩니다.
- JSON은 전체 데이터 보존용, CSV는 스프레드시트 분석용, Markdown은 사람이 읽는 보고서용으로 역할이 다릅니다.
- 저장 파일명에 timestamp를 넣어 이전 실행 결과를 덮어쓰지 않게 합니다.

### 전체 코드 연결 관계

아래는 실제 import와 호출 기준으로 본 연결 관계입니다.

```text
main.py
  -> graphs.job_graph.run_job_search_workflow
  -> utils.output_formatter.*

app/streamlit_app.py
  -> graphs.job_graph.run_job_search_workflow_with_progress
  -> app.graph_visualizer.render_langgraph_flow
  -> app.dashboard.render_dashboard
  -> utils.output_formatter.*

graphs/job_graph.py
  -> crawlers.saramin_crawler.crawl_saramin_jobs
  -> chains.preprocess_chain.run_preprocess_pipeline
  -> chains.filter_chain.evaluate_jobs
  -> chains.summary_chain.summarize_results

chains/filter_chain.py
  -> prompts.filter_prompt.create_filter_chain
  -> langchain_openai.ChatOpenAI

tools/saramin_tool.py
  -> crawlers.saramin_crawler.crawl_saramin_jobs
```

핵심 데이터 변환 흐름:

```text
keyword: str
user_profile: Dict
  |
  v
raw_jobs: List[Dict]
  |
  v
processed_jobs: List[Dict + job_description]
  |
  v
evaluation_results: List[Dict]
  |
  v
summary: Dict
  |
  v
JSON / CSV / Markdown / Streamlit Dashboard
```

## 실행 준비

### 1. 가상환경 준비

Windows PowerShell 예시:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. 의존성 설치

```powershell
python -m pip install -r requirements.txt
```

### 3. 환경 변수 설정

프로젝트 루트의 `.env`에 OpenAI API 키를 넣습니다.

```env
OPENAI_API_KEY=your_api_key_here
```

평가 체인은 [config.py](config.py)의 `LLM_MODEL`과 `LLM_TEMPERATURE`를 사용합니다. 현재 기본 모델은 `gpt-4o-mini`입니다.

## 실행 방법

### 콘솔 모드

```powershell
python main.py
```

콘솔 모드는 다음 입력 방식을 제공합니다.

1. 코드에 정의된 기본 프로필 사용
2. JSON 프로필 파일 로드
3. 수동 프로필 입력

JSON 파일 로드 선택 시 기본 예시 경로는 `data/user_profile.json`입니다.

### 데모 모드

```powershell
python main.py --demo
```

미리 정의된 프로필과 `AI 개발자` 검색어로 워크플로우를 바로 실행합니다.

### Streamlit 웹앱

```powershell
python -m streamlit run app/streamlit_app.py
```

기본 접속 주소:

```text
http://localhost:8501
```

웹앱에서 입력하는 값:

- 이름
- 보유 스킬
- 자격증
- 희망 지역
- 희망 근무형태
- 최종 학력
- 경력
- 관심 직무
- 검색할 직무

## 입력 프로필 형식

사용자 프로필은 아래 형태의 dict 또는 JSON을 사용합니다.

```json
{
  "name": "홍길동",
  "skills": ["Python", "LangChain", "SQL", "FastAPI"],
  "certifications": ["정보처리기사"],
  "preferred_employment_types": ["정규직", "계약직"],
  "preferred_locations": ["서울", "경기"],
  "education": "학사",
  "career_level": "신입",
  "interested_jobs": ["AI 개발자", "백엔드 개발자"]
}
```

필드 의미는 [models/schemas.py](models/schemas.py)의 `UserProfile`에서 확인할 수 있습니다.

## 크롤링 범위

현재 크롤러는 사람인 검색 결과 목록에서 확인 가능한 정보를 수집합니다.

```python
{
    "company": "회사명",
    "title": "공고명",
    "url": "공고 상세 URL",
    "location": "근무지역",
    "career": "경력",
    "education": "학력 또는 None",
    "employment_type": "근무형태",
    "deadline": "마감일",
    "required_skills": ["검색 결과에 노출된 태그"]
}
```

현재 목록 selector:

```python
job_items = soup.select("div.item_recruit, div.cell.job_item")
```

자격요건과 우대사항 상세 본문은 상세 페이지에서 별도로 크롤링하지 않습니다. 목록에서 얻은 정보가 제한적이면 LLM 평가는 그 범위 안에서만 판단합니다.

## 평가 결과 형식

[prompts/filter_prompt.py](prompts/filter_prompt.py)는 LLM 응답을 JSON으로 파싱하도록 구성되어 있습니다. 공고별 평가 결과에는 다음 값이 포함됩니다.

```json
{
  "index": 1,
  "company": "회사명",
  "title": "AI 개발자",
  "url": "https://www.saramin.co.kr/...",
  "result": "보완필요",
  "fit_score": 85,
  "apply_level": "보완후지원",
  "matched_skills": ["Python", "SQL"],
  "missing_core_skills": ["PyTorch"],
  "missing_optional_skills": ["Docker"],
  "missing_certs": [],
  "requirements_check": "자격요건 판단",
  "preferred_check": "우대사항 판단",
  "career_check": "경력 조건 판단",
  "education_check": "학력 조건 판단",
  "employment_type_check": "근무형태 판단",
  "location_check": "근무지역 판단",
  "junior_friendly": true,
  "junior_reason": "신입 지원 가능성 설명",
  "reason": "최종 판단 이유",
  "study_priority": ["PyTorch", "Docker"]
}
```

판정 기준:

| 점수            | 판정     | 지원 추천  |
| --------------- | -------- | ---------- |
| 90 이상         | 적합     | 즉시지원   |
| 70 이상 90 미만 | 보완필요 | 보완후지원 |
| 70 미만         | 부적합   | 비추천     |

## 결과 저장

실행 결과는 기본적으로 `data/results/` 아래에 저장됩니다.

```text
data/results/
├── evaluation_results_YYYYMMDD_HHMMSS.json
├── evaluation_results_YYYYMMDD_HHMMSS.csv
└── report_YYYYMMDD_HHMMSS.md
```

| 파일     | 내용                                                    |
| -------- | ------------------------------------------------------- |
| JSON     | 평가 결과 전체, 생성 시각, 요약 정보                    |
| CSV      | 핵심 평가 컬럼을 표 형태로 저장                         |
| Markdown | 사용자 정보, 통계, 추천 공고, 학습 계획, 상위 상세 평가 |

## Streamlit 화면

웹앱은 사람인 미니 프로젝트의 실행 결과뿐 아니라 LangGraph 실행 흐름을 함께 보여주는 데모 화면을 제공합니다.

3D 화면은 [app/graph_visualizer.py](app/graph_visualizer.py)가 HTML을 생성해 `app/_generated/langgraph_space_flow.html`에 저장한 뒤 iframe으로 렌더링합니다. 화면 하단의 `Data contract flow` 레일은 각 단계의 input/output 타입 흐름을 보여주며, 노드나 타입 카드를 선택하면 해당 단계가 읽고 쓰는 `JobSearchState` 키까지 상세 패널에서 확인할 수 있습니다. Three.js와 OrbitControls는 CDN에서 불러오므로 브라우저가 외부 리소스에 접근할 수 있어야 합니다.

현재 3D 화면은 다음과 같은 우주감 요소를 포함합니다.

- 다층 성운 오버레이(보라, 파랑, 분홍, 주황, 노랑 계열)
- 더 밝고 선명하게 보이는 별 레이어
- 보정된 안개와 조명으로 별빛이 어두운 배경에서도 눈에 띄도록 구성

- 현재 LangGraph 워크플로우와 LangChain tool 래퍼는 2페이지 수집으로 호출합니다.
- 크롤링 요청 사이에는 2초 대기 시간이 있습니다.
- 공고별 LLM 평가 호출 사이에는 1초 대기 시간이 있습니다.

## 제한 사항

- 사람인 HTML 구조가 바뀌면 selector 수정이 필요할 수 있습니다.
- 현재 구현은 검색 결과 목록 위주이며 상세 공고 본문 크롤링은 포함하지 않습니다.
- LLM 평가는 공고 수만큼 API 호출을 발생시켜 시간과 비용이 늘어날 수 있습니다.
- OpenAI API 키가 없거나 외부 네트워크가 막혀 있으면 평가 단계가 실패합니다.
- 3D UI는 WebGL, Three.js CDN 로딩 상태, 브라우저의 GPU/배경 렌더링 설정에 영향을 받습니다.

## 문제 해결

### `ModuleNotFoundError: No module named 'bs4'`

```powershell
python -m pip install beautifulsoup4
```

### `streamlit` 명령을 찾지 못함

```powershell
python -m pip install streamlit
python -m streamlit run app/streamlit_app.py
```

### 공고 항목을 찾지 못함

사람인 검색 결과 HTML 구조가 바뀌었는지 [crawlers/saramin_crawler.py](crawlers/saramin_crawler.py)의 selector를 확인합니다.

### Streamlit dataframe 변환 오류

LLM 응답에는 list 또는 dict 값이 섞일 수 있습니다. 웹 대시보드는 [app/dashboard.py](app/dashboard.py)에서 표 렌더링 전에 중첩 값을 문자열로 변환합니다.

### 3D 흐름도가 보이지 않음

- 브라우저에서 WebGL이 활성화되어 있는지 확인합니다.
- 브라우저가 GPU 가속을 지원하는지 확인합니다.
- Three.js CDN 접근이 가능한지 확인합니다.
- Streamlit 서버 재시작 후 브라우저를 새로고침합니다.

## 작성 정보

- 최종 업데이트: 2026-05-26
- 용도: 사람인 미니 프로젝트를 활용한 LangChain/LangGraph 구조 설명용 데모
