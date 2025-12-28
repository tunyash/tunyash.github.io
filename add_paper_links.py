#!/usr/bin/env python3
"""
Script to convert plaintext paper references in abstracts to <a> tags.
Finds patterns like "Author Name (Conference Year)" and converts them to links.
"""

import re
from pathlib import Path


def find_paper_references(text):
    """
    Find plaintext paper references in the format:
    - Author Name (Conference Year)
    - Author, Author, and Author (Conference Year)
    
    Returns a list of (match, start, end) tuples.
    """
    # Pattern to match author names followed by conference/year in parentheses
    # This matches patterns like:
    # - "Author (STOC 2025)"
    # - "Author and Author (ICALP 2020)"
    # - "Author, Author, and Author (EUROCRYPT 2020)"
    # - "Author Name (Conference Name 2024)"
    # Handles Unicode characters in names (like Göös)
    
    # Author pattern: handles names with Unicode, multiple words, commas, and "and"
    # Use [A-Z] with Unicode flag or [A-Z\w] to match capital letters (including accented)
    # Pattern breakdown:
    # - [A-Z\w] matches capital letters (including accented like Ö in Göös)
    # - [a-z\w]+ matches lowercase letters and accented characters
    # - Handles: "Author", "Author and Author", "Author, Author, and Author"
    # Use \w for Unicode word characters (handles accented letters like ö in Göös)
    # First char must be uppercase (A-Z or Unicode uppercase), rest can be word chars
    # Simplified pattern: match word chars for names (handles Unicode)
    author_word = r'[A-Z]\w+'  # Single word author name (handles Unicode like Göös)
    author_pattern = rf'{author_word}(?:,\s+{author_word})*(?:\s+and\s+{author_word})?'
    
    # Conference pattern: matches conference names (may have spaces)
    conference_pattern = r'[A-Z][A-Za-z0-9\s]+'
    
    # Full pattern: authors, optional space, parenthesis, conference, space, year, closing parenthesis
    # Just match the pattern - we'll filter out bad matches later
    pattern = rf'({author_pattern})\s+\(({conference_pattern})\s+([0-9]{{4}})\)'
    
    matches = []
    # Common words that shouldn't start author citations
    skip_words = {'Moreover', 'Also', 'Furthermore', 'Additionally', 'Similarly', 
                  'Additionally', 'of', 'and', 'the', 'a', 'an'}
    
    for match in re.finditer(pattern, text):
        full_match = match.group(0)
        authors = match.group(1)
        conference = match.group(2).strip()
        year = match.group(3)
        
        # Skip if this is already inside an <a> tag
        start_pos = match.start()
        before_match = text[:start_pos]
        last_open_a = before_match.rfind('<a')
        last_close_a = before_match.rfind('</a>')
        
        if last_open_a > last_close_a:
            # We're inside an <a> tag, skip this match
            continue
        
        # Skip if authors start with common transition words
        if authors:
            first_word = authors.split()[0].rstrip(',')
            if first_word in skip_words:
                continue
        
        # Note: We're converting ALL paper references to links, even if they appear
        # after prepositions like "of Author (Conference Year)" - this is intentional
        # as the user wants all implicit paper citations to become active links
        
        matches.append((match.start(), match.end(), full_match, authors, conference, year))
    
    return matches


def convert_references_to_links(text):
    """
    Convert plaintext paper references to <a> tags without href.
    """
    matches = find_paper_references(text)
    
    # Filter out matches that are contained within other matches (prioritize longer matches)
    filtered_matches = []
    for i, match1 in enumerate(matches):
        start1, end1 = match1[0], match1[1]
        is_contained = False
        for j, match2 in enumerate(matches):
            if i == j:
                continue
            start2, end2 = match2[0], match2[1]
            # Check if match1 is contained within match2
            if start2 <= start1 and end1 <= end2:
                is_contained = True
                break
        if not is_contained:
            filtered_matches.append(match1)
    
    # Sort by start position (reverse for processing from end to beginning)
    filtered_matches.sort(key=lambda x: x[0], reverse=True)
    
    # Process matches in reverse order to maintain correct indices
    for start, end, full_match, authors, conference, year in filtered_matches:
        # Create the link tag without href
        link_tag = f'<a>{full_match}</a>'
        text = text[:start] + link_tag + text[end:]
    
    return text


def process_abstract_file(file_path):
    """Process a single abstract file."""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    content = convert_references_to_links(content)
    
    if content != original_content:
        file_path.write_text(content, encoding='utf-8')
        return True
    return False


def main():
    """Process all abstract files."""
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
        if process_abstract_file(file_path):
            print(f"Modified: {file_path.name}")
            modified_count += 1
    
    print(f"\nProcessed {len(abstract_files)} files, modified {modified_count} files")


if __name__ == "__main__":
    main()

