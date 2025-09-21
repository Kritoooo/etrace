"""
GitHub 相关枚举定义
"""
from enum import StrEnum, auto


class ModelType(StrEnum):
    """数据模型类型枚举"""
    ACTIVITY = auto()
    REPOSITORY = auto()
    USER_PROFILE = auto()


class ActivityType(StrEnum):
    """GitHub 活动类型枚举"""
    PUSH = auto()
    PULL_REQUEST = auto()
    ISSUE = auto()
    ISSUE_COMMENT = auto()
    CREATE_REPO = auto()
    STAR = auto()
    FORK = auto()
    WATCH = auto()
    COMMIT = auto()
    RELEASE = auto()
    UNKNOWN = auto()


class RepositoryType(StrEnum):
    """仓库类型枚举"""
    PUBLIC = auto()
    PRIVATE = auto()
    FORK = auto()
    TEMPLATE = auto()
    ARCHIVED = auto()


class RepositoryLanguage(StrEnum):
    """主要编程语言枚举"""
    PYTHON = auto()
    JAVASCRIPT = auto()
    TYPESCRIPT = auto()
    JAVA = auto()
    GO = auto()
    RUST = auto()
    CPP = auto()
    C = auto()
    CSHARP = auto()
    PHP = auto()
    RUBY = auto()
    SWIFT = auto()
    KOTLIN = auto()
    DART = auto()
    HTML = auto()
    CSS = auto()
    SHELL = auto()
    OTHER = auto()