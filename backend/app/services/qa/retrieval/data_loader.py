import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass


CIR_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "sandbox"
RAW_JSON_DATA_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent.parent / "sandbox"


@dataclass
class CIRSection:
    node_id: str
    node_name: str
    node_type: str
    page_num: Optional[int]
    key_points: List[str]
    teaching_content: str
    path: str
    score: float = 0.0


@dataclass
class TextBlock:
    id: str
    content: str
    page_num: int
    bbox: Optional[Dict[str, float]]
    element_type: str


def load_cir_data(lesson_id: str) -> List[Dict[str, Any]]:
    cir_file = CIR_DATA_DIR / f"cir_sample_{lesson_id}.json"
    if not cir_file.exists():
        lesson_name_map = {
            "lesson_mm_001": "material_mechanics",
            "lesson_ai_001": "ai_intro"
        }
        short_name = lesson_name_map.get(lesson_id)
        if short_name:
            cir_file = CIR_DATA_DIR / f"cir_sample_{short_name}.json"

    if not cir_file.exists():
        alt_file = CIR_DATA_DIR / "cir_sample_material_mechanics.json"
        if alt_file.exists():
            cir_file = alt_file
        else:
            return []

    try:
        with open(cir_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        sections = data.get("cir_sections", [])
        result = []
        for section in sections:
            if section.get("node_type") == "subchapter":
                result.append({
                    "node_id": section.get("node_id"),
                    "node_name": section.get("node_name"),
                    "node_type": section.get("node_type"),
                    "page_num": section.get("page_num"),
                    "key_points": section.get("key_points", []),
                    "teaching_content": section.get("teaching_content", ""),
                    "path": section.get("path"),
                    "lesson_id": section.get("lesson_id")
                })
        return result
    except Exception as e:
        print(f"Error loading CIR data: {e}")
        return []


def load_raw_json_data(lesson_id: str) -> Optional[Dict[str, Any]]:
    raw_json_file = RAW_JSON_DATA_DIR / "extract.json"

    if not raw_json_file.exists():
        return None

    try:
        with open(raw_json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        print(f"Error loading Raw JSON data: {e}")
        return None


def extract_text_blocks(raw_data: Dict[str, Any], page_range: List[int]) -> List[TextBlock]:
    if not raw_data:
        return []

    blocks = []
    page_set = set(page_range)

    structure = raw_data.get("data", {}).get("structurePreview", {})
    chapters = structure.get("chapters", [])

    block_id = 0
    for chapter in chapters:
        sub_chapters = chapter.get("subChapters", [])
        for sub_chapter in sub_chapters:
            page_range_str = sub_chapter.get("pageRange", "")
            page_nums = _parse_page_range(page_range_str)

            if not page_set.intersection(set(page_nums)):
                continue

            elements = sub_chapter.get("elements", [])
            for element in elements:
                content = element.get("content", "")
                if not content or not content.strip():
                    continue

                element_bbox = element.get("bbox")
                element_type = element.get("type", "text")

                for page_num in page_nums:
                    if page_num in page_set:
                        blocks.append(TextBlock(
                            id=f"block_{block_id}",
                            content=content,
                            page_num=page_num,
                            bbox=element_bbox,
                            element_type=element_type
                        ))
                        block_id += 1
                        break

    return blocks


def _parse_page_range(page_range_str: str) -> List[int]:
    if not page_range_str:
        return []

    page_nums = []
    parts = page_range_str.split(",")

    for part in parts:
        part = part.strip()
        if "-" in part:
            try:
                start, end = part.split("-")
                page_nums.extend(range(int(start), int(end) + 1))
            except ValueError:
                continue
        else:
            try:
                page_nums.append(int(part))
            except ValueError:
                continue

    return page_nums


def text_blocks_to_dict(blocks: List[TextBlock]) -> List[Dict[str, Any]]:
    return [
        {
            "id": b.id,
            "content": b.content,
            "page_num": b.page_num,
            "bbox": b.bbox,
            "element_type": b.element_type
        }
        for b in blocks
    ]
