import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

with open('filtered_hidden_node_papers.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

print(f"Total filtered papers: {len(papers)}")

print("\n--- PAPERS CONTAINING 'rssi' OR 'rss' or 'signal strength' ---")
rssi_papers = []
for p in papers:
    abstract = p.get('abstract', '').lower()
    title = p.get('title', '').lower()
    if 'rssi' in abstract or 'rssi' in title or 'rss ' in abstract or 'signal strength' in abstract or 'signal strength' in title:
        rssi_papers.append(p)

for i, p in enumerate(rssi_papers):
    print(f"[{i+1}] {p['title']} ({p['year']})")
    print(f"    Authors: {', '.join(p['authors'])}")
    print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
    print(f"    URL: {p['url']}")
    print(f"    Abstract snippet: {p['abstract'][:300]}...")
    print("-" * 50)

print("\n--- PAPERS CONTAINING 'active' OR 'probe' OR 'probing' ---")
active_papers = []
for p in papers:
    abstract = p.get('abstract', '').lower()
    title = p.get('title', '').lower()
    if 'active' in abstract or 'active' in title or 'probe' in abstract or 'probe' in title or 'probing' in abstract or 'probing' in title:
        active_papers.append(p)

for i, p in enumerate(active_papers):
    if p not in rssi_papers: # don't repeat if already shown
        print(f"[{i+1}] {p['title']} ({p['year']})")
        print(f"    Authors: {', '.join(p['authors'])}")
        print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
        print(f"    URL: {p['url']}")
        print(f"    Abstract snippet: {p['abstract'][:300]}...")
        print("-" * 50)
