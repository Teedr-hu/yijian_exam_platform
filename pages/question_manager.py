"""题目管理"""
import streamlit as st
import os
from pathlib import Path
from database import (
    get_all_questions, get_category_list, add_question,
    delete_question, import_sample_questions
)
from import_questions import get_import_files, import_all_files, IMPORT_FOLDER


def show():
    st.markdown("### 📖 题目管理")

    tabs = st.tabs(["📋 题目列表", "➕ 添加题目", "📥 批量导入", "🔄 更新题库"])

    # 题目列表
    with tabs[0]:
        questions = get_all_questions()
        categories = get_category_list()

        if not questions:
            st.info("暂无题目，请添加题目或导入题库")
        else:
            st.write(f"共 {len(questions)} 道题目")

            for q in questions:
                diff_map = {1: "🟢 简单", 2: "🟡 中等", 3: "🔴 困难"}
                with st.expander(f"【{q['category']}】{q['question_text'][:50]}...", expanded=False):
                    st.write(f"**题目：** {q['question_text']}")
                    st.write(f"**A.** {q['option_a']}")
                    st.write(f"**B.** {q['option_b']}")
                    st.write(f"**C.** {q['option_c']}")
                    st.write(f"**D.** {q['option_d']}")
                    st.success(f"正确答案：{q['correct_answer']}")
                    st.info(f"解析：{q.get('explanation', '暂无')}")
                    st.write(f"难度：{diff_map.get(q['difficulty'], '未知')} | 分类：{q['category']}")

                    if st.button("🗑️ 删除", key=f"del_{q['id']}"):
                        delete_question(q['id'])
                        st.success("删除成功")
                        st.rerun()

    # 添加题目
    with tabs[1]:
        st.markdown("#### 添加新题目")

        with st.form("add_question_form"):
            col1, col2 = st.columns(2)

            with col1:
                category = st.text_input("分类 *", placeholder="如：法规、管理、实务")
                question_text = st.text_area("题目内容 *", placeholder="请输入题目内容", height=80)

            with col2:
                difficulty = st.selectbox("难度", [1, 2, 3], format_func=lambda x: {1: "简单", 2: "中等", 3: "困难"}[x])

            option_a = st.text_input("选项A *", placeholder="A选项内容")
            option_b = st.text_input("选项B *", placeholder="B选项内容")
            option_c = st.text_input("选项C *", placeholder="C选项内容")
            option_d = st.text_input("选项D *", placeholder="D选项内容")

            correct_answer = st.radio("正确答案 *", ["A", "B", "C", "D"], horizontal=True)
            explanation = st.text_area("解析（可选）", placeholder="题目解析", height=60)

            submitted = st.form_submit_button("💾 保存题目", type="primary", use_container_width=True)

            if submitted:
                if not category or not question_text or not all([option_a, option_b, option_c, option_d]):
                    st.error("请填写所有必填项")
                else:
                    add_question(
                        category=category,
                        question_text=question_text,
                        option_a=option_a,
                        option_b=option_b,
                        option_c=option_c,
                        option_d=option_d,
                        correct_answer=correct_answer,
                        explanation=explanation,
                        difficulty=difficulty
                    )
                    st.success("题目添加成功！")
                    st.rerun()

        st.markdown("---")
        st.markdown("#### 📚 快速导入")

        if st.button("📥 导入示例题目", type="secondary", use_container_width=True):
            import_sample_questions()
            st.success("示例题目导入成功！")
            st.rerun()

    # 批量导入
    with tabs[2]:
        st.markdown("#### 批量导入题目")

        st.info("""
        **导入格式说明：**
        每行一道题目，格式为：
        ```
        分类|题目内容|选项A|选项B|选项C|选项D|正确答案|解析|难度(1-3)
        ```
        """)

        batch_text = st.text_area("粘贴题目内容", placeholder="请按照上述格式粘贴题目，每行一道", height=200)

        if st.button("📥 开始导入", type="primary", use_container_width=True):
            if not batch_text.strip():
                st.error("请输入题目内容")
            else:
                success_count = 0
                for line in batch_text.strip().split('\n'):
                    line = line.strip()
                    if not line:
                        continue
                    parts = line.split('|')
                    if len(parts) >= 7:
                        try:
                            add_question(
                                category=parts[0].strip(),
                                question_text=parts[1].strip(),
                                option_a=parts[2].strip(),
                                option_b=parts[3].strip(),
                                option_c=parts[4].strip(),
                                option_d=parts[5].strip(),
                                correct_answer=parts[6].strip().upper(),
                                explanation=parts[7].strip() if len(parts) > 7 else "",
                                difficulty=int(parts[8].strip()) if len(parts) > 8 and parts[8].strip().isdigit() else 1
                            )
                            success_count += 1
                        except:
                            pass

                st.success(f"成功导入 {success_count} 道题目！")
                st.rerun()

    # 更新题库
    with tabs[3]:
        st.markdown("#### 🔄 更新题库")

        st.markdown(f"""
        **📁 题库文件夹：** `{IMPORT_FOLDER}`

        将题库文件（Excel、CSV、TXT）放入上述文件夹，然后点击「开始更新」按钮。
        """)

        # 显示文件夹中的文件
        files = get_import_files()

        if files:
            st.markdown("**📋 发现以下文件：**")
            for f in files:
                file_size = f.stat().st_size / 1024  # KB
                st.write(f"  - `{f.name}` ({file_size:.1f} KB)")
        else:
            st.warning(f"文件夹为空，请将题库文件放入：`{IMPORT_FOLDER}`")

        st.markdown("---")

        # 更新按钮
        col_update, col_refresh = st.columns([1, 1])

        with col_update:
            if st.button("🔄 开始更新题库", type="primary", use_container_width=True, disabled=len(files) == 0):
                with st.spinner("正在导入题库..."):
                    count, details = import_all_files()

                if count > 0:
                    st.success(f"✅ 成功导入 {count} 道题目！")
                    for d in details:
                        st.write(f"  - {d}")
                else:
                    st.warning("未能导入任何题目，请检查文件格式")

                st.rerun()

        with col_refresh:
            if st.button("🔍 刷新文件列表", use_container_width=True):
                st.rerun()

        st.markdown("---")

        # 支持的格式说明
        with st.expander("📖 支持的文件格式"):
            st.markdown("""
            **1. Excel 文件 (.xlsx, .xls)**
            - 需要包含表头行
            - 支持多Sheet，会读取所有Sheet

            **2. CSV 文件 (.csv)**
            - 默认使用UTF-8编码
            - 如有问题可尝试GBK编码

            **3. TXT 文件 (.txt)**
            - 每行一道题目
            - 使用 `|` 或 `Tab` 分隔各字段
            - 格式：`分类|题目|A选项|B选项|C选项|D选项|答案|解析|难度`

            **4. Word 文件 (.docx)**
            - 自动识别题目编号、选项、答案、解析
            - 建议格式：1. 题目内容 / A. 选项 / 答案：B / 解析：xxx

            **5. PDF 文件 (.pdf)**
            - 自动识别题目、选项、答案、解析
            - 基于文本的PDF效果最佳
            """)
