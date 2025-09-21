from typing import List, Any, Type, Optional
from .base_strategy import BaseStrategy
from ..model.github import Activity, Repository, UserProfile
from ..model.base import BaseModel


class GitHubStrategy(BaseStrategy):
    """GitHub爬取策略"""
    
    def __init__(self, crawler_service, model_type: str = "activity"):
        super().__init__(crawler_service)
        self.model_type = model_type
        self._model_map = {
            "activity": Activity,
            "repository": Repository,
            "user": UserProfile
        }
    
    def get_model_class(self) -> Type[BaseModel]:
        """根据模型类型返回对应的数据模型类"""
        if self.model_type not in self._model_map:
            raise ValueError(f"不支持的模型类型: {self.model_type}")
        return self._model_map[self.model_type]
    
    def validate_url(self, url: str) -> bool:
        """验证是否为GitHub URL"""
        return super().validate_url(url) and "github.com" in url
    
    async def execute(self, url: str) -> Optional[List[Any]]:
        """执行GitHub爬取策略"""
        return await self.crawl_single_url(url)
    
    async def crawl_user_repositories(self, username: str) -> Optional[List[Any]]:
        """爬取用户的仓库列表"""
        url = f"https://github.com/{username}?tab=repositories"
        self.model_type = "repository"
        return await self.execute(url)
    
    async def crawl_user_activity(self, username: str) -> Optional[List[Any]]:
        """爬取用户活动"""
        url = f"https://github.com/{username}"
        self.model_type = "activity"
        return await self.execute(url)
    
    async def crawl_user_profile(self, username: str) -> Optional[List[Any]]:
        """爬取用户资料"""
        url = f"https://github.com/{username}"
        self.model_type = "user"
        return await self.execute(url)
    
    async def crawl_repository_info(self, owner: str, repo: str) -> Optional[List[Any]]:
        """爬取仓库信息"""
        url = f"https://github.com/{owner}/{repo}"
        self.model_type = "repository"
        return await self.execute(url)