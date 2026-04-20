import json
import re
from pathlib import Path
from typing import Any, Dict, List


def normalize_brackets(text: str) -> str:
    text = text.replace("（", "(").replace("）", ")")
    text = text.replace("【", "(").replace("】", ")")
    text = text.replace("[", "(").replace("]", ")")
    text = text.replace("「", "(").replace("」", ")")
    text = text.replace("『", "(").replace("』", ")")
    return text


def normalize_page_numbering(page_text: str) -> str:
    lines = page_text.split("\n")
    result: List[str] = []
    letter_pattern = re.compile(r"^\(([a-zA-Z])\)\s*")
    circle_pattern = re.compile(r"^([①②③④⑤⑥⑦⑧⑨⑩])")
    circle_to_num = {"①": "1", "②": "2", "③": "3", "④": "4", "⑤": "5", "⑥": "6", "⑦": "7", "⑧": "8", "⑨": "9", "⑩": "10"}

    for line in lines:
        stripped = line.strip()
        if not stripped:
            result.append(line)
            continue
        letter_match = letter_pattern.match(stripped)
        circle_match = circle_pattern.match(stripped)
        if letter_match:
            content = letter_pattern.sub("", stripped).strip()
            result.append(f"(1) {content}")
        elif circle_match:
            circle_num = circle_match.group(1)
            content = circle_pattern.sub("", stripped).strip()
            result.append(f"({circle_to_num[circle_num]}) {content}")
        else:
            result.append(line)
    return "\n".join(result)


def extract_content_with_page_number(json_data: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    chapters = json_data.get("data", {}).get("structurePreview", {}).get("chapters", [])
    page_number = 1
    for chapter in chapters:
        for sub_chapter in chapter.get("subChapters", []) or []:
            page_content: List[str] = []
            for element in sub_chapter.get("elements", []) or []:
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
                page_text = normalize_brackets("\n".join(page_content))
                page_text = normalize_page_numbering(page_text)
                result.append(f"=== 第 {page_number} 页 ===\n{page_text}")
                page_number += 1
    return result


def convert_json_to_text_with_page(json_path: str, output_path: str) -> int:
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    pages = extract_content_with_page_number(data)
    Path(output_path).write_text("\n\n".join(pages) + ("\n" if pages else ""), encoding="utf-8-sig")
    return len(pages)


def main() -> None:
    json_path = "sandbox/extract.json"
    output_path = "sandbox/output_with_page.txt"
    try:
        count = convert_json_to_text_with_page(json_path, output_path)
        print(f"处理完成！已生成 {output_path}")
        print(f"共处理 {count} 页")
    except Exception as e:
        print(f"处理过程中发生错误: {str(e)}")


if __name__ == "__main__":
    main()
