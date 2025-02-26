# arxiv-to-prompt

Extract and expand LaTeX source from arXiv papers for LLM prompts.

## Installation

```bash
pip install arxiv-to-prompt
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

# You can also use arXiv URLs
arxiv-to-prompt https://arxiv.org/abs/2411.02272 --clean | pbcopy
```

### Python API

```python
from arxiv_to_prompt import extract_arxiv_id, download_arxiv_source, find_main_tex_file, expand_latex, clean_latex
import tempfile

# Create a temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    # Get arXiv ID
    arxiv_id = extract_arxiv_id("https://arxiv.org/abs/2402.02392")
    
    # Download source files
    source_dir = download_arxiv_source(arxiv_id, temp_dir)
    
    # Find main TeX file
    main_file = find_main_tex_file(source_dir)
    
    # Expand LaTeX source
    expanded_content = expand_latex(main_file, clean=False)
    
    # Optionally clean the content
    cleaned_content = clean_latex(expanded_content)
    
    # Use the content...
    print(cleaned_content)
```

## License

MIT
