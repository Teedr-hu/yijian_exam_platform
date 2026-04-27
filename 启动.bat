@echo off
echo ========================================
echo    一建考试模拟平台 - 启动中...
echo ========================================
cd /d "%~dp0"
pip install -r requirements.txt -q
echo.
echo 安装完成，正在启动...
streamlit run app.py
pause
