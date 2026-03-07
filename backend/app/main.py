"""DebatePrep - 主入口"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

from app.config import PAGE_TITLE, PAGE_ICON
from app.components.styles import inject_custom_css
from app.components.sidebar import render_sidebar
from app.views.dashboard_page import render_dashboard_page
from app.views.search_page import render_search_page
from app.views.documents_page import render_documents_page
from app.views.favorites_page import render_favorites_page
from app.views.tags_page import render_tags_page
from app.views.arguments_page import render_arguments_page
from app.views.export_page import render_export_page
from app.views.settings_page import render_settings_page
from app.utils.init_data import init_demo_data
from app.utils.logger import app_logger as logger


# 页面配置
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """主函数"""
    # 初始化示例数据
    init_demo_data()
    
    # 注入自定义样式
    inject_custom_css()
    
    # 渲染侧边栏
    render_sidebar()
    
    # 根据当前页面渲染内容
    current_page = st.session_state.get("current_page", "dashboard")
    
    page_renderers = {
        "dashboard": render_dashboard_page,
        "search": render_search_page,
        "documents": render_documents_page,
        "favorites": render_favorites_page,
        "tags": render_tags_page,
        "arguments": render_arguments_page,
        "export": render_export_page,
        "settings": render_settings_page,
    }
    
    renderer = page_renderers.get(current_page, render_search_page)
    renderer()
    
    # 启动成功日志
    print_startup_message()


def print_startup_message():
    """打印启动成功消息（仅在首次加载时）"""
    if "startup_logged" not in st.session_state:
        st.session_state.startup_logged = True
        logger.info("=" * 60)
        logger.info("✅ Startup Success")
        logger.info("🌐 Frontend: http://localhost:8501")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
