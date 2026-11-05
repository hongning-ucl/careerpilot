
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# =================================
# 1. 初始化 DeepSeek API
# =================================

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


# =================================
# 2. 固定的六大能力维度
# =================================

CAPABILITY_FRAMEWORK = [
    {
        "dimension": "产品架构能力",
        "description": "产品体系设计、功能架构、业务流程和系统规划能力"
    },
    {
        "dimension": "数据产品能力",
        "description": "数据获取、清洗、治理、分析、指标体系和数据应用能力"
    },
    {
        "dimension": "AI 技术理解",
        "description": "理解机器学习、深度学习、LLM、Agent、RAG 等技术原理及能力边界"
    },
    {
        "dimension": "AI 产品设计",
        "description": "AI 场景识别、人机协作、智能决策、AI 功能设计和效果评估能力"
    },
    {
        "dimension": "业务理解能力",
        "description": "行业认知、商业模式、用户需求、业务目标和经营指标理解能力"
    },
    {
        "dimension": "创新与落地能力",
        "description": "产品机会识别、创新方案设计、资源协调、项目推进和效果验证能力"
    }
]


# =================================
# 3. JD 分析主函数
# =================================

def analyze_jd(jd_text):

    if not jd_text or not jd_text.strip():
        raise ValueError("岗位 JD 不能为空")

    # ---------------------------------
    # System Prompt
    # ---------------------------------

    system_prompt = """
你是一名专业的招聘岗位分析专家和产品岗位能力建模专家。

你的任务是分析企业发布的 JD，
提取岗位职责、任职要求，并建立岗位能力模型。

本系统采用固定的六大一级能力维度。
你必须严格使用指定的六个维度，不得新增、删除或修改维度名称。

【一、核心分析原则】

1. 严格依据 JD 原文，不得编造岗位要求。
2. 先理解岗位业务任务，再判断所需能力。
3. 将分散在不同 JD 段落中的相似要求进行归纳。
4. 将岗位能力拆解为具体、可考察的二级能力。
5. 不要简单地将岗位职责复制为能力名称。
6. 不要将技术工具名称直接作为能力。
7. 不同能力维度之间应有清晰边界。
8. 不要为了填满六个维度而编造能力。
9. 同一项二级能力不要在不同维度重复出现。
10. 每项二级能力都必须关联 JD 原文或明确标记为推导。

【二、固定的六大能力维度】

1. 产品架构能力

主要考察：
产品体系设计、功能架构、业务流程、
系统规划、产品模块划分等。

2. 数据产品能力

主要考察：
数据获取、数据清洗、数据治理、
数据分析、指标体系、数据应用等。

3. AI 技术理解

主要考察：
机器学习、深度学习、LLM、Agent、RAG、
模型原理、技术架构、技术能力边界等。

4. AI 产品设计

主要考察：
AI 场景识别、人机协作、智能决策、
AI 功能设计、模型与业务结合、效果评估等。

5. 业务理解能力

主要考察：
行业认知、商业模式、用户需求、
业务目标、经营指标和市场趋势等。

6. 创新与落地能力

主要考察：
产品机会识别、创新方案设计、
资源协调、项目推进、产品落地和效果验证等。

以上是统一的能力分类框架。
具体二级能力必须根据当前 JD 动态提取，
不能直接把示例内容全部复制到结果中。

【三、能力归类规则】

当某项要求可能涉及多个能力维度时，
根据它最主要的考察目标进行归类。

例如：

- 商品数据体系设计：产品架构能力。
- 跨平台数据获取与数据治理：数据产品能力。
- Agent 工作机制和结构化输出原理：AI 技术理解。
- AI 导购和智能推荐方案设计：AI 产品设计。
- 海外电商商业模式：业务理解能力。
- 发现新场景并推动产品上线：创新与落地能力。

注意：
同一业务场景可能涉及多种能力，
但不同能力必须有不同的具体考察内容。

【四、二级能力提取规则】

每个二级能力必须包含：

capability：
具体能力名称，简洁明确。

description：
解释该能力具体要求候选人掌握什么。

evidence_source：

explicit：JD 明确提及该能力或相关要求。

inferred：JD 没有直接提及能力名称，
但可以根据明确的岗位职责合理推导。

source_evidence：
支持该能力判断的 JD 原文。
不得编造原文。

如果某个能力没有任何可靠的 JD 依据，
不要输出该能力。

【五、二级能力重要程度判断】

importance 必须针对每一项二级能力单独判断，
不得在一级能力维度层面统一设置或继承。
同一个一级维度下，不同二级能力可以有不同的重要程度。

importance 只能使用以下值：

must_have：JD 明确要求，且直接影响岗位核心职责完成的能力。

important：对完成岗位工作有明显价值，但并非最核心的胜任条件。

preferred：JD 明确表达的优先条件、加分能力或非必要要求。

unknown：JD 缺少足够信息，无法可靠判断重要程度。

判断时必须结合该项二级能力对应的 JD 原文、职责和上下文，
不得仅因为某项能力归属于某个一级维度，就给它相同的重要程度。
不要将所有能力默认设置为 must_have。

【六、其他信息提取】

job_responsibilities：
提取岗位的主要工作职责。

preferred_qualifications：
只提取 JD 明确表达的优先条件和加分项。

technical_skills：
提取明确出现的技术、工具、平台和框架。

industry_knowledge：
提取岗位涉及的行业和业务领域知识。

不得将以上信息与六大能力维度混为一谈。

【七、输出要求】

1. 必须完整输出六个一级能力维度。
2. 六个维度名称必须与指定名称完全一致。
3. 每个维度只出现一次。
4. 没有相关能力时，sub_capabilities 返回空数组。
5. 没有可靠依据时，importance 使用 unknown。
6. 不得为了让每个维度都有内容而自行补充能力。
7. 只返回合法 JSON，不输出 Markdown。

【能力维度边界与去重规则】

1. 产品架构能力
关注产品整体结构、模块划分、业务流程、
信息体系和系统规划。
不负责归类单纯的数据采集、清洗和治理能力。

2. 数据产品能力
关注数据获取、加工、清洗、校验、治理、
质量管理和数据应用。
跨平台数据获取与处理应优先归入此维度。

3. AI 技术理解
关注 AI 技术原理、模型工作机制、
Agent 运行逻辑、结构化输出机制和技术边界。
重点判断候选人是否理解技术本身。

4. AI 产品设计
关注如何将 AI 技术转化为具体产品功能，
包括 AI 导购、智能分发、个性化推荐、
人机交互和业务流程适配。

5. 业务理解能力
关注行业、商业模式、用户需求、
业务运营机制和经营目标。

6. 创新与落地能力
关注新机会识别、创新方向判断、
产品方案设计、资源协调和落地推进。

【跨维度去重】

1. 同一项具体能力原则上只能归入一个一级维度。
2. 如果一个业务场景涉及多个维度，
   应根据实际考察内容拆成不同能力，而不是重复复制。
3. AI 技术理解与 AI 产品设计必须区分：
   前者考察技术机制，后者考察产品应用。
4. AI 产品设计与创新落地必须区分：
   前者考察具体 AI 产品方案，后者考察机会识别与推进落地。
5. 数据产品能力与产品架构能力必须区分：
   前者考察数据生命周期，后者考察产品整体架构。

【二级能力拆分规则】

1. 根据 JD 中不同的职责、工作对象和专业方法，
   将一级能力维度拆分为具体的二级能力。

2. 不要机械地将每个一级维度限制为一项二级能力。
   如果同一维度包含多个独立的工作内容或专业能力，
   应拆分为多个二级能力。

3. 不要为了增加数量而过度拆分。
   如果多个职责实际上考察的是同一种能力，
   可以合并为一个二级能力。

4. 每个二级能力必须具备独立的考察价值，
   能够进一步转化为面试问题和评价标准。

5. 二级能力的 description 不要简单复述 JD。
   应描述候选人需要具备的具体知识、方法、
   判断能力或实际解决问题的能力。

【重要程度判断补充规则】

1. importance 是每项二级能力自己的属性，不是一级维度的属性。
2. 同一一级维度下的不同二级能力，必须分别判断重要程度。
3. preferred 表示 JD 明确表达的加分项或优先条件；
   如果 JD 没有足够信息判断，则使用 unknown。
4. 不允许因为某项能力属于核心维度，就自动将其标记为 must_have。

"""

    # ---------------------------------
    # User Prompt
    # ---------------------------------

    user_prompt = f"""
请分析以下岗位 JD，并建立岗位能力模型。

必须按照以下 JSON 结构输出：

{{
    "job": {{
        "job_title": null,
        "department": null,
        "seniority": null,
        "job_responsibilities": [],

        "capability_dimensions": [
            {{
                "dimension": "产品架构能力",
                "description": "产品体系设计、功能架构、业务流程和系统规划能力",
                "sub_capabilities": [
                    {{
                        "capability": null,
                        "description": null,
                        "importance": "unknown",
                        "evidence_source": "explicit",
                        "source_evidence": []
                    }}
                ]
            }},
            {{
                "dimension": "数据产品能力",
                "description": "数据获取、清洗、治理、分析和数据应用能力",
                "sub_capabilities": []
            }},
            {{
                "dimension": "AI 技术理解",
                "description": "AI 技术原理、架构及能力边界理解",
                "sub_capabilities": []
            }},
            {{
                "dimension": "AI 产品设计",
                "description": "AI 场景识别、功能设计及业务应用能力",
                "sub_capabilities": []
            }},
            {{
                "dimension": "业务理解能力",
                "description": "行业、商业模式、用户需求和业务目标理解",
                "sub_capabilities": []
            }},
            {{
                "dimension": "创新与落地能力",
                "description": "产品机会识别、方案设计和落地推进能力",
                "sub_capabilities": []
            }}
        ],

        "preferred_qualifications": [],
        "technical_skills": [],
        "industry_knowledge": []
    }}
}}

【能力模型生成步骤】

第一步：理解岗位

识别岗位名称、主要职责、业务场景和任职要求。

第二步：提取具体能力

从岗位职责和任职要求中提取可用于面试考察的具体能力。

第三步：能力分类

将每项具体能力归入六大固定维度之一。

第四步：能力聚合

将不同 JD 段落中相似的能力合并，
避免重复提取。

第五步：证据关联

为每项二级能力提供原文依据，
并判断其属于 explicit 还是 inferred。

第六步：重要程度判断

针对每一项二级能力，结合其对应的 JD 原文、职责和上下文，
独立判断 importance。
同一一级维度下的不同二级能力可以具有不同的重要程度。
一级维度本身不设置 importance。

【特别注意】

1. 六大一级维度必须全部出现。
2. 二级能力数量不固定，完全由 JD 内容决定。
3. 一个维度可以有多项二级能力。
4. 一个维度也可以没有二级能力。
5. 不要将所有职责平均分配到六个维度。
6. 不要为了追求六个维度都有内容而推测岗位要求。
7. 不同维度之间不能出现明显重复的二级能力。
8. 必须保留每项二级能力对应的 JD 证据。

岗位 JD 原文：

{jd_text}
"""

    # ---------------------------------
    # 4. 调用 DeepSeek
    # ---------------------------------

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
        max_tokens=3500,
        response_format={
            "type": "json_object"
        }
    )

    # ---------------------------------
    # 5. 解析 JSON
    # ---------------------------------

    content = response.choices[0].message.content

    if not content:
        raise ValueError("DeepSeek 未返回有效内容")

    try:
        result = json.loads(content)
    except json.JSONDecodeError as e:
        raise ValueError(f"JD 解析结果不是有效 JSON：{e}")

    # ---------------------------------
    # 6. 结构校验
    # ---------------------------------

    if "job" not in result:
        raise ValueError("JD 解析结果缺少 job 字段")

    job = result["job"]

    required_fields = [
        "job_title",
        "department",
        "seniority",
        "job_responsibilities",
        "capability_dimensions",
        "preferred_qualifications",
        "technical_skills",
        "industry_knowledge"
    ]

    for field in required_fields:
        if field not in job:
            raise ValueError(f"JD 解析结果缺少字段：{field}")

    # 检查六大维度是否完整
    expected_dimensions = [
        item["dimension"] for item in CAPABILITY_FRAMEWORK
    ]

    actual_dimensions = [
        item.get("dimension")
        for item in job["capability_dimensions"]
    ]

    if actual_dimensions != expected_dimensions:
        raise ValueError(
            "能力维度不符合固定的六维框架。"
            f"预期：{expected_dimensions}；"
            f"实际：{actual_dimensions}"
        )

    # 检查每个维度的字段
    for dimension in job["capability_dimensions"]:

        if "importance" in dimension:
            raise ValueError(
                f"{dimension['dimension']} 不应设置一级 importance；"
                "importance 应属于每项二级能力"
            )

        if not isinstance(dimension.get("sub_capabilities"), list):
            raise ValueError(
                f"{dimension['dimension']} 的 sub_capabilities 必须是列表"
            )

        for capability in dimension["sub_capabilities"]:

            required_capability_fields = [
                "capability",
                "description",
                "importance",
                "evidence_source",
                "source_evidence"
            ]

            for field in required_capability_fields:
                if field not in capability:
                    raise ValueError(
                        f"二级能力缺少字段：{field}"
                    )

            if capability["importance"] not in [
                "must_have",
                "important",
                "preferred",
                "unknown"
            ]:
                raise ValueError(
                    "importance 只能是 must_have、important、preferred 或 unknown"
                )

            if capability["evidence_source"] not in [
                "explicit",
                "inferred"
            ]:
                raise ValueError(
                    "evidence_source 只能是 explicit 或 inferred"
                )

    return result
