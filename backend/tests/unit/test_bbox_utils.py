import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.services.qa.retrieval.bbox_utils import (
    Bbox, TextBlockWithBbox, MergedBboxResult, merge_bboxes_by_page, format_bbox_for_response
)


class TestBboxMerge:

    def test_bbox_to_list(self):
        bbox = Bbox(0.1, 0.2, 0.5, 0.3)
        assert bbox.to_list() == [0.1, 0.2, 0.5, 0.3]

    def test_bbox_from_dict(self):
        d = {"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.3}
        bbox = Bbox.from_dict(d)
        assert bbox.x == 0.1
        assert bbox.y == 0.2

    def test_bbox_from_dict_none(self):
        bbox = Bbox.from_dict(None)
        assert bbox is None

    def test_merge_single_page_bboxes(self):
        blocks = [
            TextBlockWithBbox(
                content="text1",
                bbox=Bbox(0.1, 0.1, 0.2, 0.1),
                page_num=1,
                element_type="text"
            ),
            TextBlockWithBbox(
                content="text2",
                bbox=Bbox(0.3, 0.2, 0.2, 0.1),
                page_num=1,
                element_type="text"
            )
        ]
        results = merge_bboxes_by_page(blocks)

        assert len(results) == 1
        assert results[0].page_num == 1
        assert results[0].merged_bbox.x == 0.1
        assert results[0].merged_bbox.y == 0.1
        assert results[0].merged_bbox.width == 0.4

    def test_keep_different_pages_separate(self):
        blocks = [
            TextBlockWithBbox(
                content="text1",
                bbox=Bbox(0.1, 0.1, 0.2, 0.1),
                page_num=1,
                element_type="text"
            ),
            TextBlockWithBbox(
                content="text2",
                bbox=Bbox(0.3, 0.2, 0.2, 0.1),
                page_num=2,
                element_type="text"
            )
        ]
        results = merge_bboxes_by_page(blocks)

        assert len(results) == 2
        assert [r.page_num for r in results] == [1, 2]

    def test_merge_empty_blocks(self):
        blocks = []
        results = merge_bboxes_by_page(blocks)
        assert results == []

    def test_merge_blocks_without_bbox(self):
        blocks = [
            TextBlockWithBbox(
                content="text1",
                bbox=None,
                page_num=1,
                element_type="text"
            )
        ]
        results = merge_bboxes_by_page(blocks)
        assert results == []

    def test_format_bbox_for_response(self):
        merged = [
            MergedBboxResult(
                page_num=1,
                bboxes=[Bbox(0.1, 0.1, 0.2, 0.1)],
                merged_bbox=Bbox(0.1, 0.1, 0.2, 0.1),
                total_area_ratio=0.02,
                is_merged=False
            )
        ]
        formatted = format_bbox_for_response(merged)

        assert len(formatted) == 1
        assert formatted[0]["page_num"] == 1
        assert formatted[0]["bboxes"][0] == [0.1, 0.1, 0.2, 0.1]
