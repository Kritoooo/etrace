from datetime import datetime
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel, Field


class EventActor(BaseModel):
    id: int
    login: str
    display_login: Optional[str] = None
    gravatar_id: Optional[str] = None
    url: str
    avatar_url: str


class EventRepo(BaseModel):
    id: int
    name: str
    url: str


class EventPayload(BaseModel):
    action: Optional[str] = None
    
    class Config:
        extra = "allow"


class PushEventPayload(EventPayload):
    push_id: Optional[int] = None
    size: Optional[int] = None
    distinct_size: Optional[int] = None
    ref: Optional[str] = None
    head: Optional[str] = None
    before: Optional[str] = None
    commits: Optional[list] = Field(default_factory=list)


class WatchEventPayload(EventPayload):
    action: str = "started"


class CreateEventPayload(EventPayload):
    ref: Optional[str] = None
    ref_type: Optional[str] = None
    master_branch: Optional[str] = None
    description: Optional[str] = None
    pusher_type: Optional[str] = None


class ForkEventPayload(EventPayload):
    forkee: Optional[Dict[str, Any]] = None


class IssuesEventPayload(EventPayload):
    issue: Optional[Dict[str, Any]] = None


class PullRequestEventPayload(EventPayload):
    number: Optional[int] = None
    pull_request: Optional[Dict[str, Any]] = None


class Event(BaseModel):
    
    id: str = Field(description="事件唯一标识符")
    type: str = Field(description="事件类型，如 PushEvent, WatchEvent 等")
    actor: EventActor = Field(description="事件执行者信息")
    repo: EventRepo = Field(description="关联的仓库信息")
    payload: Union[
        PushEventPayload,
        WatchEventPayload, 
        CreateEventPayload,
        ForkEventPayload,
        IssuesEventPayload,
        PullRequestEventPayload,
        EventPayload
    ] = Field(description="事件具体内容")
    public: bool = Field(description="是否为公开事件")
    created_at: datetime = Field(description="事件创建时间")
    org: Optional[Dict[str, Any]] = Field(default=None, description="组织信息")
    
    @classmethod
    def from_api_response(cls, data: Dict[str, Any]) -> "Event":
        payload_data = data.get("payload", {})
        event_type = data.get("type", "")
        
        if event_type == "PushEvent":
            payload = PushEventPayload(**payload_data)
        elif event_type == "WatchEvent":
            payload = WatchEventPayload(**payload_data)
        elif event_type == "CreateEvent":
            payload = CreateEventPayload(**payload_data)
        elif event_type == "ForkEvent":
            payload = ForkEventPayload(**payload_data)
        elif event_type == "IssuesEvent":
            payload = IssuesEventPayload(**payload_data)
        elif event_type == "PullRequestEvent":
            payload = PullRequestEventPayload(**payload_data)
        else:
            payload = EventPayload(**payload_data)
        
        return cls(
            id=data["id"],
            type=data["type"],
            actor=EventActor(**data["actor"]),
            repo=EventRepo(**data["repo"]),
            payload=payload,
            public=data["public"],
            created_at=datetime.fromisoformat(data["created_at"].replace("Z", "+00:00")),
            org=data.get("org")
        )
    
    def get_event_summary(self) -> str:
        actor_name = self.actor.login
        repo_name = self.repo.name
        
        if self.type == "PushEvent":
            commits_count = len(self.payload.commits) if hasattr(self.payload, 'commits') and self.payload.commits else 0
            return f"{actor_name} pushed {commits_count} commit(s) to {repo_name}"
        elif self.type == "WatchEvent":
            return f"{actor_name} starred {repo_name}"
        elif self.type == "CreateEvent":
            ref_type = getattr(self.payload, 'ref_type', 'repository')
            return f"{actor_name} created {ref_type} in {repo_name}"
        elif self.type == "ForkEvent":
            return f"{actor_name} forked {repo_name}"
        elif self.type == "IssuesEvent":
            action = getattr(self.payload, 'action', 'unknown')
            return f"{actor_name} {action} an issue in {repo_name}"
        elif self.type == "PullRequestEvent":
            action = getattr(self.payload, 'action', 'unknown')
            return f"{actor_name} {action} a pull request in {repo_name}"
        else:
            return f"{actor_name} performed {self.type} in {repo_name}"