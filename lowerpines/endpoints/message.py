# pyre-strict
from typing import List, Dict, TYPE_CHECKING, Union, Optional

from lowerpines.endpoints.object import AbstractObject, Field, RetrievableObject
from lowerpines.endpoints.request import Request
from lowerpines.endpoints.like import LikeCreateRequest, LikeDestroyRequest
from lowerpines.exceptions import InvalidOperationException

if TYPE_CHECKING:
    from lowerpines.message import ComplexMessage
    from lowerpines.gmi import GMI


class Message(AbstractObject, RetrievableObject):
    # pyre-ignore
    message_id: Optional[str] = Field(api_name="id")
    # pyre-ignore
    source_guid: str = Field()
    # pyre-ignore
    created_at: str = Field()
    # pyre-ignore
    user_id: str = Field()
    # pyre-ignore
    group_id: str = Field()
    # pyre-ignore
    name: str = Field()
    # pyre-ignore
    avatar_url: str = Field()
    # pyre-ignore
    text: str = Field()
    # pyre-ignore
    system: str = Field()
    # pyre-ignore
    favorited_by: str = Field()
    # pyre-ignore
    attachments: List[Dict[str, Union[List[str], str]]] = Field()
    # pyre-ignore
    sender_type: str = Field()
    # pyre-ignore
    sender_id: str = Field()

    # pyre-ignore
    complex_text: "ComplexMessage"

    def __init__(
        self,
        gmi: "GMI",
        group_id: str,
        source_guid: str,
        text: str,
        attachments: Optional[List[Dict[str, Union[List[str], str]]]] = None,
    ) -> None:
        self.gmi = gmi
        self.group_id = group_id
        self.source_guid = source_guid
        self.text = text
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
        if self.message_id:
            new_data = MessagesShowRequest(
                self.gmi,
                self.group_id,
                # pyre-ignore
                self.message_id,
            ).result
            self._refresh_from_other(new_data)
        else:
            raise InvalidOperationException(
                "Must have a message_id to pull data from the server"
            )

    def on_fields_loaded(self) -> None:
        if self.text is None:
            self.text = ""
        from lowerpines.message import ComplexMessage, RefAttach

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
    def get(gmi: "GMI", group_id: str, message_id: str) -> "Message":
        return MessagesShowRequest(gmi, group_id, message_id).result

    def like(self) -> None:
        if self.message_id is None:
            raise InvalidOperationException(
                "Message must be saved before it can be liked"
            )
        # pyre-ignore
        LikeCreateRequest(self.gmi, self.group_id, self.message_id)

    def unlike(self) -> None:
        if self.message_id is None:
            raise InvalidOperationException(
                "Message must be saved before it can be unliked"
            )
        # pyre-ignore
        LikeDestroyRequest(self.gmi, self.group_id, self.message_id)


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

    def args(self) -> Dict[str, str]:
        args_dict = {}
        if self.before_id is not None:
            args_dict["before_id"] = self.before_id
        if self.since_id is not None:
            args_dict["since_id"] = self.since_id
        if self.after_id is not None:
            args_dict["after_id"] = self.after_id
        if self.limit is not 20:
            args_dict["limit"] = self.limit
        return args_dict

    def parse(self, response: Dict[str, str]) -> List[Message]:
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
        attachments: Optional[List[Dict[str, str]]] = None,
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

    def args(self) -> Dict[str, Dict[str, Optional[Union[List[Dict[str, str]], str]]]]:
        return {
            "message": {
                "source_guid": self.source_guid,
                "text": self.text,
                "attachments": self.attachments,
            }
        }

    def parse(self, response: Dict[str, str]) -> Message:
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

    def parse(self, response: Dict[str, str]) -> Message:
        return Message.from_json(self.gmi, response["message"])
