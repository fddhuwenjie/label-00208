"""仪表盘页面 - 专业统计展示（增强版）"""

import streamlit as st
from datetime import datetime

from app.services.content_manager import ContentManager
from app.services.data_statistics import get_document_statistics, DataStatisticsService
from app.config import DISABLE_DEMO_DATA


def render_dashboard_page():
    """渲染仪表盘页面"""
    
    # 注入仪表盘专用样式
    inject_dashboard_styles()
    
    # 页面标题
    st.markdown('''
<div class="dashboard-header">
    <h1 class="dashboard-title">仪表盘</h1>
    <p class="dashboard-subtitle">文档库概览与统计分析</p>
</div>
''', unsafe_allow_html=True)
    
    # 演示数据提示
    render_demo_data_banner()
    
    # 获取统计数据
    stats = get_dashboard_stats()
    
    # 核心指标卡片
    render_metric_cards(stats)
    
    # 间距
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    
    # 三列布局
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_file_type_distribution(stats)
    
    with col2:
        render_data_extraction_stats(stats)
    
    with col3:
        render_recent_activity(stats)
    
    # 间距
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    
    # 两列布局：关键词云 + 论点分析
    col_kw, col_arg = st.columns(2)
    
    with col_kw:
        render_keyword_cloud(stats)
    
    with col_arg:
        render_argument_analysis(stats)
    
    # 间距
    st.markdown('<div class="section-gap"></div>', unsafe_allow_html=True)
    
    # 索引状态
    render_index_status(stats)


