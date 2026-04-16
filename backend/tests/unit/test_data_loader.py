import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.services.qa.retrieval.data_loader import (
    load_cir_data,
    load_raw_json_data,
    extract_text_blocks,
    _parse_page_range,
    text_blocks_to_dict
)


class TestDataLoader:

    def test_parse_page_range_single(self):
        result = _parse_page_range("5")
        assert result == [5]

    def test_parse_page_range_multiple(self):
        result = _parse_page_range("3,5,7")
        assert result == [3, 5, 7]

    def test_parse_page_range_range(self):
        result = _parse_page_range("3-5")
        assert result == [3, 4, 5]

    def test_parse_page_range_mixed(self):
        result = _parse_page_range("1,3-5,10")
        assert result == [1, 3, 4, 5, 10]

    def test_parse_page_range_empty(self):
        result = _parse_page_range("")
        assert result == []

    def test_load_cir_data_material_mechanics(self):
        data = load_cir_data("lesson_mm_001")
        assert len(data) > 0
        assert all("node_id" in d for d in data)
        assert all("page_num" in d for d in data)

    def test_load_cir_data_with_mapping(self):
        data = load_cir_data("lesson_ai_001")
        assert len(data) > 0
        assert data[0]["node_name"] is not None

    def test_load_cir_data_unknown(self):
        data = load_cir_data("unknown_lesson")
        assert len(data) >= 0

    def test_load_raw_json_data(self):
        data = load_raw_json_data("lesson_mm_001")
        assert data is not None
        assert "data" in data
        assert "structurePreview" in data["data"]

    def test_extract_text_blocks(self):
        raw_data = {
            "data": {
                "structurePreview": {
                    "chapters": [
                        {
                            "subChapters": [
                                {
                                    "pageRange": "1",
                                    "elements": [
                                        {"content": "测试内容", "bbox": {"x": 0.1, "y": 0.2, "width": 0.5, "height": 0.3}, "type": "text"}
                                    ]
                                }
                            ]
                        }
                    ]
                }
            }
        }
        blocks = extract_text_blocks(raw_data, [1])
        assert len(blocks) == 1
        assert blocks[0].content == "测试内容"
        assert blocks[0].page_num == 1

    def test_extract_text_blocks_empty_page_range(self):
        raw_data = {"data": {"structurePreview": {"chapters": []}}}
        blocks = extract_text_blocks(raw_data, [])
        assert len(blocks) == 0

    def test_text_blocks_to_dict(self):
        from backend.app.services.qa.retrieval.data_loader import TextBlock
        blocks = [TextBlock("id1", "content1", 1, {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.4}, "text")]
        result = text_blocks_to_dict(blocks)
        assert len(result) == 1
        assert result[0]["id"] == "id1"
