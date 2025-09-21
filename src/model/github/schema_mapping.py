"""
模型类型到抽取 Schema 的映射
提供业务模型和抽取 Schema 之间的转换
"""
from typing import Type
from .enums import ModelType
from .extraction import (
    ActivityExtractionSchema,
    RepositoryExtractionSchema,
    UserProfileExtractionSchema,
    SimpleActivitySchema
)
from .activity import Activity
from .repository import Repository
from .user import UserProfile
from ..base import BaseModel


# 业务模型映射
BUSINESS_MODEL_MAP = {
    ModelType.ACTIVITY: Activity,
    ModelType.REPOSITORY: Repository,
    ModelType.USER_PROFILE: UserProfile,
}

# 抽取 Schema 映射
EXTRACTION_SCHEMA_MAP = {
    ModelType.ACTIVITY: ActivityExtractionSchema,
    ModelType.REPOSITORY: RepositoryExtractionSchema,
    ModelType.USER_PROFILE: UserProfileExtractionSchema,
}

# 简化抽取 Schema 映射（用于快速抽取）
SIMPLE_EXTRACTION_MAP = {
    ModelType.ACTIVITY: SimpleActivitySchema,
    ModelType.REPOSITORY: RepositoryExtractionSchema,  # 仓库使用标准版本
    ModelType.USER_PROFILE: UserProfileExtractionSchema,  # 用户使用标准版本
}


def get_business_model(model_type: ModelType) -> Type[BaseModel]:
    """获取业务数据模型类"""
    if model_type not in BUSINESS_MODEL_MAP:
        raise ValueError(f"不支持的模型类型: {model_type}")
    return BUSINESS_MODEL_MAP[model_type]


def get_extraction_schema(model_type: ModelType, simple: bool = False) -> Type[BaseModel]:
    """获取抽取 Schema 类
    
    Args:
        model_type: 模型类型
        simple: 是否使用简化版本
    """
    schema_map = SIMPLE_EXTRACTION_MAP if simple else EXTRACTION_SCHEMA_MAP
    
    if model_type not in schema_map:
        raise ValueError(f"不支持的模型类型: {model_type}")
    
    return schema_map[model_type]


def get_extraction_instruction(model_type: ModelType, simple: bool = False) -> str:
    """获取抽取指令"""
    schema_class = get_extraction_schema(model_type, simple)
    return schema_class.get_extraction_instruction()


def convert_extraction_to_business(extraction_data: dict, model_type: ModelType) -> dict:
    """将抽取数据转换为业务数据格式
    
    这个函数可以在后续实现数据转换逻辑
    目前简单返回原数据
    """
    # TODO: 实现具体的数据转换逻辑
    # 例如：字符串数字转换为整数，时间格式标准化等
    return extraction_data


# 导出所有映射和函数
__all__ = [
    'BUSINESS_MODEL_MAP',
    'EXTRACTION_SCHEMA_MAP', 
    'SIMPLE_EXTRACTION_MAP',
    'get_business_model',
    'get_extraction_schema',
    'get_extraction_instruction',
    'convert_extraction_to_business'
]