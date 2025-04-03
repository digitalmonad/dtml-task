import logging
import os
from collections.abc import Iterator
from datetime import datetime
from typing import List

from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session

from .models import Base, Event

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///database.db")

# SQLAlchemy setup
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Initialize the database and create tables."""
    Base.metadata.create_all(engine)
    print("✅ Database initialized")


def get_session() -> Iterator:
    """Provide a database session for dependency injection."""
    with Session(engine) as session:
        yield session


def insert_event(
    session: Session,
    event_id: str,
    event_type: str,
    repo_name: str,
    created_at: str,
) -> None:
    """Insert a new event into the database."""
    event = Event(
        id=event_id,
        event_type=event_type,
        repo_name=repo_name,
        created_at=created_at,
    )
    session.merge(event)
    session.commit()
    logger.debug(f"Inserted event: {event_id}")


def get_pull_request_times(
    session: Session,
    user_name: str,
    repo_name: str,
) -> List[datetime]:
    """Retrieve timestamps of PullRequestEvents for a given repository."""
    events = (
        session.query(Event)
        .filter(
            Event.event_type == "PullRequestEvent",
            Event.repo_name == f"{user_name}/{repo_name}",
        )
        .order_by(Event.created_at)
        .all()
    )

    print(events)

    times = [datetime.fromisoformat(event.created_at) for event in events]
    logger.debug(f"Retrieved {len(times)} pull request times for {repo_name}")
    return times


def get_event_count_since(
    session: Session,
    cutoff: datetime,
    event_type: str = None,
) -> dict:
    """Get counts of events by type since a given cutoff time, optionally filtering by event_type."""
    query = session.query(Event).filter(Event.created_at >= cutoff)

    if event_type:
        query = query.filter(Event.event_type == event_type)

    event_counts = (
        query.with_entities(Event.event_type, func.count().label("count"))
        .group_by(Event.event_type)
        .all()
    )

    print(event_counts)

    counts = {event_type: count for event_type, count in event_counts}
    return counts
