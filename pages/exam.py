"""模拟考试"""
import streamlit as st
import random
from database import get_all_questions, get_questions_by_category, get_category_list, get_wrong_questions, save_answer_record


def show():
    st.markdown("### 📝 模拟考试")

    # 初始化
    for key in ['exam_started', 'exam_questions', 'current_index', 'exam_results']:
        if key not in st.session_state:
            st.session_state[key] = False if key == 'exam_started' else [] if key in ['exam_questions', 'exam_results'] else 0

    categories = get_category_list()

    # 考试设置界面
    if not st.session_state.exam_started:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**📋 题目来源**")
            source = st.radio(
                "",
                ["全部分类", "针对性练习（错题本）", "指定分类"],
                horizontal=True,
                label_visibility="collapsed"
            )

        with col2:
            st.markdown("**📊 题目数量**")
            if source == "指定分类" and categories:
                selected_category = st.selectbox("选择分类", categories)
            else:
                selected_category = None

        if source == "针对性练习（错题本）":
            wrong_qs = get_wrong_questions()
            max_wrong = len(wrong_qs)
            if max_wrong == 0:
                st.success("🎉 错题本已清空！暂无需要针对性练习的题目")
                return
            question_count = st.number_input("选择题目数量", 1, max_wrong, min(5, max_wrong))
        else:
            all_qs = get_questions_by_category(selected_category) if selected_category else get_all_questions()
            max_count = len(all_qs)
            if max_count == 0:
                st.info("该分类暂无题目，请先添加题目")
                return
            question_count = st.number_input("选择题目数量", 1, max_count, min(10, max_count))

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        if st.button("🚀 开始考试", type="primary", use_container_width=True):
            if source == "针对性练习（错题本）":
                questions = get_wrong_questions()[:question_count]
            elif selected_category:
                questions = get_questions_by_category(selected_category)
                questions = random.sample(questions, min(len(questions), question_count))
            else:
                questions = get_all_questions()
                questions = random.sample(questions, min(len(questions), question_count))

            st.session_state.exam_questions = questions
            st.session_state.current_index = 0
            st.session_state.exam_results = []
            st.session_state.exam_started = True
            st.rerun()

    # 考试进行中
    if st.session_state.exam_started and st.session_state.exam_questions:
        q = st.session_state.exam_questions[st.session_state.current_index]
        total = len(st.session_state.exam_questions)
        current = st.session_state.current_index + 1

        st.progress(current / total, text=f"第 {current} / {total} 题")

        # 题目卡片
        st.markdown(f"""
        <div class="question-card">
            <span class="category-badge">{q['category']}</span>
            <span class="difficulty-badge difficulty-{q['difficulty']}">
                {'简单' if q['difficulty'] == 1 else '中等' if q['difficulty'] == 2 else '困难'}
            </span>
            <h4 style="margin: 16px 0 0 0;">{q['question_text']}</h4>
        </div>
        """, unsafe_allow_html=True)

        # 选项
        options = {
            'A': q['option_a'],
            'B': q['option_b'],
            'C': q['option_c'],
            'D': q['option_d']
        }

        user_answer = st.radio(
            "请选择答案：",
            list(options.keys()),
            format_func=lambda x: f"{x}. {options[x]}",
            key=f"q_{q['id']}"
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        col_prev, col_next, col_submit = st.columns([1, 1, 2])

        with col_prev:
            if st.session_state.current_index > 0:
                if st.button("⬅️ 上一题", use_container_width=True):
                    st.session_state.current_index -= 1
                    st.rerun()

        with col_next:
            if st.session_state.current_index < total - 1:
                if st.button("下一题 ➡️", use_container_width=True):
                    st.rerun()

        with col_submit:
            if current == total:
                if st.button("📤 提交答卷", type="primary", use_container_width=True):
                    for question in st.session_state.exam_questions:
                        selected = st.session_state.get(f"q_{question['id']}", "")
                        is_correct = selected == question['correct_answer']
                        if selected:
                            save_answer_record(question['id'], selected, is_correct)
                        st.session_state.exam_results.append({
                            'question': question,
                            'user_answer': selected or '未答',
                            'is_correct': is_correct
                        })
                    st.session_state.exam_started = False
                    st.rerun()

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        if st.button("🔚 提前交卷", use_container_width=True):
            for question in st.session_state.exam_questions:
                selected = st.session_state.get(f"q_{question['id']}", "")
                is_correct = selected == question['correct_answer']
                if selected:
                    save_answer_record(question['id'], selected, is_correct)
                    st.session_state.exam_results.append({
                        'question': question,
                        'user_answer': selected,
                        'is_correct': is_correct
                    })
                else:
                    save_answer_record(question['id'], '未答', False)
                    st.session_state.exam_results.append({
                        'question': question,
                        'user_answer': '未答',
                        'is_correct': False
                    })
            st.session_state.exam_started = False
            st.rerun()

    # 考试成绩
    if not st.session_state.exam_started and st.session_state.exam_results:
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("### 📋 考试成绩")

        results = st.session_state.exam_results
        correct = sum(1 for r in results if r['is_correct'])
        total = len(results)
        accuracy = round(correct / total * 100, 1)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="label">正确题数</div>
                <div class="value">{correct}/{total}</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
            <div class="metric-card {'success' if accuracy >= 60 else 'danger'}">
                <div class="label">正确率</div>
                <div class="value">{accuracy}%</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if accuracy >= 80:
                st.success("🎉 表现优秀！")
            elif accuracy >= 60:
                st.warning("💪 继续加油！")
            else:
                st.error("📚 需要加强学习")

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        st.markdown("#### 📖 答题详情")
        for i, r in enumerate(results, 1):
            q = r['question']
            status = "✅" if r['is_correct'] else "❌"

            with st.expander(f"{status} 第{i}题 - {q['question_text'][:40]}...", expanded=False):
                st.write(f"**题目：** {q['question_text']}")
                st.write(f"**你的答案：** {r['user_answer']}")
                st.write(f"**正确答案：** {q['correct_answer']}")
                st.info(f"**解析：** {q.get('explanation', '暂无解析')}")

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        if st.button("🔄 再来一次", type="primary", use_container_width=True):
            st.session_state.exam_results = []
            st.rerun()
