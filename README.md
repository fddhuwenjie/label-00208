# DebatePrep - 辩论赛智能备赛助手

> 本地文档智能分析工具，专为辩论赛备赛设计。基于深度学习的语义理解，帮助你从海量资料中快速定位关键论据。

## 功能特性

- **文档遍历与提取**: 支持 .docx, .doc, .xlsx, .xls, .pdf, .txt 格式
- **智能搜索**: 关键词精确搜索、布尔搜索、**深度语义联想**
- **内容管理**: 标签系统、收藏功能、Markdown 导出
- **辩论专用**: 论点管理、**正反方自动归类**、**关系图谱可视化**、数据统计
- **引用追踪**: 从搜索结果直接添加论据，自动记录来源位置

### 文档格式支持说明

| 格式 | 支持程度 | 解析引擎 | 说明 |
|------|----------|----------|------|
| .docx | ✅ 完整支持 | python-docx | Office 2007+ Word 文档 |
| .doc | ✅ 多级降级 | docx → antiword → textract | 自动尝试多种方式解析 |
| .xlsx | ✅ 完整支持 | openpyxl | Office 2007+ Excel 文档 |
| .xls | ✅ 完整支持 | xlrd | Excel 97-2003 格式 |
| .pdf | ✅ 完整支持 | pdfplumber | 支持文本提取和布局分析 |
| .txt | ✅ 完整支持 | chardet | 自动编码检测（UTF-8/GBK等） |

> **提示**：
> - 旧版 .doc 格式（Word 97-2003）如解析失败，建议用 Word/WPS 另存为 .docx 格式
> - 系统会自动检测文件格式并选择最佳解析引擎

## ⚠️ 重要提示：首次启动说明

本项目使用 **深度学习语义模型** 提供真正的语义理解能力，请注意以下事项：

### 镜像大小
- Docker 镜像约 **3-4GB**（包含 PyTorch 和语义模型）
- 首次 `docker compose build` 需要较长时间下载依赖

### 首次启动
- 首次使用语义联想功能时，系统会自动下载语义模型（约 **500MB**）
- 下载时间取决于网络速度，请耐心等待
- 模型下载完成后会自动缓存，后续启动无需重复下载

### 内存要求
- 建议至少 **4GB 可用内存**
- 语义模型加载后约占用 500MB-1GB 内存

## 快速启动

### 方式一：Docker 启动（推荐，零配置）

```bash
# 1. 将你的文档放入 documents 目录
cp -r /path/to/your/docs/* documents/

# 2. 构建并启动服务（首次构建约需 10-15 分钟）
docker compose up --build

# 3. 访问应用
open http://localhost:8501
```

### 方式二：本地开发

> **⚠️ 重要：本地开发必须先安装依赖**
>
> 首次运行前，**必须**执行以下步骤安装依赖，否则会报 `ModuleNotFoundError`：
>
> ```bash
> cd backend
> # 方法 A：使用初始化脚本（推荐）
> ./setup.sh
>
> # 方法 B：手动安装
> python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
> ```

```bash
# 1. 进入 backend 目录
cd backend

# 2. 运行初始化脚本（自动创建虚拟环境、安装依赖）
./setup.sh

# 3. 激活虚拟环境
source venv/bin/activate

# 4. 将你的文档放入 documents 目录
cp -r /path/to/your/docs/* ../documents/

# 5. 启动应用
streamlit run app/main.py

# 6. 访问地址
open http://localhost:8501
```

### 方式三：手动配置

```bash
# 1. 进入 backend 目录
cd backend

# 2. 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 3. 安装依赖（需要较长时间下载 PyTorch）
pip install -r requirements.txt

# 4. 创建必要目录
mkdir -p ../documents ../data/index ../data/vectors

# 5. 启动应用
streamlit run app/main.py
```

## 新增功能 v2.0

### 🧠 深度语义联想
- 基于 Sentence-Transformers 深度学习模型
- 真正理解语义关系：输入"年轻人"可找到"就业"、"消费"、"压力"等相关概念
- 支持跨语言语义匹配

### 🗺️ 论点-论据关系图谱
- 可视化展示论点与论据的关系
- 正反方对比视图
- 论点强度评估

### ⚖️ 正反方自动归类
- AI 自动分析文本立场倾向
- 智能建议论点分类
- 论据立场一致性检测

### 📊 增强数据统计
- 自动提取数值、百分比、年份数据
- 热门关键词分析
- 论点/论据统计图表

## 项目结构

