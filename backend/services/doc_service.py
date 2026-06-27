import PyPDF2
import io

def extract_text(file_content:bytes,filename:str)->str:
    
    """
    从文件内容中提取文本。
    支持 PDF、txt、md 格式。

    """
    if filename.lower().endswith('.pdf'):
        return extract_pdf(file_content)
    elif filename.endswith(('.txt', '.md')):
        return file_content.decode('utf-8')
    else:
        raise "不支持的文件格式"
    
def extract_pdf(file_content: bytes) -> str:
    """从 PDF 中提取文本"""
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_content))
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        return f"PDF解析失败: {str(e)}"