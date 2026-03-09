"""搜索结果数据模型"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SearchResultItem:
    """搜索结果项"""
    doc_id: str
    file_path: str
    file_name: str
    file_type: str
    content: str
    highlighted_content: str
    paragraph_index: int = 0
    page_number: int = 0
    score: float = 0.0
    
    # 可选的附加信息
    heading_level: Optional[int] = None
    is_favorite: bool = False
    tags: list[str] = field(default_factory=list)
    
    @property
    def location_str(self) -> str:
        """位置描述字符串"""
        parts = []
        if self.page_number > 0:
            parts.append(f"第 {self.page_number} 页")
        if self.paragraph_index > 0:
            parts.append(f"段落 {self.paragraph_index}")
        return " | ".join(parts) if parts else "文档开头"
    
    @property
    def score_percent(self) -> int:
        """相关度百分比（0-100）"""
        # 简单映射，实际分数范围可能需要调整
        return min(100, int(self.score * 10))
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "doc_id": self.doc_id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "content": self.content,
            "highlighted_content": self.highlighted_content,
            "paragraph_index": self.paragraph_index,
            "page_number": self.page_number,
            "score": self.score,
            "location_str": self.location_str,
            "score_percent": self.score_percent,
        }


@dataclass
class SearchResult:
    """搜索结果集"""
    query: str
    items: list[SearchResultItem] = field(default_factory=list)
    total_count: int = 0
    
    # 搜索元信息
    search_time_ms: float = 0.0
    error: Optional[str] = None
    
    # 同义词扩展
    expanded_query: Optional[str] = None
    expanded_terms: list[str] = field(default_factory=list)
    
    # 语义联想词
    related_terms: list[str] = field(default_factory=list)
    
    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0
    
    @property
    def has_error(self) -> bool:
        return self.error is not None
    
    def get_unique_files(self) -> list[str]:
        """获取去重后的文件列表"""
        seen = set()
        files = []
        for item in self.items:
            if item.file_path not in seen:
                seen.add(item.file_path)
                files.append(item.file_path)
        return files
    
    def group_by_file(self) -> dict[str, list[SearchResultItem]]:
        """按文件分组"""
        groups = {}
        for item in self.items:
            if item.file_path not in groups:
                groups[item.file_path] = []
            groups[item.file_path].append(item)
        return groups
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "query": self.query,
            "items": [item.to_dict() for item in self.items],
            "total_count": self.total_count,
            "search_time_ms": self.search_time_ms,
            "error": self.error,
            "related_terms": self.related_terms,
        }
