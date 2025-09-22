from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class BaseExtractionSchema(BaseModel):
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        raise NotImplementedError("子类必须实现 get_extraction_instruction 方法")
    
    @classmethod
    def get_schema_dict(cls) -> Dict[str, Any]:
        return cls.model_json_schema()
    
    @classmethod
    def create_extraction_config(cls) -> Dict[str, Any]:
        return {
            "schema": cls.get_schema_dict(),
            "instruction": cls.get_extraction_instruction(),
            "extraction_type": "schema"
        }





class UserProfileExtractionSchema(BaseExtractionSchema):
    """用户资料抽取 Schema - 简化版本"""
    
    # 基础信息
    username: str = Field(..., description="用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    
    # 位置和工作信息
    location: Optional[str] = Field(None, description="地理位置")
    company: Optional[str] = Field(None, description="公司/组织")
    
    # 联系方式
    website: Optional[str] = Field(None, description="个人网站")
    twitter: Optional[str] = Field(None, description="Twitter用户名")
    email: Optional[str] = Field(None, description="邮箱地址")
    
    # 统计信息 - 使用字符串类型
    followers: str = Field("0", description="关注者数量")
    following: str = Field("0", description="关注数量")
    public_repos: str = Field("0", description="公开仓库数量")
    public_gists: str = Field("0", description="公开Gist数量")
    
    # 账户信息
    account_type: str = Field("User", description="账户类型（User/Organization）")
    created_at: str = Field(..., description="账户创建时间")
    
    # 组织信息
    organizations: List[str] = Field(default_factory=list, description="所属组织列表")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub用户资料页面中提取用户信息。
        重点关注：
        1. 基础信息（用户名、显示名称、头像、简介）
        2. 位置和工作信息
        3. 联系方式（网站、社交媒体）
        4. 统计数据（关注者、关注数、仓库数、Gist数）
        5. 账户信息（类型、创建时间）
        6. 所属组织列表
        
        统计数据请提取为字符串格式，避免数字解析错误。
        请返回JSON格式的用户信息。"""


# 抽取 Schema 映射
EXTRACTION_SCHEMAS = {
    "user_profile": UserProfileExtractionSchema,
}


def get_extraction_schema(model_type: str) -> BaseModel:
    """根据模型类型获取对应的抽取 Schema"""
    return EXTRACTION_SCHEMAS.get(model_type)