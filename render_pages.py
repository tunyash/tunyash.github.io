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


def read_svg_file(filename: str) -> str:
    """Read an SVG file and return its contents."""
    svg_path = Path(filename)
    if svg_path.exists():
        return svg_path.read_text()
    return ""


def load_abstract(abstracts_dir: Path, paper_id: str) -> str:
    """Load abstract from file for a given paper ID."""
    abstract_file = abstracts_dir / f"{paper_id}.html"
    if abstract_file.exists():
        return abstract_file.read_text(encoding='utf-8')
    return ""


def load_papers(data_file: str, abstracts_dir: Path) -> list:
    """Load papers from JSON file, sort by date (newest first), and load abstracts from files."""
    with open(data_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # Sort by date (newest first)
    sorted_papers = sorted(
        papers,
        key=lambda paper: -datetime.datetime.fromisoformat(paper['date']).timestamp()
    )
    
    # Load abstracts from files using paper_id from JSON
    for paper in sorted_papers:
        # Use paper_id from JSON if present, otherwise generate it (backward compatibility)
        if 'paper_id' not in paper:
            paper['paper_id'] = generate_paper_id(paper['title'])
        
        paper_id = paper['paper_id']
        abstract_content = load_abstract(abstracts_dir, paper_id)
        if abstract_content:
            paper['abstract'] = abstract_content
        else:
            paper['abstract'] = ""
    
    return sorted_papers


def get_all_topics() -> list:
    """Return list of all available topics, with 'all' first."""
    return ["all", "proof-complexity", "communication-complexity", "circuit-complexity", "combinatorics"]


def main():
    """Generate the main index.html file from templates."""
    # Setup paths
    base_dir = Path(__file__).parent
    templates_dir = base_dir / "templates"
    data_file = base_dir / "data.json"
    abstracts_dir = base_dir / "abstracts"
    output_file = base_dir / "index.html"
    
    # Load data (including abstracts from files)
    papers = load_papers(data_file, abstracts_dir)
    
    # Setup Jinja2 environment
    env = Environment(
        loader=FileSystemLoader(str(templates_dir)),
        autoescape=select_autoescape(['html', 'xml'])
    )
    
    # Load SVG files for topics
    topics = get_all_topics()
    svg_contents = {}
    for topic in topics:
        svg_contents[topic] = read_svg_file(base_dir / f"{topic}.svg")
    
    # Get template
    template = env.get_template('index.html')
    
    # Render template
    rendered_html = template.render(
        papers=papers,
        topics=topics,
        svg_contents=svg_contents,
        update_date=datetime.date.today().isoformat()
    )
    
    # Write output
    output_file.write_text(rendered_html, encoding='utf-8')
    print(f"Successfully generated {output_file}")


if __name__ == "__main__":
    main()
