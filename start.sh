#!/bin/bash
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$ROOT/quant-backend"
FRONTEND="$ROOT/quant-frontend"

echo "🚀 启动量化交易系统..."

# 启动后端
cd "$BACKEND"
if [ ! -d ".venv" ]; then
  echo "📦 创建 Python 虚拟环境..."
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt -q
else
  source .venv/bin/activate
fi

echo "✅ 启动后端 (http://localhost:8888)..."
uvicorn main:app --host 0.0.0.0 --port 8888 --reload &
BACKEND_PID=$!

# 启动前端
cd "$FRONTEND"
if [ ! -d "node_modules" ]; then
  echo "📦 安装前端依赖..."
  npm install -q
fi

echo "✅ 启动前端 (http://localhost:5173)..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "==============================="
echo "  量化交易系统已启动"
echo "  前端: http://localhost:5173"
echo "  后端: http://localhost:8888"
echo "  Ctrl+C 关闭所有服务"
echo "==============================="

# 等待 Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo '已关闭'" SIGINT SIGTERM
wait
