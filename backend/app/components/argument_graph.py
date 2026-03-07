"""论点-论据关系图谱组件"""

import streamlit as st
import json
from typing import Optional
from app.models.argument import Argument, ArgumentSide


def render_argument_graph(arguments: list[Argument], title: str = "论点-论据关系图谱"):
    """
    渲染论点-论据关系图谱
    
    使用 HTML/CSS/JS 实现交互式可视化图谱
    """
    if not arguments:
        st.info("暂无论点数据，请先创建论点")
        return
    
    # 构建图谱数据
    graph_data = build_graph_data(arguments)
    
    # 渲染图谱
    st.markdown(f"""
    <div class="graph-container">
        <h3 class="graph-title">{title}</h3>
        <div class="graph-legend">
            <span class="legend-item pro"><span class="legend-dot"></span>正方</span>
            <span class="legend-item con"><span class="legend-dot"></span>反方</span>
            <span class="legend-item neutral"><span class="legend-dot"></span>中立</span>
            <span class="legend-item evidence"><span class="legend-dot"></span>论据</span>
        </div>
        <div id="argument-graph" class="graph-canvas"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # 注入图谱样式
    inject_graph_styles()
    
    # 渲染静态图谱（Streamlit 兼容）
    render_static_graph(arguments)


def build_graph_data(arguments: list[Argument]) -> dict:
    """构建图谱数据结构"""
    nodes = []
    edges = []
    
    for arg in arguments:
        # 论点节点
        node_type = arg.side.value
        nodes.append({
            "id": f"arg_{arg.id}",
            "label": arg.title[:20] + "..." if len(arg.title) > 20 else arg.title,
            "type": node_type,
            "full_title": arg.title,
            "description": arg.description or "",
            "evidence_count": len(arg.evidences)
        })
        
        # 论据节点和边
        for ev in arg.evidences:
            ev_id = f"ev_{ev.id}"
            nodes.append({
                "id": ev_id,
                "label": ev.content[:15] + "..." if len(ev.content) > 15 else ev.content,
                "type": "evidence",
                "full_content": ev.content,
                "source": ev.source_file_name or ""
            })
            edges.append({
                "source": f"arg_{arg.id}",
                "target": ev_id
            })
    
    return {"nodes": nodes, "edges": edges}


def inject_graph_styles():
    """注入图谱样式"""
    st.markdown("""
    <style>
    .graph-container {
        background: #1E293B;
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
    }
    .graph-title {
        color: #F8FAFC;
        font-size: 18px;
        font-weight: 600;
        margin: 0 0 16px 0;
    }
    .graph-legend {
        display: flex;
        gap: 20px;
        margin-bottom: 20px;
        flex-wrap: wrap;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 6px;
        font-size: 13px;
        color: #94A3B8;
    }
    .legend-dot {
        width: 12px;
        height: 12px;
        border-radius: 50%;
    }
    .legend-item.pro .legend-dot { background: #14B8A6; }
    .legend-item.con .legend-dot { background: #F59E0B; }
    .legend-item.neutral .legend-dot { background: #A855F7; }
    .legend-item.evidence .legend-dot { background: #6366F1; border-radius: 2px; }
    
    /* 静态图谱样式 */
    .static-graph {
        display: flex;
        flex-direction: column;
        gap: 24px;
    }
    .graph-section {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 12px;
        padding: 20px;
    }
    .section-header {
        display: flex;
        align-items: center;
        gap: 10px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 1px solid #334155;
    }
    .section-title {
        color: #F8FAFC;
        font-size: 15px;
        font-weight: 600;
    }
    .section-badge {
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: 500;
    }
    .section-badge.pro { background: rgba(20, 184, 166, 0.15); color: #14B8A6; }
    .section-badge.con { background: rgba(245, 158, 11, 0.15); color: #F59E0B; }
    .section-badge.neutral { background: rgba(168, 85, 247, 0.15); color: #A855F7; }
    
    /* 论点卡片 */
    .graph-arg-card {
        display: flex;
        align-items: flex-start;
        gap: 16px;
        margin-bottom: 16px;
    }
    .arg-node {
        flex-shrink: 0;
        width: 160px;
        padding: 14px 16px;
        border-radius: 10px;
        text-align: center;
    }
    .arg-node.pro { background: rgba(20, 184, 166, 0.12); border: 2px solid #14B8A6; }
    .arg-node.con { background: rgba(245, 158, 11, 0.12); border: 2px solid #F59E0B; }
    .arg-node.neutral { background: rgba(168, 85, 247, 0.12); border: 2px solid #A855F7; }
    .arg-node-title {
        color: #F8FAFC;
        font-size: 13px;
        font-weight: 600;
        line-height: 1.4;
    }
    .arg-node-count {
        color: #64748B;
        font-size: 11px;
        margin-top: 6px;
    }
    
    /* 连接线 */
    .graph-connector {
        display: flex;
        align-items: center;
        color: #475569;
        font-size: 18px;
        padding: 0 8px;
    }
    
    /* 论据列表 */
    .ev-list {
        flex: 1;
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }
    .ev-node {
        background: rgba(99, 102, 241, 0.1);
        border: 1px solid rgba(99, 102, 241, 0.3);
        border-radius: 8px;
        padding: 10px 14px;
        max-width: 220px;
    }
    .ev-node-content {
        color: #CBD5E1;
        font-size: 12px;
        line-height: 1.5;
        word-break: break-word;
    }
    .ev-node-source {
        color: #64748B;
        font-size: 10px;
        margin-top: 6px;
    }
    .no-evidence {
        color: #64748B;
        font-size: 12px;
        font-style: italic;
    }
    
    /* 统计摘要 */
    .graph-summary {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 16px;
        margin-bottom: 24px;
    }
    .summary-card {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        padding: 16px;
        text-align: center;
    }
    .summary-value {
        font-size: 28px;
        font-weight: 700;
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 4px;
    }
    .summary-value.pro { color: #14B8A6; }
    .summary-value.con { color: #F59E0B; }
    .summary-value.neutral { color: #A855F7; }
    .summary-value.total { color: #6366F1; }
    .summary-label {
        color: #64748B;
        font-size: 12px;
    }
    </style>
    """, unsafe_allow_html=True)


def render_static_graph(arguments: list[Argument]):
    """渲染静态图谱（纯 HTML/CSS 实现，Streamlit 兼容）"""
    import html as html_lib
    
    # 统计摘要
    pro_args = [a for a in arguments if a.side == ArgumentSide.PRO]
    con_args = [a for a in arguments if a.side == ArgumentSide.CON]
    neutral_args = [a for a in arguments if a.side == ArgumentSide.NEUTRAL]
    total_evidences = sum(len(a.evidences) for a in arguments)
    
    summary_html = f'''<div class="graph-summary">
<div class="summary-card"><div class="summary-value pro">{len(pro_args)}</div><div class="summary-label">正方论点</div></div>
<div class="summary-card"><div class="summary-value con">{len(con_args)}</div><div class="summary-label">反方论点</div></div>
<div class="summary-card"><div class="summary-value neutral">{len(neutral_args)}</div><div class="summary-label">中立观点</div></div>
<div class="summary-card"><div class="summary-value total">{total_evidences}</div><div class="summary-label">总论据数</div></div>
</div>'''
    st.markdown(summary_html, unsafe_allow_html=True)
    
    # 按立场分组渲染
    sections = [
        ("正方论点", pro_args, "pro"),
        ("反方论点", con_args, "con"),
        ("中立观点", neutral_args, "neutral"),
    ]
    
    graph_parts = ['<div class="static-graph">']
    
    for section_title, args, side_class in sections:
        if not args:
            continue
        
        graph_parts.append(f'<div class="graph-section"><div class="section-header"><span class="section-title">{section_title}</span><span class="section-badge {side_class}">{len(args)} 个</span></div>')
        
        for arg in args:
            safe_title = html_lib.escape(arg.title[:25] + "..." if len(arg.title) > 25 else arg.title)
            ev_count = len(arg.evidences)
            
            graph_parts.append(f'<div class="graph-arg-card"><div class="arg-node {side_class}"><div class="arg-node-title">{safe_title}</div><div class="arg-node-count">{ev_count} 条论据</div></div><div class="graph-connector">→</div><div class="ev-list">')
            
            if arg.evidences:
                for ev in arg.evidences[:5]:
                    safe_content = html_lib.escape(ev.content[:50] + "..." if len(ev.content) > 50 else ev.content)
                    source_html = f'<div class="ev-node-source">📄 {html_lib.escape(ev.source_file_name)}</div>' if ev.source_file_name else ''
                    graph_parts.append(f'<div class="ev-node"><div class="ev-node-content">{safe_content}</div>{source_html}</div>')
                if len(arg.evidences) > 5:
                    graph_parts.append(f'<div class="ev-node"><div class="ev-node-content">+{len(arg.evidences) - 5} 更多...</div></div>')
            else:
                graph_parts.append('<div class="no-evidence">暂无论据</div>')
            
            graph_parts.append('</div></div>')
        
        graph_parts.append('</div>')
    
    graph_parts.append('</div>')
    
    graph_html = ''.join(graph_parts)
    st.markdown(graph_html, unsafe_allow_html=True)


def render_comparison_view(arguments: list[Argument]):
    """渲染正反方对比视图"""
    pro_args = [a for a in arguments if a.side == ArgumentSide.PRO]
    con_args = [a for a in arguments if a.side == ArgumentSide.CON]
    
    st.markdown("""
    <style>
    .comparison-container {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 24px;
    }
    .comparison-side {
        background: #1E293B;
        border-radius: 16px;
        padding: 20px;
        border: 1px solid #334155;
    }
    .comparison-side.pro { border-top: 4px solid #14B8A6; }
    .comparison-side.con { border-top: 4px solid #F59E0B; }
    .comparison-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 20px;
        padding-bottom: 12px;
        border-bottom: 1px solid #334155;
    }
    .comparison-title {
        font-size: 16px;
        font-weight: 600;
    }
    .comparison-title.pro { color: #14B8A6; }
    .comparison-title.con { color: #F59E0B; }
    .comparison-count {
        background: rgba(255, 255, 255, 0.05);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        color: #94A3B8;
    }
    .comparison-item {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 10px;
        padding: 14px 16px;
        margin-bottom: 12px;
    }
    .comparison-item-title {
        color: #F8FAFC;
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 8px;
    }
    .comparison-item-desc {
        color: #94A3B8;
        font-size: 12px;
        line-height: 1.5;
    }
    .comparison-item-meta {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-top: 10px;
        color: #64748B;
        font-size: 11px;
    }
    .strength-bar {
        flex: 1;
        height: 4px;
        background: #334155;
        border-radius: 2px;
        overflow: hidden;
    }
    .strength-fill {
        height: 100%;
        border-radius: 2px;
    }
    .strength-fill.pro { background: linear-gradient(90deg, #14B8A6, #2DD4BF); }
    .strength-fill.con { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
    .empty-side {
        text-align: center;
        padding: 40px 20px;
        color: #64748B;
        font-size: 13px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    import html as html_lib
    
    parts = ['<div class="comparison-container">']
    
    # 正方
    parts.append(f'<div class="comparison-side pro"><div class="comparison-header"><span class="comparison-title pro">👍 正方观点</span><span class="comparison-count">{len(pro_args)} 个论点</span></div>')
    
    if pro_args:
        max_strength = max((a.strength for a in pro_args), default=1) or 1
        for arg in pro_args:
            safe_title = html_lib.escape(arg.title)
            safe_desc = html_lib.escape(arg.description[:100] + "..." if arg.description and len(arg.description) > 100 else (arg.description or ""))
            strength_percent = (arg.strength / max_strength) * 100
            desc_html = f'<div class="comparison-item-desc">{safe_desc}</div>' if safe_desc else ''
            parts.append(f'<div class="comparison-item"><div class="comparison-item-title">{safe_title}</div>{desc_html}<div class="comparison-item-meta"><span>{len(arg.evidences)} 条论据</span><div class="strength-bar"><div class="strength-fill pro" style="width: {strength_percent}%"></div></div></div></div>')
    else:
        parts.append('<div class="empty-side">暂无正方论点</div>')
    
    parts.append('</div>')
    
    # 反方
    parts.append(f'<div class="comparison-side con"><div class="comparison-header"><span class="comparison-title con">👎 反方观点</span><span class="comparison-count">{len(con_args)} 个论点</span></div>')
    
    if con_args:
        max_strength = max((a.strength for a in con_args), default=1) or 1
        for arg in con_args:
            safe_title = html_lib.escape(arg.title)
            safe_desc = html_lib.escape(arg.description[:100] + "..." if arg.description and len(arg.description) > 100 else (arg.description or ""))
            strength_percent = (arg.strength / max_strength) * 100
            desc_html = f'<div class="comparison-item-desc">{safe_desc}</div>' if safe_desc else ''
            parts.append(f'<div class="comparison-item"><div class="comparison-item-title">{safe_title}</div>{desc_html}<div class="comparison-item-meta"><span>{len(arg.evidences)} 条论据</span><div class="strength-bar"><div class="strength-fill con" style="width: {strength_percent}%"></div></div></div></div>')
    else:
        parts.append('<div class="empty-side">暂无反方论点</div>')
    
    parts.append('</div></div>')
    
    st.markdown(''.join(parts), unsafe_allow_html=True)
