import asyncio
from typing import Optional, Any, Type, List
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
from ..config import Settings
from ..model.base import BaseModel
from .llm import LLMService
from ..util.logger import get_logger


class CrawlerService:
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.llm_service = LLMService(settings)
        self.logger = get_logger(__name__)
    
    async def crawl_with_extraction(
        self,
        url: str,
        model_class: Type[BaseModel],
        config: Optional[CrawlerRunConfig] = None
) -> Optional[List[Any]]:
        try:
            from crawl4ai.extraction_strategy import LLMExtractionStrategy
            
            extraction_config = self.llm_service.create_extraction_config(model_class)
            strategy = LLMExtractionStrategy(
                llm_config=self.llm_service.llm_config,
                **extraction_config
            )
            if config is None:
                config = CrawlerRunConfig(extraction_strategy=strategy)
            else:
                config.extraction_strategy = strategy
            
            async with AsyncWebCrawler() as crawler:
                self.logger.info(f"开始爬取URL: {url}")
                result = await crawler.arun(url, config=config)
                if result.success:
                    self.logger.info(f"爬取成功: {url}")
                    return result.extracted_content
                else:
                    self.logger.error(f"爬取失败: {url}, 错误: {result.error_message}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"爬取过程中发生异常: {str(e)}")
            return None
    
    async def crawl_multiple_urls(
        self,
        urls: List[str],
        model_class: Type[BaseModel],
        concurrent_limit: int = 3
) -> List[Optional[List[Any]]]:
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def crawl_with_semaphore(url: str) -> Optional[List[Any]]:
            async with semaphore:
                return await self.crawl_with_extraction(url, model_class)
        
        tasks = [crawl_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"URL {urls[i]} 爬取异常: {str(result)}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results