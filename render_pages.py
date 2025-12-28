#!/usr/bin/env python3
"""
Build script for generating the website HTML from templates and data.
Uses Jinja2 for templating.
"""

import json
import datetime
import re
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


def generate_paper_id(title: str, max_length: int = 15) -> str:
    """
    Generate a URL-safe ID from a paper title.
    Limits to max_length characters.
    
    Examples:
        "Lower Bounds Beyond DNF of Parities" -> "lower-bounds-bey"
        "Better Boosting of Communication Oracles" -> "better-boostin"
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


# Papers are now loaded dynamically via JavaScript, so we don't need to load them here


def get_all_topics() -> list:
    """Return list of all available topics, with 'all' first."""
    return ["all", "proof-complexity", "communication-complexity", "circuit-complexity", "combinatorics"]


def main():
    """Generate the main index.html file from templates."""
    # Setup paths
    base_dir = Path(__file__).parent
    templates_dir = base_dir / "templates"
    output_file = base_dir / "index.html"
    
    # Papers are loaded dynamically via JavaScript, no need to load them here
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Get topics list
    topics = get_all_topics()
    
    # Get template
    template = env.get_template('index.html')
    
    # Render template (papers are loaded dynamically, so we don't need to pass them)
    rendered_html = template.render(
        papers=[],  # Papers loaded dynamically via JavaScript
        topics=topics,
        update_date=datetime.date.today().isoformat()
    )
    
    # Write output
    output_file.write_text(rendered_html, encoding='utf-8')
    print(f"Successfully generated {output_file}")


if __name__ == "__main__":
    main()
