"""标签数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Tag:
    """标签"""
    id: int
    name: str
    color: str = "#6366F1"  # 默认紫色
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class DocumentTag:
    """文档-标签关联"""
    document_id: str
    tag_id: int
    paragraph_index: Optional[int] = None  # 可选：标记特定段落
    created_at: datetime = field(default_factory=datetime.now)
