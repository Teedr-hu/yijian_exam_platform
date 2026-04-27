"""一建考试模拟平台 - 主入口"""
import streamlit as st
from pathlib import Path
from database import init_database, import_sample_questions

# 页面配置
st.set_page_config(
    page_title="一建考试模拟平台",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 加载自定义样式
def load_css():
    css_path = Path(__file__).parent / "styles.css"
    if css_path.exists():
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# 初始化数据库
init_database()
# import_sample_questions()  # 暂时禁用自动导入示例题目


def render_metric_card(label, value, delta="", card_type=""):
    """渲染指标卡片"""
    cls = f"metric-card {card_type}" if card_type else "metric-card"
    st.markdown(f"""
    <div class="{cls}">
        <div class="label">{label}</div>
        <div class="value">{value}</div>
        <div class="trend">{delta}</div>
    </div>
    """, unsafe_allow_html=True)


def main():
    load_css()

    # 顶部标题卡片
    st.markdown("""
    <div class="title-card">
        <h1>📚 一建考试模拟平台</h1>
        <p>高效备考 · 智能出题 · 精准分析</p>
    </div>
    """, unsafe_allow_html=True)

    # 侧边栏导航
    with st.sidebar:
        st.markdown("### 📖 功能导航")
        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)

        page = st.radio(
            "",
            [
                "🏠 首页概览",
                "📝 模拟考试",
                "❌ 错题本",
                "📊 薄弱点分析",
                "📖 题目管理"
            ],
            index=0,
            label_visibility="collapsed"
        )

        st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align: center; padding: 20px 0; color: #94a3b8; font-size: 13px;">
            <p>💡 坚持每日练习</p>
            <p>顺利通过考试！</p>
        </div>
        """, unsafe_allow_html=True)

    # 路由
    if page == "🏠 首页概览":
        from pages import home
        home.show()
    elif page == "📝 模拟考试":
        from pages import exam
        exam.show()
    elif page == "❌ 错题本":
        from pages import wrong_questions
        wrong_questions.show()
    elif page == "📊 薄弱点分析":
        from pages import analysis
        analysis.show()
    elif page == "📖 题目管理":
        from pages import question_manager
        question_manager.show()


if __name__ == "__main__":
    main()
