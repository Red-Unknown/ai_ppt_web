import asyncio
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

from backend.app.core.database import SessionLocal
from backend.app.core.logging_config import get_logger
from backend.app.models.cir import CIRSection
from backend.app.models.course import Lesson
from backend.app.services.parser.generate_mindmap import generate_mindmap_async
from backend.app.services.parser.lesson_parser import LessonParserService
from backend.app.services.script.async_tts_service import async_tts_service
try:
    from backend.app.services.script_generator import generate_script_for_node, generate_scripts_for_sections
except Exception:
    generate_script_for_node = None
    generate_scripts_for_sections = None

logger = get_logger(__name__)


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


def _run_qdrant_ingest_sync(raw_json_path: Path, lesson_id: str, school_id: str) -> Tuple[bool, str]:
    script_path = Path("scripts/indexing/ingest_to_qdrant.py")
    if not script_path.exists():
        return False, f"qdrant ingest script not found: {script_path}"
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
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    text = f"{proc.stdout or ''}{proc.stderr or ''}"
    return proc.returncode == 0, text


async def _run_qdrant_ingest(raw_json_path: Path, lesson_id: str, school_id: str) -> Tuple[bool, str]:
    return await asyncio.to_thread(_run_qdrant_ingest_sync, raw_json_path, lesson_id, school_id)


def _fallback_script_content(node_name: str, teaching_content: str) -> str:
    base = (teaching_content or node_name or "").strip()
    return base if base else "本节内容待补充。"


