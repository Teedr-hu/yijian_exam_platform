import json
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

with open('extracted_pptx.json', 'r', encoding='utf-8') as f:
    slides = json.load(f)

def get_slide_num(s):
    m = re.search(r'slide(\d+)', s['slide'])
    return int(m.group(1)) if m else 0

slides.sort(key=get_slide_num)

# 查找多选题
for i, s in enumerate(slides):
    if '二、多项选择题 21' in s['text']:
        print(f'Found multi-choice at slide {i}: {s["slide"]}')
        for j in range(i, min(i+8, len(slides))):
            print(f'{slides[j]["slide"]}: {slides[j]["text"][:200]}')
            print()
        break