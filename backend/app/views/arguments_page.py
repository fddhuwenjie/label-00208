"""论点管理页面 - 增强版"""

import streamlit as st
import html
from app.services.content_manager import ContentManager
from app.services.semantic_analyzer import auto_classify_stance
from app.models.argument import ArgumentSide
from app.components.argument_graph import render_argument_graph, render_comparison_view
from app.utils.text_utils import strip_html_tags


def render_arguments_page():
    """渲染论点管理页面"""
    
    inject_arguments_styles()
    
    st.markdown("""
    <div class="args-header">
        <h1 class="args-title">📑 论点管理</h1>
        <p class="args-subtitle">整理辩论论点和论据，支持关系图谱可视化</p>
    </div>
    """, unsafe_allow_html=True)
    
    manager = get_content_manager()
    
    # 功能选项卡
    tab1, tab2, tab3 = st.tabs(["📋 论点列表", "🗺️ 关系图谱", "⚖️ 正反对比"])
    
    with tab1:
        # 创建新论点
        render_create_argument_form(manager)
        st.markdown('<div class="args-divider"></div>', unsafe_allow_html=True)
        # 论点列表
        render_argument_list(manager)
    
    with tab2:
        arguments = manager.get_all_arguments()
        render_argument_graph(arguments)
    
    with tab3:
        arguments = manager.get_all_arguments()
        render_comparison_view(arguments)


def inject_arguments_styles():
    """注入样式"""
    st.markdown("""
    <style>
    .args-header { margin-bottom: 24px; }
    .args-title { font-size: 28px; font-weight: 600; color: #F8FAFC; margin: 0 0 8px 0; }
    .args-subtitle { font-size: 14px; color: #64748B; margin: 0; }
    .args-divider { height: 1px; background: linear-gradient(90deg, transparent, #334155, transparent); margin: 24px 0; }
    
    /* 立场标签 */
    .side-label {
        padding: 12px 20px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 14px;
        text-align: center;
        margin-bottom: 16px;
    }
    .side-label.pro { background: rgba(20, 184, 166, 0.12); color: #14B8A6; border: 1px solid rgba(20, 184, 166, 0.25); }
    .side-label.con { background: rgba(245, 158, 11, 0.12); color: #F59E0B; border: 1px solid rgba(245, 158, 11, 0.25); }
    .side-label.neutral { background: rgba(168, 85, 247, 0.12); color: #A855F7; border: 1px solid rgba(168, 85, 247, 0.25); }
    
    /* 论点模块 */
    .arg-module {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        margin-bottom: 20px;
        overflow: hidden;
    }
    .arg-module.pro { border-left: 4px solid #14B8A6; }
    .arg-module.con { border-left: 4px solid #F59E0B; }
    .arg-module.neutral { border-left: 4px solid #A855F7; }
    
    /* 模块头部 */
    .arg-module-header {
        padding: 18px 20px;
        background: rgba(15, 23, 42, 0.3);
        border-bottom: 1px solid #334155;
    }
    .arg-module-title {
        color: #F8FAFC;
        font-weight: 600;
        font-size: 16px;
        margin-bottom: 6px;
    }
    .arg-module-desc {
        color: #94A3B8;
        font-size: 13px;
        line-height: 1.5;
    }
    
    /* 模块内容区 - 论据 */
    .arg-module-body {
        padding: 16px 20px;
    }
    .arg-section-title {
        color: #64748B;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .evidence-card {
        background: #0F172A;
        border: 1px solid #334155;
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 10px;
    }
    .evidence-text {
        color: #CBD5E1;
        font-size: 13px;
        line-height: 1.7;
    }
    .evidence-meta {
        color: #64748B;
        font-size: 11px;
        margin-top: 10px;
        padding-top: 10px;
        border-top: 1px dashed #334155;
    }
    .no-evidence {
        color: #64748B;
        font-size: 13px;
        text-align: center;
        padding: 20px;
        background: rgba(15, 23, 42, 0.5);
        border-radius: 8px;
    }
    
    /* 模块底部 - 操作区 */
    .arg-module-footer {
        padding: 14px 20px;
        background: rgba(15, 23, 42, 0.5);
        border-top: 1px solid #334155;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .arg-badge {
        font-size: 12px;
        padding: 4px 10px;
        border-radius: 6px;
    }
    .arg-badge.pro { background: rgba(20, 184, 166, 0.15); color: #14B8A6; }
    .arg-badge.con { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
    .arg-badge.neutral { background: rgba(168, 85, 247, 0.15); color: #A855F7; }
    
    /* 空状态 */
    .args-empty {
        text-align: center;
        padding: 60px 24px;
        background: #1E293B;
        border-radius: 16px;
        border: 2px dashed #334155;
    }
    .args-empty-icon { font-size: 48px; margin-bottom: 16px; opacity: 0.4; }
    .args-empty-title { color: #94A3B8; font-size: 16px; margin-bottom: 8px; }
    .args-empty-desc { color: #64748B; font-size: 14px; }
    
    /* 列空状态 */
    .col-empty {
        text-align: center;
        padding: 40px 20px;
        color: #64748B;
        font-size: 13px;
        background: rgba(30, 41, 59, 0.5);
        border-radius: 12px;
        border: 1px dashed #334155;
    }
    
    /* 自动分类建议 */
    .auto-classify-result {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 10px;
        padding: 14px 16px;
        margin-top: 12px;
    }
    .classify-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
    }
    .classify-icon { font-size: 16px; }
    .classify-title {
        color: #818CF8;
        font-size: 13px;
        font-weight: 600;
    }
    .classify-suggestion {
        color: #94A3B8;
        font-size: 12px;
        line-height: 1.5;
    }
    .classify-keywords {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 8px;
    }
    .classify-keyword {
        background: rgba(255, 255, 255, 0.05);
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        color: #CBD5E1;
    }
    </style>
    """, unsafe_allow_html=True)


