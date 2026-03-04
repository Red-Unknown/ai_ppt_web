import json
import random
import os
from typing import List, Dict

# Path to knowledge base
KB_PATH = os.path.join(os.path.dirname(__file__), "../../backend/app/core/knowledge_base.json")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "retrieval_dataset_golden.json")

def load_kb():
    with open(KB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_leaf_nodes(node, nodes=None):
    if nodes is None:
        nodes = []
    if isinstance(node, dict):
        if "content" in node and "id" in node:
            nodes.append(node)
        else:
            for k, v in node.items():
                if isinstance(v, (dict, list)):
                    get_all_leaf_nodes(v, nodes)
    elif isinstance(node, list):
        for item in node:
            get_all_leaf_nodes(item, nodes)
    return nodes

def generate_typo(text):
    """Introduce random typos (char swap, deletion, insertion)."""
    if len(text) < 2:
        return text
    text = list(text)
    # 1. Swap
    if random.random() < 0.3:
        idx = random.randint(0, len(text) - 2)
        text[idx], text[idx+1] = text[idx+1], text[idx]
    # 2. Replace (simulate pinyin/homophone by just random char for now as simple noise)
    elif random.random() < 0.3:
        idx = random.randint(0, len(text) - 1)
        text[idx] = random.choice("的一是了我不人在有") # Common chars noise
    # 3. Delete
    elif random.random() < 0.3:
        idx = random.randint(0, len(text) - 1)
        del text[idx]
    return "".join(text)

def generate_dataset():
    data = load_kb()
    nodes = get_all_leaf_nodes(data.get("knowledge_tree", {}))
    
    dataset = []
    
    # 1. Exact Match (Title)
    for node in nodes:
        dataset.append({
            "query": node["title"],
            "expected_ids": [node["id"]],
            "type": "exact_title"
        })
        
    # 2. Typos (Title)
    for node in nodes:
        typo_title = generate_typo(node["title"])
        if typo_title != node["title"]:
            dataset.append({
                "query": typo_title,
                "expected_ids": [node["id"]],
                "type": "typo"
            })
            
    # 3. Content Query (Keywords from content)
    for node in nodes:
        # Extract a substring or keywords
        content = node["content"]
        if len(content) > 10:
            start = random.randint(0, len(content) - 10)
            query = content[start:start+10]
            dataset.append({
                "query": query,
                "expected_ids": [node["id"]],
                "type": "content_fragment"
            })
            
    # 4. Mixed/Multi Concept (Combine two nodes)
    if len(nodes) >= 2:
        for _ in range(20): # Generate 20 pairs
            n1, n2 = random.sample(nodes, 2)
            query = f"{n1['title']}与{n2['title']}的区别"
            dataset.append({
                "query": query,
                "expected_ids": [n1["id"], n2["id"]],
                "type": "multi_concept"
            })
            
    # 5. Synonym Query
    for node in nodes:
        if "synonyms" in node and node["synonyms"]:
            for syn in node["synonyms"]:
                dataset.append({
                    "query": syn,
                    "expected_ids": [node["id"]],
                    "type": "synonym"
                })

    # Save
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, indent=2, ensure_ascii=False)
    print(f"Generated {len(dataset)} test cases in {OUTPUT_PATH}")

if __name__ == "__main__":
    generate_dataset()
