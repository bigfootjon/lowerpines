from typing import Any

from lowerpines.gmi import GMI
from lowerpines.endpoints.request import Request


class LikeCreateRequest(Request):
    def __init__(self, gmi: GMI, conversation_id: str, message_id: str) -> None:
        self.conversation_id = conversation_id
        self.message_id = message_id
        super().__init__(gmi)

    def parse(self, response: dict) -> Any:
        return None

    def url(self) -> str:
        return self.base_url + '/messages/' + self.conversation_id + '/' + self.message_id + '/like'

    def mode(self) -> str:
        return "POST"


class LikeDestroyRequest(Request):
    def __init__(self, gmi: GMI, conversation_id: str, message_id: str) -> None:
        self.conversation_id = conversation_id
        self.message_id = message_id
        super().__init__(gmi)

    def parse(self, response: dict) -> Any:
        return None

    def url(self) -> str:
        return self.base_url + '/messages/' + self.conversation_id + '/' + self.message_id + '/unlike'

    def mode(self) -> str:
        return "POST"
