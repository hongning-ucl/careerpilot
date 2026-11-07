import json
import os

from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st


load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

QUESTION_COUNT = 5

QUESTION_CATEGORIES = [
    "岗位匹配与求职动机",
    "经历深挖与个人贡献",
    "业务分析与产品设计",
    "AI 技术与应用基础",
    "行为面试与学习成长",
]


def _extract_json(content):
    """兼容模型偶尔返回 Markdown 代码围栏的情况。"""
    content = (content or "").strip()

    if content.startswith("```"):
        content = content.split("\n", 1)[-1]

        if content.endswith("```"):
            content = content[:-3].strip()

    return json.loads(content)


def validate_interview_questions(data):
    """校验面试题输出结构。"""

    if not isinstance(data, dict):
        raise ValueError("面试题生成结果必须是 JSON 对象。")

    questions = data.get("questions")

    if not isinstance(questions, list):
        raise ValueError("面试题结果缺少 questions 列表。")

    if len(questions) != QUESTION_COUNT:
        raise ValueError(
            f"面试题必须恰好生成 {QUESTION_COUNT} 道，"
            f"当前为 {len(questions)} 道。"
        )

    required_fields = [
        "question_id",
        "category",
        "question",
        "assessed_capabilities",
        "answer_key_points",
        "follow_up_directions",
    ]

    for index, question in enumerate(questions, start=1):

        if not isinstance(question, dict):
            raise ValueError(f"第 {index} 道题格式不正确。")

        for field in required_fields:
            if field not in question:
                raise ValueError(
                    f"第 {index} 道题缺少字段：{field}"
                )

        if not isinstance(question["assessed_capabilities"], list):
            raise ValueError(
                f"第 {index} 道题 assessed_capabilities 必须是列表。"
            )

        if not isinstance(question["answer_key_points"], list):
            raise ValueError(
                f"第 {index} 道题 answer_key_points 必须是列表。"
            )

        if not isinstance(question["follow_up_directions"], list):
            raise ValueError(
                f"第 {index} 道题 follow_up_directions 必须是列表。"
            )

        if not str(question["question"]).strip():
            raise ValueError(
                f"第 {index} 道题题目内容不能为空。"
            )

        if not question["answer_key_points"]:
            raise ValueError(
                f"第 {index} 道题没有生成关键得分点。"
            )

    return data


def generate_interview_questions(
    resume_data,
    jd_data,
    matching_data,
    job_title=None,
):
    """
    根据简历、JD 和能力匹配结果生成 5 道个性化面试主问题。
    只生成题目，不负责面试流程控制和动态追问。
    """

    if not all(
        isinstance(item, dict)
        for item in [resume_data, jd_data, matching_data]
    ):
        raise ValueError(
            "resume_data、jd_data 和 matching_data 必须是字典。"
        )

    job = jd_data.get("job", {})

    if not isinstance(job, dict):
        raise ValueError(
            "jd_data 缺少有效的 job 对象。"
        )

    capability_matches = matching_data.get(
        "capability_matches", []
    )

    if not isinstance(capability_matches, list) or not capability_matches:
        raise ValueError(
            "岗位能力匹配结果为空，无法生成个性化面试题。"
        )

    model_input = {
        "job_title": job_title or job.get("job_title", ""),
        "job": job,
        "candidate_profile": matching_data.get(
            "candidate_profile", {}
        ),
        "resume_candidate": resume_data.get(
            "candidate", {}
        ),
        "resume_education": resume_data.get(
            "education", []
        ),
        "resume_experiences": resume_data.get(
            "experiences", []
        ),
        "capability_matches": capability_matches,
        "matching_summary": matching_data.get(
            "matching_summary", {}
        ),
        "question_categories": QUESTION_CATEGORIES,
        "question_count": QUESTION_COUNT,
    }

    system_prompt = """
你是一名资深招聘面试官，负责为目标岗位设计高质量、
个性化的结构化面试问题。

你的任务是：结合岗位 JD、候选人简历解析结果、
岗位能力匹配结果，生成恰好 5 道主问题。

【一、出题目标】

1. 题目必须针对当前岗位和当前候选人，
   不得生成通用题库式问题。

2. 题目要覆盖岗位关键能力，
   同时利用候选人真实经历进行深挖。

3. 优先考察 JD 中 importance 为 must_have、
   important 的能力；preferred/nice_to_have 次之。

4. 综合考虑 Direct、Transferable、Unverified 标签，
   但标签不能成为唯一出题依据。

5. 必须同时阅读 capability、importance、
   match_level、evidence、match_reason、missing_evidence。

6. Direct 能力可以追问决策依据、个人贡献和结果；
   Transferable 能力可以考察迁移思路；
   Unverified 能力可以通过场景题验证，
   但不能预设候选人不会。

7. 简历证据缺失只表示尚未验证，
   不代表候选人不具备能力。

【二、题目分布】

5 道题应尽量覆盖以下五类，每类原则上 1 道：

- 岗位匹配与求职动机
- 经历深挖与个人贡献
- 业务分析与产品设计
- AI 技术与应用基础
- 行为面试与学习成长

如果岗位 JD 明显不涉及某类内容，
可以将该题名额调整给更重要的岗位能力。

5 道题整体必须有区分度，
不能重复考察同一件事。

【三、个性化要求】

1. 经历深挖题必须引用候选人简历中真实存在的
   项目、职责、行动或结果，不得编造经历。

2. 业务分析题应尽可能贴近 JD 中的真实业务场景。

3. AI 技术题应围绕 JD 提及的技术及其业务应用，
   不要考无关的算法八股。

4. 对 Unverified 能力，可以设计岗位情境题
   或请候选人讲述相关方法，
   不得把未验证写成能力缺陷。

5. 题目应是面试官可以直接说出口的自然中文，
   清晰、具体，一题尽量只考察一个核心问题。

6. 不要在问题中泄露系统的匹配标签或评分结论。

7. 不要提供参考答案，不要替候选人补充经历。

【四、关键得分点生成要求】

1. 每道题必须生成 answer_key_points。
2. 每道题列出 3-5 个关键得分点。
3. 得分点应当是评价候选人回答时需要关注的能力、事实或逻辑。
4. 得分点必须对应题目实际考察的能力，不能泛泛罗列。
5. 不得把未经简历证实的经历、数据或结果写成候选人的事实。
6. 对于简历没有直接证据的能力，得分点应描述候选人需要解释的思路、方法或判断依据。
7. 不生成完整参考答案，不替候选人组织虚构的口述经历。
8. 不生成 question_rationale 和 evidence_basis。

【五、输出格式】

只返回合法 JSON，不要 Markdown，不要解释。

必须包含 questions 数组，且恰好 5 项。

每项字段：

{
  "question_id": "Q1",
  "category": "五类题型之一",
  "question": "可直接向候选人提出的问题",
  "assessed_capabilities": [
    "对应的岗位二级能力"
  ],
  "answer_key_points": [
    "关键得分点1",
    "关键得分点2",
    "关键得分点3"
  ],
  "follow_up_directions": [
    "可用于动态追问的方向，最多 2 个"
  ]
}
"""

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {
                "role": "user",
                "content": json.dumps(
                    model_input,
                    ensure_ascii=False,
                ),
            },
        ],
        temperature=0.4,
        response_format={
            "type": "json_object"
        },
    )

    content = response.choices[0].message.content

    result = _extract_json(content)

    return validate_interview_questions(result)