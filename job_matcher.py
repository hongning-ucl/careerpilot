import os
import json
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
# job_matcher.py

# ==========================================
# 1. 匹配规则配置
# ==========================================

MATCH_LEVELS = [
    "direct",
    "transferable",
    "unverified"
]

IMPORTANCE_LEVELS = [
    "must_have",
    "important",
    "nice_to_have",
    "unknown"
]

EVIDENCE_TYPES = [
    "background",
    "responsibility",
    "action",
    "result"
]

REQUIRED_MATCH_FIELDS = [
    "dimension",
    "capability",
    "importance",
    "match_level",
    "evidence",
    "match_reason",
    "missing_evidence"
]


# ==========================================
# 2. 匹配结果模板
# ==========================================

def create_match_template():
    """
    创建一条岗位能力匹配记录。
    """

    return {
        "dimension": "",
        "capability": "",
        "importance": "unknown",
        "match_level": "unverified",
        "evidence": [],
        "match_reason": "",
        "missing_evidence": [],
        "suggested_question": ""
    }


def create_matching_result():
    """
    创建完整的岗位能力匹配结果。
    """

    return {
        "candidate_profile": {
            "career_stage": "unknown",
            "career_transition": None
        },
        "capability_matches": [],
        "matching_summary": {
            "direct_count": 0,
            "transferable_count": 0,
            "unverified_count": 0
        }
    }


# ==========================================
# 3. 单条证据校验
# ==========================================

def validate_evidence(evidence):
    """
    检查简历证据是否符合规范。
    """

    required_fields = [
        "experience_id",
        "experience_name",
        "evidence_type",
        "evidence_text"
    ]

    if not isinstance(evidence, dict):
        return False

    for field in required_fields:
        if field not in evidence:
            return False

    if evidence["evidence_type"] not in EVIDENCE_TYPES:
        return False

    if not isinstance(evidence["evidence_text"], str):
        return False

    if not evidence["evidence_text"].strip():
        return False

    return True


# ==========================================
# 4. 单项能力匹配结果校验
# ==========================================

def validate_capability_match(match):
    """
    检查一项 JD 二级能力的匹配结果。
    """

    if not isinstance(match, dict):
        return False

    # 检查必要字段
    for field in REQUIRED_MATCH_FIELDS:
        if field not in match:
            return False

    # 检查匹配等级
    if match["match_level"] not in MATCH_LEVELS:
        return False

    # 检查重要程度
    if match["importance"] not in IMPORTANCE_LEVELS:
        return False

    # 检查证据列表
    if not isinstance(match["evidence"], list):
        return False

    for evidence in match["evidence"]:
        if not validate_evidence(evidence):
            return False

    # 检查缺失证据列表
    if not isinstance(match["missing_evidence"], list):
        return False

    # 待验证状态不能有支持匹配的证据
    if match["match_level"] == "unverified":
        if match["evidence"]:
            return False

    # 直接匹配和可迁移匹配必须有证据
    if match["match_level"] in ["direct", "transferable"]:
        if not match["evidence"]:
            return False

    return True


# ==========================================
# 5. 完整匹配结果校验
# ==========================================

