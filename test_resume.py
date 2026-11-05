
import json
import io
from pathlib import Path

from resume_reader import extract_resume_text
from resume_analyzer import analyze_resume


# 1. 指定测试 PDF 文件
pdf_path = Path("experieced简历.pdf")


# 2. 检查文件是否存在
if not pdf_path.exists():
    raise FileNotFoundError(f"找不到简历文件：{pdf_path.resolve()}")



# 3. 读取 PDF 并提取文本
pdf_file = io.BytesIO(pdf_path.read_bytes())
pdf_file.name = pdf_path.name

resume_text = extract_resume_text(pdf_file)


print("===== PDF 文本提取结果 =====")
print(resume_text)


# 4. 调用 DeepSeek 进行简历解析
print("\n===== 开始解析简历 =====")

result = analyze_resume(resume_text)


# 5. 输出 JSON 结果
print("\n===== 简历解析结果 =====")
print(json.dumps(result, ensure_ascii=False, indent=4))


# 6. 保存解析结果，方便后续检查
output_path = Path("resume_result.json")

with output_path.open("w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=4)

print(f"\n解析结果已保存至：{output_path.resolve()}")
