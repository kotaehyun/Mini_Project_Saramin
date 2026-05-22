# 공통 설정 파일

import os
from dotenv import load_dotenv

load_dotenv()

# 사람인 기본 URL
BASE_URL = "https://www.saramin.co.kr/zf_user/"
SEARCH_BASE_URL = "https://www.saramin.co.kr/zf_user/search"

# 요청 헤더 (User-Agent 필수)
HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# LLM 설정
LLM_MODEL = "gpt-4o-mini"  # 또는 "gpt-4o"
LLM_TEMPERATURE = 0.3  # JSON 출력 안정성을 위해 낮은 온도 사용

# 크롤링 설정
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# 데이터 저장 경로
DATA_DIR = "data"
RESULTS_DIR = os.path.join(DATA_DIR, "results")
os.makedirs(RESULTS_DIR, exist_ok=True)

# 페이지당 공고 수 (사람인 페이지 구조에 따라 조정)
JOBS_PER_PAGE = 20

# 크롤링할 최대 페이지 수 (미니 프로젝트이므로 제한)
MAX_PAGES = 2
