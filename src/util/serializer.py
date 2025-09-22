"""
数据序列化工具类
处理各种数据类型的序列化，确保输出为人类可阅读的格式
"""
import json
from datetime import datetime, date
from pathlib import Path
from typing import Any, List, Union
from pydantic import BaseModel


class DataSerializer:
    """数据序列化工具类"""
    
    @staticmethod
    def serialize_for_json(data: Any) -> Any:
        """
        将数据序列化为 JSON 兼容格式
        
        Args:
            data: 要序列化的数据
            
        Returns:
            JSON 兼容的数据
        """
        if isinstance(data, BaseModel):
            return data.model_dump()
        elif isinstance(data, list):
            return [DataSerializer.serialize_for_json(item) for item in data]
        elif isinstance(data, dict):
            return {key: DataSerializer.serialize_for_json(value) for key, value in data.items()}
        elif isinstance(data, (datetime, date)):
            return data.isoformat()
        elif hasattr(data, '__dict__'):
            # 处理其他有属性的对象
            return DataSerializer.serialize_for_json(data.__dict__)
        else:
            return data
    
    @staticmethod
    def save_to_json(
        data: Any, 
        file_path: Union[str, Path], 
        indent: int = 2,
        ensure_ascii: bool = False
    ) -> bool:
        """
        将数据保存为 JSON 文件
        
        Args:
            data: 要保存的数据
            file_path: 文件路径
            indent: JSON 缩进
            ensure_ascii: 是否确保 ASCII 编码
            
        Returns:
            是否保存成功
        """
        try:
            # 确保目录存在
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # 序列化数据
            serialized_data = DataSerializer.serialize_for_json(data)
            
            # 保存到文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(
                    serialized_data, 
                    f, 
                    indent=indent, 
                    ensure_ascii=ensure_ascii,
                    default=str
                )
            
            return True
            
        except Exception as e:
            print(f"保存文件失败: {str(e)}")
            return False
    
    @staticmethod
    def convert_pydantic_list_to_dict_list(models: List[BaseModel]) -> List[dict]:
        """
        将 Pydantic 模型列表转换为字典列表
        
        Args:
            models: Pydantic 模型列表
            
        Returns:
            字典列表
        """
        return [model.model_dump() for model in models]
    
    @staticmethod
    def format_data_for_display(data: Any, max_items: int = 10) -> str:
        """
        格式化数据用于显示
        
        Args:
            data: 要格式化的数据
            max_items: 最大显示项目数
            
        Returns:
            格式化后的字符串
        """
        if isinstance(data, list):
            if len(data) > max_items:
                display_data = data[:max_items]
                suffix = f"\n... (显示前 {max_items} 项，共 {len(data)} 项)"
            else:
                display_data = data
                suffix = ""
            
            serialized_data = DataSerializer.serialize_for_json(display_data)
            return json.dumps(serialized_data, indent=2, ensure_ascii=False, default=str) + suffix
        else:
            serialized_data = DataSerializer.serialize_for_json(data)
            return json.dumps(serialized_data, indent=2, ensure_ascii=False, default=str)