# pyre-strict
from typing import TYPE_CHECKING, Dict

from requests import Response

from lowerpines.endpoints.request import Request

if TYPE_CHECKING:
    from lowerpines.gmi import GMI


class ImageConvertRequest(Request[str]):
    data: bytes

    def __init__(self, gmi: "GMI", data: bytes) -> None:
        self.data = data
        super().__init__(gmi)

    def url(self) -> str:
        return "https://image.groupme.com/pictures"

    def mode(self) -> str:
        return "POST_RAW"

    def args(self) -> bytes:
        return self.data

    def parse(self, response: Dict[str, Dict[str, str]]) -> str:
        return response["payload"]["url"]

    def extract_response(self, response: Response) -> Dict[str, Dict[str, str]]:
        return response.json()
