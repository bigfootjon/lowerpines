# pyre-strict
from typing import List, Dict, TYPE_CHECKING, Union, Optional

from lowerpines.endpoints.object import AbstractObject, Field
from lowerpines.endpoints.request import Request
from lowerpines.exceptions import InvalidOperationException
from lowerpines.message import smart_split_complex_message

if TYPE_CHECKING:
    from lowerpines.gmi import GMI
    from lowerpines.endpoints.message import Message
    from lowerpines.message import ComplexMessage


class Chat(AbstractObject):
    created_at = Field()
    updated_at = Field()
    messages_count = Field()
    last_message_raw = Field(api_name="last_message")
    other_user_raw = Field(api_name="other_user")

    last_message: Optional['DirectMessage'] = None
    other_user: Optional[str] = None

    def __init__(self, gmi: 'GMI') -> None:
        self.gmi = gmi
        self.messages = ChatMessagesManager(self)

    @staticmethod
    def get_all(gmi: 'GMI') -> List['DirectMessage']:
        return DirectMessageChatsRequest(gmi).result

    def get(self, other_user_id: str) -> 'DirectMessage':
        return DirectMessageIndexRequest(self.gmi, other_user_id).result

    def post(self, message: Union['ComplexMessage', str]) -> 'DirectMessage':
        text, attachments = smart_split_complex_message(message)
        return DirectMessageCreateRequest(
            self.gmi,
            self.gmi.user.get().user_id,
            # pyre-ignore
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
    def get(gmi: 'GMI', *args: None) -> None:
        raise InvalidOperationException("This is non-trivial to implement")

    def refresh(self) -> None:
        raise InvalidOperationException("This is non-trivial to implement")

    # pyre-ignore
    attachments: Optional[Dict[str, str]] = Field()
    # pyre-ignore
    avatar_url: str = Field()
    # pyre-ignore
    conversation_id: str = Field()
    # pyre-ignore
    created_at: str = Field()
    # pyre-ignore
    favorited_by: str = Field()
    # pyre-ignore
    direct_message_id: str = Field(api_name="id")
    # pyre-ignore
    name: str = Field()
    # pyre-ignore
    recipient_id: str = Field()
    # pyre-ignore
    sender_id: str = Field()
    # pyre-ignore
    sender_type: str = Field()
    # pyre-ignore
    source_guid: str = Field()
    # pyre-ignore
    text: str = Field()
    # pyre-ignore
    user_id: str = Field()

    def __init__(
        self, gmi: 'GMI', source_guid: Optional[str] = None, recipient_id: Optional[str] = None, text: Optional[str] = None, attachments: Optional[Dict[str, str]] = None
    ) -> None:
        self.gmi = gmi
        # pyre-ignore
        self.source_guid = source_guid
        # pyre-ignore
        self.recipient_id = recipient_id
        # pyre-ignore
        self.text = text
        self.attachments = attachments

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
    def get(gmi: 'GMI', *args: None) -> None:
        raise InvalidOperationException("This operation does not make sense")

    def refresh(self) -> None:
        raise InvalidOperationException("This operation is non-trivial to implement")

    avatar_url = Field()
    user_id = Field()
    name = Field()

    def __init__(self, gmi: 'GMI') -> None:
        self.gmi = gmi

    def __str__(self) -> str:
        return str(self.name)


class ChatMessagesManager:
    count = 0

    last_id = str()
    last_created_at = str()

    def __init__(self, chat: Chat) -> None:
        self.chat = chat

    def all(self) -> List['Message']:
        messages = self.recent()
        while len(messages) < self.count:
            messages.extend(self.before(messages[-1]))
        return messages

    def recent(self) -> List['Message']:
        return DirectMessageIndexRequest(
            # pyre-ignore
            self.chat.gmi, self.chat.other_user.user_id
        ).result

    def before(self, message: 'Message') -> List['Message']:
        return DirectMessageIndexRequest(
            # pyre-ignore
            self.chat.gmi, self.chat.other_user.user_id, before_id=message.message_id
        ).result

    def since(self, message: 'Message') -> List['Message']:
        return DirectMessageIndexRequest(
            # pyre-ignore
            self.chat.gmi, self.chat.group_id, since_id=message.message_id
        ).result


class DirectMessageChatsRequest(Request[List[Chat]]):
    def __init__(self, gmi: 'GMI', page: Optional[str] = None, per_page: Optional[str] = None) -> None:
        self.page = page
        self.per_page = per_page
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/chats"

    def args(self) -> Dict[str, str]:
        arg_dict = {}
        if self.page is not None:
            arg_dict["page"] = self.page
        if self.per_page is not None:
            arg_dict["per_page"] = self.per_page
        return arg_dict

    def parse(self, response: str) -> List[Chat]:
        chats = []
        for chat_json in response:
            chats.append(Chat.from_json(self.gmi, chat_json))
        return chats

    def mode(self) -> str:
        return "GET"


class DirectMessageIndexRequest(Request[List[DirectMessage]]):
    def __init__(self, gmi: 'GMI', other_user_id: str, before_id: Optional[str] = None, since_id: Optional[str] = None) -> None:
        self.other_user_id = other_user_id
        if before_id and since_id:
            raise ValueError("Cannot define both before_id and since_id!")
        self.before_id = before_id
        self.since_id = since_id
        super().__init__(gmi)

    def url(self) -> str:
        return self.base_url + "/direct_messages"

    def args(self) -> Dict[str, str]:
        arg_dict = {"other_user_id": self.other_user_id}
        if self.before_id:
            # pyre-ignore
            arg_dict["before_id"] = self.before_id
        elif self.since_id:
            # pyre-ignore
            arg_dict["since_id"] = self.since_id
        return arg_dict

    def parse(self, response: Dict[str, str]) -> List[DirectMessage]:
        dms = []
        for dm_json in response["direct_messages"]:
            dms.append(DirectMessage.from_json(self.gmi, dm_json))
        return dms

    def mode(self) -> str:
        return "GET"


class DirectMessageCreateRequest(Request[None]):
    def __init__(self, gmi: 'GMI', sender_id: str, recipient_id: str, text: str, attachments: Optional[Dict[str, str]] = None) -> None:
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def parse(self, response: str) -> None:
        # return DirectMessage.from_json(self.gmi, response['direct_message'])
        # TODO: Fix this
        pass

    def url(self) -> str:
        return self.base_url + "/direct_messages"

    def args(self) -> Dict[str, Union[Dict[str, str], str]]:
        direct_message = {"text": self.text}
        if self.attachments:
            # pyre-ignore
            direct_message["attachments"] = self.attachments
        return {
            "message": direct_message,
            "conversation_id": self.recipient_id + "+" + self.sender_id,
        }

    def mode(self) -> str:
        return "POST"
