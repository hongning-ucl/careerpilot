
import json

from resume_reader import extract_resume_text
from resume_analyzer import analyze_resume
from job_matcher import extract_experience_evidence

from pathlib import Path
import io


# 1. 读取 PDF
pdf_path = Path("experieced简历.pdf")

pdf_file = io.BytesIO(pdf_path.read_bytes())
pdf_file.name = pdf_path.name

resume_text = extract_resume_text(pdf_file)


# 2. 解析简历
resume_data = analyze_resume(resume_text)


# 3. 提取经历证据
evidence_list = extract_experience_evidence(resume_data)


# 4. 输出结果
print("===== 经历证据提取结果 =====")

print(
    json.dumps(
        evidence_list,
        ensure_ascii=False,
        indent=4
    )
)

print("\n证据总数：", len(evidence_list))
