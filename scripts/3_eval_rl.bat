@echo off
echo ========================================
echo 评测RL策略（不含Safety Shield）
echo ========================================
echo.

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 切换到项目根目录
cd ..

REM 检查模型是否存在
if not exist "outputs\models\best\best_model.zip" (
    echo [错误] 模型文件不存在！
    echo 请先运行 1_train_ppo.bat 训练模型
    pause
    exit /b 1
)

REM 运行评测
echo 开始评测RL策略...
python -m src.rl.evaluate --model outputs\models\best\best_model --config-dir configs --output-dir outputs --n-episodes 50

echo.
echo ========================================
echo 评测完成！
echo ========================================
echo.
echo 结果保存在: outputs\results\
echo.
pause
