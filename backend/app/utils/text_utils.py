"""文本处理工具函数"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """清理文本：去除多余空白、特殊字符"""
    if not text:
        return ""
    
    # 替换多个空白字符为单个空格
    text = re.sub(r"\s+", " ", text)
    # 去除首尾空白
    text = text.strip()
    return text


def normalize_whitespace(text: str) -> str:
    """标准化空白字符"""
    # 保留段落结构，但标准化行内空白
    lines = text.split("\n")
    normalized = []
    for line in lines:
        line = re.sub(r"[ \t]+", " ", line).strip()
        if line:
            normalized.append(line)
    return "\n".join(normalized)


def extract_sentences(text: str) -> list[str]:
    """提取句子列表"""
    # 中文和英文句子分割
    pattern = r"[。！？\.!?]+"
    sentences = re.split(pattern, text)
    return [s.strip() for s in sentences if s.strip()]


def get_context_around(
    text: str,
    keyword: str,
    context_chars: int = 100,
    context_sentences: int = 2
) -> list[dict]:
    """
    获取关键词周围的上下文
    
    Args:
        text: 全文
        keyword: 关键词
        context_chars: 上下文字符数
        context_sentences: 上下文句子数
    
    Returns:
        包含上下文信息的列表
    """
    results = []
    keyword_lower = keyword.lower()
    text_lower = text.lower()
    
    # 查找所有匹配位置
    start = 0
    while True:
        pos = text_lower.find(keyword_lower, start)
        if pos == -1:
            break
        
        # 计算上下文范围
        context_start = max(0, pos - context_chars)
        context_end = min(len(text), pos + len(keyword) + context_chars)
        
        # 获取上下文
        context = text[context_start:context_end]
        
        # 添加省略号
        prefix = "..." if context_start > 0 else ""
        suffix = "..." if context_end < len(text) else ""
        
        results.append({
            "position": pos,
            "context": prefix + context + suffix,
            "keyword": text[pos:pos + len(keyword)]  # 保留原始大小写
        })
        
        start = pos + 1
    
    return results


def highlight_keyword(text: str, keyword: str, tag: str = "mark") -> str:
    """高亮关键词"""
    if not keyword:
        return text
    
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    return pattern.sub(f"<{tag}>\\g<0></{tag}>", text)


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """截断文本"""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def count_words(text: str) -> int:
    """统计词数（中英文混合）"""
    # 简单统计：中文按字符，英文按空格分词
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    english_words = len(re.findall(r"[a-zA-Z]+", text))
    return chinese_chars + english_words


def is_chinese(text: str) -> bool:
    """判断是否主要是中文"""
    chinese_chars = len(re.findall(r"[\u4e00-\u9fff]", text))
    total_chars = len(re.findall(r"\w", text))
    if total_chars == 0:
        return False
    return chinese_chars / total_chars > 0.5


def split_into_paragraphs(text: str, min_length: int = 10) -> list[str]:
    """将文本分割为段落"""
    paragraphs = re.split(r"\n\s*\n|\n{2,}", text)
    return [p.strip() for p in paragraphs if len(p.strip()) >= min_length]
