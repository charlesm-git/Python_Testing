import pytest


class TestServer:
    def test_index_page_status_code(self, client):
        response = client.get("/")
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
