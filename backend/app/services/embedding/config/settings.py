import os
from typing import Optional
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


class Settings:
    def __init__(self):
        self.HOST = os.getenv("EMBEDDING_HOST", "localhost")
        self.PORT = int(os.getenv("EMBEDDING_PORT", "8000"))

        local_model_path = os.getenv("EMBEDDING_LOCAL_MODEL_PATH", "F:\\develop\\hub\\models--BAAI--bge-m3\\snapshots\\5617a9f61b028005a4858fdac845db406aefb181")
        self.MODEL_NAME = local_model_path if os.path.exists(local_model_path) else os.getenv("EMBEDDING_MODEL_NAME", "BAAI/bge-m3")
        self.DEVICE = os.getenv("EMBEDDING_DEVICE", None)
        self.USE_FP16 = os.getenv("EMBEDDING_USE_FP16", None)

        if self.USE_FP16 is not None:
            self.USE_FP16 = self.USE_FP16.lower() in ("true", "1", "yes")

        self.MAX_BATCH_SIZE = int(os.getenv("EMBEDDING_MAX_BATCH_SIZE", "32"))
        self.BATCH_TIMEOUT = float(os.getenv("EMBEDDING_BATCH_TIMEOUT", "0.05"))
        self.MAX_LENGTH = int(os.getenv("EMBEDDING_MAX_LENGTH", "8192"))

        self.LOG_LEVEL = os.getenv("EMBEDDING_LOG_LEVEL", "INFO")

        self.ALLOW_ORIGINS = os.getenv("EMBEDDING_ALLOW_ORIGINS", "*").split(",")
        self.ALLOW_CREDENTIALS = os.getenv("EMBEDDING_ALLOW_CREDENTIALS", "true").lower() in ("true", "1", "yes")

        self.reload_logging()

    def reload_logging(self):
        logging.getLogger().setLevel(getattr(logging, self.LOG_LEVEL.upper(), logging.INFO))

    def get_model_kwargs(self) -> dict:
        kwargs = {"model_name": self.MODEL_NAME}
        if self.DEVICE:
            kwargs["device"] = self.DEVICE
        if self.USE_FP16 is not None:
            kwargs["use_fp16"] = self.USE_FP16
        return kwargs


settings = Settings()
