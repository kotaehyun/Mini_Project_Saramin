# Python 코드 리뷰 학습 문서

이 문서는 프로젝트의 `.py` 파일을 처음 읽는 사람을 위한 전체 지도입니다. 각 폴더별 상세 설명은 해당 폴더의 `CODE_REVIEW.md`를 함께 보면 됩니다.

## 전체 흐름

이 프로젝트는 사람인 채용공고를 검색하고, 사용자 프로필과 비교해서 지원 적합도를 평가한 뒤 결과를 파일과 화면으로 보여주는 구조입니다.

```text
사용자 입력
  -> 사람인 공고 크롤링
  -> 공고 데이터 전처리
  -> LLM으로 적합도 평가
  -> 평가 결과 요약
  -> JSON / CSV / Markdown 저장
  -> CLI 또는 Streamlit 화면 출력
```

## 주요 실행 파일

### `main.py`

콘솔에서 실행하는 진입점입니다.

- `load_user_profile()`: JSON 파일 또는 기본값으로 사용자 프로필을 만듭니다.
- `get_user_input()`: 콘솔에서 사용자 정보를 입력받습니다.
- `main()`: 입력, 워크플로우 실행, 결과 저장, 콘솔 출력을 순서대로 처리합니다.
- `demo_mode()`: 입력 없이 테스트용 프로필로 전체 흐름을 실행합니다.

초보자 관점에서는 `main()`을 먼저 읽으면 전체 프로그램의 순서를 가장 쉽게 파악할 수 있습니다.

### `config.py`

프로젝트 전역 설정 파일입니다.

- 사람인 URL
- HTTP 요청 헤더
- LLM 모델명과 temperature
- 크롤링 제한값
- 결과 저장 경로

설정값을 한 파일에 모아두면 코드 여러 곳에서 같은 값을 반복하지 않아도 됩니다.

## 폴더별 역할

| 폴더 | 역할 |
| --- | --- |
| `app/` | Streamlit 웹 화면, 대시보드, 그래프 시각화 |
| `chains/` | 전처리, LLM 평가, 요약처럼 단계별 처리 로직 |
| `crawlers/` | 사람인 검색 결과 페이지 크롤링 |
| `graphs/` | LangGraph 워크플로우 연결 |
| `models/` | Pydantic 데이터 스키마 |
| `prompts/` | LLM 프롬프트와 출력 파서 |
| `tools/` | LangChain `@tool` 래퍼 |
| `utils/` | 결과 저장, 보고서 생성, 콘솔 출력 |

## 공부 순서 추천

1. `main.py`에서 전체 실행 순서를 본다.
2. `graphs/job_graph.py`에서 각 단계가 어떻게 이어지는지 본다.
3. `crawlers/saramin_crawler.py`에서 외부 데이터를 어떻게 가져오는지 본다.
4. `chains/preprocess_chain.py`에서 데이터를 LLM이 읽기 좋게 바꾸는 과정을 본다.
5. `prompts/filter_prompt.py`와 `chains/filter_chain.py`에서 LLM 호출 구조를 본다.
6. `chains/summary_chain.py`와 `utils/output_formatter.py`에서 결과를 어떻게 요약하고 저장하는지 본다.
7. `app/streamlit_app.py`에서 같은 기능을 웹 화면으로 연결하는 방식을 본다.

## 코드 리뷰 핵심 포인트

- 책임 분리가 비교적 명확합니다. 크롤링, 전처리, 평가, 요약, 출력이 다른 모듈에 나뉘어 있습니다.
- `state` 딕셔너리를 중심으로 데이터가 흐르기 때문에, 각 단계가 어떤 키를 읽고 쓰는지 추적하는 것이 중요합니다.
- LLM 응답은 외부 API 결과라 항상 안정적이라고 가정하면 안 됩니다. JSON 파싱, 누락 필드, 호출 실패 처리를 더 강화할 수 있습니다.
- 크롤링 코드는 웹사이트 HTML 구조 변경에 취약합니다. selector 변경 가능성을 염두에 두고 테스트 데이터나 예외 처리가 필요합니다.
- 현재 일부 import는 사용되지 않습니다. 예를 들어 `main.py`의 `UserProfile`, `tools/saramin_tool.py`의 `JobPosting`, `graphs/job_graph.py`의 상단 `json` import는 정리 후보입니다.

## 초보자가 기억할 개념

- `Dict`: 키와 값으로 이루어진 데이터 묶음입니다.
- `List[Dict]`: 딕셔너리가 여러 개 들어 있는 리스트입니다. 채용공고 목록처럼 씁니다.
- `TypedDict`: 딕셔너리 안에 어떤 키가 있어야 하는지 타입 힌트로 표현합니다.
- `Pydantic BaseModel`: 입력/출력 데이터 구조를 명확히 표현하는 모델입니다.
- `LangGraph`: 여러 처리 단계를 노드로 만들고 순서대로 실행하는 워크플로우 도구입니다.
- `LangChain chain`: 프롬프트, LLM, 파서를 파이프처럼 연결한 실행 단위입니다.
