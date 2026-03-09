"""收藏数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Favorite:
    """收藏项"""
    id: int
    document_id: str
    file_name: str
    content: str  # 收藏的内容片段
    paragraph_index: int = 0
    page_number: int = 0
    
    note: Optional[str] = None  # 用户笔记
    folder: str = "默认"  # 收藏夹分组
    
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "document_id": self.document_id,
            "file_name": self.file_name,
            "content": self.content,
            "paragraph_index": self.paragraph_index,
            "page_number": self.page_number,
            "note": self.note,
            "folder": self.folder,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    @property
    def preview(self) -> str:
        """内容预览"""
        if len(self.content) <= 100:
            return self.content
        return self.content[:100] + "..."
