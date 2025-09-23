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


class IssueCommentEventPayload(EventPayload):
    issue: Optional[Dict[str, Any]] = None
    comment: Optional[Dict[str, Any]] = None


class CommitCommentEventPayload(EventPayload):
    comment: Optional[Dict[str, Any]] = None


class PullRequestReviewEventPayload(EventPayload):
    pull_request: Optional[Dict[str, Any]] = None
    review: Optional[Dict[str, Any]] = None


class PullRequestReviewCommentEventPayload(EventPayload):
    pull_request: Optional[Dict[str, Any]] = None
    comment: Optional[Dict[str, Any]] = None


class DeleteEventPayload(EventPayload):
    ref: Optional[str] = None
    ref_type: Optional[str] = None
    pusher_type: Optional[str] = None


class ReleaseEventPayload(EventPayload):
    release: Optional[Dict[str, Any]] = None


class GollumEventPayload(EventPayload):
    pages: Optional[list] = Field(default_factory=list)


class MemberEventPayload(EventPayload):
    member: Optional[Dict[str, Any]] = None


class PublicEventPayload(EventPayload):
    pass


class SponsorshipEventPayload(EventPayload):
    sponsorship: Optional[Dict[str, Any]] = None


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
        IssueCommentEventPayload,
        CommitCommentEventPayload,
        PullRequestReviewEventPayload,
        PullRequestReviewCommentEventPayload,
        DeleteEventPayload,
        ReleaseEventPayload,
        GollumEventPayload,
        MemberEventPayload,
        PublicEventPayload,
        SponsorshipEventPayload,
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
        elif event_type == "IssueCommentEvent":
            payload = IssueCommentEventPayload(**payload_data)
        elif event_type == "CommitCommentEvent":
            payload = CommitCommentEventPayload(**payload_data)
        elif event_type == "PullRequestReviewEvent":
            payload = PullRequestReviewEventPayload(**payload_data)
        elif event_type == "PullRequestReviewCommentEvent":
            payload = PullRequestReviewCommentEventPayload(**payload_data)
        elif event_type == "DeleteEvent":
            payload = DeleteEventPayload(**payload_data)
        elif event_type == "ReleaseEvent":
            payload = ReleaseEventPayload(**payload_data)
        elif event_type == "GollumEvent":
            payload = GollumEventPayload(**payload_data)
        elif event_type == "MemberEvent":
            payload = MemberEventPayload(**payload_data)
        elif event_type == "PublicEvent":
            payload = PublicEventPayload(**payload_data)
        elif event_type == "SponsorshipEvent":
            payload = SponsorshipEventPayload(**payload_data)
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
        elif self.type == "IssueCommentEvent":
            action = getattr(self.payload, 'action', 'created')
            issue_number = ""
            if hasattr(self.payload, 'issue') and self.payload.issue:
                issue_number = f" #{self.payload.issue.get('number', '')}"
            return f"{actor_name} {action} comment on issue{issue_number} in {repo_name}"
        elif self.type == "CommitCommentEvent":
            return f"{actor_name} commented on commit in {repo_name}"
        elif self.type == "PullRequestReviewEvent":
            action = getattr(self.payload, 'action', 'submitted')
            pr_number = ""
            if hasattr(self.payload, 'pull_request') and self.payload.pull_request:
                pr_number = f" #{self.payload.pull_request.get('number', '')}"
            return f"{actor_name} {action} review for PR{pr_number} in {repo_name}"
        elif self.type == "PullRequestReviewCommentEvent":
            action = getattr(self.payload, 'action', 'created')
            pr_number = ""
            if hasattr(self.payload, 'pull_request') and self.payload.pull_request:
                pr_number = f" #{self.payload.pull_request.get('number', '')}"
            return f"{actor_name} {action} review comment on PR{pr_number} in {repo_name}"
        elif self.type == "DeleteEvent":
            ref_type = getattr(self.payload, 'ref_type', 'branch')
            ref = getattr(self.payload, 'ref', '')
            return f"{actor_name} deleted {ref_type} {ref} in {repo_name}"
        elif self.type == "ReleaseEvent":
            action = getattr(self.payload, 'action', 'published')
            tag_name = ""
            if hasattr(self.payload, 'release') and self.payload.release:
                tag_name = self.payload.release.get('tag_name', '')
            return f"{actor_name} {action} release {tag_name} in {repo_name}"
        elif self.type == "GollumEvent":
            pages_count = len(getattr(self.payload, 'pages', []))
            return f"{actor_name} updated {pages_count} wiki page(s) in {repo_name}"
        elif self.type == "MemberEvent":
            action = getattr(self.payload, 'action', 'added')
            member_name = ""
            if hasattr(self.payload, 'member') and self.payload.member:
                member_name = self.payload.member.get('login', '')
            return f"{actor_name} {action} {member_name} as member to {repo_name}"
        elif self.type == "PublicEvent":
            return f"{actor_name} made {repo_name} public"
        elif self.type == "SponsorshipEvent":
            action = getattr(self.payload, 'action', 'created')
            return f"{actor_name} {action} sponsorship"
        else:
            return f"{actor_name} performed {self.type} in {repo_name}"