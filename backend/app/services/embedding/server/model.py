import os
import sys
import torch
import logging
from typing import List, Dict, Any
import transformers.utils.import_utils

logging.basicConfig(level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger(__name__)

if not hasattr(transformers.utils.import_utils, 'is_torch_fx_available'):
    transformers.utils.import_utils.is_torch_fx_available = lambda: False

from FlagEmbedding import BGEM3FlagModel
import numpy as np


class ModelHandler:
    def __init__(self, model_name: str = "BAAI/bge-m3", device: str = None, use_fp16: bool = None):
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device

        if use_fp16 is None:
            self.use_fp16 = self.device == "cuda"
        else:
            self.use_fp16 = use_fp16

        logger.info(f"Loading model {model_name} to {self.device} (fp16={self.use_fp16})...")

        self.model_name = model_name
        self.model = BGEM3FlagModel(
            model_name,
            use_fp16=self.use_fp16,
            device=self.device
        )
        logger.info("Model loaded successfully")

    def encode(self, texts: List[str], batch_size: int = 12, max_length: int = 8192) -> Dict[str, Any]:
        try:
            output = self.model.encode(
                texts,
                batch_size=batch_size,
                max_length=max_length,
                return_dense=True,
                return_sparse=True,
                return_colbert_vecs=False
            )

            dense_vecs = output['dense_vecs']
            lexical_weights = output['lexical_weights']

            if isinstance(dense_vecs, np.ndarray):
                dense_vecs = dense_vecs.tolist()

            return {
                "dense": dense_vecs,
                "sparse": lexical_weights
            }

        except Exception as e:
            import traceback
            logger.error(f"Model inference error: {str(e)}")
            logger.error(traceback.format_exc())
            raise e

    def get_device_info(self) -> Dict[str, Any]:
        info = {
            "device": self.device,
            "model_name": self.model_name,
            "use_fp16": self.use_fp16
        }
        if self.device == "cuda":
            try:
                info["gpu_name"] = torch.cuda.get_device_name(0)
                info["gpu_memory_allocated"] = f"{torch.cuda.memory_allocated(0) / 1024**3:.2f} GB"
                info["gpu_memory_reserved"] = f"{torch.cuda.memory_reserved(0) / 1024**3:.2f} GB"
            except Exception:
                pass
        return info
