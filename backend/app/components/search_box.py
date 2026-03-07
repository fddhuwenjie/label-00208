"""搜索框组件"""

import streamlit as st


def render_search_box(
    placeholder: str = "输入关键词搜索...",
    key: str = "search_input"
) -> tuple[str, bool]:
    """
    渲染搜索框
    
    Returns:
        (搜索关键词, 是否触发搜索)
    """
    # 检查是否有待处理的搜索词（如点击语义标签）
    pending_query = st.session_state.pop("pending_search_query", None)
    if pending_query:
        st.session_state[key] = pending_query
    
    # 定义回车键触发的回调
    def on_enter():
        st.session_state.search_triggered = True
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        query = st.text_input(
            label="搜索",
            placeholder=placeholder,
            key=key,
            label_visibility="collapsed",
            on_change=on_enter
        )
    
    with col2:
        search_clicked = st.button("搜索", key=f"{key}_btn", type="primary", use_container_width=True)
    
    # 检查是否通过回车键触发
    enter_triggered = st.session_state.pop("search_triggered", False)
    
    return query, search_clicked or enter_triggered


def render_search_filters():
    """渲染搜索过滤器"""
    with st.expander("高级搜索选项", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            file_types = st.multiselect(
                "文件类型",
                options=["docx", "xlsx", "pdf", "txt"],
                default=None,
                key="filter_file_types"
            )
        
        with col2:
            search_mode = st.selectbox(
                "搜索模式",
                options=["智能搜索", "精确匹配", "布尔搜索"],
                key="filter_search_mode"
            )
        
        with col3:
            sort_by = st.selectbox(
                "排序方式",
                options=["相关度", "文件名", "修改时间"],
                key="filter_sort_by"
            )
        
        # 布尔搜索帮助
        if search_mode == "布尔搜索":
            st.info("""
            **布尔搜索语法:**
            - `AND` - 同时包含多个词，如: `年轻人 AND 就业`
            - `OR` - 包含任一词，如: `青年 OR 年轻人`
            - `NOT` - 排除某词，如: `年轻人 NOT 老年`
            - 使用括号组合: `(年轻人 OR 青年) AND 就业`
            """)
    
    return {
        "file_types": file_types if file_types else None,
        "search_mode": search_mode,
        "sort_by": sort_by,
    }


def render_semantic_tags(tags: list[str], on_click_key: str = "semantic_tag"):
    """渲染语义联想标签"""
    if not tags:
        return None
    
    st.markdown("""
    <div style="margin: 16px 0;">
        <span style="color: #64748B; font-size: 14px; margin-right: 12px;">💡 相关概念:</span>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建标签网格
    cols = st.columns(min(len(tags), 6))
    clicked_tag = None
    
    for idx, tag in enumerate(tags[:12]):  # 最多显示12个
        col_idx = idx % 6
        with cols[col_idx]:
            if st.button(
                tag,
                key=f"{on_click_key}_{idx}",
                use_container_width=True,
            ):
                clicked_tag = tag
    
    return clicked_tag
