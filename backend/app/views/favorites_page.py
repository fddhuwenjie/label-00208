"""收藏夹页面"""

import streamlit as st
from app.services.content_manager import ContentManager


def render_favorites_page():
    """渲染收藏夹页面"""
    
    # 注入专用样式
    inject_favorites_styles()
    
    st.markdown("""
    <div class="favorites-header">
        <h1 class="favorites-title">⭐ 收藏夹</h1>
        <p class="favorites-subtitle">管理你收藏的重要论据片段</p>
    </div>
    """, unsafe_allow_html=True)
    
    manager = get_content_manager()
    
    # 收藏夹选择
    folders = manager.get_favorite_folders()
    if not folders:
        folders = ["默认"]
    
    # 顶部操作栏
    col1, col2, col3 = st.columns([4, 1, 1])
    
    with col1:
        selected_folder = st.selectbox(
            "收藏夹",
            options=["全部"] + folders,
            key="favorite_folder_select",
            label_visibility="collapsed"
        )
    
    with col2:
        if st.button("🧹 去重", help="删除重复的收藏"):
            deleted = manager.remove_duplicate_favorites()
            if deleted > 0:
                st.toast(f"已删除 {deleted} 条重复收藏", icon="✅")
                st.rerun()
            else:
                st.toast("没有重复的收藏", icon="ℹ️")
    
    with col3:
        if st.button("📤 导出", type="primary"):
            export_favorites(manager)
    
    # 分隔线
    st.markdown('<div class="favorites-divider"></div>', unsafe_allow_html=True)
    
    # 获取收藏
    if selected_folder == "全部":
        favorites = manager.get_all_favorites()
    else:
        favorites = manager.get_all_favorites(folder=selected_folder)
    
    if not favorites:
        render_empty_favorites()
        return
    
    # 显示收藏列表
    for idx, fav in enumerate(favorites):
        render_favorite_card(fav, manager, idx)


def render_favorite_card(fav, manager, idx: int):
    """渲染收藏卡片"""
    
    # 卡片头部信息（纯展示）
    content_preview = fav.content[:300] + '...' if len(fav.content) > 300 else fav.content
    
    st.markdown(f"""
    <div class="fav-card">
        <div class="fav-card-header">
            <div class="fav-card-info">
                <div class="fav-card-title">📄 {fav.file_name}</div>
                <div class="fav-card-meta">{fav.folder} · 第 {fav.page_number} 页</div>
            </div>
            <div class="fav-card-badge">⭐ 已收藏</div>
        </div>
        <div class="fav-card-content">{content_preview}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # 笔记和操作区域：整合在一起
    note_col, action_col = st.columns([10, 1])
    
    with note_col:
        note = st.text_input(
            "笔记",
            value=fav.note or "",
            key=f"fav_note_{fav.id}",
            placeholder="笔记内容",
            label_visibility="collapsed"
        )
    
    with action_col:
        # 根据笔记是否修改显示不同按钮
        note_changed = note != (fav.note or "")
        if note_changed:
            if st.button("💾", key=f"save_note_{fav.id}", help="保存笔记", use_container_width=True):
                manager.update_favorite_note(fav.id, note)
                st.toast("笔记已保存", icon="✅")
                st.rerun()
        else:
            if st.button("🗑️", key=f"del_fav_{fav.id}", help="取消收藏", use_container_width=True):
                manager.delete_favorite(fav.id)
                st.toast("已取消收藏", icon="🗑️")
                st.rerun()
    
    # 卡片间距
    st.markdown('<div class="fav-card-spacer"></div>', unsafe_allow_html=True)


def inject_favorites_styles():
    """注入收藏夹页面专用样式"""
    st.markdown("""
    <style>
    /* 页面头部 */
    .favorites-header {
        margin-bottom: 24px;
    }
    .favorites-title {
        font-size: 28px;
        font-weight: 600;
        color: #F8FAFC;
        margin: 0 0 8px 0;
        letter-spacing: -0.3px;
    }
    .favorites-subtitle {
        font-size: 14px;
        color: #64748B;
        margin: 0;
    }
    
    /* 分隔线 */
    .favorites-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #334155, transparent);
        margin: 20px 0 24px 0;
    }
    
    /* 收藏卡片 */
    .fav-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 8px;
        transition: all 0.2s ease;
    }
    .fav-card:hover {
        border-color: #FBBF24;
        box-shadow: 0 4px 20px rgba(251, 191, 36, 0.08);
    }
    
    /* 卡片头部 */
    .fav-card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 16px;
        gap: 12px;
    }
    .fav-card-info {
        flex: 1;
        min-width: 0;
    }
    .fav-card-title {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 15px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .fav-card-meta {
        color: #64748B;
        font-size: 12px;
        margin-top: 4px;
    }
    .fav-card-badge {
        background: rgba(251, 191, 36, 0.12);
        color: #FBBF24;
        padding: 6px 12px;
        border-radius: 8px;
        font-size: 12px;
        font-weight: 500;
        white-space: nowrap;
        flex-shrink: 0;
    }
    
    /* 卡片内容 */
    .fav-card-content {
        color: #94A3B8;
        font-size: 14px;
        line-height: 1.7;
        padding: 16px;
        background: rgba(15, 23, 42, 0.6);
        border-radius: 12px;
        border: 1px solid rgba(51, 65, 85, 0.5);
    }
    
    /* 卡片间距 */
    .fav-card-spacer {
        height: 16px;
    }
    
    /* 空状态 */
    .fav-empty {
        text-align: center;
        padding: 80px 24px;
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border-radius: 16px;
        border: 2px dashed #334155;
    }
    .fav-empty-icon {
        font-size: 56px;
        margin-bottom: 20px;
        opacity: 0.4;
    }
    .fav-empty-title {
        color: #94A3B8;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .fav-empty-desc {
        color: #64748B;
        font-size: 14px;
    }
    
    /* 让按钮与输入框高度一致 */
    [data-testid="stTextInput"] input {
        height: 40px !important;
    }
    [data-testid="stButton"] > button {
        height: 40px !important;
        min-height: 40px !important;
        max-height: 40px !important;
        padding: 0 12px !important;
        line-height: 40px !important;
    }
    
    /* 调整列内元素垂直对齐 */
    [data-testid="column"] {
        display: flex;
        align-items: flex-end;
    }
    [data-testid="column"] > div {
        width: 100%;
    }
    [data-testid="column"] [data-testid="stVerticalBlock"] {
        gap: 0 !important;
    }
    </style>
    """, unsafe_allow_html=True)


def render_empty_favorites():
    """渲染空状态"""
    st.markdown("""
    <div class="fav-empty">
        <div class="fav-empty-icon">⭐</div>
        <div class="fav-empty-title">收藏夹为空</div>
        <div class="fav-empty-desc">在搜索结果中点击 ⭐ 按钮收藏重要论据</div>
    </div>
    """, unsafe_allow_html=True)


def export_favorites(manager):
    """导出收藏"""
    md_content = manager.export_to_markdown(
        include_favorites=True,
        include_arguments=False,
        include_tags=False
    )
    
    st.download_button(
        label="📥 下载 Markdown",
        data=md_content,
        file_name="favorites_export.md",
        mime="text/markdown"
    )


def get_content_manager() -> ContentManager:
    """获取内容管理器实例"""
    if "content_manager" not in st.session_state:
        st.session_state.content_manager = ContentManager()
    return st.session_state.content_manager
