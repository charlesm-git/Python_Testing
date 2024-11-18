import pytest

from server import loadCompetitions, loadClubs


class TestServer:
    def test_index_page_status_code(self, client):
        response = client.get("/")
        assert response.status_code == 200
        
    def test_points_page_status_code(self, client):
        response = client.get("/points")
        assert response.status_code == 200

    def test_login_success_status_code(self, client):
        response = client.post(
            "/showSummary", data=dict(email="test20@test.co")
        )
        assert response.status_code == 200
        assert b"Welcome" in response.data

    def test_login_bad_input_status_code(self, client):
        response = client.post(
            "/showSummary", data=dict(email="bad-input@test.co")
        )
        assert response.status_code == 200
        assert b"This email was not found in the database" in response.data
        
    def test_app_should_load_competitions_when_started(self, app):
        expected_value = [
            {
                "name": "test_competition_20_places",
                "date": "2024-01-01 10:00:00",
                "numberOfPlaces": 20,
            },
            {
                "name": "test_competition_8_places",
                "date": "2024-01-01 10:00:00",
                "numberOfPlaces": 8,
            },
        ]
        assert app.competitions == expected_value

    def test_app_should_load_clubs_when_started(self, app):
        expected_value = [
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
        assert app.clubs == expected_value

    @pytest.mark.parametrize("input_value", [1, 5, 10, 12])
    def test_can_book_places(self, client, input_value):
        response = client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=input_value,
            ),
            follow_redirects=True,
        )
        assert b"Great-booking complete!" in response.data

    @pytest.mark.parametrize("input_value", [9, 12])
    def test_cant_book_if_not_enough_places_in_competition(
        self, client, input_value
    ):
        response = client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_8_places",
                club="test_club_20_points",
                places=input_value,
            ),
            follow_redirects=True,
        )
        assert (
            b"You are booking more places than the number of places available "
            b"for this competition" in response.data
        )

    @pytest.mark.parametrize("input_value", [6, 10])
    def test_cant_book_if_not_enough_points(self, client, input_value):
        response = client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_5_points",
                places=input_value,
            ),
            follow_redirects=True,
        )
        assert (
            b"You don&#39;t have enough points to book that many places"
            in response.data
        )

    @pytest.mark.parametrize("input_value", [13, 20])
    def test_cant_book_more_than_12_places_single_booking(
        self, client, input_value
    ):
        response = client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=input_value,
            ),
            follow_redirects=True,
        )
        assert (
            b"You can&#39;t purchase more than 12 places per club for a "
            b"competition" in response.data
        )

    @pytest.mark.parametrize("input_value_second_booking", [3, 6, 10])
    def test_cant_book_more_than_12_places_multiple_booking(
        self, client, input_value_second_booking
    ):
        # client.post("/showSummary", data=dict(email="test5@test.co"))
        # First books 10 places
        client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=10,
            ),
            follow_redirects=True,
        )
        # Books 10 places again and check that it is not possible
        response = client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=input_value_second_booking,
            ),
            follow_redirects=True,
        )
        assert (
            b"You can&#39;t purchase more than 12 places per club for a "
            b"competition" in response.data
        )

    def test_competitions_database_updates_after_booking(self, client, app):
        # client.post("/showSummary", data=dict(email="test20@test.co"))
        client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=10,
            ),
            follow_redirects=True,
        )
        expected_value = [
            {
                "name": "test_competition_20_places",
                "date": "2024-01-01 10:00:00",
                "numberOfPlaces": 10,
                "participants": {"test_club_20_points": 10},
            },
            {
                "name": "test_competition_8_places",
                "date": "2024-01-01 10:00:00",
                "numberOfPlaces": 8,
            },
        ]
        app.competitions = loadCompetitions(app.config["COMPETITIONS_DB_PATH"])
        assert app.competitions == expected_value

    def test_clubs_database_updates_after_booking(self, client, app):
        # client.post("/showSummary", data=dict(email="test20@test.co"))
        client.post(
            "/purchasePlaces",
            data=dict(
                competition="test_competition_20_places",
                club="test_club_20_points",
                places=10,
            ),
            follow_redirects=True,
        )
        expected_value = [
            {
                "name": "test_club_20_points",
                "email": "test20@test.co",
                "points": 10,
            },
            {
                "name": "test_club_5_points",
                "email": "test5@test.co",
                "points": 5,
            },
        ]
        app.competitions = loadClubs(app.config["CLUBS_DB_PATH"])
        assert app.competitions == expected_value
