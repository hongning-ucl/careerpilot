
from job_matcher import (
    create_matching_result,
    create_match_template,
    validate_matching_result
)

# 创建匹配结果
result = create_matching_result()

# 创建一条测试能力
match = create_match_template()

match.update({
    "dimension": "产品架构能力",
    "capability": "商品信息体系架构设计",
    "importance": "must_have",
    "match_level": "transferable",
    "evidence": [
        {
            "experience_id": "exp_001",
            "experience_name": "短视频广告自动化投放产品",
            "evidence_type": "action",
            "evidence_text": "设计广告计划、广告单元和素材管理流程"
        }
    ],
    "match_reason": "具备复杂产品体系设计经验，但缺少直接的商品信息体系建设证据。",
    "missing_evidence": ["商品信息库建设"],
    "suggested_question": "你如何设计复杂产品的信息架构？"
})

result["capability_matches"].append(match)

result["matching_summary"] = {
    "direct_count": 0,
    "transferable_count": 1,
    "unverified_count": 0
}

# 执行校验
print("校验结果：", validate_matching_result(result))
print("测试通过！")
