"""
Extract and expand LaTeX source from arXiv papers for LLM prompts.
"""

from .main import download_arxiv_source, expand_latex, clean_latex, extract_arxiv_id

__version__ = "0.1.0"