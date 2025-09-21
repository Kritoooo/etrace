"""
GitHub 数据抽取专用的简化 Schema
仅包含基本数据类型，专门用于 LLM 数据抽取
与业务数据模型分离，保持简单高效
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BaseExtractionSchema(BaseModel):
    """抽取 Schema 基类"""
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        """获取提取指令 - 子类必须实现"""
        raise NotImplementedError("子类必须实现 get_extraction_instruction 方法")
    
    @classmethod
    def get_schema_dict(cls) -> Dict[str, Any]:
        """获取模型的JSON schema"""
        return cls.model_json_schema()
    
    @classmethod
    def create_extraction_config(cls) -> Dict[str, Any]:
        """创建提取配置"""
        return {
            "schema": cls.get_schema_dict(),
            "instruction": cls.get_extraction_instruction(),
            "extraction_type": "schema"
        }


class ActivityExtractionSchema(BaseExtractionSchema):
    """活动数据抽取 Schema - 简化版本"""
    
    # 基础信息 - 只保留字符串类型
    type: str = Field(..., description="活动类型（如：push, pull_request, issue, star, fork等）")
    timestamp: str = Field(..., description="活动时间")
    
    # 执行者信息
    actor_username: str = Field(..., description="执行者用户名")
    actor_avatar: Optional[str] = Field(None, description="执行者头像URL")
    
    # 仓库信息
    repository_name: str = Field(..., description="仓库名称（格式：owner/repo）")
    repository_url: str = Field(..., description="仓库URL")
    repository_description: Optional[str] = Field(None, description="仓库描述")
    
    # 活动详情 - 使用简单字符串
    action_description: str = Field(..., description="活动描述")
    commit_count: Optional[str] = Field(None, description="提交数量（如果适用）")
    branch_name: Optional[str] = Field(None, description="分支名称（如果适用）")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub活动页面中提取用户活动信息。
        重点关注：
        1. 活动类型（push、pull_request、issue、star、fork等）
        2. 活动时间
        3. 执行者信息
        4. 相关仓库信息
        5. 活动的具体描述
        
        请返回JSON格式的活动列表。"""


class RepositoryExtractionSchema(BaseExtractionSchema):
    """仓库数据抽取 Schema - 简化版本"""
    
    # 基础信息
    name: str = Field(..., description="仓库名称")
    full_name: str = Field(..., description="完整名称（owner/repo）")
    description: Optional[str] = Field(None, description="仓库描述")
    url: str = Field(..., description="仓库URL")
    
    # 所有者信息
    owner_username: str = Field(..., description="所有者用户名")
    owner_type: str = Field("User", description="所有者类型（User/Organization）")
    
    # 技术信息 - 使用字符串类型
    language: Optional[str] = Field(None, description="主要编程语言")
    topics: List[str] = Field(default_factory=list, description="话题标签")
    
    # 统计信息 - 使用字符串避免类型转换问题
    stars: str = Field("0", description="星标数")
    forks: str = Field("0", description="分叉数")
    watchers: str = Field("0", description="关注者数")
    open_issues: str = Field("0", description="开放问题数")
    
    # 时间信息
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="最后更新时间")
    pushed_at: Optional[str] = Field(None, description="最后推送时间")
    
    # 仓库状态
    private: str = Field("false", description="是否私有（true/false）")
    fork: str = Field("false", description="是否为分叉（true/false）")
    archived: str = Field("false", description="是否已归档（true/false）")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub仓库页面中提取仓库详细信息。
        重点关注：
        1. 仓库基本信息（名称、描述、URL）
        2. 所有者信息
        3. 技术信息（主要语言、话题标签）
        4. 统计数据（星标、分叉、关注者、问题数）
        5. 时间信息（创建、更新、推送时间）
        6. 仓库状态（私有、分叉、归档状态）
        
        统计数据请提取为字符串格式，时间请保持原始格式。
        请返回JSON格式的仓库信息。"""


class UserProfileExtractionSchema(BaseExtractionSchema):
    """用户资料抽取 Schema - 简化版本"""
    
    # 基础信息
    username: str = Field(..., description="用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    
    # 位置和工作信息
    location: Optional[str] = Field(None, description="地理位置")
    company: Optional[str] = Field(None, description="公司/组织")
    
    # 联系方式
    website: Optional[str] = Field(None, description="个人网站")
    twitter: Optional[str] = Field(None, description="Twitter用户名")
    email: Optional[str] = Field(None, description="邮箱地址")
    
    # 统计信息 - 使用字符串类型
    followers: str = Field("0", description="关注者数量")
    following: str = Field("0", description="关注数量")
    public_repos: str = Field("0", description="公开仓库数量")
    public_gists: str = Field("0", description="公开Gist数量")
    
    # 账户信息
    account_type: str = Field("User", description="账户类型（User/Organization）")
    created_at: str = Field(..., description="账户创建时间")
    
    # 组织信息
    organizations: List[str] = Field(default_factory=list, description="所属组织列表")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub用户资料页面中提取用户信息。
        重点关注：
        1. 基础信息（用户名、显示名称、头像、简介）
        2. 位置和工作信息
        3. 联系方式（网站、社交媒体）
        4. 统计数据（关注者、关注数、仓库数、Gist数）
        5. 账户信息（类型、创建时间）
        6. 所属组织列表
        
        统计数据请提取为字符串格式，避免数字解析错误。
        请返回JSON格式的用户信息。"""


class SimpleActivitySchema(BaseExtractionSchema):
    """极简活动抽取 Schema - 用于快速提取"""
    repositories: str = Field(..., description="仓库名称")
    date: str = Field(..., description="活动日期")
    activity_type: str = Field(..., description="活动类型")
    description: str = Field(..., description="活动描述")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub页面中提取简单的活动信息。
        每个活动包含：仓库名称、日期、活动类型、描述。
        请返回JSON格式的活动列表。"""


# 抽取 Schema 映射
EXTRACTION_SCHEMAS = {
    "activity": ActivityExtractionSchema,
    "repository": RepositoryExtractionSchema, 
    "user_profile": UserProfileExtractionSchema,
    "simple_activity": SimpleActivitySchema,
}


def get_extraction_schema(model_type: str) -> BaseModel:
    """根据模型类型获取对应的抽取 Schema"""
    return EXTRACTION_SCHEMAS.get(model_type, SimpleActivitySchema)