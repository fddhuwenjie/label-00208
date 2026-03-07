"""
统一日志模块

提供结构化的日志记录功能，替代分散的 print() 语句。
支持控制台输出和文件记录，便于调试和问题排查。
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# 日志格式
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# 日志目录
LOG_DIR = Path("/app/data/logs") if Path("/app").exists() else Path("data/logs")


def setup_logger(
    name: str,
    level: int = logging.INFO,
    log_to_file: bool = False,
    log_file: Optional[str] = None
) -> logging.Logger:
    """
    创建并配置日志记录器
    
    Args:
        name: 日志记录器名称（通常使用模块名）
        level: 日志级别
        log_to_file: 是否写入文件
        log_file: 日志文件名（可选）
        
    Returns:
        配置好的 Logger 实例
    """
    logger = logging.getLogger(name)
    
    # 避免重复添加 handler
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # 控制台 Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
    logger.addHandler(console_handler)
    
    # 文件 Handler（可选）
    if log_to_file:
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        
        if log_file is None:
            log_file = f"{name}_{datetime.now().strftime('%Y%m%d')}.log"
        
        file_handler = logging.FileHandler(
            LOG_DIR / log_file,
            encoding="utf-8"
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT))
        logger.addHandler(file_handler)
    
    return logger


# 预配置的模块日志器
def get_logger(name: str) -> logging.Logger:
    """
    获取模块日志记录器（简化接口）
    
    Args:
        name: 模块名称
        
    Returns:
        Logger 实例
    """
    return setup_logger(f"debateprep.{name}")


# 应用级日志器
app_logger = get_logger("app")
search_logger = get_logger("search")
parser_logger = get_logger("parser")
db_logger = get_logger("database")
semantic_logger = get_logger("semantic")


class LoggerMixin:
    """
    日志混入类，为类提供 self.logger 属性
    
    使用方式：
        class MyService(LoggerMixin):
            def do_something(self):
                self.logger.info("Doing something")
    """
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, "_logger"):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger
