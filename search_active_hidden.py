import urllib.request
import urllib.parse
import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def search_openalex_broad(query, mailto="antigravity@google.com"):
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://api.openalex.org/works?search={encoded_query}&sort=cited_by_count:desc&per_page=50&mailto={mailto}"
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
    queries = [
        '"hidden terminal" active detection',
        '"hidden node" active detection',
        '"hidden terminal" RSSI active',
        '"hidden node" RSSI active',
        'active detection "hidden terminal" wifi',
        'active detection "hidden node" wifi'
    ]
    
    all_results = []
    seen_ids = set()
    
    for q in queries:
        results = search_openalex_broad(q)
        for paper in results:
            pid = paper.get('id')
            if pid not in seen_ids:
                seen_ids.add(pid)
                
                # Format paper
                authors = [auth.get('author', {}).get('display_name', 'Unknown') for auth in paper.get('authorships', [])]
                primary_loc = paper.get('primary_location') or {}
                source = primary_loc.get('source') or {}
                venue = source.get('display_name', 'Unknown Venue')
                doi = paper.get('doi', '')
                citations = paper.get('cited_by_count', 0)
                year = paper.get('publication_year', 'Unknown')
                title = paper.get('display_name', 'No Title')
                
                # Extract abstract
                abstract_index = paper.get('abstract_inverted_index', None)
                abstract = ""
                if abstract_index:
                    word_list = []
                    for word, positions in abstract_index.items():
                        for pos in positions:
                            word_list.append((pos, word))
                    word_list.sort()
                    abstract = " ".join([word for pos, word in word_list])
                    
                all_results.append({
                    'title': title,
                    'authors': authors,
                    'year': year,
                    'venue': venue,
                    'citations': citations,
                    'doi': doi,
                    'abstract': abstract,
                    'url': pid
                })
                
    # Sort by citations
    all_results.sort(key=lambda x: x['citations'], reverse=True)
    
    print(f"\nFound {len(all_results)} papers in total.")
    with open('active_hidden_detection_broad.json', 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
        
    for i, p in enumerate(all_results[:20]):
        print(f"[{i+1}] {p['title']} ({p['year']})")
        print(f"    Authors: {', '.join(p['authors'])}")
        print(f"    Venue: {p['venue']} | Citations: {p['citations']}")
        print(f"    DOI: {p['doi']}")
        print(f"    Abstract Snippet: {p['abstract'][:250]}...")
        print("-" * 50)

if __name__ == '__main__':
    main()
