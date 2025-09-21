from typing import List, Any, Type, Optional
from .base_strategy import BaseStrategy
from ..model.github import Activity, Repository, UserProfile, ModelType
from ..model.github.schema_mapping import (
    get_business_model, 
    get_extraction_schema,
    get_extraction_instruction
)
from ..model.base import BaseModel


class GitHubStrategy(BaseStrategy):
    """GitHub爬取策略"""
    
    def __init__(self, crawler_service, model_type: ModelType = ModelType.ACTIVITY, use_simple_schema: bool = True):
        super().__init__(crawler_service)
        self.model_type = model_type
        self.use_simple_schema = use_simple_schema
    
    def get_model_class(self) -> Type[BaseModel]:
        """根据模型类型返回对应的数据模型类"""
        return get_business_model(self.model_type)
    
    def get_extraction_schema_class(self) -> Type[BaseModel]:
        """获取抽取 Schema 类"""
        return get_extraction_schema(self.model_type, simple=self.use_simple_schema)
    
    def get_extraction_instructions(self) -> str:
        """获取抽取指令"""
        return get_extraction_instruction(self.model_type, simple=self.use_simple_schema)
    
    def validate_url(self, url: str) -> bool:
        """验证是否为GitHub URL"""
        return super().validate_url(url) and "github.com" in url
    
    async def execute(self, url: str) -> Optional[List[Any]]:
        """执行GitHub爬取策略"""
        return await self.crawl_single_url_with_extraction_schema(url)
    
    async def crawl_single_url_with_extraction_schema(self, url: str) -> Optional[List[Any]]:
        """使用抽取 Schema 爬取单个URL"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        extraction_schema = self.get_extraction_schema_class()
        return await self.crawler_service.crawl_with_extraction(url, extraction_schema)
    
    async def crawl_user_repositories(self, username: str) -> Optional[List[Any]]:
        """爬取用户的仓库列表"""
        url = f"https://github.com/{username}?tab=repositories"
        self.model_type = ModelType.REPOSITORY
        return await self.execute(url)
    
    async def crawl_user_activity(self, username: str) -> Optional[List[Any]]:
        """爬取用户活动"""
        url = f"https://github.com/{username}"
        self.model_type = ModelType.ACTIVITY
        return await self.execute(url)
    
    async def crawl_user_profile(self, username: str) -> Optional[List[Any]]:
        """爬取用户资料"""
        url = f"https://github.com/{username}"
        self.model_type = ModelType.USER_PROFILE
        return await self.execute(url)
    
    async def crawl_repository_info(self, owner: str, repo: str) -> Optional[List[Any]]:
        """爬取仓库信息"""
        url = f"https://github.com/{owner}/{repo}"
        self.model_type = ModelType.REPOSITORY
        return await self.execute(url)