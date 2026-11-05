
# resume_parser.py
# CareerPilot：简历经历结构化解析

from pprint import pprint


# ==================================================
# 一、单段经历的数据结构模板
# ==================================================

EXPERIENCE_TEMPLATE = {

    # 1. 基本信息
    "basic_info": {
        "experience_type": None,
        "company": None,
        "position": None,
        "domain": None,
    },

    # 2. 项目背景
    "project_context": {
        "project_name": None,
        "project_goal": None,
        "business_problem": None,
    },

    # 3. 个人职责
    "responsibility": {
        "candidate_role": None,
        "responsibility_scope": [],
        "ownership_level": None,
    },

    # 4. 具体行动
    "actions": [
        {
            "action": None,
            "method": None,
            "tools": [],
        }
    ],

    # 5. 项目结果
    "results": [
        {
            "metric": None,
            "value": None,
            "direction": None,
            "evidence": None,
        }
    ],

    # 6. 信息缺口
    "evidence_gaps": [
        {
            "field": None,
            "issue": None,
            "importance": None,
        }
    ],

    # 7. 原始简历描述，用于信息回溯
    "source_text": None,
}


# ==================================================
# 二、张晨的实习经历：人工解析示例
# ==================================================

internship_example = {

    "basic_info": {
        "experience_type": "internship",
        "company": "某互联网科技公司",
        "position": "产品经理实习生",
        "domain": "短视频广告",
    },

    "project_context": {
        "project_name": "广告投放后台功能优化",
        "project_goal": "优化广告投放后台功能",
        "business_problem": "部分广告计划点击率较低",
    },

    "responsibility": {
        "candidate_role": "产品经理实习生",
        "responsibility_scope": [
            "协助收集业务需求",
            "整理产品需求文档",
            "参与广告投放数据分析",
            "参与素材管理功能优化",
            "跟进需求评审及上线",
        ],
        "ownership_level": "参与及协助，独立负责范围尚不明确",
    },

    "actions": [
        {
            "action": "收集业务需求",
            "method": None,
            "tools": [],
        },
        {
            "action": "分析广告投放数据",
            "method": None,
            "tools": [],
        },
        {
            "action": "参与素材管理功能优化",
            "method": None,
            "tools": [],
        },
        {
            "action": "跟进需求评审及功能上线",
            "method": "跨团队协作",
            "tools": [],
        },
    ],

    "results": [
        {
            "metric": "功能使用率",
            "value": None,
            "direction": "提升",
            "evidence": "简历描述上线后相关功能使用率有所提升",
        }
    ],

    "evidence_gaps": [
        {
            "field": "responsibility_scope",
            "issue": "候选人独立负责的工作范围不明确",
            "importance": "high",
        },
        {
            "field": "data_analysis",
            "issue": "数据分析方法和指标口径不明确",
            "importance": "high",
        },
        {
            "field": "product_solution",
            "issue": "素材管理功能具体优化方案不明确",
            "importance": "high",
        },
        {
            "field": "results",
            "issue": "功能使用率缺少具体提升幅度",
            "importance": "medium",
        },
    ],

    "source_text": (
        "参与短视频平台广告投放后台的产品功能优化，"
        "协助收集业务需求并整理产品需求文档。"
        "通过分析广告投放数据，发现部分广告计划存在点击率较低的问题，"
        "参与优化广告素材管理功能。"
        "与研发、设计、运营团队协作，跟进需求评审及功能上线。"
        "上线后相关功能使用率有所提升。"
    ),
}


# ==================================================
# 三、基础数据校验
# ==================================================

def validate_experience(experience):

    required_fields = [
        "basic_info",
        "project_context",
        "responsibility",
        "actions",
        "results",
        "evidence_gaps",
        "source_text",
    ]

    for field in required_fields:
        if field not in experience:
            raise ValueError(f"缺少必要字段：{field}")

    if not isinstance(experience["actions"], list):
        raise TypeError("actions 必须是列表")

    if not isinstance(experience["results"], list):
        raise TypeError("results 必须是列表")

    if not isinstance(experience["evidence_gaps"], list):
        raise TypeError("evidence_gaps 必须是列表")

    return True


# ==================================================
# 四、测试入口
# ==================================================

if __name__ == "__main__":

    validate_experience(internship_example)

    print("简历经历结构校验通过！")

    print("\n基本信息：")
    pprint(internship_example["basic_info"])

    print("\n个人职责：")
    pprint(internship_example["responsibility"])

    print("\n项目结果：")
    pprint(internship_example["results"])

    print("\n信息缺口：")
    pprint(internship_example["evidence_gaps"])
