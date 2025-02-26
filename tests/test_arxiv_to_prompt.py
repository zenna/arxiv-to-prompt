import pytest
import os
import tempfile
from unittest.mock import patch, MagicMock
from arxiv_to_prompt import (
    extract_arxiv_id, 
    download_arxiv_source, 
    find_main_tex_file, 
    expand_latex,
)

def test_extract_arxiv_id():
    # Test direct ID
    assert extract_arxiv_id("2402.02392") == "2402.02392"
    
    # Test URL
    assert extract_arxiv_id("https://arxiv.org/abs/2402.02392") == "2402.02392"
    
    # Test PDF URL
    assert extract_arxiv_id("https://arxiv.org/pdf/2402.02392.pdf") == "2402.02392"
    
    # Test with version
    assert extract_arxiv_id("2402.02392v1") == "2402.02392v1"
    
    # Test invalid input should raise ValueError
    with pytest.raises(ValueError):
        extract_arxiv_id("not-an-arxiv-id")

@patch('urllib.request.urlretrieve')
def test_download_arxiv_source(mock_urlretrieve):
    # Mock the urlretrieve call
    mock_urlretrieve.return_value = None
    
    # Mock tarfile operations
    with patch('tarfile.is_tarfile', return_value=True), \
         patch('tarfile.open'), \
         patch('os.makedirs'):
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test successful download
            result = download_arxiv_source("2402.02392", temp_dir)
            assert os.path.basename(result) == "source"
            mock_urlretrieve.assert_called_once()

@patch('os.path.exists')
@patch('pathlib.Path.glob')
def test_find_main_tex_file(mock_glob, mock_exists):
    # Test finding a common name
    mock_exists.return_value = True
    result = find_main_tex_file("/fake/path")
    assert result.endswith("main.tex")
    
    # Test when common names don't exist
    mock_exists.return_value = False
    
    # Mock finding a file with \documentclass and \begin{document}
    mock_file = MagicMock()
    mock_file.__str__.return_value = "/fake/path/paper.tex"
    mock_glob.return_value = [mock_file]
    
    with patch('builtins.open', return_value=MagicMock(
            __enter__=MagicMock(return_value=MagicMock(
                read=MagicMock(return_value="\\documentclass{article}\\begin{document}")
            ))
        )):
        result = find_main_tex_file("/fake/path")
        assert result == "/fake/path/paper.tex"
    
    # Test no valid files found
    mock_glob.return_value = []
    with pytest.raises(FileNotFoundError):
        find_main_tex_file("/fake/path")

@patch('subprocess.run')
def test_expand_latex(mock_run):
    # Mock subprocess.run to return a simulated output
    mock_run.return_value = MagicMock(
        stdout="Expanded LaTeX content",
        returncode=0
    )
    
    # Test with keep comments
    result = expand_latex("/path/to/main.tex", clean=False)
    assert result == "Expanded LaTeX content"
    
    # Verify latexpand was called with --keep-comments
    mock_run.assert_called_with(
        ["latexpand", "--verbose", "--keep-comments", "/path/to/main.tex"],
        capture_output=True,
        text=True,
        check=True,
        cwd=os.path.dirname("/path/to/main.tex"),
        timeout=60
    )
    
    # Test with clean (no comments)
    mock_run.reset_mock()
    result = expand_latex("/path/to/main.tex", clean=True)
    assert result == "Expanded LaTeX content"
    
    # Verify latexpand was called without --keep-comments
    mock_run.assert_called_with(
        ["latexpand", "--verbose", "/path/to/main.tex"],
        capture_output=True,
        text=True,
        check=True,
        cwd=os.path.dirname("/path/to/main.tex"),
        timeout=60
    )