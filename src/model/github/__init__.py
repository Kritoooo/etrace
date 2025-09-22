"""
GitHub 数据模型包
提供完整的 GitHub 相关数据模型和枚举
"""

# 导入枚举
from .enums import ModelType, RepositoryType, RepositoryLanguage

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

# 导入事件相关模型
from .event import (
    Event,
    EventActor,
    EventRepo,
    EventPayload,
    PushEventPayload,
    WatchEventPayload,
    CreateEventPayload,
    ForkEventPayload,
    IssuesEventPayload,
    PullRequestEventPayload
)

# 导入抽取 Schema
from .extraction import (
    BaseExtractionSchema,
    RepositoryExtractionSchema,
    UserProfileExtractionSchema,
    EXTRACTION_SCHEMAS
)

# 导入 Schema 映射工具
from .schema_mapping import (
    get_domain_model,
    get_extraction_schema,
    get_extraction_instruction,
    convert_extraction_to_domain,
    DOMAIN_MODEL_MAP,
    EXTRACTION_SCHEMA_MAP,
    SIMPLE_EXTRACTION_MAP
)


# 导出所有公开接口
__all__ = [
    # 枚举
    'ModelType', 'RepositoryType', 'RepositoryLanguage',  # 'ActivityType' 已废弃
    
    # 主要模型
    'Repository', 'UserProfile', 'Event',
    
    # 仓库相关子模型
    'RepositoryOwner', 'RepositoryLicense', 'RepositoryStats', 'RepositoryTopics',
    
    # 用户相关子模型
    'UserSocialLinks', 'UserStats', 'UserOrganization', 'UserSearchResult',
    
    # 事件相关子模型
    'EventActor', 'EventRepo', 'EventPayload', 'PushEventPayload', 'WatchEventPayload',
    'CreateEventPayload', 'ForkEventPayload', 'IssuesEventPayload', 'PullRequestEventPayload',
    
    # 抽取 Schema
    'BaseExtractionSchema', 'RepositoryExtractionSchema', 
    'UserProfileExtractionSchema', 'EXTRACTION_SCHEMAS',
    
    # Schema 映射工具
    'get_domain_model', 'get_extraction_schema', 'get_extraction_instruction',
    'convert_extraction_to_domain', 'DOMAIN_MODEL_MAP', 'EXTRACTION_SCHEMA_MAP',
    'SIMPLE_EXTRACTION_MAP'
]