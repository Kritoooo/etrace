from pydantic import Field
from .base import BaseModel


class Activity(BaseModel):
    """GitHub活动数据模型"""
    repositories: str = Field(..., description="存储库的名称")
    date: str = Field(..., description="存储库的创建或更新日期")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从提供的HTML内容中提取GitHub存储库信息。包含存储库名称和日期。"


class Repository(BaseModel):
    """GitHub仓库数据模型"""
    name: str = Field(..., description="仓库名称")
    description: str = Field(default="", description="仓库描述")
    language: str = Field(default="", description="主要编程语言")
    stars: int = Field(default=0, description="星标数")
    forks: int = Field(default=0, description="分支数")
    updated_at: str = Field(..., description="最后更新时间")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从GitHub页面中提取仓库的详细信息，包括名称、描述、语言、星标数、分支数和更新时间。"


class UserProfile(BaseModel):
    """GitHub用户资料数据模型"""
    username: str = Field(..., description="用户名")
    name: str = Field(default="", description="显示名称")
    bio: str = Field(default="", description="个人简介")
    location: str = Field(default="", description="地理位置")
    company: str = Field(default="", description="所属公司")
    followers: int = Field(default=0, description="关注者数量")
    following: int = Field(default=0, description="关注数量")
    public_repos: int = Field(default=0, description="公开仓库数量")
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return "从GitHub用户资料页面中提取用户的基本信息，包括用户名、显示名称、简介、位置、公司和统计数据。"