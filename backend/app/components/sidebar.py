"""侧边栏组件"""

import streamlit as st
from pathlib import Path


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        # Logo 和标题
        st.markdown("""
        <div style="padding: 20px 0; text-align: center; border-bottom: 1px solid #334155; margin-bottom: 20px;">
            <h1 style="font-size: 24px; font-weight: 700; color: #F8FAFC; margin: 0;">
                🎯 DebatePrep
            </h1>
            <p style="font-size: 12px; color: #64748B; margin-top: 8px;">
                辩论赛智能备赛助手
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 导航菜单
        st.markdown("""
        <style>
            .nav-item {
                display: flex;
                align-items: center;
                padding: 12px 16px;
                margin: 4px 0;
                border-radius: 8px;
                color: #94A3B8;
                text-decoration: none;
                transition: all 150ms ease;
                cursor: pointer;
            }
            .nav-item:hover {
                background-color: #1E293B;
                color: #F8FAFC;
            }
            .nav-item.active {
                background-color: #1E293B;
                color: #F8FAFC;
                border-left: 3px solid #6366F1;
            }
            .nav-icon {
                margin-right: 12px;
                font-size: 18px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        # 使用 session_state 管理当前页面
        if "current_page" not in st.session_state:
            st.session_state.current_page = "dashboard"
        
        # 导航按钮
        pages = [
            ("dashboard", "📊", "仪表盘"),
            ("search", "🔍", "智能搜索"),
            ("documents", "📂", "文档库"),
            ("favorites", "⭐", "收藏夹"),
            ("tags", "🏷️", "标签管理"),
            ("arguments", "📑", "论点管理"),
            ("export", "📤", "导出"),
        ]
        
        for page_id, icon, label in pages:
            if st.button(
                f"{icon}  {label}",
                key=f"nav_{page_id}",
                use_container_width=True,
                type="secondary" if st.session_state.current_page != page_id else "primary"
            ):
                st.session_state.current_page = page_id
                st.rerun()
        
        # 底部设置
        st.markdown("<hr style='margin: 20px 0; border-color: #334155;'>", unsafe_allow_html=True)
        
        if st.button("⚙️  设置", key="nav_settings", use_container_width=True, type="secondary"):
            st.session_state.current_page = "settings"
            st.rerun()


