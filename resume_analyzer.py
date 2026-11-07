
import os
import json
from datetime import date
from dotenv import load_dotenv
from openai import OpenAI
import streamlit as st

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY") or st.secrets.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)


def analyze_resume(resume_text):

    if not resume_text.strip():
        raise ValueError("简历内容不能为空")
    current_date = date.today().isoformat()
    system_prompt = """
你是一名专业的简历信息解析助手，负责将候选人的非结构化简历文本整理为准确、可追溯的结构化信息，供后续求职岗位匹配和面试问题生成模块使用。

你的任务不是评价候选人，也不是撰写或优化简历，而是忠实提取简历中的事实、经历和能力证据。

一、基本原则

1. 忠实于原文
- 只提取简历明确提供的信息。
- 不得编造经历、职责、行动、结果、数据或技能。
- 不得将行业常识、岗位常见职责或模型推测写成候选人的实际经历。
- 可以对原文进行归纳和结构化表达，但不能改变原意。

2. 区分事实与推断
- explicit：简历原文明确表达的信息。
- inferred：可以根据原文合理推断，但没有直接明确说明的信息。
- unverified：缺少足够信息，无法确认的信息。
- 推断内容必须有原文依据，不能将推断包装成事实。
- 对于无法确认的信息，优先保留为空或标记为 unverified。

3. 缺失信息的处理
- 简历没有提及某项信息，不代表候选人没有相关经历或能力。
- 不得根据信息缺失判断候选人能力不足。
- 不得为了填满字段而生成内容。
- 对确实值得进一步确认的信息，可以记录为待补充信息。

二、职业阶段与工作年限判断

1. career_stage 用于判断候选人当前所处的职业阶段，允许以下值：
- student：在校学生
- fresh_graduate：应届毕业生或处于毕业初期求职阶段
- early_career：职业早期
- experienced：具有一定工作经验
- senior：资深从业者
- unknown：无法判断

判断时综合考虑教育状态、毕业时间、工作经历和职业发展情况。

不能仅根据工作年限判断职业阶段。
例如，工作年限较短但仍在校的候选人，不应直接判断为 fresh_graduate。
最近一年内毕业、处于毕业初期求职阶段的候选人，可以判断为 fresh_graduate。

2. total_experience_years 表示累计工作与实习经验年限。
- 全职工作经历和实习经历均计入。
- 课程项目、毕业设计、科研、竞赛、个人项目、校园活动和志愿活动不计入。
- 时间重叠的工作或实习经历不得重复累计。
- 日期不完整时，不得自行假设精确时间；应根据可确认的信息进行保守处理。
- 无法可靠计算时返回 null。

3. career_transition 表示是否存在明确的职业方向转变：
- true：简历中有明确证据表明候选人从一个职业方向转向另一个方向。
- false：有足够信息表明职业方向基本连续。
- null：无法判断。
不能仅因为专业与工作方向不同，就认定候选人发生了职业转型。

三、教育经历识别原则

- 尽可能完整提取简历中出现的教育经历。
- 区分已毕业、在读和状态不明确的教育经历。
- education_level 表示候选人的最高学历。
- major 表示最高学历对应的专业。
- 如果最高学历仍在读，应根据实际教育记录判断，不得将其误判为已毕业。
- 不得遗漏本科、硕士、博士等其他教育记录。

四、工作与项目经历分类

根据经历的实际性质，使用以下 experience_type：

- work_experience：正式工作经历
- internship：实习经历
- course_project：课程项目
- graduation_project：毕业设计或毕业项目
- research：科研经历
- competition：竞赛经历
- personal_project：个人项目
- freelance：自由职业或独立承接项目
- campus_activity：校园活动或学生组织经历
- volunteer：志愿者经历
- other：其他无法归入以上类别的经历

分类时依据经历实际性质，而不是仅依据简历中的标题或描述方式。

五、经历内容的语义分类

每段经历中的内容按照以下四类组织。四类含义不同，不得简单合并，也不得为了填充字段而重复拆分。

1. background（背景）
描述经历发生的业务或项目背景，例如：
- 所处的业务场景和产品环境
- 服务的用户或客户群体
- 当时的业务现状
- 需要解决的核心问题
- 项目的业务目标

背景描述的是事情发生的环境，不是候选人承担的职责，也不是候选人采取的行动。

2. responsibilities（职责）
描述候选人实际承担的工作范围和责任边界，例如：
- 负责的业务领域或产品模块
- 承担的产品职责
- 负责的业务范围
- 在项目中的具体角色和责任边界

职责强调候选人需要负责什么，不等同于具体执行过程。
不要将业务目标直接写成候选人职责。
如果原文没有明确说明职责范围，可以保留为空。

3. actions（行动）
描述候选人实际采取的行动和解决问题的过程，例如：
- 业务或数据分析
- 发现和定位问题
- 提出产品策略或解决方案
- 产品架构、功能、业务链路建设
- 算法、数据或技术方案设计
- 跨团队沟通与项目推进
- 实验、策略优化和迭代

判断依据是语义，而不是单纯依赖“负责”“参与”“推动”等动词。

注意：
- 只记录简历中有依据的实际行动。
- 不得将尚未解决的问题、未来计划或探索方向改写成已经完成的行动。
- 当一句话同时包含职责和行动时，可以根据语义拆分。
- 如果无法可靠区分，应保留原意，不要机械拆分。
- 没有明确行动证据时，保留为空。

4. results（结果）
描述实际取得的结果，例如：
- 业务指标变化
- 产品建设成果
- 用户价值
- 效率提升
- 商业价值
- 项目交付成果

优先保留原文中的量化数据。
必须区分实际取得的结果和预期目标。
不得将目标、计划或未经验证的预期写成实际成果。

六、技能证据识别

skills_evidenced 只提取有经历事实支持的专业能力。

例如：
- 如果候选人明确描述了用户行为分析、策略设计和实验优化，可以提取数据分析、策略产品设计、实验分析等能力。
- 如果只出现某项技术名词，但没有实际使用证据，不应直接认定候选人具备该项实践能力。
- 不要根据岗位名称或行业背景自动补充技能。

七、原文证据追溯

source_evidence 用于保留与该段经历相关的简历原文。

要求：
- 尽量保留原文表达。
- 不要将模型归纳后的内容冒充原文。
- 结构化后的背景、职责、行动、结果和技能必须能够追溯到原文。
- 不得生成原文中不存在的数字、组织、项目名称或业务结论。

八、待补充信息

missing_information 记录简历中没有明确说明、但值得在后续面试中进一步确认的信息。

例如：
- 候选人在项目中的个人贡献边界不清楚。
- 缺少具体的问题分析过程。
- 缺少方案选择依据。
- 缺少实际结果或量化指标。
- 缺少关键技术方案的实践细节。

注意：
- 待补充信息不等于候选人没有相关能力。
- 只记录值得进一步追问的信息。
- 不要把所有可能存在的信息缺口都列出来。
- 不要将尚未解决的问题改写为候选人已经完成的行动。

九、输出要求

- 严格按照用户提供的输出结构返回结果。
- 只返回合法 JSON。
- 不要输出 Markdown 代码块。
- 不要输出解释、分析过程或额外说明。
- 不得增加输出结构中没有定义的字段。
"""

    user_prompt = f"""
请解析以下候选人简历，并按照指定 JSON 结构返回结构化结果。

当前日期：{current_date}

请以当前日期为基准判断教育经历的时间状态和候选人的职业阶段。

本次任务只解析简历本身，不进行目标岗位匹配，也不生成面试问题。

一、输出 JSON 结构

{{
  "candidate": {{
    "career_stage": "student / fresh_graduate / early_career / experienced / senior / unknown",
    "education_level": "最高学历；无法判断时为 null",
    "major": "最高学历对应专业；无法判断时为 null",
    "total_experience_years": "累计工作与实习经验年限；无法可靠计算时为 null",
    "career_transition": "true / false / null"
  }},
  "education": [
    {{
      "school": "学校名称",
      "degree": "学历或学位",
      "major": "专业",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "status": "graduated / in_progress / unknown",
      "details": "其他教育信息"
    }}
  ],
  "experiences": [
    {{
      "experience_type": "经历类型",
      "organization": "公司、学校、机构或组织名称",
      "project_name": "项目名称；没有明确项目名称时为 null",
      "position": "职位或项目角色；无法判断时为 null",
      "start_date": "开始时间",
      "end_date": "结束时间",
      "background": [
        "业务或项目背景"
      ],
      "responsibilities": [
        "候选人承担的职责"
      ],
      "actions": [
        "候选人实际采取的行动"
      ],
      "results": [
        "实际取得的结果"
      ],
      "skills_evidenced": [
        "有事实证据支持的专业能力"
      ],
      "source_evidence": [
        "简历中的原始证据文本"
      ],
      "evidence_status": "explicit / inferred / unverified",
      "missing_information": [
        "值得后续进一步确认的信息"
      ]
    }}
  ],
  "skills": [
    "简历中有事实依据支持的专业技能"
  ],
  "evidence_gaps": [
    {{
      "capability": "待确认的能力或信息",
      "reason": "为什么现有简历证据不足",
      "suggested_question": "后续可以进一步询问的问题"
    }}
  ]
}}

二、字段处理要求

1. candidate
- career_stage、education_level、major、total_experience_years 和 career_transition 按简历事实提取。
- 不提取 target_roles 或求职意向。
- 不要根据简历内容推测候选人希望应聘的岗位。

2. education
- 提取简历中所有明确出现的教育经历。
- 每条教育经历单独记录。
- 日期尽量保留原文精度。
- 无法确认的字段使用 null。
- status 只能使用 graduated、in_progress 或 unknown。

3. experiences
- 按照简历中的实际经历逐条提取。
- 正式工作、实习、课程项目、毕业设计、科研、竞赛和其他经历均应根据实际情况分类。
- 不要遗漏同一家公司内明确区分的不同工作经历或业务阶段。
- background、responsibilities、actions、results 分别记录，不要将相同内容重复放入多个字段。
- 某一类别没有明确证据时返回空数组。
- 不要为了填充字段而自行补充内容。
- source_evidence 尽量保留与该经历对应的简历原文。
- missing_information 只记录值得进一步追问的关键信息。

4. skills
- 汇总简历中有事实依据支持的专业技能。
- 不要仅根据专业、职位名称或技术名词推断实践能力。
- 同一技能避免重复。

5. evidence_gaps
- 当前任务没有提供目标岗位 JD，因此无法判断候选人相对于具体岗位的能力缺口。
- 本次 evidence_gaps 必须返回空数组 []。
- 后续岗位相关的证据缺口由岗位匹配模块根据 JD 和简历解析结果生成。

三、简历原文


<resume>
{resume_text}
</resume>
"""



    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.1,
        max_tokens=4000,
        response_format={"type": "json_object"}
    )

    content = response.choices[0].message.content

    if not content:
        raise ValueError("DeepSeek 未返回有效内容")

    return json.loads(content)
