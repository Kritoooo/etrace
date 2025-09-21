"""
GitHub 数据模型包
提供完整的 GitHub 相关数据模型和枚举
"""

# 导入枚举
from .enums import ModelType, ActivityType, RepositoryType, RepositoryLanguage

# 导入活动相关模型
from .activity import (
    Activity, 
    ActivityActor, 
    ActivityTarget, 
    ActivityPayload, 
    ActivityStats
)

# 导入仓库相关模型
from .repository import (
    Repository,
    RepositoryOwner,
    RepositoryLicense,
    RepositoryStats,
    RepositoryTopics
)

# 导入用户相关模型
from .user import (
    UserProfile,
    UserSocialLinks,
    UserStats,
    UserOrganization,
    UserSearchResult
)

# 导入抽取 Schema
from .extraction import (
    BaseExtractionSchema,
    ActivityExtractionSchema,
    RepositoryExtractionSchema,
    UserProfileExtractionSchema,
    SimpleActivitySchema,
    EXTRACTION_SCHEMAS
)

# 导入 Schema 映射工具
from .schema_mapping import (
    get_business_model,
    get_extraction_schema,
    get_extraction_instruction,
    convert_extraction_to_business,
    BUSINESS_MODEL_MAP,
    EXTRACTION_SCHEMA_MAP,
    SIMPLE_EXTRACTION_MAP
)

# 为了保持向后兼容性，保留原有的简单模型定义
from pydantic import Field
from ..base import BaseModel


class LegacyActivity(BaseModel):
    """遗留的简单活动模型（保持向后兼容）"""
    repositories: str = Field(..., description="存储库的名称")
    date: str = Field(..., description="存储库的创建或更新日期")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从提供的HTML内容中提取GitHub存储库信息。包含存储库名称和日期。"


class LegacyRepository(BaseModel):
    """遗留的简单仓库模型（保持向后兼容）"""
    name: str = Field(..., description="仓库名称")
    description: str = Field(default="", description="仓库描述")
    language: str = Field(default="", description="主要编程语言")
    stars: int = Field(default=0, description="星标数")
    forks: int = Field(default=0, description="分支数")
    updated_at: str = Field(..., description="最后更新时间")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从GitHub页面中提取仓库的详细信息，包括名称、描述、语言、星标数、分支数和更新时间。"


class LegacyUserProfile(BaseModel):
    """遗留的简单用户模型（保持向后兼容）"""
    username: str = Field(..., description="用户名")
    name: str = Field(default="", description="显示名称")
    bio: str = Field(default="", description="个人简介")
    location: str = Field(default="", description="地理位置")
    company: str = Field(default="", description="所属公司")
    followers: int = Field(default=0, description="关注者数量")
    following: int = Field(default=0, description="关注数量")
    public_repos: int = Field(default=0, description="公开仓库数量")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从GitHub用户资料页面中提取用户的基本信息，包括用户名、显示名称、简介、位置、公司和统计数据。"


# 导出所有公开接口
__all__ = [
    # 枚举
    'ModelType', 'ActivityType', 'RepositoryType', 'RepositoryLanguage',
    
    # 主要模型
    'Activity', 'Repository', 'UserProfile',
    
    # 活动相关子模型
    'ActivityActor', 'ActivityTarget', 'ActivityPayload', 'ActivityStats',
    
    # 仓库相关子模型
    'RepositoryOwner', 'RepositoryLicense', 'RepositoryStats', 'RepositoryTopics',
    
    # 用户相关子模型
    'UserSocialLinks', 'UserStats', 'UserOrganization', 'UserSearchResult',
    
    # 遗留模型
    'LegacyActivity', 'LegacyRepository', 'LegacyUserProfile',
    
    # 抽取 Schema
    'BaseExtractionSchema', 'ActivityExtractionSchema', 'RepositoryExtractionSchema', 
    'UserProfileExtractionSchema', 'SimpleActivitySchema', 'EXTRACTION_SCHEMAS',
    
    # Schema 映射工具
    'get_business_model', 'get_extraction_schema', 'get_extraction_instruction',
    'convert_extraction_to_business', 'BUSINESS_MODEL_MAP', 'EXTRACTION_SCHEMA_MAP',
    'SIMPLE_EXTRACTION_MAP'
]