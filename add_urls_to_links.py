#!/usr/bin/env python3
"""
Script to add href URLs to <a> tags without href in abstracts.
Uses DBLP API to look up paper citations and find URLs.
"""

import json
import re
import time
import ssl
from pathlib import Path
from html import unescape
from urllib.parse import quote, urljoin
import urllib.request
import urllib.error


def extract_authors_from_citation(citation_text):
    """Extract author names from citation text like 'Author1, Author2, and Author3 (Venue Year)'."""
    # Remove the venue/year part: everything after the last opening parenthesis
    match = re.match(r'^(.+?)\s*\([^)]+\)$', citation_text.strip())
    if not match:
        return []
    
    authors_part = match.group(1).strip()
    
    # Split by comma and "and"
    authors = []
    parts = re.split(r',\s*and\s+|\s+and\s+', authors_part)
    
    for part in parts:
        # Handle comma-separated authors
        comma_parts = part.split(',')
        for author in comma_parts:
            author = author.strip()
            if author:
                authors.append(author)
    
    return authors


def extract_venue_year_from_citation(citation_text):
    """Extract venue and year from citation text like 'Author (Venue Year)' or 'Author (Year)'."""
    # Try pattern with venue and year
    match = re.match(r'.*\((.+?)\s+([0-9]{4})\)$', citation_text.strip())
    if match:
        venue_part = match.group(1).strip()
        year = match.group(2).strip()
        # Check if venue_part is just a 4-digit year (no venue)
        if re.match(r'^[0-9]{4}$', venue_part):
            return None, venue_part
        return venue_part, year
    
    # Try pattern with just year: "Author (1985)"
    match = re.match(r'.*\(([0-9]{4})\)$', citation_text.strip())
    if match:
        year = match.group(1).strip()
        return None, year
    
    return None, None


def normalize_author_for_dblp(author_name):
    """Normalize author name for DBLP search."""
    # DBLP typically uses "First Last" format
    # Handle cases like "Mika Göös" -> "Mika Göös"
    # Handle initials and common patterns
    name = author_name.strip()
    # Remove extra spaces
    name = ' '.join(name.split())
    return name


def search_dblp(authors, venue=None, year=None):
    """
    Search DBLP API for papers matching authors, venue, and year.
    Returns list of matching publications with URLs.
    """
    # DBLP API endpoint: https://dblp.org/search/publ/api
    # Format: https://dblp.org/search/publ/api?q=query&format=json
    
    # Build query: use first two authors for better matching
    if not authors:
        return []
    
    query_parts = []
    # Use first two authors (if available) for better matching
    for author in authors[:2]:
        query_parts.append(normalize_author_for_dblp(author))
    
    if venue:
        query_parts.append(venue)
    if year:
        query_parts.append(year)
    
    query = ' '.join(query_parts)
    
    # Construct DBLP API URL
    base_url = "https://dblp.org/search/publ/api"
    
    # Request more results for better matching
    url = f"{base_url}?q={quote(query)}&format=json&h=20"
    
    try:
        # Create SSL context - use unverified to avoid certificate issues
        ctx = ssl._create_unverified_context()
        
        # Request with proper headers
        req = urllib.request.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (compatible; Academic Citation Linker)')
        
        with urllib.request.urlopen(req, timeout=10, context=ctx) as response:
            data = json.loads(response.read().decode('utf-8'))
            
            results = []
            if 'result' in data and 'hits' in data['result']:
                hits = data['result']['hits'].get('hit', [])
                
                for hit in hits:
                    info = hit.get('info', {})
                    
                    # Extract paper details
                    title = info.get('title', '')
                    
                    # Extract authors - can be dict, list, or missing
                    paper_authors = []
                    authors_data = info.get('authors', {})
                    if authors_data:
                        author_list = authors_data.get('author', [])
                        if isinstance(author_list, dict):
                            # Single author
                            paper_authors = [author_list.get('text', '')]
                        elif isinstance(author_list, list):
                            # Multiple authors
                            paper_authors = [a.get('text', '') if isinstance(a, dict) else str(a) for a in author_list]
                    
                    # Get URL - prefer 'ee' (electronic edition), then 'url', then construct from key
                    url_key = info.get('ee', '') or info.get('url', '')
                    if not url_key:
                        # Construct URL from key
                        key = hit.get('@key', '') or info.get('key', '')
                        if key:
                            url_key = f"https://dblp.org/rec/{key}.html"
                    
                    # Extract venue and year
                    venue_info = info.get('venue', '')
                    year_info = str(info.get('year', ''))
                    
                    results.append({
                        'title': title,
                        'authors': paper_authors,
                        'venue': venue_info,
                        'year': year_info,
                        'url': url_key,
                        'key': hit.get('@key', '') or info.get('key', '')
                    })
            
            return results
            
    except urllib.error.URLError as e:
        print(f"  DBLP API error: {e}")
        return []
    except json.JSONDecodeError as e:
        print(f"  JSON decode error: {e}")
        return []
    except Exception as e:
        print(f"  Error searching DBLP: {e}")
        return []


