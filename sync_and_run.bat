@echo off
chcp 65001 >nul
cd /d D:\yijian_exam_platform

echo Checking for updates...
git add -A
git status | findstr /C:"nothing to commit" >nul 2>&1
if %errorlevel%==0 (
    echo No changes to commit.
) else (
    echo Committing and pushing to GitHub...
    git commit -m "Auto sync"
    git push origin master
)

echo Starting app at http://localhost:8501
py -m streamlit run app.py --server.headless=true --server.port=8501

pause