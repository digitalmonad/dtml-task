from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Event(Base):
    """Database model for GitHub events."""

    __tablename__ = "events"

    id = Column(String, primary_key=True, nullable=False)
    event_type = Column(String, nullable=False)
    repo_name = Column(String, nullable=False)
    created_at = Column(String, nullable=False)
