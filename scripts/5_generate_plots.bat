@echo off
echo ========================================
echo 生成论文图表
echo ========================================
echo.

REM 激活虚拟环境
call ..\venv\Scripts\activate.bat

REM 切换到项目根目录
cd ..

REM 运行绘图脚本
echo 生成图表...
python -m src.utils.visualize --results-dir outputs\results --output-dir outputs\figures

echo.
echo ========================================
echo 图表生成完成！
echo ========================================
echo.
echo 图表保存在: outputs\figures\
echo.
pause
