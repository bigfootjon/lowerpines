# pyre-strict
from typing import TYPE_CHECKING, List

from lowerpines.endpoints.object import AbstractObject, Field
from lowerpines.endpoints.request import Request, JsonType

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI


class Block(AbstractObject):
    user_id: str = Field().with_type(str)
    blocked_user_id: str = Field().with_type(str)

    def __init__(self, gmi: "GMI") -> None:
        self.gmi = gmi

    def get_all(self, user_id: str) -> List["Block"]:
        return BlockIndexRequest(self.gmi, user_id).result

    @staticmethod
    def block_exists(gmi: "GMI", user_id: str, other_user_id: str) -> bool:
        return BlockBetweenRequest(gmi, user_id, other_user_id).result

    @staticmethod
    def block(gmi: "GMI", user_id: str, other_user_id: str) -> None:
        BlockCreateRequest(gmi, user_id, other_user_id)

    @staticmethod
    def unblock(gmi: "GMI", user_id: str, other_user_id: str) -> None:
        BlockUnblockRequest(gmi, user_id, other_user_id)


class BlockIndexRequest(Request[List[Block]]):
    def __init__(self, gmi: "GMI", user_id: str) -> None:
        self.user_id = user_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> List[Block]:
        blocks = list()
        for block_json in response["blocks"]:
            blocks.append(Block.from_json(self.gmi, block_json))
        return blocks

    def args(self) -> JsonType:
        return {"user": self.user_id}

    def url(self) -> str:
        return self.base_url + "/blocks"


class BlockBetweenRequest(Request[bool]):
    def __init__(self, gmi: "GMI", user_id: str, other_user_id: str) -> None:
        self.user_id = user_id
        self.other_user_id = other_user_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "GET"

    def parse(self, response: JsonType) -> bool:
        return response["between"]

    def args(self) -> JsonType:
        return {"user": self.user_id, "otherUser": self.other_user_id}

    def url(self) -> str:
        return self.base_url + "/blocks/between"


class BlockCreateRequest(Request[None]):
    def __init__(self, gmi: "GMI", user_id: str, other_user_id: str) -> None:
        self.user_id = user_id
        self.other_user_id = other_user_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def parse(self, response: JsonType) -> None:
        return None

    def args(self) -> JsonType:
        return {}

    def url(self) -> str:
        return (
            self.base_url
            + "/blocks?user="
            + self.user_id
            + "&otherUser="
            + self.other_user_id
        )


class BlockUnblockRequest(Request[None]):
    def __init__(self, gmi: "GMI", user_id: str, other_user_id: str) -> None:
        self.user_id = user_id
        self.other_user_id = other_user_id
        super().__init__(gmi)

    def mode(self) -> str:
        return "POST"

    def parse(self, response: JsonType) -> None:
        return None

    def args(self) -> JsonType:
        return {}

    def url(self) -> str:
        return (
            self.base_url
            + "/blocks/delete"
            + "/blocks?user="
            + self.user_id
            + "&otherUser="
            + self.other_user_id
        )
