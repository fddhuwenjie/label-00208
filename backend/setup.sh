#!/bin/bash
# DebatePrep 环境初始化脚本

set -e

echo "========================================"
echo "  DebatePrep 辩论赛智能备赛助手"
echo "  环境初始化脚本"
echo "========================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查 Python 版本
check_python() {
    echo "📦 检查 Python 环境..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo -e "${RED}❌ 未找到 Python，请先安装 Python 3.9+${NC}"
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
    echo -e "${GREEN}✅ Python 版本: $PYTHON_VERSION${NC}"
}

# 创建虚拟环境
create_venv() {
    echo ""
    echo "📦 创建虚拟环境..."
    
    if [ -d "venv" ]; then
        echo -e "${YELLOW}⚠️  虚拟环境已存在，跳过创建${NC}"
    else
        $PYTHON_CMD -m venv venv
        echo -e "${GREEN}✅ 虚拟环境创建成功${NC}"
    fi
}

# 激活虚拟环境
activate_venv() {
    echo ""
    echo "📦 激活虚拟环境..."
    
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
    
    echo -e "${GREEN}✅ 虚拟环境已激活${NC}"
}

# 安装依赖
install_deps() {
    echo ""
    echo "📦 安装项目依赖..."
    
    pip install --upgrade pip -q
    pip install -r requirements.txt
    
    echo -e "${GREEN}✅ 依赖安装完成${NC}"
}

# 创建必要目录
create_dirs() {
    echo ""
    echo "📁 创建必要目录..."
    
    mkdir -p documents
    mkdir -p data/index
    mkdir -p data/vectors
    
    echo -e "${GREEN}✅ 目录创建完成${NC}"
}

# 显示完成信息
show_complete() {
    echo ""
    echo "========================================"
    echo -e "${GREEN}🎉 环境初始化完成！${NC}"
    echo "========================================"
    echo ""
    echo "后续使用说明："
    echo ""
    echo "  1. 激活虚拟环境："
    echo "     source venv/bin/activate"
    echo ""
    echo "  2. 将文档放入 documents 目录"
    echo ""
    echo "  3. 启动应用："
    echo "     streamlit run app/main.py"
    echo ""
    echo "  4. 访问地址："
    echo "     http://localhost:8501"
    echo ""
    echo "========================================"
    echo "  或使用 Docker 方式启动："
    echo "     docker compose up"
    echo "========================================"
}

# 主流程
main() {
    check_python
    create_venv
    activate_venv
    install_deps
    create_dirs
    show_complete
}

main
