# -*- coding: utf-8 -*-
"""题库导入模块"""
import os
import re
import pandas as pd
from pathlib import Path

try:
    from docx import Document as DocxDocument
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from database import add_question

IMPORT_FOLDER = Path(__file__).parent / "import"


def get_import_files():
    """获取可导入的文件"""
    if not IMPORT_FOLDER.exists():
        return []

    supported_formats = ['.xlsx', '.xls', '.csv', '.txt', '.docx', '.pdf']
    files = []
    for f in IMPORT_FOLDER.iterdir():
        if f.suffix.lower() in supported_formats:
            files.append(f)
    return files


def import_from_excel(file_path):
    """从Excel文件导入"""
    questions = []
    try:
        excel_file = pd.ExcelFile(file_path)
        for sheet_name in excel_file.sheet_names:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            questions.extend(parse_dataframe(df))
    except Exception as e:
        print(f"读取Excel失败: {e}")
    return questions


def import_from_csv(file_path):
    """从CSV文件导入"""
    questions = []
    for encoding in ['utf-8', 'gbk', 'gb2312']:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            questions.extend(parse_dataframe(df))
            break
        except:
            continue
    return questions


def import_from_txt(file_path):
    """从Txt文件导入"""
    questions = []
    for encoding in ['utf-8', 'gbk', 'gb2312']:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    parts = [p.strip() for p in re.split(r'[|\t]', line)]
                    if len(parts) >= 7:
                        q = {
                            'category': parts[0] if parts[0] else '未分类',
                            'question_text': parts[1] if parts[1] else '',
                            'option_a': parts[2] if parts[2] else '',
                            'option_b': parts[3] if parts[3] else '',
                            'option_c': parts[4] if parts[4] else '',
                            'option_d': parts[5] if parts[5] else '',
                            'correct_answer': parts[6].upper() if parts[6] else '',
                            'explanation': parts[7] if len(parts) > 7 and parts[7] else '',
                            'difficulty': int(parts[8]) if len(parts) > 8 and parts[8].isdigit() else 1
                        }
                        if q['question_text'] and q['correct_answer']:
                            questions.append(q)
            break
        except:
            continue
    return questions


