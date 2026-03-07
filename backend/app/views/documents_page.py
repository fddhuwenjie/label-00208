"""文档库页面"""

import streamlit as st
from pathlib import Path
import os

from app.services.document_parser import DocumentScanner
from app.services.search_engine import SearchEngine
from app.services.content_manager import ContentManager
from app.utils.file_utils import format_file_size, scan_directory
from app.config import DOCUMENTS_DIR


def render_documents_page():
    """渲染文档库页面"""
    st.markdown("""
    <h1 style="color: #F8FAFC; font-size: 28px; font-weight: 600; margin-bottom: 8px;">
        📂 文档库
    </h1>
    <p style="color: #64748B; font-size: 14px; margin-bottom: 24px;">
        管理和扫描你的辩论素材文档
    </p>
    """, unsafe_allow_html=True)
    
    # 文档目录设置
    render_directory_settings()
    
    st.markdown("<hr style='border-color: #334155; margin: 24px 0;'>", unsafe_allow_html=True)
    
    # 文档列表
    render_document_list()


def render_directory_settings():
    """渲染目录设置"""
    col1, col2 = st.columns([4, 1])
    
    with col1:
        doc_dir = st.text_input(
            "文档目录路径",
            value=st.session_state.get("documents_dir", DOCUMENTS_DIR),
            placeholder="输入文档目录的绝对路径",
            key="doc_dir_input"
        )
    
    with col2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📂 扫描", type="primary"):
            scan_documents(doc_dir)
    
    # 保存目录设置
    st.session_state.documents_dir = doc_dir
    
    # 显示目录状态
    demo_docs = st.session_state.get("documents", [])
    if os.path.isdir(doc_dir):
        file_count = sum(1 for _ in scan_directory(doc_dir))
        if file_count > 0:
            st.success(f"✅ 目录有效，发现 {file_count} 个支持的文件")
        elif demo_docs:
            st.info(f"📚 演示模式：已加载 {len(demo_docs)} 个示例文档")
        else:
            st.info("📂 目录为空，请添加文档后点击扫描")
    elif doc_dir:
        if demo_docs:
            st.info(f"📚 演示模式：已加载 {len(demo_docs)} 个示例文档")
        else:
            st.warning("⚠️ 目录不存在，请检查路径")


def scan_documents(directory: str):
    """扫描文档目录"""
    if not os.path.isdir(directory):
        st.error("目录不存在")
        return
    
    scanner = DocumentScanner()
    engine = SearchEngine()
    
    # 进度条
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_callback(current, total, file_name):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"正在处理 ({current}/{total}): {file_name}")
    
    # 扫描文档
    with st.spinner("正在扫描文档..."):
        documents = scanner.scan_directory(directory, progress_callback=progress_callback)
    
    status_text.text(f"扫描完成，发现 {len(documents)} 个文档")
    
    # 建立索引
    status_text.text("正在建立索引...")
    
    def index_callback(current, total, file_name):
        progress = current / total
        progress_bar.progress(progress)
        status_text.text(f"正在索引 ({current}/{total}): {file_name}")
    
    indexed = engine.index_documents(documents, progress_callback=index_callback)
    
    progress_bar.progress(1.0)
    status_text.text(f"✅ 完成！成功索引 {indexed} 个文档")
    
    # 更新统计
    st.session_state.doc_count = len(documents)
    st.session_state.index_count = engine.get_document_count()
    st.session_state.documents = documents
    
    # 清除旧的搜索结果
    if "search_results" in st.session_state:
        del st.session_state.search_results
    
    st.success(f"🎉 扫描完成！已索引 {indexed} 个文档")


