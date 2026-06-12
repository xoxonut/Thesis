import urllib.request
import urllib.parse
import json
import xml.etree.ElementTree as ET
import time
import os

def search_openalex(query, email="antigravity@google.com"):
    # Clean the query for URL encoding
    encoded_query = urllib.parse.quote_plus(query)
    url = f"https://api.openalex.org/works?search={encoded_query}&sort=cited_by_count:desc&per_page=20&mailto={email}"
    print(f"Querying OpenAlex: {url}")
    
    headers = {
        'User-Agent': 'AntigravityAgent/1.0 (mailto:antigravity@google.com)'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data.get('results', [])
    except Exception as e:
        print(f"Error querying OpenAlex: {e}")
        return []

def search_arxiv(query):
    # Formulate query
    encoded_query = urllib.parse.quote_plus(query)
    url = f"http://export.arxiv.org/api/query?search_query={encoded_query}&max_results=20&sortBy=relevance"
    print(f"Querying arXiv: {url}")
    
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            xml_data = response.read()
            root = ET.fromstring(xml_data)
            
            results = []
            namespace = {'atom': 'http://www.w3.org/2005/Atom'}
            for entry in root.findall('atom:entry', namespace):
                paper = {}
                # Title
                title_node = entry.find('atom:title', namespace)
                paper['title'] = title_node.text.replace('\n', ' ').strip() if title_node is not None else ""
                
                # Summary
                summary_node = entry.find('atom:summary', namespace)
                paper['summary'] = summary_node.text.replace('\n', ' ').strip() if summary_node is not None else ""
                
                # ID
                id_node = entry.find('atom:id', namespace)
                if id_node is not None:
                    paper['id'] = id_node.text.split('/abs/')[-1]
                    paper['url'] = id_node.text
                
                # Published
                published_node = entry.find('atom:published', namespace)
                paper['published_year'] = published_node.text[:4] if published_node is not None else ""
                
                # Authors
                authors = []
                for author in entry.findall('atom:author', namespace):
                    name_node = author.find('atom:name', namespace)
                    if name_node is not None:
                        authors.append(name_node.text)
                paper['authors'] = authors
                
                results.append(paper)
            return results
    except Exception as e:
        print(f"Error querying arXiv: {e}")
        return []

def format_openalex_paper(paper):
    authors = [auth.get('author', {}).get('display_name', 'Unknown') for auth in paper.get('authorships', [])]
    primary_loc = paper.get('primary_location') or {}
    source = primary_loc.get('source') or {}
    venue = source.get('display_name', 'Unknown Venue')
    doi = paper.get('doi', '')
    citations = paper.get('cited_by_count', 0)
    
    # Abstract in OpenAlex is stored as inverted index
    abstract_index = paper.get('abstract_inverted_index', None)
    abstract = ""
    if abstract_index:
        # Reconstruct abstract
        word_list = []
        for word, positions in abstract_index.items():
            for pos in positions:
                word_list.append((pos, word))
        word_list.sort()
        abstract = " ".join([word for pos, word in word_list])
        
    return {
        'title': paper.get('display_name', 'No Title'),
        'authors': authors,
        'year': paper.get('publication_year', 'Unknown'),
        'venue': venue,
        'citations': citations,
        'doi': doi,
        'abstract': abstract,
        'url': paper.get('id', '')
    }

def main():
    # 1. Search OpenAlex
    # Query focusing on RSSI active detection wifi hidden node
    query_oa = "wifi \"hidden node\" RSSI active"
    results_oa = search_openalex(query_oa)
    
    # Let's also do a broader query if results are few
    if len(results_oa) < 5:
        print("Broadening OpenAlex query...")
        results_oa_broad = search_openalex("wifi hidden node RSSI")
        # merge and deduplicate
        seen = {p['id'] for p in results_oa}
        for p in results_oa_broad:
            if p['id'] not in seen:
                results_oa.append(p)
                seen.add(p['id'])
                
    # 2. Search arXiv
    query_arxiv = 'all:"hidden node" AND all:wifi AND (all:RSSI OR all:active OR all:detection)'
    results_arxiv = search_arxiv(query_arxiv)
    
    formatted_papers = []
    
    # Process OpenAlex
    for paper in results_oa:
        formatted_papers.append(format_openalex_paper(paper))
        
    # Process arXiv
    for paper in results_arxiv:
        # check duplicate by title
        title_lower = paper['title'].lower()
        is_dup = False
        for fp in formatted_papers:
            if fp['title'].lower() == title_lower:
                is_dup = True
                break
        if not is_dup:
            formatted_papers.append({
                'title': paper['title'],
                'authors': paper['authors'],
                'year': paper['published_year'],
                'venue': 'arXiv Preprint',
                'citations': 0, # arXiv papers don't have citations easily queryable here
                'doi': '',
                'abstract': paper['summary'],
                'url': paper['url']
            })
            
    # Save the output
    output_data = {
        'query_oa': query_oa,
        'query_arxiv': query_arxiv,
        'papers': formatted_papers
    }
    
    with open('wifi_hidden_node_results.json', 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
        
    print(f"Saved {len(formatted_papers)} papers to wifi_hidden_node_results.json")

if __name__ == '__main__':
    main()
