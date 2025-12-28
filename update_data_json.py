#!/usr/bin/env python3
"""
Script to update data.json: remove abstract fields and add paper_id fields.
"""

import json
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


def update_data_json(data_file: str, backup: bool = True):
    """Remove abstract fields and add paper_id fields to data.json."""
    data_path = Path(data_file)
    
    # Load papers
    with open(data_path, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # Create backup if requested
    if backup:
        backup_path = data_path.with_suffix('.json.backup')
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(papers, f, indent=2, ensure_ascii=False)
        print(f"Created backup: {backup_path}")
    
    # Update each paper
    updated_count = 0
    abstracts_removed = 0
    for paper in papers:
        # Generate and add paper_id if not present
        if 'paper_id' not in paper:
            paper['paper_id'] = generate_paper_id(paper['title'])
            updated_count += 1
        
        # Remove abstract field if present
        if 'abstract' in paper:
            del paper['abstract']
            abstracts_removed += 1
    
    # Write updated papers
    with open(data_path, 'w', encoding='utf-8') as f:
        json.dump(papers, f, indent=2, ensure_ascii=False)
    
    print(f"\nUpdated {updated_count} papers with paper_id fields")
    print(f"Removed {abstracts_removed} abstract fields")
    print(f"Successfully updated {data_path}")


if __name__ == "__main__":
    update_data_json("data.json", backup=True)

