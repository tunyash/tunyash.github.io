#!/usr/bin/env python3
"""
Script to replace $...$ and $$...$$ math delimiters with \(...\) and \[...\] 
in abstract HTML files.
"""

import re
from pathlib import Path


def replace_math_delimiters(content):
    """Replace $ delimiters with \( \) for inline and \[ \] for display math."""
    
    # First, handle display math ($$...$$) - must be done before inline to avoid conflicts
    # Display math: $$...$$
    def replace_display_math(match):
        math_content = match.group(1)
        return f'\\[{math_content}\\]'
    
    # Pattern for display math: $$...$$ (non-greedy, but we want to match across newlines)
    # Use DOTALL flag to match across newlines
    # In regex, \$ matches a literal $ sign
    content = re.sub(r'\$\$(.*?)\$\$', replace_display_math, content, flags=re.DOTALL)
    
    # Then handle inline math ($...$)
    # Inline math: $...$
    # Replace $...$ with \(...\)
    # In regex, \$ matches a literal $ sign
    # Use non-greedy matching and ensure we don't match $$ (already handled above)
    content = re.sub(r'(?<!\$)\$(?!\$)(.*?)(?<!\$)\$(?!\$)', r'\\(\1\\)', content)
    
    return content


def fix_abstract_file(file_path):
    """Fix math delimiters in a single abstract file."""
    content = file_path.read_text(encoding='utf-8')
    original_content = content
    
    content = replace_math_delimiters(content)
    
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
        if fix_abstract_file(file_path):
            print(f"Modified: {file_path.name}")
            modified_count += 1
    
    print(f"\nProcessed {len(abstract_files)} files, modified {modified_count} files")


if __name__ == "__main__":
    main()

