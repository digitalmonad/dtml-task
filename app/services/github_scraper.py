import logging
import time
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.db import insert_event

logger = logging.getLogger(__name__)
import logging

from apscheduler.events import EVENT_JOB_ERROR, EVENT_JOB_EXECUTED
from apscheduler.schedulers.background import BackgroundScheduler

from app.db import engine

logger = logging.getLogger(__name__)

ITEMS_PER_PAGE = 100
PAGES = 1
SCRAPE_INTERVAL = 60


class GitHubService:
    def __init__(self):
        # Scheduler instance
        self.scheduler = BackgroundScheduler()

    def start_scheduler(self) -> None:
        """Start the scheduler for GitHub events scraping."""
        self.scheduler.add_job(self.job, "interval", seconds=SCRAPE_INTERVAL)
        self.scheduler.add_listener(
            self.job_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR,
        )
        self.scheduler.start()
        logger.info("Scheduler started for GitHub scraping.")

    def job(self) -> None:
        """Job to fetch and store events from GitHub."""
        with Session(engine) as session:
            self.fetch_and_store_events(session)
        logger.info("Fetched and stored events from GitHub.")

    def job_listener(self, event) -> None:
        """Listener to log the status of each job execution."""
        if event.exception:
            logger.error(f"Job {event.job_id} failed")
        else:
            logger.info(f"Job {event.job_id} completed successfully.")

    def stop_scheduler(self) -> None:
        """Stop the scheduler."""
        self.scheduler.shutdown()
        logger.info("Scheduler stopped.")

    def fetch_and_store_events(self, session: Session) -> None:
        """Fetch events from the GitHub API and store them in the database."""
        url = "https://api.github.com/events"
        headers = {"Accept": "application/vnd.github.v3+json"}

        page = 1
        events_fetched = 0

        while page <= PAGES:  # Continue until the desired number of pages is processed
            params = {"per_page": ITEMS_PER_PAGE, "page": page}

            try:
                response = requests.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=10,
                )
                response.raise_for_status()  # Check for HTTP errors

                events = response.json()

                if not events:
                    logger.info(f"Page {page} returned no events.")
                    break  # Stop if the page contains no events

                # Store each event in the database
                for event in events:
                    if event["type"] in [
                        "WatchEvent",
                        "PullRequestEvent",
                        "IssuesEvent",
                    ]:
                        insert_event(
                            session,
                            event["id"],
                            event["type"],
                            event["repo"]["name"],
                            datetime.strptime(
                                event["created_at"],
                                "%Y-%m-%dT%H:%M:%SZ",
                            ).isoformat(),
                        )

                events_fetched += len(events)
                logger.info(
                    f"Fetched and stored {len(events)} events from page {page}.",
                )

                time.sleep(1)
                # Move to the next page
                page += 1

            except requests.RequestException as e:
                logger.error(
                    f"Failed to fetch events from GitHub API on page {page}: {e}",
                )
                break  # Stop if there is an error

        logger.info(f"Total events fetched and stored: {events_fetched}")
