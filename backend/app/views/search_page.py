"""搜索页面"""

import streamlit as st
import time
from pathlib import Path

from app.components.search_box import render_search_box, render_search_filters, render_semantic_tags
from app.components.result_card import render_result_list, render_result_stats, render_empty_state
from app.components.concept_tree import render_concept_tree
from app.services.search_engine import SearchEngine
from app.services.document_parser import DocumentScanner
from app.services.semantic_analyzer import get_semantic_suggestions, SemanticAnalyzer
from app.utils.logger import get_logger
from app.utils.validators import validate_search_query

logger = get_logger("search_page")


def render_search_page():
    """渲染搜索页面"""
    
    # 检查并显示待显示的 toast 消息
    if "_toast_msg" in st.session_state:
        msg, icon = st.session_state.pop("_toast_msg")
        st.toast(msg, icon=icon)
    
    st.markdown("""
    <h1 style="color: #F8FAFC; font-size: 28px; font-weight: 600; margin-bottom: 8px;">
        🔍 智能搜索
    </h1>
    <p style="color: #64748B; font-size: 14px; margin-bottom: 24px;">
        在文档库中搜索关键词，支持语义联想和布尔搜索
    </p>
    """, unsafe_allow_html=True)
    
    # 搜索框
    query, search_triggered = render_search_box()
    
    # 搜索过滤器
    filters = render_search_filters()
    
    # 处理搜索（按钮点击、回车键、或自动搜索）
    auto_search = st.session_state.get("auto_search", False)
    
    if query and (search_triggered or auto_search):
        perform_search(query, filters)
    
    # 显示搜索结果
    if "search_results" in st.session_state and st.session_state.search_results:
        results = st.session_state.search_results
        
        # 语义联想标签
        if results.related_terms:
            clicked_tag = render_semantic_tags(results.related_terms)
            if clicked_tag:
                st.session_state.pending_search_query = clicked_tag
                st.session_state.auto_search = True
                st.rerun()
        
        # 按文件名去重，计算实际显示的文档数
        seen_files = set()
        unique_count = 0
        for item in results.items:
            if item.file_name not in seen_files:
                seen_files.add(item.file_name)
                unique_count += 1
        
        # 结果统计（显示去重后的文档数）
        render_result_stats(unique_count, results.query)
        
        # 概念树（可展开，放在结果上方）
        with st.expander("🌳 概念联想树", expanded=False):
            try:
                documents = st.session_state.get("documents", [])
                analyzer = SemanticAnalyzer()
                concept_tree = analyzer.build_concept_tree(results.query, documents, depth=2)
                render_concept_tree(concept_tree)
            except Exception as e:
                logger.warning(f"构建概念树失败: {e}")
                st.info("概念树构建中...")
        
        # 结果列表（不嵌套在列内）
        render_result_list(results.items)
    
    elif not query:
        render_welcome_state()


def perform_search(query: str, filters: dict):
    """执行搜索"""
    # 输入校验
    is_valid, cleaned_query, error_msg = validate_search_query(query)
    if not is_valid:
        st.warning(error_msg or "请输入有效的搜索内容")
        return
    
    with st.spinner("搜索中..."):
        start_time = time.time()
        
        # 获取搜索引擎
        engine = get_search_engine()
        
        # 执行搜索（使用清理后的查询）
        results = engine.search(
            query_str=cleaned_query,
            file_types=filters.get("file_types"),
        )
        
        results.search_time_ms = (time.time() - start_time) * 1000
        
        # 获取语义联想词
        documents = st.session_state.get("documents", [])
        if documents:
            try:
                suggestions = get_semantic_suggestions(cleaned_query, documents, top_k=12)
                results.related_terms = suggestions
            except Exception as e:
                logger.warning(f"语义联想失败: {e}")
        
        # 存储结果
        st.session_state.search_results = results
        st.session_state.auto_search = False


def get_search_engine() -> SearchEngine:
    """获取搜索引擎实例"""
    if "search_engine" not in st.session_state:
        st.session_state.search_engine = SearchEngine()
    return st.session_state.search_engine


def render_welcome_state():
    """渲染欢迎状态"""
    welcome_html = """
<div style="text-align: center; padding: 60px 24px; max-width: 600px; margin: 0 auto;">
    <div style="font-size: 64px; margin-bottom: 24px;">🎯</div>
    <h2 style="color: #F8FAFC; font-size: 24px; font-weight: 600; margin-bottom: 16px;">开始搜索你的辩论素材</h2>
    <p style="color: #94A3B8; font-size: 15px; line-height: 1.8; margin-bottom: 32px;">
        输入关键词搜索文档内容，支持语义联想自动扩展相关概念。<br>
        例如搜索"年轻人"，可以找到关于青年就业、消费、心理健康等相关内容。
    </p>
    <div style="background-color: #1E293B; border-radius: 12px; padding: 20px; text-align: left;">
        <div style="color: #64748B; font-size: 12px; margin-bottom: 12px;">💡 搜索技巧</div>
        <div style="color: #94A3B8; font-size: 14px; line-height: 2;">
            • <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">年轻人 AND 就业</code> - 同时包含两个词<br>
            • <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">青年 OR 年轻人</code> - 包含任意一个词<br>
            • <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">消费 NOT 老年</code> - 排除特定词
        </div>
    </div>
</div>
"""
    st.markdown(welcome_html, unsafe_allow_html=True)
