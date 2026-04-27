import subprocess
import os
from pathlib import Path

# 搜索包含题目的PDF
base_dir = Path("D:/2026一建【建筑】SVIP")
pdf_files = []

# 关键词：真题、习题、练习、模考、考点
keywords = ['真题', '习题', '练习', '模考', '考点', '考题']

for pdf in base_dir.rglob("*.pdf"):
    name = pdf.stem.lower()
    # 跳过视频PDF
    if '.mp4' in str(pdf) or 'mp4' in name:
        continue
    # 跳过讲义类（除非包含关键词）
    if any(kw in pdf.name for kw in keywords):
        pdf_files.append(pdf)

print(f"找到 {len(pdf_files)} 个可能包含题目的PDF文件:")
for p in pdf_files[:20]:
    print(f"  {p.name[:50]}")
if len(pdf_files) > 20:
    print(f"  ... 还有 {len(pdf_files) - 20} 个")

# 转换PDF到MD
output_dir = Path("D:/yijian_exam_platform/pdf_md")
output_dir.mkdir(exist_ok=True)

converted = 0
failed = []

for pdf_path in pdf_files:
    md_name = pdf_path.stem + ".md"
    md_path = output_dir / md_name

    # 跳过已转换的
    if md_path.exists():
        print(f"跳过(已存在): {pdf_path.name[:40]}")
        converted += 1
        continue

    try:
        print(f"转换: {pdf_path.name[:40]}...", end=" ", flush=True)
        result = subprocess.run(
            ["py", "-m", "markitdown", str(pdf_path), "-o", str(md_path)],
            capture_output=True,
            text=True,
            timeout=120
        )
        if md_path.exists() and md_path.stat().st_size > 100:
            converted += 1
            print(f"成功 ({md_path.stat().st_size // 1024}KB)")
        else:
            failed.append(pdf_path.name)
            print(f"失败")
    except Exception as e:
        failed.append(pdf_path.name)
        print(f"异常: {e}")

print(f"\n完成! 成功: {converted}, 失败: {len(failed)}")
if failed:
    print("失败的文件:")
    for f in failed[:10]:
        print(f"  {f}")