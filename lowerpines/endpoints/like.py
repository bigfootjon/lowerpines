# pyre-strict
from typing import Union, Dict

from requests import Response

from lowerpines.gmi import GMI
from lowerpines.endpoints.request import Request


class LikeCreateRequest(Request[None]):
    def __init__(self, gmi: GMI, conversation_id: str, message_id: str) -> None:
        self.conversation_id = conversation_id
        self.message_id = message_id
        super().__init__(gmi)

    def parse(self, response: Dict[str, Union[str, int]]) -> None:
        return None

    def url(self) -> str:
        return (
            self.base_url
            + "/messages/"
            + self.conversation_id
            + "/"
            + self.message_id
            + "/like"
        )

    def mode(self) -> str:
        return "POST"


class LikeDestroyRequest(Request[None]):
    def __init__(self, gmi: GMI, conversation_id: str, message_id: str) -> None:
        self.conversation_id = conversation_id
        self.message_id = message_id
        super().__init__(gmi)

    def parse(self, response: Dict[str, Union[str, int]]) -> None:
        return None

    def url(self) -> str:
        return (
            self.base_url
            + "/messages/"
            + self.conversation_id
            + "/"
            + self.message_id
            + "/unlike"
        )

    def mode(self) -> str:
        return "POST"
