from typing import Type
from .enums import ModelType
from .extraction import (
    BaseExtractionSchema,
    UserProfileExtractionSchema
)
from .repository import Repository
from .user import UserProfile
from .event import Event


DOMAIN_MODEL_MAP = {
    ModelType.REPOSITORY: Repository,
    ModelType.USER_PROFILE: UserProfile,
    ModelType.EVENT: Event,
}

EXTRACTION_SCHEMA_MAP = {
    ModelType.USER_PROFILE: UserProfileExtractionSchema,
}

SIMPLE_EXTRACTION_MAP = {
    ModelType.USER_PROFILE: UserProfileExtractionSchema,
}


def get_domain_model(model_type: ModelType) -> Type:
    if model_type not in DOMAIN_MODEL_MAP:
        raise ValueError(f"不支持的模型类型: {model_type}")
    return DOMAIN_MODEL_MAP[model_type]


def get_extraction_schema(model_type: ModelType, simple: bool = False) -> Type[BaseExtractionSchema]:
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


def convert_extraction_to_domain(extraction_data: dict, model_type: ModelType) -> dict:
    """将抽取数据转换为领域数据格式
    
    这个函数可以在后续实现数据转换逻辑
    目前简单返回原数据
    """
    # TODO: 实现具体的数据转换逻辑
    # 例如：字符串数字转换为整数，时间格式标准化等
    return extraction_data


# 导出所有映射和函数
__all__ = [
    'DOMAIN_MODEL_MAP',
    'EXTRACTION_SCHEMA_MAP', 
    'SIMPLE_EXTRACTION_MAP',
    'get_domain_model',
    'get_extraction_schema',
    'get_extraction_instruction',
    'convert_extraction_to_domain'
]