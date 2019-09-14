# pyre-strict
from requests import Response
from typing import TYPE_CHECKING

from lowerpines.endpoints.request import Request, JsonType

if TYPE_CHECKING:  # pragma: no cover
    from lowerpines.gmi import GMI


class ImageConvertRequest(Request[str]):
    def __init__(self, gmi: "GMI", data: bytes) -> None:
        self.data = data
        super().__init__(gmi)

    def url(self) -> str:
        return "https://image.groupme.com/pictures"

    def mode(self) -> str:
        return "POST_RAW"

    def args(self) -> bytes:
        return self.data

    def parse(self, response: JsonType) -> str:
        return response["payload"]["url"]

    def extract_response(self, response: Response) -> JsonType:
        return response.json()
