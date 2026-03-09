import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path
from backend.app.core.config import settings

def setup_logging():
    """
    配置应用程序日志系统
    符合行业标准：文件轮转、分级日志、结构化格式
    """
    # 创建日志目录
    log_dir = settings.LOG_DIR
    log_dir.mkdir(exist_ok=True)
    
    # 配置根日志器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG if settings.DEBUG else logging.INFO)
    
    # 清除现有处理器
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # 文件处理器 - 按大小轮转 (10MB)
    file_handler = RotatingFileHandler(
        filename=log_dir / "app.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.INFO)
    
    # 错误文件处理器 - 专门记录ERROR及以上级别
    error_handler = RotatingFileHandler(
        filename=log_dir / "error.log", 
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # 格式化器 - 结构化日志格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s [%(filename)s:%(lineno)d]'
    )
    
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # 控制台输出（开发环境）
    if settings.DEBUG:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # 记录日志系统初始化完成
    logger.info("Logging system initialized successfully")
    logger.info(f"Log directory: {log_dir.absolute()}")
    logger.info(f"Log level: {'DEBUG' if settings.DEBUG else 'INFO'}")

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志器
    
    Args:
        name: 日志器名称，通常使用 __name__
    
    Returns:
        logging.Logger: 配置好的日志器实例
    """
    return logging.getLogger(name)