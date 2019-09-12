# pyre-strict
from typing import TYPE_CHECKING, Optional, List, Type

import requests

if TYPE_CHECKING:
    from lowerpines.group import GroupManager
    from lowerpines.bot import BotManager
    from lowerpines.chat import ChatManager
    from lowerpines.user import UserManager

_gmi_objects: List["GMI"] = []


def get_gmi(access_token: str) -> "GMI":
    for gmi in _gmi_objects:
        if gmi.access_token == access_token:
            return gmi
    gmi = GMI(access_token)
    _gmi_objects.append(gmi)
    return gmi


class GMI:
    # pyre-ignore
    groups: "GroupManager"
    # pyre-ignore
    bots: "BotManager"
    # pyre-ignore
    chats: "ChatManager"
    # pyre-ignore
    user: "UserManager"

    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

        self.refresh()

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
