"""
GitHub 活动相关数据模型
"""
from typing import Optional, List
from datetime import datetime
from pydantic import Field, field_validator
from ..base import BaseModel
from .enums import ActivityType


class ActivityTarget(BaseModel):
    """活动目标对象（仓库、Issue、PR等）"""
    name: str = Field(..., description="目标名称")
    url: Optional[str] = Field(None, description="目标URL")
    type: str = Field(..., description="目标类型")
    id: Optional[str] = Field(None, description="目标ID")


class ActivityActor(BaseModel):
    """活动执行者"""
    username: str = Field(..., description="用户名")
    display_name: Optional[str] = Field(None, description="显示名称")
    avatar_url: Optional[str] = Field(None, description="头像URL")
    profile_url: Optional[str] = Field(None, description="用户资料页URL")


class ActivityPayload(BaseModel):
    """活动负载数据"""
    commit_count: Optional[int] = Field(None, description="提交数量")
    commits: Optional[List[str]] = Field(None, description="提交哈希列表")
    branch: Optional[str] = Field(None, description="分支名称")
    ref: Optional[str] = Field(None, description="引用名称")
    ref_type: Optional[str] = Field(None, description="引用类型")
    description: Optional[str] = Field(None, description="描述信息")
    size: Optional[int] = Field(None, description="大小")


class Activity(BaseModel):
    """GitHub活动数据模型"""
    
    # 基本信息
    id: str = Field(..., description="活动唯一标识")
    type: ActivityType = Field(..., description="活动类型")
    created_at: datetime = Field(..., description="活动创建时间")
    updated_at: Optional[datetime] = Field(None, description="活动更新时间")
    
    # 执行者信息
    actor: ActivityActor = Field(..., description="活动执行者")
    
    # 目标信息
    repository: ActivityTarget = Field(..., description="相关仓库")
    target: Optional[ActivityTarget] = Field(None, description="活动目标对象")
    
    # 活动详情
    payload: Optional[ActivityPayload] = Field(None, description="活动负载数据")
    public: bool = Field(True, description="是否为公开活动")
    
    # 元数据
    organization: Optional[str] = Field(None, description="所属组织")
    visibility: str = Field("public", description="可见性")
    
    @field_validator('type', mode='before')
    @classmethod
    def validate_activity_type(cls, v):
        """验证活动类型"""
        if isinstance(v, str):
            try:
                return ActivityType(v.lower())
            except ValueError:
                return ActivityType.UNKNOWN
        return v
    
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
        return """从GitHub活动页面中提取活动信息，包括：
        - 活动类型（push、pull_request、issue等）
        - 活动时间
        - 执行者信息（用户名、头像等）
        - 相关仓库信息
        - 活动详情（提交数量、分支、描述等）
        请以JSON格式返回活动列表。"""
    
    def get_summary(self) -> str:
        """获取活动摘要"""
        actor_name = self.actor.display_name or self.actor.username
        repo_name = self.repository.name
        
        summaries = {
            ActivityType.PUSH: f"{actor_name} pushed to {repo_name}",
            ActivityType.PULL_REQUEST: f"{actor_name} created pull request in {repo_name}",
            ActivityType.ISSUE: f"{actor_name} created issue in {repo_name}",
            ActivityType.STAR: f"{actor_name} starred {repo_name}",
            ActivityType.FORK: f"{actor_name} forked {repo_name}",
            ActivityType.CREATE_REPO: f"{actor_name} created repository {repo_name}",
            ActivityType.RELEASE: f"{actor_name} released in {repo_name}",
            ActivityType.WATCH: f"{actor_name} watched {repo_name}",
            ActivityType.COMMIT: f"{actor_name} committed to {repo_name}",
        }
        
        return summaries.get(self.type, f"{actor_name} performed {self.type} on {repo_name}")


class ActivityStats(BaseModel):
    """活动统计信息"""
    total_activities: int = Field(0, description="总活动数")
    activities_by_type: dict[ActivityType, int] = Field(default_factory=dict, description="按类型分组的活动数")
    most_active_repository: Optional[str] = Field(None, description="最活跃的仓库")
    activity_streak: int = Field(0, description="活动连续天数")
    last_activity_date: Optional[datetime] = Field(None, description="最后活动日期")
    
    @classmethod
    def from_activities(cls, activities: List[Activity]) -> 'ActivityStats':
        """从活动列表生成统计信息"""
        if not activities:
            return cls()
        
        # 按类型统计
        type_counts = {}
        repo_counts = {}
        
        for activity in activities:
            # 类型统计
            if activity.type in type_counts:
                type_counts[activity.type] += 1
            else:
                type_counts[activity.type] = 1
            
            # 仓库统计
            repo_name = activity.repository.name
            if repo_name in repo_counts:
                repo_counts[repo_name] += 1
            else:
                repo_counts[repo_name] = 1
        
        # 找到最活跃的仓库
        most_active_repo = max(repo_counts.items(), key=lambda x: x[1])[0] if repo_counts else None
        
        # 最后活动时间
        last_activity = max(activities, key=lambda x: x.created_at)
        
        return cls(
            total_activities=len(activities),
            activities_by_type=type_counts,
            most_active_repository=most_active_repo,
            last_activity_date=last_activity.created_at
        )