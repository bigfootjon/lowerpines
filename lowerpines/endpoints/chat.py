# pyre-strict
from typing import List, Optional, TYPE_CHECKING, Any

from lowerpines.endpoints.message import AttachmentType
from lowerpines.endpoints.object import AbstractObject, Field
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI
    from lowerpines.message import ComplexMessage


class Chat(AbstractObject):
    created_at: int = Field().with_type(int)
    updated_at: int = Field().with_type(int)
    messages_count: int = Field().with_type(int)
    last_message_raw: JsonType = Field().with_api_name("last_message").with_type(
        JsonType
    )
    other_user_raw: JsonType = Field().with_api_name("other_user").with_type(JsonType)

    last_message: Optional["DirectMessage"] = None
    other_user: "DirectMessageUser" = None  # type: ignore

    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi
        self.messages = ChatMessagesManager(self)

    @staticmethod
    def get_all(gmi: "GMI") -> List["Chat"]:
        return DirectMessageChatsRequest(gmi).result

    def get(self, other_user_id: str) -> List["DirectMessage"]:
        return DirectMessageIndexRequest(self.gmi, other_user_id).result

    def post(self, message: "ComplexMessage") -> "DirectMessage":
        text, attachments = smart_split_complex_message(message)
        return DirectMessageCreateRequest(
            self.gmi,
            self.gmi.user.get().user_id,
            self.other_user.user_id,
            text,
            attachments,
        ).result

    def on_fields_loaded(self) -> None:
        self.last_message = DirectMessage.from_json(self.gmi, self.last_message_raw)
        self.other_user = DirectMessageUser.from_json(self.gmi, self.other_user_raw)

    def __str__(self) -> str:
        return "Chat with " + str(self.other_user)

    def __repr__(self) -> str:
        return "C:" + str(self.other_user)


class DirectMessage(AbstractObject):
    @staticmethod
    def get(gmi: "GMI", *args: Any) -> None:
        raise InvalidOperationException("This is non-trivial to implement")

    def refresh(self) -> None:
        raise InvalidOperationException("This is non-trivial to implement")

    # pyre-ignore
    attachments: List[AttachmentType] = Field().with_type(List[AttachmentType])
    avatar_url: str = Field().with_type(str)
    conversation_id: str = Field().with_type(str)
    created_at: str = Field().with_type(str)
    favorited_by: str = Field().with_type(str)
    direct_message_id: str = Field().with_api_name("id").with_type(str)
    name: str = Field().with_type(str)
    recipient_id: str = Field().with_type(str)
    sender_id: str = Field().with_type(str)
    sender_type: str = Field().with_type(str)
    source_guid: str = Field().with_type(str)
    text: str = Field().with_type(str)
    user_id: str = Field().with_type(str)

    def __init__(
        self,
        gmi: "GMI",
        source_guid: Optional[str] = None,
        recipient_id: Optional[str] = None,
        text: Optional[str] = None,
        attachments: Optional[List[AttachmentType]] = None,
    ) -> None:
        self.gmi = gmi  # type: ignore
        self.source_guid = source_guid  # type: ignore
        self.recipient_id = recipient_id  # type: ignore
        self.text = text  # type: ignore
        self.attachments = attachments or []

    def save(self) -> None:
        if self.direct_message_id == "":
            new_data = DirectMessageCreateRequest(
                self.gmi,
                self.source_guid,
                self.recipient_id,
                self.text,
                self.attachments,
            ).result
            self._refresh_from_other(new_data)
        else:
            raise InvalidOperationException(
                "You cannot change a message that has already been sent"
            )

    def __str__(self) -> str:
        return self.text

    def __repr__(self) -> str:
        return "M:" + str(self)


class DirectMessageUser(AbstractObject):
    def save(self) -> None:
        raise InvalidOperationException("This operation is not permitted")

    @staticmethod
    def get(gmi: "GMI", *args: Any) -> None:
        raise InvalidOperationException("This operation does not make sense")

    def refresh(self) -> None:
        raise InvalidOperationException("This operation is non-trivial to implement")

    avatar_url: str = Field()  # type: ignore
    user_id: str = Field()  # type: ignore
    name: str = Field()  # type: ignore

    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi

    def __str__(self) -> str:
        return str(self.name)


class ChatMessagesManager:
    count = 0

    last_id = str()
    last_created_at = str()

    def __init__(self, chat: Chat) -> None:
        self.chat = chat

    def all(self) -> List[DirectMessage]:
        messages = self.recent()
        while len(messages) < self.count:
            messages.extend(self.before(messages[-1]))
        return messages

    def recent(self) -> List[DirectMessage]:
        return DirectMessageIndexRequest(
            self.chat.gmi, self.chat.other_user.user_id
        ).result

    def before(self, message: DirectMessage) -> List[DirectMessage]:
        return DirectMessageIndexRequest(
            self.chat.gmi,
            self.chat.other_user.user_id,
            before_id=message.message_id,  # type: ignore
        ).result

    def since(self, message: DirectMessage) -> List[DirectMessage]:
        return DirectMessageIndexRequest(
            self.chat.gmi,
            self.chat.other_user.user_id,
            since_id=message.message_id,  # type: ignore
        ).result


class DirectMessageChatsRequest(Request[List[Chat]]):
    def __init__(
        self, gmi: "GMI", page: Optional[str] = None, per_page: Optional[str] = None
    ) -> None:
        self.page = page
        self.per_page = per_page
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/chats"

    def args(self) -> JsonType:
        arg_dict = {}
        if self.page is not None:
            arg_dict["page"] = self.page
        if self.per_page is not None:
            arg_dict["per_page"] = self.per_page
        return arg_dict

    def parse(self, response: JsonType) -> List[Chat]:
        chats = []
        for chat_json in response:
            chats.append(Chat.from_json(self.gmi, chat_json))  # type: ignore
        return chats

    def mode(self) -> str:
        return "GET"


class DirectMessageIndexRequest(Request[List[DirectMessage]]):
    def __init__(
        self,
        gmi: "GMI",
        other_user_id: str,
        before_id: Optional[str] = None,
        since_id: Optional[str] = None,
    ) -> None:
        self.other_user_id = other_user_id
        if before_id and since_id:
            raise ValueError("Cannot define both before_id and since_id!")
        self.before_id = before_id
        self.since_id = since_id
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/direct_messages"

    def args(self) -> JsonType:
        arg_dict = {"other_user_id": self.other_user_id}
        before_id = self.before_id
        since_id = self.since_id
        if before_id:
            arg_dict["before_id"] = before_id
        elif since_id:
            arg_dict["since_id"] = since_id
        return arg_dict

    def parse(self, response: JsonType) -> List[DirectMessage]:
        dms = []
        for dm_json in response["direct_messages"]:
            dms.append(DirectMessage.from_json(self.gmi, dm_json))
        return dms

    def mode(self) -> str:
        return "GET"


class DirectMessageCreateRequest(Request[DirectMessage]):
    def __init__(
        self,
        gmi: "GMI",
        sender_id: str,
        recipient_id: str,
        text: str,
        attachments: Optional[List[AttachmentType]] = None,
    ) -> None:
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response: JsonType) -> DirectMessage:
        return DirectMessage.from_json(self.gmi, response["direct_message"])

    def url(self) -> str:
        return self.base_url + "/direct_messages"

    def args(self) -> JsonType:
        direct_message: JsonType = {"text": self.text}
        if self.attachments:
            direct_message["attachments"] = self.attachments
        return {
            "message": direct_message,
            "conversation_id": self.recipient_id + "+" + self.sender_id,
        }

    def mode(self) -> str:
        return "POST"
