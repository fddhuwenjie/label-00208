"""应用配置"""

import os
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = DATA_DIR / "index"
VECTOR_DIR = DATA_DIR / "vectors"
DB_PATH = DATA_DIR / "debate_prep.db"

# 文档目录（Docker 挂载或本地指定）
DOCUMENTS_DIR = os.environ.get("DOCUMENTS_DIR", str(BASE_DIR / "documents"))

# 支持的文件类型
SUPPORTED_EXTENSIONS = {".docx", ".doc", ".xlsx", ".xls", ".pdf", ".txt"}

# 搜索配置（可通过环境变量或设置页面调整）
CONTEXT_SENTENCES = int(os.environ.get("CONTEXT_SENTENCES", "3"))
MAX_RESULTS = int(os.environ.get("MAX_RESULTS", "50"))

# 语义分析配置
# SIMILARITY_THRESHOLD: 语义相似度阈值（0.0-1.0），值越低匹配越宽松
SIMILARITY_THRESHOLD = float(os.environ.get("SIMILARITY_THRESHOLD", "0.3"))

# 演示数据配置
# 设置 DISABLE_DEMO_DATA=true 禁用演示数据加载（用于生产环境）
DISABLE_DEMO_DATA = os.environ.get("DISABLE_DEMO_DATA", "false").lower() in ("true", "1", "yes")

# 语义模型配置
# 设置 DISABLE_SEMANTIC_MODEL=true 禁用深度语义模型，使用 TF-IDF 方案
DISABLE_SEMANTIC_MODEL = os.environ.get("DISABLE_SEMANTIC_MODEL", "false").lower() in ("true", "1", "yes")

# UI 配置
PAGE_TITLE = "DebatePrep - 辩论赛智能备赛助手"
PAGE_ICON = "🎯"
