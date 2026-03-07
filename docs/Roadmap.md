# 开发路线图

## 项目信息

| 属性 | 值 |
|------|-----|
| 项目名称 | DebatePrep - 辩论赛智能备赛助手 |
| 启动命令 | `docker compose up` |
| 访问地址 | `http://localhost:8501` |

---

## Phase 1: 基础架构与文档处理 (P0)

### 1.1 项目骨架搭建
- [x] **T1.1.1** 初始化项目结构
- [x] **T1.1.2** 配置 Docker 环境（Dockerfile + docker-compose.yml）
- [x] **T1.1.3** 配置依赖管理（requirements.txt）
- [x] **T1.1.4** Streamlit 基础框架搭建

### 1.2 文档解析引擎
- [x] **T1.2.1** Word 文档解析器（.docx）
- [x] **T1.2.2** Excel 文档解析器（.xlsx）
- [x] **T1.2.3** PDF 文档解析器
- [x] **T1.2.4** 纯文本解析器（.txt）
- [x] **T1.2.5** 统一文档处理接口
- [x] **T1.2.6** 文件夹递归遍历功能

### 1.3 索引系统
- [x] **T1.3.1** Whoosh 搜索引擎集成
- [x] **T1.3.2** 文档索引 Schema 设计
- [x] **T1.3.3** 索引构建与持久化
- [x] **T1.3.4** 索引重建功能

### 1.4 基础搜索功能
- [x] **T1.4.1** 关键词精确搜索
- [x] **T1.4.2** 搜索结果高亮显示
- [x] **T1.4.3** 上下文片段提取
- [x] **T1.4.4** 布尔搜索（AND/OR/NOT）

### 1.5 基础 UI
- [x] **T1.5.1** 文件夹选择与扫描界面
- [x] **T1.5.2** 搜索界面
- [x] **T1.5.3** 搜索结果展示界面
- [x] **T1.5.4** 文档列表界面

**Phase 1 交付物**:
- 可运行的 Docker 容器
- 支持 4 种文档格式解析
- 基础搜索功能可用

---

## Phase 2: 语义分析与内容管理 (P0/P1)

### 2.1 语义联想引擎
- [x] **T2.1.1** jieba 中文分词集成
- [x] **T2.1.2** Sentence-Transformers 模型加载
- [x] **T2.1.3** 文档向量化处理
- [x] **T2.1.4** 语义相似度计算
- [x] **T2.1.5** 上下文共现词分析
- [x] **T2.1.6** 概念扩展算法实现

### 2.2 内容管理系统
- [x] **T2.2.1** SQLite 数据库设计
- [x] **T2.2.2** 标签系统实现
- [x] **T2.2.3** 收藏功能实现
- [x] **T2.2.4** 笔记/注释功能
- [x] **T2.2.5** Markdown 导出功能

### 2.3 增强搜索
- [x] **T2.3.1** 语义搜索界面
- [x] **T2.3.2** 联想词展示组件
- [x] **T2.3.3** 搜索历史记录
- [x] **T2.3.4** 模糊搜索实现

### 2.4 UI 优化
- [x] **T2.4.1** 标签管理界面
- [x] **T2.4.2** 收藏夹界面
- [x] **T2.4.3** 导出功能界面
- [x] **T2.4.4** 整体视觉优化

**Phase 2 交付物**:
- 语义联想搜索可用
- 标签、收藏、导出功能完整
- 界面美观度达标

---

## Phase 3: 辩论专用功能 (P0/P1)

### 3.1 论点管理
- [x] **T3.1.1** 论点卡片数据模型
- [x] **T3.1.2** 论点创建与编辑界面
- [x] **T3.1.3** 论据关联功能
- [x] **T3.1.4** 正反方标记功能

### 3.2 数据支持
- [x] **T3.2.1** Excel 数据提取增强
- [x] **T3.2.2** 数据统计展示
- [x] **T3.2.3** 引用来源追踪

### 3.3 可视化
- [x] **T3.3.1** 正反方对比视图
- [ ] **T3.3.2** 论点-论据关系图谱（可选）

### 3.4 最终优化
- [x] **T3.4.1** 性能优化
- [x] **T3.4.2** 错误处理完善
- [x] **T3.4.3** 用户体验打磨

