"""搜索引擎单元测试"""

import pytest
import tempfile
import shutil
from pathlib import Path

from app.services.search_engine import SearchEngine
from app.models.document import Document, DocumentParagraph


class TestSearchEngine:
    """搜索引擎测试类"""
    
    @pytest.fixture
    def temp_index_dir(self):
        """创建临时索引目录"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def search_engine(self, temp_index_dir):
        """创建搜索引擎实例"""
        return SearchEngine(index_dir=temp_index_dir)
    
    @pytest.fixture
    def sample_documents(self):
        """创建示例文档"""
        return [
            Document(
                id="doc_001",
                file_path="/test/doc1.pdf",
                file_name="人工智能研究报告.pdf",
                file_type="pdf",
                file_size=1024,
                paragraphs=[
                    DocumentParagraph(
                        content="人工智能技术正在快速发展，深度学习和机器学习是其核心技术。",
                        paragraph_index=0,
                        page_number=1
                    ),
                    DocumentParagraph(
                        content="AI在医疗、金融、教育等领域的应用日益广泛。",
                        paragraph_index=1,
                        page_number=1
                    ),
                ],
                full_text="人工智能技术正在快速发展。AI应用日益广泛。"
            ),
            Document(
                id="doc_002",
                file_path="/test/doc2.docx",
                file_name="经济发展分析.docx",
                file_type="docx",
                file_size=2048,
                paragraphs=[
                    DocumentParagraph(
                        content="中国经济持续增长，就业市场保持稳定。",
                        paragraph_index=0,
                        page_number=1
                    ),
                ],
                full_text="中国经济持续增长，就业市场保持稳定。"
            ),
        ]
    
    def test_index_document(self, search_engine, sample_documents):
        """测试单文档索引"""
        doc = sample_documents[0]
        result = search_engine.index_document(doc)
        
        assert result is True
        assert search_engine.get_document_count() > 0
    
    def test_index_documents_batch(self, search_engine, sample_documents):
        """测试批量索引"""
        count = search_engine.index_documents(sample_documents)
        
        assert count == len(sample_documents)
        assert search_engine.get_document_count() > 0
    
    def test_search_basic(self, search_engine, sample_documents):
        """测试基本搜索"""
        search_engine.index_documents(sample_documents)
        
        results = search_engine.search("人工智能")
        
        assert results.total_count > 0
        assert len(results.items) > 0
        assert "人工智能" in results.items[0].file_name or "人工智能" in results.items[0].content
    
    def test_search_no_results(self, search_engine, sample_documents):
        """测试无结果搜索"""
        search_engine.index_documents(sample_documents)
        
        results = search_engine.search("完全不存在的关键词xyz123")
        
        assert results.total_count == 0
        assert results.is_empty is True
    
    def test_search_with_synonyms(self, search_engine, sample_documents):
        """测试同义词扩展搜索"""
        search_engine.index_documents(sample_documents)
        
        # 搜索 "AI" 应该能匹配到包含 "人工智能" 的文档
        results = search_engine.search("AI", expand_synonyms=True)
        
        assert results.expanded_query is not None
        assert len(results.expanded_terms) > 0
    
    def test_search_by_file_type(self, search_engine, sample_documents):
        """测试按文件类型过滤"""
        search_engine.index_documents(sample_documents)
        
        results = search_engine.search("发展", file_types=["pdf"])
        
        for item in results.items:
            assert item.file_type == "pdf"
    
    def test_clear_index(self, search_engine, sample_documents):
        """测试清空索引"""
        search_engine.index_documents(sample_documents)
        assert search_engine.get_document_count() > 0
        
        search_engine.clear_index()
        assert search_engine.get_document_count() == 0
    
    def test_rebuild_index(self, search_engine, sample_documents):
        """测试重建索引"""
        search_engine.index_documents(sample_documents)
        initial_count = search_engine.get_document_count()
        
        count = search_engine.rebuild_index(sample_documents[:1])
        
        assert count == 1
        assert search_engine.get_document_count() < initial_count


class TestSearchResult:
    """搜索结果测试类"""
    
    def test_search_result_properties(self, ):
        """测试搜索结果属性"""
        from app.models.search_result import SearchResult, SearchResultItem
        
        result = SearchResult(query="测试查询")
        
        assert result.is_empty is True
        assert result.has_error is False
        
        result.items.append(SearchResultItem(
            doc_id="1",
            file_path="/test.pdf",
            file_name="test.pdf",
            file_type="pdf",
            content="测试内容",
            highlighted_content="<mark>测试</mark>内容",
            score=5.0
        ))
        result.total_count = 1
        
        assert result.is_empty is False
        assert result.items[0].score_percent == 50
