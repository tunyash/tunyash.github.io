#!/usr/bin/env python3
"""
Migration script to extract abstracts from data.json to separate files.
Run this once to migrate existing abstracts.
Abstracts are extracted in the same order as papers will be sorted (by date, newest first).
Uses title-based IDs (max 15 characters).
"""

import json
import datetime
import re
from pathlib import Path


def generate_paper_id(title: str, max_length: int = 15) -> str:
    """
    Generate a URL-safe ID from a paper title.
    Limits to max_length characters.
    """
    # Convert to lowercase
    slug = title.lower()
    
    # Replace spaces and common punctuation with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)  # Remove special chars except hyphens
    slug = re.sub(r'[-\s]+', '-', slug)   # Replace spaces/hyphens with single hyphen
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Limit to max_length characters
    slug = slug[:max_length]
    
    # Remove trailing hyphen if we truncated at a hyphen
    slug = slug.rstrip('-')
    
    return slug


def extract_abstracts(data_file: str, abstracts_dir: str):
    """Extract abstracts from data.json to separate files (sorted by date, newest first)."""
    base_dir = Path(__file__).parent
    data_path = base_dir / data_file
    abstracts_path = base_dir / abstracts_dir
    
    # Create abstracts directory if it doesn't exist
    abstracts_path.mkdir(exist_ok=True)
    
    # Load papers
    with open(data_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # Sort by date (newest first) - same as in render_pages.py
    sorted_papers = sorted(
        papers,
        key=lambda paper: -datetime.datetime.fromisoformat(paper['date']).timestamp()
    )
    
    extracted_count = 0
    for paper in sorted_papers:
        if 'abstract' in paper and paper['abstract']:
            paper_id = generate_paper_id(paper['title'])
            abstract_file = abstracts_path / f"{paper_id}.html"
            abstract_file.write_text(paper['abstract'], encoding='utf-8')
            extracted_count += 1
            print(f"Extracted abstract for {paper_id}: {paper['title'][:50]}...")
    
    print(f"\nExtracted {extracted_count} abstracts to {abstracts_path}/")
    print("Abstracts use title-based IDs (max 15 characters).")
    print("You can now remove 'abstract' fields from data.json if desired.")


if __name__ == "__main__":
    extract_abstracts("data.json", "abstracts")

