import json

import requests

from lowerpines.exceptions import (
    InvalidOperationException,
    GroupMeApiException,
    TimeoutException,
    UnauthorizedException,
)


class Request:
    def __init__(self, gmi):
        self.gmi = gmi
        self.result = self.parse(self.execute())

    base_url = "https://api.groupme.com/v3"

    def url(self):
        raise NotImplementedError

    def mode(self):
        raise NotImplementedError

    def parse(self, response):
        raise NotImplementedError

    def args(self):
        return {}

    def execute(self):
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

    def error_check(self, request):
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

    def extract_response(self, response):
        response = response.json()["response"]

        json_dump_dir = self.gmi.write_json_to
        if json_dump_dir is not None:
            from test.dump_json import dump_json

            dump_json(json_dump_dir, self, response)

        return response
