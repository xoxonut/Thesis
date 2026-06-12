import urllib.request
import urllib.parse
import json
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding='utf-8')

def search_openalex_title(title, mailto="antigravity@google.com"):
    encoded_title = urllib.parse.quote_plus(title)
    url = f"https://api.openalex.org/works?filter=title.search:{encoded_title}&mailto={mailto}"
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
    results = search_openalex_title('"Passive and Active Hidden Terminal Detection"')
    for i, p in enumerate(results):
        authors = [auth.get('author', {}).get('display_name', 'Unknown') for auth in p.get('authorships', [])]
        primary_loc = p.get('primary_location') or {}
        source = primary_loc.get('source') or {}
        venue = source.get('display_name', 'Unknown Venue')
        
        print(f"[{i+1}] {p.get('display_name')} ({p.get('publication_year')})")
        print(f"    Authors: {', '.join(authors)}")
        print(f"    Venue: {venue} | Citations: {p.get('cited_by_count')}")
        print(f"    DOI: {p.get('doi')}")
        print(f"    URL: {p.get('id')}")
        print("-" * 50)

if __name__ == '__main__':
    main()
