#!/bin/bash
# Mac启动脚本 - 高速公路超车RL系统Web界面

# 进入脚本所在目录
cd "$(dirname "$0")"

echo "========================================"
echo "高速公路超车RL系统 - Web界面启动"
echo "========================================"
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python3，请先安装"
    read -p "按任意键退出..."
    exit 1
fi

# 激活虚拟环境（如果存在）
if [ -d "venv" ]; then
    echo "[1/3] 激活虚拟环境..."
    source venv/bin/activate
else
    echo "[警告] 未找到虚拟环境，使用系统Python"
fi

# 检查streamlit是否安装
if ! python3 -c "import streamlit" &> /dev/null; then
    echo "[2/3] 安装Streamlit..."
    pip3 install streamlit plotly
else
    echo "[2/3] Streamlit已安装"
fi

# 启动Streamlit应用
echo "[3/3] 启动Web应用..."
echo ""
echo "========================================"
echo "应用将在浏览器中自动打开"
echo "地址: http://localhost:8501"
echo "按 Ctrl+C 停止应用"
echo "========================================"
echo ""

python3 -m streamlit run app.py

# 保持窗口打开
read -p "按任意键关闭..."
