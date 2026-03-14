"""设置页面"""

import streamlit as st
from app.services.search_engine import SearchEngine
from app.services.semantic_analyzer import is_using_fallback_mode
from app.config import (
    INDEX_DIR, DATA_DIR, 
    SIMILARITY_THRESHOLD, MAX_RESULTS, CONTEXT_SENTENCES,
    DISABLE_DEMO_DATA, DISABLE_SEMANTIC_MODEL
)


def render_settings_page():
    """渲染设置页面"""
    st.markdown("""
    <h1 style="color: #F8FAFC; font-size: 28px; font-weight: 600; margin-bottom: 8px;">
        ⚙️ 设置
    </h1>
    <p style="color: #64748B; font-size: 14px; margin-bottom: 24px;">
        管理应用配置和数据
    </p>
    """, unsafe_allow_html=True)
    
    # 搜索参数配置
    render_search_settings()
    
    st.markdown("<hr style='border-color: #334155; margin: 32px 0;'>", unsafe_allow_html=True)
    
    # 索引管理
    st.markdown("""
    <div style="color: #F8FAFC; font-size: 18px; font-weight: 600; margin-bottom: 16px;">
        📚 索引管理
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        engine = SearchEngine()
        doc_count = engine.get_document_count()
        
        st.markdown(f"""
        <div style="
            background-color: #1E293B;
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="color: #64748B; font-size: 14px; margin-bottom: 8px;">索引状态</div>
            <div style="color: #F8FAFC; font-size: 24px; font-weight: 700; font-family: 'JetBrains Mono', monospace;">
                {doc_count}
            </div>
            <div style="color: #64748B; font-size: 12px;">索引项</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div style="
            background-color: #1E293B;
            border-radius: 12px;
            padding: 20px;
        ">
            <div style="color: #64748B; font-size: 14px; margin-bottom: 8px;">索引目录</div>
            <div style="color: #94A3B8; font-size: 12px; word-break: break-all;">
                {INDEX_DIR}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
    
    # 使用两列布局，按钮撑满宽度
    btn_col1, btn_col2 = st.columns(2)
    
    with btn_col1:
        if st.button("🔄 重建索引", type="primary", use_container_width=True):
            if "documents" in st.session_state and st.session_state.documents:
                with st.spinner("正在重建索引..."):
                    engine.rebuild_index(st.session_state.documents)
                st.success("索引重建完成")
            else:
                st.warning("请先扫描文档目录")
    
    with btn_col2:
        if st.button("🗑️ 清空索引", type="secondary", use_container_width=True):
            if st.session_state.get("confirm_clear_index", False):
                engine.clear_index()
                st.session_state.doc_count = 0
                st.session_state.index_count = 0
                st.session_state.confirm_clear_index = False
                st.success("索引已清空")
            else:
                st.session_state.confirm_clear_index = True
                st.warning("再次点击确认清空索引")
    
    st.markdown("<hr style='border-color: #334155; margin: 32px 0;'>", unsafe_allow_html=True)
    
    # 关于
    st.markdown("""
    <div style="color: #F8FAFC; font-size: 18px; font-weight: 600; margin-bottom: 16px;">
        ℹ️ 关于
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="
        background-color: #1E293B;
        border-radius: 12px;
        padding: 20px;
    ">
        <div style="color: #F8FAFC; font-size: 16px; font-weight: 600; margin-bottom: 12px;">
            🎯 DebatePrep - 辩论赛智能备赛助手
        </div>
        <div style="color: #94A3B8; font-size: 14px; line-height: 1.8;">
            本地文档智能分析工具，专为辩论赛备赛设计。<br><br>
            <strong>功能特性：</strong><br>
            • 支持 Word、Excel、PDF、TXT 格式文档<br>
            • 关键词精确搜索和布尔搜索<br>
            • 语义联想自动扩展相关概念<br>
            • 标签管理和收藏功能<br>
            • 论点管理和正反方归类<br>
            • Markdown 格式导出
        </div>
        <div style="color: #64748B; font-size: 12px; margin-top: 16px;">
            版本: 2.0.0 | 技术栈: Python + Streamlit + Whoosh + Sentence-Transformers
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_search_settings():
    """渲染搜索参数配置"""
    st.markdown("""
    <div style="color: #F8FAFC; font-size: 18px; font-weight: 600; margin-bottom: 16px;">
        🔧 搜索参数配置
    </div>
    """, unsafe_allow_html=True)
    
    # 当前配置状态
    semantic_mode = "TF-IDF 降级模式" if is_using_fallback_mode() else "深度语义模式"
    semantic_color = "#F59E0B" if is_using_fallback_mode() else "#22C55E"
    
    st.markdown(f"""
    <div style="
        background-color: #1E293B;
        border-radius: 12px;
        padding: 16px 20px;
        margin-bottom: 16px;
    ">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="color: #64748B; font-size: 12px; margin-bottom: 4px;">当前语义分析模式</div>
                <div style="color: {semantic_color}; font-size: 14px; font-weight: 600;">{semantic_mode}</div>
            </div>
            <div>
                <div style="color: #64748B; font-size: 12px; margin-bottom: 4px;">演示数据</div>
                <div style="color: {'#EF4444' if DISABLE_DEMO_DATA else '#22C55E'}; font-size: 14px; font-weight: 600;">
                    {'已禁用' if DISABLE_DEMO_DATA else '已启用'}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # 相似度阈值
        new_threshold = st.slider(
            "语义相似度阈值",
            min_value=0.1,
            max_value=0.9,
            value=st.session_state.get("similarity_threshold", SIMILARITY_THRESHOLD),
            step=0.05,
            help="值越低，匹配结果越多但相关性可能降低；值越高，结果更精确但可能遗漏相关内容"
        )
        st.session_state["similarity_threshold"] = new_threshold
    
    with col2:
        # 最大结果数
        new_max_results = st.slider(
            "最大搜索结果数",
            min_value=10,
            max_value=200,
            value=st.session_state.get("max_results", MAX_RESULTS),
            step=10,
            help="每次搜索返回的最大结果数量"
        )
        st.session_state["max_results"] = new_max_results
    
    with col3:
        # 上下文句子数
        new_context = st.slider(
            "上下文句子数",
            min_value=1,
            max_value=10,
            value=st.session_state.get("context_sentences", CONTEXT_SENTENCES),
            step=1,
            help="搜索结果中显示的上下文句子数量"
        )
        st.session_state["context_sentences"] = new_context
    
    st.markdown("""
    <div style="
        background-color: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 12px 16px;
        margin-top: 12px;
    ">
        <div style="color: #818CF8; font-size: 12px; font-weight: 600; margin-bottom: 6px;">💡 提示</div>
        <div style="color: #94A3B8; font-size: 12px; line-height: 1.6;">
            以上参数调整将立即生效并应用于当前会话。<br>
            如需永久修改默认值，请设置相应的环境变量：<br>
            <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">SIMILARITY_THRESHOLD</code>、
            <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">MAX_RESULTS</code>、
            <code style="background: #334155; padding: 2px 6px; border-radius: 4px;">CONTEXT_SENTENCES</code>
        </div>
    </div>
    """, unsafe_allow_html=True)