def validate_matching_result(result):
    """
    检查完整的岗位能力匹配结果。
    """

    if not isinstance(result, dict):
        raise ValueError("匹配结果必须是字典。")

    required_fields = [
        "candidate_profile",
        "capability_matches",
        "matching_summary"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(f"缺少必要字段：{field}")

    # 检查候选人信息
    profile = result["candidate_profile"]

    if not isinstance(profile, dict):
        raise ValueError("candidate_profile 必须是字典。")

    if "career_stage" not in profile:
        raise ValueError("缺少 career_stage。")

    if "career_transition" not in profile:
        raise ValueError("缺少 career_transition。")

    # 检查能力匹配列表
    matches = result["capability_matches"]

    if not isinstance(matches, list):
        raise ValueError("capability_matches 必须是列表。")

    for index, match in enumerate(matches):
        if not validate_capability_match(match):
            raise ValueError(
                f"第 {index + 1} 项能力匹配结果不符合规范。"
            )

    # 检查汇总数量
    summary = result["matching_summary"]

    expected_summary = {
        "direct_count": sum(
            1 for m in matches
            if m["match_level"] == "direct"
        ),
        "transferable_count": sum(
            1 for m in matches
            if m["match_level"] == "transferable"
        ),
        "unverified_count": sum(
            1 for m in matches
            if m["match_level"] == "unverified"
        )
    }

    if summary != expected_summary:
        raise ValueError(
            f"匹配统计数量不一致。正确结果应为：{expected_summary}"
        )

    return True


def extract_experience_evidence(resume_data):
    """
    从简历解析结果中提取结构化经历证据。

    输入：
        resume_data：resume_analyzer.py 返回的 JSON

    输出：
        evidence_list：统一格式的经历证据列表
    """

    if not isinstance(resume_data, dict):
        raise ValueError("resume_data 必须是字典")

    experiences = resume_data.get("experiences", [])

    if not isinstance(experiences, list):
        raise ValueError("experiences 必须是列表")

    evidence_list = []

    # 不同字段对应的证据类型
    evidence_fields = {
        "background": "background",
        "responsibilities": "responsibility",
        "actions": "action",
        "results": "result"
    }

    for index, experience in enumerate(experiences, start=1):

        experience_id = f"exp_{index:03d}"

        organization = experience.get("organization")
        project_name = experience.get("project_name")
        position = experience.get("position")

        # 组合经历名称
        name_parts = [
            item for item in [organization, project_name]
            if item
        ]

        experience_name = "｜".join(name_parts)

        # 遍历背景、职责、行动和结果
        for field, evidence_type in evidence_fields.items():

            content = experience.get(field)

            if isinstance(content, str):
                content = [content]

            if not isinstance(content, list):
                continue

            for text in content:

                if not isinstance(text, str) or not text.strip():
                    continue

                evidence_list.append({
                    "experience_id": experience_id,
                    "experience_name": experience_name,
                    "experience_type": experience.get(
                        "experience_type", "other"
                    ),
                    "position": position,
                    "evidence_type": evidence_type,
                    "evidence_text": text.strip()
                })

    return evidence_list

def match_resume_to_jd(resume_data, jd_data):
    """
    将简历经历证据与 JD 岗位能力进行语义匹配。

    输入：
        resume_data：简历解析结果
        jd_data：JD 解析结果

    输出：
        matching_result：岗位能力匹配结果
    """

    # ==================================
    # 1. 检查输入
    # ==================================

    if not isinstance(resume_data, dict):
        raise ValueError("resume_data 必须是字典")

    if not isinstance(jd_data, dict):
        raise ValueError("jd_data 必须是字典")

    job = jd_data.get("job")

    if not isinstance(job, dict):
        raise ValueError("jd_data 缺少 job 字段")

    dimensions = job.get("capability_dimensions", [])

    if not isinstance(dimensions, list):
        raise ValueError("capability_dimensions 必须是列表")

    # ==================================
    # 2. 提取 JD 二级能力
    # ==================================

    capability_list = []

    importance_mapping = {
        "must_have": "must_have",
        "important": "important",
        "preferred": "nice_to_have",
        "nice_to_have": "nice_to_have",
        "unknown": "unknown"
    }

    for dimension in dimensions:

        dimension_name = dimension.get("dimension")

        sub_capabilities = dimension.get(
            "sub_capabilities", []
        )

        for capability in sub_capabilities:

            # importance 属于 JD 二级能力，不从一级维度继承
            capability_importance = capability.get(
                "importance", "unknown"
            )

            importance = importance_mapping.get(
                capability_importance, "unknown"
            )

            capability_list.append({
                "capability_id": f"cap_{len(capability_list) + 1:03d}",
                "dimension": dimension_name,
                "capability": capability.get("capability"),
                "description": capability.get("description"),
                "importance": importance,
                "source_evidence": capability.get(
                    "source_evidence", []
                )
            })

    if not capability_list:
        raise ValueError("JD 中没有可匹配的二级能力")

    # ==================================
    # 3. 提取简历证据
    # ==================================

    evidence_list = extract_experience_evidence(
        resume_data
    )

    if not evidence_list:
        raise ValueError("简历中没有可用于匹配的经历证据")

    # 为每条证据增加唯一 ID
    for index, evidence in enumerate(evidence_list):

        evidence["evidence_id"] = f"ev_{index + 1:03d}"

    # ==================================
    # 4. 准备模型输入
    # ==================================

    candidate_profile = resume_data.get(
        "candidate", {}
    )

    model_input = {
        "capabilities": capability_list,
        "resume_evidence": evidence_list
    }

    system_prompt = """
你是一名专业的招聘岗位能力匹配分析助手。

你的任务是将 JD 中的具体岗位能力与候选人简历中的实际经历证据进行关联。

一、匹配原则

1. 只能使用输入中提供的 JD 能力和简历证据。
2. 不得编造候选人的经历、技能、行动或结果。
3. 每项岗位能力独立判断。
4. 一项岗位能力可以关联多条简历证据。
5. 同一条简历证据可以支持不同的岗位能力，但必须有合理的语义关联。

二、匹配等级

direct：
简历中存在明确、具体且高度相关的经历证据，
候选人曾在相同或高度相似的场景中体现该能力。

transferable：
简历中存在相关的方法、经验或解决问题的能力，
但实际应用场景与目标岗位存在差异，
可以合理迁移。

unverified：
现有简历没有足够证据证明候选人具备该能力。

注意：
unverified 不代表候选人不具备该能力，
只代表当前简历无法验证。

三、证据使用规则

1. 必须使用输入中真实存在的 evidence_id。
2. 不得修改或重写原始证据。
3. background 仅用于理解业务上下文，
   不得单独作为 direct 或 transferable 的能力证明。
4. 优先使用 responsibility、action 和 result 作为能力证据。
5. 如果没有足够的支持证据，必须选择 unverified。
6. 不得为了提高匹配数量而降低证据标准。

四、匹配理由

match_reason：
说明匹配等级的判断依据，结合具体证据解释。

missing_evidence：
记录目前简历中缺少哪些能够验证该能力的信息。
如果现有证据已经充分，可以返回空数组。

suggested_question：
提出一个能够进一步验证该项能力的问题。
问题应具体，避免泛泛而谈。

五、输出要求

严格按照输入中的 capability_id 顺序，
为每项岗位能力返回一条匹配记录。

不得新增、删除或修改岗位能力。

只返回合法 JSON，不输出 Markdown。
"""

    user_prompt = f"""
请完成以下简历与岗位能力匹配任务。

输入数据：

{json.dumps(model_input, ensure_ascii=False)}

按照以下 JSON 格式返回：

{{
    "matches": [
        {{
            "capability_id": "cap_001",
            "match_level": "direct",
            "evidence_ids": ["ev_001"],
            "match_reason": "匹配理由",
            "missing_evidence": [],
            "suggested_question": "建议追问的问题"
        }}
    ]
}}
"""

    # ==================================
    # 5. 调用 DeepSeek
    # ==================================

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],
        temperature=0.1,
        max_tokens=4000,
        response_format={
            "type": "json_object"
        }
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("DeepSeek 未返回有效匹配结果")

    try:
        model_result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"匹配结果不是有效 JSON：{e}")

    # ==================================
    # 6. 建立证据索引
    # ==================================

    evidence_index = {
        item["evidence_id"]: item
        for item in evidence_list
    }

    capability_index = {
        item["capability_id"]: item
        for item in capability_list
    }

    model_matches = model_result.get("matches", [])

    if not isinstance(model_matches, list):
        raise ValueError("模型返回的 matches 必须是列表")

    returned_ids = [
        item.get("capability_id")
        for item in model_matches
    ]

    expected_ids = [
        item["capability_id"]
        for item in capability_list
    ]

    if (
        len(returned_ids) != len(expected_ids)
        or set(returned_ids) != set(expected_ids)
    ):
        raise ValueError("模型返回的岗位能力数量或 ID 不正确")

    # ==================================
    # 7. 组装匹配结果
    # ==================================

    result = create_matching_result()

    result["candidate_profile"] = {
        "career_stage": candidate_profile.get(
            "career_stage", "unknown"
        ),
        "career_transition": candidate_profile.get(
            "career_transition"
        )
    }

    for model_match in model_matches:

        capability_id = model_match["capability_id"]

        capability = capability_index[capability_id]

        match_level = model_match.get("match_level")

        if match_level not in MATCH_LEVELS:
            raise ValueError(
                f"{capability_id} 的匹配等级不合法"
            )

        selected_ids = model_match.get(
            "evidence_ids", []
        )

        if not isinstance(selected_ids, list):
            raise ValueError("evidence_ids 必须是列表")

        # 只允许引用真实存在的证据
        selected_evidence = []

        for evidence_id in selected_ids:

            if evidence_id not in evidence_index:
                raise ValueError(
                    f"模型引用了不存在的证据：{evidence_id}"
                )

            evidence = evidence_index[evidence_id]

            # 背景不能单独证明岗位能力
            if evidence["evidence_type"] == "background":
                continue

            selected_evidence.append({
                key: value
                for key, value in evidence.items()
                if key != "evidence_id"
            })

        # 没有有效证据时，必须降为 unverified
        if not selected_evidence:
            match_level = "unverified"

        elif match_level == "unverified":
            selected_evidence = []

        match_record = create_match_template()

        match_record.update({
            "dimension": capability["dimension"],
            "capability": capability["capability"],
            "importance": capability["importance"],
            "match_level": match_level,
            "evidence": selected_evidence,
            "match_reason": model_match.get(
                "match_reason", ""
            ),
            "missing_evidence": model_match.get(
                "missing_evidence", []
            ),
            "suggested_question": model_match.get(
                "suggested_question", ""
            )
        })

        result["capability_matches"].append(
            match_record
        )

    # ==================================
    # 8. 自动统计匹配数量
    # ==================================

    matches = result["capability_matches"]

    result["matching_summary"] = {
        "direct_count": sum(
            1 for item in matches
            if item["match_level"] == "direct"
        ),
        "transferable_count": sum(
            1 for item in matches
            if item["match_level"] == "transferable"
        ),
        "unverified_count": sum(
            1 for item in matches
            if item["match_level"] == "unverified"
        )
    }

    # ==================================
    # 9. 结果校验
    # ==================================

    validate_matching_result(result)

    return result