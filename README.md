# 사람인 구인공고 필터링 시스템

사람인 채용공고를 크롤링하고, 사용자 이력과 비교해 LLM이 공고별 적합도를 평가하는 Python 미니 프로젝트입니다.

콘솔 실행과 Streamlit 웹앱 실행을 모두 지원합니다. Streamlit 웹앱에서는 LangGraph 진행상황, 3D 워크플로우 표면, 결과 대시보드, 결과 파일 다운로드를 확인할 수 있습니다.

---

## 핵심 기능

- 사람인 검색 결과 페이지 크롤링
- 검색어 기반 URL 자동 생성
- 회사명, 공고명, 지역, 경력, 학력, 근무형태, 마감일, 기술 태그 추출
- 공고 데이터 전처리 및 중복 제거
- LangChain + OpenAI 기반 공고 적합도 평가
- LangGraph 기반 워크플로우 실행
- 부족 기술, 부족 자격증, 학습 우선순위 분석
- JSON, CSV, Markdown 보고서 저장
- Streamlit 웹앱 UI
- Three.js 기반 3D LangGraph 워크플로우 표면
- 결과 대시보드 및 다운로드 버튼

---

## 프로젝트 구조

```text
saramin_project/
├── main.py                         # 콘솔 실행 진입점
├── config.py                       # 공통 설정
├── requirements.txt                # 의존성
├── .env                            # OpenAI API 키
│
├── app/
│   ├── __init__.py
│   ├── streamlit_app.py            # Streamlit 웹앱
│   ├── graph_visualizer.py         # Three.js 3D 흐름도
│   ├── dashboard.py                # 결과 대시보드
│   └── _generated/                 # 3D 흐름도 HTML 자동 생성
│
├── crawlers/
│   └── saramin_crawler.py          # 사람인 크롤러
│
├── chains/
│   ├── preprocess_chain.py         # 전처리
│   ├── filter_chain.py             # LLM 평가
│   └── summary_chain.py            # 결과 요약
│
├── graphs/
│   └── job_graph.py                # LangGraph 워크플로우
│
├── prompts/
│   └── filter_prompt.py            # LLM 프롬프트
│
├── models/
│   └── schemas.py                  # Pydantic 스키마
│
├── tools/
│   └── saramin_tool.py             # LangChain tool 래핑
│
├── utils/
│   └── output_formatter.py         # 결과 저장/출력
│
└── data/
    ├── user_profile.json           # 사용자 프로필 예시
    └── results/                    # 실행 결과 저장
```

---

## 실행 준비

### 1. 가상환경 활성화

```powershell
.\.venv\Scripts\activate
```

VS Code에서는 아래 인터프리터를 선택합니다.

```text
Ctrl + Shift + P
→ Python: Select Interpreter
→ .\.venv\Scripts\python.exe
```

### 2. 의존성 설치

```powershell
python -m pip install -r requirements.txt
```

`streamlit` 명령을 못 찾는 경우:

```powershell
python -m pip install streamlit
```

`bs4` 오류가 나는 경우:

```powershell
python -m pip install beautifulsoup4
```

현재 크롤러는 `html.parser`를 사용하므로 `lxml` 파서가 없어도 동작합니다.

### 3. OpenAI API 키 설정

`.env` 파일에 API 키를 입력합니다.

```env
OPENAI_API_KEY=your_api_key_here
```

---

## 실행 방법

### 콘솔 모드

```powershell
python main.py
```

실행 후 아래 메뉴 중 하나를 선택합니다.

```text
1. 기본 프로필 사용
2. JSON 파일에서 로드
3. 수동 입력
```

### 데모 모드

```powershell
python main.py --demo
```

### Streamlit 웹앱

```powershell
python -m streamlit run app/streamlit_app.py
```

브라우저 주소:

```text
http://localhost:8501
```

웹앱 입력 항목:

- 이름
- 보유 스킬
- 자격증
- 희망 지역
- 희망 근무형태
- 최종 학력
- 경력
- 관심 직무
- 검색할 직무

---

## LangGraph 워크플로우

```text
START
  ↓
crawl_jobs_node
  - 검색 URL 생성
  - 사람인 공고 크롤링
  ↓
preprocess_jobs_node
  - 불완전한 공고 제거
  - 중복 제거
  - LLM 평가용 텍스트 생성
  ↓
filter_jobs_node
  - 사용자 프로필과 공고 비교
  - LLM 적합도 평가
  - 원본 공고 정보 병합
  ↓
summarize_result_node
  - 평가 통계 생성
  - 추천 공고 TOP 3
  - 부족 기술 및 학습 우선순위 분석
  ↓
END
```

Streamlit 웹앱에서는 `run_job_search_workflow_with_progress()`가 각 노드를 순서대로 실행하면서 상태를 표시합니다.

상태 값:

```text
대기 / 진행중 / 완료 / 실패
```

---

## Streamlit 웹앱

Streamlit 앱은 기존 콘솔 로직을 다시 만들지 않고, 기존 크롤러/체인/LangGraph 노드를 그대로 재사용합니다.

