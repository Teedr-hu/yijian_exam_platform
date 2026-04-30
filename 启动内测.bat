@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Starting 一建考试模拟平台 on http://localhost:8501
start "一建考试平台" cmd /c "python -m streamlit run app.py --server.port 8501"
