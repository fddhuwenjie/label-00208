"""
输入校验模块

提供统一的输入验证功能，确保数据安全性和有效性。
"""

import re
import os
from pathlib import Path
from typing import Optional, Tuple

from app.utils.logger import get_logger

logger = get_logger("validators")


# ========== 常量定义 ==========

# 搜索相关限制
MAX_SEARCH_QUERY_LENGTH = 500
MIN_SEARCH_QUERY_LENGTH = 1

# 文件路径相关
ALLOWED_EXTENSIONS = {".docx", ".doc", ".pdf", ".xlsx", ".xls", ".txt"}
MAX_FILE_NAME_LENGTH = 255
MAX_PATH_LENGTH = 4096

# 文本内容相关
MAX_TAG_NAME_LENGTH = 50
MAX_ARGUMENT_TITLE_LENGTH = 200
MAX_NOTE_LENGTH = 5000


# ========== 搜索输入校验 ==========

def validate_search_query(query: str) -> Tuple[bool, str, str]:
    """
    校验搜索查询输入
    
    Args:
        query: 用户输入的搜索查询
        
    Returns:
        (是否有效, 清理后的查询, 错误信息)
    """
    if query is None:
        return False, "", "搜索内容不能为空"
    
    # 清理输入：去除首尾空白
    cleaned = query.strip()
    
    # 长度校验
    if len(cleaned) < MIN_SEARCH_QUERY_LENGTH:
        return False, "", "搜索内容不能为空"
    
    if len(cleaned) > MAX_SEARCH_QUERY_LENGTH:
        logger.warning(f"搜索查询过长: {len(cleaned)} 字符，截断至 {MAX_SEARCH_QUERY_LENGTH}")
        cleaned = cleaned[:MAX_SEARCH_QUERY_LENGTH]
    
    # 危险字符过滤（防止注入）
    dangerous_patterns = [
        r"[<>]",  # HTML 标签
        r"javascript:",  # JS 注入
        r"data:",  # Data URI
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, cleaned, re.IGNORECASE):
            logger.warning(f"搜索查询包含危险字符: {pattern}")
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
    
    return True, cleaned, ""


def sanitize_search_query(query: str) -> str:
    """
    清理搜索查询（简化版，直接返回清理后的字符串）
    
    Args:
        query: 原始查询
        
    Returns:
        清理后的查询
    """
    valid, cleaned, _ = validate_search_query(query)
    return cleaned if valid else ""


# ========== 文件路径校验 ==========

def validate_file_path(file_path: str) -> Tuple[bool, str, str]:
    """
    校验文件路径的合法性和安全性
    
    Args:
        file_path: 文件路径字符串
        
    Returns:
        (是否有效, 规范化路径, 错误信息)
    """
    if not file_path:
        return False, "", "文件路径不能为空"
    
    # 长度校验
    if len(file_path) > MAX_PATH_LENGTH:
        return False, "", f"文件路径过长（最大 {MAX_PATH_LENGTH} 字符）"
    
    try:
        path = Path(file_path)
    except Exception as e:
        logger.error(f"无效的文件路径格式: {file_path}, 错误: {e}")
        return False, "", "无效的文件路径格式"
    
    # 文件名长度校验
    if len(path.name) > MAX_FILE_NAME_LENGTH:
        return False, "", f"文件名过长（最大 {MAX_FILE_NAME_LENGTH} 字符）"
    
    # 路径遍历攻击检测
    if ".." in str(path):
        logger.warning(f"检测到路径遍历尝试: {file_path}")
        return False, "", "文件路径不允许包含 '..'"
    
    # 危险字符检测
    dangerous_chars = ["<", ">", "|", "\x00", "\n", "\r"]
    for char in dangerous_chars:
        if char in file_path:
            logger.warning(f"文件路径包含危险字符: {repr(char)}")
            return False, "", "文件路径包含非法字符"
    
    # 规范化路径
    try:
        normalized = str(path.resolve()) if path.exists() else str(path)
    except Exception:
        normalized = str(path)
    
    return True, normalized, ""


def validate_file_extension(file_path: str) -> Tuple[bool, str]:
    """
    校验文件扩展名是否在允许列表中
    
    Args:
        file_path: 文件路径
        
    Returns:
        (是否允许, 扩展名)
    """
    ext = Path(file_path).suffix.lower()
    
    if ext not in ALLOWED_EXTENSIONS:
        logger.warning(f"不支持的文件类型: {ext}")
        return False, ext
    
    return True, ext


def is_safe_path(base_dir: str, file_path: str) -> bool:
    """
    检查文件路径是否在指定目录内（防止目录遍历）
    
    Args:
        base_dir: 基础目录
        file_path: 待检查的文件路径
        
    Returns:
        是否安全
    """
    try:
        base = Path(base_dir).resolve()
        target = Path(file_path).resolve()
        
        return str(target).startswith(str(base))
    except Exception as e:
        logger.error(f"路径安全检查失败: {e}")
        return False


# ========== 文本内容校验 ==========

def validate_tag_name(name: str) -> Tuple[bool, str, str]:
    """
    校验标签名称
    
    Args:
        name: 标签名称
        
    Returns:
        (是否有效, 清理后的名称, 错误信息)
    """
    if not name:
        return False, "", "标签名称不能为空"
    
    cleaned = name.strip()
    
    if len(cleaned) > MAX_TAG_NAME_LENGTH:
        return False, "", f"标签名称过长（最大 {MAX_TAG_NAME_LENGTH} 字符）"
    
    if len(cleaned) < 1:
        return False, "", "标签名称不能为空"
    
    # 移除特殊字符
    cleaned = re.sub(r"[<>\"'`]", "", cleaned)
    
    return True, cleaned, ""


def validate_argument_title(title: str) -> Tuple[bool, str, str]:
    """
    校验论点标题
    
    Args:
        title: 论点标题
        
    Returns:
        (是否有效, 清理后的标题, 错误信息)
    """
    if not title:
        return False, "", "论点标题不能为空"
    
    cleaned = title.strip()
    
    if len(cleaned) > MAX_ARGUMENT_TITLE_LENGTH:
        return False, "", f"论点标题过长（最大 {MAX_ARGUMENT_TITLE_LENGTH} 字符）"
    
    if len(cleaned) < 2:
        return False, "", "论点标题至少需要 2 个字符"
    
    return True, cleaned, ""


def validate_note(note: str) -> Tuple[bool, str, str]:
    """
    校验笔记内容
    
    Args:
        note: 笔记内容
        
    Returns:
        (是否有效, 清理后的内容, 错误信息)
    """
    if note is None:
        return True, "", ""
    
    cleaned = note.strip()
    
    if len(cleaned) > MAX_NOTE_LENGTH:
        logger.warning(f"笔记内容过长: {len(cleaned)} 字符，截断至 {MAX_NOTE_LENGTH}")
        cleaned = cleaned[:MAX_NOTE_LENGTH]
    
    return True, cleaned, ""
