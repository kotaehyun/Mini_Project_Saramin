import os
import sys

import streamlit as st


# app/ 폴더에서 실행해도 프로젝트 루트 모듈을 import할 수 있게 경로 추가
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.dashboard import render_dashboard
from app.graph_visualizer import render_langgraph_flow
from graphs.job_graph import run_job_search_workflow_with_progress
from utils.output_formatter import (
    generate_markdown_report,
    save_results_as_csv,
    save_results_as_json,
)


STEPS = [
    "검색 URL 생성",
    "사람인 공고 크롤링",
    "공고 데이터 전처리",
    "LLM 적합도 평가",
    "결과 요약 생성",
    "결과 파일 저장",
]


def apply_xai_theme():
    """xAI 문서의 dark-canvas 규칙을 Streamlit 화면에 적용한다."""

    st.markdown(
        """
        <style>
        :root {
            --cursor-primary: #ffffff;
            --cursor-primary-active: #fafaf7;
            --cursor-ink: #ffffff;
            --cursor-body: #dadbdf;
            --cursor-muted: #7d8187;
            --cursor-muted-soft: #363a3f;
            --cursor-canvas: #0a0a0a;
            --cursor-canvas-soft: #1a1c20;
            --cursor-card: #191919;
            --cursor-surface-strong: #363a3f;
            --cursor-hairline: #212327;
            --cursor-hairline-soft: #212327;
            --cursor-hairline-strong: rgba(255, 255, 255, 0.25);
            --cursor-thinking: #ff7a17;
            --cursor-grep: #a0c3ec;
            --cursor-read: #c4b5fd;
            --cursor-edit: #ffc285;
            --cursor-done: #ffffff;
            --cursor-success: #a0c3ec;
            --cursor-error: #ff7a17;
        }

        * {
            letter-spacing: 0;
        }

        html,
        body,
        [data-testid="stAppViewContainer"] {
            color: var(--cursor-body);
            background: var(--cursor-canvas);
            font-family: "Inter", "Geist", -apple-system, BlinkMacSystemFont,
                "Segoe UI", sans-serif;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        [data-testid="stToolbar"],
        [data-testid="stDecoration"] {
            display: none;
        }

        [data-testid="stMainBlockContainer"] {
            max-width: 1248px;
            padding: 0 24px 96px;
        }

        [data-testid="stSidebar"] {
            background: var(--cursor-canvas);
            border-right: 1px solid var(--cursor-hairline);
        }

        [data-testid="stSidebar"] > div {
            padding-top: 24px;
        }

        h1,
        h2,
        h3,
        h4 {
            color: var(--cursor-ink);
            font-family: "Inter", "Geist", -apple-system, BlinkMacSystemFont,
                "Segoe UI", sans-serif;
            font-weight: 400;
            letter-spacing: -0.03em;
        }

        h2 {
            font-size: 42px;
            line-height: 1.14;
        }

        h3 {
            font-size: 30px;
            line-height: 1.18;
        }

        p,
        label,
        [data-testid="stCaptionContainer"] {
            font-size: 16px;
            line-height: 1.55;
        }

        a {
            color: var(--cursor-ink);
        }

        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        textarea {
            min-height: 44px;
            color: var(--cursor-ink);
            background: var(--cursor-canvas-soft);
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            box-shadow: none;
        }

        [data-baseweb="input"] > div:focus-within,
        [data-baseweb="select"] > div:focus-within,
        textarea:focus {
            border-color: var(--cursor-hairline-strong);
            box-shadow: none;
        }

        div.stButton > button,
        div.stDownloadButton > button {
            min-height: 40px;
            padding: 10px 18px;
            border: 1px solid var(--cursor-hairline-strong);
            border-radius: 9999px;
            color: var(--cursor-ink);
            background: transparent;
            box-shadow: none;
            font-size: 14px;
            font-weight: 400;
        }

        div.stButton > button[kind="primary"] {
            border-color: var(--cursor-primary);
            color: var(--cursor-canvas);
            background: var(--cursor-primary);
        }

        div.stButton > button:active,
        div.stDownloadButton > button:active {
            border-color: var(--cursor-hairline-strong);
            color: var(--cursor-canvas);
            background: var(--cursor-primary-active);
        }

        div.stButton > button:focus-visible,
        div.stDownloadButton > button:focus-visible {
            outline: 2px solid rgba(255, 255, 255, 0.54);
            outline-offset: 2px;
        }

        [data-testid="stMetric"] {
            min-height: 116px;
            padding: 24px;
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            background: var(--cursor-card);
            box-shadow: none;
        }

        [data-testid="stMetricLabel"] p {
            color: var(--cursor-muted);
            font: 400 11px "Geist Mono", "JetBrains Mono", Consolas, monospace;
            letter-spacing: 1.2px;
            text-transform: uppercase;
        }

        [data-testid="stMetricValue"] {
            color: var(--cursor-ink);
            font-family: "Inter", "Geist", system-ui, sans-serif;
            font-size: 36px;
            font-weight: 400;
        }

        [data-testid="stDataFrame"] {
            overflow: hidden;
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            background: var(--cursor-card);
        }

        [data-testid="stExpander"] {
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            background: var(--cursor-card);
            box-shadow: none;
        }

        [data-testid="stAlert"] {
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            background: var(--cursor-card);
            box-shadow: none;
        }

        .cursor-top-nav {
            position: sticky;
            top: 0;
            z-index: 30;
            min-height: 64px;
            margin: 0 -24px;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 24px;
            color: var(--cursor-ink);
            background: rgba(10, 10, 10, 0.94);
            border-bottom: 1px solid var(--cursor-hairline);
            font-size: 14px;
        }

        .cursor-brand,
        .cursor-nav-links,
        .cursor-nav-actions,
        .cursor-hero-actions,
        .cursor-status-key {
            display: flex;
            align-items: center;
        }

        .cursor-brand {
            gap: 12px;
            color: var(--cursor-ink);
            font-weight: 400;
        }

        .cursor-mark {
            width: 28px;
            height: 28px;
            display: inline-grid;
            place-items: center;
            border: 1px solid var(--cursor-hairline-strong);
            border-radius: 9999px;
            color: var(--cursor-ink);
            background: transparent;
            font: 400 11px "Geist Mono", "JetBrains Mono", Consolas, monospace;
        }

        .cursor-wordmark {
            font-size: 15px;
            line-height: 1.3;
        }

        .cursor-nav-links {
            gap: 22px;
            flex: 1;
            color: var(--cursor-body);
            font-weight: 400;
        }

        .cursor-nav-actions {
            gap: 12px;
            white-space: nowrap;
        }

        .cursor-text-link {
            color: var(--cursor-ink);
            font: 400 14px "Inter", system-ui, sans-serif;
        }

        .cursor-nav-cta,
        .cursor-button,
        .cursor-button-secondary {
            min-height: 40px;
            padding: 10px 18px;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            border-radius: 9999px;
            border: 1px solid var(--cursor-hairline-strong);
            font-size: 14px;
            font-weight: 400;
        }

        .cursor-nav-cta,
        .cursor-button {
            color: var(--cursor-canvas);
            border-color: var(--cursor-primary);
            background: var(--cursor-primary);
        }

        .cursor-button-secondary {
            color: var(--cursor-ink);
            background: transparent;
        }

        .cursor-hero-band {
            min-height: 620px;
            margin: 0 -24px;
            padding: 80px 24px 64px;
            display: grid;
            grid-template-columns: 1fr;
            gap: 48px;
            align-items: center;
            color: var(--cursor-ink);
            background: var(--cursor-canvas);
        }

        .cursor-eyebrow {
            margin: 0 0 16px;
            color: var(--cursor-body);
            font: 400 12px "Geist Mono", "JetBrains Mono", Consolas, monospace;
            line-height: 1.4;
            letter-spacing: 1.2px;
            text-transform: uppercase;
        }

        .cursor-hero-band h1 {
            max-width: 900px;
            margin: 0;
            font-size: 88px;
            line-height: 0.98;
            letter-spacing: -0.04em;
        }

        .cursor-hero-copy {
            max-width: 560px;
            margin: 24px 0 0;
            color: var(--cursor-body);
            font-size: 18px;
            line-height: 1.56;
        }

        .cursor-hero-actions {
            gap: 12px;
            margin-top: 32px;
            flex-wrap: wrap;
        }

        .cursor-ide-card {
            min-height: 360px;
            display: grid;
            grid-template-columns: minmax(150px, 0.26fr) minmax(0, 1fr) minmax(220px, 0.42fr);
            gap: 12px;
            padding: 12px;
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            color: var(--cursor-ink);
            background: var(--cursor-card);
        }

        .cursor-run-head,
        .cursor-run-foot,
        .cursor-stage-row {
            display: flex;
            align-items: center;
        }

        .cursor-run-head {
            justify-content: space-between;
            gap: 16px;
            color: var(--cursor-muted);
            font: 400 12px "Geist Mono", "JetBrains Mono", Consolas, monospace;
            text-transform: uppercase;
        }

        .cursor-run-badge {
            padding: 6px 12px;
            border-radius: 999px;
            color: var(--cursor-ink);
            background: transparent;
            border: 1px solid var(--cursor-hairline-strong);
        }

        .cursor-ide-pane {
            display: grid;
            gap: 12px;
            padding: 16px;
            border: 1px solid var(--cursor-hairline-soft);
            border-radius: 8px;
            background: var(--cursor-canvas-soft);
            font: 400 13px "Geist Mono", "JetBrains Mono", ui-monospace,
                Consolas, monospace;
        }

        .cursor-file-tree {
            align-content: start;
            color: var(--cursor-muted);
        }

        .cursor-chat-pane {
            align-content: space-between;
        }

        .cursor-stage-row {
            justify-content: space-between;
            gap: 18px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--cursor-hairline);
        }

        .cursor-stage-row:last-child {
            padding-bottom: 0;
            border-bottom: 0;
        }

        .cursor-stage-pill {
            padding: 4px 10px;
            border-radius: 9999px;
            color: var(--cursor-ink);
            border: 1px solid var(--cursor-hairline-strong);
            font: 400 11px "Geist Mono", "JetBrains Mono", Consolas, monospace;
            letter-spacing: 1.2px;
            text-transform: uppercase;
        }

        .cursor-stage-pill.is-grep {
            color: var(--cursor-canvas);
            background: var(--cursor-grep);
        }

        .cursor-stage-pill.is-read {
            color: var(--cursor-canvas);
            background: var(--cursor-read);
        }

        .cursor-stage-pill.is-edit {
            color: var(--cursor-canvas);
            background: var(--cursor-edit);
        }

        .cursor-stage-pill.is-done {
            color: var(--cursor-canvas);
            background: var(--cursor-done);
        }

        .cursor-run-foot {
            justify-content: space-between;
            gap: 16px;
            color: var(--cursor-muted);
            font-size: 14px;
        }

        .cursor-run-foot b {
            color: var(--cursor-ink);
            font-weight: 400;
        }

        .cursor-query-band {
            margin: 0 -24px;
            padding: 48px 24px 32px;
            border-top: 1px solid var(--cursor-hairline);
            border-bottom: 1px solid var(--cursor-hairline);
            background: var(--cursor-canvas);
        }

        .cursor-query-band h3 {
            margin: 0 0 10px;
        }

        .cursor-query-band p {
            max-width: 720px;
            margin: 0 0 20px;
            color: var(--cursor-muted);
        }

        .cursor-workflow-intro {
            margin: 0 -24px;
            padding: 72px 24px 32px;
            color: var(--cursor-ink);
            background: var(--cursor-canvas);
        }

        .cursor-workflow-intro h2 {
            margin: 0 0 12px;
            color: var(--cursor-ink);
        }

        .cursor-workflow-intro p {
            max-width: 760px;
            margin: 0;
            color: var(--cursor-body);
        }

        .cursor-status-key {
            gap: 12px;
            margin-top: 20px;
            color: var(--cursor-ink);
            font-size: 14px;
            flex-wrap: wrap;
        }

        .cursor-chip {
            padding: 6px 12px;
            border-radius: 9999px;
            border: 1px solid var(--cursor-hairline);
            background: transparent;
        }

        .cursor-chip.is-live {
            color: var(--cursor-canvas);
            background: var(--cursor-thinking);
        }

        .cursor-chip.is-done {
            color: var(--cursor-canvas);
            background: var(--cursor-done);
        }

        .cursor-chip.is-fail {
            color: var(--cursor-canvas);
            background: var(--cursor-error);
        }

        .cursor-dashboard-head {
            margin: 88px -24px 32px;
            padding: 64px 24px 32px;
            border-top: 1px solid var(--cursor-hairline);
            background: var(--cursor-canvas);
        }

        .cursor-dashboard-head h2 {
            margin: 0 0 12px;
        }

        .cursor-dashboard-head p {
            max-width: 760px;
            margin: 0;
            color: var(--cursor-muted);
        }

        .cursor-sidebar-note {
            margin: 0 0 24px;
            padding: 20px;
            border: 1px solid var(--cursor-hairline);
            border-radius: 8px;
            color: var(--cursor-ink);
            background: var(--cursor-card);
        }

        .cursor-sidebar-note strong {
            display: block;
            margin-bottom: 8px;
            color: var(--cursor-ink);
            font-size: 18px;
            font-weight: 400;
        }

        .cursor-sidebar-note span {
            color: var(--cursor-muted);
            font-size: 14px;
            line-height: 1.55;
        }

        [data-testid="stVerticalBlockBorderWrapper"] {
            box-shadow: none;
        }

        @media (max-width: 1024px) {
            .cursor-ide-card {
                grid-template-columns: minmax(120px, 0.28fr) minmax(0, 1fr);
            }

            .cursor-chat-pane {
                grid-column: 1 / -1;
            }
        }

        @media (max-width: 833px) {
            [data-testid="stMainBlockContainer"] {
                padding-right: 20px;
                padding-left: 20px;
            }

            .cursor-top-nav,
            .cursor-hero-band,
            .cursor-query-band,
            .cursor-workflow-intro,
            .cursor-dashboard-head {
                margin-right: -20px;
                margin-left: -20px;
                padding-right: 20px;
                padding-left: 20px;
            }

            .cursor-nav-links span:not(:first-child),
            .cursor-text-link {
                display: none;
            }

            .cursor-hero-band {
                min-height: auto;
                padding-top: 72px;
                padding-bottom: 72px;
            }

            .cursor-hero-band h1 {
                font-size: 56px;
                letter-spacing: -0.04em;
            }

            .cursor-hero-copy {
                font-size: 17px;
            }
        }

        @media (max-width: 640px) {
            .cursor-top-nav {
                padding-right: 16px;
                padding-left: 16px;
            }

            .cursor-nav-links {
                display: none;
            }

            .cursor-nav-cta {
                padding-right: 14px;
                padding-left: 14px;
            }

            .cursor-hero-band {
                gap: 32px;
            }

            .cursor-hero-band h1 {
                font-size: 40px;
                letter-spacing: -0.04em;
            }

            .cursor-ide-card {
                grid-template-columns: 1fr;
            }

            .cursor-run-foot,
            .cursor-stage-row {
                align-items: flex-start;
                flex-direction: column;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_shell_intro():
    """상단 내비게이션과 첫 화면을 렌더링한다."""

    st.markdown(
        """
        <div class="cursor-top-nav">
            <div class="cursor-brand">
                <span class="cursor-mark">SM</span>
                <span class="cursor-wordmark">Saramin Match</span>
            </div>
            <div class="cursor-nav-links">
                <span>Profile</span>
                <span>Workflow</span>
                <span>Results</span>
            </div>
            <div class="cursor-nav-actions">
                <span class="cursor-text-link">LangGraph</span>
                <span class="cursor-nav-cta">Run match</span>
            </div>
        </div>
        <section class="cursor-hero-band">
            <div>
                <p class="cursor-eyebrow">Saramin job search with LangGraph</p>
                <h1>지원할 공고를 읽고, 다음 선택을 정리합니다.</h1>
                <p class="cursor-hero-copy">
                    프로필과 채용공고를 비교해 적합도, 부족 스킬, 학습 우선순위를
                    한 흐름 안에서 차분하게 검토합니다.
                </p>
                <div class="cursor-hero-actions">
                    <span class="cursor-button">워크플로우 실행</span>
                    <span class="cursor-button-secondary">결과 대시보드</span>
                </div>
            </div>
            <div class="cursor-ide-card">
                <div class="cursor-ide-pane cursor-file-tree">
                    <span>app/streamlit_app.py</span>
                    <span>graphs/job_graph.py</span>
                    <span>chains/filter_chain.py</span>
                    <span>data/results/report.md</span>
                </div>
                <div class="cursor-ide-pane">
                    <div class="cursor-run-head">
                        <span>job_graph.py</span>
                        <span class="cursor-run-badge">Candidate fit</span>
                    </div>
                    <div class="cursor-stage-row">
                        <span>01 crawl_jobs</span>
                        <span class="cursor-stage-pill is-grep">Grepping</span>
                    </div>
                    <div class="cursor-stage-row">
                        <span>02 preprocess</span>
                        <span class="cursor-stage-pill is-read">Reading</span>
                    </div>
                    <div class="cursor-stage-row">
                        <span>03 evaluate_fit</span>
                        <span class="cursor-stage-pill is-edit">Editing</span>
                    </div>
                    <div class="cursor-stage-row">
                        <span>04 summarize</span>
                        <span class="cursor-stage-pill is-done">Done</span>
                    </div>
                </div>
                <div class="cursor-ide-pane cursor-chat-pane">
                    <div>
                        <p class="cursor-eyebrow">Agent note</p>
                        <span>프로필과 공고 요건을 비교해 지원 가능성과 학습 순서를 요약합니다.</span>
                    </div>
                    <div class="cursor-run-foot">
                        <span><b>Output</b> 추천 공고 보고서</span>
                        <span>JSON · CSV · Markdown</span>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_keyword_intro():
    """검색 키워드 입력 전 맥락을 표시한다."""

    st.markdown(
        """
        <section class="cursor-query-band">
            <p class="cursor-eyebrow">Search brief</p>
            <h3>Search brief</h3>
            <p>왼쪽 프로필을 기준으로 탐색할 직무 키워드를 정합니다.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_workflow_intro():
    """워크플로우 섹션의 설명과 상태 키를 표시한다."""

    st.markdown(
        """
        <section class="cursor-workflow-intro">
            <p class="cursor-eyebrow">Workflow</p>
            <h2>Workflow</h2>
            <p>검색 URL 생성부터 결과 파일 저장까지 상태와 데이터 타입 계약이 어떻게 이어지는지 함께 확인합니다.</p>
            <div class="cursor-status-key">
                <span class="cursor-chip">대기</span>
                <span class="cursor-chip is-live">진행중</span>
                <span class="cursor-chip is-done">완료</span>
                <span class="cursor-chip is-fail">실패</span>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def split_comma_text(value: str):
    """쉼표로 입력한 텍스트를 리스트로 변환한다."""

    return [item.strip() for item in value.split(",") if item.strip()]


def render_status(status_area, status):
    """단계별 상태를 화면에 표시한다."""

    with status_area.container():
        cols = st.columns(3)
        for idx, step in enumerate(STEPS):
            cols[idx % 3].metric(step, status.get(step, "대기"))


def render_graph(graph_area, status):
    """3D LangGraph 흐름도를 다시 그린다."""

    graph_area.empty()
    with graph_area.container():
        render_langgraph_flow(status)


def build_user_profile():
    """사이드바 입력값으로 사용자 프로필 딕셔너리를 만든다."""

    st.sidebar.markdown(
        """
        <div class="cursor-sidebar-note">
            <strong>Candidate profile</strong>
            <span>공고 평가 기준이 되는 선호 조건과 현재 역량을 입력합니다.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("## 사용자 프로필")
    st.sidebar.caption("검색 기준과 지원 가능성을 함께 비교합니다.")

    name = st.sidebar.text_input("이름", "홍길동")
    skills = st.sidebar.text_input("보유 스킬", "Python, SQL, FastAPI, LangChain")
    certifications = st.sidebar.text_input("자격증", "정보처리기사")
    preferred_locations = st.sidebar.text_input("희망 지역", "서울, 경기")
    preferred_employment_types = st.sidebar.text_input("희망 근무형태", "정규직")
    education = st.sidebar.selectbox(
        "최종 학력",
        ["고졸", "초대졸", "학사", "석사", "박사"],
        index=2,
    )
    career_level = st.sidebar.text_input("경력", "신입")
    interested_jobs = st.sidebar.text_input("관심 직무", "AI 개발자, 백엔드 개발자")

    return {
        "name": name,
        "skills": split_comma_text(skills),
        "certifications": split_comma_text(certifications),
        "preferred_locations": split_comma_text(preferred_locations),
        "preferred_employment_types": split_comma_text(preferred_employment_types),
        "education": education,
        "career_level": career_level,
        "interested_jobs": split_comma_text(interested_jobs),
    }


def main():
    st.set_page_config(page_title="사람인 공고 필터링 시스템", layout="wide")
    apply_xai_theme()
    render_shell_intro()

    user_profile = build_user_profile()
    render_keyword_intro()
    keyword = st.text_input("검색할 직무", "AI 개발자")

    render_workflow_intro()
    st.subheader("LangGraph 흐름도")
    graph_area = st.empty()
    status_area = st.empty()
    status = {step: "대기" for step in STEPS}

    render_graph(graph_area, status)
    render_status(status_area, status)

    if st.button("워크플로우 실행", type="primary"):
        if not keyword.strip():
            st.warning("검색할 직무를 입력해주세요.")
            return

        try:
            final_state = run_job_search_workflow_with_progress(
                keyword=keyword.strip(),
                user_profile=user_profile,
                status=status,
                render_status=lambda current_status: (
                    render_graph(graph_area, current_status),
                    render_status(status_area, current_status),
                ),
            )

            if final_state.get("error"):
                st.error(final_state["error"])
                return

            evaluation_results = final_state.get("evaluation_results", [])
            summary = final_state.get("summary", {})

            status["결과 파일 저장"] = "진행중"
            render_graph(graph_area, status)
            render_status(status_area, status)

            json_path = save_results_as_json(evaluation_results, summary)
            csv_path = save_results_as_csv(evaluation_results)
            md_path = generate_markdown_report(user_profile, evaluation_results, summary)

            status["결과 파일 저장"] = "완료"
            render_graph(graph_area, status)
            render_status(status_area, status)

            st.success("워크플로우가 완료되었습니다.")
            render_dashboard(final_state)

            st.subheader("결과 파일 다운로드")

            download_files = [
                ("JSON 결과 다운로드", json_path, "application/json"),
                ("CSV 결과 다운로드", csv_path, "text/csv"),
                ("Markdown 보고서 다운로드", md_path, "text/markdown"),
            ]

            for label, path, mime in download_files:
                with open(path, "rb") as file:
                    st.download_button(
                        label=label,
                        data=file,
                        file_name=os.path.basename(path),
                        mime=mime,
                    )

        except Exception as exc:
            status["결과 파일 저장"] = "실패"
            render_graph(graph_area, status)
            render_status(status_area, status)
            st.error(f"실행 중 오류가 발생했습니다: {exc}")


if __name__ == "__main__":
    main()