def render_document_list():
    """渲染文档列表"""
    documents = st.session_state.get("documents", [])
    
    if not documents:
        st.markdown("""
        <div style="
            text-align: center;
            padding: 48px 24px;
            background-color: #1E293B;
            border-radius: 12px;
            border: 1px dashed #334155;
        ">
            <div style="font-size: 48px; margin-bottom: 16px; opacity: 0.5;">📁</div>
            <div style="color: #94A3B8; font-size: 16px; margin-bottom: 8px;">
                文档库为空
            </div>
            <div style="color: #64748B; font-size: 14px;">
                请设置文档目录并点击"扫描目录"按钮
            </div>
        </div>
        """, unsafe_allow_html=True)
        return
    
    # 文档统计
    st.markdown(f"""
    <div style="
        display: flex;
        gap: 16px;
        margin-bottom: 20px;
    ">
        <div style="
            flex: 1;
            background-color: #1E293B;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        ">
            <div style="font-size: 28px; font-weight: 700; color: #F8FAFC; font-family: 'JetBrains Mono', monospace;">
                {len(documents)}
            </div>
            <div style="font-size: 12px; color: #64748B;">总文档数</div>
        </div>
        <div style="
            flex: 1;
            background-color: #1E293B;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        ">
            <div style="font-size: 28px; font-weight: 700; color: #3B82F6; font-family: 'JetBrains Mono', monospace;">
                {sum(1 for d in documents if d.file_type in ['docx', 'doc'])}
            </div>
            <div style="font-size: 12px; color: #64748B;">Word 文档</div>
        </div>
        <div style="
            flex: 1;
            background-color: #1E293B;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        ">
            <div style="font-size: 28px; font-weight: 700; color: #22C55E; font-family: 'JetBrains Mono', monospace;">
                {sum(1 for d in documents if d.file_type in ['xlsx', 'xls'])}
            </div>
            <div style="font-size: 12px; color: #64748B;">Excel 文档</div>
        </div>
        <div style="
            flex: 1;
            background-color: #1E293B;
            border-radius: 12px;
            padding: 16px;
            text-align: center;
        ">
            <div style="font-size: 28px; font-weight: 700; color: #EF4444; font-family: 'JetBrains Mono', monospace;">
                {sum(1 for d in documents if d.file_type == 'pdf')}
            </div>
            <div style="font-size: 12px; color: #64748B;">PDF 文档</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # 文档列表
    st.markdown("""
<div style="color: #64748B; font-size: 14px; margin-bottom: 12px;">文档列表（点击展开查看内容，点击 ⭐ 收藏段落）</div>
""", unsafe_allow_html=True)
    
    # 获取 content_manager
    cm = ContentManager()
    
    for idx, doc in enumerate(documents[:50]):  # 最多显示50个
        icon = {"docx": "📄", "doc": "📄", "xlsx": "📊", "xls": "📊", "pdf": "📕", "txt": "📝"}.get(doc.file_type, "📄")
        
        # 获取文档已有标签
        doc_tags = cm.get_document_tags(doc.id)
        tag_badges = " ".join([f'<span style="background:{t.color}20;color:{t.color};padding:2px 6px;border-radius:4px;font-size:11px;margin-left:4px;">{t.name}</span>' for t in doc_tags])
        
        with st.expander(f"{icon} {doc.file_name} ({doc.paragraph_count} 段落 · {format_file_size(doc.file_size)})"):
            # 文档操作栏
            action_col1, action_col2, action_col3 = st.columns([1, 1, 4])
            with action_col1:
                if st.button("🏷️ 自动标签", key=f"auto_tag_{idx}", help="AI 自动为文档推荐标签"):
                    # 使用全文进行标签推荐
                    suggestions = cm.suggest_tags_for_content(doc.full_text, max_suggestions=5)
                    if suggestions:
                        st.session_state[f"tag_suggestions_{doc.id}"] = suggestions
                    else:
                        st.warning("未找到匹配的标签，请先创建相关标签")
            
            with action_col2:
                if st.button("🏷️ 一键标记", key=f"apply_tag_{idx}", help="自动应用推荐标签"):
                    added = cm.auto_tag_content(doc.id, doc.full_text, threshold=0.3)
                    if added:
                        st.toast(f"已添加 {len(added)} 个标签", icon="🏷️")
                        st.rerun()
                    else:
                        st.warning("未找到匹配的标签")
            
            # 显示标签推荐结果
            if f"tag_suggestions_{doc.id}" in st.session_state:
                suggestions = st.session_state[f"tag_suggestions_{doc.id}"]
                st.markdown("""
<div style="background:rgba(99,102,241,0.1);border:1px solid rgba(99,102,241,0.3);border-radius:8px;padding:12px;margin:8px 0;">
<div style="color:#818CF8;font-size:12px;font-weight:600;margin-bottom:8px;">🤖 AI 推荐标签</div>
</div>
""", unsafe_allow_html=True)
                for tag, score in suggestions:
                    tag_col1, tag_col2 = st.columns([4, 1])
                    with tag_col1:
                        st.markdown(f'<span style="color:{tag.color};">{tag.name}</span> <span style="color:#64748B;font-size:12px;">（匹配度: {score:.2f}）</span>', unsafe_allow_html=True)
                    with tag_col2:
                        if st.button("添加", key=f"add_tag_{doc.id}_{tag.id}"):
                            cm.add_tag_to_document(doc.id, tag.id)
                            del st.session_state[f"tag_suggestions_{doc.id}"]
                            st.toast(f"已添加标签: {tag.name}", icon="🏷️")
                            st.rerun()
            
            # 显示已有标签
            if doc_tags:
                st.markdown(f'<div style="margin:8px 0;"><span style="color:#64748B;font-size:12px;">已有标签:</span>{tag_badges}</div>', unsafe_allow_html=True)
            
            if doc.paragraphs:
                for para_idx, para in enumerate(doc.paragraphs[:10]):
                    col1, col2 = st.columns([12, 1])
                    
                    with col1:
                        st.markdown(f"""
<div style="background:#0F172A;padding:12px;border-radius:8px;border-left:3px solid #6366F1;">
<div style="color:#64748B;font-size:11px;margin-bottom:4px;">段落 {para_idx + 1}</div>
<div style="color:#94A3B8;font-size:14px;line-height:1.6;">{para.content}</div>
</div>
""", unsafe_allow_html=True)
                    
                    with col2:
                        if st.button("⭐", key=f"fav_doc_{idx}_{para_idx}", help="收藏此段落"):
                            cm.add_favorite(
                                document_id=doc.id,
                                file_name=doc.file_name,
                                content=para.content,
                                paragraph_index=para.paragraph_index,
                                page_number=para.page_number or 0
                            )
                            st.toast("已添加到收藏夹", icon="⭐")
                            st.rerun()
                
                if len(doc.paragraphs) > 10:
                    st.caption(f"还有 {len(doc.paragraphs) - 10} 个段落未显示")
            else:
                st.info("无段落内容")
    
    if len(documents) > 50:
        st.info(f"还有 {len(documents) - 50} 个文档未显示")
