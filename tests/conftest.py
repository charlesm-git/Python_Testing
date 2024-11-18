import json
import pytest
from server import create_app


@pytest.fixture
def temp_competition_db(tmp_path):
    temp_competition_file = tmp_path / "test_competition_db.json"

    initial_competition_data = {
        "competitions": [
            {
                "name": "test_old_competition",
                "date": "2000-01-01 10:00:00",
                "numberOfPlaces": 20,
            },
            {
                "name": "test_competition_20_places",
                "date": "2100-01-01 10:00:00",
                "numberOfPlaces": 20,
            },
            {
                "name": "test_competition_8_places",
                "date": "2100-01-01 10:00:00",
                "numberOfPlaces": 8,
            },
        ]
    }
    temp_competition_file.write_text(json.dumps(initial_competition_data))

    yield str(temp_competition_file)


@pytest.fixture
def temp_club_db(tmp_path):
    temp_club_file = tmp_path / "test_club_db.json"

    initial_club_data = {
        "clubs": [
            {
                "name": "test_club_20_points",
                "email": "test20@test.co",
                "points": 20,
            },
            {
                "name": "test_club_5_points",
                "email": "test5@test.co",
                "points": 5,
            },
        ]
    }
    temp_club_file.write_text(json.dumps(initial_club_data))

    yield str(temp_club_file)


@pytest.fixture
def app(temp_club_db, temp_competition_db):
    config = {
        "TESTING": True,
        "COMPETITIONS_DB_PATH": temp_competition_db,
        "CLUBS_DB_PATH": temp_club_db,
    }
    app = create_app(config)
    return app


@pytest.fixture
def client(app):
    with app.test_client() as client:
        yield client
