from enum import StrEnum, auto


class ModelType(StrEnum):
    REPOSITORY = auto()
    USER_PROFILE = auto()
    EVENT = auto()


class RepositoryType(StrEnum):
    PUBLIC = auto()
    PRIVATE = auto()
    FORK = auto()
    TEMPLATE = auto()
    ARCHIVED = auto()


class RepositoryLanguage(StrEnum):
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