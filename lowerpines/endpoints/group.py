# pyre-strict

from datetime import datetime
from typing import TYPE_CHECKING, Optional, List, Union

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.endpoints.member import MembersAddRequest, MembersRemoveRequest, Member
from lowerpines.endpoints.message import Message
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI
    from lowerpines.message import ComplexMessage  # noqa: F401
    from lowerpines.endpoints.bot import Bot
    from lowerpines.manager import AbstractManager


class Group(AbstractObject, RetrievableObject):
    group_id: str = Field().with_api_name("id").with_type(str)
    name: str = Field().with_type(str)
    type: str = Field().with_type(str)
    description: Optional[str] = Field().with_type(str)
    image_url: Optional[str] = Field().with_type(str)
    creator_user_id: str = Field().with_type(str)
    created_at: int = Field().with_type(int)
    updated_at: int = Field().with_type(int)
    share_url: Optional[str] = Field().with_type(str)
    share_qr_code_url: Optional[str] = Field().with_type(str)
    office_mode: bool = Field().with_type(bool)
    phone_number: Optional[str] = Field().with_type(str)
    members: List[Member]
    members_raw: List[JsonType] = Field().with_api_name("members").with_type(
        List[JsonType]
    )
    messages_count_raw: int = Field().with_api_name("messages.count").with_type(int)
    messages_last_message_id_raw: Optional[str] = Field().with_api_name(
        "messages.last_message_id"
    ).with_type(str)
    messages_last_message_created_at_raw: Optional[  # type: ignore
        int
    ] = Field().with_api_name("messages.last_message_created_at")

    def __init__(
        self,
        gmi: "GMI",
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
    ) -> None:
        super().__init__(gmi)
        self.gmi = gmi
        self.messages = GroupMessagesManager(self)
        self.name = name  # type: ignore
        self.description = description
        self.image_url = image_url
        self.members = []

    @property
    def bots(self) -> "AbstractManager[Bot]":
        return self.gmi.bots.filter(group_id=self.group_id)

    def on_fields_loaded(self) -> None:
        self.members = []
        for member_json in self.members_raw:
            self.members.append(Member.from_json(self.gmi, member_json, self.group_id))
        self.messages.count = self.messages_count_raw
        self.messages.last_id = self.messages_last_message_id_raw
        self.messages.last_created_at = self.messages_last_message_created_at_raw

    def save(self) -> None:
        if self.group_id is None:
            new_data = GroupsCreateRequest(
                self.gmi, self.name, self.description, self.image_url
            ).result
        else:
            new_data = GroupsUpdateRequest(
                self.gmi, self.group_id, self.name, self.description, self.image_url
            ).result

        self._refresh_from_other(new_data)

    def delete(self) -> None:
        if self.group_id is None:
            raise InvalidOperationException("Cannot destroy a group that isn't saved!")
        else:
            GroupsDestroyRequest(self.gmi, self.group_id)

    def refresh(self) -> None:
        if self.group_id is None:
            raise InvalidOperationException("Must have an id to perform this operation")
        else:
            new_data = GroupsShowRequest(self.gmi, group_id=self.group_id).result
            self._refresh_from_other(new_data)

    def member_add(self, name: str, user_id: str) -> None:
        MembersAddRequest(self.gmi, self.group_id, name, user_id=user_id)

    def member_rm(self, member_id: str) -> None:
        MembersRemoveRequest(self.gmi, self.group_id, member_id)

    def post(self, message: Union["ComplexMessage", str]) -> Message:
        text, attachments = smart_split_complex_message(message)
        obj = Message(self.gmi, self.group_id, str(datetime.now()), text, attachments)
        obj.save()
        return obj

    @staticmethod
    def get(gmi: "GMI", group_id: str) -> "Group":  # type: ignore
        return GroupsShowRequest(gmi, group_id).result

    @staticmethod
    def get_all(gmi: "GMI") -> List["Group"]:
        return GroupsIndexRequest(gmi, per_page=100).result

    @staticmethod
    def get_former(gmi: "GMI") -> List["Group"]:
        return GroupsFormerRequest(gmi).result

    @staticmethod
    def join(gmi: "GMI", group_id: str, share_token: str) -> "Group":
        return GroupsJoinRequest(gmi, group_id, share_token).result

    @staticmethod
    def rejoin(gmi: "GMI", group_id: str) -> "Group":
        return GroupsRejoinRequest(gmi, group_id).result

    def change_owner(self, owner_id: str) -> JsonType:
        return GroupsChangeOwnersRequest(self.gmi, self.group_id, owner_id).result

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
        return str(self)


