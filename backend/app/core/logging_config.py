import logging
import sys
from pathlib import Path
from loguru import logger
from backend.app.core.config import settings

class InterceptHandler(logging.Handler):
    """
    拦截标准 logging 消息并转发到 Loguru
    """
    def emit(self, record):
        # 获取对应的 Loguru 日志级别
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # 查找调用堆栈，确保日志源准确
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # 转发到 Loguru，绑定 record.name 为 name 字段
        logger.opt(depth=depth, exception=record.exc_info).bind(name=record.name).log(
            level, record.getMessage()
        )

def setup_logging():
    """
    配置应用程序日志系统 - 使用 Loguru 替换标准 logging
    解决 Windows 下多进程日志轮转问题，提供更强大的日志管理功能
    """
    # 创建日志目录
    log_dir = settings.LOG_DIR
    log_dir.mkdir(parents=True, exist_ok=True)

    # 1. 重置 Loguru 配置
    logger.remove() 
    
    # 2. 配置 Loguru 输出
    
    # 控制台输出 (开发环境详细，生产环境简洁)
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )
    
    logger.add(
        sys.stderr,
        level="DEBUG" if settings.DEBUG else "INFO",
        format=console_format,
        enqueue=True  # 异步写入
    )

    # 文件输出 - 主日志 (自动轮转)
    # rotation="10 MB": 文件达到 10MB 时轮转
    # retention=5: 保留 5 个历史文件
    # compression="zip": 压缩历史日志
    # enqueue=True: 进程安全，解决 Windows 文件占用问题
    logger.add(
        log_dir / "app.log",
        rotation="10 MB",
        retention=5,
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )
    
    # 文件输出 - 错误日志 (单独记录)
    logger.add(
        log_dir / "error.log",
        rotation="5 MB",
        retention=3,
        compression="zip",
        enqueue=True,
        encoding="utf-8",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # 3. 配置标准 logging 拦截
    # 将 logging 的根处理器替换为 InterceptHandler
    logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)
    
    # 拦截 uvicorn 和 fastapi 的日志
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "fastapi"):
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = [InterceptHandler()]
        logging_logger.propagate = False

    logger.info(f"Logging system initialized with Loguru. Log directory: {log_dir}")

def get_logger(name: str):
    """
    获取日志器
    为了保持兼容性，返回标准 logging logger，但会被 InterceptHandler 拦截。
    推荐直接在模块中使用 `from loguru import logger`。
    """
    return logging.getLogger(name)
