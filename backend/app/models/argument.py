"""论点数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class ArgumentSide(Enum):
    """立场"""
    PRO = "pro"  # 正方
    CON = "con"  # 反方
    NEUTRAL = "neutral"  # 中立


@dataclass
class Evidence:
    """论据"""
    id: int
    argument_id: int
    content: str
    source_document_id: Optional[str] = None
    source_file_name: Optional[str] = None
    source_location: Optional[str] = None  # 页码/段落位置
    
    note: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "argument_id": self.argument_id,
            "content": self.content,
            "source_document_id": self.source_document_id,
            "source_file_name": self.source_file_name,
            "source_location": self.source_location,
            "note": self.note,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class Argument:
    """论点"""
    id: int
    title: str
    description: Optional[str] = None
    side: ArgumentSide = ArgumentSide.NEUTRAL
    
    evidences: list[Evidence] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    
    strength: int = 0  # 论点强度（基于论据数量和质量）
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    
    @property
    def side_label(self) -> str:
        """立场标签"""
        labels = {
            ArgumentSide.PRO: "正方",
            ArgumentSide.CON: "反方",
            ArgumentSide.NEUTRAL: "中立",
        }
        return labels.get(self.side, "未知")
    
    @property
    def side_color(self) -> str:
        """立场颜色"""
        colors = {
            ArgumentSide.PRO: "#14B8A6",  # 青色
            ArgumentSide.CON: "#F59E0B",  # 琥珀色
            ArgumentSide.NEUTRAL: "#A855F7",  # 紫色
        }
        return colors.get(self.side, "#64748B")
    
    @property
    def evidence_count(self) -> int:
        return len(self.evidences)
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "side": self.side.value,
            "side_label": self.side_label,
            "evidences": [e.to_dict() for e in self.evidences],
            "tags": self.tags,
            "strength": self.strength,
            "evidence_count": self.evidence_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
