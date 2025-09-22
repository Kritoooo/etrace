from typing import List, Any, Type, Optional
from datetime import datetime
import json
from .base_strategy import BaseStrategy
from ..model.github import Repository, UserProfile, Event, ModelType
from ..model.github.extraction import BaseExtractionSchema
from ..model.github.schema_mapping import (
    get_business_model, 
    get_extraction_schema,
    get_extraction_instruction
)
# 移除ExtractableModel引用，业务模型现在是纯粹的
from ..service import GitHubAPIService


class GitHubStrategy(BaseStrategy):
    """GitHub爬取策略"""
    
    def __init__(self, crawler_service, model_type: ModelType = ModelType.EVENT, use_simple_schema: bool = True):
        super().__init__(crawler_service)
        self.model_type = model_type
        self.use_simple_schema = use_simple_schema
        self.github_api_service = GitHubAPIService(crawler_service.settings)
    
    def get_model_class(self) -> Type:
        """根据模型类型返回对应的数据模型类"""
        return get_business_model(self.model_type)
    
    def get_extraction_schema_class(self) -> Type[BaseExtractionSchema]:
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
    
    def _convert_to_models(self, extracted_data: List[dict]) -> List[Any]:
        """将抽取数据转换为业务模型实例"""
        business_model_class = self.get_model_class()
        business_models = []
        
        for data in extracted_data:
            try:
                # 根据模型类型进行数据转换
                converted_data = self._convert_extraction_to_business_data(data)
                model_instance = business_model_class(**converted_data)
                business_models.append(model_instance)
            except Exception as e:
                print(f"转换数据失败: {e}, 数据: {data}")
                continue
                
        return business_models
    
    def _process_extraction_data(self, extracted_data: Any) -> List[dict]:
        """处理抽取数据，确保返回字典列表格式"""
        # 如果是字符串，尝试解析为JSON
        if isinstance(extracted_data, str):
            try:
                parsed_data = json.loads(extracted_data)
                if isinstance(parsed_data, list):
                    return parsed_data
                elif isinstance(parsed_data, dict):
                    return [parsed_data]
                else:
                    print(f"解析后的数据格式不正确: {type(parsed_data)}")
                    return []
            except json.JSONDecodeError as e:
                print(f"JSON解析失败: {e}, 数据: {extracted_data[:100]}...")
                return []
        
        # 如果是列表，直接返回
        elif isinstance(extracted_data, list):
            # 检查列表中的元素是否都是字典
            result = []
            for item in extracted_data:
                if isinstance(item, dict):
                    result.append(item)
                elif isinstance(item, str):
                    try:
                        parsed_item = json.loads(item)
                        if isinstance(parsed_item, dict):
                            result.append(parsed_item)
                        else:
                            print(f"列表中的字符串解析后不是字典: {type(parsed_item)}")
                    except json.JSONDecodeError:
                        print(f"列表中的字符串不是有效JSON: {item[:100]}...")
                else:
                    print(f"列表中包含非字典非字符串元素: {type(item)}")
            return result
        
        # 如果是字典，包装成列表
        elif isinstance(extracted_data, dict):
            return [extracted_data]
        
        # 其他类型
        else:
            print(f"未知的抽取数据类型: {type(extracted_data)}")
            return []
    
    def _convert_extraction_to_business_data(self, extraction_data: dict) -> dict:
        """将抽取Schema数据转换为业务模型数据格式"""
        if self.model_type == ModelType.USER_PROFILE:
            return self._convert_user_profile_data(extraction_data)
        elif self.model_type == ModelType.REPOSITORY:
            return self._convert_repository_data(extraction_data)
        elif self.model_type == ModelType.EVENT:
            return self._convert_event_data(extraction_data)
        else:
            return extraction_data
    
    def _convert_user_profile_data(self, data: dict) -> dict:
        """转换用户资料数据"""
        # 确保必要字段存在
        username = data.get('username', '')
        if not username:
            # 如果没有username，使用其他可用字段作为fallback
            username = data.get('login', data.get('name', 'unknown'))
        
        return {
            'id': username,
            'username': username,
            'name': data.get('display_name', ''),
            'bio': data.get('bio', ''),
            'avatar_url': data.get('avatar_url') or None,
            'gravatar_id': '',
            'location': data.get('location', ''),
            'company': data.get('company', ''),
            'hireable': True,
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'type': data.get('account_type', 'User'),
            'site_admin': False,
            # 嵌套对象 - 使用字典，Pydantic会自动转换
            'social_links': {
                'website': data.get('website'),
                'twitter': data.get('twitter'),
                'email': data.get('email')
            },
            'stats': {
                'followers': int(data.get('followers', '0') or '0'),
                'following': int(data.get('following', '0') or '0'),
                'public_repos': int(data.get('public_repos', '0') or '0'),
                'public_gists': int(data.get('public_gists', '0') or '0'),
                'private_repos': 0,
                'owned_private_repos': 0,
                'total_private_repos': 0,
                'collaborators': 0
            },
            'html_url': f"https://github.com/{username}",
            'organizations': []  # 空列表，后续可以填充
        }
    
    def _convert_repository_data(self, data: dict) -> dict:
        """转换仓库数据"""
        return {
            'id': str(hash(data.get('name', 'unknown'))),
            'node_id': f"R_{hash(data.get('name', 'unknown'))}",
            'name': data.get('name', ''),
            'full_name': data.get('full_name', data.get('name', '')),
            'description': data.get('description', ''),
            'private': False,  # 从网页抓取的通常是公开仓库
            'html_url': data.get('url', ''),
            'clone_url': data.get('url', ''),
            'created_at': datetime.now(),
            'updated_at': datetime.now(),
            'pushed_at': datetime.now(),
            'size': 0,
            'stargazers_count': int(str(data.get('stars', '0')).replace(',', '') or '0'),
            'watchers_count': int(str(data.get('watchers', '0')).replace(',', '') or '0'),
            'language': data.get('language', ''),
            'forks_count': int(str(data.get('forks', '0')).replace(',', '') or '0'),
            'archived': False,
            'disabled': False,
            'open_issues_count': 0,
            'license': None,
            'allow_forking': True,
            'is_template': False,
            'visibility': 'public',
            'default_branch': 'main',
            # 嵌套对象
            'owner': {
                'login': data.get('owner_username', ''),
                'type': data.get('owner_type', 'User'),
                'avatar_url': '',
                'html_url': ''
            },
            'topics': [],
            'stats': {
                'stargazers_count': int(str(data.get('stars', '0')).replace(',', '') or '0'),
                'watchers_count': int(str(data.get('watchers', '0')).replace(',', '') or '0'),
                'forks_count': int(str(data.get('forks', '0')).replace(',', '') or '0'),
                'open_issues_count': 0,
                'network_count': 0,
                'subscribers_count': 0
            }
        }
    
    def _convert_event_data(self, data: dict) -> dict:
        """转换事件数据 - 这个需要特殊处理，因为Event模型期望API格式"""
        # 由于Event模型是为GitHub API设计的，从网页抽取的数据格式不匹配
        # 这里创建一个兼容的数据结构
        return {
            'id': str(hash(f"{data.get('type', 'unknown')}_{data.get('timestamp', '')}")),
            'type': f"{data.get('type', 'Unknown')}Event",
            'actor': {
                'id': hash(data.get('actor_username', 'unknown')),
                'login': data.get('actor_username', ''),
                'avatar_url': data.get('actor_avatar', ''),
                'url': f"https://github.com/{data.get('actor_username', '')}"
            },
            'repo': {
                'id': hash(data.get('repository_name', 'unknown')),
                'name': data.get('repository_name', ''),
                'url': data.get('repository_url', '')
            },
            'payload': {
                'action': data.get('action_description', ''),
                'size': int(data.get('commit_count', '0') or '0'),
                'ref': data.get('branch_name', '')
            },
            'public': True,
            'created_at': data.get('timestamp', datetime.now().isoformat())
        }
    
    async def crawl_single_url_with_extraction_schema(self, url: str) -> Optional[List[Any]]:
        """使用抽取 Schema 爬取单个URL并转换为业务模型"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        extraction_schema = self.get_extraction_schema_class()
        extracted_data = await self.crawler_service.crawl_with_extraction(url, extraction_schema)
        
        if not extracted_data:
            return None
        
        # 处理可能的JSON字符串格式
        processed_data = self._process_extraction_data(extracted_data)
        if not processed_data:
            return None
            
        # 转换为业务模型
        return self._convert_to_models(processed_data)
    
    async def crawl_user_repositories(self, username: str) -> Optional[List[Repository]]:
        """爬取用户的仓库列表"""
        url = f"https://github.com/{username}?tab=repositories"
        self.model_type = ModelType.REPOSITORY
        return await self.execute(url)
    
    async def crawl_user_activity(self, username: str) -> Optional[List[Event]]:
        """爬取用户活动"""
        url = f"https://github.com/{username}"
        self.model_type = ModelType.EVENT
        return await self.execute(url)
    
    async def crawl_user_profile(self, username: str) -> Optional[List[UserProfile]]:
        """爬取用户资料"""
        url = f"https://github.com/{username}"
        self.model_type = ModelType.USER_PROFILE
        return await self.execute(url)
    
    async def crawl_repository_info(self, owner: str, repo: str) -> Optional[List[Repository]]:
        """爬取仓库信息"""
        url = f"https://github.com/{owner}/{repo}"
        self.model_type = ModelType.REPOSITORY
        return await self.execute(url)
    
    async def get_user_events_via_api(self, username: str, event_type: str = "public", per_page: int = 30) -> Optional[List[Event]]:
        """
        通过 API 获取用户事件
        
        Args:
            username: GitHub 用户名
            event_type: 事件类型 ("public", "all", "received", "received_public")
            per_page: 每页数量
            
        Returns:
            事件列表或None
        """
        if event_type == "public":
            return await self.github_api_service.get_user_public_events(username, per_page=per_page)
        elif event_type == "all":
            return await self.github_api_service.get_user_events(username, per_page=per_page)
        elif event_type == "received":
            return await self.github_api_service.get_user_received_events(username, per_page=per_page)
        elif event_type == "received_public":
            return await self.github_api_service.get_user_received_public_events(username, per_page=per_page)
        else:
            return await self.github_api_service.get_user_public_events(username, per_page=per_page)
    
    async def get_repository_events_via_api(self, owner: str, repo: str, per_page: int = 30) -> Optional[List[Event]]:
        """
        通过 API 获取仓库事件
        
        Args:
            owner: 仓库所有者
            repo: 仓库名称
            per_page: 每页数量
            
        Returns:
            事件列表或None
        """
        return await self.github_api_service.get_repository_events(owner, repo, per_page=per_page)
    
    async def get_organization_events_via_api(self, org: str, per_page: int = 30) -> Optional[List[Event]]:
        """
        通过 API 获取组织事件
        
        Args:
            org: 组织名称
            per_page: 每页数量
            
        Returns:
            事件列表或None
        """
        return await self.github_api_service.get_organization_events(org, per_page=per_page)
    
    async def get_public_events_via_api(self, per_page: int = 30) -> Optional[List[Event]]:
        """
        通过 API 获取公共事件
        
        Args:
            per_page: 每页数量
            
        Returns:
            事件列表或None
        """
        return await self.github_api_service.get_public_events(per_page=per_page)