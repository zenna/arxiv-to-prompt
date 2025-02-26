"""
Extract and expand LaTeX source from arXiv papers for LLM prompts.
"""

from .main import download_arxiv_source, expand_latex, extract_arxiv_id, find_main_tex_file

__version__ = "0.1.0"