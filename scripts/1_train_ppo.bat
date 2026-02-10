@echo off
echo ========================================
echo 训练PPO模型
echo ========================================
echo.

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 切换到项目根目录
cd ..

REM 运行训练
echo 开始训练...
python -m src.rl.train --config-dir configs --output-dir outputs

echo.
echo ========================================
echo 训练完成！
echo ========================================
echo.
echo 模型保存在: outputs\models\
echo 日志保存在: outputs\logs\
echo.
pause
