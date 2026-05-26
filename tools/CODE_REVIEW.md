# `tools/` 코드 리뷰

`tools/` 폴더는 기존 Python 함수를 LangChain Agent나 Tool 체계에서 쓸 수 있도록 감싸는 역할을 합니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `saramin_tool.py` | 사람인 크롤링 함수를 LangChain `@tool`로 래핑 |

## `saramin_tool.py`

### 함수 구조

- `search_saramin_jobs(keyword)`: `@tool` 데코레이터가 붙은 LangChain Tool 함수입니다.

내부에서는 `crawlers.saramin_crawler.crawl_saramin_jobs()`를 호출합니다.

```text
LangChain Tool 호출
  -> search_saramin_jobs(keyword)
  -> _crawl_saramin_jobs(keyword, max_pages=2)
  -> List[Dict]
```

## 초보자 설명

`@tool`은 일반 함수를 LangChain에서 사용할 수 있는 도구로 등록하는 데코레이터입니다. 즉, 함수 자체의 핵심 로직은 크롤러에 두고, 이 파일에서는 "LangChain이 호출할 수 있는 형태"로 포장합니다.

## 코드 리뷰 포인트

- 크롤링 핵심 로직을 다시 작성하지 않고 기존 함수를 재사용하는 점이 좋습니다.
- `max_pages=2`가 하드코딩되어 있습니다. 설정값을 쓰거나 인자로 받을 수 있습니다.
- `JobPosting` import는 현재 사용되지 않습니다. 정리 후보입니다.

## 개선 후보

- Tool 입력 스키마를 명확히 만들면 Agent가 더 안정적으로 호출할 수 있습니다.
- 크롤링 실패 시 Tool 결과에 에러 메시지를 구조화해서 반환하면 후속 처리가 쉬워집니다.
