"""数据库操作模块"""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "data" / "exam.db"


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()

    # 题目表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            question_text TEXT NOT NULL,
            option_a TEXT NOT NULL,
            option_b TEXT NOT NULL,
            option_c TEXT NOT NULL,
            option_d TEXT NOT NULL,
            correct_answer TEXT NOT NULL,
            explanation TEXT,
            difficulty INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 答题记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS answer_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            user_answer TEXT NOT NULL,
            is_correct BOOLEAN NOT NULL,
            answered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    # 用户错题表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wrong_questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            wrong_count INTEGER DEFAULT 1,
            last_wrong_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mastered BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (question_id) REFERENCES questions(id)
        )
    """)

    conn.commit()
    conn.close()


def add_question(category, question_text, option_a, option_b, option_c, option_d,
                 correct_answer, explanation="", difficulty=1):
    """添加题目"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO questions (category, question_text, option_a, option_b, option_c,
                             option_d, correct_answer, explanation, difficulty)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (category, question_text, option_a, option_b, option_c, option_d,
          correct_answer, explanation, difficulty))
    conn.commit()
    question_id = cursor.lastrowid
    conn.close()
    return question_id


def get_all_questions():
    """获取所有题目"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions ORDER BY category, id")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def get_questions_by_category(category):
    """按分类获取题目"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE category = ?", (category,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def delete_question(question_id):
    """删除题目"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
    conn.commit()
    conn.close()


def update_question(question_id, **kwargs):
    """更新题目"""
    conn = get_connection()
    cursor = conn.cursor()
    allowed_fields = ['category', 'question_text', 'option_a', 'option_b',
                     'option_c', 'option_d', 'correct_answer', 'explanation', 'difficulty']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields}
    if updates:
        set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
        values = list(updates.values()) + [question_id]
        cursor.execute(f"UPDATE questions SET {set_clause} WHERE id = ?", values)
        conn.commit()
    conn.close()


def save_answer_record(question_id, user_answer, is_correct):
    """保存答题记录"""
    conn = get_connection()
    cursor = conn.cursor()

    # 记录答题
    cursor.execute("""
        INSERT INTO answer_records (question_id, user_answer, is_correct)
        VALUES (?, ?, ?)
    """, (question_id, user_answer, is_correct))

    # 更新错题表
    if not is_correct:
        cursor.execute("""
            SELECT id FROM wrong_questions WHERE question_id = ?
        """, (question_id,))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
                UPDATE wrong_questions
                SET wrong_count = wrong_count + 1, last_wrong_at = ?
                WHERE question_id = ?
            """, (datetime.now(), question_id))
        else:
            cursor.execute("""
                INSERT INTO wrong_questions (question_id, wrong_count, last_wrong_at)
                VALUES (?, 1, ?)
            """, (question_id, datetime.now()))
    else:
        # 答对了，从错题移除
        cursor.execute("""
            DELETE FROM wrong_questions WHERE question_id = ?
        """, (question_id,))

    conn.commit()
    conn.close()


def get_wrong_questions():
    """获取错题列表"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.*, q.* FROM wrong_questions w
        JOIN questions q ON w.question_id = q.id
        WHERE w.mastered = FALSE
        ORDER BY w.wrong_count DESC, w.last_wrong_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]


def mark_question_mastered(question_id):
    """标记题目已掌握"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE wrong_questions SET mastered = TRUE WHERE question_id = ?
    """, (question_id,))
    conn.commit()
    conn.close()


def get_statistics():
    """获取统计数据"""
    conn = get_connection()
    cursor = conn.cursor()

    # 总题目数
    cursor.execute("SELECT COUNT(*) as total FROM questions")
    total_questions = cursor.fetchone()['total']

    # 已掌握错题数
    cursor.execute("SELECT COUNT(*) as mastered FROM wrong_questions WHERE mastered = TRUE")
    mastered = cursor.fetchone()['mastered']

    # 未掌握错题数
    cursor.execute("SELECT COUNT(*) as not_mastered FROM wrong_questions WHERE mastered = FALSE")
    not_mastered = cursor.fetchone()['not_mastered']

    # 分类统计
    cursor.execute("""
        SELECT category,
               COUNT(*) as total,
               SUM(CASE WHEN id IN (SELECT question_id FROM wrong_questions WHERE mastered = FALSE) THEN 1 ELSE 0 END) as wrong_count
        FROM questions
        GROUP BY category
    """)
    category_stats = [dict(row) for row in cursor.fetchall()]

    # 难度分布
    cursor.execute("""
        SELECT difficulty, COUNT(*) as count
        FROM questions
        GROUP BY difficulty
    """)
    difficulty_stats = [dict(row) for row in cursor.fetchall()]

    # 最近正确率趋势（最近10次）
    cursor.execute("""
        SELECT date(answered_at) as date,
               ROUND(CAST(SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) * 100, 1) as accuracy
        FROM answer_records
        GROUP BY date(answered_at)
        ORDER BY date DESC
        LIMIT 10
    """)
    accuracy_trend = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'total_questions': total_questions,
        'mastered': mastered,
        'not_mastered': not_mastered,
        'category_stats': category_stats,
        'difficulty_stats': difficulty_stats,
        'accuracy_trend': accuracy_trend
    }


def get_category_list():
    """获取所有分类"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT DISTINCT category FROM questions ORDER BY category")
    categories = [row['category'] for row in cursor.fetchall()]
    conn.close()
    return categories


