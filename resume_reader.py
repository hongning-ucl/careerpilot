
# resume_reader.py
# CareerPilot：简历文件读取模块

from docx import Document
from pypdf import PdfReader
from pathlib import Path


def read_docx(file):
    """读取 Word 文件，提取段落和表格文本。"""

    doc = Document(file)
    content = []

    # 读取普通段落
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()

        if text:
            content.append(text)

    # 读取表格
    for table in doc.tables:
        for row in table.rows:
            row_text = [
                cell.text.strip()
                for cell in row.cells
                if cell.text.strip()
            ]

            if row_text:
                content.append(" | ".join(row_text))

    return "\n".join(content)


def read_pdf(file):
    """读取 PDF 文件，逐页提取文本。"""

    reader = PdfReader(file)
    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        if text.strip():
            pages.append(
                f"【第 {page_number} 页】\n{text.strip()}"
            )

    return "\n\n".join(pages)


def extract_resume_text(file):
    """根据文件扩展名自动选择读取方法。"""

    filename = file.name.lower()
    suffix = Path(filename).suffix

    if suffix == ".docx":
        return read_docx(file)

    elif suffix == ".pdf":
        return read_pdf(file)

    else:
        raise ValueError(
            "暂不支持该文件格式，请上传 DOCX 或 PDF。"
        )


# 入口

if __name__ == "__main__":

    import os

    filename = "应届生广告产品经理示例简历.pdf"

    if not os.path.exists(filename):
        print(f"找不到文件：{filename}")

    else:
        with open(filename, "rb") as file:
            resume_text = extract_resume_text(file)

        print("简历读取成功！")
        print("=" * 50)
        print(resume_text)
        print("=" * 50)
        print(f"提取字符数：{len(resume_text)}")
