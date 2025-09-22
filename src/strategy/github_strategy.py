from typing import List, Any, Type, Optional
import json
from .base_strategy import BaseStrategy
from ..model.github import Repository, UserProfile, Event, ModelType
from ..model.github.extraction import BaseExtractionSchema
from ..model.github.schema_mapping import (
    get_domain_model, 
    get_extraction_schema,
    get_extraction_instruction
)
from ..model.github.converters import SchemaToModelConverter, DataConverter
from ..service import GitHubAPIService


class GitHubStrategy(BaseStrategy):
    
    def __init__(self, crawler_service, model_type: ModelType = ModelType.EVENT, use_simple_schema: bool = True):
        super().__init__(crawler_service)
        self.model_type = model_type
        self.use_simple_schema = use_simple_schema
        self.github_api_service = GitHubAPIService(crawler_service.settings)
    
    def get_model_class(self) -> Type:
        return get_domain_model(self.model_type)
    
    def get_extraction_schema_class(self) -> Type[BaseExtractionSchema]:
        return get_extraction_schema(self.model_type, simple=self.use_simple_schema)
    
    def get_extraction_instructions(self) -> str:
        return get_extraction_instruction(self.model_type, simple=self.use_simple_schema)
    
    def validate_url(self, url: str) -> bool:
        return super().validate_url(url) and "github.com" in url
    
    async def execute(self, url: str) -> Optional[List[Any]]:
        return await self.crawl_single_url_with_extraction_schema(url)
    
    def _convert_to_models(self, extracted_data: List[dict]) -> List[Any]:
        """将抽取数据转换为领域模型实例"""
        domain_model_class = self.get_model_class()
        converter = SchemaToModelConverter(self.model_type)
        
        converted_data_list = converter.convert_batch(extracted_data)
        
        domain_models = []
        for converted_data in converted_data_list:
            try:
                model_instance = domain_model_class(**converted_data)
                domain_models.append(model_instance)
            except Exception as e:
                print(f"创建模型实例失败: {e}, 数据: {converted_data}")
                continue
                
        return domain_models
    
    def _process_extraction_data(self, extracted_data: Any) -> List[dict]:
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
        
        elif isinstance(extracted_data, list):
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
        
        elif isinstance(extracted_data, dict):
            return [extracted_data]
        
        else:
            print(f"未知的抽取数据类型: {type(extracted_data)}")
            return []
    
    async def crawl_single_url_with_extraction_schema(self, url: str) -> Optional[List[Any]]:
        """使用抽取Schema爬取单个URL并转换为领域模型"""
        if not self.validate_url(url):
            raise ValueError(f"无效的URL: {url}")
        
        extraction_schema = self.get_extraction_schema_class()
        extracted_data = await self.crawler_service.crawl_with_extraction(url, extraction_schema)
        
        if not extracted_data:
            return None
        
        processed_data = self._process_extraction_data(extracted_data)
        if not processed_data:
            return None
            
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