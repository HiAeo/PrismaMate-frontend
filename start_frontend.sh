#!/bin/bash
# ============================================================
# PrismaMate 棱镜 - 前端启动脚本 (Linux/Mac)
# ============================================================
# 用法:
#   开发模式: ./start_frontend.sh dev
#   预览模式: ./start_frontend.sh preview
# ============================================================

MODE="${1:-dev}"

echo "========================================"
echo "PrismaMate 棱镜 - 前端启动"
echo "========================================"

# 获取脚本目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查 Node.js
if ! command -v node &> /dev/null; then
    echo "错误: 未安装 Node.js，请先安装 Node.js 24+"
    exit 1
fi

NODE_VERSION=$(node --version)
echo "Node.js 版本: $NODE_VERSION"

# 检查依赖
if [ ! -d "node_modules" ]; then
    echo "正在安装依赖..."
    npm install
fi

case "$MODE" in
    dev)
        echo ""
        echo "启动开发服务器..."
        echo "访问地址: http://localhost:3000"
        echo "按 Ctrl+C 停止服务"
        echo ""
        npm run dev
        ;;
    preview)
        echo ""
        echo "构建生产版本并预览..."
        npm run build
        npm run preview
        ;;
    *)
        echo "用法: $0 {dev|preview}"
        exit 1
        ;;
esac