def inject_dashboard_styles():
    """注入仪表盘专用 CSS"""
    st.markdown('''
<style>
/* 仪表盘头部 */
.dashboard-header {
    margin-bottom: 32px;
}
.dashboard-title {
    font-size: 32px;
    font-weight: 700;
    color: #F8FAFC;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}
.dashboard-subtitle {
    font-size: 14px;
    color: #64748B;
    margin: 0;
}

/* 间距 */
.section-gap {
    height: 24px;
}

/* 指标卡片容器 */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
}

/* 单个指标卡片 */
.metric-card {
    background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
    transition: all 0.2s ease;
}
.metric-card:hover {
    border-color: #6366F1;
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.15);
}
.metric-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 16px;
    font-size: 24px;
}
.metric-icon.blue { background: rgba(99, 102, 241, 0.15); }
.metric-icon.green { background: rgba(34, 197, 94, 0.15); }
.metric-icon.amber { background: rgba(245, 158, 11, 0.15); }
.metric-icon.pink { background: rgba(236, 72, 153, 0.15); }

.metric-value {
    font-size: 36px;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    margin-bottom: 8px;
    line-height: 1;
}
.metric-value.blue { color: #818CF8; }
.metric-value.green { color: #4ADE80; }
.metric-value.amber { color: #FCD34D; }
.metric-value.pink { color: #F472B6; }

.metric-label {
    font-size: 13px;
    color: #64748B;
    font-weight: 500;
}

/* 面板卡片 */
.panel-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 24px;
    height: 100%;
}
.panel-title {
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}
.panel-icon {
    width: 24px;
    height: 24px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
}

/* 进度条项 */
.progress-item {
    margin-bottom: 16px;
}
.progress-item:last-child {
    margin-bottom: 0;
}
.progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}
.progress-label {
    font-size: 13px;
    color: #94A3B8;
}
.progress-value {
    font-size: 13px;
    color: #F8FAFC;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.progress-bar {
    height: 6px;
    background: #334155;
    border-radius: 3px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 3px;
    transition: width 0.5s ease;
}
.progress-fill.blue { background: linear-gradient(90deg, #6366F1, #818CF8); }
.progress-fill.red { background: linear-gradient(90deg, #EF4444, #F87171); }
.progress-fill.green { background: linear-gradient(90deg, #22C55E, #4ADE80); }
.progress-fill.gray { background: linear-gradient(90deg, #64748B, #94A3B8); }

/* 文档列表项 */
.doc-item {
    display: flex;
    align-items: center;
    padding: 12px 0;
    border-bottom: 1px solid #334155;
}
.doc-item:last-child {
    border-bottom: none;
}
.doc-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-right: 12px;
    flex-shrink: 0;
}
.doc-dot.blue { background: #3B82F6; }
.doc-dot.red { background: #EF4444; }
.doc-dot.green { background: #22C55E; }
.doc-dot.gray { background: #94A3B8; }
.doc-name {
    font-size: 13px;
    color: #94A3B8;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* 空状态 */
.empty-state {
    text-align: center;
    padding: 40px 20px;
}
.empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.4;
}
.empty-text {
    font-size: 13px;
    color: #64748B;
}

/* 状态卡片 */
.status-card {
    background: #1E293B;
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 20px 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}
.status-info h3 {
    font-size: 16px;
    font-weight: 600;
    color: #F8FAFC;
    margin: 0 0 4px 0;
}
.status-info p {
    font-size: 13px;
    color: #64748B;
    margin: 0;
}
.status-badge {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 16px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}
.status-badge.success {
    background: rgba(34, 197, 94, 0.15);
    color: #4ADE80;
}
.status-badge.warning {
    background: rgba(245, 158, 11, 0.15);
    color: #FCD34D;
}
.status-badge.neutral {
    background: rgba(100, 116, 139, 0.15);
    color: #94A3B8;
}
.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}
.status-badge.success .status-dot { background: #4ADE80; }
.status-badge.warning .status-dot { background: #FCD34D; }
.status-badge.neutral .status-dot { background: #94A3B8; }

/* 数据提取统计样式 */
.stat-item {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid #334155;
}
.stat-item:last-child {
    border-bottom: none;
}
.stat-icon {
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
}
.stat-info {
    flex: 1;
}
.stat-value {
    font-size: 18px;
    font-weight: 700;
    color: #F8FAFC;
    font-family: 'JetBrains Mono', monospace;
}
.stat-label {
    font-size: 12px;
    color: #64748B;
}

/* 关键词云样式 */
.keyword-cloud {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    padding: 12px 0;
}
.keyword-tag {
    background: rgba(99, 102, 241, 0.1);
    border: 1px solid rgba(99, 102, 241, 0.2);
    color: #818CF8;
    padding: 4px 12px;
    border-radius: 20px;
    white-space: nowrap;
    transition: all 0.2s ease;
}
.keyword-tag:hover {
    background: rgba(99, 102, 241, 0.2);
    transform: scale(1.05);
}

/* 论点分析样式 */
.argument-stats {
    margin: 16px 0;
}
.arg-stat-row {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 14px;
}
.arg-stat-label {
    width: 40px;
    font-size: 13px;
    font-weight: 500;
}
.arg-stat-bar {
    flex: 1;
    height: 8px;
    background: #334155;
    border-radius: 4px;
    overflow: hidden;
}
.arg-stat-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
}
.arg-stat-fill.pro { background: linear-gradient(90deg, #14B8A6, #2DD4BF); }
.arg-stat-fill.con { background: linear-gradient(90deg, #F59E0B, #FBBF24); }
.arg-stat-fill.neutral { background: linear-gradient(90deg, #A855F7, #C084FC); }
.arg-stat-value {
    width: 30px;
    text-align: right;
    font-size: 14px;
    font-weight: 600;
    color: #F8FAFC;
    font-family: 'JetBrains Mono', monospace;
}

.evidence-summary {
    text-align: center;
    padding: 16px;
    background: rgba(99, 102, 241, 0.1);
    border-radius: 10px;
    margin-top: 8px;
}
.evidence-count {
    font-size: 28px;
    font-weight: 700;
    color: #818CF8;
    font-family: 'JetBrains Mono', monospace;
}
.evidence-label {
    display: block;
    font-size: 12px;
    color: #64748B;
    margin-top: 4px;
}
</style>
''', unsafe_allow_html=True)