def import_sample_questions():
    """导入示例题目（一建法规）"""
    sample_questions = [
        {
            'category': '法规',
            'question_text': '根据《建筑法》，关于建筑工程施工许可的说法，正确的是（）',
            'option_a': '申领施工许可证需具备的条件之一是已确定施工企业',
            'option_b': '施工许可证由建设单位申领',
            'option_c': '施工许可证应当在签订施工合同前申领',
            'option_d': '申领施工许可证应当有保证工程质量和安全的具体措施',
            'correct_answer': 'B',
            'explanation': '《建筑法》规定，申请领取施工许可证，应当具备下列条件：（1）已经办理该建筑工程用地批准手续；（2）依法应当办理建设工程规划许可证的，已经取得规划许可证；（3）需要拆迁的，其拆迁进度符合施工要求；（4）已经确定建筑施工企业；（5）有满足施工需要的资金安排、施工图纸及技术资料；（6）有保证工程质量和安全的具体措施。',
            'difficulty': 2
        },
        {
            'category': '法规',
            'question_text': '下列关于投标的说法，正确的是（）',
            'option_a': '投标人在招标文件要求提交投标文件的截止时间前，可以补充、修改或撤回已提交的投标文件',
            'option_b': '两个以上法人可以组成联合体以一个投标人的身份共同投标',
            'option_c': '投标人不得以低于成本的报价竞标',
            'option_d': '以上都对',
            'correct_answer': 'D',
            'explanation': '根据《招标投标法》，投标人在招标文件要求提交投标文件的截止时间前，可以补充、修改或撤回已提交的投标文件；两个以上法人可以组成联合体以一个投标人的身份共同投标；投标人不得以低于成本的报价竞标。',
            'difficulty': 1
        },
        {
            'category': '法规',
            'question_text': '建设工程施工合同无效，但工程经竣工验收合格，关于工程款支付的说法，正确的是（）',
            'option_a': '参照合同约定支付工程价款',
            'option_b': '承包人无权请求参照合同约定支付工程价款',
            'option_c': '发包人应当参照市场价支付工程价款',
            'option_d': '以上都不对',
            'correct_answer': 'A',
            'explanation': '《最高人民法院关于审理建设工程施工合同纠纷案件适用法律问题的解释》规定，建设工程施工合同无效，但工程经竣工验收合格，承包人请求参照合同约定支付工程价款的，应予支持。',
            'difficulty': 3
        },
        {
            'category': '管理',
            'question_text': '项目管理组织结构图反映的是（）',
            'option_a': '工作流程组织',
            'option_b': '组织分工',
            'option_c': '物质流程组织',
            'option_d': '信息流程组织',
            'correct_answer': 'B',
            'explanation': '项目管理组织结构图反映的是组织分工，即各工作部门或各工作岗位之间的分工关系。工作流程组织反映的是逻辑关系。',
            'difficulty': 2
        },
        {
            'category': '管理',
            'question_text': '根据《建设工程项目管理规范》GB/T 50326-2017，项目管理规划的编制依据不包括（）',
            'option_a': '适用的法律、法规及标准',
            'option_b': '项目的目标',
            'option_c': '类似项目经验',
            'option_d': '项目策划的结果',
            'correct_answer': 'D',
            'explanation': '项目管理规划的编制依据包括：（1）适用的法律、法规及标准；（2）项目目标及相关要求；（3）项目的设计文件；（4）类似项目经验；（5）项目所在地的环境条件；（6）其他相关信息。',
            'difficulty': 2
        },
        {
            'category': '管理',
            'question_text': '施工成本管理的基础工作不包括（）',
            'option_a': '建立成本管理责任体系',
            'option_b': '加强质量监督',
            'option_c': '加强预算管理',
            'option_d': '建立施工台账',
            'correct_answer': 'B',
            'explanation': '施工成本管理的基础工作包括：建立成本管理责任体系、加强预算管理、建立施工台账、设计概算、施工定额等。质量监督不属于成本管理基础工作。',
            'difficulty': 1
        },
        {
            'category': '实务',
            'question_text': '钢筋混凝土结构中，钢筋的连接方式不包括（）',
            'option_a': '焊接连接',
            'option_b': '机械连接',
            'option_c': '绑扎连接',
            'option_d': '铆钉连接',
            'correct_answer': 'D',
            'explanation': '钢筋混凝土结构中钢筋的连接方式主要有：焊接连接（包括电弧焊、电渣压力焊、闪光对焊等）、机械连接（套筒连接）、绑扎连接。铆钉连接是钢结构连接方式。',
            'difficulty': 1
        },
        {
            'category': '实务',
            'question_text': '关于混凝土施工缝的留置方法，正确的是（）',
            'option_a': '应留在剪力较小且便于施工的部位',
            'option_b': '柱应留在基础的顶面',
            'option_c': '单向板应留在平行于短边的任何位置',
            'option_d': '有主次梁的楼板，施工缝应留在主梁跨中1/3范围内',
            'correct_answer': 'A',
            'explanation': '施工缝的留置位置应符合下列规定：（1）柱：宜留置在基础、楼板、梁的顶面，梁和吊车梁牛腿、无梁楼板柱帽的下面；（2）与板连成整体的大截面梁，留置在板底面以下20～30mm处；（3）单向板：留置在平行于板的短边的任何位置；（4）有主次梁的楼板，施工缝应留在次梁跨中1/3范围内。',
            'difficulty': 3
        },
        {
            'category': '法规',
            'question_text': '根据《安全生产法》，生产经营单位的安全生产管理人员应当履行的职责不包括（）',
            'option_a': '组织制定本单位安全生产规章制度',
            'option_b': '督促落实本单位重大危险源的安全管理措施',
            'option_c': '组织或者参与本单位应急救援演练',
            'option_d': '制止和纠正违章指挥、强令冒险作业、违反操作规程的行为',
            'correct_answer': 'A',
            'explanation': '《安全生产法》第二十五条规定，生产经营单位的安全生产管理人员应当：（1）组织或者参与拟订本单位安全生产规章制度、操作规程和生产安全事故应急救援预案；（2）组织或者参与本单位安全生产教育和培训；（3）督促落实本单位重大危险源的安全管理措施；（4）组织或者参与本单位应急救援演练；（5）制止和纠正违章指挥、强令冒险作业、违反操作规程的行为；（6）依法应履行的其他职责。',
            'difficulty': 2
        },
        {
            'category': '管理',
            'question_text': '双代号时标网络计划中，波形线表示（）',
            'option_a': '工作的自由时差',
            'option_b': '工作的总时差',
            'option_c': '工作的持续时间',
            'option_d': '工作之间的逻辑关系',
            'correct_answer': 'A',
            'explanation': '双代号时标网络计划中，波形线表示工作的自由时差，即在紧后工作最早开始时间确定的前提下，该工作可以延迟开始的时间。',
            'difficulty': 2
        }
    ]

    conn = get_connection()
    cursor = conn.cursor()

    # 检查是否已有题目
    cursor.execute("SELECT COUNT(*) FROM questions")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    for q in sample_questions:
        cursor.execute("""
            INSERT INTO questions (category, question_text, option_a, option_b, option_c,
                                 option_d, correct_answer, explanation, difficulty)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (q['category'], q['question_text'], q['option_a'], q['option_b'],
              q['option_c'], q['option_d'], q['correct_answer'],
              q['explanation'], q['difficulty']))

    conn.commit()
    conn.close()
