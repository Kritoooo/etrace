"""
GitHub 仓库相关数据模型
"""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, HttpUrl
from .enums import RepositoryType, RepositoryLanguage


class RepositoryOwner(BaseModel):
    """仓库所有者"""
    username: str = Field(..., description="用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    type: str = Field("User", description="所有者类型（User/Organization）")
    profile_url: Optional[HttpUrl] = Field(None, description="用户资料页URL")


class RepositoryLicense(BaseModel):
    """仓库许可证"""
    key: str = Field(..., description="许可证标识符")
    name: str = Field(..., description="许可证名称")
    spdx_id: Optional[str] = Field(None, description="SPDX标识符")
    url: Optional[HttpUrl] = Field(None, description="许可证URL")


class RepositoryStats(BaseModel):
    """仓库统计信息"""
    stars: int = Field(0, description="星标数")
    forks: int = Field(0, description="派生数")
    watchers: int = Field(0, description="关注者数")
    open_issues: int = Field(0, description="开放的问题数")
    open_pull_requests: int = Field(0, description="开放的PR数")
    contributors: int = Field(0, description="贡献者数")
    commits: int = Field(0, description="提交数")
    branches: int = Field(0, description="分支数")
    releases: int = Field(0, description="发布数")
    
    def popularity_score(self) -> float:
        """计算仓库受欢迎程度分数"""
        return (self.stars * 1.0 + 
                self.forks * 0.8 + 
                self.watchers * 0.6 + 
                self.contributors * 0.5)


class RepositoryTopics(BaseModel):
    """仓库话题标签"""
    topics: List[str] = Field(default_factory=list, description="话题列表")
    
    def has_topic(self, topic: str) -> bool:
        """检查是否包含指定话题"""
        return topic.lower() in [t.lower() for t in self.topics]


class Repository(BaseModel):
    """GitHub仓库数据模型"""
    
    # 基本信息
    id: str = Field(..., description="仓库唯一标识")
    name: str = Field(..., description="仓库名称")
    full_name: str = Field(..., description="完整仓库名称（owner/repo）")
    description: Optional[str] = Field(None, description="仓库描述")
    url: HttpUrl = Field(..., description="仓库URL")
    clone_url: Optional[HttpUrl] = Field(None, description="克隆URL")
    ssh_url: Optional[str] = Field(None, description="SSH克隆URL")
    
    # 所有者信息
    owner: RepositoryOwner = Field(..., description="仓库所有者")
    
    # 仓库属性
    type: RepositoryType = Field(RepositoryType.PUBLIC, description="仓库类型")
    private: bool = Field(False, description="是否为私有仓库")
    fork: bool = Field(False, description="是否为分支仓库")
    archived: bool = Field(False, description="是否已归档")
    disabled: bool = Field(False, description="是否已禁用")
    template: bool = Field(False, description="是否为模板仓库")
    
    # 技术信息
    language: Optional[RepositoryLanguage] = Field(None, description="主要编程语言")
    languages: Dict[str, int] = Field(default_factory=dict, description="语言统计（语言->字节数）")
    size: int = Field(0, description="仓库大小（KB）")
    default_branch: str = Field("main", description="默认分支")
    
    # 许可证和话题
    license: Optional[RepositoryLicense] = Field(None, description="许可证信息")
    topics: RepositoryTopics = Field(default_factory=RepositoryTopics, description="话题标签")
    
    # 统计信息
    stats: RepositoryStats = Field(default_factory=RepositoryStats, description="统计信息")
    
    # 时间信息
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    pushed_at: Optional[datetime] = Field(None, description="最后推送时间")
    
    # 父仓库信息（如果是fork）
    parent: Optional['Repository'] = Field(None, description="父仓库信息")
    source: Optional['Repository'] = Field(None, description="源仓库信息")
    
    @field_validator('language', mode='before')
    @classmethod
    def validate_language(cls, v):
        """验证编程语言"""
        if isinstance(v, str) and v:
            # 尝试匹配已知语言
            v_upper = v.upper()
            for lang in RepositoryLanguage:
                if lang.value.upper() == v_upper:
                    return lang
            return RepositoryLanguage.OTHER
        return v
    
    @field_validator('type', mode='before')
    @classmethod
    def validate_repository_type(cls, v):
        """验证仓库类型"""
        if isinstance(v, str):
            try:
                return RepositoryType(v.lower())
            except ValueError:
                return RepositoryType.PUBLIC
        return v
    
    @field_validator('created_at', 'updated_at', 'pushed_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """解析日期时间"""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()
        return v
    
    
    def is_active(self, days: int = 30) -> bool:
        """检查仓库是否在指定天数内活跃"""
        if not self.pushed_at:
            return False
        delta = datetime.now() - self.pushed_at.replace(tzinfo=None)
        return delta.days <= days
    
    def get_language_percentage(self) -> Dict[str, float]:
        """获取语言使用百分比"""
        if not self.languages:
            return {}
        
        total_bytes = sum(self.languages.values())
        if total_bytes == 0:
            return {}
        
        return {
            lang: (bytes_count / total_bytes) * 100
            for lang, bytes_count in self.languages.items()
        }
    
    def get_activity_level(self) -> str:
        """获取活跃度等级"""
        score = self.stats.popularity_score()
        
        if score >= 1000:
            return "Very High"
        elif score >= 100:
            return "High"
        elif score >= 10:
            return "Medium"
        elif score > 0:
            return "Low"
        else:
            return "Inactive"