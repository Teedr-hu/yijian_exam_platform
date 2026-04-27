@echo off
cd /d D:\yijian_exam_platform

echo Sync code to GitHub...
git add -A
git commit -m "sync" 2>nul
git push origin master 2>nul

echo.
echo Starting app...
py -m streamlit run app.py --server.headless=true --server.port=8501
