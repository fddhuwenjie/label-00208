"""
数据初始化模块 - 初始化演示数据

⚠️ 重要说明：
本模块包含的所有数据均为 **演示/示例数据**，仅用于：
1. 首次启动时展示系统功能
2. 开发和测试环境的数据填充
3. 用户体验演示

这些数据并非来自真实文档解析，而是硬编码的模拟数据。
在生产环境中，用户应将真实文档放入 documents/ 目录，
系统会自动解析并替换这些演示数据。

演示数据包括：
- 12 份模拟文档（涵盖就业、科技、环境等主题）
- 6 个预设标签
- 3 条示例收藏
- 3 个示例论点及论据

禁用演示数据：
设置环境变量 DISABLE_DEMO_DATA=true 可禁用演示数据加载
"""

import streamlit as st
from datetime import datetime, timedelta
import random
import uuid

from app.config import DISABLE_DEMO_DATA
from app.services.content_manager import ContentManager
from app.services.search_engine import SearchEngine
from app.models.argument import ArgumentSide
from app.models.document import Document, DocumentParagraph
from app.utils.logger import app_logger as logger


def init_demo_data():
    """
    初始化演示数据（仅首次运行时执行）
    
    ⚠️ 注意：此函数加载的是演示数据，非真实文档。
    用户上传真实文档后，搜索结果将包含真实内容。
    
    可通过环境变量 DISABLE_DEMO_DATA=true 禁用演示数据加载。
    """
    if st.session_state.get("demo_data_initialized", False):
        return
    
    # 检查是否禁用演示数据
    if DISABLE_DEMO_DATA:
        logger.info("⏭️ 演示数据已禁用（DISABLE_DEMO_DATA=true）")
        st.session_state.demo_data_initialized = True
        st.session_state.doc_count = 0
        st.session_state.index_count = 0
        return
    
    # 初始化文档统计（演示数据）
    init_document_stats()
    
    # 初始化模拟文档库（检查索引是否已存在）
    init_demo_documents()
    
    # 初始化数据库演示数据
    init_database_data()
    
    st.session_state.demo_data_initialized = True
    logger.info("✅ 示例数据初始化完成")


def init_document_stats():
    """
    初始化文档统计数据
    
    ⚠️ 演示数据：以下统计数据为模拟值，
    真实统计将在用户上传文档后自动更新。
    """
    # [演示数据] 文件类型分布
    st.session_state.file_type_stats = {
        "docx": 5,
        "doc": 1,
        "pdf": 3,
        "xlsx": 2,
        "xls": 0,
        "txt": 1
    }
    
    # 上次索引时间
    st.session_state.last_index_time = datetime.now() - timedelta(hours=2)


