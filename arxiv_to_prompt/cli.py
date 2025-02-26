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
    expand_latex
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
    parser.add_argument("--output", "-o", help="Output file (default: stdout)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress status messages")
    args = parser.parse_args()
    
    # Create temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            # Extract arXiv ID from the input
            arxiv_id = extract_arxiv_id(args.identifier)
            
            if not args.quiet:
                print(f"Processing arXiv:{arxiv_id}...", file=sys.stderr)
                
            # Download the source
            source_dir = download_arxiv_source(arxiv_id, temp_dir)
            
            # Find the main .tex file
            main_file = find_main_tex_file(source_dir)
            
            if not args.quiet:
                print(f"Found main file: {main_file}", file=sys.stderr)
                
            # Expand the LaTeX source
            content = expand_latex(main_file, args.clean)
            
            # Output the result
            if args.output:
                with open(args.output, 'w', encoding='utf-8') as f:
                    f.write(content)
                if not args.quiet:
                    print(f"Output written to {args.output}", file=sys.stderr)
            else:
                print(content)
            
        except Exception as e:
            print(f"Error: {str(e)}", file=sys.stderr)
            sys.exit(1)

if __name__ == "__main__":
    main() 