from enum import Enum

from pydantic import BaseModel


class EventType(str, Enum):
    WatchEvent = "WatchEvent"
    PullRequestEvent = "PullRequestEvent"
    IssuesEvent = "IssuesEvent"


class EventSchema(BaseModel):
    id: str
    event_type: str
    repo_name: str
    created_at: str


class AvgPullRequestTimeResponse(BaseModel):
    average_time_seconds: float


class EventCountResponse(BaseModel):
    count: int
