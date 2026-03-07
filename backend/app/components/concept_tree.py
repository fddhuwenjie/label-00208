"""概念树可视化组件 - 展示概念-子概念树状结构"""

import streamlit as st
import html


def render_concept_tree(tree: dict, on_concept_click: callable = None):
    """
    渲染概念树
    
    Args:
        tree: 概念树数据结构 {"keyword": str, "children": [{"keyword": str, "score": float, "children": [...]}]}
        on_concept_click: 点击概念时的回调函数
    """
    if not tree or not tree.get("keyword"):
        return
    
    inject_concept_tree_styles()
    
    root_keyword = html.escape(tree.get("keyword", ""))
    children = tree.get("children", [])
    
    # 渲染根节点
    st.markdown(f"""
    <div class="concept-tree-container">
        <div class="concept-tree-header">
            <span class="concept-tree-icon">🌳</span>
            <span class="concept-tree-title">概念联想树</span>
        </div>
        <div class="concept-root">
            <span class="concept-root-label">{root_keyword}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if not children:
        st.info("暂无相关子概念，请尝试其他关键词")
        return
    
    # 渲染子概念
    for i, child in enumerate(children[:8]):
        child_keyword = html.escape(child.get("keyword", ""))
        child_score = child.get("score", 0)
        sub_children = child.get("children", [])
        
        # 根据分数确定颜色
        if child_score >= 0.7:
            color = "#22C55E"  # 绿色 - 高相关
        elif child_score >= 0.5:
            color = "#3B82F6"  # 蓝色 - 中相关
        else:
            color = "#94A3B8"  # 灰色 - 低相关
        
        with st.expander(f"📌 {child_keyword} ({child_score:.0%})", expanded=False):
            # 子概念操作
            col1, col2 = st.columns([1, 4])
            with col1:
                if st.button("🔍 搜索", key=f"search_concept_{i}", help=f"搜索「{child_keyword}」"):
                    st.session_state.pending_search_query = child_keyword
                    st.session_state.auto_search = True
                    st.rerun()
            
            # 显示子子概念
            if sub_children:
                st.markdown(f"""
                <div style="color:#64748B;font-size:12px;margin-bottom:8px;">相关延伸概念:</div>
                """, unsafe_allow_html=True)
                
                sub_concepts_html = ""
                for sub in sub_children[:6]:
                    sub_kw = html.escape(sub.get("keyword", ""))
                    sub_score = sub.get("score", 0)
                    sub_concepts_html += f"""
                    <span style="
                        display:inline-block;
                        background:rgba(99,102,241,0.1);
                        border:1px solid rgba(99,102,241,0.3);
                        padding:4px 10px;
                        border-radius:6px;
                        margin:4px;
                        font-size:12px;
                        color:#94A3B8;
                    ">{sub_kw} <span style="color:#64748B;">({sub_score:.0%})</span></span>
                    """
                
                st.markdown(f'<div style="display:flex;flex-wrap:wrap;gap:4px;">{sub_concepts_html}</div>', unsafe_allow_html=True)
            else:
                st.caption("暂无更深层延伸概念")


def render_concept_tree_compact(tree: dict):
    """渲染紧凑版概念树（用于搜索结果侧边栏）"""
    if not tree or not tree.get("keyword"):
        return
    
    children = tree.get("children", [])
    if not children:
        return
    
    st.markdown("""
    <div style="
        background:rgba(99,102,241,0.05);
        border:1px solid rgba(99,102,241,0.2);
        border-radius:12px;
        padding:16px;
        margin-top:16px;
    ">
        <div style="color:#818CF8;font-size:13px;font-weight:600;margin-bottom:12px;">
            🌳 概念联想树
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    for i, child in enumerate(children[:5]):
        child_keyword = child.get("keyword", "")
        child_score = child.get("score", 0)
        sub_children = child.get("children", [])
        
        # 构建子概念标签
        sub_tags = ""
        if sub_children:
            sub_tags = " → " + ", ".join([s.get("keyword", "") for s in sub_children[:3]])
        
        if st.button(f"📌 {child_keyword} ({child_score:.0%}){sub_tags}", key=f"tree_btn_{i}"):
            st.session_state.pending_search_query = child_keyword
            st.session_state.auto_search = True
            st.rerun()


def inject_concept_tree_styles():
    """注入概念树样式"""
    st.markdown("""
    <style>
    .concept-tree-container {
        background: linear-gradient(135deg, rgba(99,102,241,0.08) 0%, rgba(139,92,246,0.08) 100%);
        border: 1px solid rgba(99,102,241,0.2);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 16px;
    }
    .concept-tree-header {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 16px;
    }
    .concept-tree-icon {
        font-size: 20px;
    }
    .concept-tree-title {
        color: #818CF8;
        font-size: 14px;
        font-weight: 600;
    }
    .concept-root {
        text-align: center;
        margin-bottom: 16px;
    }
    .concept-root-label {
        display: inline-block;
        background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
        color: white;
        padding: 12px 24px;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(99,102,241,0.3);
    }
    </style>
    """, unsafe_allow_html=True)
