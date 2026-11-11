import re
from pathlib import Path

patterns = [
    '0.8591', '87.69', '60.38', '98.67', '125', '441', '6.02', '399,597', 
    '188 pages', '0.7234', '78.46', '95.94%', '86.77%', '1420.0', '145.2',
    'zero hallucination', '100% citation integrity', 'hallucination-free'
]

files = [
    Path('docs/camera_ready_paper.tex'),
    Path('docs/REVISED_RESEARCH_PAPER_ICICF2027.md'),
    Path('docs/RESPONSE_TO_REVIEWERS.md')
]

for f in files:
    if not f.exists():
        continue
    content = f.read_text(encoding='utf-8')
    print(f"\n=== {f} ===")
    for pat in patterns:
        count = len(re.findall(re.escape(pat), content, re.IGNORECASE))
        if count > 0:
            print(f"  '{pat}': {count} occurrences")

