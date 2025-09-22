
__version__ = "1.0.0"
__author__ = "Your Name"

from .config import Settings
from .service import CrawlerService, LLMService
from .strategy import GitHubStrategy, BaseStrategy
from .model import Event, Repository, UserProfile
from .util import get_logger, setup_logging

__all__ = [
    "Settings",
    "CrawlerService", 
    "LLMService",
    "GitHubStrategy",
    "BaseStrategy", 
    "Event",
    "Repository",
    "UserProfile",
    "get_logger",
    "setup_logging"
]