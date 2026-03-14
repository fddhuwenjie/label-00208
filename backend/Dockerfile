FROM python:3.11-slim

LABEL maintainer="DebatePrep Team"
LABEL description="辩论赛智能备赛助手 - 本地文档智能分析工具"
LABEL version="2.0"

WORKDIR /app

# 设置时区为中国时间
ENV TZ=Asia/Shanghai

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    tzdata \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 复制依赖文件
COPY requirements.txt .

# 安装 Python 依赖（使用 CPU 版本的 PyTorch，支持 x86 和 ARM64）
RUN pip install --no-cache-dir -r requirements.txt \
    && pip cache purge

# 预下载语义模型（可选，会增加镜像大小但加快首次启动）
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')" || true

# 复制应用代码
COPY app/ ./app/
COPY .streamlit/ ./.streamlit/

# 创建数据目录
RUN mkdir -p /app/data/index /app/data/vectors /app/documents

# 暴露端口
EXPOSE 8501

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# 启动命令
CMD ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
