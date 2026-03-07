"""导出页面"""

import streamlit as st
from datetime import datetime
from app.services.content_manager import ContentManager


def render_export_page():
    """渲染导出页面"""
    
    inject_export_styles()
    
    st.markdown("""
    <div class="export-header">
        <h1 class="export-title">📤 导出</h1>
        <p class="export-subtitle">导出收藏和论点为 Markdown 格式</p>
    </div>
    """, unsafe_allow_html=True)
    
    manager = get_content_manager()
    
    fav_count = len(manager.get_all_favorites())
    arg_count = len(manager.get_all_arguments())
    tag_count = len(manager.get_all_tags())
    
    # 导出选项 - 使用原生 checkbox 但美化布局
    st.markdown('<div class="section-label">选择导出内容</div>', unsafe_allow_html=True)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        include_favorites = st.checkbox(f"⭐ 收藏夹 ({fav_count})", value=True, key="export_favorites")
    with c2:
        include_arguments = st.checkbox(f"📑 论点整理 ({arg_count})", value=True, key="export_arguments")
    with c3:
        include_tags = st.checkbox(f"🏷️ 标签信息 ({tag_count})", value=False, key="export_tags")
    
    st.markdown('<div class="export-divider"></div>', unsafe_allow_html=True)
    
    # 操作按钮 - 紧凑居中
    st.markdown('<div class="btn-group">', unsafe_allow_html=True)
    b1, b2, b3 = st.columns([1, 1, 1])
    with b1:
        preview_clicked = st.button("🔍 预览", use_container_width=True)
    with b2:
        export_clicked = st.button("📥 导出", type="primary", use_container_width=True)
    with b3:
        copy_clicked = st.button("📋 复制", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # 预览
    if preview_clicked:
        st.session_state.export_preview = manager.export_to_markdown(
            include_favorites=include_favorites,
            include_arguments=include_arguments,
            include_tags=include_tags
        )
    
    if st.session_state.get("export_preview"):
        st.markdown('<div class="section-label">预览内容</div>', unsafe_allow_html=True)
        st.code(st.session_state.export_preview, language="markdown")
    
    # 导出
    if export_clicked:
        md_content = manager.export_to_markdown(
            include_favorites=include_favorites,
            include_arguments=include_arguments,
            include_tags=include_tags
        )
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        st.download_button(
            label="⬇️ 点击下载",
            data=md_content,
            file_name=f"export_{timestamp}.md",
            mime="text/markdown",
            use_container_width=True
        )
    
    # 复制
    if copy_clicked:
        md_content = manager.export_to_markdown(
            include_favorites=include_favorites,
            include_arguments=include_arguments,
            include_tags=include_tags
        )
        st.session_state.show_copy_area = True
        st.session_state.copy_content = md_content
        st.rerun()
    
    # 显示可复制的文本区域
    if st.session_state.get("show_copy_area", False):
        copy_content = st.session_state.get("copy_content", "")
        st.markdown('<div class="section-label">📋 复制内容（Ctrl+A 全选，Ctrl+C 复制）</div>', unsafe_allow_html=True)
        st.text_area(
            "复制内容",
            value=copy_content,
            height=300,
            key="copy_textarea",
            label_visibility="collapsed"
        )
        st.info("请点击文本框，按 Ctrl+A 全选，然后 Ctrl+C 复制")
        if st.button("关闭", key="close_copy_area"):
            st.session_state.show_copy_area = False
            st.rerun()
    
    # 提示
    st.markdown("""
    <div class="export-tips">
        <strong>💡 提示</strong><br>
        导出的 Markdown 可在 Typora、Obsidian、VS Code 中打开
    </div>
    """, unsafe_allow_html=True)


def inject_export_styles():
    st.markdown("""
    <style>
    .export-header { margin-bottom: 24px; }
    .export-title { font-size: 28px; font-weight: 600; color: #F8FAFC; margin: 0 0 8px 0; }
    .export-subtitle { font-size: 14px; color: #64748B; margin: 0; }
    
    .section-label {
        color: #94A3B8;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .export-divider {
        height: 1px;
        background: #334155;
        margin: 24px 0;
    }
    
    .btn-group {
        max-width: 500px;
        margin: 0 auto 24px auto;
    }
    
    .export-tips {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 16px;
        margin-top: 24px;
        color: #94A3B8;
        font-size: 13px;
        line-height: 1.6;
    }
    </style>
    """, unsafe_allow_html=True)


def get_content_manager() -> ContentManager:
    if "content_manager" not in st.session_state:
        st.session_state.content_manager = ContentManager()
    return st.session_state.content_manager
