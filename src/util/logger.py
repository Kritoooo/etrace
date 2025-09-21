import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    设置日志配置
    
    Args:
        level: 日志级别
        log_file: 日志文件路径
        format_string: 日志格式字符串
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # 配置根日志记录器
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=format_string,
        handlers=[]
    )
    
    # 添加控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(format_string))
    logging.getLogger().addHandler(console_handler)
    
    # 添加文件处理器（如果指定）
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter(format_string))
        logging.getLogger().addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """
    获取日志记录器
    
    Args:
        name: 记录器名称
        
    Returns:
        日志记录器实例
    """
    return logging.getLogger(name)