import pytest
from arxiv_to_prompt import extract_arxiv_id

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