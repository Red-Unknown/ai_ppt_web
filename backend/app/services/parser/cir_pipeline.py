import asyncio
import json
import os
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Tuple

from backend.app.core.database import SessionLocal
from backend.app.models.cir import CIRSection
from backend.app.models.course import Lesson
from backend.app.services.parser.generate_mindmap import generate_mindmap_async
from backend.app.services.script.async_tts_service import async_tts_service


def _extract_content_pages(json_data: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    chapters = json_data.get("data", {}).get("structurePreview", {}).get("chapters", [])
    for chapter in chapters:
        for sub in chapter.get("subChapters", []) or []:
            page_content: List[str] = []
            for element in sub.get("elements", []) or []:
                elem_type = element.get("type")
                if elem_type == "text":
                    content = (element.get("content") or "").strip().replace("\n", "")
                    if content:
                        page_content.append(content)
                elif elem_type == "image":
                    relationship = element.get("relationship") or ""
                    content_data = element.get("content_data") or ""
                    if relationship or content_data:
                        page_content.append(f"'{relationship},{content_data}'")
            if page_content:
                result.append("\n".join(page_content))
    return result


def _build_cir_rows(parsed_json: Dict[str, Any], lesson_id: str, school_id: str) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    chapters = parsed_json.get("data", {}).get("structurePreview", {}).get("chapters", [])
    for c_idx, chapter in enumerate(chapters):
        chapter_id = chapter.get("chapterId") or f"chapter_{c_idx}"
        chapter_name = chapter.get("chapterName") or f"章节{c_idx + 1}"
        rows.append(
            {
                "node_id": chapter_id,
                "lesson_id": lesson_id,
                "school_id": school_id,
                "node_name": chapter_name,
                "parent_id": None,
                "node_type": "chapter",
                "sort_order": c_idx,
                "path": f"/{chapter_name}",
                "page_num": None,
                "teaching_content": chapter_name,
                "key_points": [],
            }
        )
        for s_idx, sub in enumerate(chapter.get("subChapters", []) or []):
            sub_id = sub.get("subChapterId") or f"{chapter_id}_sub_{s_idx}"
            sub_name = sub.get("subChapterName") or f"小节{s_idx + 1}"
            page_range = str(sub.get("pageRange") or "")
            page_num = int(page_range.split(",")[0].split("-")[0]) if page_range and page_range[0].isdigit() else None
            text_parts: List[str] = []
            for element in sub.get("elements", []) or []:
                content = (element.get("content") or "").strip()
                if content:
                    text_parts.append(content)
            teaching_content = "\n".join(text_parts).strip() or sub_name
            rows.append(
                {
                    "node_id": sub_id,
                    "lesson_id": lesson_id,
                    "school_id": school_id,
                    "node_name": sub_name,
                    "parent_id": chapter_id,
                    "node_type": "subchapter",
                    "sort_order": s_idx,
                    "path": f"/{chapter_name}/{sub_name}",
                    "page_num": page_num,
                    "teaching_content": teaching_content,
                    "key_points": [line for line in teaching_content.splitlines() if line.strip().startswith("§")][:8],
                }
            )
    return rows


async def run_cir_pipeline(
    json_path: str,
    output_text_path: str,
    lesson_id: str | None = None,
    course_id: str | None = None,
    school_id: str = "default_school",
    title: str | None = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
) -> AsyncGenerator[Dict[str, Any], None]:
    yield {"type": "status", "step": "start", "message": "开始执行CIR异步流水线"}

    parsed_json = await asyncio.to_thread(lambda: json.loads(Path(json_path).read_text(encoding="utf-8")))
    final_lesson_id = lesson_id or parsed_json.get("data", {}).get("parseId") or f"parse_{uuid.uuid4().hex[:10]}"
    file_name = parsed_json.get("data", {}).get("fileInfo", {}).get("fileName", "")
    final_title = title or (file_name or final_lesson_id)
    yield {"type": "status", "step": "load_json", "lesson_id": final_lesson_id, "message": "解析JSON已加载"}

    pages = await asyncio.to_thread(_extract_content_pages, parsed_json)
    out_path = Path(output_text_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(
        lambda: out_path.write_text("\n\n".join(pages) + ("\n" if pages else ""), encoding="utf-8-sig")
    )
    yield {"type": "status", "step": "extract_content", "pages": len(pages), "output_text_path": str(out_path)}

    content_text = "\n\n".join(pages)
    mind_map, keywords = await generate_mindmap_async(content_text)
    yield {"type": "status", "step": "mindmap", "keywords_count": len(keywords), "message": "思维导图与关键词生成完成"}

    yield {"type": "status", "step": "script", "message": "i讲稿生成暂未实现，已跳过"}

    cir_rows = _build_cir_rows(parsed_json, final_lesson_id, school_id)
    await async_tts_service.start()
    for idx, row in enumerate(cir_rows, start=1):
        if row["node_type"] != "subchapter":
            continue
        text = (row.get("teaching_content") or row["node_name"])[:600]
        task_id, _ = await async_tts_service.synthesize_async(text=text, voice=voice, client_id=final_lesson_id)
        row["audio_url"] = f"tts_task://{task_id}" if task_id else None
        yield {"type": "progress", "step": "tts", "current": idx, "total": len(cir_rows)}

    def _save_db() -> Tuple[int, int]:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
            if not lesson:
                lesson = Lesson(
                    lesson_id=final_lesson_id,
                    course_id=course_id,
                    school_id=school_id,
                    title=final_title,
                    file_type="ppt",
                    file_url=json_path,
                    task_status="completed",
                    file_info=parsed_json.get("data", {}).get("fileInfo"),
                )
                db.add(lesson)
            lesson.mind_map = {"mind_map": mind_map, "keywords": keywords}
            lesson.task_status = "completed"

            db.query(CIRSection).filter(CIRSection.lesson_id == final_lesson_id).delete()
            insert_count = 0
            for row in cir_rows:
                db.add(
                    CIRSection(
                        node_id=row["node_id"],
                        lesson_id=row["lesson_id"],
                        school_id=row["school_id"],
                        node_name=row["node_name"],
                        parent_id=row.get("parent_id"),
                        node_type=row["node_type"],
                        sort_order=row["sort_order"],
                        path=row.get("path"),
                        page_num=row.get("page_num"),
                        key_points=row.get("key_points"),
                        teaching_content=row.get("teaching_content"),
                        script_content=row.get("teaching_content"),  # i讲稿未实现，先落教学内容占位
                        audio_url=row.get("audio_url"),
                    )
                )
                insert_count += 1
            db.commit()
            return insert_count, len(keywords)
        finally:
            db.close()

    inserted, kw_count = await asyncio.to_thread(_save_db)
    yield {
        "type": "done",
        "step": "store_cir",
        "lesson_id": final_lesson_id,
        "inserted_nodes": inserted,
        "keywords_count": kw_count,
        "message": "CIR入库完成",
    }
