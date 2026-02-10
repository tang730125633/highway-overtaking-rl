@echo off
REM Windows启动脚本 - 高速公路超车RL系统Web界面

echo ========================================
echo 高速公路超车RL系统 - Web界面启动
echo ========================================
echo.

REM 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先运行 setup.bat 安装环境
    pause
    exit /b 1
)

REM 激活虚拟环境（如果存在）
if exist venv\Scripts\activate.bat (
    echo [1/3] 激活虚拟环境...
    call venv\Scripts\activate.bat
) else (
    echo [警告] 未找到虚拟环境，使用系统Python
)

REM 检查streamlit是否安装
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [2/3] 安装Streamlit...
    pip install streamlit plotly -q
) else (
    echo [2/3] Streamlit已安装
)

REM 启动Streamlit应用
echo [3/3] 启动Web应用...
echo.
echo ========================================
echo 应用将在浏览器中自动打开
echo 地址: http://localhost:8501
echo 按 Ctrl+C 停止应用
echo ========================================
echo.

python -m streamlit run app.py

pause
