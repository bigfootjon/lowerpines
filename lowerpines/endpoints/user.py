from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.endpoints.sms import SmsCreateRequest, SmsDeleteRequest


class User(AbstractObject, RetrievableObject):
    user_id = Field()
    phone_number = Field()
    image_url = Field()
    name = Field()
    created_at = Field()
    updated_at = Field()
    email = Field()
    sms = Field()

    def __init__(self, gmi):
        self.gmi = gmi

    def save(self):
        new_data = UserUpdateRequest(self.gmi, self.image_url, self.name, self.email).result
        self._refresh_from_other(new_data)

    def refresh(self):
        new_data = UserMeRequest(self.gmi).result
        self._refresh_from_other(new_data)

    @classmethod
    def get(cls, gmi):
        user = cls(gmi)
        user.refresh()
        return user

    def enable_sms(self, duration, registration_id):
        SmsCreateRequest(self.gmi, duration, registration_id)

    def disable_sms(self):
        SmsDeleteRequest(self.gmi)


class UserMeRequest(Request):
    def mode(self):
        return "GET"

    def parse(self, response):
        return User.from_json(self.gmi, response)

    def url(self):
        return self.base_url + '/users/me'


class UserUpdateRequest(Request):
    def __init__(self, gmi, avatar_url=None, name=None, email=None, zip_code=None):
        self.avatar_url = avatar_url
        self.name = name
        self.email = email
        self.zip_code = zip_code
        super().__init__(gmi)

    def mode(self):
        return "POST"

    def parse(self, response):
        return User.from_json(self.gmi, response)

    def url(self):
        return self.base_url + '/users/update'

    def args(self):
        arg_dict = dict()

        if self.avatar_url:
            arg_dict['avatar_url'] = self.avatar_url
        if self.name:
            arg_dict['name'] = self.name
        if self.email:
            arg_dict['email'] = self.email
        if self.zip_code:
            arg_dict['zip_code'] = self.zip_code

        return arg_dict
