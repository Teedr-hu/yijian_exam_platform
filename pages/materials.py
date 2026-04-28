"""学习资料页面"""
import streamlit as st
from pathlib import Path

# 学习资料目录
MATERIALS_DIR = Path("D:/2026一建【建筑】SVIP/学习资料")

def load_md_content(filename):
    """加载MD文件内容"""
    filepath = MATERIALS_DIR / filename
    if filepath.exists():
        return filepath.read_text(encoding='utf-8')
    return None

def parse_tips_content(content):
    """解析口诀内容"""
    if not content:
        return []
    items = []
    lines = content.split('\n')
    current_item = None
    current_answer = []
    in_answer = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过标题行
        if '年一建' in line or '记忆口诀' in line or '速记口诀' in line:
            continue

        # 检查是否是口诀总结行
        if '速记总结' in line or '速记口诀' in line or '记忆口诀' in line:
            if current_item:
                current_answer.append(line)
                items.append({
                    'question': current_item,
                    'answer': '\n'.join(current_answer)
                })
                current_item = None
                current_answer = []
                in_answer = False
            continue

        # 如果没有在答案中，检查是否是编号开头的问题
        if not in_answer and (line[0].isdigit() if line else False):
            # 新问题开始了
            if current_item and current_answer:
                items.append({
                    'question': current_item,
                    'answer': '\n'.join(current_answer)
                })
            # 提取问题（去掉编号）
            current_item = line
            current_answer = []
            in_answer = True
        elif in_answer and current_item:
            # 在答案部分
            current_answer.append(line)

    # 最后一个
    if current_item and current_answer:
        items.append({
            'question': current_item,
            'answer': '\n'.join(current_answer)
        })

    return items

def parse_case_content(content):
    """解析案例内容"""
    if not content:
        return []
    items = []
    lines = content.split('\n')
    current_q = None
    current_a = []
    in_answer = False

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 跳过标题
        if '案例' in line and '问' in line:
            continue

        # 检查问号（问题结尾）
        if '？' in line or '?' in line:
            if current_q and current_a:
                items.append({
                    'question': current_q,
                    'answer': '\n'.join(current_a)
                })
            current_q = line
            current_a = []
            in_answer = True
        elif in_answer and current_q:
            current_a.append(line)

    if current_q and current_a:
        items.append({
            'question': current_q,
            'answer': '\n'.join(current_a)
        })

    return items

def show():
    st.markdown("### 📚 学习资料")

    # 子导航
    sub_page = st.radio(
        "选择资料类型",
        [
            "🏠 资料首页",
            "📝 案例200问"
        ],
        horizontal=True
    )

    if sub_page == "🏠 资料首页":
        show_home()
    elif sub_page == "📝 案例200问":
        show_case_questions()

def show_home():
    """资料首页"""
    st.markdown("""
    <div class="question-card">
        <h3>📚 学习资料中心</h3>
        <p>这里汇集了一建考试的各种学习资料，包括：</p>
        <ul>
            <li><strong>📝 案例200问</strong> - 建筑工程案例分析问答，涵盖施工技术、项目管理等</li>
        </ul>
        <p style="color: #666; font-size: 13px;">选择上方不同标签查看各类资料</p>
    </div>
    """, unsafe_allow_html=True)

    # 资料统计
    col1, = st.columns(1)
    with col1:
        st.metric("案例200问", "200+", "案例分析")

def show_case_questions():
    """案例200问"""
    st.markdown("#### 📝 案例200问")
    st.markdown("*建筑工程管理与实务案例分析 - 问答题形式*")

    content = load_md_content("案例必背200问.md")
    if not content:
        st.error("未找到案例200问资料文件")
        return

    items = parse_case_content(content)
    st.success(f"共 {len(items)} 道案例问答")

    # 搜索
    search = st.text_input("搜索", "")

    # 过滤
    filtered = []
    for item in items:
        if search and search.lower() not in item['question'].lower():
            continue
        filtered.append(item)

    # 显示 - 优化格式
    st.markdown("---")
    for i, item in enumerate(filtered):
        # 直接使用原始问题
        question = item['question']

        # 显示问题和答案按钮
        st.markdown(f"**Q{i+1}: {question}**")
        with st.expander("🔍 查看答案"):
            st.markdown(item['answer'])

def format_answer_text(answer):
    """格式化答案文本，合并多余空行"""
    # 按换行分割
    lines = answer.split('\n')
    items = []
    for line in lines:
        line = line.strip()
        if line:
            items.append(line)
    # 合并为连续文本，用<br>显示
    return '<br>'.join(items)


