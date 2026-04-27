"""错题本"""
import streamlit as st
from database import get_wrong_questions, mark_question_mastered


def show():
    st.markdown("### ❌ 错题本")

    wrong_qs = get_wrong_questions()

    if not wrong_qs:
        st.markdown("""
        <div class="empty-state" style="background: linear-gradient(135deg, #dcfce7, #bbf7d0); border-color: #22c55e;">
            <div class="icon">🎉</div>
            <h3>太棒了！错题本已清空！</h3>
            <p>没有需要复习的题目了，继续保持！</p>
        </div>
        """, unsafe_allow_html=True)
        return

    categories = list(set(q['category'] for q in wrong_qs))

    # 统计卡片
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="label">📚 待攻克题目</div>
            <div class="value">{len(wrong_qs)}</div>
            <div class="trend">道题目需要复习</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card primary">
            <div class="label">📂 涉及分类</div>
            <div class="value">{len(categories)}</div>
            <div class="trend">个分类需要加强</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # 操作区
    col_all, col_m = st.columns([3, 1])
    with col_all:
        st.markdown(f"""
        <div style="background: #f8fafc; padding: 16px 20px; border-radius: 12px;">
            <span style="font-weight: 600;">错题分布在 </span>
            <span class="tag tag-purple">{len(categories)} 个分类</span>
            <span style="color: #64748b; margin-left: 12px;">{'、'.join(categories)}</span>
        </div>
        """, unsafe_allow_html=True)

    with col_m:
        if st.button("✅ 全部标记已掌握", type="secondary", use_container_width=True):
            for q in wrong_qs:
                mark_question_mastered(q['id'])
            st.success("已全部标记为已掌握！")
            st.rerun()

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # 按分类显示
    for cat in categories:
        cat_qs = [q for q in wrong_qs if q['category'] == cat]

        with st.expander(f"📚 {cat} ({len(cat_qs)}道错题)", expanded=True):
            for idx, q in enumerate(cat_qs):
                diff_map = {1: "简单", 2: "中等", 3: "困难"}

                st.markdown(f"""
                <div class="wrong-card">
                    <div style="margin-bottom: 12px;">
                        <span class="tag tag-blue">{q['category']}</span>
                        <span class="tag {'tag-green' if q['difficulty'] == 1 else 'tag-yellow' if q['difficulty'] == 2 else 'tag-red'}">
                            {diff_map[q['difficulty']]}
                        </span>
                        <span class="tag tag-red">错{q['wrong_count']}次</span>
                    </div>
                    <h4 style="margin: 0 0 16px 0;">{idx + 1}. {q['question_text']}</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px;">
                        <div style="background: white; padding: 10px 14px; border-radius: 8px; font-size: 14px;">A. {q['option_a']}</div>
                        <div style="background: white; padding: 10px 14px; border-radius: 8px; font-size: 14px;">B. {q['option_b']}</div>
                        <div style="background: white; padding: 10px 14px; border-radius: 8px; font-size: 14px;">C. {q['option_c']}</div>
                        <div style="background: white; padding: 10px 14px; border-radius: 8px; font-size: 14px;">D. {q['option_d']}</div>
                    </div>
                    <div style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; padding: 10px 16px; border-radius: 8px; display: inline-block;">
                        ✅ 正确答案：<strong>{q['correct_answer']}</strong>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                col_mark, col_detail = st.columns([1, 1])
                with col_mark:
                    if st.button(f"✅ 我掌握了", key=f"master_{q['id']}", use_container_width=True):
                        mark_question_mastered(q['id'])
                        st.success("已标记为已掌握！")
                        st.rerun()

                with col_detail:
                    with st.expander("📖 查看解析"):
                        st.info(q.get('explanation', '暂无解析'))

                st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    st.markdown("### 🎯 针对性练习")
    if st.button("📝 开始针对性练习", type="primary", use_container_width=True):
        st.switch_page("pages/exam.py")
