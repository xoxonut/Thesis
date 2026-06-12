import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

with open('exact_matches.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

for i, p in enumerate(papers):
    print(f"[{i+1}] {p['title']} ({p['year']})")
    print(f"    Authors: {', '.join(p['authors'])}")
    print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
    print(f"    DOI: {p['doi']}")
    print(f"    Abstract: {p['abstract']}")
    print("=" * 60)
