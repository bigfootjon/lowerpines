import json

import requests

from lowerpines.exceptions import InvalidOperationException, GroupMeApiException


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
        headers = {'X-Access-Token': self.gmi.access_token, 'User-Agent': 'GroupYouLibrary/1.0'}
        if self.mode() == "GET":
            params.update(self.args())
            r = requests.get(url=self.url(), params=params, headers=headers)
        elif self.mode() == "POST":
            headers['Content-Type'] = 'application/json'
            r = requests.post(url=self.url(), params=params, headers=headers, data=json.dumps(self.args()))
        elif self.mode() == "POST_RAW":
            r = requests.post(url=self.url(), params=params, headers=headers, data=self.args())
        else:
            raise InvalidOperationException()
        self.error_check(r)
        if r.content.decode('utf-8').isspace():
            return None
        else:
            return r.json()["response"]

    def error_check(self, request):
        code = int(request.status_code)
        if 399 < code < 500:
            # noinspection PyBroadException
            try:
                text = '(JSON): ' + str(request.json()['meta']['errors'])
            except:
                text = '(TEXT): ' + str(request.text)
            raise GroupMeApiException('Something has gone wrong ' + text + ' for ' + str(self.mode()) + ' ' + str(
                self.url()) + ' with data:\n' + str(self.args()))