**Phase 3 交付物**:
- 完整的辩论备赛功能
- 生产级稳定性
- 优秀的用户体验

---

## 项目结构

```
debate-prep/
├── backend/                      # 后端应用（Alkaid-SOP 命名规范）
│   ├── app/                      # 主应用代码
│   │   ├── __init__.py
│   │   ├── main.py               # Streamlit 入口
│   │   ├── config.py             # 配置管理
│   │   ├── components/           # UI 组件
│   │   │   ├── __init__.py
│   │   │   ├── sidebar.py        # 侧边栏
│   │   │   ├── search_box.py     # 搜索框
│   │   │   ├── result_card.py    # 结果卡片
│   │   │   ├── argument_graph.py # 论点关系图谱
│   │   │   ├── concept_tree.py   # 概念树组件
│   │   │   └── styles.py         # 样式定义
│   │   ├── views/                # 页面视图
│   │   │   ├── __init__.py
│   │   │   ├── dashboard_page.py # 仪表盘页面
│   │   │   ├── search_page.py    # 搜索页面
│   │   │   ├── documents_page.py # 文档管理页面
│   │   │   ├── arguments_page.py # 论点管理页面
│   │   │   ├── favorites_page.py # 收藏夹页面
│   │   │   ├── tags_page.py      # 标签管理页面
│   │   │   ├── export_page.py    # 导出功能页面
│   │   │   └── settings_page.py  # 设置页面
│   │   ├── services/             # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── document_parser.py    # 文档解析
│   │   │   ├── search_engine.py      # 搜索引擎
│   │   │   ├── semantic_analyzer.py  # 语义分析
│   │   │   ├── content_manager.py    # 内容管理
│   │   │   └── data_statistics.py    # 数据统计
│   │   ├── models/               # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── document.py
│   │   │   ├── search_result.py
│   │   │   ├── tag.py
│   │   │   ├── favorite.py
│   │   │   └── argument.py
│   │   └── utils/                # 工具函数
│   │       ├── __init__.py
│   │       ├── file_utils.py
│   │       ├── text_utils.py
│   │       ├── validators.py     # 数据验证
│   │       ├── logger.py         # 日志工具
│   │       ├── synonym_dict.py   # 同义词词典
│   │       └── init_data.py      # 初始化数据
│   ├── tests/                    # 测试代码
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── test_search_engine.py
│   │   ├── test_content_manager.py
│   │   └── test_synonym_dict.py
│   ├── data/                     # 数据存储（运行时生成）
│   │   ├── index/                # Whoosh 索引
│   │   ├── vectors/              # 向量存储
│   │   └── debate_prep.db        # SQLite 数据库
│   ├── .streamlit/               # Streamlit 配置
│   │   └── config.toml
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── requirements.txt
│   └── setup.sh                  # 启动脚本
├── docs/                         # 项目文档
│   ├── Requirements.md
│   ├── Roadmap.md
│   ├── DesignSpec.md
│   └── SelfTestReport.md
├── documents/                    # 用户文档目录（挂载点）
├── .gitignore
├── docker-compose.yml
└── README.md
```

---

## 技术决策记录

### TD1: 搜索引擎选型
- **选择**: Whoosh
- **理由**: 纯 Python 实现，无外部依赖，适合本地部署

### TD2: 语义模型选型
- **选择**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **理由**: 支持中文，模型体积适中（~500MB），本地运行

### TD3: 向量存储选型
- **选择**: NumPy + 文件存储
- **理由**: 简单高效，文档量级（<10000）无需专用向量数据库

### TD4: UI 框架选型
- **选择**: Streamlit
- **理由**: 快速开发，内置美观组件，Docker 友好

---

## 里程碑

| 里程碑 | 内容 | 状态 |
|--------|------|------|
| M1 | 基础搜索可用 | ✅ 完成 |
| M2 | 语义联想可用 | ✅ 完成 |
| M3 | 内容管理完整 | ✅ 完成 |
| M4 | 辩论功能完整 | ✅ 完成 |
| M5 | 生产级交付 | ✅ 完成 |

---

## 文档版本

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| 1.0 | 2026-03-06 | 初始版本 |
| 1.1 | 2026-03-07 | 更新项目结构，与实际代码结构保持一致（Alkaid-SOP backend 命名规范） |
