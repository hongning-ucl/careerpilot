
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com",
)

job_title = "AI 产品经理"

job_description = """
负责 AI 产品规划、需求分析、大模型应用落地，
与算法、研发和业务团队协作，推动产品效果持续优化。
"""

experience = """
有多年互联网产品经理经验，负责过广告自动化投放产品，
具备机器学习和深度学习系统实践经历。
"""

prompt = f"""
你是一名资深 AI 产品经理面试官。

请根据以下信息，生成恰好 5 道面试问题。

目标岗位：
{job_title}

岗位 JD：
{job_description}

候选人经历：
{experience}

要求：
1. 问题必须与目标岗位相关。
2. 至少 2 道题需要结合候选人的实际经历。
3. 问题应覆盖业务分析、产品设计、AI 技术应用和项目复盘。
4. 只输出 5 道问题，每道问题单独一行。
5. 不要输出开场白、答案或额外解释。
"""

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "user", "content": prompt}
    ],
    max_tokens=800,
)

print(response.choices[0].message.content)
