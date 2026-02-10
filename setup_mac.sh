#!/bin/bash

echo "========================================"
echo "高速公路超车RL系统 - macOS环境安装"
echo "========================================"
echo ""

# 检查是否有conda
if command -v conda &> /dev/null; then
    echo "检测到 conda，将使用 conda 创建 Python 3.10 环境..."
    echo ""

    # 创建conda环境
    echo "[1/4] 创建 Python 3.10 虚拟环境..."
    conda create -n highway_rl python=3.10 -y

    echo ""
    echo "[2/4] 激活虚拟环境..."
    source $(conda info --base)/etc/profile.d/conda.sh
    conda activate highway_rl

    echo ""
    echo "[3/4] 安装依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt

    if [ $? -ne 0 ]; then
        echo "[错误] 依赖安装失败"
        exit 1
    fi

    echo ""
    echo "[4/4] 验证安装..."
    python -c "import gymnasium; import highway_env; import stable_baselines3; print('✓ 核心依赖安装成功')"

    if [ $? -ne 0 ]; then
        echo "[错误] 依赖验证失败"
        exit 1
    fi

    echo ""
    echo "========================================"
    echo "✓ 安装完成！"
    echo "========================================"
    echo ""
    echo "下一步操作："
    echo "  1. 激活环境: conda activate highway_rl"
    echo "  2. 测试环境: python test_env.py"
    echo "  3. 开始训练: python -m src.rl.train"
    echo ""

else
    echo "[错误] 未检测到 conda"
    echo ""
    echo "你的系统是 Python 3.14.3，需要使用 Python 3.10"
    echo ""
    echo "请先安装 conda："
    echo "  下载地址: https://docs.conda.io/en/latest/miniconda.html"
    echo ""
    echo "或者安装 pyenv 来管理多个 Python 版本："
    echo "  brew install pyenv"
    echo "  pyenv install 3.10.13"
    echo "  pyenv local 3.10.13"
    echo ""
    exit 1
fi
