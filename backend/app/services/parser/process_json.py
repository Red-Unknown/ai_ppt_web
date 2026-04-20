import json
from pathlib import Path
from typing import Any, Dict, List


def extract_content_by_page(json_data: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    chapters = json_data.get("data", {}).get("structurePreview", {}).get("chapters", [])
    for chapter in chapters:
        sub_chapters = chapter.get("subChapters", [])
        for sub_chapter in sub_chapters:
            page_content: List[str] = []
            elements = sub_chapter.get("elements", [])
            for element in elements:
                elem_type = element.get("type")
                if elem_type == "text":
                    content = (element.get("content", "") or "").strip().replace("\n", "")
                    if content:
                        page_content.append(content)
                elif elem_type == "image":
                    relationship = element.get("relationship", "")
                    content_data = element.get("content_data", "")
                    if relationship or content_data:
                        page_content.append(f"'{relationship},{content_data}'")
            if page_content:
                result.append("\n".join(page_content))
    return result


def convert_json_to_text(json_path: str, output_path: str) -> int:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    pages_content = extract_content_by_page(data)
    Path(output_path).write_text("\n\n".join(pages_content) + ("\n" if pages_content else ""), encoding="utf-8-sig")
    return len(pages_content)


def main() -> None:
    json_path = "sandbox/extract.json"
    output_path = "sandbox/output.txt"
    try:
        count = convert_json_to_text(json_path, output_path)
        print(f"处理完成！已生成 {output_path}")
        print(f"共处理 {count} 页")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
