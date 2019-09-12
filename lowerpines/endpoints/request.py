import json
from typing import TYPE_CHECKING, Dict, Optional, Generic, TypeVar, Union, NewType

import requests
from requests import Response

from lowerpines.exceptions import (
    InvalidOperationException,
    GroupMeApiException,
    TimeoutException,
    UnauthorizedException,
)

if TYPE_CHECKING:
    from lowerpines.gmi import GMI

T = TypeVar("T")
JSON = NewType("JSON", Dict[str, Union[int, str]])


class Request(Generic[T]):
    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi
        self.result = self.parse(self.execute())

    base_url = "https://api.groupme.com/v3"

    def url(self) -> str:
        raise NotImplementedError

    def mode(self) -> str:
        raise NotImplementedError

    def parse(self, response) -> T:
        raise NotImplementedError

    def args(self):
        return {}

    def execute(self) -> Optional[str]:
        params = {}
        headers = {
            "X-Access-Token": self.gmi.access_token,
            "User-Agent": "GroupYouLibrary/1.0",
        }
        if self.mode() == "GET":
            params.update(self.args())
            r = requests.get(url=self.url(), params=params, headers=headers)
        elif self.mode() == "POST":
            headers["Content-Type"] = "application/json"
            r = requests.post(
                url=self.url(),
                params=params,
                headers=headers,
                data=json.dumps(self.args()),
            )
        elif self.mode() == "POST_RAW":
            r = requests.post(
                url=self.url(), params=params, headers=headers, data=self.args()
            )
        else:
            raise InvalidOperationException()
        self.error_check(r)
        if r.content.decode("utf-8").isspace():
            return None
        else:
            return self.extract_response(r)

    def error_check(self, request: Response) -> None:
        code = int(request.status_code)
        if 399 < code < 500:
            request_string = (
                str(self.mode())
                + " "
                + str(self.url())
                + " with data:\n"
                + str(self.args())
            )
            try:
                errors = request.json()["meta"]["errors"]
                if "request timeout" in errors:
                    raise TimeoutException("Timeout for " + request_string)
                elif "unauthorized" in errors:
                    raise UnauthorizedException(
                        "Not authorized to perform " + request_string
                    )
                text = "(JSON): " + str(errors)
            except ValueError:
                text = "(TEXT): " + str(request.text)
            raise GroupMeApiException(
                "Unknown error " + text + " for " + request_string
            )

    def extract_response(self, response: Response):
        return response.json()["response"]
