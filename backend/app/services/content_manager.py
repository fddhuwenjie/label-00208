"""内容管理服务 - SQLite 数据库操作"""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

import jieba
import jieba.analyse

from app.config import DB_PATH
from app.models.tag import Tag, DocumentTag
from app.models.favorite import Favorite
from app.models.argument import Argument, Evidence, ArgumentSide


class ContentManager:
    """内容管理器"""
    
    def __init__(self, db_path: str = None):
        self.db_path = Path(db_path or DB_PATH)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """初始化数据库表"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 标签表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    color TEXT DEFAULT '#6366F1',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 文档-标签关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS document_tags (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    tag_id INTEGER NOT NULL,
                    paragraph_index INTEGER,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE,
                    UNIQUE(document_id, tag_id, paragraph_index)
                )
            """)
            
            # 收藏表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    document_id TEXT NOT NULL,
                    file_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    paragraph_index INTEGER DEFAULT 0,
                    page_number INTEGER DEFAULT 0,
                    note TEXT,
                    folder TEXT DEFAULT '默认',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 论点表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS arguments (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    side TEXT DEFAULT 'neutral',
                    strength INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # 论据表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS evidences (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    argument_id INTEGER NOT NULL,
                    content TEXT NOT NULL,
                    source_document_id TEXT,
                    source_file_name TEXT,
                    source_location TEXT,
                    note TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (argument_id) REFERENCES arguments(id) ON DELETE CASCADE
                )
            """)
            
            # 论点-标签关联表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS argument_tags (
                    argument_id INTEGER NOT NULL,
                    tag_id INTEGER NOT NULL,
                    PRIMARY KEY (argument_id, tag_id),
                    FOREIGN KEY (argument_id) REFERENCES arguments(id) ON DELETE CASCADE,
                    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
                )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_document_tags_doc ON document_tags(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_favorites_doc ON favorites(document_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_evidences_arg ON evidences(argument_id)")
    
    # ========== 标签管理 ==========
    
    def create_tag(self, name: str, color: str = "#6366F1") -> Optional[Tag]:
        """创建标签"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO tags (name, color) VALUES (?, ?)",
                    (name, color)
                )
                tag_id = cursor.lastrowid
                return Tag(id=tag_id, name=name, color=color)
            except sqlite3.IntegrityError:
                return None
    
    def get_all_tags(self) -> list[Tag]:
        """获取所有标签"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM tags ORDER BY name")
            rows = cursor.fetchall()
            return [
                Tag(
                    id=row["id"],
                    name=row["name"],
                    color=row["color"],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
                )
                for row in rows
            ]
    
    def delete_tag(self, tag_id: int) -> bool:
        """删除标签"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tags WHERE id = ?", (tag_id,))
            return cursor.rowcount > 0
    
    def add_tag_to_document(
        self,
        document_id: str,
        tag_id: int,
        paragraph_index: int = None
    ) -> bool:
        """为文档添加标签"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO document_tags (document_id, tag_id, paragraph_index) VALUES (?, ?, ?)",
                    (document_id, tag_id, paragraph_index)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def get_document_tags(self, document_id: str) -> list[Tag]:
        """获取文档的标签"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* FROM tags t
                JOIN document_tags dt ON t.id = dt.tag_id
                WHERE dt.document_id = ?
            """, (document_id,))
            rows = cursor.fetchall()
            return [
                Tag(id=row["id"], name=row["name"], color=row["color"])
                for row in rows
            ]
    
    def suggest_tags_for_content(
        self,
        content: str,
        max_suggestions: int = 5
    ) -> list[tuple[Tag, float]]:
        """
        根据内容自动推荐标签
        
        Args:
            content: 文本内容
            max_suggestions: 最大推荐数量
            
        Returns:
            [(Tag, 匹配度), ...] 按匹配度降序排列
        """
        if not content or len(content) < 10:
            return []
        
        # 获取所有标签
        all_tags = self.get_all_tags()
        if not all_tags:
            return []
        
        # 使用 jieba 提取内容关键词
        keywords = jieba.analyse.extract_tags(content, topK=30, withWeight=True)
        keyword_dict = {kw: weight for kw, weight in keywords}
        
        # 定义标签关键词映射（扩展标签的匹配范围）
        tag_keywords_map = {
            "经济": ["经济", "GDP", "增长", "发展", "收入", "就业", "消费", "投资", "贸易", "金融", "财政", "税收"],
            "社会": ["社会", "公共", "公民", "群体", "阶层", "城市", "农村", "社区", "民生"],
            "教育": ["教育", "学校", "学生", "教师", "课程", "学习", "培训", "高考", "大学", "毕业"],
            "科技": ["科技", "技术", "创新", "人工智能", "AI", "互联网", "数字", "自动化", "智能"],
            "环境": ["环境", "生态", "污染", "碳排放", "气候", "绿色", "新能源", "可持续"],
            "政策": ["政策", "法律", "法规", "政府", "监管", "制度", "改革", "规划"],
            "医疗": ["医疗", "健康", "医院", "疾病", "治疗", "药品", "卫生"],
            "人口": ["人口", "生育", "老龄化", "养老", "人口结构", "劳动力"],
        }
        
        suggestions = []
        
        for tag in all_tags:
            tag_name = tag.name
            score = 0.0
            
            # 直接匹配标签名
            if tag_name in keyword_dict:
                score += keyword_dict[tag_name] * 2.0
            
            # 匹配标签关键词
            tag_kws = tag_keywords_map.get(tag_name, [tag_name])
            for kw in tag_kws:
                if kw in keyword_dict:
                    score += keyword_dict[kw]
                # 模糊匹配：关键词包含标签词或标签词包含关键词
                for content_kw in keyword_dict:
                    if kw in content_kw or content_kw in kw:
                        score += keyword_dict[content_kw] * 0.5
            
            if score > 0:
                suggestions.append((tag, score))
        
        # 按匹配度排序
        suggestions.sort(key=lambda x: x[1], reverse=True)
        
        return suggestions[:max_suggestions]
    
    def auto_tag_content(
        self,
        document_id: str,
        content: str,
        threshold: float = 0.5,
        paragraph_index: int = None
    ) -> list[Tag]:
        """
        自动为内容添加标签
        
        Args:
            document_id: 文档ID
            content: 文本内容
            threshold: 匹配度阈值
            paragraph_index: 段落索引
            
        Returns:
            成功添加的标签列表
        """
        suggestions = self.suggest_tags_for_content(content)
        
        added_tags = []
        for tag, score in suggestions:
            if score >= threshold:
                success = self.add_tag_to_document(document_id, tag.id, paragraph_index)
                if success:
                    added_tags.append(tag)
        
        return added_tags
    
    def get_tag_statistics(self) -> list[dict]:
        """获取标签使用统计"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.id, t.name, t.color, COUNT(dt.id) as usage_count
                FROM tags t
                LEFT JOIN document_tags dt ON t.id = dt.tag_id
                GROUP BY t.id
                ORDER BY usage_count DESC
            """)
            rows = cursor.fetchall()
            return [
                {
                    "id": row["id"],
                    "name": row["name"],
                    "color": row["color"],
                    "usage_count": row["usage_count"]
                }
                for row in rows
            ]
    
    # ========== 收藏管理 ==========
    
    def add_favorite(
        self,
        document_id: str,
        file_name: str,
        content: str,
        paragraph_index: int = 0,
        page_number: int = 0,
        note: str = None,
        folder: str = "默认"
    ) -> Optional[Favorite]:
        """添加收藏（防止重复）"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 检查是否已存在相同的收藏（基于文档ID、段落索引和内容）
            cursor.execute("""
                SELECT id FROM favorites 
                WHERE document_id = ? AND paragraph_index = ? AND content = ?
            """, (document_id, paragraph_index, content))
            
            existing = cursor.fetchone()
            if existing:
                # 已存在，返回 None 表示未添加
                return None
            
            cursor.execute("""
                INSERT INTO favorites 
                (document_id, file_name, content, paragraph_index, page_number, note, folder)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (document_id, file_name, content, paragraph_index, page_number, note, folder))
            
            fav_id = cursor.lastrowid
            return Favorite(
                id=fav_id,
                document_id=document_id,
                file_name=file_name,
                content=content,
                paragraph_index=paragraph_index,
                page_number=page_number,
                note=note,
                folder=folder
            )
    
    def get_all_favorites(self, folder: str = None) -> list[Favorite]:
        """获取所有收藏"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if folder:
                cursor.execute(
                    "SELECT * FROM favorites WHERE folder = ? ORDER BY created_at DESC",
                    (folder,)
                )
            else:
                cursor.execute("SELECT * FROM favorites ORDER BY created_at DESC")
            
            rows = cursor.fetchall()
            return [
                Favorite(
                    id=row["id"],
                    document_id=row["document_id"],
                    file_name=row["file_name"],
                    content=row["content"],
                    paragraph_index=row["paragraph_index"],
                    page_number=row["page_number"],
                    note=row["note"],
                    folder=row["folder"],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None
                )
                for row in rows
            ]
    
    def update_favorite_note(self, favorite_id: int, note: str) -> bool:
        """更新收藏笔记"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE favorites SET note = ? WHERE id = ?",
                (note, favorite_id)
            )
            return cursor.rowcount > 0
    
    def delete_favorite(self, favorite_id: int) -> bool:
        """删除收藏"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM favorites WHERE id = ?", (favorite_id,))
            return cursor.rowcount > 0
    
    def get_favorite_folders(self) -> list[str]:
        """获取所有收藏夹"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT folder FROM favorites ORDER BY folder")
            return [row["folder"] for row in cursor.fetchall()]
    
    def remove_duplicate_favorites(self) -> int:
        """删除重复的收藏，保留每组重复中最早的一条"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # 找出重复记录中需要删除的ID（保留最小ID即最早的记录）
            cursor.execute("""
                DELETE FROM favorites 
                WHERE id NOT IN (
                    SELECT MIN(id) 
                    FROM favorites 
                    GROUP BY document_id, paragraph_index, content
                )
            """)
            deleted_count = cursor.rowcount
            return deleted_count
    
    # ========== 论点管理 ==========
    
    def create_argument(
        self,
        title: str,
        description: str = None,
        side: ArgumentSide = ArgumentSide.NEUTRAL
    ) -> Argument:
        """创建论点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO arguments (title, description, side)
                VALUES (?, ?, ?)
            """, (title, description, side.value))
            
            arg_id = cursor.lastrowid
            return Argument(
                id=arg_id,
                title=title,
                description=description,
                side=side
            )
    
    def get_all_arguments(self, side: ArgumentSide = None) -> list[Argument]:
        """获取所有论点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            if side:
                cursor.execute(
                    "SELECT * FROM arguments WHERE side = ? ORDER BY created_at DESC",
                    (side.value,)
                )
            else:
                cursor.execute("SELECT * FROM arguments ORDER BY created_at DESC")
            
            rows = cursor.fetchall()
            arguments = []
            
            for row in rows:
                arg = Argument(
                    id=row["id"],
                    title=row["title"],
                    description=row["description"],
                    side=ArgumentSide(row["side"]),
                    strength=row["strength"],
                    created_at=datetime.fromisoformat(row["created_at"]) if row["created_at"] else None,
                    updated_at=datetime.fromisoformat(row["updated_at"]) if row["updated_at"] else None
                )
                
                # 获取论据
                cursor.execute(
                    "SELECT * FROM evidences WHERE argument_id = ? ORDER BY created_at",
                    (arg.id,)
                )
                evidence_rows = cursor.fetchall()
                arg.evidences = [
                    Evidence(
                        id=e["id"],
                        argument_id=e["argument_id"],
                        content=e["content"],
                        source_document_id=e["source_document_id"],
                        source_file_name=e["source_file_name"],
                        source_location=e["source_location"],
                        note=e["note"],
                        created_at=datetime.fromisoformat(e["created_at"]) if e["created_at"] else None
                    )
                    for e in evidence_rows
                ]
                
                arguments.append(arg)
            
            return arguments
    
    def update_argument(
        self,
        argument_id: int,
        title: str = None,
        description: str = None,
        side: ArgumentSide = None
    ) -> bool:
        """更新论点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            updates = []
            values = []
            
            if title:
                updates.append("title = ?")
                values.append(title)
            if description is not None:
                updates.append("description = ?")
                values.append(description)
            if side:
                updates.append("side = ?")
                values.append(side.value)
            
            if not updates:
                return False
            
            updates.append("updated_at = ?")
            values.append(datetime.now().isoformat())
            values.append(argument_id)
            
            cursor.execute(
                f"UPDATE arguments SET {', '.join(updates)} WHERE id = ?",
                values
            )
            return cursor.rowcount > 0
    
    def delete_argument(self, argument_id: int) -> bool:
        """删除论点"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM arguments WHERE id = ?", (argument_id,))
            return cursor.rowcount > 0
    
    def add_evidence(
        self,
        argument_id: int,
        content: str,
        source_document_id: str = None,
        source_file_name: str = None,
        source_location: str = None,
        note: str = None
    ) -> Optional[Evidence]:
        """添加论据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO evidences 
                (argument_id, content, source_document_id, source_file_name, source_location, note)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (argument_id, content, source_document_id, source_file_name, source_location, note))
            
            evidence_id = cursor.lastrowid
            
            # 更新论点强度
            cursor.execute(
                "UPDATE arguments SET strength = strength + 1, updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), argument_id)
            )
            
            return Evidence(
                id=evidence_id,
                argument_id=argument_id,
                content=content,
                source_document_id=source_document_id,
                source_file_name=source_file_name,
                source_location=source_location,
                note=note
            )
    
    def delete_evidence(self, evidence_id: int) -> bool:
        """删除论据"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 获取论点 ID
            cursor.execute("SELECT argument_id FROM evidences WHERE id = ?", (evidence_id,))
            row = cursor.fetchone()
            if not row:
                return False
            
            argument_id = row["argument_id"]
            
            # 删除论据
            cursor.execute("DELETE FROM evidences WHERE id = ?", (evidence_id,))
            
            # 更新论点强度
            cursor.execute(
                "UPDATE arguments SET strength = MAX(0, strength - 1), updated_at = ? WHERE id = ?",
                (datetime.now().isoformat(), argument_id)
            )
            
            return True
    
    # ========== 导出功能 ==========
    
    def export_to_markdown(
        self,
        include_favorites: bool = True,
        include_arguments: bool = True,
        include_tags: bool = True
    ) -> str:
        """导出为 Markdown 格式"""
        # 格式化当前时间，确保格式正确
        now = datetime.now()
        export_time = f"{now.year:04d}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"
        lines = ["# DebatePrep 导出", "", f"*导出时间: {export_time}*", ""]
        
        if include_favorites:
            favorites = self.get_all_favorites()
            if favorites:
                lines.append("## 收藏夹")
                lines.append("")
                
                # 按文件夹分组
                folders = {}
                for fav in favorites:
                    if fav.folder not in folders:
                        folders[fav.folder] = []
                    folders[fav.folder].append(fav)
                
                for folder, items in folders.items():
                    lines.append(f"### {folder}")
                    lines.append("")
                    
                    for fav in items:
                        lines.append(f"#### {fav.file_name}")
                        lines.append(f"> {fav.content}")
                        if fav.note:
                            lines.append(f"")
                            lines.append(f"*笔记: {fav.note}*")
                        lines.append("")
        
        if include_arguments:
            arguments = self.get_all_arguments()
            if arguments:
                lines.append("## 论点整理")
                lines.append("")
                
                # 按立场分组
                pro_args = [a for a in arguments if a.side == ArgumentSide.PRO]
                con_args = [a for a in arguments if a.side == ArgumentSide.CON]
                neutral_args = [a for a in arguments if a.side == ArgumentSide.NEUTRAL]
                
                if pro_args:
                    lines.append("### 正方论点")
                    lines.append("")
                    for arg in pro_args:
                        self._export_argument(arg, lines)
                
                if con_args:
                    lines.append("### 反方论点")
                    lines.append("")
                    for arg in con_args:
                        self._export_argument(arg, lines)
                
                if neutral_args:
                    lines.append("### 中立观点")
                    lines.append("")
                    for arg in neutral_args:
                        self._export_argument(arg, lines)
        
        return "\n".join(lines)
    
    def _export_argument(self, arg: Argument, lines: list):
        """导出单个论点"""
        lines.append(f"#### {arg.title}")
        if arg.description:
            lines.append(f"{arg.description}")
        lines.append("")
        
        if arg.evidences:
            lines.append("**论据:**")
            for i, ev in enumerate(arg.evidences, 1):
                lines.append(f"{i}. {ev.content}")
                if ev.source_file_name:
                    lines.append(f"   *来源: {ev.source_file_name}*")
            lines.append("")
