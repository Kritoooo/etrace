from .github import (
    # 主要模型
    Event, Repository, UserProfile,
    # 枚举
    ModelType, RepositoryType, RepositoryLanguage,
    # 子模型
    RepositoryOwner, RepositoryLicense, RepositoryStats, RepositoryTopics,
    UserSocialLinks, UserStats, UserOrganization, UserSearchResult,
    # Event相关模型
    EventActor, EventRepo, EventPayload, PushEventPayload, WatchEventPayload,
    CreateEventPayload, ForkEventPayload, IssuesEventPayload, PullRequestEventPayload
)
# 业务模型直接使用Pydantic BaseModel，专注于业务逻辑
from pydantic import BaseModel as DataModel

# 单独导入各模块以支持更精细的导入
from . import github

__all__ = [
    # 主要模型
    "Event", "Repository", "UserProfile",
    # 枚举
    "ModelType", "RepositoryType", "RepositoryLanguage",
    # 子模型
    "RepositoryOwner", "RepositoryLicense", "RepositoryStats", "RepositoryTopics", 
    "UserSocialLinks", "UserStats", "UserOrganization", "UserSearchResult",
    # Event相关模型
    "EventActor", "EventRepo", "EventPayload", "PushEventPayload", "WatchEventPayload",
    "CreateEventPayload", "ForkEventPayload", "IssuesEventPayload", "PullRequestEventPayload",
    # 基础模型
    "DataModel",
    # 模块
    "github"
]