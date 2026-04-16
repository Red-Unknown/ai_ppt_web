import logging
import time
import json
from typing import List, Dict, Any, Optional
from pathlib import Path

from .index_store import memory_index_store, IndexedDocument
from .data_loader import load_cir_data, load_raw_json_data, extract_text_blocks, text_blocks_to_dict

logger = logging.getLogger("IndexBuilder")


class IndexBuilder:
    def __init__(self, embedding_endpoint: str = "http://localhost:8000/embedding"):
        self.embedding_endpoint = embedding_endpoint
        logger.info(f"IndexBuilder initialized with endpoint: {embedding_endpoint}")

    async def build_index_for_lesson(self, lesson_id: str) -> Dict[str, Any]:
        start_time = time.time()
        logger.info(f"=" * 60)
        logger.info(f"[INDEX_BUILDER] Starting index build for lesson_id={lesson_id}")
        logger.info(f"=" * 60)

        results = {
            "lesson_id": lesson_id,
            "cir_indexed": 0,
            "raw_indexed": 0,
            "errors": []
        }

        cir_start = time.time()
        cir_result = await self._build_cir_index(lesson_id)
        results["cir_indexed"] = cir_result["indexed_count"]
        results["cir_time_ms"] = (time.time() - cir_start) * 1000

        if cir_result["errors"]:
            results["errors"].extend(cir_result["errors"])

        raw_start = time.time()
        raw_result = await self._build_raw_index(lesson_id)
        results["raw_indexed"] = raw_result["indexed_count"]
        results["raw_time_ms"] = (time.time() - raw_start) * 1000

        if raw_result["errors"]:
            results["errors"].extend(raw_result["errors"])

        results["total_time_ms"] = (time.time() - start_time) * 1000

        logger.info(f"=" * 60)
        logger.info(f"[INDEX_BUILDER] Index build completed for lesson_id={lesson_id}")
        logger.info(f"[INDEX_BUILDER] CIR indexed: {results['cir_indexed']}, time: {results['cir_time_ms']:.2f}ms")
        logger.info(f"[INDEX_BUILDER] RAW indexed: {results['raw_indexed']}, time: {results['raw_time_ms']:.2f}ms")
        logger.info(f"[INDEX_BUILDER] Total time: {results['total_time_ms']:.2f}ms")
        logger.info(f"=" * 60)

        return results

    async def _build_cir_index(self, lesson_id: str) -> Dict[str, Any]:
        logger.debug(f"[INDEX_BUILDER] Loading CIR data for lesson_id={lesson_id}")
        cir_data = load_cir_data(lesson_id)

        if not cir_data:
            logger.warning(f"[INDEX_BUILDER] No CIR data found for lesson_id={lesson_id}")
            return {"indexed_count": 0, "errors": ["No CIR data found"]}

        logger.info(f"[INDEX_BUILDER] Loaded {len(cir_data)} CIR documents")

        documents_to_index = []
        for doc in cir_data:
            key_points_text = " ".join(doc.get("key_points", []))
            teaching_content = doc.get("teaching_content", "")
            combined_text = f"{key_points_text} {teaching_content}"

            documents_to_index.append(IndexedDocument(
                doc_id=doc.get("node_id", ""),
                content=combined_text,
                metadata={
                    "node_id": doc.get("node_id"),
                    "node_name": doc.get("node_name"),
                    "node_type": doc.get("node_type"),
                    "page_num": doc.get("page_num"),
                    "path": doc.get("path"),
                    "lesson_id": lesson_id
                }
            ))

        logger.debug(f"[INDEX_BUILDER] Preparing to embed {len(documents_to_index)} CIR documents")

        embed_start = time.time()
        embedded_docs = await self._embed_documents(documents_to_index)
        embed_time = (time.time() - embed_start) * 1000
        logger.info(f"[INDEX_BUILDER] CIR embedding completed in {embed_time:.2f}ms")

        success = memory_index_store.add_cir_documents(lesson_id, embedded_docs)

        return {
            "indexed_count": len(embedded_docs) if success else 0,
            "errors": [] if success else ["Failed to store CIR index"]
        }

    async def _build_raw_index(self, lesson_id: str) -> Dict[str, Any]:
        logger.debug(f"[INDEX_BUILDER] Loading Raw JSON data for lesson_id={lesson_id}")
        raw_data = load_raw_json_data(lesson_id)

        if not raw_data:
            logger.warning(f"[INDEX_BUILDER] No Raw JSON data found for lesson_id={lesson_id}")
            return {"indexed_count": 0, "errors": ["No Raw JSON data found"]}

        structure = raw_data.get("data", {}).get("structurePreview", {})
        chapters = structure.get("chapters", [])

        all_page_nums = set()
        for chapter in chapters:
            for sub_chapter in chapter.get("subChapters", []):
                page_range_str = sub_chapter.get("pageRange", "")
                page_nums = self._parse_page_range(page_range_str)
                all_page_nums.update(page_nums)

        page_range = sorted(list(all_page_nums))
        logger.info(f"[INDEX_BUILDER] Found {len(page_range)} pages to index: {page_range[:10]}...")

        text_blocks = extract_text_blocks(raw_data, page_range)
        logger.debug(f"[INDEX_BUILDER] Extracted {len(text_blocks)} text blocks")

        if not text_blocks:
            logger.warning(f"[INDEX_BUILDER] No text blocks extracted for lesson_id={lesson_id}")
            return {"indexed_count": 0, "errors": ["No text blocks extracted"]}

        documents_to_index = []
        for block in text_blocks:
            documents_to_index.append(IndexedDocument(
                doc_id=block.id,
                content=block.content,
                metadata={
                    "page_num": block.page_num,
                    "element_type": block.element_type,
                    "lesson_id": lesson_id
                },
                dense_vector=None,
                sparse_vector=None
            ))

        logger.debug(f"[INDEX_BUILDER] Preparing to embed {len(documents_to_index)} RAW documents")

        embed_start = time.time()
        embedded_docs = await self._embed_documents(documents_to_index)
        embed_time = (time.time() - embed_start) * 1000
        logger.info(f"[INDEX_BUILDER] RAW embedding completed in {embed_time:.2f}ms")

        success = memory_index_store.add_raw_documents(lesson_id, embedded_docs)

        return {
            "indexed_count": len(embedded_docs) if success else 0,
            "errors": [] if success else ["Failed to store RAW index"]
        }

    async def _embed_documents(self, documents: List[IndexedDocument]) -> List[IndexedDocument]:
        if not documents:
            return []

        texts = [doc.content for doc in documents]

        logger.debug(f"[EMBEDDING] Calling embedding service with {len(texts)} texts")
        logger.debug(f"[EMBEDDING] First text preview: {texts[0][:100] if texts else 'N/A'}...")

        embed_request_start = time.time()

        try:
            import httpx
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    self.embedding_endpoint,
                    json={
                        "data": texts,
                        "bDense": True,
                        "bSparse": True
                    }
                )

                embed_request_time = (time.time() - embed_request_start) * 1000
                logger.info(f"[EMBEDDING] Request completed in {embed_request_time:.2f}ms, status={response.status_code}")

                if response.status_code != 200:
                    error_msg = f"Embedding service returned {response.status_code}: {response.text}"
                    logger.error(f"[EMBEDDING] {error_msg}")
                    raise Exception(error_msg)

                result = response.json()

                if not result.get("success"):
                    error_msg = result.get("message", "Unknown error")
                    logger.error(f"[EMBEDDING] Embedding failed: {error_msg}")
                    raise Exception(error_msg)

                process_time = result.get("meta", {}).get("process_time_ms", 0)
                logger.debug(f"[EMBEDDING] Internal processing time: {process_time}ms")

                dense_vectors = result.get("data", [])
                sparse_vectors = result.get("data_sparse", [])

                logger.debug(f"[EMBEDDING] Received {len(dense_vectors)} dense vectors, {len(sparse_vectors)} sparse vectors")

                for i, doc in enumerate(documents):
                    if i < len(dense_vectors):
                        doc.dense_vector = dense_vectors[i]
                    if i < len(sparse_vectors):
                        doc.sparse_vector = sparse_vectors[i]

                return documents

        except httpx.ConnectError as e:
            logger.error(f"[EMBEDDING] Failed to connect to embedding service: {e}")
            raise Exception(f"Cannot connect to embedding service at {self.embedding_endpoint}")
        except Exception as e:
            logger.error(f"[EMBEDDING] Error during embedding: {e}")
            raise

    def _parse_page_range(self, page_range_str: str) -> List[int]:
        if not page_range_str:
            return []

        page_nums = []
        parts = page_range_str.split(",")

        for part in parts:
            part = part.strip()
            if "-" in part:
                try:
                    start, end = part.split("-")
                    page_nums.extend(range(int(start), int(end) + 1))
                except ValueError:
                    continue
            else:
                try:
                    page_nums.append(int(part))
                except ValueError:
                    continue

        return page_nums

    def get_index_stats(self, lesson_id: str) -> Dict[str, Any]:
        stats = memory_index_store.get_stats()
        metadata = memory_index_store.get_metadata(lesson_id)

        result = {
            "lesson_id": lesson_id,
            "global_stats": stats,
            "metadata": {
                k: {
                    "document_count": v.document_count,
                    "created_at": v.created_at,
                    "index_type": v.index_type
                }
                for k, v in metadata.items()
            }
        }

        logger.debug(f"[INDEX_BUILDER] Stats for lesson_id={lesson_id}: {result}")
        return result


index_builder = IndexBuilder()
