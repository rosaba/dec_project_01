from dotenv import load_dotenv
import pytest
from datetime import datetime
from ELT.connectors.collisions_api import CollisionsApiClient
import os

@pytest.fixture
def setup():
    load_dotenv()


def test_collisions_client_one_day():
    app_token = os.environ.get("X-App-Token")
    
    collisions_api_client = CollisionsApiClient(app_token=app_token)

    crash_day = datetime(
        year=2025, month=10, day=2, hour=0, minute=0, second=0
    ).isoformat()

    crash_time = "22:00"

    data = collisions_api_client.get_collisions_of_one_day(
        dataset_id="h9gi-nx95.json", day_date_iso=crash_day, crash_time=crash_time
        )

    assert type(data) == list
    assert len(data) == 2