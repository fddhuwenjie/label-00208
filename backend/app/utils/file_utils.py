"""文件操作工具函数"""

import os
import hashlib
from pathlib import Path
from typing import Generator

SUPPORTED_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".txt"}


def get_file_hash(file_path: str) -> str:
    """计算文件 MD5 哈希值"""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def get_file_id(file_path: str) -> str:
    """生成文件唯一 ID（基于路径哈希）"""
    return hashlib.md5(file_path.encode()).hexdigest()[:16]


def get_file_size(file_path: str) -> int:
    """获取文件大小（字节）"""
    return os.path.getsize(file_path)


def is_supported_file(file_path: str) -> bool:
    """检查文件是否支持"""
    ext = Path(file_path).suffix.lower()
    return ext in SUPPORTED_EXTENSIONS


def scan_directory(
    directory: str,
    recursive: bool = True,
    extensions: set[str] | None = None
) -> Generator[str, None, None]:
    """
    扫描目录获取所有支持的文件
    
    Args:
        directory: 目录路径
        recursive: 是否递归扫描子目录
        extensions: 要扫描的扩展名集合，None 表示使用默认支持的扩展名
    
    Yields:
        文件路径
    """
    if extensions is None:
        extensions = SUPPORTED_EXTENSIONS
    
    directory = Path(directory)
    
    if not directory.exists():
        return
    
    if recursive:
        for file_path in directory.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                yield str(file_path)
    else:
        for file_path in directory.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in extensions:
                yield str(file_path)


def get_relative_path(file_path: str, base_dir: str) -> str:
    """获取相对路径"""
    try:
        return str(Path(file_path).relative_to(base_dir))
    except ValueError:
        return file_path


def ensure_directory(directory: str) -> None:
    """确保目录存在"""
    Path(directory).mkdir(parents=True, exist_ok=True)


def format_file_size(size_bytes: int) -> str:
    """格式化文件大小显示"""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