```text
app/streamlit_app.py
  ↓
graphs/job_graph.py
  ↓
crawlers / chains / utils
```

웹앱 화면 구성:

- 사용자 프로필 입력 사이드바
- 검색어 입력
- LangGraph 3D 워크플로우 표면
- 단계별 진행상황 카드
- 결과 대시보드
- JSON/CSV/Markdown 다운로드 버튼

---

## 3D 워크플로우 표면

`app/graph_visualizer.py`는 Three.js로 LangGraph 흐름을 xAI 문서 기반의 어두운 3D 워크플로우 표면으로 시각화합니다.

표시 노드:

```text
START → URL → CRAWL → PREP → LLM → SUM → SAVE → END
```

시각화 요소:

- 태양/달 느낌의 시작/종료 노드
- 다양한 색상의 행성형 노드
- 단계 번호 표시
- 전체 진행률 숫자와 진행 바
- 상태별 색상 변화
- 행성 주변 위성 입자
- 노드 사이 데이터 입자 이동
- 메인 흐름선
- 다차원 네트워크 보조 라인
- 노드 클릭/터치 시 상세 정보 표시

상태별 색상:

```text
대기: muted gray
진행중: sunset orange
완료: white
실패: twilight violet
```

조작 방법:

```text
마우스/터치 드래그: 회전
마우스 휠/핀치: 확대 또는 축소
우클릭 드래그: 화면 이동
노드 클릭/터치: 노드 정보 확인
Front / Top / Side / Wide: 카메라 시점 변경
Pause / Play: 모션 일시정지 또는 재생
```

구현 메모:

- Streamlit 최신 API에 맞춰 `st.iframe()`을 사용합니다.
- 3D HTML은 `app/_generated/langgraph_space_flow.html`에 자동 생성됩니다.
- Three.js와 OrbitControls는 CDN에서 불러옵니다.
- 3D 화면이 보이지 않으면 브라우저 새로고침 또는 Streamlit 서버 재시작이 필요할 수 있습니다.
- 오프라인 환경에서는 CDN 로딩 문제로 3D 화면이 표시되지 않을 수 있습니다.

---

## 결과 대시보드

`app/dashboard.py`는 실행 결과를 Streamlit 화면에 정리해서 보여줍니다.

표시 항목:

- 전체 수집 공고 수
- 전처리 후 공고 수
- 평가 완료 공고 수
- 적합 공고 수
- 보완필요 공고 수
- 부적합 공고 수
- 추천 공고 TOP 3
- 부족 스킬 TOP 5
- 추천 학습 우선순위
- 상세 평가 결과

상세 평가 결과는 원본 JSON을 그대로 노출하지 않고 아래처럼 표시합니다.

```text
상세 평가 결과
├── 핵심 컬럼 요약 표
└── 공고별 상세 보기
    ├── 적합도 / 판정 / 지원추천
    ├── 판단 이유
    ├── 일치 스킬
    ├── 부족 핵심 스킬
    ├── 부족 우대 스킬
    ├── 부족 자격증
    ├── 학습 우선순위
    ├── 자격요건 / 우대사항 / 경력 / 학력 / 근무형태 / 지역 판단
    └── 공고 링크
```

Streamlit의 `st.dataframe()`은 내부적으로 PyArrow를 사용합니다. LLM 결과에 list/dict가 섞이면 Arrow 변환 오류가 날 수 있으므로, 대시보드 표시 전 모든 중첩 값을 읽기 쉬운 문자열로 변환합니다.

---

## 크롤링 추출 필드

현재 크롤러는 검색 결과 페이지에서 아래 필드를 추출합니다.

```python
{
    "company": "회사명",
    "title": "공고명",
    "url": "공고 상세 URL",
    "location": "근무지역",
    "career": "경력",
    "education": "학력",
    "employment_type": "근무형태",
    "deadline": "마감일",
    "required_skills": ["기술/직무 태그"]
}
```

현재 selector:

```python
job_items = soup.select("div.item_recruit, div.cell.job_item")
company_elem = job_item.select_one("strong.corp_name, div.corp_name")
title_elem = job_item.select_one("h2.job_tit a, h2.job_title a, a.job_tit")
condition_elems = job_item.select("div.job_condition > span")
deadline_elem = job_item.select_one("div.job_date span.date, span.deadline")
skill_elems = job_item.select("div.job_sector a, span.skill")
```

사람인 HTML 구조가 바뀌면 selector 수정이 필요할 수 있습니다.

---

## 평가 결과 예시

```json
{
  "index": 1,
  "company": "회사명",
  "title": "AI 개발자",
  "url": "https://www.saramin.co.kr/...",
  "fit_score": 85,
  "result": "보완필요",
  "apply_level": "보완후지원",
  "matched_skills": ["Python", "SQL"],
  "missing_core_skills": ["머신러닝"],
  "missing_optional_skills": ["Docker"],
  "missing_certs": [],
  "reason": "판단 이유",
  "study_priority": ["머신러닝", "Docker"]
}
```

