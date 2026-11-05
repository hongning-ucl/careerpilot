
# interview_blueprint.py
# CareerPilot：应届生面试策略引擎

from copy import deepcopy


# ==================================================
# 一、目标用户配置
# ==================================================

CANDIDATE_LEVELS = {
    "fresh_graduate": {
        "name": "应届毕业生",
        "description": "面向应届毕业生及海外留学生",
        "default": True,
    }
}


# 候选人可能具备的经历类型
EXPERIENCE_TYPES = {
    "internship": "实习经历",
    "course_project": "课程项目",
    "graduation_project": "毕业设计",
    "research": "科研经历",
    "competition": "竞赛经历",
    "personal_project": "个人项目",
    "campus_activity": "校园活动与社团经历",
}


# ==================================================
# 二、岗位类型与题型权重
# ==================================================

ROLE_PROFILES = {

    "AI产品经理": {
        "weights": {
            "岗位匹配与求职动机": 15,
            "经历深挖与个人贡献": 25,
            "业务分析与产品设计": 25,
            "AI技术与应用基础": 25,
            "行为面试与学习成长": 10,
        }
    },

    "广告/推荐产品经理": {
        "weights": {
            "岗位匹配与求职动机": 15,
            "经历深挖与个人贡献": 25,
            "业务分析与产品设计": 30,
            "AI技术与应用基础": 15,
            "行为面试与学习成长": 15,
        }
    },

    "通用互联网产品经理": {
        "weights": {
            "岗位匹配与求职动机": 15,
            "经历深挖与个人贡献": 25,
            "业务分析与产品设计": 35,
            "AI技术与应用基础": 10,
            "行为面试与学习成长": 15,
        }
    },
}


# ==================================================
# 三、不同题型的考察目标与素材来源
# ==================================================

QUESTION_TYPE_CONFIG = {

    "岗位匹配与求职动机": {
        "objective": "考察候选人对岗位、行业和职业发展的理解",
        "evidence_types": [
            "教育背景",
            "专业知识",
            "实习经历",
            "职业规划",
        ],
    },

    "经历深挖与个人贡献": {
        "objective": "考察候选人解决问题、执行任务和承担责任的能力",
        "evidence_types": [
            "实习经历",
            "课程项目",
            "毕业设计",
            "科研经历",
            "竞赛经历",
            "个人项目",
        ],
    },

    "业务分析与产品设计": {
        "objective": "考察产品思维、业务分析、用户理解和方案设计能力",
        "evidence_types": [
            "案例分析",
            "产品设计题",
            "商业场景题",
            "课程项目",
            "实习经历",
        ],
    },

    "AI技术与应用基础": {
        "objective": "考察技术基础、AI应用理解和技术与业务结合能力",
        "evidence_types": [
            "专业课程",
            "AI个人项目",
            "课程项目",
            "毕业设计",
            "实习经历",
        ],
    },

    "行为面试与学习成长": {
        "objective": "考察沟通协作、主动性、学习能力和问题复盘能力",
        "evidence_types": [
            "实习经历",
            "课程项目",
            "竞赛经历",
            "校园活动",
            "跨文化经历",
        ],
    },
}


# ==================================================
# 四、面试流程配置
# ==================================================

INTERVIEW_CONFIG = {
    "duration_minutes": 15,
    "main_question_count": 5,
    "max_follow_up_count": 2,
    "language": "中文",
    "feedback_timing": "面试结束后统一反馈",
}


# ==================================================
# 五、评分维度
# ==================================================

SCORING_RUBRIC = {

    "岗位相关性": {
        "weight": 30,
        "description": "回答是否切中岗位要求和面试问题",
    },

    "逻辑结构": {
        "weight": 20,
        "description": "回答是否有清晰的分析框架和推导过程",
    },

    "事实与证据": {
        "weight": 30,
        "description": "是否提供具体行动、数据、结果和决策依据",
    },

    "表达清晰度": {
        "weight": 20,
        "description": "是否准确、简洁地表达观点",
    },
}


