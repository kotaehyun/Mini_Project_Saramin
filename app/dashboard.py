import streamlit as st


def _format_cell_for_table(value):
    """Streamlit 표시용으로 list/dict 값을 읽기 쉬운 문자열로 변환한다."""

    if value is None:
        return ""
    if isinstance(value, list):
        if not value:
            return ""
        return ", ".join(_format_cell_for_table(item) for item in value)
    if isinstance(value, dict):
        if not value:
            return ""
        return " / ".join(
            f"{key}: {_format_cell_for_table(item)}"
            for key, item in value.items()
        )
    return str(value)


def _format_rows_for_table(rows):
    """pyarrow 변환 오류를 막기 위해 중첩 값을 평탄한 문자열로 바꾼다."""

    return [
        {key: _format_cell_for_table(value) for key, value in row.items()}
        for row in rows
    ]


def _order_evaluation_columns(rows):
    """상세 평가 결과에서 자주 보는 컬럼을 앞쪽에 배치한다."""

    preferred_columns = [
        "index",
        "company",
        "title",
        "fit_score",
        "result",
        "apply_level",
        "matched_skills",
        "missing_core_skills",
        "missing_optional_skills",
        "missing_certs",
        "reason",
        "url",
    ]

    ordered_rows = []
    for row in rows:
        ordered = {key: row.get(key, "") for key in preferred_columns if key in row}
        for key, value in row.items():
            if key not in ordered:
                ordered[key] = value
        ordered_rows.append(ordered)
    return ordered_rows


def _build_evaluation_summary_rows(evaluation_results):
    """상세 평가 전체 표에는 핵심 컬럼만 보여준다."""

    rows = []
    for idx, result in enumerate(evaluation_results, 1):
        rows.append({
            "번호": _format_cell_for_table(result.get("index", idx)),
            "회사명": _format_cell_for_table(result.get("company", "")),
            "직무명": _format_cell_for_table(result.get("title", "")),
            "점수": _format_cell_for_table(result.get("fit_score", "")),
            "판정": _format_cell_for_table(result.get("result", "")),
            "지원추천": _format_cell_for_table(result.get("apply_level", "")),
            "일치 스킬": _format_cell_for_table(result.get("matched_skills", [])),
            "부족 핵심 스킬": _format_cell_for_table(result.get("missing_core_skills", [])),
            "URL": _format_cell_for_table(result.get("url", "")),
        })
    return rows


def _render_list(label, values):
    """리스트형 평가 값을 짧고 보기 좋게 출력한다."""

    formatted = _format_cell_for_table(values)
    st.markdown(f"**{label}**: {formatted or '없음'}")


def _render_check(label, value):
    """요건 판단처럼 dict/string이 섞이는 값을 출력한다."""

    formatted = _format_cell_for_table(value)
    if formatted:
        st.markdown(f"**{label}**: {formatted}")


def _render_section_intro(title, description):
    """결과 섹션의 제목과 설명을 한 리듬으로 표시한다."""

    st.markdown(
        f"""
        <div class="cursor-dashboard-head">
            <p class="cursor-eyebrow">Analysis output</p>
            <h2>{title}</h2>
            <p>{description}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_dashboard(final_state):
    """
    LangGraph 실행 결과를 Streamlit 대시보드로 출력한다.
    """

    raw_jobs = final_state.get("raw_jobs", [])
    processed_jobs = final_state.get("processed_jobs", [])
    evaluation_results = final_state.get("evaluation_results", [])
    summary = final_state.get("summary", {})

    _render_section_intro(
        "Results",
        "수집된 공고 수, 추천 결과, 부족 역량을 한 화면에서 비교합니다.",
    )

    result_stats = summary.get("statistics", {}).get("by_result", {})

    col1, col2, col3 = st.columns(3)
    col1.metric("전체 수집 공고 수", len(raw_jobs))
    col2.metric("전처리 후 공고 수", len(processed_jobs))
    col3.metric("평가 완료 공고 수", len(evaluation_results))

    col4, col5, col6 = st.columns(3)
    col4.metric("적합 공고 수", result_stats.get("적합", 0))
    col5.metric("보완필요 공고 수", result_stats.get("보완필요", 0))
    col6.metric("부적합 공고 수", result_stats.get("부적합", 0))

    st.subheader("추천 공고 TOP 3")
    recommended_jobs = summary.get("recommended_jobs", [])
    if recommended_jobs:
        st.dataframe(_format_rows_for_table(recommended_jobs), width="stretch")
    else:
        st.info("추천 공고가 없습니다.")

    st.subheader("부족 스킬 TOP 5")
    missing_core_skills = summary.get("top_missing_skills", {}).get("core", [])
    if missing_core_skills:
        st.dataframe(_format_rows_for_table(missing_core_skills[:5]), width="stretch")
    else:
        st.info("부족 스킬 데이터가 없습니다.")

    st.subheader("추천 학습 우선순위")
    priority_skills = summary.get("learning_recommendations", {}).get("priority_skills", [])
    if priority_skills:
        st.dataframe(_format_rows_for_table(priority_skills), width="stretch")
    else:
        st.info("추천 학습 우선순위가 없습니다.")

    st.subheader("상세 평가 결과")
    if evaluation_results:
        summary_rows = _build_evaluation_summary_rows(evaluation_results)
        st.dataframe(summary_rows, width="stretch")

        st.markdown("#### 공고별 상세 보기")
        for idx, result in enumerate(evaluation_results, 1):
            company = result.get("company", "미상")
            title = result.get("title", "공고명 미상")
            score = result.get("fit_score", 0)
            apply_level = result.get("apply_level", "미분류")

            with st.expander(f"{idx}. {company} - {title} ({score}점 / {apply_level})"):
                top_cols = st.columns(3)
                top_cols[0].metric("적합도", score)
                top_cols[1].metric("판정", result.get("result", "미분류"))
                top_cols[2].metric("지원추천", apply_level)

                st.markdown(f"**판단 이유**: {result.get('reason', '미기재')}")
                _render_list("일치 스킬", result.get("matched_skills", []))
                _render_list("부족 핵심 스킬", result.get("missing_core_skills", []))
                _render_list("부족 우대 스킬", result.get("missing_optional_skills", []))
                _render_list("부족 자격증", result.get("missing_certs", []))
                _render_list("학습 우선순위", result.get("study_priority", []))

                _render_check("자격요건 판단", result.get("requirements_check"))
                _render_check("우대사항 판단", result.get("preferred_check"))
                _render_check("경력 판단", result.get("career_check"))
                _render_check("학력 판단", result.get("education_check"))
                _render_check("근무형태 판단", result.get("employment_type_check"))
                _render_check("지역 판단", result.get("location_check"))

                if result.get("url"):
                    st.markdown(f"[공고 링크 열기]({result['url']})")
    else:
        st.info("평가 결과가 없습니다.")
