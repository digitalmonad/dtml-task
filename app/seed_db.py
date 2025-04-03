import logging
from datetime import datetime, timedelta

from faker import Faker
from sqlalchemy.orm import Session

from app.db import Event, engine, init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def seed_database() -> None:
    """Seed the database with 600 demo events using Faker."""
    faker = Faker()
    event_types = ["WatchEvent", "PullRequestEvent", "IssuesEvent"]
    repo_names = ["demo/repo1", "demo/repo2", "test/repo3", "example/repo4"]
    now = datetime.now()

    with Session(engine) as session:
        for i in range(600):
            event = Event(
                id=faker.uuid4(),
                event_type=faker.random_element(event_types),
                repo_name=faker.random_element(repo_names),
                created_at=(
                    now - timedelta(minutes=faker.random_int(min=1, max=40))
                ).isoformat(),
            )
            session.merge(event)

        session.commit()
        logger.info("Database seeded with 600 demo events using Faker.")


if __name__ == "__main__":
    init_db()
    print("Seeding...")
    seed_database()
