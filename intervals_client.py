import requests

import config

BASE_URL = "https://intervals.icu/api/v1"


class IntervalsClient:
    def __init__(self, api_key=None, athlete_id=None):
        self.api_key = api_key or config.INTERVALS_ICU_API_KEY
        self.athlete_id = athlete_id or config.INTERVALS_ICU_ATHLETE_ID
        self.session = requests.Session()
        self.session.auth = ("API_KEY", self.api_key)

    def _athlete_url(self, path):
        return f"{BASE_URL}/athlete/{self.athlete_id}{path}"

    def get_athlete(self):
        response = self.session.get(self._athlete_url(""))
        response.raise_for_status()
        return response.json()

    def get_wellness(self, oldest, newest):
        response = self.session.get(
            self._athlete_url("/wellness"),
            params={"oldest": oldest, "newest": newest},
        )
        response.raise_for_status()
        return response.json()

    def get_activities(self, oldest, newest):
        response = self.session.get(
            self._athlete_url("/activities"),
            params={"oldest": oldest, "newest": newest},
        )
        response.raise_for_status()
        return response.json()

    def get_events(self, oldest, newest):
        response = self.session.get(
            self._athlete_url("/events"),
            params={"oldest": oldest, "newest": newest},
        )
        response.raise_for_status()
        return response.json()

    def create_event(self, event):
        response = self.session.post(self._athlete_url("/events"), json=event)
        response.raise_for_status()
        return response.json()

    def update_event(self, event_id, event):
        response = self.session.put(
            self._athlete_url(f"/events/{event_id}"), json=event
        )
        response.raise_for_status()
        return response.json()