def get_dashboard_stats() -> dict:
    """获取仪表盘统计数据（增强版）"""
    cm = ContentManager()
    
    doc_count = st.session_state.get("doc_count", 0)
    index_count = st.session_state.get("index_count", 0)
    favorites_count = len(cm.get_all_favorites())
    arguments = cm.get_all_arguments()
    arguments_count = len(arguments)
    
    file_types = st.session_state.get("file_type_stats", {"docx": 0, "pdf": 0, "xlsx": 0, "txt": 0})
    recent_docs = st.session_state.get("recent_documents", [])
    
    # 增强：获取文档统计数据
    documents = st.session_state.get("documents", [])
    doc_stats = {}
    if documents:
        try:
            doc_stats = get_document_statistics(documents)
        except Exception:
            pass
    
    # 论点统计
    from app.models.argument import ArgumentSide
    pro_count = len([a for a in arguments if a.side == ArgumentSide.PRO])
    con_count = len([a for a in arguments if a.side == ArgumentSide.CON])
    neutral_count = len([a for a in arguments if a.side == ArgumentSide.NEUTRAL])
    total_evidences = sum(len(a.evidences) for a in arguments)
    
    return {
        "doc_count": doc_count,
        "index_count": index_count,
        "favorites_count": favorites_count,
        "arguments_count": arguments_count,
        "file_types": file_types,
        "recent_docs": recent_docs[:5],
        "last_index_time": st.session_state.get("last_index_time", None),
        # 增强数据
        "total_characters": doc_stats.get("total_characters", 0),
        "total_paragraphs": doc_stats.get("total_paragraphs", 0),
        "numeric_data_count": doc_stats.get("numeric_data_count", 0),
        "percentage_data_count": doc_stats.get("percentage_data_count", 0),
        "year_references_count": doc_stats.get("year_references_count", 0),
        "top_keywords": doc_stats.get("top_keywords", []),
        # 论点统计
        "pro_arguments": pro_count,
        "con_arguments": con_count,
        "neutral_arguments": neutral_count,
        "total_evidences": total_evidences,
    }


def render_metric_cards(stats: dict):
    """渲染核心指标卡片"""
    metrics_html = f'''
<div class="metric-grid">
    <div class="metric-card">
        <div class="metric-icon blue">📄</div>
        <div class="metric-value blue">{stats["doc_count"]}</div>
        <div class="metric-label">文档总数</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon green">🔍</div>
        <div class="metric-value green">{stats["index_count"]}</div>
        <div class="metric-label">索引项数</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon amber">⭐</div>
        <div class="metric-value amber">{stats["favorites_count"]}</div>
        <div class="metric-label">收藏数量</div>
    </div>
    <div class="metric-card">
        <div class="metric-icon pink">📑</div>
        <div class="metric-value pink">{stats["arguments_count"]}</div>
        <div class="metric-label">论点数量</div>
    </div>
</div>
'''
    st.markdown(metrics_html, unsafe_allow_html=True)


def render_file_type_distribution(stats: dict):
    """渲染文件类型分布"""
    file_types = stats["file_types"]
    
    word_count = file_types.get("docx", 0) + file_types.get("doc", 0)
    pdf_count = file_types.get("pdf", 0)
    excel_count = file_types.get("xlsx", 0) + file_types.get("xls", 0)
    txt_count = file_types.get("txt", 0)
    total = word_count + pdf_count + excel_count + txt_count or 1
    
    def calc_percent(count):
        return (count / total) * 100 if total > 0 else 0
    
    html = f'''<div class="panel-card" style="height: 340px; overflow: auto;">
<h3 class="panel-title"><span class="panel-icon">📁</span>文件类型分布</h3>
<div class="progress-item"><div class="progress-header"><span class="progress-label">Word 文档</span><span class="progress-value">{word_count}</span></div><div class="progress-bar"><div class="progress-fill blue" style="width: {calc_percent(word_count)}%;"></div></div></div>
<div class="progress-item"><div class="progress-header"><span class="progress-label">PDF 文档</span><span class="progress-value">{pdf_count}</span></div><div class="progress-bar"><div class="progress-fill red" style="width: {calc_percent(pdf_count)}%;"></div></div></div>
<div class="progress-item"><div class="progress-header"><span class="progress-label">Excel 表格</span><span class="progress-value">{excel_count}</span></div><div class="progress-bar"><div class="progress-fill green" style="width: {calc_percent(excel_count)}%;"></div></div></div>
<div class="progress-item"><div class="progress-header"><span class="progress-label">文本文件</span><span class="progress-value">{txt_count}</span></div><div class="progress-bar"><div class="progress-fill gray" style="width: {calc_percent(txt_count)}%;"></div></div></div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def render_recent_activity(stats: dict):
    """渲染最近文档"""
    recent_docs = stats.get("recent_docs", [])
    
    if recent_docs:
        items_html = ""
        for doc in recent_docs[:5]:
            file_name = doc.get("file_name", "未知文件")
            ext = file_name.split(".")[-1].lower() if "." in file_name else "txt"
            dot_class = {"docx": "blue", "doc": "blue", "pdf": "red", "xlsx": "green", "xls": "green"}.get(ext, "gray")
            display_name = file_name if len(file_name) <= 30 else file_name[:27] + "..."
            items_html += f'<div class="doc-item"><div class="doc-dot {dot_class}"></div><span class="doc-name">{display_name}</span></div>'
        content = items_html
    else:
        content = '<div class="empty-state"><div class="empty-icon">📭</div><div class="empty-text">暂无文档，请先导入文档库</div></div>'
    
    html = f'<div class="panel-card" style="height: 340px; overflow: auto;"><h3 class="panel-title"><span class="panel-icon">🕐</span>最近文档</h3>{content}</div>'
    st.markdown(html, unsafe_allow_html=True)


def render_data_extraction_stats(stats: dict):
    """渲染数据提取统计"""
    numeric_count = stats.get("numeric_data_count", 0)
    percentage_count = stats.get("percentage_data_count", 0)
    year_count = stats.get("year_references_count", 0)
    total_chars = stats.get("total_characters", 0)
    
    # 格式化字符数
    if total_chars >= 10000:
        chars_display = f"{total_chars / 10000:.1f}万"
    else:
        chars_display = str(total_chars)
    
    html = f'''<div class="panel-card" style="height: 340px; overflow: auto;">