```
├── backend/             # 后端代码
│   ├── app/             # 主应用代码
│   │   ├── components/  # UI 组件
│   │   ├── services/    # 业务逻辑
│   │   ├── models/      # 数据模型
│   │   └── utils/       # 工具函数
│   ├── tests/           # 测试代码
│   ├── .streamlit/      # Streamlit 配置
│   ├── Dockerfile       # 容器构建文件
│   └── requirements.txt # Python 依赖
├── data/                # 数据存储（自动创建）
├── docs/                # 项目文档
├── documents/           # 待分析的文档（用户提供）
└── docker-compose.yml   # 容器编排配置
```

## 运行测试

### 前置条件

1. **已安装依赖**：确保已在 backend 目录执行 `./setup.sh` 或 `pip install -r requirements.txt`
2. **测试依赖**：pytest 已包含在 requirements.txt 中，无需额外安装
3. **数据目录**：测试会自动创建临时数据目录，无需手动初始化

### 运行测试

```bash
# 1. 进入 backend 目录并激活虚拟环境
cd backend
source venv/bin/activate

# 2. 运行所有测试
pytest tests/ -v

# 3. 运行测试并生成覆盖率报告
pytest tests/ -v --cov=app --cov-report=html

# 4. 仅运行特定测试文件
pytest tests/test_search.py -v

# 5. 跳过需要语义模型的测试（加速测试）
DISABLE_SEMANTIC_MODEL=true pytest tests/ -v
```

### 测试说明

- 测试使用独立的 SQLite 数据库，不会影响生产数据
- 首次运行语义相关测试时可能需要下载模型
- 设置 `DISABLE_SEMANTIC_MODEL=true` 可跳过深度语义测试

## 演示数据说明

首次启动时，系统会自动加载演示数据以展示功能，包括：

- 12 份模拟文档（就业、科技、环境等主题）
- 6 个预设标签
- 3 条示例收藏
- 3 个示例论点及论据

这些数据仅用于演示目的。将真实文档放入 `documents/` 目录后，系统会自动解析并索引。

### 禁用演示数据

如果不需要演示数据（生产环境），可通过环境变量禁用：

```bash
# Docker 启动
DISABLE_DEMO_DATA=true docker compose up

# 本地启动
DISABLE_DEMO_DATA=true streamlit run app/main.py
```

## 配置参数

可通过环境变量或设置页面调整以下参数：

| 环境变量 | 默认值 | 说明 |
|----------|--------|------|
| `SIMILARITY_THRESHOLD` | 0.3 | 语义相似度阈值（0.1-0.9） |
| `MAX_RESULTS` | 50 | 最大搜索结果数 |
| `CONTEXT_SENTENCES` | 3 | 上下文句子数 |
| `DISABLE_DEMO_DATA` | false | 禁用演示数据加载 |
| `DISABLE_SEMANTIC_MODEL` | false | 禁用深度语义模型（使用 TF-IDF） |
| `DOCUMENTS_DIR` | ./documents | 文档目录路径 |

## 技术栈

- **Web 框架**: Streamlit
- **文档处理**: python-docx, openpyxl, pdfplumber
- **搜索引擎**: Whoosh + 同义词扩展
- **语义分析**: **Sentence-Transformers (深度学习)**, jieba
- **数据存储**: SQLite
- **容器化**: Docker + Docker Compose

## 系统要求

| 项目 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 2 核 | 4 核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 10GB | 20GB+ |
| 网络 | 首次需联网下载模型 | - |

## 常见问题

### Q: 首次启动很慢？
A: 首次启动需要下载语义模型（约 500MB），请确保网络连接稳定。下载完成后，后续启动会很快。

### Q: 内存不足？
A: 语义模型需要约 1GB 内存。如果内存不足，可以编辑 `app/services/semantic_analyzer.py`，将 `_model_name` 改为更小的模型如 `paraphrase-MiniLM-L6-v2`。

### Q: 如何跳过语义模型？
A: 如果不需要深度语义功能，可以在 `semantic_analyzer.py` 中注释掉 sentence-transformers 相关代码，系统会回退到 TF-IDF 方案。

## 交付验收

### 一键启动

```bash
docker compose up
```

### 启动成功标志

容器日志中显示以下内容表示启动成功：

```
============================================================
✅ Startup Success
🌐 Frontend: http://localhost:8501
============================================================
```

### 访问地址

- **Web 界面**: http://localhost:8501
- **健康检查**: http://localhost:8501/_stcore/health

## 开发状态

🚀 **v2.0** - Production Ready

## License

MIT