def import_from_docx(file_path):
    """从Word文件导入"""
    questions = []
    if not DOCX_AVAILABLE:
        print("python-docx未安装")
        return questions

    try:
        doc = DocxDocument(file_path)
        current_category = '未分类'
        current_question = None
        options = []
        correct_answer = ''
        explanation = ''
        difficulty = 1

        for para in doc.paragraphs:
            text = para.text.strip()
            if not text:
                continue

            # 检测是否为分类标题（格式：第X章 或 【分类名】）
            if re.match(r'^[第章节部]\s*\S|^\[.*\]$|^【.*】$', text):
                current_category = re.sub(r'^[第章节部]\s*\S+\s*', '', text).strip('[]【】')
                continue

            # 检测是否为题目
            # 常见格式：1. 题目内容 或 题目内容（题目带括号的）
            if re.match(r'^\d+[.、:：]', text) or '（' in text or '(' in text:
                # 保存上一题
                if current_question and correct_answer:
                    q = {
                        'category': current_category,
                        'question_text': current_question,
                        'option_a': options[0] if len(options) > 0 else '',
                        'option_b': options[1] if len(options) > 1 else '',
                        'option_c': options[2] if len(options) > 2 else '',
                        'option_d': options[3] if len(options) > 3 else '',
                        'correct_answer': correct_answer.upper(),
                        'explanation': explanation,
                        'difficulty': difficulty
                    }
                    if all([q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer']]):
                        questions.append(q)

                # 开始新题目
                # 提取题目文本
                match = re.match(r'^\d+[.、:：]\s*(.+)', text)
                if match:
                    current_question = match.group(1).strip()
                else:
                    current_question = text
                options = []
                correct_answer = ''
                explanation = ''
                difficulty = 1
                continue

            # 检测是否为选项
            opt_match = re.match(r'^([A-D])[.、:：]\s*(.+)', text, re.IGNORECASE)
            if opt_match:
                options.append(opt_match.group(2).strip())
                continue

            # 检测答案（格式：答案：A 或 正确答案：A）
            ans_match = re.search(r'答案[是为：:\s]*([A-D])', text, re.IGNORECASE)
            if ans_match:
                correct_answer = ans_match.group(1).upper()
                continue

            # 检测解析
            if '解析' in text or '答案分析' in text:
                explanation = re.sub(r'^[解析答案分析：:\s]+', '', text).strip()
                continue

            # 检测难度
            diff_match = re.search(r'难度[是为：:\s]*(\d)', text)
            if diff_match:
                difficulty = int(diff_match.group(1))
                continue

        # 保存最后一题
        if current_question and correct_answer:
            q = {
                'category': current_category,
                'question_text': current_question,
                'option_a': options[0] if len(options) > 0 else '',
                'option_b': options[1] if len(options) > 1 else '',
                'option_c': options[2] if len(options) > 2 else '',
                'option_d': options[3] if len(options) > 3 else '',
                'correct_answer': correct_answer.upper(),
                'explanation': explanation,
                'difficulty': difficulty
            }
            if all([q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer']]):
                questions.append(q)

    except Exception as e:
        print(f"读取Word失败: {e}")

    return questions


def import_from_pdf(file_path):
    """从PDF文件导入"""
    questions = []
    if not PDF_AVAILABLE:
        print("pdfplumber未安装")
        return questions

    try:
        with pdfplumber.open(file_path) as pdf:
            current_category = '未分类'
            current_question = None
            options = []
            correct_answer = ''
            explanation = ''
            difficulty = 1
            buffer = []

            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split('\n')
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # 检测是否为分类标题
                    if re.match(r'^[第章节部]\s*\S|^\[.*\]$|^【.*】$', line):
                        current_category = re.sub(r'^[第章节部]\s*\S+\s*', '', line).strip('[]【】')
                        continue

                    # 检测是否为题目
                    if re.match(r'^\d+[.、:：]', line) or ('（' in line and '）' in line):
                        # 保存上一题
                        if current_question and correct_answer:
                            q = {
                                'category': current_category,
                                'question_text': current_question,
                                'option_a': options[0] if len(options) > 0 else '',
                                'option_b': options[1] if len(options) > 1 else '',
                                'option_c': options[2] if len(options) > 2 else '',
                                'option_d': options[3] if len(options) > 3 else '',
                                'correct_answer': correct_answer.upper(),
                                'explanation': explanation,
                                'difficulty': difficulty
                            }
                            if all([q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer']]):
                                questions.append(q)

                        # 开始新题目
                        match = re.match(r'^\d+[.、:：]\s*(.+)', line)
                        if match:
                            current_question = match.group(1).strip()
                        else:
                            current_question = line
                        options = []
                        correct_answer = ''
                        explanation = ''
                        difficulty = 1
                        continue

                    # 检测是否为选项
                    opt_match = re.match(r'^([A-D])[.、:：]\s*(.+)', line, re.IGNORECASE)
                    if opt_match:
                        options.append(opt_match.group(2).strip())
                        continue

                    # 检测答案
                    ans_match = re.search(r'答案[是为：:\s]*([A-D])', line, re.IGNORECASE)
                    if ans_match:
                        correct_answer = ans_match.group(1).upper()
                        continue

                    # 检测解析
                    if '解析' in line or '答案分析' in line:
                        explanation = re.sub(r'^[解析答案分析：:\s]+', '', line).strip()
                        continue

            # 保存最后一题
            if current_question and correct_answer:
                q = {
                    'category': current_category,
                    'question_text': current_question,
                    'option_a': options[0] if len(options) > 0 else '',
                    'option_b': options[1] if len(options) > 1 else '',
                    'option_c': options[2] if len(options) > 2 else '',
                    'option_d': options[3] if len(options) > 3 else '',
                    'correct_answer': correct_answer.upper(),
                    'explanation': explanation,
                    'difficulty': difficulty
                }
                if all([q['question_text'], q['option_a'], q['option_b'], q['option_c'], q['option_d'], q['correct_answer']]):
                    questions.append(q)

    except Exception as e:
        print(f"读取PDF失败: {e}")

    return questions


def parse_dataframe(df):
    """解析DataFrame为题目列表"""
    questions = []
    columns = df.columns.tolist()
    col_mapping = {}

    for col in columns:
        col_lower = str(col).lower()
        if '分类' in col or 'category' in col_lower:
            col_mapping['category'] = col
        elif '题目' in col or 'question' in col_lower or 'content' in col_lower:
            col_mapping['question_text'] = col
        elif 'a' in col_lower and '选项' not in col and 'answer' not in col_lower:
            col_mapping['option_a'] = col
        elif 'b' in col_lower and '选项' not in col and 'answer' not in col_lower:
            col_mapping['option_b'] = col
        elif 'c' in col_lower and '选项' not in col and 'answer' not in col_lower:
            col_mapping['option_c'] = col
        elif 'd' in col_lower and '选项' not in col and 'answer' not in col_lower:
            col_mapping['option_d'] = col
        elif '答案' in col or 'answer' in col_lower:
            col_mapping['correct_answer'] = col
        elif '解析' in col or 'explanation' in col_lower:
            col_mapping['explanation'] = col
        elif '难度' in col or 'difficulty' in col_lower:
            col_mapping['difficulty'] = col

    # 使用前几列作为默认值
    if not col_mapping.get('question_text') and len(columns) >= 2:
        col_mapping['category'] = columns[0]
        col_mapping['question_text'] = columns[1]
    if not col_mapping.get('option_a') and len(columns) >= 3:
        col_mapping['option_a'] = columns[2]
    if not col_mapping.get('option_b') and len(columns) >= 4:
        col_mapping['option_b'] = columns[3]
    if not col_mapping.get('option_c') and len(columns) >= 5:
        col_mapping['option_c'] = columns[4]
    if not col_mapping.get('option_d') and len(columns) >= 6:
        col_mapping['option_d'] = columns[5]
    if not col_mapping.get('correct_answer') and len(columns) >= 7:
        col_mapping['correct_answer'] = columns[6]

    for _, row in df.iterrows():
        try:
            q = {
                'category': str(row.get(col_mapping.get('category', ''))).strip() or '未分类',
                'question_text': str(row.get(col_mapping.get('question_text', ''))).strip(),
                'option_a': str(row.get(col_mapping.get('option_a', ''))).strip(),
                'option_b': str(row.get(col_mapping.get('option_b', ''))).strip(),
                'option_c': str(row.get(col_mapping.get('option_c', ''))).strip(),
                'option_d': str(row.get(col_mapping.get('option_d', ''))).strip(),
                'correct_answer': str(row.get(col_mapping.get('correct_answer', ''))).strip().upper(),
                'explanation': str(row.get(col_mapping.get('explanation', ''))).strip(),
                'difficulty': int(row.get(col_mapping.get('difficulty', 1))) if str(row.get(col_mapping.get('difficulty', 1))).isdigit() else 1
            }
            if q['question_text'] and q['option_a'] and q['option_b'] and q['option_c'] and q['option_d'] and q['correct_answer']:
                questions.append(q)
        except:
            continue

    return questions


def import_all_files():
    """导入import文件夹中的所有文件"""
    files = get_import_files()
    total_imported = 0
    details = []
    errors = []

    for file_path in files:
        questions = []
        suffix = file_path.suffix.lower()

        if suffix in ['.xlsx', '.xls']:
            questions = import_from_excel(file_path)
        elif suffix == '.csv':
            questions = import_from_csv(file_path)
        elif suffix == '.txt':
            questions = import_from_txt(file_path)
        elif suffix == '.docx':
            questions = import_from_docx(file_path)
        elif suffix == '.pdf':
            questions = import_from_pdf(file_path)

        imported_count = 0
        for q in questions:
            try:
                add_question(
                    category=q['category'],
                    question_text=q['question_text'],
                    option_a=q['option_a'],
                    option_b=q['option_b'],
                    option_c=q['option_c'],
                    option_d=q['option_d'],
                    correct_answer=q['correct_answer'],
                    explanation=q['explanation'],
                    difficulty=q['difficulty']
                )
                imported_count += 1
            except Exception as e:
                errors.append(f"{file_path.name}: {str(e)}")

        total_imported += imported_count
        details.append(f"{file_path.name}: {imported_count}道")

    return total_imported, details, errors


if __name__ == "__main__":
    count, details, errors = import_all_files()
    print(f"共导入 {count} 道题目")
    for d in details:
        print(f"  - {d}")
    if errors:
        print(f"错误: {errors}")
