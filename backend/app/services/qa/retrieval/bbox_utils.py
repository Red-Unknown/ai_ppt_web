from typing import List, Dict, Optional, Any
from dataclasses import dataclass


@dataclass
class Bbox:
    x: float
    y: float
    width: float
    height: float

    def to_list(self) -> List[float]:
        return [self.x, self.y, self.width, self.height]

    @staticmethod
    def from_dict(d: Dict[str, float]) -> Optional["Bbox"]:
        if not d:
            return None
        return Bbox(
            x=d.get("x", 0),
            y=d.get("y", 0),
            width=d.get("width", 0),
            height=d.get("height", 0)
        )


@dataclass
class TextBlockWithBbox:
    content: str
    bbox: Optional[Bbox]
    page_num: int
    element_type: str = "text"


@dataclass
class MergedBboxResult:
    page_num: int
    bboxes: List[Bbox]
    merged_bbox: Bbox
    total_area_ratio: float
    is_merged: bool = True


def merge_bboxes_by_page(blocks: List[TextBlockWithBbox]) -> List[MergedBboxResult]:
    from collections import defaultdict
    page_groups: Dict[int, List[TextBlockWithBbox]] = defaultdict(list)

    for block in blocks:
        page_groups[block.page_num].append(block)

    results = []
    for page_num, page_blocks in page_groups.items():
        bboxes = [b.bbox for b in page_blocks if b.bbox is not None]
        if not bboxes:
            continue

        merged = _merge_bbox_list(bboxes)
        area_ratio = merged.width * merged.height

        results.append(MergedBboxResult(
            page_num=page_num,
            bboxes=bboxes,
            merged_bbox=merged,
            total_area_ratio=area_ratio,
            is_merged=len(bboxes) > 1
        ))

    return sorted(results, key=lambda x: x.page_num)


def _merge_bbox_list(bboxes: List[Bbox]) -> Bbox:
    if not bboxes:
        return Bbox(0, 0, 0, 0)

    min_x = min(b.x for b in bboxes)
    min_y = min(b.y for b in bboxes)
    max_x = max(b.x + b.width for b in bboxes)
    max_y = max(b.y + b.height for b in bboxes)

    return Bbox(
        x=min_x,
        y=min_y,
        width=max_x - min_x,
        height=max_y - min_y
    )


def format_bbox_for_response(merged_results: List[MergedBboxResult]) -> List[Dict[str, Any]]:
    return [
        {
            "page_num": r.page_num,
            "bboxes": [b.to_list() for b in r.bboxes],
            "merged_bbox": r.merged_bbox.to_list(),
            "is_merged": r.is_merged,
            "total_area_ratio": round(r.total_area_ratio, 4)
        }
        for r in merged_results
    ]
