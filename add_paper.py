#!/usr/bin/env python3
"""
Script to add a new paper to data.json.
Prompts for paper information and adds it to the database.
"""

import json
import re
from pathlib import Path
from datetime import datetime


def generate_paper_id(title: str, max_length: int = 15) -> str:
    """Generate a URL-safe ID from a paper title."""
    slug = title.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    slug = slug.strip('-')
    slug = slug[:max_length]
    slug = slug.rstrip('-')
    return slug


def add_paper_interactive():
    """Interactive function to add a paper to data.json."""
    data_file = Path("data.json")
    
    # Load existing papers
    with open(data_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    print("Add a new paper to the database")
    print("=" * 50)
    
    # Get title
    title = input("\nTitle: ").strip()
    if not title:
        print("Title is required!")
        return
    
    # Check if paper already exists
    existing_ids = {p.get('paper_id') for p in papers if 'paper_id' in p}
    paper_id = generate_paper_id(title)
    
    # Handle duplicate IDs
    counter = 1
    original_id = paper_id
    while paper_id in existing_ids:
        # Try to make it unique by appending a number
        paper_id = original_id[:max(0, 15 - len(str(counter)) - 1)] + str(counter)
        counter += 1
    
    print(f"\nGenerated paper_id: {paper_id}")
    
    # Get date
    date_str = input("\nDate (YYYY-MM-DD, or press Enter for today): ").strip()
    if not date_str:
        date_str = datetime.now().strftime("%Y-%m-%d")
    date_str += " 19:23:03+02:00"  # Add time if not present
    
    # Get draft status
    draft_input = input("\nIs this a draft? (y/n, default: y): ").strip().lower()
    draft = draft_input != 'n'
    
    # Get topics
    print("\nAvailable topics: all, proof-complexity, communication-complexity, circuit-complexity, combinatorics")
    topics_input = input("Topics (comma-separated): ").strip()
    topics = [t.strip() for t in topics_input.split(',') if t.strip()]
    
    # Get authors
    print("\nEnter authors (one per line, format: Name|URL, or just Name for no URL, empty line to finish):")
    authors = []
    while True:
        author_input = input("  Author: ").strip()
        if not author_input:
            break
        if '|' in author_input:
            name, url = author_input.split('|', 1)
            authors.append({"name": name.strip(), "url": url.strip()})
        else:
            authors.append({"name": author_input, "url": ""})
    
    # Get links
    print("\nEnter links (one per line, format: Name|URL, empty line to finish):")
    links = []
    while True:
        link_input = input("  Link: ").strip()
        if not link_input:
            break
        if '|' in link_input:
            name, url = link_input.split('|', 1)
            links.append({"name": name.strip(), "url": url.strip()})
        else:
            print("  Warning: Link format should be Name|URL, skipping...")
    
    # Create paper object
    paper = {
        "title": title,
        "date": date_str,
        "draft": draft,
        "topics": topics,
        "author": authors,
        "links": links,
        "paper_id": paper_id
    }
    
    # Confirm
    print("\n" + "=" * 50)
    print("Paper to be added:")
    print(json.dumps(paper, indent=2, ensure_ascii=False))
    print("=" * 50)
    
    confirm = input("\nAdd this paper? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        return
    
    # Add paper (insert at the beginning, so newest papers appear first)
    papers.insert(0, paper)
    
    # Write back to file
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"\nPaper added successfully!")
    print(f"Paper ID: {paper_id}")
    print(f"Remember to create an abstract file at: abstracts/{paper_id}.html (if needed)")


if __name__ == "__main__":
    add_paper_interactive()