# ==================================================
# 六、配置校验
# ==================================================

def validate_blueprint():

    # 检查岗位配置
    for role, profile in ROLE_PROFILES.items():

        weights = profile["weights"]

        assert sum(weights.values()) == 100, (
            f"{role} 的题型权重之和不等于 100"
        )

        assert all(weight >= 0 for weight in weights.values()), (
            f"{role} 存在负数权重"
        )

        assert set(weights.keys()) == set(QUESTION_TYPE_CONFIG.keys()), (
            f"{role} 的题型与题型配置不一致"
        )

    # 检查面试配置
    assert INTERVIEW_CONFIG["main_question_count"] > 0
    assert INTERVIEW_CONFIG["max_follow_up_count"] >= 0

    # 检查评分权重
    score_weights = [
        item["weight"]
        for item in SCORING_RUBRIC.values()
    ]

    assert sum(score_weights) == 100, (
        "评分维度的权重之和不等于 100"
    )

    print("面试蓝图校验通过！")
    print(f"岗位数量：{len(ROLE_PROFILES)}")
    print(f"候选人阶段：{len(CANDIDATE_LEVELS)}")
    print(f"主问题数量：{INTERVIEW_CONFIG['main_question_count']}")
    print(f"最多追问数量：{INTERVIEW_CONFIG['max_follow_up_count']}")


# ==================================================
# 七、根据岗位和候选人阶段生成面试蓝图
# ==================================================

def get_interview_blueprint(
    role,
    candidate_level="fresh_graduate"
):

    if role not in ROLE_PROFILES:
        raise ValueError(
            f"暂不支持该岗位：{role}"
        )

    if candidate_level not in CANDIDATE_LEVELS:
        raise ValueError(
            f"暂不支持该候选人阶段：{candidate_level}"
        )

    blueprint = {
        "role": role,
        "candidate_level": candidate_level,
        "candidate_profile": deepcopy(
            CANDIDATE_LEVELS[candidate_level]
        ),
        "question_weights": deepcopy(
            ROLE_PROFILES[role]["weights"]
        ),
        "question_type_config": deepcopy(
            QUESTION_TYPE_CONFIG
        ),
        "experience_types": deepcopy(
            EXPERIENCE_TYPES
        ),
        "interview_config": deepcopy(
            INTERVIEW_CONFIG
        ),
        "scoring_rubric": deepcopy(
            SCORING_RUBRIC
        ),
    }

    return blueprint


# ==================================================
# 八、生成主问题安排
# ==================================================

def build_question_plan(blueprint):

    weights = blueprint["question_weights"]
    type_config = blueprint["question_type_config"]

    question_plan = []

    for index, (category, weight) in enumerate(
        weights.items(),
        start=1
    ):

        question_info = type_config[category]

        question_plan.append({

            "question_number": index,

            "question_type": category,

            "priority_weight": weight,

            "main_question_count": 1,

            "objective": question_info["objective"],

            "evidence_types": question_info["evidence_types"],

        })

    return question_plan


# ==================================================
# 九、测试入口
# ==================================================

if __name__ == "__main__":

    validate_blueprint()

    # 测试岗位
    blueprint = get_interview_blueprint(
        role="广告/推荐产品经理"
    )

    print("\n生成的面试蓝图：")

    print(f"目标岗位：{blueprint['role']}")
    print(f"候选人阶段：{blueprint['candidate_profile']['name']}")

    print("\n题型分布：")

    for category, weight in blueprint["question_weights"].items():
        print(f"{category}：{weight}%")

    # 生成题目安排
    question_plan = build_question_plan(blueprint)

    print("\n面试题目安排：")

    for question in question_plan:

        print(
            f"\n第{question['question_number']}题："
            f"{question['question_type']}"
        )

        print(f"考察目标：{question['objective']}")

        print(
            f"可用经历素材："
            f"{'、'.join(question['evidence_types'])}"
        )

        print(
            f"题型权重："
            f"{question['priority_weight']}%"
        )
