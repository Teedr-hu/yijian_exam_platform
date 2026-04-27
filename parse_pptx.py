import json
import re
import sys
from database import add_question

sys.stdout.reconfigure(encoding='utf-8')

with open('extracted_pptx.json', 'r', encoding='utf-8') as f:
    slides = json.load(f)

def get_slide_num(s):
    m = re.search(r'slide(\d+)', s['slide'])
    return int(m.group(1)) if m else 0

slides.sort(key=get_slide_num)

def parse_question(text):
    """解析题目文本，提取问题、选项、答案"""
    is_multi = '二、多项选择题' in text

    # 匹配多选题 (5个选项 A-E)
    if is_multi:
        match = re.search(r'\d+\.\s*(.+?)\s+([A-E])\.\s*([^\n]+?)\s+([A-E])\.\s*([^\n]+?)\s+([A-E])\.\s*([^\n]+?)\s+([A-E])\.\s*([^\n]+?)\s+([A-E])\.\s*([^\n]+?)$', text, re.DOTALL)
        if match:
            return {
                'text': match.group(1).strip(),
                'option_a': match.group(3).strip(),
                'option_b': match.group(5).strip(),
                'option_c': match.group(7).strip(),
                'option_d': match.group(9).strip(),
                'option_e': match.group(11).strip(),
                'is_multi': True
            }
    else:
        # 匹配单选题 (4个选项 A-D)
        match = re.search(r'\d+\.\s*(.+?)\s+([A-D])\.\s*([^\n]+?)\s+([A-D])\.\s*([^\n]+?)\s+([A-D])\.\s*([^\n]+?)\s+([A-D])\.\s*([^\n]+?)$', text, re.DOTALL)
        if match:
            return {
                'text': match.group(1).strip(),
                'option_a': match.group(3).strip(),
                'option_b': match.group(5).strip(),
                'option_c': match.group(7).strip(),
                'option_d': match.group(9).strip(),
                'option_e': '',
                'is_multi': False
            }
    return None

def parse_answer(text):
    """解析答案文本"""
    ans_match = re.search(r'答案[：:]\s*([A-Za-z,，、]+)', text)
    exp_match = re.search(r'解析[：:]\s*(.+)', text)
    return {
        'answer': ans_match.group(1) if ans_match else "",
        'explanation': exp_match.group(1).strip() if exp_match else ""
    }

# 处理所有幻灯片
questions_data = []
i = 0
while i < len(slides):
    slide = slides[i]
    text = slide['text']

    # 跳过标题页和说明页
    if any(kw in text for kw in ['考试真题', '一、单项选择题 共', '二、多项选择题 二', '主讲老师']):
        i += 1
        continue

    # 检查是否是题目页
    q = parse_question(text)
    if q:
        # 找对应的答案页
        if i + 1 < len(slides):
            ans = parse_answer(slides[i + 1]['text'])
            q['answer'] = ans['answer']
            q['explanation'] = ans['explanation']
            questions_data.append(q)
            i += 2
            continue
    i += 1

print(f"共解析出 {len(questions_data)} 道题目\n")

# 显示前10道题目
for q in questions_data[:10]:
    qtype = "多选" if q['is_multi'] else "单选"
    print(f"[{qtype}] {q['text'][:60]}...")
    print(f"  答案: {q['answer']}")
    print()

# 导入到数据库
print("开始导入数据库...")
imported = 0
for q in questions_data:
    category = "多选题" if q['is_multi'] else "单选题"
    difficulty = 2

    # 清理答案格式
    answer = q['answer'].upper().replace('，', ',').replace('、', ',').replace(' ', '')

    try:
        add_question(
            category=category,
            question_text=q['text'],
            option_a=q['option_a'],
            option_b=q['option_b'],
            option_c=q['option_c'],
            option_d=q['option_d'],
            correct_answer=answer,
            explanation=q['explanation'],
            difficulty=difficulty
        )
        imported += 1
    except Exception as e:
        print(f"导入失败: {q['text'][:30]}... 错误: {e}")

print(f"\n成功导入 {imported} 道题目到数据库！")