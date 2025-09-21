"""
ETrace - 可扩展的网页数据提取工具

一个基于crawl4ai的模块化网页爬虫框架，支持自定义数据模型和提取策略。
"""

__version__ = "1.0.0"
__author__ = "Your Name"

from .config import Settings
from .service import CrawlerService, LLMService
from .strategy import GitHubStrategy, BaseStrategy
from .model import Activity, Repository, UserProfile
from .util import get_logger, setup_logging

__all__ = [
    "Settings",
    "CrawlerService", 
    "LLMService",
    "GitHubStrategy",
    "BaseStrategy", 
    "Activity",
    "Repository",
    "UserProfile",
    "get_logger",
    "setup_logging"
]