# `crawlers/` 코드 리뷰

`crawlers/` 폴더는 사람인 검색 결과 페이지에서 채용공고 데이터를 가져오는 역할을 합니다.

## 파일 구조

| 파일 | 역할 |
| --- | --- |
| `saramin_crawler.py` | 검색 URL 생성, HTML 요청, BeautifulSoup 파싱, 공고 정보 추출 |

## `saramin_crawler.py`

### 함수 구조

- `generate_search_url(keyword, page=1)`: 검색어와 페이지 번호를 사람인 검색 URL로 바꿉니다.
- `build_absolute_url(relative_url)`: 상대 URL을 완전한 URL로 변환합니다.
- `crawl_saramin_jobs(keyword, max_pages=MAX_PAGES)`: 여러 페이지를 요청하고 공고 리스트를 수집합니다.
- `_extract_job_info(job_item)`: HTML 공고 블록 1개에서 회사명, 제목, URL, 근무조건 등을 추출합니다.

## 데이터 흐름

```text
keyword
  -> generate_search_url()
  -> requests.get()
  -> BeautifulSoup(response.text)
  -> soup.select(...)
  -> _extract_job_info()
  -> List[Dict]
```

## 초보자 설명

- `requests.get()`은 웹페이지 HTML을 가져오는 함수입니다.
- `BeautifulSoup`은 HTML 문자열에서 원하는 태그를 찾기 쉽게 해주는 도구입니다.
- `soup.select("CSS selector")`는 CSS 선택자 문법으로 원하는 요소를 찾습니다.
- `urljoin()`은 `/zf_user/view?...` 같은 상대 주소를 `https://www.saramin.co.kr/...` 형태로 바꿉니다.

## 코드 리뷰 포인트

- 사람인 HTML 구조가 바뀌면 selector가 동작하지 않을 수 있습니다.
- 요청 실패, 파싱 실패는 예외 처리되어 전체 프로그램이 바로 죽지는 않습니다.
- `MAX_RETRIES`를 import하지만 현재 실제 재시도 로직에는 쓰지 않습니다. 재시도 기능을 넣거나 import를 정리할 수 있습니다.
- 크롤링 예절을 위해 페이지 요청 후 `time.sleep(2)`가 들어 있습니다.

## 개선 후보

- HTML 샘플을 저장해 `_extract_job_info()` 단위 테스트를 만들면 selector 변경을 빨리 알아챌 수 있습니다.
- `MAX_RETRIES`를 활용해 일시적인 네트워크 실패를 다시 시도할 수 있습니다.
- 상세 페이지까지 들어가면 학력, 자격요건, 우대사항을 더 정확히 수집할 수 있습니다.