class GroupMessagesManager:
    count = 0

    last_id: Optional[str] = str()
    last_created_at: Optional[int] = int()

    def __init__(self, group: Group) -> None:
        self.group = group

    def all(self) -> List[Message]:
        messages = self.recent()
        while len(messages) < self.count:
            messages.extend(self.before(messages[-1]))
        return messages

    def recent(self, count: int = 100) -> List[Message]:
        from lowerpines.endpoints.message import MessagesIndexRequest

        return MessagesIndexRequest(
            self.group.gmi, self.group.group_id, limit=count
        ).result

    def before(self, message: Message, count: int = 100) -> List[Message]:
        from lowerpines.endpoints.message import MessagesIndexRequest

        return MessagesIndexRequest(
            self.group.gmi,
            self.group.group_id,
            limit=count,
            before_id=message.message_id,
        ).result

    def since(self, message: Message, count: int = 100) -> List[Message]:
        from lowerpines.endpoints.message import MessagesIndexRequest

        return MessagesIndexRequest(
            self.group.gmi,
            self.group.group_id,
            limit=count,
            since_id=message.message_id,
        ).result

    def after(self, message: Message, count: int = 100) -> List[Message]:
        from lowerpines.endpoints.message import MessagesIndexRequest

        return MessagesIndexRequest(
            self.group.gmi,
            self.group.group_id,
            limit=count,
            after_id=message.message_id,
        ).result


class GroupsIndexRequest(Request[List[Group]]):
    def __init__(self, gmi: "GMI", page: int = 1, per_page: int = 10) -> None:
        self.page = page
        self.per_page = per_page
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/groups"

    def args(self) -> JsonType:
        return {"page": self.page, "per_page": self.per_page}

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> List[Group]:
        groups = []
        for group_json in response:
            groups.append(Group.from_json(self.gmi, group_json))  # type: ignore
        return groups


class GroupsFormerRequest(Request[List[Group]]):
    def url(self) -> str:
        return self.base_url + "/groups/former"

    def args(self) -> JsonType:
        return {}

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> List[Group]:
        groups = []
        for group_json in response:
            groups.append(Group.from_json(self.gmi, group_json))  # type: ignore
        return groups


class GroupsShowRequest(Request[Group]):
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.group_id = group_id
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id)

    def args(self) -> JsonType:
        return {}

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> Group:
        return Group.from_json(self.gmi, response)


class GroupsCreateRequest(Request[Group]):
    def parse(self, response: JsonType) -> Group:
        return Group.from_json(self.gmi, response)

    def __init__(
        self,
        gmi: "GMI",
        name: str,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        share: Optional[str] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.image_url = image_url
        self.share = share
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/groups"

    def mode(self) -> str:
        return "POST"

    def args(self) -> JsonType:
        post_args = {"name": self.name}
        description = self.description
        if description is not None:
            post_args["description"] = description
        image_url = self.image_url
        if image_url is not None:
            post_args["image_url"] = image_url
        share = self.share
        if share is not None:
            post_args["share"] = share
        return post_args


class GroupsUpdateRequest(Request[Group]):
    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        image_url: Optional[str] = None,
        office_mode: Optional[str] = None,
        share: Optional[str] = None,
    ) -> None:
        self.group_id = group_id
        self.name = name
        self.description = description
        self.image_url = image_url
        self.office_mode = office_mode
        self.share = share
        super().__init__(gmi)

    def parse(self, response: JsonType) -> Group:
        return Group.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/update"

    def mode(self) -> str:
        return "POST"

    def args(self) -> JsonType:
        arg_dict = {}
        if self.name is not None:
            arg_dict["name"] = self.name
        if self.description is not None:
            arg_dict["description"] = self.description
        if self.image_url is not None:
            arg_dict["image_url"] = self.image_url
        if self.office_mode is not None:
            arg_dict["office_mode"] = self.office_mode
        if self.share is not None:
            arg_dict["share"] = self.share
        return arg_dict


class GroupsDestroyRequest(Request[None]):
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response: JsonType) -> None:
        pass

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/destroy"

    def mode(self) -> str:
        return "POST"


class GroupsJoinRequest(Request[Group]):
    def __init__(self, gmi: "GMI", group_id: str, share_token: str) -> None:
        self.group_id = group_id
        self.share_token = share_token
        super().__init__(gmi)

    def parse(self, response: JsonType) -> Group:
        return Group.from_json(self.gmi, response)

    def url(self) -> str:
        return (
            self.base_url
            + "/groups/"
            + str(self.group_id)
            + "/join/"
            + str(self.share_token)
        )

    def mode(self) -> str:
        return "POST"


class GroupsRejoinRequest(Request[Group]):
    def __init__(self, gmi: "GMI", group_id: str) -> None:
        self.group_id = group_id
        super().__init__(gmi)

    def parse(self, response: JsonType) -> Group:
        return Group.from_json(self.gmi, response)

    def url(self) -> str:
        return self.base_url + "/groups/join"

    def mode(self) -> str:
        return "POST"

    def args(self) -> JsonType:
        return {"group_id": self.group_id}


class GroupsChangeOwnersRequest(Request[JsonType]):
    def __init__(self, gmi: "GMI", group_id: str, owner_id: str) -> None:
        self.group_id = group_id
        self.owner_id = owner_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/groups/change_owners"

    def parse(self, response: JsonType) -> JsonType:
        return response

    def args(self) -> JsonType:
        return {"requests": [{"group_id": self.group_id, "owner_id": self.owner_id}]}
