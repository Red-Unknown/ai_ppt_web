import asyncio
import time
import logging
import sys
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn
from starlette.middleware.cors import CORSMiddleware

from server.model import ModelHandler
from config.settings import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stdout
)
logger = logging.getLogger("EmbeddingService")
logger.info("Embedding Service starting...")


class EmbeddingRequest(BaseModel):
    data: List[str] = Field(..., description="List of texts to embed")
    bDense: bool = Field(True, description="Return dense vectors")
    bSparse: bool = Field(True, description="Return sparse vectors")


class EmbeddingResponse(BaseModel):
    success: bool
    data: Optional[List[List[float]]] = None
    data_sparse: Optional[List[Dict[str, float]]] = None
    message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None


class QueueItem:
    def __init__(self, text: str, future: asyncio.Future):
        self.text = text
        self.future = future


model_handler: Optional[ModelHandler] = None
request_queue: asyncio.Queue = asyncio.Queue()
processing_task: Optional[asyncio.Task] = None


async def batch_processing_loop():
    logger.info("Starting batch processing loop...")
    while True:
        batch_items: List[QueueItem] = []

        try:
            item = await request_queue.get()
            batch_items.append(item)
        except asyncio.CancelledError:
            break

        start_time = time.time()
        while len(batch_items) < settings.MAX_BATCH_SIZE:
            elapsed = time.time() - start_time
            remaining = settings.BATCH_TIMEOUT - elapsed

            if remaining <= 0:
                break

            try:
                item = await asyncio.wait_for(request_queue.get(), timeout=remaining)
                batch_items.append(item)
            except asyncio.TimeoutError:
                break
            except asyncio.CancelledError:
                break
            except Exception:
                break

        if not batch_items:
            continue

        try:
            texts = [item.text for item in batch_items]

            loop = asyncio.get_running_loop()
            results = await loop.run_in_executor(
                None,
                lambda: model_handler.encode(texts, batch_size=len(texts), max_length=settings.MAX_LENGTH)
            )

            dense_vecs = results.get("dense", [])
            sparse_vecs = results.get("sparse", [])

            for i, item in enumerate(batch_items):
                if not item.future.done():
                    item.future.set_result({
                        "dense": dense_vecs[i] if dense_vecs else None,
                        "sparse": sparse_vecs[i] if sparse_vecs else None
                    })

        except Exception as e:
            logger.error(f"Batch processing failed: {str(e)}")
            for item in batch_items:
                if not item.future.done():
                    item.future.set_exception(e)
        finally:
            for _ in batch_items:
                request_queue.task_done()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model_handler, processing_task

    logger.info("=" * 50)
    logger.info("Starting Embedding Service...")
    logger.info(f"Model: {settings.MODEL_NAME}")
    logger.info(f"Device: {settings.DEVICE or 'auto'}")
    logger.info(f"Max batch size: {settings.MAX_BATCH_SIZE}")
    logger.info("=" * 50)
    
    logger.info("Loading model, please wait...")
    try:
        model_kwargs = settings.get_model_kwargs()
        model_handler = ModelHandler(**model_kwargs)
        logger.info(f"Model loaded successfully: {settings.MODEL_NAME}")
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        raise

    logger.info("Starting batch processing task...")
    loop = asyncio.get_event_loop()
    processing_task = loop.create_task(batch_processing_loop())
    logger.info("Batch processing task started")
    
    logger.info("Embedding Service is ready!")
    logger.info("=" * 50)

    yield

    logger.info("Shutting down...")
    if processing_task:
        processing_task.cancel()
        try:
            await processing_task
        except asyncio.CancelledError:
            pass
    logger.info("Shutdown complete")


app = FastAPI(
    title="Embedding Service",
    description="BGE-M3 Embedding Service with batch processing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error", "detail": str(exc)}
    )


@app.get("/health", tags=["Health"])
async def health_check():
    if model_handler is None:
        raise HTTPException(status_code=503, detail="Model not initialized")
    return {
        "status": "healthy",
        "model": settings.MODEL_NAME,
        "device_info": model_handler.get_device_info()
    }


@app.get("/", tags=["Health"])
async def root():
    return {"service": "Embedding Service", "version": "1.0.0", "status": "running"}


@app.post("/embedding", response_model=EmbeddingResponse, tags=["Embedding"])
async def embedding_endpoint(request: EmbeddingRequest):
    if not request.data:
        return EmbeddingResponse(success=False, message="Input text list is empty")

    start_time = time.time()
    futures = []

    for text in request.data:
        future = asyncio.get_running_loop().create_future()
        await request_queue.put(QueueItem(text, future))
        futures.append(future)

    try:
        results = await asyncio.gather(*futures)

        dense_list = []
        sparse_list = []

        for res in results:
            if request.bDense:
                dense_list.append(res["dense"])
            if request.bSparse:
                sparse_list.append(res["sparse"])

        process_time = (time.time() - start_time) * 1000

        return EmbeddingResponse(
            success=True,
            data=dense_list if request.bDense else None,
            data_sparse=sparse_list if request.bSparse else None,
            meta={"process_time_ms": process_time, "batch_size": len(request.data)}
        )

    except Exception as e:
        logger.error(f"Request processing failed: {str(e)}")
        return EmbeddingResponse(success=False, message=str(e))


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level=settings.LOG_LEVEL.lower()
    )
