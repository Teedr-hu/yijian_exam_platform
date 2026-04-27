"""首页概览"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database import get_statistics


def show():
    stats = get_statistics()

    # 核心指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card primary">
            <div class="label">📚 总题库</div>
            <div class="value">{stats['total_questions']}</div>
            <div class="trend">道题目</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card danger">
            <div class="label">❌ 待攻克</div>
            <div class="value">{stats['not_mastered']}</div>
            <div class="trend">需要加强</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card success">
            <div class="label">✅ 已掌握</div>
            <div class="value">{stats['mastered']}</div>
            <div class="trend">错题已清</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        accuracy = stats['accuracy_trend'][0]['accuracy'] if stats['accuracy_trend'] else 0
        st.markdown(f"""
        <div class="metric-card">
            <div class="label">📈 最近正确率</div>
            <div class="value">{accuracy}%</div>
            <div class="trend">最近一次</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # 分类掌握情况
    if stats['category_stats']:
        st.markdown("### 📊 分类掌握情况")

        col_chart, col_table = st.columns([2, 1])

        with col_chart:
            df = pd.DataFrame(stats['category_stats'])
            df['掌握率'] = df.apply(
                lambda x: round((x['total'] - x['wrong_count']) / x['total'] * 100, 1)
                if x['total'] > 0 else 0, axis=1
            )

            colors = ['#4caf50' if r >= 80 else '#ff9800' if r >= 60 else '#f44336' for r in df['掌握率']]

            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=df['category'],
                y=df['掌握率'],
                marker_color=colors,
                text=[f"{r}%" for r in df['掌握率']],
                textposition='outside'
            ))
            fig.update_layout(
                yaxis_range=[0, 110],
                showlegend=False,
                height=350,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(family="Inter, sans-serif")
            )
            st.plotly_chart(fig, use_container_width=True)

        with col_table:
            st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
            st.markdown("**📋 详细数据**")
            for _, row in df.iterrows():
                rate = row['掌握率']
                emoji = "🟢" if rate >= 80 else "🟡" if rate >= 60 else "🔴"
                st.markdown(f"{emoji} **{row['category']}**: {rate}% (错{row['wrong_count']}题)")
            st.markdown("</div>", unsafe_allow_html=True)

    else:
        st.markdown("""
        <div class="empty-state">
            <div class="icon">📚</div>
            <h3>暂无题目数据</h3>
            <p>请先在「题目管理」中添加题目</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

    # 薄弱类别推荐
    st.markdown("### 🎯 推荐加强")

    if stats['category_stats']:
        weak = [c for c in stats['category_stats'] if c['wrong_count'] > 0]
        if weak:
            cols = st.columns(min(len(weak), 3))
            for idx, wc in enumerate(sorted(weak, key=lambda x: x['wrong_count'], reverse=True)[:3]):
                mastery = round((wc['total'] - wc['wrong_count']) / wc['total'] * 100, 1)
                with cols[idx]:
                    st.markdown(f"""
                    <div class="metric-card warning">
                        <div class="label">{wc['category']}</div>
                        <div class="value" style="font-size: 24px;">错{wc['wrong_count']}题</div>
                        <div class="trend">掌握率: {mastery}%</div>
                    </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"去练习", key=f"home_prac_{wc['category']}"):
                        st.switch_page("pages/exam.py")
        else:
            st.success("🎉 太棒了！所有类别都已掌握，继续保持！")