def init_demo_documents():
    """
    初始化模拟文档库数据
    
    ⚠️ 演示数据：以下文档数据为硬编码的模拟数据，
    用于演示系统的搜索和分析功能。真实使用时，
    用户应将文档放入 documents/ 目录，系统会自动解析。
    """
    # 检查 session_state 是否已有文档数据
    if st.session_state.get("documents"):
        return
    
    # 检查索引是否已存在数据
    engine = SearchEngine()
    existing_count = engine.get_document_count()
    skip_indexing = existing_count > 0
    
    # ========== [演示数据] 模拟文档列表 ==========
    # 包含 12 份模拟文档，涵盖以下主题：
    # - 就业与劳动力市场
    # - 新能源与环保
    # - 人工智能与科技
    # - 教育与社会公平
    # - 经济与数字化转型
    demo_docs_data = [
        {
            "file_name": "2024年中国青年就业报告.pdf",
            "file_type": "pdf",
            "file_size": 2457600,
            "paragraphs": [
                "根据调查显示，2024年应届毕业生中，有67.8%选择进入民营企业就业，较去年提升5.2个百分点。",
                "灵活就业比例达到15.3%，反映出年轻人就业观念的变化。",
                "一线城市就业意愿下降，二三线城市吸引力增强。",
            ],
            "page_count": 45
        },
        {
            "file_name": "新能源汽车产业分析.docx",
            "file_type": "docx",
            "file_size": 1843200,
            "paragraphs": [
                "截至2024年第三季度，中国新能源汽车保有量突破2000万辆，渗透率达到38.6%。",
                "动力电池技术持续突破，固态电池商业化进程加速。",
                "充电基础设施建设快速推进，全国充电桩数量超过500万个。",
                "主要车企纷纷发布智能驾驶战略，L2+级别辅助驾驶普及率提升。",
            ],
            "page_count": 28
        },
        {
            "file_name": "人工智能伦理问题研究.docx",
            "file_type": "docx",
            "file_size": 1024000,
            "paragraphs": [
                "AI决策的可解释性问题日益突出。研究表明，在医疗诊断、金融信贷等高风险场景中，85%的受访者认为了解AI决策依据非常重要。",
                "算法偏见是当前AI伦理面临的核心挑战之一。",
                "数据隐私保护与AI发展之间存在张力。",
            ],
            "page_count": 22
        },
        {
            "file_name": "全球气候变化数据汇总.xlsx",
            "file_type": "xlsx",
            "file_size": 512000,
            "paragraphs": [
                "2023年全球平均气温较工业化前上升1.2°C，创历史新高。",
                "北极海冰面积持续缩小，夏季最小值再创纪录。",
            ],
            "page_count": 15
        },
        {
            "file_name": "教育公平政策梳理.pdf",
            "file_type": "pdf",
            "file_size": 1536000,
            "paragraphs": [
                "义务教育均衡发展取得显著成效，城乡差距逐步缩小。",
                "高考改革持续深化，综合素质评价纳入录取参考。",
                "职业教育地位提升，产教融合模式不断创新。",
            ],
            "page_count": 35
        },
        {
            "file_name": "世界经济论坛报告2024.pdf",
            "file_type": "pdf",
            "file_size": 3072000,
            "paragraphs": [
                "世界经济论坛预测，到2025年AI将创造9700万个新工作岗位，同时取代8500万个岗位，净增1200万个就业机会。",
                "数字化转型成为企业核心战略，超过80%的企业加大数字化投入。",
                "绿色经济成为新增长点，可持续发展理念深入人心。",
            ],
            "page_count": 120
        },
        {
            "file_name": "麦肯锡全球研究院报告.docx",
            "file_type": "docx",
            "file_size": 2048000,
            "paragraphs": [
                "历史数据显示，自动化技术每取代1个岗位，平均创造1.3个新岗位，且新岗位薪资水平通常更高。",
                "技能转型成为劳动者面临的主要挑战。",
                "企业需要重新思考人才战略，建立持续学习文化。",
            ],
            "page_count": 85
        },
        {
            "file_name": "劳动力市场分析.docx",
            "file_type": "docx",
            "file_size": 768000,
            "paragraphs": [
                "研究显示，受AI影响最大的是重复性工作岗位，这些岗位的从业者往往缺乏快速转型所需的技能和资源。",
                "服务业就业持续增长，制造业就业结构优化。",
            ],
            "page_count": 18
        },
        {
            "file_name": "社会公平研究报告.docx",
            "file_type": "docx",
            "file_size": 1280000,
            "paragraphs": [
                "低收入群体再就业周期平均为18个月，是高收入群体的3倍，技术变革加剧社会不平等。",
                "教育资源分配不均是社会流动性下降的重要原因。",
                "社会保障体系需要适应新就业形态的发展。",
            ],
            "page_count": 42
        },
        {
            "file_name": "碳排放研究数据.xlsx",
            "file_type": "xlsx",
            "file_size": 384000,
            "paragraphs": [
                "生命周期分析表明，电动汽车全生命周期碳排放比燃油车低40%-60%，且随着电网清洁化比例提升，这一优势将进一步扩大。",
                "工业部门碳排放占比最高，达到40%以上。",
            ],
            "page_count": 8
        },
        {
            "file_name": "技术发展趋势报告.txt",
            "file_type": "txt",
            "file_size": 128000,
            "paragraphs": [
                "大语言模型技术快速迭代，应用场景不断拓展。",
                "量子计算取得突破性进展，商用化进程加速。",
            ],
            "page_count": 1
        },
        {
            "file_name": "数字经济白皮书.doc",
            "file_type": "doc",
            "file_size": 1920000,
            "paragraphs": [
                "数字经济规模持续扩大，占GDP比重超过40%。",
                "数字基础设施建设加速，5G网络覆盖率大幅提升。",
                "数字化转型成为传统产业升级的重要路径。",
            ],
            "page_count": 55
        },
    ]
    
    # 创建 Document 对象列表
    documents = []
    for doc_data in demo_docs_data:
        doc_id = str(uuid.uuid4())
        paragraphs = [
            DocumentParagraph(
                content=p,
                paragraph_index=i,
                page_number=i // 3 + 1
            )
            for i, p in enumerate(doc_data["paragraphs"])
        ]
        
        doc = Document(
            id=doc_id,
            file_path=f"/app/documents/{doc_data['file_name']}",
            file_name=doc_data["file_name"],
            file_type=doc_data["file_type"],
            file_size=doc_data["file_size"],
            paragraphs=paragraphs,
            full_text="\n\n".join(doc_data["paragraphs"]),
            page_count=doc_data.get("page_count", len(paragraphs))
        )
        documents.append(doc)
    
    # 存储到 session_state
    st.session_state.documents = documents
    st.session_state.doc_count = len(documents)
    
    # 建立搜索索引（如果尚未索引）
    if not skip_indexing:
        indexed_count = engine.index_documents(documents)
    st.session_state.index_count = engine.get_document_count()
    
    # 最近文档列表
    st.session_state.recent_documents = [
        {"file_name": doc.file_name, "file_type": doc.file_type}
        for doc in documents[:5]
    ]


