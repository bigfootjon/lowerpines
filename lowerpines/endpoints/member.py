# pyre-strict
from typing import Dict, TYPE_CHECKING, List, Optional

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.exceptions import InvalidOperationException

if TYPE_CHECKING:
    from lowerpines.gmi import GMI


class Member(AbstractObject, RetrievableObject):
    # pyre-ignore
    member_id: str = Field(api_name="id")
    # pyre-ignore
    user_id: Optional[str] = Field()
    # pyre-ignore
    nickname: str = Field()
    # pyre-ignore
    muted: str = Field()
    # pyre-ignore
    image_url: str = Field()
    # pyre-ignore
    autokicked: str = Field()
    # pyre-ignore
    app_installed: str = Field()
    # pyre-ignore
    guid: str = Field()

    # pyre-ignore
    phone_number: Optional[str] = Field()
    # pyre-ignore
    email: Optional[str] = Field()

    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        nickname: str,
        user_id: Optional[str] = None,
        phone_number: Optional[str] = None,
        email: Optional[str] = None,
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id
        self.nickname = nickname
        self.user_id = user_id
        self.phone_number = phone_number
        self.email = email

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
    def get(gmi: "GMI", member_id: str) -> None:
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

    def args(self) -> Dict[str, List[Dict[str, Optional[str]]]]:
        add_dict = {"members": [{"nickname": self.nickname, "user_id": self.user_id}]}
        return add_dict

    def mode(self) -> str:
        return "POST"

    def parse(self, response: Dict[str, str]) -> str:
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

    def parse(self, response: Dict[str, str]) -> List[Member]:
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

    def parse(self, response: str) -> None:
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

    def args(self) -> Dict[str, Dict[str, str]]:
        return {"membership": {"nickname": self.nickname}}

    def parse(self, response: str) -> Member:
        return Member.from_json(self.gmi, response, self.group_id)
