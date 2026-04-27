"""薄弱点分析"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import get_statistics


def show():
    st.markdown("## 📊 薄弱点分析")

    stats = get_statistics()

    if not stats['total_questions']:
        st.info("暂无学习数据，开始做题后这里会显示详细分析")
        return

    # 薄弱点总览
    st.markdown("### 🎯 薄弱点总览")

    col1, col2, col3 = st.columns(3)

    with col1:
        if stats['category_stats']:
            worst = max(stats['category_stats'], key=lambda x: x['wrong_count'])
            st.metric("⚠️ 最薄弱分类", worst['category'], delta=f"错{worst['wrong_count']}题")

    with col2:
        st.metric("❌ 待攻克", f"{stats['not_mastered']}题")

    with col3:
        if stats['total_questions'] > 0:
            overall = round((stats['total_questions'] - stats['not_mastered']) / stats['total_questions'] * 100, 1)
            st.metric("📚 整体掌握率", f"{overall}%")

    st.markdown("---")

    # 分类详细分析
    if stats['category_stats']:
        st.markdown("### 📊 分类分析")

        df = pd.DataFrame(stats['category_stats'])
        df['掌握率'] = df.apply(
            lambda x: round((x['total'] - x['wrong_count']) / x['total'] * 100, 1)
            if x['total'] > 0 else 0, axis=1
        )

        col_bar, col_pie = st.columns(2)

        with col_bar:
            fig_bar = px.bar(
                df,
                x='category',
                y='掌握率',
                color='掌握率',
                color_continuous_scale=['#ff6b6b', '#ffd93d', '#6bcb77'],
                title="各类别掌握率"
            )
            fig_bar.update_layout(
                yaxis_range=[0, 100],
                showlegend=False,
                height=350
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        with col_pie:
            wrong_df = df[df['wrong_count'] > 0]
            if not wrong_df.empty:
                fig_pie = px.pie(
                    wrong_df,
                    values='wrong_count',
                    names='category',
                    title="错题分布",
                    hole=0.4
                )
                fig_pie.update_layout(height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.success("🎉 所有分类都已掌握！")

        st.markdown("---")

        # 薄弱类别
        weak_cats = df[df['掌握率'] < 80].sort_values('掌握率')

        if not weak_cats.empty:
            st.markdown("### 🔴 需要加强的分类")

            for _, row in weak_cats.iterrows():
                with st.container():
                    col_cat, col_stats, col_action = st.columns([2, 2, 1])

                    with col_cat:
                        st.write(f"**{row['category']}**")

                    with col_stats:
                        progress = row['掌握率'] / 100
                        st.progress(progress, text=f"掌握率: {row['掌握率']}% | 总题: {row['total']} | 错题: {row['wrong_count']}")

                    with col_action:
                        if st.button("针对性练习", key=f"analyze_{row['category']}"):
                            st.switch_page("pages/exam.py")

    st.markdown("---")

    # 正确率趋势
    if stats['accuracy_trend']:
        st.markdown("### 📉 学习趋势")

        df_trend = pd.DataFrame(stats['accuracy_trend'][::-1])

        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=df_trend['date'],
            y=df_trend['accuracy'],
            mode='lines+markers',
            line=dict(color='#667eea', width=3),
            marker=dict(size=10)
        ))
        fig_line.update_layout(
            yaxis_range=[0, 100],
            height=300,
            showlegend=False
        )
        st.plotly_chart(fig_line, use_container_width=True)

        if len(stats['accuracy_trend']) >= 2:
            recent = stats['accuracy_trend'][0]['accuracy']
            older = stats['accuracy_trend'][-1]['accuracy']
            change = recent - older

            if change > 5:
                st.success(f"📈 最近正确率提升了 {change}%！继续保持！")
            elif change < -5:
                st.warning(f"📉 最近正确率下降了 {abs(change)}%，建议加强复习")
            else:
                st.info("➡️ 正确率基本稳定，继续保持当前学习节奏")

    st.markdown("---")

    # 学习建议
    st.markdown("### 💡 学习建议")

    suggestions = []

    if stats['category_stats']:
        weak_cats = [c for c in stats['category_stats'] if c['wrong_count'] > 0]
        if weak_cats:
            suggestions.append(f"1. 重点关注薄弱分类：{', '.join([c['category'] for c in weak_cats])}")

    if stats['not_mastered'] > 10:
        suggestions.append("2. 错题较多，建议每天抽出时间复习错题本")
    elif stats['not_mastered'] > 0:
        suggestions.append("3. 坚持练习，错题本中的题目掌握后及时标记")

    if not suggestions:
        suggestions.append("🎉 当前学习状态良好，继续保持！")

    for s in suggestions:
        st.write(s)
