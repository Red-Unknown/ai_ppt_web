import asyncio
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from backend.app.core.database import SessionLocal
from backend.app.models.cir import CIRSection
from backend.app.models.course import Lesson
from backend.app.services.parser.generate_mindmap import generate_mindmap_async
from backend.app.services.parser.lesson_parser import LessonParserService
from backend.app.services.script.async_tts_service import async_tts_service
from backend.app.services.script_generator import generate_script_for_node


def _extract_content_by_page(json_data: Dict[str, Any]) -> List[str]:
    result: List[str] = []
    chapters = json_data.get("data", {}).get("structurePreview", {}).get("chapters", [])
    for chapter in chapters:
        for sub_chapter in chapter.get("subChapters", []) or []:
            page_content: List[str] = []
            for element in sub_chapter.get("elements", []) or []:
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


def _build_raw_json_payload(parsed: Dict[str, Any], lesson_id: str) -> Dict[str, Any]:
    return {
        "code": 200,
        "msg": "课件解析成功",
        "data": {
            "parseId": lesson_id,
            "fileInfo": _to_plain(parsed["fileInfo"]),
            "structurePreview": _to_plain(parsed["structurePreview"]),
            "taskStatus": "completed",
        },
        "requestId": f"req{uuid.uuid4().hex[:12]}",
    }


def _to_plain(obj: Any) -> Any:
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "dict"):
        return obj.dict()
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_to_plain(v) for v in obj]
    return obj


def _safe_parse_page_num(page_range: str) -> Optional[int]:
    if not page_range:
        return None
    token = str(page_range).split(",")[0].split("-")[0].strip()
    return int(token) if token.isdigit() else None


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
                "bbox": None,
                "image_url": None,
            }
        )
        for s_idx, sub in enumerate(chapter.get("subChapters", []) or []):
            sub_id = sub.get("subChapterId") or f"{chapter_id}_sub_{s_idx}"
            sub_name = sub.get("subChapterName") or f"小节{s_idx + 1}"
            page_num = _safe_parse_page_num(sub.get("pageRange") or "")
            elements = sub.get("elements", []) or []
            text_parts: List[str] = []
            bbox = None
            image_url = None
            for element in elements:
                content = (element.get("content") or "").strip()
                if content:
                    text_parts.append(content)
                if bbox is None and isinstance(element.get("bbox"), dict):
                    bbox = element.get("bbox")
                if image_url is None and element.get("type") == "image":
                    image_url = element.get("image_url") or element.get("url")
            teaching_content = "\n".join(text_parts).strip() or sub_name
            key_points = [line for line in teaching_content.splitlines() if line.strip().startswith("§")][:8]
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
                    "key_points": key_points,
                    "bbox": bbox,
                    "image_url": image_url,
                }
            )
    return rows


