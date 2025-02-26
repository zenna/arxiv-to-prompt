#!/usr/bin/env python3
"""
Command-line interface for arxiv-to-prompt.
"""

import sys
import argparse
import tempfile
import subprocess
from .main import (
    extract_arxiv_id,
    download_arxiv_source, 
    find_main_tex_file,
    expand_latex,
    clean_latex
)

def check_dependencies():
    """Check if required external dependencies are installed."""
    try:
        subprocess.run(["latexpand", "--help"], 
                      stdout=subprocess.PIPE, 
                      stderr=subprocess.PIPE, 
                      check=False)
    except FileNotFoundError:
        print("Error: 'latexpand' command not found. Please install it first.", file=sys.stderr)
        print("On Debian/Ubuntu: sudo apt-get install texlive-extra-utils", file=sys.stderr)
        print("On macOS with Homebrew: brew install texlive", file=sys.stderr)
        sys.exit(1)

def main():
    # Check dependencies first
    check_dependencies()
    
    parser = argparse.ArgumentParser(description="Extract and expand LaTeX source from arXiv papers")
    parser.add_argument("identifier", help="arXiv URL, ID, or PDF link")
    parser.add_argument("--clean", action="store_true", help="Clean LaTeX output (remove comments, etc.)")
    args = parser.parse_args()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract arXiv ID from the input
            arxiv_id = extract_arxiv_id(args.identifier)
            
            # Download the source
            source_dir = download_arxiv_source(arxiv_id, temp_dir)
            
            # Find the main .tex file
            main_file = find_main_tex_file(source_dir)
            
            # Expand the LaTeX source
            content = expand_latex(main_file, args.clean)
            
            # Optionally clean the content
            if args.clean:
                content = clean_latex(content)
            
            # Output the result
            print(content)
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main() 