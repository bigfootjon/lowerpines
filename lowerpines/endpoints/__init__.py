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
        headers = {'X-Access-Token': self.gmi.api_key, 'User-Agent': 'GroupYouLibrary/1.0'}
        if self.mode() == "GET":
            params.update(self.args())
            r = requests.get(url=self.url(), params=params, headers=headers)
        elif self.mode() == "POST":
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


class AbstractObject:
    field_map = {}  # This is a dict of keys to values using: AbstractObject.KEY = json[VALUE]

    def save(self):
        raise NotImplementedError

    def _refresh_from_other(self, other):
        for key, _ in self.field_map.items():
            setattr(self, key, getattr(other, key))
        self.on_fields_loaded()

    def on_fields_loaded(self):
        pass

    def refresh(self):
        raise NotImplementedError

    @staticmethod
    def get(gmi, *args):
        raise NotImplementedError

    @classmethod
    def from_json(cls, gmi, json, *args):
        obj = cls(gmi, *args)

        for key, value_raw in obj.field_map.items():
            json_val = json
            for val in value_raw.split('.'):
                json_val = json_val.get(val, None)
            setattr(obj, key, json_val)
        obj.on_fields_loaded()
        return obj
