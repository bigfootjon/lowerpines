from typing import Any, Dict

from lowerpines.gmi import GMI
from lowerpines.endpoints.request import Request


class SmsCreateRequest(Request):
    def __init__(self, gmi: GMI, duration: int, registration_id: str) -> None:
        if duration > 48:
            raise ValueError('Cannot have a duration of SMS mode for more than 48 hours')
        self.duration = duration
        self.registration_id = registration_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def parse(self, response: dict) -> Any:
        return None

    def args(self) -> Dict[str, Any]:
        return {
            'duration': self.duration,
            'registration_id': self.registration_id
        }

    def url(self) -> str:
        return self.base_url + "/users/sms_mode"


class SmsDeleteRequest(Request):
    def mode(self) -> str:
        return "POST"

    def parse(self, response: dict) -> Any:
        return None

    def url(self) -> str:
        return self.base_url + '/users/sms_mode/delete'
