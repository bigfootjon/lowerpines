# pyre-strict
import json
from typing import TypeVar, Generic, TYPE_CHECKING, Optional, Dict, Any, Union

import requests
from requests import Response

from lowerpines.exceptions import (
    InvalidOperationException,
    GroupMeApiException,
    TimeoutException,
    UnauthorizedException,
)

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI

T = TypeVar("T")

# TODO Model JSON better
JsonType = Dict[str, Any]


class Request(Generic[T]):
    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi
        nullable_result = self.execute()
        if nullable_result is not None:
            self.result: T = self.parse(nullable_result)
        else:
            json_dump_dir = self.gmi.write_json_to
            if json_dump_dir is not None:
                from test.dump_json import dump_json

                dump_json(json_dump_dir, self, nullable_result)

    base_url = "https://api.groupme.com/v3"

    def url(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def mode(self) -> str:
        raise NotImplementedError  # pragma: no cover

    def parse(self, response: JsonType) -> T:
        raise NotImplementedError  # pragma: no cover

    def args(self) -> Union[JsonType, bytes]:
        return {}

    def execute(self) -> Optional[JsonType]:
        params = {}
        headers = {
            "X-Access-Token": self.gmi.access_token,
            "User-Agent": "GroupYouLibrary/1.0",
        }
        args = self.args()
        if self.mode() == "GET" and isinstance(args, dict):
            params.update(args)
            r = requests.get(url=self.url(), params=params, headers=headers)
        elif self.mode() == "POST" and isinstance(args, dict):
            headers["Content-Type"] = "application/json"
            r = requests.post(
                url=self.url(),
                params=params,
                headers=headers,
                data=json.dumps(self.args()),
            )
        elif self.mode() == "POST_RAW" and isinstance(args, bytes):
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

    def extract_response(self, response: Response) -> JsonType:
        response = response.json()["response"]

        json_dump_dir = self.gmi.write_json_to
        if json_dump_dir is not None:
            from test.dump_json import dump_json

            dump_json(json_dump_dir, self, response)

        return response  # type: ignore
