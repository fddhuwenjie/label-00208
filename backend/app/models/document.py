"""文档数据模型"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from pathlib import Path


@dataclass
class DocumentParagraph:
    """文档段落"""
    content: str
    paragraph_index: int
    heading_level: Optional[int] = None  # None 表示正文，1-6 表示标题级别
    page_number: Optional[int] = None
    
    @property
    def is_heading(self) -> bool:
        return self.heading_level is not None


@dataclass
class Document:
    """文档实体"""
    id: str
    file_path: str
    file_name: str
    file_type: str  # docx, xlsx, pdf, txt
    file_size: int  # bytes
    
    paragraphs: list[DocumentParagraph] = field(default_factory=list)
    full_text: str = ""
    
    created_at: datetime = field(default_factory=datetime.now)
    modified_at: Optional[datetime] = None
    indexed_at: Optional[datetime] = None
    
    # 元数据
    title: Optional[str] = None
    author: Optional[str] = None
    page_count: Optional[int] = None
    
    @property
    def extension(self) -> str:
        return Path(self.file_path).suffix.lower()
    
    @property
    def paragraph_count(self) -> int:
        return len(self.paragraphs)
    
    def get_text_preview(self, max_length: int = 200) -> str:
        """获取文本预览"""
        if len(self.full_text) <= max_length:
            return self.full_text
        return self.full_text[:max_length] + "..."
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type,
            "file_size": self.file_size,
            "full_text": self.full_text,
            "paragraph_count": self.paragraph_count,
            "title": self.title,
            "author": self.author,
            "page_count": self.page_count,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "indexed_at": self.indexed_at.isoformat() if self.indexed_at else None,
        }


@dataclass
class ExcelSheet:
    """Excel 工作表"""
    name: str
    rows: list[list[str]]
    
    def to_text(self) -> str:
        """转换为文本"""
        lines = []
        for row in self.rows:
            line = " | ".join(str(cell) for cell in row if cell)
            if line.strip():
                lines.append(line)
        return "\n".join(lines)


@dataclass
class ExcelDocument(Document):
    """Excel 文档"""
    sheets: list[ExcelSheet] = field(default_factory=list)
    
    def get_all_text(self) -> str:
        """获取所有工作表文本"""
        texts = []
        for sheet in self.sheets:
            texts.append(f"[工作表: {sheet.name}]")
            texts.append(sheet.to_text())
        return "\n\n".join(texts)
