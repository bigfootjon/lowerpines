import json
from typing import Dict, Any, Union

import requests
from requests import Response

from lowerpines.gmi import GMI


class Request:
    def __init__(self, gmi: GMI) -> None:
        self.gmi = gmi
        self.result = self.parse(self.execute())

    base_url = "https://api.groupme.com/v3"

    def url(self) -> str:
        raise NotImplementedError

    def mode(self) -> str:
        raise NotImplementedError

    def parse(self, response: dict) -> Any:
        raise NotImplementedError

    def args(self) -> Dict[str, Any]:
        return {}

    def execute(self) -> Union[None, dict]:
        params = {}
        headers = {'X-Access-Token': self.gmi.api_key, 'User-Agent': 'GroupYouLibrary/1.0'}
        if self.mode() == "GET":
            params.update(self.args())
            r = requests.get(url=self.url(), params=params, headers=headers)
        elif self.mode() == "POST":
            r = requests.post(url=self.url(), params=params, headers=headers, data=json.dumps(self.args()))
        else:
            raise Exception("Invalid mode!")
        self.error_check(r)
        if r.content.decode('utf-8').isspace():
            return None
        else:
            return r.json()["response"]

    def error_check(self, request: Response) -> None:
        code = int(request.status_code)
        if 399 < code < 500:
            # noinspection PyBroadException
            try:
                text = '(JSON): ' + str(request.json()['meta']['errors'])
            except:
                text = '(TEXT): ' + str(request.text)
            raise Exception('Something has gone wrong ' + text + ' for ' + str(self.mode()) + ' ' + str(self.url()) + ' with data:\n' + str(self.args()))
