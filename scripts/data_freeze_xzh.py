import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
MOCK_DIR = FIXTURES / "mock_xzh"
README = FIXTURES / "README.md"

def md5sum(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()

def line_count(p: Path) -> int:
    with p.open("rb") as f:
        return sum(1 for _ in f)

def ensure_dirs():
    MOCK_DIR.mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def generate_mock():
    # 1. Course Data (Multiple Courses)
    courses = [
        {
            "course_id": "phys101_xzh",
            "title": "大学物理（Mock）",
            "description": "基础物理课程，涵盖力学、热学、电磁学。",
            "chapters": [
                {"id": "c1", "title": "力学", "sections": [
                    {"id": "s1", "title": "牛顿定律", "content": "牛顿三大定律是经典力学的基石。"},
                    {"id": "s2", "title": "功与能", "content": "能量守恒定律是自然界普遍规律。"}
                ]},
                {"id": "c2", "title": "电磁学", "sections": [
                    {"id": "s3", "title": "静电场", "content": "库仑定律描述电荷间的作用力。"}
                ]}
            ]
        },
        {
            "course_id": "cs101_xzh",
            "title": "计算机科学导论（Mock）",
            "description": "计算机科学基础，包括算法、数据结构、网络。",
            "chapters": [
                {"id": "c3", "title": "算法基础", "sections": [
                    {"id": "s4", "title": "排序算法", "content": "快速排序的时间复杂度为O(nlogn)。"},
                    {"id": "s5", "title": "查找算法", "content": "二分查找适用于有序数组。"}
                ]}
            ]
        }
    ]

    # 2. Knowledge Graph (Rich Relationships)
    graph = {
        "nodes": [
            {"id": "n1", "path": "力学/牛顿定律/二定律", "content": "F=ma 描述合外力与加速度的关系。", "score": 0.95, "type": "concept"},
            {"id": "n2", "path": "力学/能量/功与能", "content": "功是能量转化的量度。", "score": 0.88, "type": "concept"},
            {"id": "n3", "path": "计算机/算法/排序", "content": "快速排序是一种高效的排序算法。", "score": 0.90, "type": "concept"},
            {"id": "n4", "path": "计算机/算法/复杂度", "content": "时间复杂度衡量算法执行效率。", "score": 0.85, "type": "concept"}
        ],
        "edges": [
            {"from": "n1", "to": "n2", "type": "relates_to", "weight": 0.7},
            {"from": "n3", "to": "n4", "type": "depends_on", "weight": 0.9}
        ]
    }

    # 3. Retriever Docs (For RAG)
    docs = [
        {"content": n["content"], "metadata": {"id": n["id"], "path": n["path"], "score": n["score"]}}
        for n in graph["nodes"]
    ]
    
    # 4. QA Pairs (For Verification)
    qa_pairs = [
        {"question": "牛顿第二定律的内容是什么？", "answer": "F=ma，描述合外力与加速度成正比。", "related_nodes": ["n1"]},
        {"question": "快速排序的时间复杂度是多少？", "answer": "平均情况下为O(nlogn)。", "related_nodes": ["n3"]}
    ]

    return courses, graph, docs, qa_pairs

def append_readme(records):
    ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    lines = []
    lines.append(f"\n## Freeze {ts} (xzh)\n")
    lines.append("| File | MD5 | Lines | Note |\n")
    lines.append("| ---- | --- | ----- | ---- |\n")
    for r in records:
        rel = r['path'].relative_to(ROOT).as_posix()
        lines.append(f"| {rel} | {r['md5']} | {r['lines']} | mock_xzh |\n")
    with README.open("a", encoding="utf-8") as f:
        f.writelines(lines)

def main():
    ensure_dirs()
    courses, graph, docs, qa_pairs = generate_mock()

    course_p = MOCK_DIR / "courses_xzh.json"
    graph_p = MOCK_DIR / "graph_xzh.json"
    docs_p = MOCK_DIR / "retriever_docs_xzh.jsonl"
    qa_p = MOCK_DIR / "qa_pairs_xzh.json"

    write_json(course_p, courses)
    write_json(graph_p, graph)
    write_json(qa_p, qa_pairs)
    
    with docs_p.open("w", encoding="utf-8") as f:
        for d in docs:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    records = []
    for p in [course_p, graph_p, docs_p, qa_p]:
        records.append({"path": p, "md5": md5sum(p), "lines": line_count(p)})
    
    append_readme(records)
    print("Freeze completed:", [str(r["path"]) for r in records])

if __name__ == "__main__":
    main()