def _derive_output_file(base_path: Path, suffix: str) -> Path:
    return base_path.with_name(f"{base_path.stem}_{suffix}{base_path.suffix}")


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
    start_event = {"type": "status", "step": "start", "message": "开始执行全流程"}
    logger.info("[full_pipeline] start")
    yield start_event

    parser = LessonParserService()
    parsed = await asyncio.to_thread(parser.parse_courseware, file_path, file_type)
    final_lesson_id = lesson_id or f"parse{uuid.uuid4().hex[:12]}"
    payload = _build_raw_json_payload(parsed, final_lesson_id)
    raw_json_path = Path(output_raw_json_path)
    raw_json_path.parent.mkdir(parents=True, exist_ok=True)
    mind_map_path = _derive_output_file(raw_json_path, "mind_map")
    scripts_path = _derive_output_file(raw_json_path, "scripts")
    await asyncio.to_thread(
        lambda: raw_json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    )
    parse_event = {
        "type": "status",
        "step": "vl_llm_parse_complete",
        "path": str(raw_json_path),
        "lesson_id": final_lesson_id,
        "parse_elapsed_seconds": parsed.get("parseElapsedSeconds"),
        "message": "课件解析完成（含图片理解）",
    }
    logger.info(
        f"[full_pipeline] vl_llm_parse_complete lesson_id={final_lesson_id} "
        f"elapsed={parse_event.get('parse_elapsed_seconds')} path={raw_json_path}"
    )
    yield parse_event

    pages = await asyncio.to_thread(_extract_content_by_page, payload)
    content_text = "\n\n".join(pages)
    txt_path = Path(output_text_path)
    txt_path.parent.mkdir(parents=True, exist_ok=True)
    await asyncio.to_thread(lambda: txt_path.write_text(content_text + ("\n" if content_text else ""), encoding="utf-8-sig"))
    content_event = {"type": "status", "step": "content_text", "pages": len(pages), "path": str(txt_path)}
    logger.info(f"[full_pipeline] content_text pages={len(pages)} path={txt_path}")
    yield content_event

    cir_rows = _build_cir_rows(payload, final_lesson_id, school_id)

    async def _generate_mind_map() -> Tuple[Any, List[str]]:
        return await generate_mindmap_async(content_text)

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

    def _generate_scripts_in_memory() -> Tuple[Dict[str, str], int]:
        script_map: Dict[str, str] = {}
        subchapter_rows = [row for row in cir_rows if row.get("node_type") == "subchapter"]
        generated = len(subchapter_rows)

        if generate_scripts_for_sections:
            lesson_title = title or (payload.get("data", {}).get("fileInfo", {}).get("fileName") or final_lesson_id)
            sections = [
                {
                    "node_name": row.get("node_name") or "",
                    "teaching_content": row.get("teaching_content") or "",
                    "page_num": row.get("page_num"),
                }
                for row in subchapter_rows
            ]
            try:
                content_map = generate_scripts_for_sections(sections, lesson_title, use_llm=enable_script_llm)
            except Exception:
                content_map = {}

            for row in subchapter_rows:
                node_id = row.get("node_id")
                node_name = row.get("node_name") or ""
                teaching_content = row.get("teaching_content") or ""
                script_map[node_id] = content_map.get(node_name) or _fallback_script_content(node_name, teaching_content)
            return script_map, generated

        for row in subchapter_rows:
            node_id = row.get("node_id")
            node_name = row.get("node_name") or ""
            teaching_content = row.get("teaching_content") or ""
            if generate_script_for_node:
                class _Node:
                    def __init__(self, node_name: str, teaching_content: str) -> None:
                        self.node_name = node_name
                        self.teaching_content = teaching_content

                content = generate_script_for_node(_Node(node_name, teaching_content), use_llm=enable_script_llm)
            else:
                content = _fallback_script_content(node_name, teaching_content)
            script_map[node_id] = content
        return script_map, generated

    parallel_tasks = {
        "mind_map": asyncio.create_task(_generate_mind_map()),
        "postgres_cir_base": asyncio.create_task(asyncio.to_thread(_save_base_rows)),
        "script": asyncio.create_task(asyncio.to_thread(_generate_scripts_in_memory)),
    }
    mind_map = None
    keywords: List[str] = []
    inserted = 0
    script_map: Dict[str, str] = {}
    script_count = 0

    pending = dict(parallel_tasks)
    while pending:
        done, _ = await asyncio.wait(pending.values(), return_when=asyncio.FIRST_COMPLETED)
        for finished in done:
            key = next(name for name, task in pending.items() if task is finished)
            result = finished.result()
            if key == "mind_map":
                mind_map, keywords = result
                mind_map_payload = {
                    "lesson_id": final_lesson_id,
                    "keywords": keywords,
                    "mind_map": mind_map,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                }
                await asyncio.to_thread(
                    lambda: mind_map_path.write_text(
                        json.dumps(mind_map_payload, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                )
                mind_map_event = {
                    "type": "status",
                    "step": "mind_map",
                    "keywords_count": len(keywords),
                    "path": str(mind_map_path),
                }
                logger.info(
                    f"[full_pipeline] mind_map keywords={len(keywords)} path={mind_map_path}"
                )
                yield mind_map_event
            elif key == "postgres_cir_base":
                inserted = int(result)
                postgres_event = {"type": "status", "step": "postgres_cir_base", "inserted_nodes": inserted}
                logger.info(f"[full_pipeline] postgres_cir_base inserted_nodes={inserted}")
                yield postgres_event
            elif key == "script":
                script_map, script_count = result
                script_rows = []
                for row in cir_rows:
                    if row.get("node_type") != "subchapter":
                        continue
                    node_id = row.get("node_id")
                    script_rows.append(
                        {
                            "node_id": node_id,
                            "node_name": row.get("node_name"),
                            "page_num": row.get("page_num"),
                            "script_content": script_map.get(node_id, ""),
                        }
                    )
                llm_used = bool(enable_script_llm and (generate_scripts_for_sections or generate_script_for_node))
                scripts_payload = {
                    "lesson_id": final_lesson_id,
                    "script_count": script_count,
                    "llm_enabled": llm_used,
                    "generated_at": datetime.now(timezone.utc).isoformat(),
                    "scripts": script_rows,
                }
                await asyncio.to_thread(
                    lambda: scripts_path.write_text(
                        json.dumps(scripts_payload, ensure_ascii=False, indent=2), encoding="utf-8"
                    )
                )
                script_event = {
                    "type": "status",
                    "step": "script",
                    "generated": script_count,
                    "llm": llm_used,
                    "path": str(scripts_path),
                }
                logger.info(
                    f"[full_pipeline] script generated={script_count} llm={llm_used} path={scripts_path}"
                )
                yield script_event
            pending.pop(key)

    def _apply_parallel_outputs() -> None:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
            if lesson:
                lesson.mind_map = {"mind_map": mind_map, "keywords": keywords}
            nodes = db.query(CIRSection).filter(CIRSection.lesson_id == final_lesson_id).all()
            for node in nodes:
                if node.node_id in script_map:
                    node.script_content = script_map[node.node_id]
            db.commit()
        finally:
            db.close()

    await asyncio.to_thread(_apply_parallel_outputs)

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
            tts_event = {"type": "progress", "step": "tts", "current": idx, "total": total}
            logger.info(f"[full_pipeline] tts progress {idx}/{total}")
            yield tts_event
        db.commit()
    finally:
        db.close()
    logger.info("[full_pipeline] tts_done")
    yield {"type": "status", "step": "tts_done"}

    def _finish_lesson() -> None:
        db = SessionLocal()
        try:
            lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
            if lesson:
                lesson.task_status = "completed"
                lesson.completed_at = datetime.now(timezone.utc)
                db.commit()
        finally:
            db.close()

    qdrant_task = asyncio.create_task(_run_qdrant_ingest(raw_json_path, final_lesson_id, school_id))
    finish_task = asyncio.create_task(asyncio.to_thread(_finish_lesson))
    ok, qdrant_log = await qdrant_task
    await finish_task
    if not ok:
        def _mark_failed() -> None:
            db = SessionLocal()
            try:
                lesson = db.query(Lesson).filter(Lesson.lesson_id == final_lesson_id).first()
                if lesson:
                    lesson.task_status = "failed"
                    db.commit()
            finally:
                db.close()

        await asyncio.to_thread(_mark_failed)
    qdrant_event = {"type": "status", "step": "qdrant", "ok": ok, "log": qdrant_log[-2000:]}
    logger.info(f"[full_pipeline] qdrant ok={ok}")
    yield qdrant_event
    elapsed_s = (datetime.now(timezone.utc) - start).total_seconds()
    done_event = {"type": "done", "step": "end", "lesson_id": final_lesson_id, "elapsed_seconds": round(elapsed_s, 3)}
    logger.info(f"[full_pipeline] done lesson_id={final_lesson_id} elapsed_seconds={done_event['elapsed_seconds']}")
    yield done_event
