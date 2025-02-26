# arxiv-to-prompt

Extract and expand LaTeX source from arXiv papers into a string.  This is useful for passing a paper directly into an LLM as a prompt.

## Installation

Clone and cd into the repository

```bash
pip install -e .
```

### Requirements

This package requires the `latexpand` command, which is typically available in the `texlive-extra-utils` package.

- On Debian/Ubuntu:
  ```
  sudo apt-get install texlive-extra-utils
  ```

- On macOS with Homebrew:
  ```
  brew install texlive
  ```

## Usage

### Command Line

```bash
# Get expanded LaTeX source with comments
arxiv-to-prompt 2402.02392

# Get cleaned LaTeX source (no comments)
arxiv-to-prompt 2402.02392 --clean

# You can also use arXiv URLs
arxiv-to-prompt https://arxiv.org/abs/2411.02272 --clean

# Output to a file instead of stdout
arxiv-to-prompt 2402.02392 --output paper.tex

# Suppress status messages
arxiv-to-prompt 2402.02392 --quiet

# Pipe into the clipboard for easy copy-pasting
arxiv-to-prompt https://arxiv.org/abs/2411.02272 --clean | pbcopy
```

### Python API

```python
from arxiv_to_prompt import extract_arxiv_id, download_arxiv_source, find_main_tex_file, expand_latex
import tempfile

# Create a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    # Get arXiv ID
    arxiv_id = extract_arxiv_id("https://arxiv.org/abs/2402.02392")
    
    # Download source files
    source_dir = download_arxiv_source(arxiv_id, temp_dir)
    
    # Find main TeX file
    main_file = find_main_tex_file(source_dir)
    
    # Expand LaTeX source with comments
    expanded_content = expand_latex(main_file, clean=False)
    
    # Or get clean LaTeX without comments
    clean_content = expand_latex(main_file, clean=True)
    
    # Use the content...
    print(clean_content)
```

## Troubleshooting

### Common Issues

1. **"latexpand command not found"**
   - Make sure you have installed texlive-extra-utils (see Requirements section)
   - On some systems, you may need to install the full TexLive distribution

2. **"Failed to download arXiv source"**
   - Check your internet connection
   - Verify that the arXiv ID is valid
   - arXiv might be rate-limiting your requests; try again later

3. **Expanded LaTeX still contains \input commands**
   - Some complex documents might not expand fully
   - Check if the document uses non-standard include methods
   - Try adding the LaTeX file manually to your prompt

## Development

To set up for development:

```bash
git clone https://github.com/zenna/arxiv-to-prompt.git
cd arxiv-to-prompt
pip install -e ".[dev]"
```

Run tests:

```bash
pytest
```

## License

MIT
