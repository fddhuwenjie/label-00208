"""内容管理器单元测试"""

import pytest
import tempfile
import os
from pathlib import Path

from app.services.content_manager import ContentManager
from app.models.argument import ArgumentSide


class TestContentManager:
    """内容管理器测试类"""
    
    @pytest.fixture
    def temp_db_path(self):
        """创建临时数据库文件"""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        yield path
        os.unlink(path)
    
    @pytest.fixture
    def content_manager(self, temp_db_path):
        """创建内容管理器实例"""
        return ContentManager(db_path=temp_db_path)
    
    # ========== 标签测试 ==========
    
    def test_create_tag(self, content_manager):
        """测试创建标签"""
        tag = content_manager.create_tag("经济", "#3B82F6")
        
        assert tag is not None
        assert tag.name == "经济"
        assert tag.color == "#3B82F6"
    
    def test_create_duplicate_tag(self, content_manager):
        """测试创建重复标签"""
        content_manager.create_tag("科技", "#8B5CF6")
        duplicate = content_manager.create_tag("科技", "#FF0000")
        
        assert duplicate is None
    
    def test_get_all_tags(self, content_manager):
        """测试获取所有标签"""
        content_manager.create_tag("经济", "#3B82F6")
        content_manager.create_tag("科技", "#8B5CF6")
        
        tags = content_manager.get_all_tags()
        
        assert len(tags) == 2
        names = [t.name for t in tags]
        assert "经济" in names
        assert "科技" in names
    
    def test_delete_tag(self, content_manager):
        """测试删除标签"""
        tag = content_manager.create_tag("临时标签", "#000000")
        
        result = content_manager.delete_tag(tag.id)
        
        assert result is True
        tags = content_manager.get_all_tags()
        assert len(tags) == 0
    
    def test_add_tag_to_document(self, content_manager):
        """测试为文档添加标签"""
        tag = content_manager.create_tag("经济", "#3B82F6")
        
        result = content_manager.add_tag_to_document("doc_001", tag.id)
        
        assert result is True
        
        doc_tags = content_manager.get_document_tags("doc_001")
        assert len(doc_tags) == 1
        assert doc_tags[0].name == "经济"
    
    def test_suggest_tags_for_content(self, content_manager):
        """测试自动标签推荐"""
        content_manager.create_tag("经济", "#3B82F6")
        content_manager.create_tag("科技", "#8B5CF6")
        content_manager.create_tag("环境", "#10B981")
        
        content = "人工智能技术正在推动经济增长，数字化转型成为企业核心战略。"
        suggestions = content_manager.suggest_tags_for_content(content)
        
        assert len(suggestions) > 0
        tag_names = [tag.name for tag, score in suggestions]
        assert "科技" in tag_names or "经济" in tag_names
    
    # ========== 收藏测试 ==========
    
    def test_add_favorite(self, content_manager):
        """测试添加收藏"""
        fav = content_manager.add_favorite(
            document_id="doc_001",
            file_name="测试文档.pdf",
            content="这是一段重要的内容",
            folder="测试收藏夹"
        )
        
        assert fav is not None
        assert fav.file_name == "测试文档.pdf"
        assert fav.folder == "测试收藏夹"
    
    def test_add_duplicate_favorite(self, content_manager):
        """测试添加重复收藏"""
        content_manager.add_favorite(
            document_id="doc_001",
            file_name="测试文档.pdf",
            content="相同内容"
        )
        duplicate = content_manager.add_favorite(
            document_id="doc_001",
            file_name="测试文档.pdf",
            content="相同内容"
        )
        
        assert duplicate is None
    
    def test_get_all_favorites(self, content_manager):
        """测试获取所有收藏"""
        content_manager.add_favorite("doc_001", "文档1.pdf", "内容1")
        content_manager.add_favorite("doc_002", "文档2.pdf", "内容2")
        
        favorites = content_manager.get_all_favorites()
        
        assert len(favorites) == 2
    
    def test_delete_favorite(self, content_manager):
        """测试删除收藏"""
        fav = content_manager.add_favorite("doc_001", "文档.pdf", "内容")
        
        result = content_manager.delete_favorite(fav.id)
        
        assert result is True
        favorites = content_manager.get_all_favorites()
        assert len(favorites) == 0
    
    # ========== 论点测试 ==========
    
    def test_create_argument(self, content_manager):
        """测试创建论点"""
        arg = content_manager.create_argument(
            title="人工智能促进就业",
            description="技术进步创造新岗位",
            side=ArgumentSide.PRO
        )
        
        assert arg is not None
        assert arg.title == "人工智能促进就业"
        assert arg.side == ArgumentSide.PRO
    
    def test_get_arguments_by_side(self, content_manager):
        """测试按立场获取论点"""
        content_manager.create_argument("正方论点1", side=ArgumentSide.PRO)
        content_manager.create_argument("反方论点1", side=ArgumentSide.CON)
        content_manager.create_argument("正方论点2", side=ArgumentSide.PRO)
        
        pro_args = content_manager.get_all_arguments(side=ArgumentSide.PRO)
        con_args = content_manager.get_all_arguments(side=ArgumentSide.CON)
        
        assert len(pro_args) == 2
        assert len(con_args) == 1
    
    def test_add_evidence(self, content_manager):
        """测试添加论据"""
        arg = content_manager.create_argument("测试论点", side=ArgumentSide.PRO)
        
        evidence = content_manager.add_evidence(
            argument_id=arg.id,
            content="根据研究数据显示...",
            source_file_name="研究报告.pdf"
        )
        
        assert evidence is not None
        assert evidence.content == "根据研究数据显示..."
        
        # 验证论点强度增加
        args = content_manager.get_all_arguments()
        updated_arg = next(a for a in args if a.id == arg.id)
        assert updated_arg.strength == 1
    
    def test_delete_argument(self, content_manager):
        """测试删除论点"""
        arg = content_manager.create_argument("临时论点", side=ArgumentSide.NEUTRAL)
        
        result = content_manager.delete_argument(arg.id)
        
        assert result is True
        args = content_manager.get_all_arguments()
        assert len(args) == 0
    
    # ========== 导出测试 ==========
    
    def test_export_to_markdown(self, content_manager):
        """测试导出 Markdown"""
        content_manager.add_favorite("doc_001", "文档.pdf", "重要内容")
        arg = content_manager.create_argument("测试论点", side=ArgumentSide.PRO)
        content_manager.add_evidence(arg.id, "论据内容", "来源.pdf")
        
        markdown = content_manager.export_to_markdown()
        
        assert "# DebatePrep 导出" in markdown
        assert "收藏夹" in markdown
        assert "论点整理" in markdown
        assert "重要内容" in markdown
        assert "测试论点" in markdown
