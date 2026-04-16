import logging
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("IndexBuilder")


@dataclass
class IndexMetadata:
    lesson_id: str
    index_type: str
    document_count: int
    created_at: str
    embedding_dim: Optional[int] = None


@dataclass
class IndexedDocument:
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    dense_vector: Optional[List[float]] = None
    sparse_vector: Optional[Dict[str, float]] = None


class MemoryIndexStore:
    def __init__(self):
        self._cir_index: Dict[str, List[IndexedDocument]] = {}
        self._raw_index: Dict[str, List[IndexedDocument]] = {}
        self._metadata: Dict[str, IndexMetadata] = {}
        logger.info("MemoryIndexStore initialized")

    def add_cir_documents(self, lesson_id: str, documents: List[IndexedDocument]) -> bool:
        start_time = time.time()
        logger.debug(f"[CIR] Adding {len(documents)} documents for lesson_id={lesson_id}")

        if lesson_id not in self._cir_index:
            self._cir_index[lesson_id] = []
            logger.debug(f"[CIR] Created new index for lesson_id={lesson_id}")

        self._cir_index[lesson_id].extend(documents)

        self._metadata[f"cir_{lesson_id}"] = IndexMetadata(
            lesson_id=lesson_id,
            index_type="cir",
            document_count=len(self._cir_index[lesson_id]),
            created_at=datetime.now().isoformat()
        )

        elapsed = (time.time() - start_time) * 1000
        logger.info(f"[CIR] Indexed {len(documents)} documents for lesson_id={lesson_id} in {elapsed:.2f}ms")
        logger.debug(f"[CIR] Total documents in index: {len(self._cir_index[lesson_id])}")
        return True

    def add_raw_documents(self, lesson_id: str, documents: List[IndexedDocument]) -> bool:
        start_time = time.time()
        logger.debug(f"[RAW] Adding {len(documents)} documents for lesson_id={lesson_id}")

        if lesson_id not in self._raw_index:
            self._raw_index[lesson_id] = []
            logger.debug(f"[RAW] Created new index for lesson_id={lesson_id}")

        self._raw_index[lesson_id].extend(documents)

        self._metadata[f"raw_{lesson_id}"] = IndexMetadata(
            lesson_id=lesson_id,
            index_type="raw",
            document_count=len(self._raw_index[lesson_id]),
            created_at=datetime.now().isoformat()
        )

        elapsed = (time.time() - start_time) * 1000
        logger.info(f"[RAW] Indexed {len(documents)} documents for lesson_id={lesson_id} in {elapsed:.2f}ms")
        logger.debug(f"[RAW] Total documents in index: {len(self._raw_index[lesson_id])}")
        return True

    def get_cir_documents(self, lesson_id: str) -> List[IndexedDocument]:
        docs = self._cir_index.get(lesson_id, [])
        logger.debug(f"[CIR] Retrieved {len(docs)} documents for lesson_id={lesson_id}")
        return docs

    def get_raw_documents(self, lesson_id: str) -> List[IndexedDocument]:
        docs = self._raw_index.get(lesson_id, [])
        logger.debug(f"[RAW] Retrieved {len(docs)} documents for lesson_id={lesson_id}")
        return docs

    def get_metadata(self, lesson_id: str) -> Dict[str, IndexMetadata]:
        result = {}
        cir_key = f"cir_{lesson_id}"
        raw_key = f"raw_{lesson_id}"

        if cir_key in self._metadata:
            result["cir"] = self._metadata[cir_key]
        if raw_key in self._metadata:
            result["raw"] = self._metadata[raw_key]

        logger.debug(f"[METADATA] Retrieved metadata for lesson_id={lesson_id}: {list(result.keys())}")
        return result

    def get_all_lesson_ids(self) -> List[str]:
        cir_ids = set(self._cir_index.keys())
        raw_ids = set(self._raw_index.keys())
        all_ids = list(cir_ids | raw_ids)
        logger.debug(f"[INDEX] Total lessons indexed: {len(all_ids)}")
        return all_ids

    def clear_lesson(self, lesson_id: str) -> bool:
        cir_removed = 0
        raw_removed = 0

        if lesson_id in self._cir_index:
            cir_removed = len(self._cir_index[lesson_id])
            del self._cir_index[lesson_id]
            logger.info(f"[CIR] Cleared index for lesson_id={lesson_id}, removed {cir_removed} documents")

        if lesson_id in self._raw_index:
            raw_removed = len(self._raw_index[lesson_id])
            del self._raw_index[lesson_id]
            logger.info(f"[RAW] Cleared index for lesson_id={lesson_id}, removed {raw_removed} documents")

        cir_key = f"cir_{lesson_id}"
        raw_key = f"raw_{lesson_id}"
        if cir_key in self._metadata:
            del self._metadata[cir_key]
        if raw_key in self._metadata:
            del self._metadata[raw_key]

        return cir_removed > 0 or raw_removed > 0

    def get_stats(self) -> Dict[str, Any]:
        stats = {
            "total_lessons": len(set(self._cir_index.keys()) | set(self._raw_index.keys())),
            "cir_documents": sum(len(docs) for docs in self._cir_index.values()),
            "raw_documents": sum(len(docs) for docs in self._raw_index.values()),
            "indexes": {}
        }

        for lesson_id in set(self._cir_index.keys()) | set(self._raw_index.keys()):
            stats["indexes"][lesson_id] = {
                "cir_count": len(self._cir_index.get(lesson_id, [])),
                "raw_count": len(self._raw_index.get(lesson_id, []))
            }

        logger.debug(f"[STATS] Index stats: {stats}")
        return stats


memory_index_store = MemoryIndexStore()
