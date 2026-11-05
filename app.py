import streamlit as st

from resume_reader import extract_resume_text
from resume_analyzer import analyze_resume
from jd_analyzer import analyze_jd
from job_matcher import match_resume_to_jd
from interview_generator import generate_interview_questions


# =============================
# 页面配置
# =============================

st.set_page_config(
    page_title="CareerPilot",
    page_icon="🎯",
    layout="centered",
)

st.title("🎯 CareerPilot")
st.caption(
    "AI 求职陪练｜根据简历与目标岗位，生成针对性面试问题"
)


# =============================
# Session State 初始化
# =============================

DEFAULTS = {
    "resume_text": "",
    "analysis_result": None,
    "analysis_error": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =============================
# 第一步：上传简历
# =============================

st.header("第一步：上传简历")

uploaded_resume = st.file_uploader(
    "上传个人简历",
    type=["docx", "pdf"],
    help="支持 Word（DOCX）和文本型 PDF。扫描版 PDF 暂不支持 OCR。",
)

if uploaded_resume is not None:

    try:
        resume_text = extract_resume_text(uploaded_resume)

        if resume_text and resume_text.strip():

            st.session_state.resume_text = resume_text

            st.success("简历读取成功")

            st.caption(
                f"已提取 {len(resume_text)} 个字符"
            )

            with st.expander("查看简历提取内容"):

                st.text_area(
                    "简历原始文本",
                    value=resume_text,
                    height=240,
                    disabled=True,
                )

        else:

            st.session_state.resume_text = ""

            st.warning(
                "没有从文件中提取到文本。"
                "扫描版 PDF 后续需要增加 OCR。"
            )

    except Exception as exc:

        st.session_state.resume_text = ""

        st.error(f"简历读取失败：{exc}")


# =============================
# 第二步：输入目标岗位
# =============================

st.header("第二步：输入目标岗位")

job_title = st.text_input(
    "目标岗位名称",
    placeholder="例如：AI 电商商品产品经理",
)

job_description = st.text_area(
    "岗位 JD",
    placeholder="请粘贴目标岗位的完整职位描述……",
    height=220,
)


# =============================
# 第三步：生成面试题
# =============================

st.header("第三步：生成面试题")

st.write(
    "点击按钮后，系统将解析简历、分析岗位要求、"
    "匹配岗位能力，并生成 5 道个性化面试主问题。"
)


if st.button(
    "生成面试题",
    type="primary",
    use_container_width=True,
):

    if not st.session_state.resume_text.strip():

        st.warning("请先上传并成功读取简历。")

    elif not job_title.strip():

        st.warning("请填写目标岗位名称。")

    elif not job_description.strip():

        st.warning("请粘贴目标岗位 JD。")

    else:

        try:

            # 1. 简历解析
            with st.spinner("1/4 正在解析简历……"):

                resume_data = analyze_resume(
                    st.session_state.resume_text
                )

            # 2. JD 分析
            with st.spinner("2/4 正在分析岗位 JD……"):

                jd_data = analyze_jd(
                    job_description
                )

            # 3. 岗位能力匹配
            with st.spinner(
                "3/4 正在匹配岗位能力与简历证据……"
            ):

                matching_data = match_resume_to_jd(
                    resume_data,
                    jd_data,
                )

            # 4. 面试题生成
            with st.spinner(
                "4/4 正在生成个性化面试题……"
            ):

                question_data = generate_interview_questions(
                    resume_data=resume_data,
                    jd_data=jd_data,
                    matching_data=matching_data,
                    job_title=job_title.strip(),
                )

            # 保存分析结果
            st.session_state.analysis_result = {
                "job_title": job_title.strip(),
                "resume_data": resume_data,
                "jd_data": jd_data,
                "matching_data": matching_data,
                "question_data": question_data,
            }

            st.session_state.analysis_error = None

        except Exception as exc:

            st.session_state.analysis_result = None

            st.session_state.analysis_error = str(exc)


# =============================
# 错误提示
# =============================

if st.session_state.analysis_error:

    st.error(
        f"生成失败：{st.session_state.analysis_error}"
    )


# =============================
# 分析结果展示
# =============================

if st.session_state.analysis_result:

    result = st.session_state.analysis_result

    st.success(
        f"已为「{result['job_title']}」生成 "
        f"{len(result['question_data']['questions'])} 道个性化面试题。"
    )

    # =============================
    # 简历解析结果
    # =============================

    with st.expander("查看简历解析结果"):

        resume_data = result["resume_data"]

        candidate = resume_data.get(
            "candidate",
            {},
        )

        st.subheader("候选人基本信息")

        st.json(candidate)

        st.subheader("教育经历")

        education = resume_data.get(
            "education",
            [],
        )

        if education:
            st.json(education)
        else:
            st.info("未提取到教育经历。")

        st.subheader("工作与项目经历")

        experiences = resume_data.get(
            "experiences",
            [],
        )

        if experiences:
            st.json(experiences)
        else:
            st.info("未提取到工作或项目经历。")

        st.subheader("专业技能")

        st.json(
            resume_data.get("skills", [])
        )

        st.subheader("待补充信息")

        st.json(
            resume_data.get("evidence_gaps", [])
        )

    # =============================
    # JD 解析结果
    # =============================

    with st.expander("查看岗位 JD 解析结果"):

        jd_data = result["jd_data"]

        job = jd_data.get(
            "job",
            {},
        )

        st.subheader("岗位基本信息")

        st.json({
            "job_title": job.get("job_title"),
            "department": job.get("department"),
            "seniority": job.get("seniority"),
        })

        st.subheader("岗位职责")

        st.json(
            job.get("job_responsibilities", [])
        )

        st.subheader("岗位能力模型")

        capability_dimensions = job.get(
            "capability_dimensions",
            [],
        )

        if capability_dimensions:
            st.json(capability_dimensions)
        else:
            st.info("未提取到岗位能力模型。")

        st.subheader("优先条件")

        st.json(
            job.get("preferred_qualifications", [])
        )

        st.subheader("技术技能")

        st.json(
            job.get("technical_skills", [])
        )

        st.subheader("行业知识")

        st.json(
            job.get("industry_knowledge", [])
        )

    # =============================
    # 面试题与关键得分点
    # =============================

    st.header("个性化面试题")

    questions = result["question_data"]["questions"]

    for index, item in enumerate(questions, start=1):

        with st.container(border=True):

            st.subheader(
                f"问题 {index}｜{item['category']}"
            )

            # 面试问题
            st.markdown(
                f"**{item['question']}**"
            )

            # 考察能力
            capabilities = item.get(
                "assessed_capabilities",
                [],
            )

            if capabilities:

                st.caption(
                    "考察能力：" + "、".join(capabilities)
                )

            # 关键得分点按钮
            score_key = f"show_score_points_{index}"

            if score_key not in st.session_state:
                st.session_state[score_key] = False

            if st.button(
                "隐藏关键得分点"
                if st.session_state[score_key]
                else "展示关键得分点",
                key=f"score_button_{index}",
                use_container_width=True,
            ):

                st.session_state[score_key] = (
                    not st.session_state[score_key]
                )

            # 展示关键得分点
            if st.session_state[score_key]:

                st.markdown("#### 关键得分点")

                key_points = item.get(
                    "answer_key_points",
                    [],
                )

                for point in key_points:

                    st.markdown(f"- {point}")

            # 追问方向
            follow_ups = item.get(
                "follow_up_directions",
                [],
            )

            if follow_ups:

                with st.expander("查看可能的追问方向"):

                    for follow_up in follow_ups[:2]:

                        st.markdown(f"- {follow_up}")


    # =============================
    # 开发调试信息
    # =============================

    with st.expander("开发调试信息：查看岗位能力匹配结果"):

        st.subheader("能力匹配统计")

        st.json(
            result["matching_data"].get(
                "matching_summary",
                {},
            )
        )

        st.subheader("逐项能力匹配")

        st.json(
            result["matching_data"].get(
                "capability_matches",
                [],
            )
        )


    # =============================
    # 重新开始
    # =============================

    if st.button("清除本次结果，重新开始"):

        st.session_state.analysis_result = None

        st.session_state.analysis_error = None

        for index in range(1, 6):
            st.session_state.pop(
                f"show_score_points_{index}",
                None,
            )

        st.rerun()