import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

with open('active_hidden_detection_broad.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

print(f"Total: {len(papers)}")
for i, p in enumerate(papers[:50]):
    print(f"[{i+1}] {p['title']} ({p['year']}) - Citations: {p['citations']}")
