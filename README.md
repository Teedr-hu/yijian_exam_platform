# 一建考试模拟平台

## 功能特性

- 📚 **题库管理** - 添加、编辑、删除题目，支持分类管理
- 📝 **模拟考试** - 随机出题、计时评分、答案解析
- ❌ **错题本** - 自动收集错题，针对性练习
- 📊 **薄弱点分析** - 可视化图表，找出知识薄弱点
- 💾 **数据持久化** - SQLite数据库，数据自动保存

## 快速启动

### 方式一：双击启动（Windows）
```
双击 运行平台.bat
```

### 方式二：命令行启动
```bash
cd D:\yijian_exam_platform
pip install -r requirements.txt
streamlit run app.py
```

启动后访问 http://localhost:8501

## 异地访问（部署到云端）

### 部署到 Streamlit Cloud（免费）

1. 将项目上传到 GitHub 仓库
2. 访问 https://streamlit.io/cloud
3. 连接 GitHub 并部署
4. 获得公开 URL，异地即可访问

### 部署到自己的服务器

```bash
# 使用 gunicorn (Linux)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8501 app:app
```

## 项目结构

```
yijian_exam_platform/
├── app.py              # 主入口
├── database.py         # 数据库操作
├── requirements.txt    # 依赖
├── data/               # 数据库文件（自动创建）
└── pages/              # 多页面模块
    ├── home.py         # 首页概览
    ├── exam.py         # 模拟考试
    ├── wrong_questions.py  # 错题本
    ├── analysis.py      # 薄弱点分析
    └── question_manager.py # 题目管理
```

## 使用说明

1. **首次使用** - 进入"题目管理"页面，点击"导入示例题目"
2. **开始考试** - 选择"模拟考试"，设置题目数量开始
3. **复习错题** - 答题结束后错题自动进入错题本
4. **查看分析** - 在"薄弱点分析"查看掌握情况和学习建议
