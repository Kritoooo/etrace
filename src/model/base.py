"""
数据模型基类 - 纯粹的业务模型，专注于业务逻辑
"""
from pydantic import BaseModel

# 直接使用Pydantic BaseModel作为业务模型基类
# 业务模型不应该包含抽取相关的功能