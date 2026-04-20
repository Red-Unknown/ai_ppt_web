
from datetime import datetime, timezone
from pathlib import Path
import os

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from backend.app.schemas.parser import ParseRequest, ParseResponse, ParseData
from backend.app.services.parser.lesson_parser import parser_service
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

UPLOAD_DIR = Path("uploads") / "lesson_files"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
ALLOWED_UPLOAD_EXTS = {".ppt", ".pptx", ".pdf"}
MAX_UPLOAD_SIZE = 100 * 1024 * 1024  # 100MB


@router.post("/lesson/upload")
async def upload_lesson_file(
    file: UploadFile = File(..., description="课件文件，支持 ppt/pptx/pdf"),
    course_id: str = Form(default="", description="可选：课程ID"),
    school_id: str = Form(default="", description="可选：学校ID"),
):
    """Upload lesson file and return parse-ready file metadata."""
    filename = file.filename or ""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_UPLOAD_EXTS:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}. Allowed: {sorted(ALLOWED_UPLOAD_EXTS)}")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(status_code=400, detail=f"File too large. Max: {MAX_UPLOAD_SIZE // (1024 * 1024)}MB")

    file_id = uuid.uuid4().hex
    safe_name = f"{file_id}{ext}"
    save_path = UPLOAD_DIR / safe_name
    save_path.write_bytes(content)

    file_type = "pdf" if ext == ".pdf" else ("pptx" if ext == ".pptx" else "ppt")
    return {
        "code": 200,
        "msg": "Upload successful",
        "data": {
            "fileId": file_id,
            "fileName": filename,
            "fileType": file_type,
            "fileSize": len(content),
            "fileUrl": str(save_path).replace("\\", "/"),
            "courseId": course_id or None,
            "schoolId": school_id or None,
            "uploadedAt": datetime.now(timezone.utc).isoformat(),
        },
    }

@router.post("/lesson/parse", response_model=ParseResponse)
async def parse_lesson(request: ParseRequest):
    """
    Role A: Courseware Parser Interface
    Receives PPT/PDF, parses structure.
    """
    request_id = f"req{uuid.uuid4().hex[:12]}"
    
    try:
        # Validate signature (mock for now)
        if not request.enc:
            raise HTTPException(status_code=403, detail="Signature verification failed")

        # Call service to parse
        # Note: In production, this should be an async task (Celery). 
        # For this demo/MVP, we run it synchronously (or in threadpool via FastAPI default).
        
        # Since parser_service methods are sync, FastAPI runs them in a threadpool, which is non-blocking for the event loop.
        result = parser_service.parse_courseware(request.fileUrl, request.fileType)
        
        parse_id = f"parse{uuid.uuid4().hex[:12]}"
        
        data = ParseData(
            parseId=parse_id,
            fileInfo=result["fileInfo"],
            structurePreview=result["structurePreview"],
            taskStatus="completed"
        )
        
        return ParseResponse(
            code=200,
            msg="Courseware parsing successful",
            data=data,
            requestId=request_id
        )

    except Exception as e:
        logger.error(f"Parsing error: {str(e)}")
        return ParseResponse(
            code=500,
            msg=f"Server Error: {str(e)}",
            data=None,
            requestId=request_id
        )
