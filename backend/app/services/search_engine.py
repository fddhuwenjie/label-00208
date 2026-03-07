"""搜索引擎服务 - 基于 Whoosh"""

import os
import re
from pathlib import Path
from datetime import datetime
from typing import Optional

from whoosh import index
from whoosh.fields import Schema, TEXT, ID, STORED, NUMERIC, DATETIME
from whoosh.analysis import Tokenizer, Token
from whoosh.qparser import QueryParser, OrGroup, AndGroup
from whoosh.query import And, Or, Not, Term, FuzzyTerm
from whoosh.highlight import Highlighter, HtmlFormatter
from whoosh import highlight

import jieba

from app.models.document import Document
from app.models.search_result import SearchResult, SearchResultItem
from app.config import INDEX_DIR, CONTEXT_SENTENCES, MAX_RESULTS
from app.utils.synonym_dict import get_synonym_dict
from app.utils.logger import search_logger as logger


class JiebaTokenizer(Tokenizer):
    """基于 jieba 的中文分词器"""
    
    def __call__(self, value, positions=True, chars=True, keeporiginal=True,
                 removestops=True, start_pos=0, start_char=0, tokenize=True,
                 mode='', **kwargs):
        
        if not tokenize:
            yield Token(text=value, pos=start_pos, startchar=start_char, 
                       endchar=start_char + len(value))
            return
        
        pos = start_pos
        char_pos = start_char
        
        # 使用 jieba 分词
        for word in jieba.cut_for_search(value):
            word = word.strip()
            if not word:
                continue
            
            # 查找词在原文中的位置
            word_start = value.find(word, char_pos - start_char)
            if word_start >= 0:
                word_start += start_char
            else:
                word_start = char_pos
            
            word_end = word_start + len(word)
            
            t = Token(
                text=word,
                pos=pos,
                startchar=word_start,
                endchar=word_end,
            )
            
            yield t
            pos += 1
            char_pos = word_end


def create_jieba_analyzer():
    """创建 jieba 分析器"""
    return JiebaTokenizer()


