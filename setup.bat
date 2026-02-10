@echo off
echo ========================================
echo 高速公路超车RL系统 - 环境安装
echo ========================================
echo.

REM 检测Python版本
python --version 2>nul
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8-3.10
    pause
    exit /b 1
)

echo [1/4] 检测Python版本...
python -c "import sys; assert (3,8) <= sys.version_info[:2] <= (3,10), 'Python版本必须在3.8-3.10之间'; print(f'✓ Python {sys.version_info.major}.{sys.version_info.minor}')"
if errorlevel 1 (
    pause
    exit /b 1
)

echo.
echo [2/4] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
    echo ✓ 虚拟环境创建成功
) else (
    echo ✓ 虚拟环境已存在
)

echo.
echo [3/4] 激活虚拟环境并安装依赖...
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo.
echo [4/4] 验证安装...
python -c "import gymnasium; import highway_env; import stable_baselines3; print('✓ 核心依赖安装成功')"

if errorlevel 1 (
    echo [错误] 依赖验证失败
    pause
    exit /b 1
)

echo.
echo ========================================
echo ✓ 安装完成！
echo ========================================
echo.
echo 下一步操作：
echo   1. 训练模型: scripts\1_train_ppo.bat
echo   2. 运行评测: scripts\2_eval_baseline.bat
echo   3. 生成图表: scripts\5_generate_plots.bat
echo.
pause
