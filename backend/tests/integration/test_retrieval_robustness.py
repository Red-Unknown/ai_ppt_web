import pytest
import sys
import os
from pathlib import Path

# Add project root to path
# sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

from backend.app.services.qa.retrieval.tree_retriever import TreeStructureRetriever

@pytest.fixture
def retriever():
    return TreeStructureRetriever()

def test_exact_match(retriever):
    """Test exact title match."""
    results = retriever.invoke("匀速直线运动")
    assert len(results) > 0
    assert results[0].metadata["title"] == "匀速直线运动"

def test_typo_tolerance(retriever):
    """Test typo tolerance (Levenshtein distance simulation)."""
    # 匀速直线运动 -> 匀速直先运动 (1 char typo)
    results = retriever.invoke("匀速直先运动")
    assert len(results) > 0
    # Should still be top 1 or at least top 3
    titles = [doc.metadata["title"] for doc in results[:3]]
    assert "匀速直线运动" in titles

def test_synonym_expansion(retriever):
    """Test synonym expansion."""
    # "恒速运动" is a synonym for "匀速直线运动"
    results = retriever.invoke("恒速运动")
    assert len(results) > 0
    assert results[0].metadata["title"] == "匀速直线运动"

def test_mixed_concept(retriever):
    """Test query with multiple concepts."""
    query = "牛顿第一定律与动能定理的区别"
    results = retriever.invoke(query)
    titles = [doc.metadata["title"] for doc in results]
    
    # Should find both
    assert "牛顿第一定律" in titles
    assert "动能定理" in titles

def test_content_fragment(retriever):
    """Test retrieval by content fragment."""
    # "位移与时间成正比" is from 匀速直线运动
    results = retriever.invoke("位移与时间成正比")
    assert len(results) > 0
    assert results[0].metadata["title"] == "匀速直线运动"

def test_noise_robustness(retriever):
    """Test with noise/irrelevant words."""
    query = "请问一下关于匀速直线运动的详细介绍"
    results = retriever.invoke(query)
    assert len(results) > 0
    assert results[0].metadata["title"] == "匀速直线运动"