class SearchEngine:
    """搜索引擎"""
    
    def __init__(self, index_dir: str = None):
        self.index_dir = Path(index_dir or INDEX_DIR)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        self.schema = Schema(
            doc_id=ID(stored=True, unique=True),
            file_path=STORED(),
            file_name=TEXT(stored=True, analyzer=create_jieba_analyzer()),
            file_type=ID(stored=True),
            content=TEXT(stored=True, analyzer=create_jieba_analyzer()),
            paragraph_index=NUMERIC(stored=True),
            page_number=NUMERIC(stored=True),
            heading_level=NUMERIC(stored=True),
            indexed_at=DATETIME(stored=True),
        )
        
        self._index = None
    
    @property
    def ix(self) -> index.Index:
        """获取或创建索引"""
        if self._index is None:
            if index.exists_in(str(self.index_dir)):
                self._index = index.open_dir(str(self.index_dir))
            else:
                self._index = index.create_in(str(self.index_dir), self.schema)
        return self._index
    
    def index_document(self, doc: Document) -> bool:
        """
        索引单个文档
        
        Args:
            doc: 文档对象
            
        Returns:
            是否成功
        """
        try:
            writer = self.ix.writer()
            
            # 删除旧索引
            writer.delete_by_term("doc_id", doc.id)
            
            indexed_at = datetime.now()
            
            # 如果有段落，分段索引
            if doc.paragraphs:
                for para in doc.paragraphs:
                    writer.add_document(
                        doc_id=f"{doc.id}_{para.paragraph_index}",
                        file_path=doc.file_path,
                        file_name=doc.file_name,
                        file_type=doc.file_type,
                        content=para.content,
                        paragraph_index=para.paragraph_index,
                        page_number=para.page_number or 0,
                        heading_level=para.heading_level or 0,
                        indexed_at=indexed_at,
                    )
            else:
                # 整体索引
                writer.add_document(
                    doc_id=doc.id,
                    file_path=doc.file_path,
                    file_name=doc.file_name,
                    file_type=doc.file_type,
                    content=doc.full_text,
                    paragraph_index=0,
                    page_number=0,
                    heading_level=0,
                    indexed_at=indexed_at,
                )
            
            writer.commit()
            return True
            
        except Exception as e:
            logger.error(f"索引文档失败 {doc.file_name}: {e}")
            return False
    
    def index_documents(
        self,
        documents: list[Document],
        progress_callback: callable = None
    ) -> int:
        """
        批量索引文档
        
        Args:
            documents: 文档列表
            progress_callback: 进度回调
            
        Returns:
            成功索引的文档数
        """
        success_count = 0
        total = len(documents)
        
        writer = self.ix.writer()
        indexed_at = datetime.now()
        
        try:
            for idx, doc in enumerate(documents):
                if progress_callback:
                    progress_callback(idx + 1, total, doc.file_name)
                
                # 删除旧索引
                writer.delete_by_term("doc_id", doc.id)
                
                if doc.paragraphs:
                    for para in doc.paragraphs:
                        writer.add_document(
                            doc_id=f"{doc.id}_{para.paragraph_index}",
                            file_path=doc.file_path,
                            file_name=doc.file_name,
                            file_type=doc.file_type,
                            content=para.content,
                            paragraph_index=para.paragraph_index,
                            page_number=para.page_number or 0,
                            heading_level=para.heading_level or 0,
                            indexed_at=indexed_at,
                        )
                else:
                    writer.add_document(
                        doc_id=doc.id,
                        file_path=doc.file_path,
                        file_name=doc.file_name,
                        file_type=doc.file_type,
                        content=doc.full_text,
                        paragraph_index=0,
                        page_number=0,
                        heading_level=0,
                        indexed_at=indexed_at,
                    )
                
                success_count += 1
            
            writer.commit()
            
        except Exception as e:
            logger.error(f"批量索引失败: {e}")
            writer.cancel()
        
        return success_count
    
    def search(
        self,
        query_str: str,
        max_results: int = None,
        file_types: list[str] = None,
        expand_synonyms: bool = False,
    ) -> SearchResult:
        """
        搜索文档
        
        Args:
            query_str: 搜索查询
            max_results: 最大结果数
            file_types: 限制文件类型
            expand_synonyms: 是否启用同义词扩展
            
        Returns:
            SearchResult 对象
        """
        if max_results is None:
            max_results = MAX_RESULTS
        
        # 同义词扩展
        original_query = query_str
        expanded_terms = []
        if expand_synonyms:
            synonym_dict = get_synonym_dict()
            query_str = synonym_dict.expand_query(query_str)
            expanded_terms = synonym_dict.get_all_synonyms_for_query(original_query)
        
        results = SearchResult(query=original_query)
        results.expanded_query = query_str if expand_synonyms else None
        results.expanded_terms = expanded_terms if expand_synonyms else []
        
        if not query_str.strip():
            return results
        
        try:
            with self.ix.searcher() as searcher:
                # 解析查询
                query = self._parse_query(query_str)
                
                # 添加文件类型过滤
                if file_types:
                    type_query = Or([Term("file_type", t) for t in file_types])
                    query = And([query, type_query])
                
                # 执行搜索
                search_results = searcher.search(query, limit=max_results)
                
                # 配置高亮
                search_results.formatter = HtmlFormatter(tagname="mark")
                search_results.fragmenter = highlight.ContextFragmenter(
                    maxchars=300, surround=50
                )
                
                results.total_count = len(search_results)
                
                for hit in search_results:
                    # 获取高亮片段
                    highlighted = hit.highlights("content", top=3)
                    if not highlighted:
                        # 如果没有高亮，取前200字符
                        content = hit.get("content", "")
                        highlighted = content[:200] + "..." if len(content) > 200 else content
                    
                    item = SearchResultItem(
                        doc_id=hit["doc_id"],
                        file_path=hit["file_path"],
                        file_name=hit["file_name"],
                        file_type=hit["file_type"],
                        content=hit.get("content", ""),
                        highlighted_content=highlighted,
                        paragraph_index=hit.get("paragraph_index", 0),
                        page_number=hit.get("page_number", 0),
                        score=hit.score,
                    )
                    results.items.append(item)
        
        except Exception as e:
            logger.error(f"搜索失败: {e}")
            results.error = str(e)
        
        return results
    
    def _parse_query(self, query_str: str):
        """解析查询字符串，支持布尔操作"""
        # 检测布尔操作符
        has_bool = any(op in query_str.upper() for op in [" AND ", " OR ", " NOT "])
        
        if has_bool:
            # 使用 AND 作为默认组
            parser = QueryParser("content", self.ix.schema, group=AndGroup)
        else:
            # 使用 OR 作为默认组（更宽松的匹配）
            parser = QueryParser("content", self.ix.schema, group=OrGroup)
        
        # 允许通配符和模糊搜索
        parser.add_plugin(whoosh.qparser.FuzzyTermPlugin())
        
        return parser.parse(query_str)
    
    def search_boolean(
        self,
        must_include: list[str] = None,
        should_include: list[str] = None,
        must_exclude: list[str] = None,
        max_results: int = None,
    ) -> SearchResult:
        """
        布尔搜索
        
        Args:
            must_include: 必须包含的词 (AND)
            should_include: 可选包含的词 (OR)
            must_exclude: 必须排除的词 (NOT)
            max_results: 最大结果数
            
        Returns:
            SearchResult 对象
        """
        query_parts = []
        
        if must_include:
            query_parts.extend(must_include)
        
        if should_include:
            query_parts.append(f"({' OR '.join(should_include)})")
        
        query_str = " AND ".join(query_parts)
        
        if must_exclude:
            for exc in must_exclude:
                query_str += f" NOT {exc}"
        
        return self.search(query_str, max_results=max_results)
    
    def get_document_count(self) -> int:
        """获取索引文档数"""
        try:
            with self.ix.searcher() as searcher:
                return searcher.doc_count()
        except Exception:
            return 0
    
    def clear_index(self) -> bool:
        """清空索引"""
        try:
            # 重新创建索引
            self._index = index.create_in(str(self.index_dir), self.schema)
            return True
        except Exception as e:
            logger.error(f"清空索引失败: {e}")
            return False
    
    def rebuild_index(
        self,
        documents: list[Document],
        progress_callback: callable = None
    ) -> int:
        """重建索引"""
        self.clear_index()
        return self.index_documents(documents, progress_callback)


# 导入 whoosh.qparser 模块
import whoosh.qparser
