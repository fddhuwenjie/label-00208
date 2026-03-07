"""自定义 CSS 样式"""


def get_custom_css() -> str:
    """获取自定义 CSS"""
    return """
<style>
    /* Google Fonts 导入 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    /* 全局字体 */
    html, body, [class*="css"] {
        font-family: 'Noto Sans SC', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 主背景 */
    .stApp {
        background-color: #0F172A;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: #0F172A;
        border-right: 1px solid #334155;
    }
    
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: #F8FAFC;
    }
    
    /* 搜索框样式 */
    .stTextInput > div > div > input {
        background-color: #1E293B !important;
        border: 1px solid #334155 !important;
        border-radius: 12px !important;
        color: #F8FAFC !important;
        font-size: 16px !important;
        padding: 12px 16px !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #6366F1 !important;
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #64748B !important;
    }
    
    /* 按钮样式 - 紧凑设计 */
    .stButton > button {
        background-color: #6366F1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        min-height: 40px !important;
        max-height: 44px !important;
        line-height: 1.2 !important;
        transition: all 150ms ease !important;
    }
    
    .stButton > button:hover {
        background-color: #818CF8 !important;
        transform: translateY(-1px);
    }
    
    /* 下载按钮样式 */
    .stDownloadButton > button {
        background-color: #6366F1 !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 20px !important;
        font-weight: 500 !important;
        font-size: 14px !important;
        min-height: 40px !important;
        max-height: 44px !important;
        line-height: 1.2 !important;
        transition: all 150ms ease !important;
    }
    
    .stDownloadButton > button:hover {
        background-color: #818CF8 !important;
        transform: translateY(-1px);
    }
    
    /* 次要按钮 */
    .stButton > button[kind="secondary"],
    [data-testid="stButton"] button[kind="secondary"] {
        background-color: transparent !important;
        border: 1px solid #334155 !important;
        color: #94A3B8 !important;
    }
    
    .stButton > button[kind="secondary"]:hover,
    [data-testid="stButton"] button[kind="secondary"]:hover {
        background-color: #334155 !important;
        color: #F8FAFC !important;
    }
    
    /* 图标按钮（单字符/emoji） */
    .stButton > button:has(span:only-child) {
        min-width: 44px !important;
        padding: 10px !important;
    }
    
    /* 结果卡片 */
    .result-card {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        transition: border-color 200ms ease;
    }
    
    .result-card:hover {
        border-color: #6366F1;
        cursor: pointer;
    }
    
    .result-card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 12px;
    }
    
    .result-card-title {
        color: #F8FAFC;
        font-weight: 500;
        font-size: 16px;
    }
    
    .result-card-content {
        color: #94A3B8;
        font-size: 14px;
        line-height: 1.6;
    }
    
    .result-card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #334155;
        color: #64748B;
        font-size: 12px;
    }
    
    /* 高亮文本 */
    mark {
        background-color: rgba(34, 197, 94, 0.3);
        color: #22C55E;
        padding: 2px 4px;
        border-radius: 4px;
    }
    
    /* 标签 */
    .tag {
        display: inline-block;
        background-color: #334155;
        color: #94A3B8;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 12px;
        margin-right: 8px;
        margin-bottom: 4px;
    }
    
    .tag:hover {
        background-color: #4338CA;
        color: #F8FAFC;
        cursor: pointer;
    }
    
    /* 语义联想标签 */
    .semantic-tag {
        display: inline-block;
        background-color: rgba(99, 102, 241, 0.2);
        color: #818CF8;
        padding: 6px 14px;
        border-radius: 9999px;
        font-size: 14px;
        margin: 4px;
        cursor: pointer;
        transition: all 150ms ease;
        border: 1px solid transparent;
    }
    
    .semantic-tag:hover {
        background-color: #6366F1;
        color: white;
    }
    
    /* 文件类型图标 */
    .file-type-icon {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 8px;
        font-size: 14px;
        font-weight: 600;
        margin-right: 12px;
    }
    
    .file-type-docx { background-color: #2563EB20; color: #3B82F6; }
    .file-type-pdf { background-color: #EF444420; color: #EF4444; }
    .file-type-xlsx { background-color: #22C55E20; color: #22C55E; }
    .file-type-txt { background-color: #64748B20; color: #94A3B8; }
    
    /* 进度条 */
    .score-bar {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .score-bar-bg {
        flex: 1;
        height: 6px;
        background-color: #334155;
        border-radius: 3px;
        overflow: hidden;
    }
    
    .score-bar-fill {
        height: 100%;
        background: linear-gradient(90deg, #6366F1, #22C55E);
        border-radius: 3px;
        transition: width 300ms ease;
    }
    
    /* 分隔线 */
    hr {
        border: none;
        border-top: 1px solid #334155;
        margin: 20px 0;
    }
    
    /* 统计数字 */
    .stat-number {
        font-size: 32px;
        font-weight: 700;
        color: #F8FAFC;
        font-family: 'JetBrains Mono', monospace;
    }
    
    .stat-label {
        font-size: 14px;
        color: #64748B;
        margin-top: 4px;
    }
    
    /* 空状态 */
    .empty-state {
        text-align: center;
        padding: 48px 24px;
        color: #64748B;
    }
    
    .empty-state-icon {
        font-size: 48px;
        margin-bottom: 16px;
        opacity: 0.5;
    }
    
    /* 加载状态 */
    .loading-spinner {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 32px;
        color: #6366F1;
    }
    
    /* 正方/反方标记 */
    .pro-badge {
        background-color: rgba(20, 184, 166, 0.2);
        color: #14B8A6;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .con-badge {
        background-color: rgba(245, 158, 11, 0.2);
        color: #F59E0B;
        padding: 4px 10px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: 500;
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 侧边栏折叠按钮：X 改为向左箭头 */
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button {
        background: transparent !important;
        border: none !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button svg {
        display: none !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button::before {
        content: "←";
        font-size: 20px;
        color: #94A3B8;
        font-weight: bold;
    }
    
    [data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"] button:hover::before {
        color: #F8FAFC;
    }
    
    /* 展开按钮样式：向右箭头 */
    [data-testid="collapsedControl"] button svg {
        display: none !important;
    }
    
    [data-testid="collapsedControl"] button::before {
        content: "→";
        font-size: 20px;
        color: #94A3B8;
        font-weight: bold;
    }
    
    [data-testid="collapsedControl"] button:hover::before {
        color: #6366F1;
    }
    
    /* 自定义滚动条 */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #1E293B;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #334155;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #475569;
    }
</style>
"""


def inject_custom_css():
    """注入自定义 CSS 到 Streamlit"""
    import streamlit as st
    st.markdown(get_custom_css(), unsafe_allow_html=True)
