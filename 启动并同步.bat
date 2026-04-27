@echo off
chcp 65001 >nul
echo ========================================
echo    一建考试平台 - 启动并同步到云端
echo ========================================
cd /d "%~dp0"

echo.
echo [1/4] 检查代码更新...
git add -A
git commit -m "Auto sync: %date% %time%" 2>nul
if %errorlevel%==0 (
    echo [2/4] 发现更新，正在推送到GitHub...
    git push origin master
    if %errorlevel%==0 (
        echo [3/4] 推送成功！Streamlit Cloud将自动更新...
    ) else (
        echo [3/4] 推送失败，请检查网络或GitHub账号
    )
) else (
    echo [2/4] 代码无更新，跳过推送
)

echo [4/4] 启动应用...
echo.
pip install -r requirements.txt -q 2>nul
echo 应用启动中，请访问 http://localhost:8501
echo.
streamlit run app.py
pause
