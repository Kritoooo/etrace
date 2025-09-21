from abc import ABC, abstractmethod
from typing import List, Any, Type, Optional
from ..model.base import BaseModel
from ..service.crawler import CrawlerService


class BaseStrategy(ABC):
    """爬取策略基类"""
    
    def __init__(self, crawler_service: CrawlerService):
        self.crawler_service = crawler_service
    
    @abstractmethod
    async def execute(self, *args, **kwargs) -> List[Any]:
        """执行爬取策略"""
        pass
    
    @abstractmethod
    def get_model_class(self) -> Type[BaseModel]:
        """获取对应的数据模型类"""
        pass
    
    def validate_url(self, url: str) -> bool:
        """验证URL是否符合策略要求"""
        return url.startswith(('http://', 'https://'))
    
    async def crawl_single_url(self, url: str) -> Optional[List[Any]]:
        """爬取单个URL的通用方法"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        model_class = self.get_model_class()
        return await self.crawler_service.crawl_with_extraction(url, model_class)
    
    async def crawl_multiple_urls(self, urls: List[str]) -> List[Optional[List[Any]]]:
        """爬取多个URL的通用方法"""
        invalid_urls = [url for url in urls if not self.validate_url(url)]
        if invalid_urls:
            raise ValueError(f"发现无效URL: {invalid_urls}")
        
        model_class = self.get_model_class()
        return await self.crawler_service.crawl_multiple_urls(urls, model_class)