#!/bin/bash

# 快速训练脚本（实时输出）

echo "激活环境..."
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"
eval "$(pyenv init -)"
source venv/bin/activate

echo "开始训练（实时输出）..."
# 使用PYTHONUNBUFFERED确保实时输出
PYTHONUNBUFFERED=1 python -u -m src.rl.train --config-dir configs --output-dir outputs
