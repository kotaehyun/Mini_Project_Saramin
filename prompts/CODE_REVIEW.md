# `prompts/` 코드 리뷰

`prompts/` 폴더는 LLM에게 어떤 역할을 줄지, 어떤 입력을 넘길지, 어떤 JSON 형식으로 답하게 할지를 정의합니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `filter_prompt.py` | 공고 적합도 평가용 프롬프트와 JSON 파서 체인 생성 |

## `filter_prompt.py`

### `JobEvaluation`

LLM 응답으로 기대하는 JSON 구조를 Pydantic 모델로 정의합니다.

이 모델은 LLM이 다음 정보를 반환하도록 유도합니다.

- 회사명, 공고명
- 최종 판정과 점수
- 지원 추천 수준
- 일치 스킬과 부족 스킬
- 자격요건, 우대사항, 경력, 학력, 근무형태, 지역 판단
- 신입 지원 가능 여부
- 최종 판단 이유
- 학습 우선순위

### `create_filter_prompt()`

LLM에게 보낼 `ChatPromptTemplate`을 만듭니다.

구성:

- `system_prompt`: LLM의 역할과 평가 기준을 설명합니다.
- `user_prompt`: 실제 사용자 정보와 공고 정보를 넣는 템플릿입니다.

### `create_filter_chain(llm)`

프롬프트, LLM, JSON 파서를 연결합니다.

```text
prompt
  -> llm
  -> JsonOutputParser
```

LangChain에서는 이처럼 `|` 연산자로 실행 단계를 연결할 수 있습니다.

## 공부 포인트

- LLM은 자유롭게 답하려는 경향이 있으므로 "반드시 JSON 형식"처럼 출력 형식을 강하게 지정합니다.
- `JsonOutputParser(pydantic_object=JobEvaluation)`는 JSON 형태로 파싱 가능한 응답을 기대합니다.
- 프롬프트 변수 이름은 `filter_chain.py`의 `chain_input` 키와 일치해야 합니다.

## 개선 후보

- 현재 프롬프트에는 포맷 지시가 텍스트로만 들어 있습니다. 파서의 format instruction을 프롬프트에 직접 넣으면 JSON 안정성을 더 높일 수 있습니다.
- `fit_score` 계산 기준은 프롬프트에 있지만 실제 계산은 LLM 판단에 맡겨져 있습니다. 점수 일관성이 중요하면 코드에서 계산하는 방식도 고려할 수 있습니다.