<h3 class="panel-title"><span class="panel-icon">📊</span>数据提取统计</h3>
<div class="stat-item">
    <div class="stat-icon" style="background: rgba(99, 102, 241, 0.15);">📈</div>
    <div class="stat-info">
        <div class="stat-value">{numeric_count}</div>
        <div class="stat-label">数值数据</div>
    </div>
</div>
<div class="stat-item">
    <div class="stat-icon" style="background: rgba(236, 72, 153, 0.15);">📉</div>
    <div class="stat-info">
        <div class="stat-value">{percentage_count}</div>
        <div class="stat-label">百分比数据</div>
    </div>
</div>
<div class="stat-item">
    <div class="stat-icon" style="background: rgba(34, 197, 94, 0.15);">📅</div>
    <div class="stat-info">
        <div class="stat-value">{year_count}</div>
        <div class="stat-label">年份引用</div>
    </div>
</div>
<div class="stat-item">
    <div class="stat-icon" style="background: rgba(245, 158, 11, 0.15);">📝</div>
    <div class="stat-info">
        <div class="stat-value">{chars_display}</div>
        <div class="stat-label">总字符数</div>
    </div>
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def render_keyword_cloud(stats: dict):
    """渲染关键词云"""
    keywords = stats.get("top_keywords", [])
    
    if keywords:
        # 构建关键词 HTML
        max_count = max(count for _, count in keywords) if keywords else 1
        keywords_html = ""
        for kw, count in keywords[:15]:
            # 根据频率调整大小
            size = 12 + int((count / max_count) * 10)
            opacity = 0.5 + (count / max_count) * 0.5
            keywords_html += f'<span class="keyword-tag" style="font-size: {size}px; opacity: {opacity};">{kw}</span>'
        
        content = f'<div class="keyword-cloud">{keywords_html}</div>'
    else:
        content = '<div class="empty-state"><div class="empty-icon">🔤</div><div class="empty-text">暂无关键词数据</div></div>'
    
    html = f'''<div class="panel-card" style="height: 340px; overflow: auto;">
<h3 class="panel-title"><span class="panel-icon">🏷️</span>热门关键词</h3>
{content}
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def render_argument_analysis(stats: dict):
    """渲染论点分析"""
    pro = stats.get("pro_arguments", 0)
    con = stats.get("con_arguments", 0)
    neutral = stats.get("neutral_arguments", 0)
    evidences = stats.get("total_evidences", 0)
    total = pro + con + neutral
    
    # 计算百分比
    pro_pct = (pro / total * 100) if total > 0 else 0
    con_pct = (con / total * 100) if total > 0 else 0
    
    html = f'''<div class="panel-card" style="height: 340px; overflow: auto;">
