# pyre-strict
from typing import TYPE_CHECKING, Optional, Dict, List, Any

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request, JsonType
from lowerpines.endpoints.like import LikeCreateRequest, LikeDestroyRequest
from lowerpines.exceptions import InvalidOperationException

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI
    from lowerpines.message import ComplexMessage  # noqa: F401

# TODO model attachments better
AttachmentType = Dict[str, Any]


class Message(AbstractObject, RetrievableObject):
    message_id: Optional[str] = Field().with_api_name("id").with_type(str)
    source_guid: str = Field().with_type(str)
    created_at: int = Field().with_type(int)
    user_id: str = Field().with_type(str)
    group_id: str = Field().with_type(str)
    name: str = Field().with_type(str)
    avatar_url: Optional[str] = Field().with_type(str)
    text: str = Field().with_type(str)
    system: bool = Field().with_type(bool)
    favorited_by: List[str] = Field().with_type(List[str])
    # pyre-ignore
    attachments: List[AttachmentType] = Field().with_type(List[AttachmentType])
    sender_type: Optional[str] = Field().with_type(str)
    sender_id: str = Field().with_type(str)

    complex_text: Optional["ComplexMessage"] = None

    def __init__(
        self,
        gmi: "GMI",
        group_id: Optional[str] = None,
        source_guid: Optional[str] = None,
        text: Optional[str] = None,
        attachments: Optional[List[AttachmentType]] = None,
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id  # type: ignore
        self.source_guid = source_guid  # type: ignore
        self.text = text  # type: ignore
        self.attachments = attachments or []
        self.message_id = None

    def save(self) -> None:
        if self.message_id:
            raise InvalidOperationException(
                "You cannot change a message that has already been sent"
            )
        else:
            new_data = MessagesCreateRequest(
                self.gmi, self.group_id, self.source_guid, self.text, self.attachments
            ).result
            self._refresh_from_other(new_data)

    def refresh(self) -> None:
        message_id = self.message_id
        if message_id:
            new_data = MessagesShowRequest(self.gmi, self.group_id, message_id).result
            self._refresh_from_other(new_data)
        else:
            raise InvalidOperationException(
                "Must have a message_id to pull data from the server"
            )

    def on_fields_loaded(self) -> None:
        if self.text is None:
            self.text = ""
        from lowerpines.message import ComplexMessage, RefAttach  # noqa: F811

        self.complex_text = ComplexMessage("")
        doing_mentions = False
        for attachment in self.attachments:
            if attachment["type"] == "mentions":
                doing_mentions = True
                prev_index = 0
                for i in range(len(self.text)):
                    for loci, user_id in zip(
                        attachment["loci"], attachment["user_ids"]
                    ):
                        if loci[0] == i:
                            self.complex_text += self.text[
                                prev_index : loci[0]
                            ] + RefAttach(
                                user_id, self.text[loci[0] : loci[0] + loci[1]]
                            )
                            prev_index = loci[0] + loci[1]
                self.complex_text = self.complex_text + self.text[prev_index:]
        if not doing_mentions:
            self.complex_text = ComplexMessage(self.text)

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        return self.text

    @staticmethod
    def get(gmi: "GMI", group_id: str, message_id: str) -> "Message":  # type: ignore
        return MessagesShowRequest(gmi, group_id, message_id).result

    def like(self) -> None:
        message_id = self.message_id
        if message_id is None:
            raise ValueError("Message must be saved before it can be liked")
        LikeCreateRequest(self.gmi, self.group_id, message_id)

    def unlike(self) -> None:
        message_id = self.message_id
        if message_id is None:
            raise ValueError("Message must be saved before it can be unliked")
        LikeDestroyRequest(self.gmi, self.group_id, message_id)


class MessagesIndexRequest(Request[List[Message]]):
    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        before_id: Optional[str] = None,
        since_id: Optional[str] = None,
        after_id: Optional[str] = None,
        limit: int = 20,
    ) -> None:
        self.group_id = group_id
        self.before_id = before_id
        self.since_id = since_id
        self.after_id = after_id
        self.limit = limit
        if limit > 100:
            raise ValueError("Limit must be at or below 100")
        arg_count = 0
        if before_id is not None:
            arg_count += 1
        if since_id is not None:
            arg_count += 1
        if after_id is not None:
            arg_count += 1
        elif arg_count > 1:
            raise ValueError(
                "Only one of before_id, since_id or after_id can be defined"
            )
        super().__init__(gmi)

    def mode(self) -> str:
        return "GET"

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/messages"

    def args(self) -> JsonType:
        args_dict = {}
        if self.before_id is not None:
            args_dict["before_id"] = self.before_id
        if self.since_id is not None:
            args_dict["since_id"] = self.since_id
        if self.after_id is not None:
            args_dict["after_id"] = self.after_id
        if self.limit != 20:
            args_dict["limit"] = self.limit  # type: ignore
        return args_dict

    def parse(self, response: JsonType) -> List[Message]:
        # count = int(response['count'])
        messages = []
        for message_json in response["messages"]:
            messages.append(Message.from_json(self.gmi, message_json))
        return messages


class MessagesCreateRequest(Request[Message]):
    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        source_guid: str,
        text: str,
        attachments: Optional[List[AttachmentType]] = None,
    ) -> None:
        self.group_id = group_id
        self.source_guid = source_guid
        self.text = text
        self.attachments = attachments
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def url(self) -> str:
        return self.base_url + "/groups/" + str(self.group_id) + "/messages"

    def args(self) -> JsonType:
        return {
            "message": {
                "source_guid": self.source_guid,
                "text": self.text,
                "attachments": self.attachments,
            }
        }

    def parse(self, response: JsonType) -> Message:
        return Message.from_json(self.gmi, response["message"])


# --- Undocumented ---


class MessagesShowRequest(Request[Message]):
    def __init__(self, gmi: "GMI", group_id: str, message_id: str) -> None:
        self.group_id = group_id
        self.message_id = message_id
        super().__init__(gmi)

    def url(self) -> str:
        return (
            self.base_url
            + "/groups/"
            + str(self.group_id)
            + "/messages/"
            + str(self.message_id)
        )

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> Message:
        return Message.from_json(self.gmi, response["message"])
