from locust import HttpUser, task
from urllib.parse import urlencode


class AppPerfTest(HttpUser):
    @task
    def index(self):
        self.client.get("/")

    @task
    def points(self):
        self.client.get("/points")

    @task
    def summary(self):
        self.client.post("/showSummary", {"email": "test20@test.co"})

    @task
    def book(self):
        self.client.get("/book/test_competition_20_place/test_club_20_points")
