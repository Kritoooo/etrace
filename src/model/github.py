"""
GitHub 数据模型集合 - 统一导入接口
为了保持向后兼容性，从子包中重新导出所有模型
"""

# 从 github 子包导入所有内容
from .github import *

# 确保所有导出内容都包含在 __all__ 中
from .github import __all__