def parse_tips_content_v2(content):
    """解析口诀内容 - 支持建筑/法规/管理三种格式"""
    if not content:
        return []

    items = []
    lines = content.split('\n')

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        # 跳过标题行和空行
        if '年一建' in line or not line:
            i += 1
            continue

        # 跳过纯记忆口诀行
        if '记忆口诀' in line or '速记口诀' in line or '速记总结' in line:
            i += 1
            continue

        # 法规格式：以"、"开头的问题行，下一行是单独数字
        if line.startswith('、'):
            # 问题行
            question = line[1:].strip()  # 去掉开头的"、""
            # 下一行是编号
            i += 1
            num = lines[i].strip() if i < len(lines) else ''
            # 再下一行开始是答案
            answer_lines = []
            j = i + 1
            tips = ""

            while j < len(lines):
                next_line = lines[j].strip()
                # 遇到下一个以"、"开头的问题，停止
                if next_line.startswith('、'):
                    break
                # 遇到单独的数字行且下一行也是以"、"开头，可能是下一个问题
                if next_line and len(next_line) == 1 and next_line.isdigit():
                    if j + 2 < len(lines) and lines[j+2].strip().startswith('、'):
                        break
                # 遇到口诀标记
                if '速记口诀' in next_line or '速记总结' in next_line:
                    # 提取口诀内容
                    for t in ['速记口诀：', '速记总结：']:
                        if t in next_line:
                            tips = next_line.split(t)[-1].strip().replace('【', '').replace('】', '').strip()
                            break
                    j += 1
                    continue
                # 跳过奇怪的"符号
                if next_line in ['"', '"']:
                    j += 1
                    continue
                if next_line:
                    answer_lines.append(next_line)
                j += 1

            full_answer = '\n'.join(answer_lines)
            items.append({'num': num, 'question': question, 'answer': full_answer, 'tips': tips})
            i = j
            continue

        # 建筑/管理格式：以数字+、或数字.开头（必须在行开头）
        is_main_num = line and len(line) > 1 and line[0].isdigit() and (line[1] == '、' or line[1] == '.')

        if is_main_num:
            if '、' in line:
                parts = line.split('、', 1)
                num = parts[0]
                question = parts[1]
            else:
                parts = line.split('.', 1)
                num = parts[0]
                question = parts[1] if len(parts) > 1 else ''

            answer_lines = []
            j = i + 1
            tips = ""

            while j < len(lines):
                next_line = lines[j].strip()
                # 主编号必须在行开头，且是 ASCII 数字
                is_next_main = next_line and len(next_line) > 1 and next_line[0].isdigit() and ord(next_line[0]) < 256 and (next_line[1] == '、' or next_line[1] == '.')
                if is_next_main:
                    break
                if '【记忆口诀】' in next_line or '【速记口诀】' in next_line or '【速记总结】' in next_line:
                    tips = next_line.replace('【记忆口诀】', '').replace('【速记口诀】', '').replace('【速记总结】', '').strip()
                    j += 1
                    continue
                if next_line:
                    answer_lines.append(next_line)
                j += 1

            full_answer = '\n'.join(answer_lines)
            items.append({'num': num, 'question': question, 'answer': full_answer, 'tips': tips})
            i = j
        else:
            i += 1

    return items

def show_tips():
    """记忆口诀"""
    st.markdown("#### 🧠 记忆口诀")
    st.markdown("*高效记忆技巧，用口诀记住复杂知识点*")

    # 选择科目
    subject = st.selectbox(
        "选择科目",
        ["建筑记忆口诀.md", "法规记忆口诀.md", "管理记忆口诀.md"],
        format_func=lambda x: x.replace("记忆口诀.md", ""),
        index=0
    )

    content = load_md_content(subject)
    if not content:
        st.error(f"未找到{subject}资料文件")
        return

    # 解析内容
    items = parse_tips_content_v2(content)
    st.success(f"共 {len(items)} 条记忆口诀")

    # 搜索
    search = st.text_input("搜索关键词", "")

    # 过滤
    filtered = []
    for item in items:
        if search and search.lower() not in item['question'].lower() and search.lower() not in item['answer'].lower():
            continue
        filtered.append(item)

    # 平铺显示所有记忆口诀
    st.markdown("---")

    for item in filtered:
        st.markdown(f"**{item['num']}. {item['question']}**")
        formatted_answer = format_answer_text(item['answer'])
        st.markdown(formatted_answer, unsafe_allow_html=True)
        if item['tips']:
            st.markdown(f"<span style='color:#e74c3c; font-weight:bold;'>🔑 记忆口诀：{item['tips']}</span>", unsafe_allow_html=True)
        st.markdown("---")

def show_notes():
    """三色笔记"""
    st.markdown("#### 📖 三色笔记")
    st.markdown("*重点知识整理，红色标注核心考点*")

    # 选择科目
    subject = st.selectbox(
        "选择科目",
        ["建筑三色笔记", "法规三色笔记", "管理三色笔记", "经济三色笔记"],
        index=0
    )

    # 文件映射
    file_map = {
        "建筑三色笔记": "建筑三色笔记.md",
        "法规三色笔记": "法规三色笔记.md",
        "管理三色笔记": "管理三色笔记.md",
        "经济三色笔记": "经济三色笔记.md"
    }

    content = load_md_content(file_map[subject])
    if not content:
        st.error(f"未找到{subject}资料文件")
        return

    st.info(f"正在加载{subject}...")

    # 简单展示内容（按段落分割）
    st.markdown("---")

    # 限制显示，避免页面太长
    paragraphs = content.split('\n\n')
    st.success(f"共 {len(paragraphs)} 个知识点")

    # 搜索
    search = st.text_input("搜索", "")

    filtered_paras = []
    for para in paragraphs:
        if search and search.lower() not in para.lower():
            continue
        if len(para.strip()) > 20:  # 过滤太短的内容
            filtered_paras.append(para)

    # 显示
    for para in filtered_paras[:100]:  # 最多显示100个
        if '【' in para or '★' in para or '●' in para:
            st.markdown(para)
        else:
            st.markdown(para.replace('\n', ' '))
        st.markdown("---")
