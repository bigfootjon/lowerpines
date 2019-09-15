# pyre-strict
from typing import TYPE_CHECKING, List, Optional

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.exceptions import InvalidOperationException

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI


class Member(AbstractObject, RetrievableObject):
    member_id: str = Field().with_api_name("id").with_type(str)
    user_id: str = Field().with_type(str)
    nickname: str = Field().with_type(str)
    muted: bool = Field().with_type(bool)
    image_url: Optional[str] = Field().with_type(str)
    autokicked: bool = Field().with_type(bool)
    app_installed: bool = Field().with_type(bool)
    guid: str = Field().with_type(str)
    phone_number: str = Field().with_type(str)
    email: str = Field().with_type(str)

    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        nickname: Optional[str] = None,
        user_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id  # type: ignore
        self.nickname = nickname  # type: ignore
        self.user_id = user_id  # type: ignore
        self.phone_number = phone_number  # type: ignore
        self.email = email  # type: ignore

    def save(self) -> None:
        if self.member_id is None:
            if self.user_id is not None:
                MembersAddRequest(
                    self.gmi, self.group_id, self.nickname, user_id=self.user_id
                )
            elif self.phone_number is not None:
                MembersAddRequest(
                    self.gmi,
                    self.group_id,
                    self.nickname,
                    phone_number=self.phone_number,
                )
            elif self.email is not None:
                MembersAddRequest(
                    self.gmi, self.group_id, self.nickname, email=self.email
                )
            else:
                raise ValueError(
                    "Please define one of user_id, phone_number, email before saving"
                )
        else:  # Only works for current user
            new_data = MembersUpdateRequest(
                self.gmi, self.group_id, self.nickname
            ).result
            self._refresh_from_other(new_data)

    def refresh(self) -> None:
        raise InvalidOperationException("Nontrivial to implement")

    @staticmethod
    def get(gmi: "GMI", member_id: str) -> None:  # type: ignore
        raise InvalidOperationException("Nontrivial to implement")

    def __str__(self) -> str:
        return self.nickname

    def __repr__(self) -> str:
        return str(self)


class MembersAddRequest(Request[str]):
    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        nickname: str,
        user_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
        guid: Optional[str] = None,
    ) -> None:
        self.group_id = group_id
        self.nickname = nickname
        self.guid = guid

        self.user_id = user_id
        self.email = email
        self.phone_number = phone_number

        if user_id is None and email is not None and phone_number is not None:
            raise ValueError("Must provide user_id, email, or phone_number")
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/members/add"

    def args(self) -> JsonType:
        add_dict = {"members": [{"nickname": self.nickname, "user_id": self.user_id}]}
        return add_dict

    def mode(self) -> str:
        return "POST"

    def parse(self, response: JsonType) -> str:
        return response["results_id"]


# Not used
class MembersResultsRequest(Request[List[Member]]):
    def __init__(self, gmi: "GMI", group_id: str, results_id: str) -> None:
        self.group_id = group_id
        self.results_id = results_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "GET"

    def url(self) -> str:
        return (
            self.base_url
            + "/groups/"
            + str(self.group_id)
            + "/members/results/"
            + str(self.results_id)
        )

    def parse(self, response: JsonType) -> List[Member]:
        members = []
        for member_json in response["members"]:
            members.append(Member.from_json(self.gmi, member_json, self.group_id))
        return members


class MembersRemoveRequest(Request[None]):
    def __init__(self, gmi: "GMI", group_id: str, member_id: str) -> None:
        self.group_id = group_id
        self.member_id = member_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return (
            self.base_url
            + "/groups/"
            + str(self.group_id)
            + "/members/"
            + str(self.member_id)
            + "/remove"
        )

    def parse(self, response: JsonType) -> None:
        return None


class MembersUpdateRequest(Request[Member]):
    def __init__(self, gmi: "GMI", group_id: str, nickname: str) -> None:
        self.group_id = group_id
        self.nickname = nickname
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/memberships/update"

    def args(self) -> JsonType:
        return {"membership": {"nickname": self.nickname}}

    def parse(self, response: JsonType) -> Member:
        return Member.from_json(self.gmi, response, self.group_id)
