"""搜索结果卡片组件"""

import streamlit as st
import html as html_lib
import re
from app.models.search_result import SearchResultItem
from app.services.content_manager import ContentManager


def safe_html_content(content: str) -> str:
    """安全处理 HTML 内容，保留高亮标签"""
    if not content:
        return ""
    
    # 先保存 <mark> 标签
    mark_placeholder = "___MARK_START___"
    mark_end_placeholder = "___MARK_END___"
    
    # 替换 <mark> 标签为占位符
    content = re.sub(r'<mark[^>]*>', mark_placeholder, content, flags=re.IGNORECASE)
    content = re.sub(r'</mark>', mark_end_placeholder, content, flags=re.IGNORECASE)
    
    # 转义所有 HTML 字符
    content = html_lib.escape(content)
    
    # 恢复 <mark> 标签（使用简单的样式）
    content = content.replace(mark_placeholder, '<b style="color:#22C55E;">')
    content = content.replace(mark_end_placeholder, '</b>')
    
    return content


def get_file_type_icon(file_type: str) -> tuple[str, str]:
    """获取文件类型图标和颜色"""
    icons = {
        "docx": ("📄", "#3B82F6"),
        "doc": ("📄", "#3B82F6"),
        "xlsx": ("📊", "#22C55E"),
        "xls": ("📊", "#22C55E"),
        "pdf": ("📕", "#EF4444"),
        "txt": ("📝", "#94A3B8"),
    }
    return icons.get(file_type.lower(), ("📄", "#94A3B8"))


def render_result_card(item: SearchResultItem, index: int, content_manager: ContentManager = None):
    """渲染搜索结果卡片"""
    icon, color = get_file_type_icon(item.file_type)
    
    # 计算相关度条
    score_width = min(100, max(10, item.score_percent))
    
    # 安全处理高亮内容
    safe_content = safe_html_content(item.highlighted_content)
    safe_file_name = html_lib.escape(item.file_name)
    safe_location = html_lib.escape(item.location_str)
    
    # 卡片容器
    with st.container():
        # 头部：文件信息
        st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;">
<div style="display:flex;align-items:center;">
<span style="display:inline-flex;align-items:center;justify-content:center;width:36px;height:36px;background:{color}20;border-radius:8px;margin-right:12px;font-size:18px;">{icon}</span>
<div><div style="color:#F8FAFC;font-weight:500;font-size:15px;">{safe_file_name}</div>
<div style="color:#64748B;font-size:12px;margin-top:2px;">{safe_location}</div></div>
</div>
</div>
""", unsafe_allow_html=True)
        
        # 操作按钮（使用单行列布局，避免嵌套）
        btn_col1, btn_col2, spacer = st.columns([1, 1, 10])
        with btn_col1:
            if st.button("⭐", key=f"fav_result_{index}", help="收藏此内容"):
                if content_manager:
                    result = content_manager.add_favorite(
                        document_id=item.doc_id,
                        file_name=item.file_name,
                        content=item.content,
                        paragraph_index=item.paragraph_index,
                        page_number=item.page_number
                    )
                    if result:
                        st.session_state["_toast_msg"] = ("已添加到收藏夹", "⭐")
                    else:
                        st.session_state["_toast_msg"] = ("该内容已收藏过", "ℹ️")
                    st.rerun()
        with btn_col2:
            if st.button("📎", key=f"arg_result_{index}", help="添加为论据"):
                st.session_state["pending_evidence"] = {
                    "content": item.content,
                    "source_document_id": item.doc_id,
                    "source_file_name": item.file_name,
                    "source_location": item.location_str,
                }
                st.session_state["current_page"] = "arguments"
                st.session_state["_toast_msg"] = ("请在论点管理页面选择论点添加此论据", "📎")
                st.rerun()
        
        # 内容区域
        st.markdown(f"""
<div style="background:#0F172A;padding:12px;border-radius:8px;margin:8px 0;border-left:3px solid #6366F1;">
<div style="color:#94A3B8;font-size:14px;line-height:1.7;">{safe_content}</div>
</div>
""", unsafe_allow_html=True)
        
        # 底部信息
        st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;padding:8px 0;">
<span style="color:#64748B;font-size:12px;">来源: {item.file_type.upper()}</span>
<div style="display:flex;align-items:center;gap:8px;">
<span style="color:#64748B;font-size:12px;">相关度:</span>
<div style="width:80px;height:6px;background:#334155;border-radius:3px;overflow:hidden;">
<div style="width:{score_width}%;height:100%;background:linear-gradient(90deg,#6366F1,#22C55E);border-radius:3px;"></div>
</div>
<span style="color:#64748B;font-size:12px;">{score_width}%</span>
</div>
</div>
""", unsafe_allow_html=True)
        
        st.markdown("<hr style='border:none;border-top:1px solid #334155;margin:12px 0;'>", unsafe_allow_html=True)


def render_result_list(items: list[SearchResultItem], content_manager: ContentManager = None):
    """渲染搜索结果列表 - 按文档分组，每个文档只显示最佳匹配"""
    if not items:
        render_empty_state()
        return
    
    # 获取 content_manager
    if content_manager is None:
        content_manager = ContentManager()
    
    # 按文件名分组，只保留每个文档的最高分结果
    seen_files = set()
    unique_items = []
    
    for item in items:
        if item.file_name not in seen_files:
            seen_files.add(item.file_name)
            unique_items.append(item)
    
    for idx, item in enumerate(unique_items):
        render_result_card(item, idx, content_manager)


def render_empty_state(message: str = "暂无搜索结果"):
    """渲染空状态"""
    st.markdown(f"""
    <div style="
        text-align: center;
        padding: 48px 24px;
        color: #64748B;
    ">
        <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;">🔍</div>
        <div style="font-size: 16px;">{message}</div>
        <div style="font-size: 14px; margin-top: 8px; color: #475569;">
            尝试使用不同的关键词或调整搜索条件
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_result_stats(total: int, query: str):
    """渲染搜索结果统计"""
    safe_query = html_lib.escape(query)
    st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;padding-bottom:16px;border-bottom:1px solid #334155;">
<div style="color:#F8FAFC;font-size:14px;">找到 <span style="color:#6366F1;font-weight:600;">{total}</span> 条与 "<span style="color:#22C55E;">{safe_query}</span>" 相关的结果</div>
<div style="color:#64748B;font-size:12px;">按相关度排序</div>
</div>
""", unsafe_allow_html=True)