<h3 class="panel-title"><span class="panel-icon">⚖️</span>论点分析</h3>
<div class="argument-stats">
    <div class="arg-stat-row">
        <span class="arg-stat-label" style="color: #14B8A6;">正方</span>
        <div class="arg-stat-bar">
            <div class="arg-stat-fill pro" style="width: {pro_pct}%;"></div>
        </div>
        <span class="arg-stat-value">{pro}</span>
    </div>
    <div class="arg-stat-row">
        <span class="arg-stat-label" style="color: #F59E0B;">反方</span>
        <div class="arg-stat-bar">
            <div class="arg-stat-fill con" style="width: {con_pct}%;"></div>
        </div>
        <span class="arg-stat-value">{con}</span>
    </div>
    <div class="arg-stat-row">
        <span class="arg-stat-label" style="color: #A855F7;">中立</span>
        <div class="arg-stat-bar">
            <div class="arg-stat-fill neutral" style="width: {(neutral / total * 100) if total > 0 else 0}%;"></div>
        </div>
        <span class="arg-stat-value">{neutral}</span>
    </div>
</div>
<div class="evidence-summary">
    <span class="evidence-count">{total}</span>
    <span class="evidence-label">个论点 · {evidences} 条论据</span>
</div>
</div>'''
    st.markdown(html, unsafe_allow_html=True)


def render_index_status(stats: dict):
    """渲染索引状态"""
    last_index_time = stats.get("last_index_time")
    index_count = stats["index_count"]
    doc_count = stats["doc_count"]
    
    if doc_count > 0 and index_count > 0:
        badge_class = "success"
        status_text = "索引正常"
    elif doc_count > 0 and index_count == 0:
        badge_class = "warning"
        status_text = "需要重建索引"
    else:
        badge_class = "neutral"
        status_text = "暂无数据"
    
    time_str = last_index_time.strftime("%Y-%m-%d %H:%M") if last_index_time else "从未"
    
    html = f'''
<div class="status-card">
    <div class="status-info">
        <h3>🗂️ 索引状态</h3>
        <p>上次索引时间：{time_str}</p>
    </div>
    <div class="status-badge {badge_class}">
        <div class="status-dot"></div>
        <span>{status_text}</span>
    </div>
</div>
'''
    st.markdown(html, unsafe_allow_html=True)


def render_demo_data_banner():
    """渲染演示数据提示横幅"""
    # 检查是否处于演示模式
    documents = st.session_state.get("documents", [])
    is_demo_mode = False
    
    # 如果文档列表中有演示数据的特征
    if documents and not DISABLE_DEMO_DATA:
        demo_file_names = [
            "2024年中国青年就业报告.pdf",
            "新能源汽车产业分析.docx",
            "人工智能伦理问题研究.docx"
        ]
        for doc in documents[:5]:
            if doc.file_name in demo_file_names:
                is_demo_mode = True
                break
    
    if is_demo_mode:
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, rgba(245,158,11,0.15) 0%, rgba(251,191,36,0.1) 100%);
            border: 1px solid rgba(245,158,11,0.4);
            border-radius: 12px;
            padding: 16px 20px;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            gap: 12px;
        ">
            <span style="font-size: 24px;">⚠️</span>
            <div>
                <div style="color: #F59E0B; font-size: 14px; font-weight: 600; margin-bottom: 4px;">
                    当前显示的是演示数据
                </div>
                <div style="color: #94A3B8; font-size: 13px; line-height: 1.5;">
                    这些数据为预设的模拟内容，仅用于展示系统功能。
                    请将真实文档放入 <code style="background:#334155;padding:2px 6px;border-radius:4px;">documents/</code> 目录并点击"扫描目录"来使用真实数据。
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # 添加快速操作按钮
        col1, col2, col3 = st.columns([1, 1, 4])
        with col1:
            if st.button("📂 前往文档库", key="goto_docs"):
                st.session_state.current_page = "documents"
                st.rerun()
        with col2:
            if st.button("🗑️ 清除演示数据", key="clear_demo"):
                st.session_state.documents = []
                st.session_state.doc_count = 0
                st.session_state.index_count = 0
                st.session_state.demo_data_initialized = False
                from app.services.search_engine import SearchEngine
                SearchEngine().clear_index()
                st.toast("演示数据已清除", icon="🗑️")
                st.rerun()
