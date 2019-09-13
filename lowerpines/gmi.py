# pyre-strict
from typing import Optional

import requests
from typing import List

_gmi_objects: List["GMI"] = []


def get_gmi(access_token: str) -> "GMI":
    for gmi in _gmi_objects:
        if gmi.access_token == access_token:
            return gmi
    gmi = GMI(access_token)
    _gmi_objects.append(gmi)
    return gmi


class GMI:
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

        from lowerpines.group import GroupManager
        from lowerpines.bot import BotManager
        from lowerpines.chat import ChatManager
        from lowerpines.user import UserManager

        self.groups = GroupManager(self)
        self.bots = BotManager(self)
        self.chats = ChatManager(self)
        self.user = UserManager(self)

        self.write_json_to: Optional[str] = None

    def refresh(self) -> None:
        from lowerpines.group import GroupManager
        from lowerpines.bot import BotManager
        from lowerpines.chat import ChatManager
        from lowerpines.user import UserManager

        self.groups = GroupManager(self)
        self.bots = BotManager(self)
        self.chats = ChatManager(self)
        self.user = UserManager(self)

    def convert_image_url(self, url: str) -> str:
        from lowerpines.endpoints.image import ImageConvertRequest

        return ImageConvertRequest(self, requests.get(url).content).result
