from fastapi import APIRouter, HTTPException
from typing import Optional
import uuid
import logging

from backend.app.schemas.qa import RetrieveRequest, RetrieveResponse, RetrieveResponseData, BboxItem, SourceItem
from backend.app.services.qa.retrieval.two_layer_retriever import TwoLayerRetriever

router = APIRouter(prefix="/qa", tags=["问答检索"])
logger = logging.getLogger(__name__)


@router.post("/retrieve", response_model=RetrieveResponse)
async def retrieve_answer(request: RetrieveRequest):
    request_id = str(uuid.uuid4())

    if not request.query:
        return RetrieveResponse(
            code=400,
            message="缺少必填参数: query",
            data=None,
            request_id=request_id
        )

    if not request.lesson_id:
        return RetrieveResponse(
            code=400,
            message="缺少必填参数: lesson_id",
            data=None,
            request_id=request_id
        )

    try:
        retriever = TwoLayerRetriever()
        result = await retriever.retrieve(
            query=request.query,
            lesson_id=request.lesson_id,
            top_k=request.top_k
        )

        if not result.get("cir_results"):
            return RetrieveResponse(
                code=200,
                message="success",
                data=RetrieveResponseData(
                    answer="未找到相关内容",
                    bbox_list=[],
                    context={"matched_chapters": [], "source_pages": []},
                    sources=[]
                ),
                request_id=request_id
            )

        bbox_list = []
        for bbox in result.get("bbox_list", []):
            bbox_list.append(BboxItem(
                page_num=bbox.get("page_num", 0),
                bboxes=bbox.get("bboxes", []),
                merged_bbox=bbox.get("merged_bbox", []),
                is_merged=bbox.get("is_merged", False),
                total_area_ratio=bbox.get("total_area_ratio", 0)
            ))

        sources = []
        for src in result.get("sources", []):
            sources.append(SourceItem(
                node_id=src.get("node_id", ""),
                content=src.get("content", ""),
                path=src.get("path", ""),
                relevance_score=src.get("relevance_score", 0),
                page_num=src.get("page_num"),
                bbox=src.get("bbox"),
                image_url=src.get("image_url")
            ))

        return RetrieveResponse(
            code=200,
            message="success",
            data=RetrieveResponseData(
                answer=result.get("answer", ""),
                bbox_list=bbox_list,
                context=result.get("context", {}),
                sources=sources
            ),
            request_id=request_id
        )

    except Exception as e:
        logger.error(f"检索失败: {e}")
        return RetrieveResponse(
            code=500,
            message=f"检索失败: {str(e)}",
            data=None,
            request_id=request_id
        )
