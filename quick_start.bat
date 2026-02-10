@echo off
echo ========================================
echo 高速公路超车RL系统 - 快速开始
echo ========================================
echo.
echo 本脚本将引导你完成完整流程：
echo   1. 安装环境
echo   2. 测试环境
echo   3. 训练PPO模型
echo   4. 运行所有评测
echo   5. 生成论文图表
echo.
echo 预计总耗时: 30-60分钟（取决于电脑性能）
echo.
pause

REM 步骤1: 安装环境
echo.
echo [步骤 1/5] 安装环境...
call setup.bat
if errorlevel 1 (
    echo 安装失败，请检查错误信息
    pause
    exit /b 1
)

REM 步骤2: 测试环境
echo.
echo [步骤 2/5] 测试环境...
call scripts\0_test_env.bat
if errorlevel 1 (
    echo 环境测试失败，请检查错误信息
    pause
    exit /b 1
)

REM 步骤3: 训练模型
echo.
echo [步骤 3/5] 训练PPO模型（这可能需要20-40分钟）...
call scripts\1_train_ppo.bat
if errorlevel 1 (
    echo 训练失败，请检查错误信息
    pause
    exit /b 1
)

REM 步骤4: 运行评测
echo.
echo [步骤 4/5] 运行评测（包括Baseline、RL、RL+Safety）...

echo.
echo [4.1] 评测基线策略...
call scripts\2_eval_baseline.bat

echo.
echo [4.2] 评测RL策略...
call scripts\3_eval_rl.bat

echo.
echo [4.3] 评测RL+Safety策略...
call scripts\4_eval_rl_safety.bat

REM 步骤5: 生成图表
echo.
echo [步骤 5/5] 生成论文图表...
call scripts\5_generate_plots.bat

echo.
echo ========================================
echo ✓ 所有步骤完成！
echo ========================================
echo.
echo 结果位置:
echo   - 训练模型: outputs\models\
echo   - 评测结果: outputs\results\
echo   - 论文图表: outputs\figures\
echo.
echo 你现在可以：
echo   1. 查看 outputs\figures\ 中的图表
echo   2. 查看 outputs\results\ 中的CSV数据
echo   3. 使用这些结果撰写论文
echo.
pause
