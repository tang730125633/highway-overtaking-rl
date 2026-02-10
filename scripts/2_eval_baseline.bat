@echo off
echo ========================================
echo 评测规则基线策略
echo ========================================
echo.

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 切换到项目根目录
cd ..

REM 运行评测
echo 开始评测基线策略...
python -m src.baseline.evaluate_baseline --config-dir configs --output-dir outputs --n-episodes 50

echo.
echo ========================================
echo 评测完成！
echo ========================================
echo.
echo 结果保存在: outputs\results\
echo.
pause
