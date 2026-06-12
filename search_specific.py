import urllib.request
import urllib.parse
import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def get_exact_paper(title, mailto="antigravity@google.com"):
    encoded_title = urllib.parse.quote_plus(f'"{title}"')
    url = f"https://api.openalex.org/works?filter=title.search:{encoded_title}&mailto={mailto}"
    
    headers = {
        'User-Agent': 'AntigravityAgent/1.0 (mailto:antigravity@google.com)'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except Exception as e:
        print(f"Error searching for '{title}': {e}")
        return []

def main():
    titles = [
        "Passive and Active Hidden Terminal Detection in 802.11-based Ad Hoc Networks",
        "Detecting Hidden and Exposed Terminal Problems in Densely Deployed Wireless Networks",
        "Detection and Localization of Hidden IoT Devices",
        "Active detection of hidden terminals",
        "A novel hidden station detection mechanism in IEEE 802.11 WLAN",
        "Hidden terminal detection",
        "Active hidden terminal detection",
        "RSSI-based hidden node detection"
    ]
    
    results = []
    seen = set()
    for t in titles:
        papers = get_exact_paper(t)
        for p in papers:
            if p['id'] not in seen:
                seen.add(p['id'])
                
                authors = [auth.get('author', {}).get('display_name', 'Unknown') for auth in p.get('authorships', [])]
                primary_loc = p.get('primary_location') or {}
                source = primary_loc.get('source') or {}
                venue = source.get('display_name', 'Unknown Venue')
                doi = p.get('doi', '')
                citations = p.get('cited_by_count', 0)
                year = p.get('publication_year', 'Unknown')
                title = p.get('display_name', 'No Title')
                
                abstract_index = p.get('abstract_inverted_index', None)
                abstract = ""
                if abstract_index:
                    word_list = []
                    for word, positions in abstract_index.items():
                        for pos in positions:
                            word_list.append((pos, word))
                    word_list.sort()
                    abstract = " ".join([word for pos, word in word_list])
                    
                results.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': venue,
                    'citations': citations,
                    'doi': doi,
                    'abstract': abstract,
                    'url': p['id']
                })
                
    print(f"Found {len(results)} exact match papers.")
    with open('exact_matches.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    for i, p in enumerate(results):
        print(f"[{i+1}] {p['title']} ({p['year']})")
        print(f"    Authors: {', '.join(p['authors'])}")
        print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
        print(f"    DOI: {p['doi']}")
        print(f"    URL: {p['url']}")
        print("-" * 50)

if __name__ == '__main__':
    main()
