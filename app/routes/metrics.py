import io
import logging
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db import get_event_count_since, get_pull_request_times, get_session
from app.validations.schemas import (
    AvgPullRequestTimeResponse,
    EventCountResponse,
    EventType,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/metrics")


@router.get(
    "/events/PullRequest/average-time-between/{user_name}/{repo_name}",
    response_model=AvgPullRequestTimeResponse,
)
def avg_pull_request_time(
    user_name: str,
    repo_name: str,
    session: Session = Depends(get_session),
) -> AvgPullRequestTimeResponse:
    logger.info(f"Received request for avg_pull_request_time for {repo_name}")
    pr_times = get_pull_request_times(session, user_name, repo_name)

    if len(pr_times) < 2:
        raise HTTPException(
            status_code=400,
            detail="Not enough data for a given metric.",
        )

    time_diffs = [
        (pr_times[i + 1] - pr_times[i]).total_seconds()
        for i in range(len(pr_times) - 1)
    ]
    avg_time = sum(time_diffs) / len(time_diffs)

    return AvgPullRequestTimeResponse(average_time_seconds=avg_time)


@router.get(
    "/events/{event_type}/count/{offset}",
    response_model=EventCountResponse,
)
def event_count(
    event_type: str,
    offset: int,
    session: Session = Depends(get_session),
) -> EventCountResponse:
    logger.info(f"Received request for event_counts with offset {offset}")

    if event_type not in EventType.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Allowed values are: {', '.join(EventType.__members__.keys())}",
        )

    cutoff = datetime.now() - timedelta(minutes=offset)
    count = get_event_count_since(session, cutoff, event_type)

    return EventCountResponse(
        count=count.get(event_type, 0),
    )


@router.get("/events/{event_type}/count/{offset}/visualization")
def visualize_event_counts(
    event_type: str,
    offset: int,
    session: Session = Depends(get_session),
) -> Response:
    logger.info("Received request for visualize_event_counts")

    if event_type not in EventType.__members__:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid event_type. Allowed values are: {', '.join(EventType.__members__.keys())}",
        )

    cutoff = datetime.now() - timedelta(minutes=offset)
    counts = get_event_count_since(session, cutoff, event_type)

    if event_type not in counts:
        counts[event_type] = 0

    plt.bar([event_type], [counts.get(event_type, 0)])
    plt.title(f"Event Count for {event_type} (Last {offset} Minutes)")
    plt.xlabel("(Event Type)")
    plt.ylabel("Count")

    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    plt.close()

    return Response(content=img.getvalue(), media_type="image/png")
