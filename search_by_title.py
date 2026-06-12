import urllib.request
import urllib.parse
import json
import sys

# Reconfigure stdout to support UTF-8 printing in Windows terminal
if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def search_openalex_title(title_query, mailto="antigravity@google.com"):
    # Filter works by title containing the keywords
    # Using openalex filter syntax: title.search: "hidden terminal" or title.search: "hidden node"
    encoded_title = urllib.parse.quote_plus(title_query)
    url = f"https://api.openalex.org/works?filter=title.search:{encoded_title}&sort=cited_by_count:desc&per_page=50&mailto={mailto}"
    print(f"Querying: {url}")
    
    headers = {
        'User-Agent': 'AntigravityAgent/1.0 (mailto:antigravity@google.com)'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except Exception as e:
        print(f"Error: {e}")
        return []

def main():
    papers_node = search_openalex_title("hidden node")
    papers_term = search_openalex_title("hidden terminal")
    
    all_papers = papers_node + papers_term
    
    # Deduplicate by id
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p['id'] not in seen:
            unique_papers.append(p)
            seen.add(p['id'])
            
    print(f"Found {len(unique_papers)} unique papers with 'hidden node' or 'hidden terminal' in title.")
    
    # Filter for active detection / RSSI
    filtered_papers = []
    for paper in unique_papers:
        title = paper.get('display_name', '').lower()
        
        # Extract abstract
        abstract_index = paper.get('abstract_inverted_index', None)
        abstract = ""
        if abstract_index:
            word_list = []
            for word, positions in abstract_index.items():
                for pos in positions:
                    word_list.append((pos, word))
            word_list.sort()
            abstract = " ".join([word for pos, word in word_list]).lower()
            
        full_text = title + " " + abstract
        
        # Check if the paper is related to WiFi/802.11 AND RSSI/signal strength or active/probing/detection
        is_wifi = any(w in full_text for w in ["wifi", "wi-fi", "802.11", "wlan", "wireless"])
        is_rssi = any(w in full_text for w in ["rssi", "rss", "signal strength", "received signal", "power", "channel state", "csi"])
        is_active = any(w in full_text for w in ["active", "probe", "probing", "actively", "request", "cts", "rts"])
        
        if is_wifi and (is_rssi or is_active):
            authors = [auth.get('author', {}).get('display_name', 'Unknown') for auth in paper.get('authorships', [])]
            primary_loc = paper.get('primary_location') or {}
            source = primary_loc.get('source') or {}
            venue = source.get('display_name', 'Unknown Venue')
            
            filtered_papers.append({
                'title': paper.get('display_name', 'No Title'),
                'authors': authors,
                'year': paper.get('publication_year', 'Unknown'),
                'venue': venue,
                'citations': paper.get('cited_by_count', 0),
                'doi': paper.get('doi', ''),
                'abstract': abstract[:500] + "..." if len(abstract) > 500 else abstract,
                'url': paper.get('id', ''),
                'has_rssi': is_rssi,
                'has_active': is_active
            })
            
    # Sort by citations desc
    filtered_papers.sort(key=lambda x: x['citations'], reverse=True)
    
    print(f"Filtered to {len(filtered_papers)} relevant papers.")
    
    # Save the output
    with open('filtered_hidden_node_papers.json', 'w', encoding='utf-8') as f:
        json.dump(filtered_papers, f, indent=2, ensure_ascii=False)
        
    for i, p in enumerate(filtered_papers[:15]):
        print(f"[{i+1}] {p['title']} ({p['year']})")
        print(f"    Authors: {', '.join(p['authors'])}")
        print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
        print(f"    URL: {p['url']}")
        print("-" * 50)

if __name__ == '__main__':
    main()
