import re
import sys
from pathlib import Path
from database import add_question

sys.stdout.reconfigure(encoding='utf-8')

def parse_md_file(content):
    """解析单个markdown文件的题目"""
    questions = []

    # 清理文本：合并断行
    # 选项可能断行，如 "A.电" 下一行 "影院"
    content = re.sub(r'\n([A-E])\.(\s*)', r'\n\1. ', content)

    # 解析每个题目
    # 格式: 数字. 题干 [选项A-D] 【答案】X 【解析】YYY
    pattern = r'(\d+)\s*\.\s*(.+?)\s*\nA\.\s*([^\n]+?)\s*\nB\.\s*([^\n]+?)\s*\nC\.\s*([^\n]+?)\s*\nD\.\s*([^\n]+?)\s*\n【答案】\s*([A-Za-z,，、]+?)\s*\n【解析】\s*([^\n【]+?)(?:\n|$)'

    matches = re.findall(pattern, content, re.DOTALL)

    for match in matches:
        q_num, q_text, opt_a, opt_b, opt_c, opt_d, answer, explanation = match

        # 清理
        q_text = q_text.strip()
        opt_a = opt_a.strip()
        opt_b = opt_b.strip()
        opt_c = opt_c.strip()
        opt_d = opt_d.strip()
        answer = answer.strip().upper().replace('，', ',').replace('、', ',')
        explanation = explanation.strip()

        # 判断是否多选题（答案包含多个字母）
        is_multi = len(answer) > 1 and ',' in answer

        questions.append({
            'num': q_num,
            'text': q_text,
            'option_a': opt_a,
            'option_b': opt_b,
            'option_c': opt_c,
            'option_d': opt_d,
            'option_e': '',
            'answer': answer,
            'explanation': explanation,
            'is_multi': is_multi
        })

    return questions

def parse_md_file_with_fallback(content):
    """带后备的解析"""
    questions = parse_md_file(content)
    return questions

# 解析所有markdown文件
md_dir = Path("D:/yijian_exam_platform/pdf_md")
all_questions = []
file_stats = []

for md_file in sorted(md_dir.glob("*.md")):
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    questions = parse_md_file(content)
    file_stats.append((md_file.name, len(questions)))
    all_questions.extend(questions)

print("各文件解析结果:")
for name, count in file_stats:
    print(f"  {name}: {count} 题")
print(f"\n总共: {len(all_questions)} 道题目")

# 显示前3道
print("\n前3道题目示例:")
for q in all_questions[:3]:
    print(f"\nQ{q['num']}: {q['text'][:60]}...")
    print(f"  A: {q['option_a']}")
    print(f"  B: {q['option_b']}")
    print(f"  C: {q['option_c']}")
    print(f"  D: {q['option_d']}")
    print(f"  答案: {q['answer']}")
    print(f"  解析: {q['explanation'][:60]}...")

# 导入数据库
print("\n" + "="*50)
print("开始导入数据库...")
imported = 0

for q in all_questions:
    if not q['text'] or not q['answer']:
        continue

    category = "多选题" if q['is_multi'] else "单选题"

    try:
        add_question(
            category=category,
            question_text=q['text'],
            option_a=q['option_a'],
            option_b=q['option_b'],
            option_c=q['option_c'],
            option_d=q['option_d'],
            correct_answer=q['answer'],
            explanation=q['explanation'],
            difficulty=2
        )
        imported += 1
    except Exception as e:
        pass

print(f"成功导入: {imported} 道题目")