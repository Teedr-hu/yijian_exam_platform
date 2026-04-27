@echo off
chcp 65001 >nul
title 一建考试平台 - 启动并同步
echo ========================================
echo    一建考试平台 - 启动并同步到云端
echo ========================================

:: 获取脚本所在目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: 切换到项目目录
cd /d "D:\yijian_exam_platform"

echo.
echo [1/4] 检查代码更新...
git add -A
git status | findstr /C:"nothing to commit" >nul 2>&1
if %errorlevel%==0 (
    echo [2/4] 代码无更新，跳过推送
) else (
    echo [2/4] 发现更新，正在推送到GitHub...
    git commit -m "Auto sync: %date% %time%"
    git push origin master
    if %errorlevel%==0 (
        echo [3/4] 推送成功！Streamlit Cloud将自动更新...
    ) else (
        echo [3/4] 推送失败，请检查网络或GitHub账号
    )
)

echo [4/4] 启动应用...
echo.
echo 应用启动中，请访问 http://localhost:8501
echo.

:: 启动 Streamlit
py -m streamlit run app.py --server.headless=true --server.port=8501

pause
