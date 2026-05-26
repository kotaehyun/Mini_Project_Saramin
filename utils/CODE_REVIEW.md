# `utils/` 코드 리뷰

`utils/` 폴더는 핵심 비즈니스 로직보다 보조 기능을 담당합니다. 이 프로젝트에서는 평가 결과를 저장하고 콘솔에 출력하는 코드가 들어 있습니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `output_formatter.py` | JSON, CSV, Markdown 저장과 콘솔 테이블 출력 |

## `output_formatter.py`

### 함수 구조

- `save_results_as_json(evaluation_results, summary, output_dir="data/results")`: 평가 결과와 요약을 JSON 파일로 저장합니다.
- `save_results_as_csv(evaluation_results, output_dir="data/results")`: 평가 결과를 표 형태 CSV로 저장합니다.
- `generate_markdown_report(user_profile, evaluation_results, summary, output_dir="data/results")`: 사람이 읽기 좋은 Markdown 보고서를 생성합니다.
- `print_table_format(evaluation_results, limit=10)`: 콘솔에 상위 결과를 표처럼 출력합니다.

## 데이터 흐름

```text
evaluation_results + summary
  -> JSON 저장
  -> CSV 저장
  -> Markdown 보고서 저장
  -> 콘솔 테이블 출력
```

## 공부 포인트

- `os.makedirs(output_dir, exist_ok=True)`는 저장 폴더가 없으면 만들고, 이미 있으면 넘어갑니다.
- `datetime.now().strftime(...)`로 파일명에 현재 시간을 붙여 덮어쓰기를 피합니다.
- `json.dump(..., ensure_ascii=False)`는 한글이 깨지지 않게 저장하는 데 중요합니다.
- `csv.DictWriter`는 딕셔너리를 CSV 행으로 저장할 때 유용합니다.

## 코드 리뷰 포인트

- Markdown 보고서는 문자열 리스트에 내용을 append한 뒤 마지막에 `"".join()`으로 합칩니다. 긴 문자열을 계속 더하는 것보다 효율적입니다.
- CSV는 중첩 리스트 값을 `", ".join(...)`으로 사람이 읽기 좋게 바꿉니다.
- `save_results_as_csv()`는 결과가 비어 있어도 파일 경로를 반환하지만 실제 파일은 만들어지지 않을 수 있습니다.

## 개선 후보

- 저장 파일명 생성을 공통 함수로 빼면 JSON, CSV, Markdown에서 중복을 줄일 수 있습니다.
- Markdown 보고서의 섹션 생성 로직을 작은 함수로 나누면 테스트하기 쉬워집니다.
- CSV 저장 시 빈 결과일 때도 헤더만 있는 파일을 만들지, 아예 만들지 않을지 정책을 명확히 하면 좋습니다.
