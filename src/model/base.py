from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pydantic import BaseModel as PydanticBaseModel


class BaseModel(PydanticBaseModel, ABC):
    """数据模型基类"""
    
    @classmethod
    @abstractmethod
    def get_extraction_instruction(cls) -> str:
        """获取提取指令"""
        pass
    
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