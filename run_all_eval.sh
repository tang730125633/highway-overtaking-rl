#!/bin/bash

# 一键运行所有评测脚本

echo "========================================="
echo "运行所有评测（Baseline + RL + RL+Safety）"
echo "========================================="
echo ""

# 激活环境
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
source venv/bin/activate

echo "[1/4] 评测基线策略..."
python -m src.baseline.evaluate_baseline --config-dir configs --output-dir outputs --n-episodes 20

echo ""
echo "[2/4] 评测RL策略..."
python -m src.rl.evaluate --model outputs/outputs/models/best/best_model --config-dir configs --output-dir outputs --n-episodes 20

echo ""
echo "[3/4] 评测RL+Safety策略..."
python -m src.rl.evaluate --model outputs/outputs/models/best/best_model --config-dir configs --output-dir outputs --n-episodes 20 --safety-shield

echo ""
echo "[4/4] 生成论文图表..."
python -m src.utils.visualize --results-dir outputs/outputs/results --output-dir outputs/outputs/figures

echo ""
echo "========================================="
echo "✓ 所有评测完成！"
echo "========================================="
echo ""
echo "查看结果："
echo "  - 数据: outputs/outputs/results/"
echo "  - 图表: outputs/outputs/figures/"
echo ""