---

## 결과 저장

실행 결과는 `data/results/`에 저장됩니다.

```text
data/results/
├── evaluation_results_YYYYMMDD_HHMMSS.json
├── evaluation_results_YYYYMMDD_HHMMSS.csv
└── report_YYYYMMDD_HHMMSS.md
```

파일 설명:

- JSON: 전체 평가 결과와 요약 정보
- CSV: 표 형태 평가 결과
- Markdown: 사용자 정보, 통계, 추천 공고, 부족 기술, 학습 계획 보고서

---

## 주요 변경 이력

### 1. 크롤러 안정화

- `lxml` 파서 대신 Python 내장 `html.parser` 사용
- 사람인 최신 구조인 `div.item_recruit` selector 대응
- 이전 구조인 `div.cell.job_item`도 함께 지원

### 2. 평가 결과 병합 오류 수정

LLM 평가 결과에 원본 공고 정보가 빠져 `KeyError: 'company'`가 발생하던 문제를 수정했습니다.

```python
result["company"] = job.get("company", "미상")
result["title"] = job.get("title", "공고명 미상")
result["url"] = job.get("url")
result["index"] = job.get("index", 0)
```

### 3. 보고서 저장 안정성 보강

요약 생성 실패 시에도 Markdown 보고서 생성 단계에서 바로 중단되지 않도록 기본값 처리를 추가했습니다.

### 4. Streamlit 웹앱 추가

추가 파일:

```text
app/__init__.py
app/streamlit_app.py
app/graph_visualizer.py
app/dashboard.py
```

### 5. 3D LangGraph 시각화 추가

- Three.js 기반 3D 워크플로우 표면
- 진행률 HUD
- 다양한 행성형 노드
- 위성 입자
- 데이터 흐름 입자
- 카메라 액션 버튼
- 노드 클릭 정보 표시

### 6. Streamlit 최신 API 대응

- `st.components.v1.html()` 대신 `st.iframe()` 사용
- `use_container_width=True` 대신 `width="stretch"` 사용

### 7. PyArrow dataframe 오류 처리

`st.dataframe()`에 list/dict가 포함된 데이터를 그대로 넘기면 PyArrow 변환 오류가 발생할 수 있습니다.

현재는 화면 표시 전에 list/dict 값을 문자열로 변환합니다.

---

## 자주 발생한 오류

### ModuleNotFoundError: No module named 'bs4'

```powershell
python -m pip install beautifulsoup4
```

### streamlit: The term 'streamlit' is not recognized

```powershell
python -m pip install streamlit
python -m streamlit run app/streamlit_app.py
```

### Couldn't find a tree builder with the features you requested: lxml

현재 코드는 `html.parser`를 사용하므로 최신 코드 기준으로 다시 실행합니다.

```powershell
python main.py
```

### 공고 항목을 찾을 수 없습니다

사람인 HTML 구조가 바뀌었을 가능성이 있습니다.

확인 파일:

```text
crawlers/saramin_crawler.py
```

### pyarrow.lib.ArrowTypeError

원인:

```text
st.dataframe()에 dict/list 또는 타입이 섞인 컬럼이 들어감
```

해결:

```text
app/dashboard.py에서 표시 전 문자열로 변환
```

### 3D 흐름도가 보이지 않음

가능한 원인:

- Three.js CDN 접속 실패
- Streamlit 서버가 이전 파일을 보고 있음
- 브라우저 캐시
- WebGL 비활성화

해결:

```powershell
python -m streamlit run app/streamlit_app.py
```

브라우저에서 `Ctrl + F5`로 강력 새로고침합니다.

---

## 개발 메모

- 크롤링 대상 사이트의 HTML 구조는 바뀔 수 있습니다.
- LLM 평가는 공고 수만큼 API 호출이 발생합니다.
- 현재 워크플로우는 기본적으로 최대 2페이지를 크롤링합니다.
- `config.py`의 `MAX_PAGES`로 기본 페이지 수를 조정할 수 있습니다.
- 사람인 요청 사이에는 `time.sleep(2)` 딜레이를 둡니다.
- 3D 흐름도는 `app/_generated/langgraph_space_flow.html`을 자동 생성합니다.
- Three.js는 CDN을 사용하므로 인터넷 연결이 필요할 수 있습니다.

---

## 향후 개선 아이디어

- 상세 페이지 크롤링으로 자격요건/우대사항 추출
- Streamlit UI 디자인 개선
- 사용자 프로필 저장/불러오기 기능
- SQLite 또는 PostgreSQL 저장
- API 호출 배치 처리 및 비용 절감
- FastAPI + React 기반 UI 분리
- React Flow 기반 LangGraph 노드 시각화
- Framer Motion 기반 노드 전환 애니메이션
- Three.js 3D 모션 고도화

---

## 작성 정보

- 최종 업데이트: 2026-05-22
- 버전: 1.3.0
- 용도: 학습용 미니 프로젝트
