@echo off
echo ========================================
echo 测试环境是否正常工作
echo ========================================
echo.

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 切换到项目根目录
cd ..

REM 运行测试
python test_env.py

echo.
pause
