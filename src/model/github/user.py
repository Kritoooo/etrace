"""
GitHub 用户相关数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator, HttpUrl
from ..base import BaseModel


class UserSocialLinks(BaseModel):
    """用户社交链接"""
    website: Optional[HttpUrl] = Field(None, description="个人网站")
    blog: Optional[HttpUrl] = Field(None, description="博客地址")
    twitter: Optional[str] = Field(None, description="Twitter用户名")
    linkedin: Optional[str] = Field(None, description="LinkedIn用户名")
    email: Optional[str] = Field(None, description="邮箱地址")


class UserStats(BaseModel):
    """用户统计信息"""
    followers: int = Field(0, description="关注者数量")
    following: int = Field(0, description="关注数量")
    public_repos: int = Field(0, description="公开仓库数量")
    public_gists: int = Field(0, description="公开Gist数量")
    private_repos: int = Field(0, description="私有仓库数量")
    owned_private_repos: int = Field(0, description="拥有的私有仓库数量")
    total_private_repos: int = Field(0, description="总私有仓库数量")
    collaborators: int = Field(0, description="协作者数量")
    
    def influence_score(self) -> float:
        """计算影响力分数"""
        return (self.followers * 1.0 + 
                self.public_repos * 0.5 + 
                self.public_gists * 0.2)


class UserOrganization(BaseModel):
    """用户所属组织"""
    login: str = Field(..., description="组织登录名")
    name: Optional[str] = Field(None, description="组织名称")
    description: Optional[str] = Field(None, description="组织描述")
    avatar_url: Optional[HttpUrl] = Field(None, description="组织头像URL")
    url: Optional[HttpUrl] = Field(None, description="组织URL")


class UserProfile(BaseModel):
    """GitHub用户资料数据模型"""
    
    # 基本信息
    id: str = Field(..., description="用户唯一标识")
    username: str = Field(..., description="用户名")
    name: Optional[str] = Field(None, description="显示名称")
    bio: Optional[str] = Field(None, description="个人简介")
    avatar_url: Optional[HttpUrl] = Field(None, description="头像URL")
    gravatar_id: Optional[str] = Field(None, description="Gravatar ID")
    
    # 位置和公司信息
    location: Optional[str] = Field(None, description="地理位置")
    company: Optional[str] = Field(None, description="所属公司")
    
    # 社交链接
    social_links: UserSocialLinks = Field(default_factory=UserSocialLinks, description="社交链接")
    
    # 统计信息
    stats: UserStats = Field(default_factory=UserStats, description="统计信息")
    
    # 组织信息
    organizations: List[UserOrganization] = Field(default_factory=list, description="所属组织列表")
    
    # 账户信息
    type: str = Field("User", description="账户类型")
    site_admin: bool = Field(False, description="是否为站点管理员")
    hireable: Optional[bool] = Field(None, description="是否可雇佣")
    
    # URL信息
    html_url: HttpUrl = Field(..., description="用户主页URL")
    repos_url: Optional[HttpUrl] = Field(None, description="仓库API URL")
    gists_url: Optional[str] = Field(None, description="Gist API URL")
    starred_url: Optional[str] = Field(None, description="星标API URL")
    subscriptions_url: Optional[HttpUrl] = Field(None, description="订阅API URL")
    organizations_url: Optional[HttpUrl] = Field(None, description="组织API URL")
    events_url: Optional[str] = Field(None, description="事件API URL")
    
    # 时间信息
    created_at: datetime = Field(..., description="账户创建时间")
    updated_at: datetime = Field(..., description="最后更新时间")
    
    # 计划信息
    plan: Optional[str] = Field(None, description="GitHub计划类型")
    
    @field_validator('created_at', 'updated_at', mode='before')
    @classmethod
    def parse_datetime(cls, v):
        """解析日期时间"""
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                return datetime.now()
        return v
    
    @classmethod
    def get_extraction_instruction(cls) -> str:
        return """从GitHub用户资料页面中提取用户信息，包括：
        - 基本信息（用户名、显示名称、头像、简介等）
        - 位置和公司信息
        - 统计数据（关注者、关注数、仓库数等）
        - 社交链接（网站、博客、Twitter等）
        - 所属组织信息
        - 账户创建和更新时间
        请以JSON格式返回用户信息。"""
    
    def get_activity_level(self) -> str:
        """获取用户活跃度等级"""
        score = self.stats.influence_score()
        
        if score >= 10000:
            return "Very High"
        elif score >= 1000:
            return "High"
        elif score >= 100:
            return "Medium"
        elif score > 0:
            return "Low"
        else:
            return "New User"
    
    def get_full_name(self) -> str:
        """获取完整名称"""
        if self.name:
            return f"{self.name} ({self.username})"
        return self.username
    
    def has_organization(self, org_name: str) -> bool:
        """检查是否属于指定组织"""
        return any(org.login.lower() == org_name.lower() 
                  for org in self.organizations)
    
    def get_primary_language(self) -> Optional[str]:
        """获取主要编程语言（基于仓库统计）"""
        # 这里需要额外的仓库数据来计算
        # 可以通过分析用户的仓库来确定主要使用的语言
        return None
    
    def account_age_days(self) -> int:
        """获取账户年龄（天数）"""
        delta = datetime.now() - self.created_at.replace(tzinfo=None)
        return delta.days
    
    def is_veteran_user(self, years: int = 5) -> bool:
        """检查是否为资深用户"""
        return self.account_age_days() >= (years * 365)


class UserSearchResult(BaseModel):
    """用户搜索结果"""
    users: List[UserProfile] = Field(default_factory=list, description="用户列表")
    total_count: int = Field(0, description="总数量")
    incomplete_results: bool = Field(False, description="结果是否不完整")
    
    def filter_by_location(self, location: str) -> List[UserProfile]:
        """按位置筛选用户"""
        return [user for user in self.users 
                if user.location and location.lower() in user.location.lower()]
    
    def filter_by_company(self, company: str) -> List[UserProfile]:
        """按公司筛选用户"""
        return [user for user in self.users 
                if user.company and company.lower() in user.company.lower()]
    
    def sort_by_influence(self) -> List[UserProfile]:
        """按影响力排序"""
        return sorted(self.users, 
                     key=lambda u: u.stats.influence_score(), 
                     reverse=True)