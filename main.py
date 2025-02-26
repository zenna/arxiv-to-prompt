import os
import sys
import re
import argparse
import tempfile
import subprocess
import shutil
import tarfile
import urllib.request
from pathlib import Path


def extract_arxiv_id(url_or_id):
    """Extract the arXiv ID from a URL or ID string."""
    # Handle different formats of arXiv IDs and URLs
    if re.match(r'^\d+\.\d+(?:v\d+)?$', url_or_id):
        return url_or_id
    
    match = re.search(r'arxiv\.org/(?:abs|pdf)/(\d+\.\d+(?:v\d+)?)', url_or_id)
    if match:
        return match.group(1)
    
    # Add validation to check if the string resembles an arXiv ID format
    if not re.match(r'^\d+\.\d+(?:v\d+)?$', url_or_id):
        raise ValueError(f"Could not extract a valid arXiv ID from: {url_or_id}")
    
    return url_or_id


def download_arxiv_source(arxiv_id, temp_dir):
    """Download the source files for an arXiv paper."""
    # Clean up any 'v1', 'v2' etc. from the ID for downloading source
    base_id = re.sub(r'v\d+$', '', arxiv_id)
    source_url = f"https://arxiv.org/e-print/{base_id}"
    
    print(f"Downloading source for arXiv:{arxiv_id}...", file=sys.stderr)
    
    # Download the source tarball
    tar_path = os.path.join(temp_dir, f"{base_id}.tar.gz")
    try:
        urllib.request.urlretrieve(source_url, tar_path)
    except urllib.error.URLError as e:
        raise Exception(f"Failed to download arXiv source: {e}")
    
    # Verify the downloaded file is a valid tarball
    if not tarfile.is_tarfile(tar_path):
        raise Exception(f"Downloaded file is not a valid tar archive")
    
    # Extract the tarball
    extract_dir = os.path.join(temp_dir, "source")
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
    except tarfile.ReadError as e:
        raise Exception(f"Failed to extract tar archive: {e}")
    
    return extract_dir


def find_main_tex_file(source_dir):
    """Find the main .tex file in the arXiv source."""
    # Common main file names
    common_names = ["main.tex", "paper.tex", "article.tex", "ms.tex"]
    
    # First check for common names
    for name in common_names:
        path = os.path.join(source_dir, name)
        if os.path.exists(path):
            return path
    
    # Then look for .tex files that have \documentclass and \begin{document}
    for file in Path(source_dir).glob("**/*.tex"):
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if "\\documentclass" in content and "\\begin{document}" in content:
                return str(file)
    
    # If we still haven't found it, just return the first .tex file
    tex_files = list(Path(source_dir).glob("**/*.tex"))
    if tex_files:
        return str(tex_files[0])
    
    raise FileNotFoundError("Could not find a main .tex file in the arXiv source")


def expand_latex(main_file, clean=False):
    """Use latexpand to recursively include all files."""
    try:
        # Get the directory of the main file to use as the working directory
        main_dir = os.path.dirname(os.path.abspath(main_file))
        
        # Build the command with the appropriate options
        cmd = ["latexpand", "--verbose"]  # Add verbose flag for debugging
        
        # Add option to keep comments if not cleaning
        if not clean:
            cmd.append("--keep-comments")
            
        # Add the main file path
        cmd.append(main_file)
        
        print(f"Running: {' '.join(cmd)} in directory {main_dir}", file=sys.stderr)
        
        # Run latexpand in the directory of the main file to ensure relative paths work
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True,
            cwd=main_dir  # Set working directory to the main file's directory
        )
        
        # Print some diagnostics
        if "\\input{" in result.stdout or "\\include{" in result.stdout:
            print("Warning: Output still contains \\input or \\include commands", file=sys.stderr)
            
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running latexpand: {e}", file=sys.stderr)
        print(f"Error output: {e.stderr}", file=sys.stderr)
        sys.exit(1)  # Exit immediately on latexpand error
    except FileNotFoundError:
        print("Error: 'latexpand' command not found. Please install it first.", file=sys.stderr)
        print("On Debian/Ubuntu: sudo apt-get install texlive-extra-utils", file=sys.stderr)
        print("On macOS with Homebrew: brew install texlive", file=sys.stderr)
        sys.exit(1)


def clean_latex(content):
    """Remove comments and unnecessary content from LaTeX."""
    # Remove comments (lines starting with %)
    content = re.sub(r'(?m)^%.*$', '', content)
    content = re.sub(r'(?<!\\)%.*$', '', content)
    
    # Remove consecutive empty lines
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
    
    return content


def main():
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