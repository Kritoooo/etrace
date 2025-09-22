"""
GitHub API 服务
提供直接的 GitHub API 访问功能，支持获取事件等数据
"""
import asyncio
from typing import List, Optional, Dict, Any
import httpx
from ..config import Settings
from ..model.github import Event
from ..util.logger import get_logger


class GitHubAPIService:
    """GitHub API 服务类"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "ETrace-GitHub-Crawler/1.0"
        }
        
        # 如果配置了 GitHub Token，添加到请求头
        if hasattr(settings, 'github_token') and settings.github_token:
            self.headers["Authorization"] = f"token {settings.github_token}"
    
    async def get_public_events(self, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取公共事件
        
        Args:
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/events"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_user_events(self, username: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取用户事件
        
        Args:
            username: GitHub 用户名
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/users/{username}/events"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_user_public_events(self, username: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取用户公共事件
        
        Args:
            username: GitHub 用户名
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/users/{username}/events/public"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_user_received_events(self, username: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取用户接收的事件
        
        Args:
            username: GitHub 用户名
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/users/{username}/received_events"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_user_received_public_events(self, username: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取用户接收的公共事件
        
        Args:
            username: GitHub 用户名
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/users/{username}/received_events/public"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_repository_events(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取仓库事件
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/repos/{owner}/{repo}/events"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def get_organization_events(self, org: str, per_page: int = 30, page: int = 1) -> Optional[List[Event]]:
        """
        获取组织公共事件
        
        Args:
            org: 组织名称
            per_page: 每页数量，最大100
            page: 页码
            
        Returns:
            事件列表或None
        """
        url = f"{self.base_url}/orgs/{org}/events"
        params = {
            "per_page": min(per_page, 100),
            "page": page
        }
        
        return await self._fetch_events(url, params)
    
    async def _fetch_events(self, url: str, params: Dict[str, Any]) -> Optional[List[Event]]:
        """
        通用的事件获取方法
        
        Args:
            url: API 端点URL
            params: 请求参数
            
        Returns:
            事件列表或None
        """
        try:
            async with httpx.AsyncClient() as client:
                self.logger.info(f"正在请求 GitHub API: {url}")
                
                response = await client.get(
                    url, 
                    headers=self.headers, 
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.logger.info(f"成功获取 {len(data)} 个事件")
                    # self.logger.info(f"事件数据: {data}")
                    # 将 API 响应转换为 Event 对象
                    events = []
                    for event_data in data:
                        try:
                            event = Event.from_api_response(event_data)
                            events.append(event)
                        except Exception as e:
                            self.logger.warning(f"解析事件数据失败: {str(e)}")
                            continue
                    
                    return events
                
                elif response.status_code == 403:
                    self.logger.error("API 请求被限制，可能需要认证或超出了速率限制")
                elif response.status_code == 404:
                    self.logger.error("资源未找到")
                else:
                    self.logger.error(f"API 请求失败: {response.status_code} - {response.text}")
                
                return None
                
        except Exception as e:
            self.logger.error(f"请求 GitHub API 时发生异常: {str(e)}")
            return None
    
    async def get_multiple_user_events(
        self, 
        usernames: List[str], 
        event_type: str = "public",
        per_page: int = 30,
        concurrent_limit: int = 3
    ) -> Dict[str, Optional[List[Event]]]:
        """
        并发获取多个用户的事件
        
        Args:
            usernames: 用户名列表
            event_type: 事件类型 ("public", "all", "received", "received_public")
            per_page: 每页数量
            concurrent_limit: 并发限制
            
        Returns:
            用户名到事件列表的映射
        """
        semaphore = asyncio.Semaphore(concurrent_limit)
        
        async def fetch_user_events(username: str) -> tuple[str, Optional[List[Event]]]:
            async with semaphore:
                if event_type == "public":
                    events = await self.get_user_public_events(username, per_page=per_page)
                elif event_type == "all":
                    events = await self.get_user_events(username, per_page=per_page)
                elif event_type == "received":
                    events = await self.get_user_received_events(username, per_page=per_page)
                elif event_type == "received_public":
                    events = await self.get_user_received_public_events(username, per_page=per_page)
                else:
                    events = await self.get_user_public_events(username, per_page=per_page)
                
                return username, events
        
        tasks = [fetch_user_events(username) for username in usernames]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理结果
        user_events = {}
        for result in results:
            if isinstance(result, Exception):
                self.logger.error(f"获取用户事件时发生异常: {str(result)}")
                continue
            
            username, events = result
            user_events[username] = events
        
        return user_events