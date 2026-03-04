import json
import os
import sys
import time
from collections import defaultdict
from typing import List, Dict

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from backend.app.services.qa.retrieval.tree_retriever import TreeStructureRetriever

DATASET_PATH = os.path.join(os.path.dirname(__file__), "retrieval_dataset_golden.json")

def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def evaluate():
    dataset = load_dataset()
    retriever = TreeStructureRetriever()
    
    metrics = {
        "total": 0,
        "hits_at_1": 0,
        "hits_at_3": 0,
        "hits_at_5": 0,
        "mrr": 0.0,
        "by_type": defaultdict(lambda: {"total": 0, "hits": 0, "mrr": 0.0})
    }
    
    print(f"Evaluating {len(dataset)} queries...")
    
    for case in dataset:
        query = case["query"]
        expected_ids = set(case["expected_ids"])
        case_type = case["type"]
        
        metrics["total"] += 1
        metrics["by_type"][case_type]["total"] += 1
        
        try:
            # Use invoke instead of get_relevant_documents for newer LangChain versions
            results = retriever.invoke(query)
            result_ids = [doc.metadata["node_id"] for doc in results]
            
            # Hit Rate
            hit_rank = -1
            for i, rid in enumerate(result_ids):
                if rid in expected_ids:
                    hit_rank = i + 1
                    break
            
            if hit_rank > 0:
                if hit_rank == 1: metrics["hits_at_1"] += 1
                if hit_rank <= 3: metrics["hits_at_3"] += 1
                if hit_rank <= 5: metrics["hits_at_5"] += 1
                
                metrics["mrr"] += 1.0 / hit_rank
                
                metrics["by_type"][case_type]["hits"] += 1
                metrics["by_type"][case_type]["mrr"] += 1.0 / hit_rank
            
        except Exception as e:
            print(f"Error processing query '{query}': {e}")
            
    # Finalize
    print("\n=== Retrieval Evaluation Report ===")
    print(f"Total Queries: {metrics['total']}")
    print(f"Hit Rate@1: {metrics['hits_at_1'] / metrics['total']:.2%}")
    print(f"Hit Rate@3: {metrics['hits_at_3'] / metrics['total']:.2%}")
    print(f"Hit Rate@5: {metrics['hits_at_5'] / metrics['total']:.2%}")
    print(f"MRR: {metrics['mrr'] / metrics['total']:.4f}")
    
    print("\n--- By Category ---")
    for cat, data in metrics["by_type"].items():
        if data["total"] > 0:
            hr = data["hits"] / data["total"]
            mrr = data["mrr"] / data["total"]
            print(f"{cat}: Hit Rate={hr:.2%}, MRR={mrr:.4f} (n={data['total']})")

if __name__ == "__main__":
    evaluate()