def normalize_name_for_match(name):
    """Normalize names for fuzzy matching - extract last name if full name."""
    name = name.lower().strip()
    # If it's a full name (has spaces), extract the last part (last name)
    parts = name.split()
    if len(parts) > 1:
        # Full name - use last name
        return parts[-1]
    else:
        # Already just last name or single name
        return name


def match_citation_to_dblp_result(citation_text, dblp_results, citation_authors, citation_venue, citation_year):
    """Match a citation to the best DBLP result."""
    if not dblp_results:
        return None
    
    best_match = None
    best_score = 0
    
    for result in dblp_results:
        score = 0
        
        # Match authors (check if citation authors appear in result)
        result_authors_normalized = {normalize_name_for_match(a) for a in result['authors']}
        citation_authors_normalized = {normalize_name_for_match(a) for a in citation_authors}
        
        # Calculate author overlap - require at least 50% of citation authors to match
        author_overlap = len(result_authors_normalized & citation_authors_normalized)
        if author_overlap == 0:
            continue  # Skip if no author overlap
        
        # Score based on author overlap (higher score for more matches)
        author_match_ratio = author_overlap / len(citation_authors_normalized)
        score += author_match_ratio * 4.0
        
        # Match year (strict requirement when specified)
        if citation_year:
            if result['year'] == citation_year:
                score += 4.0
            elif result['year']:
                # Year mismatch - very significant penalty
                try:
                    year_diff = abs(int(result['year']) - int(citation_year))
                    # Large year difference should eliminate the match
                    if year_diff > 2:
                        continue  # Skip matches with >2 year difference
                    score -= year_diff * 3.0
                except (ValueError, TypeError):
                    pass  # Ignore if year parsing fails
        
        # Match venue (fuzzy but important)
        if citation_venue and result['venue']:
            venue_lower = citation_venue.lower()
            result_venue_lower = result['venue'].lower()
            # Check if venue names overlap significantly
            if venue_lower in result_venue_lower or result_venue_lower in venue_lower:
                score += 3.0
            # Also check common venue abbreviations
            venue_abbrev = {
                'stoc': ['stoc', 'symposium'],
                'focs': ['focs', 'foundations'],
                'icalp': ['icalp', 'automata'],
                'eurocrypt': ['eurocrypt', 'european'],
                'sicomp': ['sicomp', 'journal'],
                'itcs': ['itcs', 'innovations']
            }
            for abbrev, keywords in venue_abbrev.items():
                if abbrev in venue_lower and any(k in result_venue_lower for k in keywords):
                    score += 3.0
        
        if score > best_score:
            best_score = score
            best_match = result
    
    # Return match if score indicates good match (at least 3.0 - requires some author overlap)
    # But prefer matches with year and venue alignment
    return best_match if best_score >= 3.0 else None


def get_best_url(dblp_result):
    """Get the best URL from a DBLP result."""
    # DBLP results usually have 'ee' field (electronic edition) or we construct from key
    url = dblp_result.get('url', '')
    
    if not url and dblp_result.get('key'):
        key = dblp_result['key']
        url = f"https://dblp.org/rec/{key}.html"
    
    return url


def add_urls_to_abstract_file(file_path):
    """Process a single abstract file and add URLs to <a> tags without href."""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    # Find all <a> tags without href using regex
    pattern = r'<a>(.*?)</a>'
    
    def replace_link(match):
        citation_text = unescape(match.group(1))
        
        # Extract citation components
        citation_authors = extract_authors_from_citation(citation_text)
        citation_venue, citation_year = extract_venue_year_from_citation(citation_text)
        
        if not citation_authors:
            return match.group(0)
        
        # Search DBLP
        print(f"  Searching DBLP for: {citation_text[:60]}...")
        dblp_results = search_dblp(citation_authors, citation_venue, citation_year)
        
        if dblp_results:
            # Find best match
            best_match = match_citation_to_dblp_result(
                citation_text, dblp_results, citation_authors, citation_venue, citation_year
            )
            
            if best_match:
                url = get_best_url(best_match)
                if url:
                    print(f"    Found: {best_match['title'][:50]}... -> {url}")
                    return f'<a href="{url}">{citation_text}</a>'
        
        print(f"    No match found")
        # Rate limiting - be nice to DBLP API
        time.sleep(0.5)
        
        # If no match found, keep the tag without href
        return match.group(0)
    
    content = re.sub(pattern, replace_link, content)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    """Main function to process all abstract files."""
    base_dir = Path(__file__).parent
    abstracts_dir = base_dir / "abstracts"
    
    if not abstracts_dir.exists():
        print(f"Error: {abstracts_dir} directory not found")
        return
    
    abstract_files = list(abstracts_dir.glob("*.html"))
    
    if not abstract_files:
        print(f"No HTML files found in {abstracts_dir}")
        return
    
    modified_count = 0
    for file_path in sorted(abstract_files):
        print(f"\nProcessing {file_path.name}...")
        if add_urls_to_abstract_file(file_path):
            print(f"  ✓ Modified")
            modified_count += 1
        else:
            print(f"  No changes")
    
    print(f"\n{'='*60}")
    print(f"Processed {len(abstract_files)} files, modified {modified_count} files")


if __name__ == "__main__":
    main()
