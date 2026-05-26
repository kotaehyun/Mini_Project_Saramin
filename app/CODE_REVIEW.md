# `app/` 코드 리뷰

`app/` 폴더는 콘솔이 아니라 웹 화면에서 프로젝트를 실행하기 위한 Streamlit UI를 담당합니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `streamlit_app.py` | Streamlit 앱의 메인 화면과 실행 버튼 처리 |
| `dashboard.py` | 워크플로우 실행 결과를 표, 지표, 상세 보기로 출력 |
| `graph_visualizer.py` | LangGraph 흐름을 3D 시각화와 데이터 계약 표로 표현 |
| `__init__.py` | `app` 폴더를 Python 패키지로 인식시키는 파일 |

## `streamlit_app.py`

이 파일은 Streamlit 앱의 시작점입니다.

### 함수 구조

- `apply_xai_theme()`: Streamlit 기본 화면에 커스텀 CSS를 적용합니다.
- `render_shell_intro()`: 상단 내비게이션과 첫 화면 소개 영역을 만듭니다.
- `render_profile_intro()`: 지원자 프로필 입력 섹션 제목을 출력합니다.
- `build_user_profile()`: 입력 폼 값을 모아 사용자 프로필 딕셔너리를 만듭니다.
- `render_keyword_intro()`: 검색 키워드 입력 섹션을 출력합니다.
- `render_workflow_intro()`: 워크플로우 안내 영역과 상태 키를 출력합니다.
- `split_comma_text()`: 쉼표로 입력한 문자열을 리스트로 바꿉니다.
- `render_status()`: 단계별 진행 상태를 metric 카드로 보여줍니다.
- `render_graph()`: 현재 상태를 반영해서 그래프 시각화를 다시 그립니다.
- `main()`: 페이지 설정, 입력, 버튼 클릭, 워크플로우 실행, 결과 다운로드를 담당합니다.

### 데이터 흐름

```text
Streamlit 입력 폼
  -> build_user_profile()
  -> run_job_search_workflow_with_progress()
  -> save_results_as_json/csv/markdown
  -> render_dashboard()
  -> download_button
```

### 공부 포인트

- `st.session_state`를 쓰지 않고 지역 변수와 `st.empty()` placeholder로 화면을 갱신합니다.
- `status` 딕셔너리를 여러 함수에 넘겨 같은 상태를 그래프와 metric에 함께 반영합니다.
- CSS가 매우 길기 때문에, UI 스타일과 비즈니스 로직이 한 파일에 섞여 있습니다. 규모가 커지면 CSS 문자열 분리가 좋습니다.

## `dashboard.py`

워크플로우 실행 결과를 사람이 읽기 좋게 보여주는 파일입니다.

### 함수 구조

- `_format_cell_for_table()`: 리스트나 딕셔너리를 표에 넣기 좋은 문자열로 바꿉니다.
- `_format_rows_for_table()`: 여러 행 전체를 문자열 중심으로 변환합니다.
- `_order_evaluation_columns()`: 상세 평가 컬럼 순서를 조정합니다. 현재는 호출되지 않는 정리 후보입니다.
- `_build_evaluation_summary_rows()`: 상세 평가 결과에서 핵심 컬럼만 뽑아 표 행을 만듭니다.
- `_render_list()`: 리스트형 값을 Markdown 텍스트로 출력합니다.
- `_render_check()`: 조건 판단 값을 출력합니다.
- `_render_section_intro()`: 결과 섹션 헤더를 HTML로 출력합니다.
- `render_dashboard()`: 전체 결과 대시보드를 렌더링합니다.

### 공부 포인트

- UI에 바로 원본 딕셔너리를 넣지 않고, 표 출력용 형태로 가공합니다.
- Streamlit의 `dataframe`, `metric`, `expander`를 조합해 요약과 상세를 모두 제공합니다.
- 함수명 앞의 `_`는 "이 파일 내부에서 주로 쓰는 보조 함수"라는 관례입니다.

## `graph_visualizer.py`

LangGraph 흐름을 3D 화면과 데이터 계약 표로 보여주는 파일입니다.

### 핵심 상수

- `NODE_STEPS`: 워크플로우 노드 이름과 짧은 라벨입니다.
- `NODE_CONTRACTS`: 각 노드가 읽는 값, 쓰는 값, 입력 타입, 출력 타입을 설명합니다.

### 함수 구조

- `render_langgraph_flow(status=None)`: 현재 진행 상태를 받아 Three.js 기반 HTML을 생성하고 Streamlit iframe으로 표시합니다.

### 공부 포인트

- Python에서 HTML, CSS, JavaScript 문자열을 만든 뒤 Streamlit iframe에 넣는 방식입니다.
- `json.dumps(..., ensure_ascii=False)`로 Python 데이터를 JavaScript가 읽을 수 있는 JSON 문자열로 바꿉니다.
- 함수가 매우 길어 유지보수 난도가 높습니다. HTML 템플릿 파일 분리, JS 분리, CSS 분리를 고려할 수 있습니다.

## 개선 후보

- `streamlit_app.py`의 CSS와 화면 구성 HTML을 별도 파일이나 함수 그룹으로 더 쪼갤 수 있습니다.
- `graph_visualizer.py`는 시각화 코드와 데이터 계약 설명이 함께 있어 파일이 큽니다.
- `_order_evaluation_columns()`처럼 사용하지 않는 함수는 실제 사용하거나 제거하는 것이 좋습니다.