def init_database_data():
    """
    初始化数据库演示数据
    
    ⚠️ 演示数据：以下标签、收藏、论点均为预设的演示数据，
    用于展示系统的标签管理、收藏和论点整理功能。
    用户可以自行创建、修改或删除这些数据。
    
    演示数据包括：
    - 6 个预设标签（经济、社会、教育、科技、环境、政策）
    - 3 条示例收藏
    - 3 个示例论点及对应论据
    """
    cm = ContentManager()
    
    # 检查是否已有数据，避免重复初始化
    if cm.get_all_tags() or cm.get_all_favorites() or cm.get_all_arguments():
        return
    
    # 创建示例标签
    tags_data = [
        ("经济", "#3B82F6"),
        ("社会", "#22C55E"),
        ("教育", "#F59E0B"),
        ("科技", "#8B5CF6"),
        ("环境", "#10B981"),
        ("政策", "#EC4899"),
    ]
    
    tags = {}
    for name, color in tags_data:
        tag = cm.create_tag(name, color)
        if tag:
            tags[name] = tag
    
    # 创建示例收藏
    favorites_data = [
        {
            "document_id": "doc_001",
            "file_name": "2024年中国青年就业报告.pdf",
            "content": "根据调查显示，2024年应届毕业生中，有67.8%选择进入民营企业就业，较去年提升5.2个百分点。同时，灵活就业比例达到15.3%，反映出年轻人就业观念的变化。",
            "folder": "就业数据"
        },
        {
            "document_id": "doc_002",
            "file_name": "新能源汽车产业分析.docx",
            "content": "截至2024年第三季度，中国新能源汽车保有量突破2000万辆，渗透率达到38.6%。动力电池技术持续突破，固态电池商业化进程加速。",
            "folder": "产业分析"
        },
        {
            "document_id": "doc_003",
            "file_name": "人工智能伦理问题研究.docx",
            "content": "AI决策的可解释性问题日益突出。研究表明，在医疗诊断、金融信贷等高风险场景中，85%的受访者认为了解AI决策依据非常重要。",
            "folder": "科技伦理"
        },
    ]
    
    for fav in favorites_data:
        cm.add_favorite(**fav)
    
    # 创建示例论点
    arguments_data = [
        {
            "title": "人工智能将创造更多就业机会",
            "description": "技术进步历来创造新岗位，AI也不例外",
            "side": ArgumentSide.PRO,
            "evidences": [
                {
                    "content": "世界经济论坛预测，到2025年AI将创造9700万个新工作岗位，同时取代8500万个岗位，净增1200万个就业机会。",
                    "source_file_name": "世界经济论坛报告2024.pdf"
                },
                {
                    "content": "历史数据显示，自动化技术每取代1个岗位，平均创造1.3个新岗位，且新岗位薪资水平通常更高。",
                    "source_file_name": "麦肯锡全球研究院报告.docx"
                }
            ]
        },
        {
            "title": "人工智能加剧就业结构性矛盾",
            "description": "AI替代效应对低技能劳动者冲击巨大",
            "side": ArgumentSide.CON,
            "evidences": [
                {
                    "content": "研究显示，受AI影响最大的是重复性工作岗位，这些岗位的从业者往往缺乏快速转型所需的技能和资源。",
                    "source_file_name": "劳动力市场分析.pdf"
                },
                {
                    "content": "低收入群体再就业周期平均为18个月，是高收入群体的3倍，技术变革加剧社会不平等。",
                    "source_file_name": "社会公平研究报告.docx"
                }
            ]
        },
        {
            "title": "新能源汽车是应对气候变化的有效手段",
            "description": "交通电动化显著减少碳排放",
            "side": ArgumentSide.PRO,
            "evidences": [
                {
                    "content": "生命周期分析表明，电动汽车全生命周期碳排放比燃油车低40%-60%，且随着电网清洁化比例提升，这一优势将进一步扩大。",
                    "source_file_name": "碳排放研究.pdf"
                }
            ]
        },
    ]
    
    for arg_data in arguments_data:
        evidences = arg_data.pop("evidences", [])
        arg = cm.create_argument(**arg_data)
        
        for ev in evidences:
            cm.add_evidence(
                argument_id=arg.id,
                content=ev["content"],
                source_file_name=ev.get("source_file_name")
            )
