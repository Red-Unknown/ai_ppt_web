from typing import List, Dict, Optional, Any
import asyncio
from .hybrid_engine import HybridSearchEngine
from .data_loader import load_cir_data, CIRSection, TextBlock
from .bbox_utils import (
    TextBlockWithBbox,
    Bbox,
    merge_bboxes_by_page,
    format_bbox_for_response,
    MergedBboxResult
)


class TwoLayerRetriever:
    def __init__(self):
        self.hybrid_engine = HybridSearchEngine()

    async def retrieve(
        self,
        query: str,
        lesson_id: str,
        top_k: int = 5
    ) -> Dict[str, Any]:
        cir_results = await self._retrieve_cir(query, lesson_id, top_k)

        if not cir_results:
            return {
                "cir_results": [],
                "raw_results": [],
                "answer": "",
                "bbox_list": [],
                "context": {
                    "matched_chapters": [],
                    "source_pages": []
                },
                "sources": []
            }

        aggregated = await self._aggregate_results(query, cir_results)

        return aggregated

    async def _retrieve_cir(
        self,
        query: str,
        lesson_id: str,
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        cir_data = load_cir_data(lesson_id)

        if not cir_data:
            return []

        results = self.hybrid_engine.search(
            query=query,
            documents=cir_data,
            search_fields=["key_points", "teaching_content"],
            top_k=top_k,
            alpha=0.5,
            beta=0.3,
            gamma=0.2
        )

        return [
            {
                "node_id": r.get("node_id"),
                "node_name": r.get("node_name"),
                "page_num": r.get("page_num"),
                "key_points": r.get("key_points", []),
                "teaching_content": r.get("teaching_content", ""),
                "path": r.get("path"),
                "bbox": r.get("bbox"),
                "image_url": r.get("image_url"),
                "score": r.get("score", 0)
            }
            for r in results
        ]

    async def _aggregate_results(
        self,
        query: str,
        cir_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        answer = await self._extract_answer(query, cir_results)

        blocks_with_bbox = []
        for r in cir_results:
            if r.get("bbox"):
                bbox_obj = Bbox.from_dict(r["bbox"])
                if bbox_obj:
                    blocks_with_bbox.append(TextBlockWithBbox(
                        content=r.get("teaching_content", ""),
                        bbox=bbox_obj,
                        page_num=r.get("page_num", 0),
                        element_type="text"
                    ))

        merged_bboxes = merge_bboxes_by_page(blocks_with_bbox)
        bbox_list = format_bbox_for_response(merged_bboxes)

        context = {
            "matched_chapters": [cir.get("node_name", "") for cir in cir_results],
            "source_pages": list(set(r.get("page_num") for r in cir_results if r.get("page_num")))
        }

        sources = [
            {
                "node_id": r.get("node_id"),
                "content": r.get("teaching_content", "")[:200] + "..." if len(r.get("teaching_content", "")) > 200 else r.get("teaching_content", ""),
                "path": r.get("path", ""),
                "relevance_score": r.get("score", 0),
                "page_num": r.get("page_num"),
                "bbox": r.get("bbox"),
                "image_url": r.get("image_url") or (f"https://cdn.example.com/slides/course_101/slide_{r.get('page_num', 1):02d}.jpg" if r.get("page_num") else None)
            }
            for r in cir_results
        ]

        return {
            "cir_results": cir_results,
            "raw_results": cir_results,
            "answer": answer,
            "bbox_list": bbox_list,
            "context": context,
            "sources": sources
        }

    async def _extract_answer(self, query: str, cir_results: List[Dict[str, Any]]) -> str:
        if not cir_results:
            return ""

        contexts = [r.get("teaching_content", "") for r in cir_results[:3] if r.get("teaching_content")]

        if not contexts:
            return ""

        combined = "\n\n".join(contexts)

        answer_prompt = f"""基于以下上下文，回答用户问题。

用户问题：{query}

上下文：
{combined}

请从上下文中提取最相关的答案片段，直接给出答案，不需要额外说明。"""

        return await self._generate_answer(answer_prompt)

    async def _generate_answer(self, prompt: str) -> str:
        try:
            from backend.app.core.config import settings
            from openai import AsyncOpenAI
            import json

            if not settings.DEEPSEEK_API_KEY:
                return self._fallback_answer(prompt)

            client = AsyncOpenAI(
                api_key=settings.DEEPSEEK_API_KEY,
                base_url=settings.DEEPSEEK_BASE_URL or "https://api.deepseek.com"
            )

            response = await client.chat.completions.create(
                model=settings.DEEPSEEK_MODEL or "deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的课程助手，负责从教材中提取答案。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )

            return response.choices[0].message.content.strip()

        except Exception as e:
            print(f"LLM call failed: {e}")
            return self._fallback_answer(prompt)

    def _fallback_answer(self, prompt: str) -> str:
        lines = prompt.split("\n")
        contexts = []
        capture = False
        for line in lines:
            if "上下文：" in line:
                capture = True
                continue
            if "请从上下文中" in line:
                capture = False
            if capture and line.strip():
                contexts.append(line.strip())

        if contexts:
            return "\n\n".join(contexts[:2])
        return "根据检索结果，未找到合适的答案。"
