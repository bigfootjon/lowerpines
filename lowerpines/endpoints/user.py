# pyre-strict
from typing import Optional, TYPE_CHECKING

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.endpoints.sms import SmsCreateRequest, SmsDeleteRequest

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI


class User(AbstractObject, RetrievableObject):
    user_id: str = Field().with_type(str)
    phone_number: str = Field().with_type(str)
    image_url: str = Field().with_type(str)
    name: str = Field().with_type(str)
    created_at: int = Field().with_type(int)
    updated_at: int = Field().with_type(int)
    email: str = Field().with_type(str)
    sms: bool = Field().with_type(bool)

    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi

    def save(self) -> None:
        new_data = UserUpdateRequest(
            self.gmi, self.image_url, self.name, self.email
        ).result
        self._refresh_from_other(new_data)

    def refresh(self) -> None:
        new_data = UserMeRequest(self.gmi).result
        self._refresh_from_other(new_data)

    @classmethod
    def get(cls, gmi: "GMI") -> "User":  # type: ignore
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

    def parse(self, response: JsonType) -> User:
        return User.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/users/me"


class UserUpdateRequest(Request[User]):
    def __init__(
        self,
        gmi: "GMI",
        avatar_url: Optional[str] = None,
        name: Optional[str] = None,
        email: Optional[str] = None,
        zip_code: Optional[str] = None,
    ) -> None:
        self.avatar_url = avatar_url
        self.name = name
        self.email = email
        self.zip_code = zip_code
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def parse(self, response: JsonType) -> User:
        return User.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/users/update"

    def args(self) -> JsonType:
        arg_dict = dict()

        if self.avatar_url:
            arg_dict["avatar_url"] = self.avatar_url
        if self.name:
            arg_dict["name"] = self.name
        if self.email:
            arg_dict["email"] = self.email
        if self.zip_code:
            arg_dict["zip_code"] = self.zip_code

        return arg_dict
