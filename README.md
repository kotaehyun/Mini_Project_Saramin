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

- 최종 업데이트: 2026-05-23
- 용도: 사람인 미니 프로젝트를 활용한 LangChain/LangGraph 구조 설명용 데모