async def _run_qdrant_ingest(raw_json_path: Path, lesson_id: str, school_id: str) -> Tuple[bool, str]:
    script_path = Path("scripts/indexing/ingest_to_qdrant.py")
    cmd = [
        sys.executable,
        str(script_path),
        "--input-json",
        str(raw_json_path),
        "--lesson-id",
        lesson_id,
        "--school-id",
        school_id,
        "--rebuild",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = out.decode("utf-8", errors="ignore")
    return proc.returncode == 0, text


async def run_full_pipeline(
    file_path: str,
    file_type: str,
    output_raw_json_path: str,
    output_text_path: str,
    lesson_id: Optional[str] = None,
    course_id: Optional[str] = None,
    school_id: str = "default_school",
    title: Optional[str] = None,
    voice: str = "zh-CN-XiaoxiaoNeural",
    enable_script_llm: bool = True,
) -> AsyncGenerator[Dict[str, Any], None]:
    start = datetime.now(timezone.utc)
    yield {"type": "status", "step": "start", "message": "开始执行全流程"}

    parser = LessonParserService()
    parsed = await asyncio.to_thread(parser.parse_courseware, file_path, file_type)
    final_lesson_id = lesson_id or f"parse{uuid.uuid4().hex[:12]}"
    payload = _build_raw_json_payload(parsed, final_lesson_id)
    raw_json_path = Path(output_raw_json_path)
    raw_json_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(
        lambda: raw_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    )
    yield {"type": "status", "step": "raw_json", "path": str(raw_json_path), "lesson_id": final_lesson_id}

    pages = await asyncio.to_thread(_extract_content_by_page, payload)
    content_text = "\n\n".join(pages)
    txt_path = Path(output_text_path)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(lambda: txt_path.write_text(content_text + ("\n" if content_text else ""), encoding="utf-8-sig"))
    yield {"type": "status", "step": "content_text", "pages": len(pages), "path": str(txt_path)}

    mind_map, keywords = await generate_mindmap_async(content_text)
    yield {"type": "status", "step": "mind_map", "keywords_count": len(keywords)}

    cir_rows = _build_cir_rows(payload, final_lesson_id, school_id)

    def _save_base_rows() -> int:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
            if not lesson:
                lesson = Lesson(
                    lesson_id=final_lesson_id,
                    course_id=course_id,
                    school_id=school_id,
                    title=title or (payload.get("data", {}).get("fileInfo", {}).get("fileName") or final_lesson_id),
                    file_type=file_type,
                    file_url=file_path,
                    task_status="processing",
                    file_info=payload.get("data", {}).get("fileInfo"),
                )
                db.add(lesson)
            lesson.mind_map = {"mind_map": mind_map, "keywords": keywords}
            db.query(CIRSection).filter(CIRSection.lesson_id == final_lesson_id).delete()
            for row in cir_rows:
                db.add(
                    CIRSection(
                        node_id=row["node_id"],
                        lesson_id=row["lesson_id"],
                        school_id=row["school_id"],
                        node_name=row["node_name"],
                        parent_id=row["parent_id"],
                        node_type=row["node_type"],
                        sort_order=row["sort_order"],
                        path=row["path"],
                        page_num=row["page_num"],
                        image_url=row["image_url"],
                        bbox=row["bbox"],
                        key_points=row["key_points"],
                        teaching_content=row["teaching_content"],
                    )
                )
            db.commit()
            return len(cir_rows)
        finally:
            db.close()

    inserted = await asyncio.to_thread(_save_base_rows)
    yield {"type": "status", "step": "postgres_cir_base", "inserted_nodes": inserted}

    def _generate_scripts() -> int:
        db = SessionLocal()
        try:
            nodes = (
                db.query(CIRSection)
                .filter(CIRSection.lesson_id == final_lesson_id, CIRSection.node_type == "subchapter")
                .order_by(CIRSection.sort_order.asc())
                .all()
            )
            cnt = 0
            for node in nodes:
                node.script_content = generate_script_for_node(node, use_llm=enable_script_llm)
                cnt += 1
            db.commit()
            return cnt
        finally:
            db.close()

    script_count = await asyncio.to_thread(_generate_scripts)
    yield {"type": "status", "step": "script", "generated": script_count, "llm": enable_script_llm}

    await async_tts_service.start()
    db = SessionLocal()
    try:
        nodes = (
            db.query(CIRSection)
            .filter(CIRSection.lesson_id == final_lesson_id, CIRSection.node_type == "subchapter")
            .order_by(CIRSection.sort_order.asc())
            .all()
        )
        total = len(nodes)
        for idx, node in enumerate(nodes, start=1):
            text = (node.script_content or node.teaching_content or node.node_name or "")[:800]
            task_id, _ = await async_tts_service.synthesize_async(text=text, voice=voice, client_id=final_lesson_id)
            node.audio_url = f"tts_task://{task_id}" if task_id else None
            yield {"type": "progress", "step": "tts", "current": idx, "total": total}
        db.commit()
    finally:
        db.close()
    yield {"type": "status", "step": "tts_done"}

    ok, qdrant_log = await _run_qdrant_ingest(raw_json_path, final_lesson_id, school_id)
    yield {"type": "status", "step": "qdrant", "ok": ok, "log": qdrant_log[-2000:]}

    def _finish_lesson() -> None:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
            if lesson:
                lesson.task_status = "completed" if ok else "failed"
                lesson.completed_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    await asyncio.to_thread(_finish_lesson)
    elapsed_s = (datetime.now(timezone.utc) - start).total_seconds()
    yield {"type": "done", "step": "end", "lesson_id": final_lesson_id, "elapsed_seconds": round(elapsed_s, 3)}
