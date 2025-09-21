from typing import Type, Any, Dict
from crawl4ai import LLMConfig
from ..config import Settings
from ..model.base import BaseModel


class LLMService:
    """LLM服务封装类"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self._llm_config = None
    
    @property
    def llm_config(self) -> LLMConfig:
        """获取LLM配置"""
        if self._llm_config is None:
            self._llm_config = LLMConfig(
                provider=self.settings.llm.provider,
                api_token=self.settings.llm.api_token,
                base_url=self.settings.llm.base_url
            )
        return self._llm_config
    
    def create_extraction_config(self, model_class: Type[BaseModel]) -> Dict[str, Any]:
        """为指定模型创建提取配置"""
        base_config = model_class.create_extraction_config()
        
        return {
            **base_config,
            "chunk_token_threshold": self.settings.crawler.chunk_token_threshold,
            "apply_chunking": self.settings.crawler.apply_chunking,
            "input_format": self.settings.crawler.input_format,
            "verbose": self.settings.crawler.verbose
        }