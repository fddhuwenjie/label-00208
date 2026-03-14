"""标签管理页面"""

import streamlit as st
from app.services.content_manager import ContentManager


def render_tags_page():
    """渲染标签管理页面"""
    
    # 统一高度样式
    st.markdown("""
    <style>
    [data-testid="stTextInput"] > div {
        background: transparent !important;
    }
    [data-testid="stTextInput"] input { 
        height: 42px !important; 
        background: #1E293B !important;
    }
    [data-testid="stColorPicker"] > div,
    [data-testid="stColorPicker"] > div > div { 
        width: 42px !important; 
        height: 42px !important; 
    }
    [data-testid="stButton"] > button { 
        height: 42px !important; 
        min-height: 42px !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <h1 style="color: #F8FAFC; font-size: 28px; font-weight: 600; margin-bottom: 8px;">
        🏷️ 标签管理
    </h1>
    <p style="color: #64748B; font-size: 14px; margin-bottom: 24px;">
        创建和管理文档标签
    </p>
    """, unsafe_allow_html=True)
    
    manager = get_content_manager()
    
    # 检查是否需要清空输入框（创建成功后的标志）
    if st.session_state.get("clear_tag_input", False):
        st.session_state["clear_tag_input"] = False
        # 使用不同的 key 来强制重置输入框
        st.session_state["tag_form_key"] = st.session_state.get("tag_form_key", 0) + 1
    
    form_key = st.session_state.get("tag_form_key", 0)
    
    # 创建新标签
    st.markdown("""
    <div style="color: #F8FAFC; font-size: 16px; font-weight: 500; margin-bottom: 12px;">
        创建新标签
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([30, 1, 10])
    
    with col1:
        new_tag_name = st.text_input(
            "标签名称",
            placeholder="输入标签名称...",
            key=f"new_tag_name_{form_key}",
            label_visibility="collapsed"
        )
    
    with col2:
        tag_color = st.color_picker(
            "颜色",
            value="#6366F1",
            key=f"new_tag_color_{form_key}",
            label_visibility="collapsed"
        )
    
    with col3:
        if st.button("➕ 创建", type="primary"):
            if new_tag_name.strip():
                result = manager.create_tag(new_tag_name.strip(), tag_color)
                if result:
                    st.toast(f"标签 '{new_tag_name}' 创建成功", icon="✅")
                    # 设置清空标志，下次渲染时会更新 form_key 来重置输入框
                    st.session_state["clear_tag_input"] = True
                    st.rerun()
                else:
                    st.error("标签名称已存在")
            else:
                st.warning("请输入标签名称")
    
    st.markdown("<hr style='border-color: #334155; margin: 24px 0;'>", unsafe_allow_html=True)
    
    # 标签列表
    st.markdown("""
    <div style="color: #F8FAFC; font-size: 16px; font-weight: 500; margin-bottom: 16px;">
        所有标签
    </div>
    """, unsafe_allow_html=True)
    
    tags = manager.get_all_tags()
    
    if not tags:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 40px 24px;
            background-color: #1E293B;
            border-radius: 12px;
            border: 1px dashed #334155;
        ">
            <div style="font-size: 32px; margin-bottom: 12px; opacity: 0.5;">🏷️</div>
            <div style="color: #94A3B8; font-size: 14px;">
                暂无标签，创建你的第一个标签吧
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 标签网格
    cols = st.columns(4)
    
    for idx, tag in enumerate(tags):
        col_idx = idx % 4
        with cols[col_idx]:
            st.markdown(f"""
            <div style="
                background-color: #1E293B;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 16px;
                margin-bottom: 12px;
                text-align: center;
            ">
                <div style="
                    display: inline-block;
                    width: 24px;
                    height: 24px;
                    background-color: {tag.color};
                    border-radius: 50%;
                    margin-bottom: 8px;
                "></div>
                <div style="color: #F8FAFC; font-size: 14px; font-weight: 500;">
                    {tag.name}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🗑️ 删除", key=f"del_tag_{tag.id}", use_container_width=True):
                manager.delete_tag(tag.id)
                st.rerun()


def get_content_manager() -> ContentManager:
    """获取内容管理器实例"""
    if "content_manager" not in st.session_state:
        st.session_state.content_manager = ContentManager()
    return st.session_state.content_manager
