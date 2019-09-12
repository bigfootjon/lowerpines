# pyre-strict
from typing import Dict, TYPE_CHECKING, Union

from requests import Response

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.endpoints.sms import SmsCreateRequest, SmsDeleteRequest

if TYPE_CHECKING:
    from lowerpines.gmi import GMI


class User(AbstractObject, RetrievableObject):
    user_id = Field()
    phone_number = Field()
    image_url = Field()
    name = Field()
    created_at = Field()
    updated_at = Field()
    email = Field()
    sms = Field()

    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi

    def save(self) -> None:
        # pyre-ignore
        new_data = UserUpdateRequest(
            self.gmi, self.image_url, self.name, self.email
        ).result
        self._refresh_from_other(new_data)

    def refresh(self) -> None:
        new_data = UserMeRequest(self.gmi).result
        self._refresh_from_other(new_data)

    @classmethod
    def get(cls, gmi: "GMI") -> "User":
        user = cls(gmi)
        user.refresh()
        return user

    def enable_sms(self, duration: int, registration_id: str) -> None:
        SmsCreateRequest(self.gmi, duration, registration_id)

    def disable_sms(self) -> None:
        SmsDeleteRequest(self.gmi)


class UserMeRequest(Request[User]):
    def mode(self) -> str:
        return "GET"

    def parse(self, response: Dict[str, Union[str, int]]) -> User:
        return User.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/users/me"


class UserUpdateRequest(Request[User]):
    avatar_url: str
    name: str
    email: str
    zip_code = str

    def __init__(self, gmi: "GMI", avatar_url: str, name: str, email: str) -> None:
        self.avatar_url = avatar_url
        self.name = name
        self.email = email
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def parse(self, response: Dict[str, Union[str, int]]) -> User:
        return User.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/users/update"

    def args(self) -> Dict[str, Union[int, str]]:
        arg_dict = dict()

        if self.avatar_url:
            arg_dict["avatar_url"] = self.avatar_url
        if self.name:
            arg_dict["name"] = self.name
        if self.email:
            arg_dict["email"] = self.email

        return arg_dict