def render_create_argument_form(manager):
    """创建论点表单 - 增强版，支持自动立场分类"""
    with st.expander("➕ 创建新论点", expanded=False):
        title = st.text_input("论点标题", placeholder="输入论点标题...", key="new_arg_title")
        
        description = st.text_area("描述（可选）", placeholder="详细描述这个论点...", key="new_arg_desc", height=100)
        
        # 自动分类功能
        auto_result = None
        if description and len(description) >= 10:
            auto_result = auto_classify_stance(description)
            
            keywords_html = "".join([f'<span class="classify-keyword">{kw}</span>' for kw in auto_result["keywords"][:6]])
            
            stance_icon = {"pro": "👍", "con": "👎", "neutral": "📌"}.get(auto_result["stance"], "📌")
            
            st.markdown(f"""
            <div class="auto-classify-result">
                <div class="classify-header">
                    <span class="classify-icon">{stance_icon}</span>
                    <span class="classify-title">AI 立场分析</span>
                </div>
                <div class="classify-suggestion">{auto_result["suggestion"]}</div>
                {"<div class='classify-keywords'>" + keywords_html + "</div>" if keywords_html else ""}
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            # 如果有自动分类结果，设置默认选项
            default_idx = 2  # 默认中立
            if auto_result:
                if auto_result["stance"] == "pro":
                    default_idx = 0
                elif auto_result["stance"] == "con":
                    default_idx = 1
            
            side = st.selectbox(
                "立场", 
                options=["正方", "反方", "中立"], 
                index=default_idx,
                key="new_arg_side",
                help="可根据 AI 分析建议选择，或手动指定"
            )
        
        with col2:
            st.markdown("<div style='height: 28px'></div>", unsafe_allow_html=True)
            if st.button("创建论点", type="primary", key="create_arg_btn", use_container_width=True):
                if title.strip():
                    side_map = {"正方": ArgumentSide.PRO, "反方": ArgumentSide.CON, "中立": ArgumentSide.NEUTRAL}
                    manager.create_argument(title=title.strip(), description=description.strip() or None, side=side_map[side])
                    st.toast(f"论点创建成功", icon="✅")
                    st.rerun()
                else:
                    st.warning("请输入论点标题")


def render_argument_list(manager):
    """渲染论点列表"""
    arguments = manager.get_all_arguments()
    
    if not arguments:
        st.markdown("""
        <div class="args-empty">
            <div class="args-empty-icon">📑</div>
            <div class="args-empty-title">暂无论点</div>
            <div class="args-empty-desc">点击上方"创建新论点"开始整理</div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    pro_args = [a for a in arguments if a.side == ArgumentSide.PRO]
    con_args = [a for a in arguments if a.side == ArgumentSide.CON]
    neutral_args = [a for a in arguments if a.side == ArgumentSide.NEUTRAL]
    
    # 正反方并排
    col_pro, col_con = st.columns(2)
    
    with col_pro:
        st.markdown(f'<div class="side-label pro">👍 正方论点 ({len(pro_args)})</div>', unsafe_allow_html=True)
        if pro_args:
            for arg in pro_args:
                render_argument_module(arg, manager, "pro")
        else:
            st.markdown('<div class="col-empty">暂无正方论点</div>', unsafe_allow_html=True)
    
    with col_con:
        st.markdown(f'<div class="side-label con">👎 反方论点 ({len(con_args)})</div>', unsafe_allow_html=True)
        if con_args:
            for arg in con_args:
                render_argument_module(arg, manager, "con")
        else:
            st.markdown('<div class="col-empty">暂无反方论点</div>', unsafe_allow_html=True)
    
    # 中立观点
    if neutral_args:
        st.markdown('<div class="args-divider"></div>', unsafe_allow_html=True)
        st.markdown(f'<div class="side-label neutral">📌 中立观点 ({len(neutral_args)})</div>', unsafe_allow_html=True)
        for arg in neutral_args:
            render_argument_module(arg, manager, "neutral")


def render_argument_module(arg, manager, side_class: str):
    """渲染单个论点模块"""
    
    safe_title = html.escape(str(arg.title)) if arg.title else ''
    safe_desc = html.escape(str(arg.description)) if arg.description else ''
    
    # 构建论据HTML
    if arg.evidences:
        evidences_html = '<div class="arg-section-title">📎 支撑论据</div>'
        for ev in arg.evidences:
            # 清理 HTML 标签，确保只显示纯文本
            clean_content = strip_html_tags(str(ev.content))
            content = clean_content[:300] + '...' if len(clean_content) > 300 else clean_content
            safe_content = html.escape(content)
            
            # 构建来源信息
            source_parts = []
            if ev.source_file_name:
                source_parts.append(f"📄 {html.escape(str(ev.source_file_name))}")
            if ev.source_location:
                source_parts.append(f"📍 {html.escape(str(ev.source_location))}")
            
            source_html = ""
            if source_parts:
                source_info = " · ".join(source_parts)
                source_html = f'<div class="evidence-meta">{source_info}</div>'
            
            evidences_html += f'''
            <div class="evidence-card">
                <div class="evidence-text">{safe_content}</div>
                {source_html}
            </div>'''
    else:
        evidences_html = '<div class="no-evidence">暂无论据，点击下方添加</div>'
    
    # 渲染完整模块
    st.markdown(f"""
    <div class="arg-module {side_class}">
        <div class="arg-module-header">
            <div class="arg-module-title">{safe_title}</div>
            {f'<div class="arg-module-desc">{safe_desc}</div>' if safe_desc else ''}
        </div>
        <div class="arg-module-body">
            {evidences_html}
        </div>
        <div class="arg-module-footer">
            <span class="arg-badge {side_class}">{len(arg.evidences) if arg.evidences else 0} 条论据</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 操作按钮行 - 使用更紧凑的布局
    c1, c2 = st.columns(2)
    with c1:
        if st.button("➕ 添加论据", key=f"add_{arg.id}", type="secondary", use_container_width=True):
            st.session_state[f"show_form_{arg.id}"] = not st.session_state.get(f"show_form_{arg.id}", False)
    with c2:
        if st.button("🗑️ 删除", key=f"del_{arg.id}", use_container_width=True):
            manager.delete_argument(arg.id)
            st.toast("已删除", icon="🗑️")
            st.rerun()
    
    # 添加论据表单
    if st.session_state.get(f"show_form_{arg.id}", False):
        render_evidence_form(arg, manager)
    
    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)


def render_evidence_form(arg, manager):
    """渲染添加论据表单 - 增强版，支持自动立场检测和来源追踪"""
    with st.container():
        st.markdown("---")
        
        # 检查是否有从搜索结果导入的论据
        pending = st.session_state.get("pending_evidence", None)
        default_content = pending.get("content", "") if pending else ""
        default_source = pending.get("source_file_name", "") if pending else ""
        default_location = pending.get("source_location", "") if pending else ""
        default_doc_id = pending.get("source_document_id", "") if pending else ""
        
        if pending:
            st.info("📎 已从搜索结果导入内容，请确认后保存", icon="📎")
        
        ev_content = st.text_area(
            "论据内容", 
            value=default_content,
            placeholder="输入支撑该论点的论据...", 
            key=f"ev_{arg.id}", 
            height=100
        )
        
        # 自动分析论据立场
        if ev_content and len(ev_content) >= 10:
            ev_analysis = auto_classify_stance(ev_content)
            stance_match = (
                (ev_analysis["stance"] == "pro" and arg.side == ArgumentSide.PRO) or
                (ev_analysis["stance"] == "con" and arg.side == ArgumentSide.CON) or
                ev_analysis["stance"] == "neutral"
            )
            
            if stance_match:
                st.success(f"✓ 论据立场与论点一致", icon="✅")
            else:
                st.warning(f"⚠️ 论据立场可能与论点不一致：{ev_analysis['suggestion']}", icon="⚠️")
        
        # 来源信息
        col_src1, col_src2 = st.columns(2)
        with col_src1:
            ev_source = st.text_input(
                "来源文件", 
                value=default_source,
                placeholder="如：报告名称.pdf", 
                key=f"src_{arg.id}"
            )
        with col_src2:
            ev_location = st.text_input(
                "位置信息", 
                value=default_location,
                placeholder="如：第3页 第2段", 
                key=f"loc_{arg.id}"
            )
        
        fc1, fc2, fc3 = st.columns([1, 1, 4])
        with fc1:
            if st.button("✅ 保存", key=f"save_{arg.id}", type="primary"):
                if ev_content.strip():
                    manager.add_evidence(
                        arg.id, 
                        ev_content.strip(), 
                        source_document_id=default_doc_id or None,
                        source_file_name=ev_source or None,
                        source_location=ev_location or None
                    )
                    st.session_state[f"show_form_{arg.id}"] = False
                    # 清除导入的待处理论据
                    if "pending_evidence" in st.session_state:
                        del st.session_state["pending_evidence"]
                    st.toast("论据已添加", icon="✅")
                    st.rerun()
                else:
                    st.warning("请输入论据内容")
        with fc2:
            if st.button("❌ 取消", key=f"cancel_{arg.id}"):
                st.session_state[f"show_form_{arg.id}"] = False
                # 清除导入的待处理论据
                if "pending_evidence" in st.session_state:
                    del st.session_state["pending_evidence"]
                st.rerun()
        st.markdown("---")


def get_content_manager() -> ContentManager:
    if "content_manager" not in st.session_state:
        st.session_state.content_manager = ContentManager()
    return st.session_state.content_manager
