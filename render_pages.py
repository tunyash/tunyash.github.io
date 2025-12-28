#!/usr/bin/env python3
"""
Build script for generating the website HTML from templates and data.
Uses Jinja2 for templating.
"""

import json
import datetime
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


def read_svg_file(filename: str) -> str:
    """Read an SVG file and return its contents."""
    svg_path = Path(filename)
    if svg_path.exists():
        return svg_path.read_text()
    return ""


def load_papers(data_file: str) -> list:
    """Load papers from JSON file and sort by date (newest first)."""
    with open(data_file, 'r', encoding='utf-8') as f:
        papers = json.load(f)
    
    # Sort by date (newest first)
    sorted_papers = sorted(
        papers,
        key=lambda paper: -datetime.datetime.fromisoformat(paper['date']).timestamp()
    )
    
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
    output_file = base_dir / "index.html"
    
    # Load data
    papers = load_papers(data_file)
    
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
