
from fastapi import APIRouter, HTTPException, Depends
from backend.app.schemas.parser import ParseRequest, ParseResponse, ParseData
from backend.app.services.parser.lesson_parser import parser_service
import uuid
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

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
