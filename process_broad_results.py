import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

with open('active_hidden_detection_broad.json', 'r', encoding='utf-8') as f:
    papers = json.load(f)

print(f"Total papers found in broad search: {len(papers)}")

filtered = []
for p in papers:
    title = p.get('title', '').lower()
    abstract = p.get('abstract', '').lower()
    full_text = title + " " + abstract
    
    # Check if this is about WiFi/Wireless hidden nodes/terminals
    is_hidden = any(w in full_text for w in ["hidden node", "hidden terminal", "hidden station", "hidden device"])
    is_wifi = any(w in full_text for w in ["wifi", "wi-fi", "802.11", "wlan", "wireless", "sensor network", "mesh"])
    
    # Check for active detection/probing/RSSI
    is_rssi_csi = any(w in full_text for w in ["rssi", "rss ", "signal strength", "received signal", "channel state", "csi"])
    is_active_probing = any(w in full_text for w in ["active", "probe", "probing", "actively", "request", "cts", "rts"])
    
    if is_hidden and is_wifi and (is_rssi_csi or is_active_probing):
        filtered.append(p)

print(f"Filtered to {len(filtered)} relevant papers.")

for i, p in enumerate(filtered[:20]):
    print(f"[{i+1}] {p['title']} ({p['year']})")
    print(f"    Authors: {', '.join(p['authors'])}")
    print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
    print(f"    DOI: {p['doi']}")
    print(f"    Abstract snippet: {p['abstract'][:300]}...")
    print("-" * 50)
